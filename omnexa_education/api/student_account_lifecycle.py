# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Student portal account lifecycle — provision, suspend, resume, financial hold."""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import now_datetime

from omnexa_education.api import laravel_client


ACCOUNT_STATUSES = (
	"Not Provisioned",
	"Provisioning",
	"Active",
	"Financial Hold",
	"Suspended",
	"Withdrawn",
)


def _settings():
	return frappe.get_single("Education Settings")


def _student_email(student) -> str:
	if student.user and frappe.db.exists("User", student.user):
		email = frappe.db.get_value("User", student.user, "email")
		if email:
			return email.strip().lower()
	safe_code = (student.student_code or "student").replace(" ", "").lower()
	company = (student.company or "school").replace(" ", "").lower()
	return f"{safe_code}@{company}.students.local"


def _student_context(student) -> dict:
	return {
		"institution": student.institution,
		"company": student.company,
		"branch": student.branch,
	}


def _log_access(student_name: str, action: str, trigger: str, before: str, after: str, **kwargs):
	frappe.get_doc(
		{
			"doctype": "Education Account Access Log",
			"student": student_name,
			"action": action,
			"trigger_source": trigger,
			"status_before": before,
			"status_after": after,
			"performed_by": frappe.session.user if frappe.session.user else "Administrator",
			"success": kwargs.get("success", 1),
			"laravel_synced": kwargs.get("laravel_synced", 0),
			"remarks": kwargs.get("remarks"),
			"laravel_response": kwargs.get("laravel_response"),
		}
	).insert(ignore_permissions=True)


def _set_user_enabled(user: str | None, enabled: int):
	if not user or not frappe.db.exists("User", user):
		return
	frappe.db.set_value("User", user, "enabled", enabled, update_modified=False)


def _ensure_portal_user(student, role: str) -> str:
	email = _student_email(student)
	if student.user and frappe.db.exists("User", student.user):
		user = student.user
	else:
		user = frappe.db.get_value("User", {"email": email}, "name")
	if not user:
		parts = (student.student_name or "Student").split(" ", 1)
		user_doc = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": parts[0],
				"last_name": parts[1] if len(parts) > 1 else "",
				"send_welcome_email": 0,
				"user_type": "Website User",
				"enabled": 0,
			}
		)
		user_doc.insert(ignore_permissions=True)
		user = user_doc.name
	if role and not frappe.db.exists("Has Role", {"parent": user, "role": role}):
		frappe.get_doc({"doctype": "Has Role", "parent": user, "parenttype": "User", "role": role}).insert(
			ignore_permissions=True
		)
	student.db_set("user", user, update_modified=False)
	return user


def build_laravel_payload(student) -> dict:
	enrollments = []
	if frappe.db.exists("DocType", "Education Course Enrollment"):
		section = student.section
		for row in frappe.get_all(
			"Education Course Enrollment",
			filters={"student": student.name, "docstatus": ["!=", 2]},
			fields=["course"],
		):
			course_code = frappe.db.get_value("Education Course", row.course, "course_code") if row.course else row.course
			enrollments.append(
				{
					"student_external_id": student.name,
					"course_external_id": course_code or row.course,
					"section_external_id": section,
					"role": "student",
				}
			)
	grade = frappe.db.get_value("Education Grade Level", student.grade_level, "grade_name") if student.grade_level else ""
	program = None
	if frappe.db.exists("DocType", "Education Student Enrollment"):
		program = frappe.db.get_value(
			"Education Student Enrollment",
			{"student": student.name, "enrollment_status": "Enrolled", "docstatus": 1},
			"program",
		)
	return {
		"external_id": student.name,
		"student_external_id": student.name,
		"student_code": student.student_code,
		"email": _student_email(student),
		"first_name": (student.student_name or "").split(" ", 1)[0],
		"last_name": (student.student_name or "").split(" ", 1)[-1] if student.student_name and " " in student.student_name else "",
		"role": "student",
		"institution_id": student.institution,
		"institution_type": frappe.db.get_value("Education Institution", student.institution, "institution_type"),
		"program_id": program,
		"grade_level": grade or student.grade_level,
		"section": student.section,
		"account_status": "active",
		"enrollments": enrollments,
		"academic_model": "university" if program else "k12",
		"_student_context": _student_context(student),
	}


