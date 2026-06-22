# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""LMS integration — Laravel TLMS + external providers."""

from __future__ import annotations

import frappe
from frappe import _

from omnexa_education.api import laravel_client
from omnexa_education.api.student_account_lifecycle import build_laravel_payload, provision_student


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
	student_doc = frappe.get_doc("Education Student", student)

	if doc.lms_provider == "Laravel TLMS":
		if student_doc.account_access_status not in ("Active", "Financial Hold"):
			provision_student(student, trigger="System")
			student_doc.reload()

		payload = build_laravel_payload(student_doc)
		course_code = frappe.db.get_value("Education Course", doc.course, "course_code") or doc.external_course_id
		payload["enrollments"] = [
			{
				"course_external_id": doc.external_course_id or course_code,
				"section_external_id": student_doc.section,
				"role": "student",
			}
		]
		if laravel_client.is_laravel_enabled():
			result = laravel_client.sync_enrollments(payload, {"institution": student_doc.institution})
			if not result.get("ok"):
				laravel_client.enqueue_sync("sync_enrollment", "Education Student", student, payload)
			return {
				"link": link,
				"student": student,
				"lms_provider": doc.lms_provider,
				"sync_status": "synced" if result.get("ok") else "queued",
				"laravel_response": result,
			}
		return {"link": link, "student": student, "sync_status": "laravel_disabled"}

	return {
		"link": link,
		"student": student,
		"lms_provider": doc.lms_provider,
		"external_course_id": doc.external_course_id,
		"sync_status": "queued",
		"sync_url": doc.sync_url,
	}


@frappe.whitelist()
def sync_all_laravel_enrollments(student: str) -> dict:
	links = frappe.get_all(
		"Education Lms Course Link",
		filters={"is_active": 1, "lms_provider": "Laravel TLMS"},
		pluck="name",
	)
	results = [sync_lms_enrollment(link, student) for link in links]
	return {"student": student, "count": len(results), "results": results}
