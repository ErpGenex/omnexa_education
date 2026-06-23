# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Teacher portal account lifecycle — provision to ErpGenEx User and Laravel TLMS."""

from __future__ import annotations

import json
import re

import frappe
from frappe import _
from frappe.utils import now_datetime

from omnexa_education.api import laravel_client


def _settings():
	return frappe.get_single("Education Settings")


def _teacher_email(teacher) -> str:
	if teacher.user and frappe.db.exists("User", teacher.user):
		email = frappe.db.get_value("User", teacher.user, "email")
		if email:
			return email.strip().lower()
	if teacher.employee:
		email = frappe.db.get_value("Employee", teacher.employee, "prefered_email") or frappe.db.get_value(
			"Employee", teacher.employee, "company_email"
		)
		if email:
			return email.strip().lower()
	safe = (teacher.teacher_code or "teacher").replace(" ", "").lower()
	company = (teacher.company or "school").replace(" ", "").lower()
	return f"{safe}@{company}.teachers.local"


def _teacher_institution(teacher) -> str | None:
	if teacher.campus:
		return frappe.db.get_value("Education Campus", teacher.campus, "institution")
	return frappe.db.get_value("Education Institution", {"company": teacher.company, "status": "Active"}, "name")


def _teacher_context(teacher) -> dict:
	institution = _teacher_institution(teacher)
	return {
		"institution": institution,
		"company": teacher.company,
		"branch": teacher.branch,
	}


def _ensure_teacher_user(teacher, role: str) -> str:
	email = _teacher_email(teacher)
	user = teacher.user if teacher.user and frappe.db.exists("User", teacher.user) else None
	if not user:
		user = frappe.db.get_value("User", {"email": email}, "name")
	if not user:
		parts = (teacher.teacher_name or "Teacher").split(" ", 1)
		user_doc = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": parts[0],
				"last_name": parts[1] if len(parts) > 1 else "",
				"send_welcome_email": 0,
				"user_type": "System User",
				"enabled": 1,
			}
		)
		user_doc.insert(ignore_permissions=True)
		user = user_doc.name
	if role and not frappe.db.exists("Has Role", {"parent": user, "role": role}):
		frappe.get_doc({"doctype": "Has Role", "parent": user, "parenttype": "User", "role": role}).insert(
			ignore_permissions=True
		)
	teacher.db_set("user", user, update_modified=False)
	return user


def build_laravel_teacher_payload(teacher) -> dict:
	institution = _teacher_institution(teacher)
	parts = (teacher.teacher_name or "Teacher").split(" ", 1)
	return {
		"external_id": teacher.name,
		"email": _teacher_email(teacher),
		"first_name": parts[0],
		"last_name": parts[1] if len(parts) > 1 else "",
		"role": "teacher",
		"institution_id": institution,
		"teacher_code": teacher.teacher_code,
		"account_status": "active",
		"_student_context": _teacher_context(teacher),
	}


@frappe.whitelist()
def provision_teacher(teacher: str, trigger: str = "Manual") -> dict:
	teacher_doc = frappe.get_doc("Education Teacher", teacher)
	if teacher_doc.status != "Active":
		frappe.throw(_("Cannot provision an inactive teacher."))

	s = _settings()
	role = s.teacher_user_role or "Teacher"
	user = _ensure_teacher_user(teacher_doc, role)

	laravel_user_id = teacher_doc.laravel_user_id
	laravel_synced = 0
	laravel_response = None
	if laravel_client.is_laravel_enabled():
		payload = build_laravel_teacher_payload(teacher_doc)
		result = laravel_client.provision_user(payload, payload.get("_student_context"))
		laravel_response = json.dumps(result, default=str)
		if result.get("ok"):
			laravel_synced = 1
			body = result.get("body") or {}
			if isinstance(body, dict):
				laravel_user_id = body.get("id") or body.get("laravel_user_id") or laravel_user_id
		else:
			laravel_client.enqueue_sync("provision", "Education Teacher", teacher, payload)

	if laravel_user_id:
		teacher_doc.db_set({"laravel_user_id": laravel_user_id, "last_laravel_sync_at": now_datetime()}, update_modified=False)

	return {
		"teacher": teacher,
		"user": user,
		"laravel_user_id": laravel_user_id,
		"laravel_synced": laravel_synced,
		"laravel_response": laravel_response,
	}


def auto_provision_teacher_if_needed(teacher_name: str):
	teacher = frappe.get_doc("Education Teacher", teacher_name)
	if teacher.status != "Active":
		return
	if not teacher.user:
		try:
			provision_teacher(teacher_name, trigger="Teacher Registration")
		except Exception:
			frappe.log_error(frappe.get_traceback(), "Teacher auto-provision failed")


@frappe.whitelist()
def bulk_provision_teachers(company: str | None = None, branch: str | None = None) -> dict:
	filters = {"status": "Active"}
	if company:
		filters["company"] = company
	if branch:
		filters["branch"] = branch
	count = 0
	for name in frappe.get_all("Education Teacher", filters=filters, pluck="name"):
		provision_teacher(name, trigger="Bulk")
		count += 1
	return {"provisioned": count}
