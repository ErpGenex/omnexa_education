# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Parent portal account lifecycle — provision guardian users to ErpGenEx and Laravel."""

from __future__ import annotations

import json
import re

import frappe
from frappe import _
from frappe.utils import now_datetime

from omnexa_education.api import laravel_client


def _settings():
	return frappe.get_single("Education Settings")


def _normalize_email(email: str) -> str:
	return (email or "").strip().lower()


def _parent_external_id(guardian_email: str, company: str) -> str:
	safe = re.sub(r"[^a-z0-9]+", "-", _normalize_email(guardian_email))
	company_slug = re.sub(r"[^a-z0-9]+", "-", (company or "school").lower())
	return f"parent-{company_slug}-{safe}"[:140]


def _ensure_parent_user(guardian_email: str, guardian_name: str | None, role: str) -> str:
	email = _normalize_email(guardian_email)
	user = frappe.db.get_value("User", {"email": email}, "name")
	if not user:
		parts = (guardian_name or "Parent").split(" ", 1)
		user_doc = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": parts[0],
				"last_name": parts[1] if len(parts) > 1 else "",
				"send_welcome_email": 0,
				"user_type": "Website User",
				"enabled": 1,
			}
		)
		user_doc.insert(ignore_permissions=True)
		user = user_doc.name
	elif not frappe.db.get_value("User", user, "enabled"):
		frappe.db.set_value("User", user, "enabled", 1, update_modified=False)
	if role and not frappe.db.exists("Has Role", {"parent": user, "role": role}):
		frappe.get_doc({"doctype": "Has Role", "parent": user, "parenttype": "User", "role": role}).insert(
			ignore_permissions=True
		)
	return user


def build_laravel_parent_payload(guardian_email: str, students: list) -> dict:
	email = _normalize_email(guardian_email)
	first_student = frappe.get_doc("Education Student", students[0])
	guardian_name = first_student.guardian_name or "Parent"
	parts = guardian_name.split(" ", 1)
	student_ids = [s for s in students if frappe.db.exists("Education Student", s)]
	return {
		"external_id": _parent_external_id(email, first_student.company),
		"email": email,
		"first_name": parts[0],
		"last_name": parts[1] if len(parts) > 1 else "",
		"role": "parent",
		"institution_id": first_student.institution,
		"student_external_ids": student_ids,
		"account_status": "active",
		"_student_context": {
			"institution": first_student.institution,
			"company": first_student.company,
			"branch": first_student.branch,
		},
	}


@frappe.whitelist()
def provision_parent(guardian_email: str, trigger: str = "Manual") -> dict:
	email = _normalize_email(guardian_email)
	if not email:
		frappe.throw(_("Guardian email is required."))
	students = frappe.get_all("Education Student", filters={"guardian_email": email, "status": "Active"}, pluck="name")
	if not students:
		frappe.throw(_("No active students linked to guardian email {0}.").format(email))

	s = _settings()
	role = s.parent_user_role or "Education Parent Portal"
	user = _ensure_parent_user(email, frappe.db.get_value("Education Student", students[0], "guardian_name"), role)

	laravel_user_id = None
	laravel_synced = 0
	laravel_response = None
	if laravel_client.is_laravel_enabled():
		payload = build_laravel_parent_payload(email, students)
		result = laravel_client.provision_user(payload, payload.get("_student_context"))
		laravel_response = json.dumps(result, default=str)
		if result.get("ok"):
			laravel_synced = 1
			body = result.get("body") or {}
			if isinstance(body, dict):
				laravel_user_id = body.get("id") or body.get("laravel_user_id")
		else:
			laravel_client.enqueue_sync("provision", "User", user, payload)

	for student_name in students:
		updates = {"guardian_user": user}
		if laravel_user_id:
			updates["guardian_laravel_user_id"] = laravel_user_id
		frappe.db.set_value("Education Student", student_name, updates, update_modified=False)

	return {
		"guardian_email": email,
		"user": user,
		"students": students,
		"laravel_user_id": laravel_user_id,
		"laravel_synced": laravel_synced,
		"laravel_response": laravel_response,
	}


def auto_provision_parent_for_student(student_name: str):
	s = _settings()
	if not getattr(s, "auto_provision_parent_user", 1):
		return
	email = frappe.db.get_value("Education Student", student_name, "guardian_email")
	if not email:
		return
	try:
		provision_parent(email, trigger="Student Registration")
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Parent auto-provision failed")
