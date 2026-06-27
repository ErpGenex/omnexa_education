# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Inbound webhooks from Laravel TLMS."""

from __future__ import annotations

import hashlib
import hmac
import json

import frappe
from frappe import _


def _verify_signature(payload: bytes, signature: str | None) -> bool:
	secret = frappe.get_single("Education Settings").get_password("laravel_webhook_secret")
	if not secret:
		return False
	if not signature:
		return False
	expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
	return hmac.compare_digest(expected, signature.replace("sha256=", "").strip())


@frappe.whitelist(allow_guest=True)
def receive():
	request = frappe.local.request
	raw = request.get_data() or b"{}"
	signature = request.headers.get("X-ErpGenEx-Signature") or request.headers.get("X-Signature")
	if not _verify_signature(raw, signature):
		frappe.throw(_("Invalid webhook signature."), frappe.AuthenticationError)

	try:
		data = json.loads(raw.decode())
	except json.JSONDecodeError as exc:
		frappe.throw(_("Invalid JSON payload: {0}").format(exc))

	event = data.get("event")
	payload = data.get("data") or {}
	handler = {
		"grade.posted": _handle_grade_posted,
		"timetable.approved": _handle_timetable_approved,
		"attendance.recorded": _handle_attendance_recorded,
		"lesson.completed": _handle_lesson_completed,
	}.get(event)

	if not handler:
		return {"ok": True, "ignored": True, "event": event}

	result = handler(payload, data)
	return {"ok": True, "event": event, "result": result}


def _handle_grade_posted(payload: dict, envelope: dict) -> dict:
	if not frappe.db.exists("DocType", "Education Assessment Result"):
		return {"skipped": True}
	student = payload.get("student_external_id")
	course = payload.get("course_external_id")
	if not student:
		return {"skipped": True}
	doc = frappe.get_doc(
		{
			"doctype": "Education Assessment Result",
			"student": student,
			"assessment_plan": payload.get("assessment_external_id"),
			"score": payload.get("score"),
			"max_score": payload.get("max_score"),
			"remarks": f"Laravel TLMS · {envelope.get('timestamp', '')}",
		}
	)
	try:
		doc.insert(ignore_permissions=True)
	except frappe.DuplicateEntryError:
		return {"duplicate": True}
	return {"name": doc.name}


def _handle_timetable_approved(payload: dict, envelope: dict) -> dict:
	if not frappe.db.exists("DocType", "Education Timetable Entry"):
		return {"skipped": True}
	count = 0
	for period in payload.get("periods") or []:
		frappe.get_doc(
			{
				"doctype": "Education Timetable Entry",
				"section": period.get("section_external_id"),
				"subject": period.get("subject_external_id"),
				"teacher": period.get("teacher_external_id"),
				"day_of_week": period.get("day_of_week"),
				"start_time": period.get("start_time"),
				"end_time": period.get("end_time"),
				"room": period.get("room_external_id"),
			}
		).insert(ignore_permissions=True)
		count += 1
	return {"periods_created": count}


def _handle_attendance_recorded(payload: dict, envelope: dict) -> dict:
	if not frappe.db.exists("DocType", "Education Attendance Record"):
		return {"skipped": True}
	student = payload.get("student_external_id")
	if not student or not frappe.db.exists("Education Student", student):
		return {"skipped": True, "reason": "student_not_found"}
	status_map = {
		"present": "Present",
		"absent": "Absent",
		"late": "Late",
		"excused": "Excused",
		"remote": "Remote",
	}
	raw_status = (payload.get("status") or "present").lower()
	status = status_map.get(raw_status, "Present")
	attendance_date = payload.get("date") or payload.get("attendance_date") or frappe.utils.today()
	session = payload.get("session_external_id") or payload.get("attendance_session")
	filters = {"student": student, "attendance_date": attendance_date}
	if session and frappe.db.exists("Education Attendance Session", session):
		filters["attendance_session"] = session
	existing = frappe.db.get_value("Education Attendance Record", filters, "name")
	if existing:
		frappe.db.set_value("Education Attendance Record", existing, "status", status)
		return {"updated": existing}
	doc = frappe.get_doc(
		{
			"doctype": "Education Attendance Record",
			"student": student,
			"status": status,
			"attendance_date": attendance_date,
			"attendance_session": session if session and frappe.db.exists("Education Attendance Session", session) else None,
			"remarks": f"Laravel TLMS · {envelope.get('timestamp', '')}",
		}
	)
	doc.insert(ignore_permissions=True)
	return {"name": doc.name}


def _handle_lesson_completed(payload: dict, envelope: dict) -> dict:
	return {"logged": True, "lesson": payload.get("lesson_id")}