@frappe.whitelist()
def provision_student(student: str, trigger: str = "Manual") -> dict:
	student_doc = frappe.get_doc("Education Student", student)
	before = student_doc.account_access_status or "Not Provisioned"
	if student_doc.status in ("Withdrawn", "Graduated"):
		frappe.throw(_("Cannot provision a withdrawn or graduated student."))

	s = _settings()
	role = s.student_user_role or "Education Student Portal"
	student_doc.db_set("account_access_status", "Provisioning", update_modified=False)
	user = _ensure_portal_user(student_doc, role)
	_set_user_enabled(user, 1)

	laravel_synced = 0
	laravel_response = None
	laravel_user_id = student_doc.laravel_user_id
	if laravel_client.is_laravel_enabled():
		payload = build_laravel_payload(student_doc)
		if frappe.get_single("Education Settings").laravel_api_key:
			result = laravel_client.provision_user(payload, _student_context(student_doc))
			laravel_response = json.dumps(result, default=str)
			if result.get("ok"):
				laravel_synced = 1
				body = result.get("body") or {}
				if isinstance(body, dict):
					laravel_user_id = body.get("id") or body.get("laravel_user_id") or laravel_user_id
			else:
				if result.get("throttled") or (result.get("error") or "").lower().find("throttl") >= 0:
					import time

					time.sleep(1.5)
				laravel_client.enqueue_sync("provision", "Education Student", student, payload)

	student_doc.db_set(
		{
			"account_access_status": "Active",
			"laravel_user_id": laravel_user_id,
			"financial_hold": 0,
			"financial_hold_reason": "",
			"last_laravel_sync_at": now_datetime(),
		},
		update_modified=False,
	)
	_log_access(student, "Provision", trigger, before, "Active", laravel_synced=laravel_synced, laravel_response=laravel_response)
	return {"student": student, "user": user, "account_access_status": "Active", "laravel_synced": laravel_synced}


@frappe.whitelist()
def suspend_student(student: str, reason: str = "", trigger: str = "Manual") -> dict:
	student_doc = frappe.get_doc("Education Student", student)
	before = student_doc.account_access_status or "Active"
	_set_user_enabled(student_doc.user, 0)
	laravel_synced = 0
	laravel_response = None
	if laravel_client.is_laravel_enabled() and student_doc.laravel_user_id:
		result = laravel_client.suspend_user(student_doc.laravel_user_id, reason, _student_context(student_doc))
		laravel_response = json.dumps(result, default=str)
		laravel_synced = 1 if result.get("ok") else 0
		if not result.get("ok"):
			laravel_client.enqueue_sync(
				"suspend",
				"Education Student",
				student,
				{"laravel_user_id": student_doc.laravel_user_id, "reason": reason, "_student_context": _student_context(student_doc)},
			)
	student_doc.db_set(
		{
			"account_access_status": "Suspended",
			"last_laravel_sync_at": now_datetime(),
		},
		update_modified=False,
	)
	_log_access(student, "Suspend", trigger, before, "Suspended", laravel_synced=laravel_synced, laravel_response=laravel_response, remarks=reason)
	return {"student": student, "account_access_status": "Suspended"}


@frappe.whitelist()
def resume_student(student: str, trigger: str = "Manual") -> dict:
	student_doc = frappe.get_doc("Education Student", student)
	if student_doc.financial_hold:
		frappe.throw(_("Clear financial hold before resuming access."))
	before = student_doc.account_access_status or "Suspended"
	_set_user_enabled(student_doc.user, 1)
	laravel_synced = 0
	laravel_response = None
	if laravel_client.is_laravel_enabled() and student_doc.laravel_user_id:
		result = laravel_client.resume_user(student_doc.laravel_user_id, _student_context(student_doc))
		laravel_response = json.dumps(result, default=str)
		laravel_synced = 1 if result.get("ok") else 0
		if not result.get("ok"):
			laravel_client.enqueue_sync(
				"resume",
				"Education Student",
				student,
				{"laravel_user_id": student_doc.laravel_user_id, "_student_context": _student_context(student_doc)},
			)
	student_doc.db_set(
		{
			"account_access_status": "Active",
			"last_laravel_sync_at": now_datetime(),
		},
		update_modified=False,
	)
	_log_access(student, "Resume", trigger, before, "Active", laravel_synced=laravel_synced, laravel_response=laravel_response)
	return {"student": student, "account_access_status": "Active"}


