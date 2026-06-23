# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Orchestrators for Laravel TLMS roster and calendar sync."""

from __future__ import annotations

import frappe
from frappe import _

from omnexa_education.api import laravel_client


def _institution_context(institution: str) -> dict:
	return {"institution": institution}


def build_classes_payload(institution: str) -> dict:
	campuses = frappe.get_all("Education Campus", filters={"institution": institution}, pluck="name")
	if not campuses:
		return {"institution_id": institution, "classes": []}

	sections = frappe.get_all(
		"Education Section",
		filters={"campus": ["in", campuses], "status": "Active"},
		fields=["name", "section_code", "section_name", "grade_level", "campus"],
		limit=500,
	)
	classes = []
	for sec in sections:
		grade_name = ""
		if sec.grade_level:
			grade_name = frappe.db.get_value("Education Grade Level", sec.grade_level, "grade_name") or sec.grade_level
		classes.append(
			{
				"external_id": sec.name,
				"section_external_id": sec.name,
				"name": sec.section_name or sec.section_code,
				"section": sec.section_code,
				"grade_level": grade_name or sec.section_code,
				"course_external_id": sec.section_code,
				"course_name": sec.section_name,
			}
		)
	return {"institution_id": institution, "classes": classes}


def build_academic_calendar_payload(institution: str) -> dict:
	terms = frappe.get_all(
		"Education Term",
		filters={"institution": institution, "status": "Active"},
		fields=["name", "term_name", "term_code", "start_date", "end_date", "academic_year"],
		limit=50,
	)
	terms_payload = [
		{
			"external_id": t.name,
			"name": t.term_name or t.term_code,
			"start_date": str(t.start_date),
			"end_date": str(t.end_date),
			"academic_year": t.academic_year,
		}
		for t in terms
	]
	events = []
	for t in terms:
		if t.start_date:
			events.append(
				{
					"external_id": f"{t.name}-START",
					"term_external_id": t.name,
					"event_type": "term_start",
					"title": f"{t.term_name or t.term_code} begins",
					"start_date": str(t.start_date),
					"end_date": str(t.start_date),
				}
			)
	return {"institution_id": institution, "terms": terms_payload, "events": events}


def build_enrollments_payload(institution: str, student: str | None = None) -> dict:
	filters: dict = {"institution": institution, "docstatus": 1}
	if student:
		filters["student"] = student
	rows = frappe.get_all(
		"Education Course Enrollment",
		filters=filters,
		fields=["name", "student", "course", "status"],
		limit=2000,
	)
	enrollments = []
	for row in rows:
		st_section = frappe.db.get_value("Education Student", row.student, "section")
		course_code = frappe.db.get_value("Education Course", row.course, "course_code") if row.course else row.course
		enrollments.append(
			{
				"student_external_id": row.student,
				"course_external_id": course_code or row.course,
				"section_external_id": st_section,
				"role": "student",
				"status": row.status,
			}
		)
	return {"institution_id": institution, "enrollments": enrollments}


def _sync_or_queue(operation: str, institution: str, payload: dict, sync_fn) -> dict:
	ctx = _institution_context(institution)
	payload = dict(payload)
	payload["_student_context"] = ctx
	result = sync_fn(payload, ctx)
	if result.get("ok"):
		return {"ok": True, "queued": False, "result": result}
	laravel_client.enqueue_sync(operation, "Education Institution", institution, payload)
	return {"ok": False, "queued": True, "result": result}


@frappe.whitelist()
def sync_institution_classes_to_laravel(institution: str) -> dict:
	if not laravel_client.is_laravel_enabled():
		return {"ok": False, "skipped": True, "reason": "laravel_disabled"}
	payload = build_classes_payload(institution)
	out = _sync_or_queue("sync_classes", institution, payload, laravel_client.sync_classes)
	out["classes"] = len(payload.get("classes") or [])
	return out


