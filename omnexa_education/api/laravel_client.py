# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""HTTP client for Laravel TLMS integration."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import urljoin

import frappe
import requests
from frappe import _
from frappe.utils import cint, get_datetime, now_datetime


def _settings() -> dict:
	return frappe.get_single("Education Settings")


def is_laravel_enabled() -> bool:
	s = _settings()
	return bool(s.enable_laravel_tlms and s.laravel_base_url)


def _base_url() -> str:
	url = (_settings().laravel_base_url or "").strip().rstrip("/")
	if not url:
		frappe.throw(_("Laravel Base URL is not configured in Education Settings."))
	return url


def _api_key() -> str:
	key = _settings().get_password("laravel_api_key") if _settings().laravel_api_key else ""
	if not key:
		frappe.throw(_("Laravel API Key is not configured in Education Settings."))
	return key


def _institution_header_value(student_doc: dict | None = None) -> str:
	if student_doc and student_doc.get("institution"):
		return student_doc["institution"]
	return frappe.db.get_value("Education Institution", {}, "name") or ""


def _headers(student_doc: dict | None = None, *, include_tenant: bool = True) -> dict[str, str]:
	s = _settings()
	header_name = (s.laravel_institution_header or "X-ErpGenEx-School").strip()
	headers = {
		"Authorization": f"Bearer {_api_key()}",
		"Content-Type": "application/json",
		"Accept": "application/json",
	}
	if include_tenant:
		headers[header_name] = _institution_header_value(student_doc)
	return headers


def _request(
	method: str,
	path: str,
	payload: dict | None = None,
	student_doc: dict | None = None,
	*,
	include_tenant: bool = True,
) -> dict:
	if not is_laravel_enabled():
		return {"ok": False, "skipped": True, "reason": "laravel_disabled"}

	url = urljoin(_base_url() + "/", path.lstrip("/"))
	try:
		resp = requests.request(
			method=method.upper(),
			url=url,
			headers=_headers(student_doc, include_tenant=include_tenant),
			json=payload,
			timeout=30,
		)
	except requests.RequestException as exc:
		return {"ok": False, "error": str(exc), "status_code": 0}

	body: Any
	try:
		body = resp.json()
	except ValueError:
		body = {"raw": resp.text[:2000]}

	ok = 200 <= resp.status_code < 300
	throttled = resp.status_code == 429
	return {
		"ok": ok,
		"status_code": resp.status_code,
		"body": body,
		"throttled": throttled,
		"error": None
		if ok
		else (
			(body.get("message") if isinstance(body, dict) else resp.text[:500])
			or ("Throttled" if throttled else resp.text[:500])
		),
	}


def ping() -> dict:
	result = _request("GET", "/api/v1/health", include_tenant=False)
	status = "OK" if result.get("ok") else "Failed"
	frappe.db.set_single_value("Education Settings", "laravel_last_ping_at", now_datetime())
	frappe.db.set_single_value("Education Settings", "laravel_last_ping_status", status)
	if result.get("ok"):
		msg = result.get("body", {}).get("message", "pong") if isinstance(result.get("body"), dict) else "pong"
		return {"ok": True, "message": msg, "status_code": result.get("status_code")}
	return {
		"ok": False,
		"error": result.get("error") or _("Laravel health check failed"),
		"status_code": result.get("status_code"),
	}


def provision_user(payload: dict, student_doc: dict | None = None) -> dict:
	return _request("POST", "/api/v1/users/provision", payload, student_doc)


def suspend_user(laravel_user_id: str, reason: str = "", student_doc: dict | None = None) -> dict:
	return _request(
		"POST",
		f"/api/v1/users/{laravel_user_id}/suspend",
		{"reason": reason, "account_status": "financial_hold" if "financial" in reason.lower() else "suspended"},
		student_doc,
	)


def resume_user(laravel_user_id: str, student_doc: dict | None = None) -> dict:
	return _request("POST", f"/api/v1/users/{laravel_user_id}/resume", {}, student_doc)


def sync_enrollments(payload: dict, student_doc: dict | None = None) -> dict:
	return _request("POST", "/api/v1/enrollments/sync", payload, student_doc)


def _context_from_payload(payload: dict) -> dict | None:
	institution = payload.get("institution_id")
	if institution:
		return {"institution": institution}
	return None


def sync_classes(payload: dict, student_doc: dict | None = None) -> dict:
	ctx = student_doc or _context_from_payload(payload)
	return _request("POST", "/api/v1/classes/sync", payload, ctx)