def apply_financial_hold(student: str, reason: str, trigger: str = "Financial") -> dict:
	student_doc = frappe.get_doc("Education Student", student)
	before = student_doc.account_access_status or "Active"
	_set_user_enabled(student_doc.user, 0)
	laravel_synced = 0
	laravel_response = None
	if laravel_client.is_laravel_enabled() and student_doc.laravel_user_id:
		result = laravel_client.suspend_user(student_doc.laravel_user_id, reason, _student_context(student_doc))
		laravel_response = json.dumps(result, default=str)
		laravel_synced = 1 if result.get("ok") else 0
	student_doc.db_set(
		{
			"account_access_status": "Financial Hold",
			"financial_hold": 1,
			"financial_hold_reason": reason,
			"last_laravel_sync_at": now_datetime(),
		},
		update_modified=False,
	)
	_log_access(
		student,
		"Financial Hold",
		trigger,
		before,
		"Financial Hold",
		laravel_synced=laravel_synced,
		laravel_response=laravel_response,
		remarks=reason,
	)
	return {"student": student, "account_access_status": "Financial Hold"}


def release_financial_hold(student: str, trigger: str = "Financial") -> dict:
	student_doc = frappe.get_doc("Education Student", student)
	before = student_doc.account_access_status or "Financial Hold"
	student_doc.db_set({"financial_hold": 0, "financial_hold_reason": ""}, update_modified=False)
	if student_doc.status in ("Withdrawn", "Graduated"):
		return suspend_student(student, reason="Student withdrawn", trigger=trigger)
	return resume_student(student, trigger=trigger)


def deprovision_student(student: str, trigger: str = "Withdrawal") -> dict:
	student_doc = frappe.get_doc("Education Student", student)
	before = student_doc.account_access_status or "Active"
	_set_user_enabled(student_doc.user, 0)
	student_doc.db_set({"account_access_status": "Withdrawn"}, update_modified=False)
	_log_access(student, "Deprovision", trigger, before, "Withdrawn")
	return {"student": student, "account_access_status": "Withdrawn"}


def auto_provision_if_needed(student_name: str):
	s = _settings()
	if not s.auto_provision_student_user:
		return
	student = frappe.get_doc("Education Student", student_name)
	if student.status != "Active":
		return
	if student.account_access_status in (None, "", "Not Provisioned"):
		provision_student(student_name, trigger="Admission")


@frappe.whitelist()
def bulk_suspend_overdue(company: str | None = None, branch: str | None = None) -> dict:
	from omnexa_education.financial_hold import get_overdue_students

	count = 0
	for row in get_overdue_students(company=company, branch=branch):
		apply_financial_hold(row["student"], row["reason"], trigger="Financial")
		count += 1
	return {"suspended": count}


@frappe.whitelist()
def bulk_provision_students(
	company: str | None = None,
	branch: str | None = None,
	institution: str | None = None,
) -> dict:
	"""Provision all active students to ErpGenEx User + Laravel."""
	filters: dict = {"status": "Active"}
	if company:
		filters["company"] = company
	if branch:
		filters["branch"] = branch
	if institution:
		filters["institution"] = institution

	names = frappe.get_all("Education Student", filters=filters, pluck="name", limit=500)
	ok = failed = skipped = 0
	laravel_on = laravel_client.is_laravel_enabled()
	for name in names:
		row = frappe.db.get_value(
			"Education Student",
			name,
			["account_access_status", "user", "laravel_user_id"],
			as_dict=True,
		)
		if row and row.account_access_status == "Active" and row.user and (not laravel_on or row.laravel_user_id):
			skipped += 1
			continue
		try:
			provision_student(name, trigger="System")
			ok += 1
		except Exception:
			failed += 1
			frappe.log_error(frappe.get_traceback(), f"Bulk provision failed: {name}")
	return {"provisioned": ok, "failed": failed, "skipped": skipped, "total": len(names)}
