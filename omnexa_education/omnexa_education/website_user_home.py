# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Send education portal website users to desk pages after login (not public /education)."""

from __future__ import annotations

import frappe

PORTAL_ROLE_HOME: dict[str, str] = {
	"Education Student Portal": "/app/education-student-portal",
	"Education Parent Portal": "/app/education-parent-mobile",
	"Teacher": "/app/education-teacher-gradebook",
	"Education Manager": "/app/education-workcenter",
	"Education User": "/app/education-admissions-portal",
	"Education Finance Officer": "/app/education-finance-desk",
}


def get_website_user_home_page(user: str) -> str | None:
	if not user or user == "Guest":
		return None
	for role in frappe.get_roles(user):
		path = PORTAL_ROLE_HOME.get(role)
		if path:
			return path
	return None
