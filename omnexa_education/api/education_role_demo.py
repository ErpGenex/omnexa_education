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

EDUCATION_STAFF_ROLES = (
	"System Manager",
	"Education Manager",
	"Education User",
	"Teacher",
	"Company Admin",
	"Accounts User",
	"Accounts Manager",
	"Education Finance Officer",
)

JOURNEY_PAGE_ROLES: dict[str, list[str]] = {
	"education-workcenter": list(EDUCATION_STAFF_ROLES),
	"education-finance-desk": [
		"System Manager",
		"Education Manager",
		"Accounts User",
		"Accounts Manager",
		"Company Admin",
		"Education Finance Officer",
	],
	"education-laravel-integration": [
		"System Manager",
		"Education Manager",
		"Company Admin",
		"Education User",
	],
	"education-student-portal": [
		"System Manager",
		"Education Manager",
		"Education Student Portal",
		"Education User",
		"Teacher",
	],
	"education-parent-mobile": [
		"System Manager",
		"Education Manager",
		"Education Parent Portal",
		"Education User",
	],
	"education-teacher-gradebook": [
		"System Manager",
		"Education Manager",
		"Teacher",
		"Education User",
	],
	"education-registrar-desk": ["System Manager", "Education Manager", "Education User"],
	"education-admissions-portal": ["System Manager", "Education Manager", "Education User"],
	"education-timetable-board": [
		"System Manager",
		"Education Manager",
		"Teacher",
		"Education User",
		"Education Student Portal",
		"Education Parent Portal",
	],
	"education-analytics-dashboard": ["System Manager", "Education Manager", "Education User"],
	"education-executive-dashboard": ["System Manager", "Education Manager", "Company Admin"],
	"education-graduation-desk": ["System Manager", "Education Manager", "Education User"],
	"education-alumni-desk": ["System Manager", "Education Manager", "Education User"],
	"education-qa-desk": ["System Manager", "Education Manager", "Education User"],
}

# Default roles for any education-* Page not listed above.
EDUCATION_PAGE_DEFAULT_ROLES = list(EDUCATION_STAFF_ROLES)

PORTAL_ONLY_ROLES = frozenset({"Education Student Portal", "Education Parent Portal"})
STAFF_ONLY_PAGES = frozenset(
	{
		"education-workcenter",
		"education-finance-desk",
		"education-laravel-integration",
		"education-teacher-gradebook",
		"education-registrar-desk",
		"education-admissions-portal",
		"education-analytics-dashboard",
		"education-executive-dashboard",
		"education-graduation-desk",
		"education-alumni-desk",
		"education-qa-desk",
	}
)


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


def _ensure_staff_roles_desk_access() -> None:
	for role in EDUCATION_STAFF_ROLES:
		if frappe.db.exists("Role", role):
			frappe.db.set_value("Role", role, "desk_access", 1, update_modified=False)


def _education_page_names() -> list[str]:
	return frappe.get_all("Page", filters={"name": ["like", "education-%"]}, pluck="name", order_by="name asc")


def sync_journey_page_roles() -> dict:
	ensure_education_roles()
	_ensure_staff_roles_desk_access()
	stats = {"pages": 0, "roles_added": 0, "roles_removed": 0, "pages_skipped": 0}
	known_pages = set(JOURNEY_PAGE_ROLES)
	for page_name in _education_page_names():
		if page_name not in known_pages:
			stats["pages_skipped"] += 1
			continue
		roles = JOURNEY_PAGE_ROLES[page_name]
		page = frappe.get_doc("Page", page_name)
		dirty = False
		if page_name in STAFF_ONLY_PAGES:
			for row in list(page.roles):
				if row.role in PORTAL_ONLY_ROLES:
					page.remove(row)
					stats["roles_removed"] += 1
					dirty = True
		existing = {r.role for r in page.roles}
		for role in roles:
			if role not in existing and frappe.db.exists("Role", role):
				page.append("roles", {"role": role})
				stats["roles_added"] += 1
				dirty = True
		if dirty:
			_save_page_roles(page)
		stats["pages"] += 1
	return stats


def _save_page_roles(page) -> None:
	"""Save Page role rows without route slug validation (provisioning only)."""
	prev = getattr(frappe.flags, "in_migrate", False)
	frappe.flags.in_migrate = True
	try:
		page.save(ignore_permissions=True)
	finally:
		frappe.flags.in_migrate = prev


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