@frappe.whitelist()
def sync_institution_academic_calendar_to_laravel(institution: str) -> dict:
	if not laravel_client.is_laravel_enabled():
		return {"ok": False, "skipped": True, "reason": "laravel_disabled"}
	payload = build_academic_calendar_payload(institution)
	out = _sync_or_queue("sync_academic_calendar", institution, payload, laravel_client.sync_academic_calendar)
	out["terms"] = len(payload.get("terms") or [])
	out["events"] = len(payload.get("events") or [])
	return out


@frappe.whitelist()
def sync_institution_enrollments_to_laravel(institution: str, student: str | None = None) -> dict:
	if not laravel_client.is_laravel_enabled():
		return {"ok": False, "skipped": True, "reason": "laravel_disabled"}
	payload = build_enrollments_payload(institution, student=student)
	ctx = _institution_context(institution)
	result = laravel_client.sync_enrollments(payload, ctx)
	if not result.get("ok"):
		laravel_client.enqueue_sync("sync_enrollment", "Education Institution", institution, payload)
		return {"ok": False, "queued": True, "enrollments": len(payload.get("enrollments") or []), "result": result}
	return {"ok": True, "enrollments": len(payload.get("enrollments") or []), "result": result}


@frappe.whitelist()
def sync_institutions_to_laravel(institutions: list[str] | None = None) -> dict:
	"""Push Education Institution master to Laravel schools (sis_external_id)."""
	if not laravel_client.is_laravel_enabled():
		return {"ok": False, "skipped": True, "reason": "laravel_disabled"}
	names = institutions or frappe.get_all(
		"Education Institution",
		filters={"status": "Active"},
		pluck="name",
		limit=100,
	)
	rows = []
	for name in names:
		doc = frappe.db.get_value(
			"Education Institution",
			name,
			["name", "institution_name", "institution_type"],
			as_dict=True,
		)
		if not doc:
			continue
		code = frappe.db.get_value("Education Institution", name, "institution_code") or name
		rows.append(
			{
				"external_id": doc.name,
				"name": doc.institution_name or doc.name,
				"code": code,
				"institution_type": doc.institution_type or "",
			}
		)
	payload = {"institutions": rows}
	result = laravel_client.sync_institutions(payload)
	if not result.get("ok"):
		laravel_client.enqueue_sync("sync_institutions", "Education Settings", "Education Settings", payload)
	return {"ok": result.get("ok"), "institutions": len(rows), "result": result}


@frappe.whitelist()
def sync_institution_full_to_laravel(institution: str) -> dict:
	if not laravel_client.is_laravel_enabled():
		return {"ok": False, "skipped": True, "reason": "laravel_disabled"}
	if not frappe.db.exists("Education Institution", institution):
		frappe.throw(_("Institution {0} not found.").format(institution))
	institutions_sync = sync_institutions_to_laravel([institution])
	results = {
		"institutions": institutions_sync,
		"programs": laravel_client.sync_institution_programs_to_laravel(institution),
		"classes": sync_institution_classes_to_laravel(institution),
		"calendar": sync_institution_academic_calendar_to_laravel(institution),
		"enrollments": sync_institution_enrollments_to_laravel(institution),
	}
	ok = all(r.get("ok") or r.get("queued") for r in results.values())
	return {"ok": ok, "institution": institution, "results": results}


def sync_single_course_enrollment(doc) -> dict | None:
	s = frappe.get_single("Education Settings")
	if not s.auto_sync_enrollments_on_submit or not laravel_client.is_laravel_enabled():
		return None
	institution = doc.institution
	if not institution:
		return None
	payload = build_enrollments_payload(institution, student=doc.student)
	ctx = {"institution": institution, "company": doc.company, "branch": doc.branch}
	result = laravel_client.sync_enrollments(payload, ctx)
	if not result.get("ok"):
		laravel_client.enqueue_sync("sync_enrollment", doc.doctype, doc.name, payload)
	return result
