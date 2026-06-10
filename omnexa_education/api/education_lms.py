# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""LMS integration — Moodle/Canvas/Google Classroom sync links."""

from __future__ import annotations

import frappe
from frappe import _


@frappe.whitelist()
def register_lms_course(
	course: str,
	lms_provider: str,
	external_course_id: str,
	sync_url: str | None = None,
) -> dict:
	course_doc = frappe.get_doc("Education Course", course)
	doc = frappe.get_doc(
		{
			"doctype": "Education Lms Course Link",
			"course": course,
			"lms_provider": lms_provider,
			"external_course_id": external_course_id,
			"sync_url": sync_url,
			"institution": course_doc.institution,
			"company": course_doc.company,
			"branch": course_doc.branch,
			"is_active": 1,
		}
	).insert(ignore_permissions=True)
	return {"link": doc.name}


@frappe.whitelist()
def list_lms_links(institution: str | None = None) -> list[dict]:
	filters = {"is_active": 1}
	if institution:
		filters["institution"] = institution
	return frappe.get_all(
		"Education Lms Course Link",
		filters=filters,
		fields=["name", "course", "lms_provider", "external_course_id", "sync_url"],
	)


@frappe.whitelist()
def sync_lms_enrollment(link: str, student: str) -> dict:
	doc = frappe.get_doc("Education Lms Course Link", link)
	return {
		"link": link,
		"student": student,
		"lms_provider": doc.lms_provider,
		"external_course_id": doc.external_course_id,
		"sync_status": "queued",
		"sync_url": doc.sync_url,
	}