def sync_programs(payload: dict) -> dict:
	"""University HE — sync programs, degree levels, academic structure to Laravel."""
	ctx = _context_from_payload(payload)
	return _request("POST", "/api/v1/programs/sync", payload, ctx)


def sync_institutions(payload: dict) -> dict:
	"""Register Education Institution rows as Laravel schools (no tenant header)."""
	return _request("POST", "/api/v1/institutions/sync", payload, include_tenant=False)


def sync_academic_calendar(payload: dict, student_doc: dict | None = None) -> dict:
	ctx = student_doc or _context_from_payload(payload)
	return _request("POST", "/api/v1/academic-calendar/sync", payload, ctx)


@frappe.whitelist()
def sync_institution_programs_to_laravel(institution: str) -> dict:
	"""Push Education Program records to Laravel TLMS (Banner/Workday parity)."""
	if not is_laravel_enabled():
		return {"ok": False, "skipped": True, "reason": "laravel_disabled"}
	programs = frappe.get_all(
		"Education Program",
		filters={"institution": institution, "is_active": 1},
		fields=["name", "program_code", "program_name", "degree_level", "company", "branch"],
	)
	courses = frappe.get_all(
		"Education Course",
		filters={"institution": institution},
		fields=["name", "course_code", "course_title", "credit_hours", "program"],
		limit=500,
	)
	payload = {
		"institution_id": institution,
		"institution_type": frappe.db.get_value("Education Institution", institution, "institution_type"),
		"programs": programs,
		"courses": courses,
		"standards": {"obe": True, "credit_hours": True, "sis": "erpgenex-education-v1"},
	}
	result = sync_programs(payload)
	if not result.get("ok"):
		enqueue_sync("sync_programs", "Education Institution", institution, payload)
	return {"ok": result.get("ok"), "programs": len(programs), "courses": len(courses), "result": result}


def enqueue_sync(
	operation: str,
	reference_doctype: str | None,
	reference_name: str | None,
	payload: dict,
) -> str:
	doc = frappe.get_doc(
		{
			"doctype": "Education Laravel Sync Queue",
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
			"operation": operation,
			"status": "Queued",
			"payload": json.dumps(payload, default=str),
			"scheduled_at": now_datetime(),
			"attempts": 0,
			"max_attempts": 5,
		}
	).insert(ignore_permissions=True)
	return doc.name


@frappe.whitelist()
def process_sync_queue(batch_size: int | None = None) -> dict:
	s = _settings()
	limit = cint(batch_size or s.laravel_sync_batch_size or 50)
	rows = frappe.get_all(
		"Education Laravel Sync Queue",
		filters={"status": ["in", ["Queued", "Failed"]]},
		fields=["name"],
		order_by="creation asc",
		limit=limit,
	)
	stats = {"processed": 0, "success": 0, "failed": 0}
	for row in rows:
		stats["processed"] += 1
		try:
			ok = _process_queue_item(row.name)
			stats["success" if ok else "failed"] += 1
		except Exception:
			stats["failed"] += 1
			frappe.log_error(frappe.get_traceback(), "Education Laravel Sync Queue")
	return stats


def _process_queue_item(name: str) -> bool:
	doc = frappe.get_doc("Education Laravel Sync Queue", name)
	if doc.attempts >= doc.max_attempts:
		doc.db_set("status", "Failed")
		return False
	doc.db_set({"status": "Processing", "attempts": cint(doc.attempts) + 1})
	payload = json.loads(doc.payload or "{}")
	try:
		if doc.operation == "provision":
			result = provision_user(payload, payload.get("_student_context"))
		elif doc.operation == "suspend":
			result = suspend_user(payload["laravel_user_id"], payload.get("reason", ""), payload.get("_student_context"))
		elif doc.operation == "resume":
			result = resume_user(payload["laravel_user_id"], payload.get("_student_context"))
		elif doc.operation == "sync_enrollment":
			result = sync_enrollments(payload, payload.get("_student_context"))
		elif doc.operation == "sync_institutions":
			result = sync_institutions(payload)
		elif doc.operation == "sync_programs":
			result = sync_programs(payload)
		elif doc.operation == "sync_classes":
			result = sync_classes(payload, payload.get("_student_context"))
		elif doc.operation == "sync_academic_calendar":
			result = sync_academic_calendar(payload, payload.get("_student_context"))
		else:
			result = {"ok": False, "error": f"Unknown operation {doc.operation}"}
	except Exception as exc:
		doc.db_set({"status": "Failed", "last_error": str(exc)})
		return False

	if result.get("ok"):
		doc.db_set({"status": "Success", "last_error": ""})
		return True
	doc.db_set({"status": "Failed", "last_error": result.get("error") or "sync failed"})
	return False
