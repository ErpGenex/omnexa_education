# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Redirect legacy www portal paths to Frappe desk pages."""

from __future__ import annotations

import frappe

DESK_PORTAL_PATHS: dict[str, str] = {
	"education-student-portal": "/app/education-student-portal",
	"education-parent-mobile": "/app/education-parent-mobile",
	"education-parent-portal": "/app/education-parent-mobile",
	"education-teacher-gradebook": "/app/education-teacher-gradebook",
	"education-workcenter": "/app/education-workcenter",
	"education-admissions-portal": "/app/education-admissions-portal",
}


def redirect_to_desk(page: str) -> None:
	target = DESK_PORTAL_PATHS.get(page)
	if not target:
		frappe.throw("Unknown portal", frappe.DoesNotExistError)
	qs = frappe.request.query_string if frappe.request else b""
	if qs:
		if isinstance(qs, bytes):
			qs = qs.decode()
		target = f"{target}?{qs}"
	frappe.local.flags.redirect_location = target
