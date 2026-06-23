# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Education role provisioning — portal roles and demo workspaces."""

from __future__ import annotations

import frappe
from frappe import _

EDUCATION_ROLES = (
	"Education Student Portal",
	"Education Parent Portal",
	"Education Finance Officer",
)

JOURNEY_PAGE_ROLES: dict[str, list[str]] = {
	"education-workcenter": [
		"System Manager",
		"Education Manager",
		"Education User",
		"Teacher",
		"Accounts User",
		"Education Student Portal",
		"Education Parent Portal",
		"Education Finance Officer",
	],
	"education-finance-desk": ["System Manager", "Education Manager", "Accounts User", "Accounts Manager", "Company Admin", "Education Finance Officer"],
	"education-laravel-integration": ["System Manager", "Education Manager", "Company Admin"],
	"education-student-portal": ["System Manager", "Education Manager", "Education Student Portal", "Education User", "Teacher"],
	"education-parent-mobile": ["System Manager", "Education Manager", "Education Parent Portal", "Education User"],
	"education-teacher-gradebook": ["System Manager", "Education Manager", "Teacher", "Education User"],
	"education-registrar-desk": ["System Manager", "Education Manager", "Education User"],
	"education-admissions-portal": ["System Manager", "Education Manager", "Education User"],
	"education-timetable-board": ["System Manager", "Education Manager", "Teacher", "Education User"],
	"education-analytics-dashboard": ["System Manager", "Education Manager", "Education User"],
	"education-executive-dashboard": ["System Manager", "Education Manager", "Company Admin"],
	"education-graduation-desk": ["System Manager", "Education Manager", "Education User"],
	"education-alumni-desk": ["System Manager", "Education Manager", "Education User"],
	"education-qa-desk": ["System Manager", "Education Manager", "Education User"],
}


def _ensure_role(role_name: str) -> None:
	if frappe.db.exists("Role", role_name):
		return
	frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1}).insert(ignore_permissions=True)


def ensure_education_roles() -> list[str]:
	created = []
	for role in EDUCATION_ROLES:
		if not frappe.db.exists("Role", role):
			_ensure_role(role)
			created.append(role)
	return created


def sync_journey_page_roles() -> dict:
	ensure_education_roles()
	stats = {"pages": 0, "roles_added": 0}
	for page_name, roles in JOURNEY_PAGE_ROLES.items():
		if not frappe.db.exists("Page", page_name):
			continue
		page = frappe.get_doc("Page", page_name)
		existing = {r.role for r in page.roles}
		for role in roles:
			if role not in existing and frappe.db.exists("Role", role):
				page.append("roles", {"role": role})
				stats["roles_added"] += 1
		page.save(ignore_permissions=True)
		stats["pages"] += 1
	return stats


@frappe.whitelist()
def seed_education_roles() -> dict:
	frappe.only_for("System Manager")
	roles = ensure_education_roles()
	page_stats = sync_journey_page_roles()
	return {"roles_created": roles, "page_sync": page_stats}


@frappe.whitelist()
def seed_education_full_demo(company: str | None = None, branch: str | None = None) -> dict:
	"""Roles + 5 institution types + demo users."""
	from omnexa_education.education_demo.education_demo_seed import seed_education_demo

	return seed_education_demo(company=company, branch=branch)
