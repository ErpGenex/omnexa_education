# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Link demo portal users (student/parent) to Education Student records."""

from __future__ import annotations

import frappe
from frappe import _

from omnexa_education.education_demo.education_demo_seed import _link_portal_users, _resolve_company_branch
from omnexa_education.education_demo.role_specs import DEMO_PASSWORD, ROLE_SPECS


def _demo_emails() -> tuple[str, str]:
	student = "student@demo.education"
	parent = "parent@demo.education"
	for spec in ROLE_SPECS:
		if spec.get("role") == "Education Student Portal" and spec.get("email"):
			student = spec["email"]
		if spec.get("role") == "Education Parent Portal" and spec.get("email"):
			parent = spec.get("guardian_email") or spec["email"]
	return student, parent


@frappe.whitelist()
def repair_portal_access(company: str | None = None, branch: str | None = None) -> dict:
	"""Fix page roles, portal user roles, and student/parent links."""
	frappe.only_for(("System Manager", "Education Manager"))
	from omnexa_education.api.education_role_demo import ensure_education_roles, sync_journey_page_roles

	roles = ensure_education_roles()
	page_stats = sync_journey_page_roles()
	link = ensure_demo_portal_users_linked(company=company, branch=branch)
	return {
		"ok": True,
		"roles_ensured": roles,
		"page_sync": page_stats,
		**link,
		"message": _("Portal access repaired. Log out and sign in as {0} or {1}.").format(
			link.get("student_email"), link.get("parent_email")
		),
	}


@frappe.whitelist()
def ensure_demo_portal_users_linked(company: str | None = None, branch: str | None = None) -> dict:
	"""Ensure student@demo / parent@demo accounts have linked Education Student rows."""
	company, branch = _resolve_company_branch(company, branch)
	student_email, parent_email = _demo_emails()

	_link_portal_users(company, branch)

	student_linked = frappe.db.get_value("Education Student", {"user": student_email}, "name")
	if not student_linked and frappe.db.exists("User", student_email):
		filters: dict = {"company": company, "status": "Active"}
		if branch:
			filters["branch"] = branch
		candidate = frappe.db.get_value("Education Student", filters, "name", order_by="creation asc")
		if candidate:
			frappe.db.set_value("Education Student", candidate, "user", student_email, update_modified=False)
			student_linked = candidate

	parent_children = frappe.get_all(
		"Education Student",
		filters={"guardian_email": parent_email, "status": "Active"},
		pluck="name",
		limit=5,
	)
	if not parent_children and student_linked and frappe.db.exists("User", parent_email):
		current_guardian = frappe.db.get_value("Education Student", student_linked, "guardian_email")
		if not current_guardian:
			frappe.db.set_value(
				"Education Student",
				student_linked,
				{"guardian_email": parent_email, "guardian_name": "Layla Parent"},
				update_modified=False,
			)
			parent_children = [student_linked]

	frappe.db.commit()
	return {
		"student_email": student_email,
		"parent_email": parent_email,
		"student_linked": student_linked,
		"parent_children": len(parent_children),
		"demo_password": DEMO_PASSWORD,
	}


@frappe.whitelist()
def get_portal_empty_hint() -> dict:
	"""Hints for empty student/parent portal views."""
	link = ensure_demo_portal_users_linked()
	user = frappe.session.user
	student_linked = frappe.db.get_value("Education Student", {"user": user}, "name")
	parent_children = frappe.db.count("Education Student", {"guardian_email": user, "status": "Active"})
	return {
		"current_user": user,
		"student_linked": student_linked,
		"parent_children": parent_children,
		"demo_student_email": link.get("student_email"),
		"demo_parent_email": link.get("parent_email"),
		"demo_password": link.get("demo_password"),
		"can_manage": frappe.session.user == "Administrator"
		or "System Manager" in frappe.get_roles()
		or "Education Manager" in frappe.get_roles(),
	}


def execute():
	return ensure_demo_portal_users_linked()
