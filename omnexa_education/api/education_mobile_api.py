# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Mobile REST API — device tokens, parent/student home."""

from __future__ import annotations

import frappe
from frappe import _


@frappe.whitelist()
def register_device_token(device_id: str, platform: str, push_token: str | None = None) -> dict:
	if not (device_id and platform):
		frappe.throw(_("device_id and platform are required"))
	user = frappe.session.user
	existing = frappe.db.get_value(
		"Education Mobile Device Token",
		{"user": user, "device_id": device_id},
		"name",
	)
	if existing:
		doc = frappe.get_doc("Education Mobile Device Token", existing)
		doc.platform = platform
		doc.push_token = push_token
		doc.is_active = 1
		doc.save(ignore_permissions=True)
	else:
		doc = frappe.get_doc(
			{
				"doctype": "Education Mobile Device Token",
				"user": user,
				"device_id": device_id,
				"platform": platform,
				"push_token": push_token,
				"is_active": 1,
			}
		).insert(ignore_permissions=True)
	return {"name": doc.name, "registered": True}


@frappe.whitelist()
def get_mobile_config() -> dict:
	return {
		"pwa_manifest": "/assets/omnexa_education/pwa/manifest.json",
		"service_worker": "/assets/omnexa_education/pwa/sw.js",
		"rtl_css": "/assets/omnexa_education/css/education-rtl.css",
		"api_version": "global-sis-3",
		"offline_cache": True,
		"push_enabled": True,
	}


@frappe.whitelist()
def parent_mobile_home(student: str) -> dict:
	from omnexa_education.api.education_compliance import log_ferpa_access

	log_ferpa_access(student, "Parent Portal", student, "Parent mobile home")
	announcements = frappe.get_all(
		"Education Announcement",
		filters={"audience": ["in", ["All", "Parents"]]},
		fields=["title", "message", "publish_date"],
		order_by="publish_date desc",
		limit=10,
	)
	attendance = frappe.get_all(
		"Education Attendance Record",
		filters={"student": student},
		fields=["status", "date"],
		order_by="date desc",
		limit=5,
	)
	return {"student": student, "announcements": announcements, "recent_attendance": attendance}


@frappe.whitelist()
def student_mobile_home(student: str) -> dict:
	from omnexa_education.api.education_timetable import get_section_timetable

	section = frappe.db.get_value("Education Student Enrollment", {"student": student}, "section")
	timetable = get_section_timetable(section) if section else []
	return {"student": student, "section": section, "timetable": timetable}


@frappe.whitelist()
def api_list_students(institution: str | None = None, limit: int = 20) -> list[dict]:
	filters = {}
	if institution:
		filters["institution"] = institution
	return frappe.get_all(
		"Education Student",
		filters=filters,
		fields=["name", "student_name", "institution", "status"],
		limit=int(limit),
	)
