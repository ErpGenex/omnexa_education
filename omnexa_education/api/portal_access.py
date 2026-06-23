# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Portal roles — DocPerm, branch access, page roles, and demo user wiring."""

from __future__ import annotations

import frappe
from frappe import _

PORTAL_ROLES = ("Education Student Portal", "Education Parent Portal")

# Read-only access for student/parent desk portals.
PORTAL_READ_DOCTYPES: dict[str, dict] = {
	"Education Settings": {"read": 1},
	"Education Student": {"read": 1},
	"Education Timetable Entry": {"read": 1},
	"Education Assessment Result": {"read": 1},
	"Education Assessment Plan": {"read": 1},
	"Education Portal Message": {"read": 1},
	"Education Announcement": {"read": 1},
	"Education Section": {"read": 1},
	"Education Grade Level": {"read": 1},
	"Education Institution": {"read": 1},
	"Education Attendance Session": {"read": 1},
	"Education Attendance Record": {"read": 1},
	"Education Report Card": {"read": 1},
	"Education Academic Year": {"read": 1},
	"Education Term": {"read": 1},
	"Education Subject": {"read": 1},
	"Education Course": {"read": 1},
}

PORTAL_ROLE_DOCTYPE_PERMS: list[tuple[str, str, dict]] = [
	("Sales Invoice", "Education Parent Portal", {"read": 1}),
	("Customer", "Education Parent Portal", {"read": 1}),
]


def ensure_portal_doctype_permissions() -> dict:
	"""Grant read permissions on portal-facing doctypes (idempotent)."""
	added = []
	for doctype, perms in PORTAL_READ_DOCTYPES.items():
		if not frappe.db.exists("DocType", doctype):
			continue
		meta = frappe.get_meta(doctype)
		existing = {(p.role, p.permlevel) for p in meta.permissions}
		for role in PORTAL_ROLES:
			if (role, 0) in existing:
				continue
			frappe.get_doc(
				{
					"doctype": "Custom DocPerm",
					"parent": doctype,
					"parenttype": "DocType",
					"parentfield": "permissions",
					"role": role,
					"permlevel": 0,
					**perms,
				}
			).insert(ignore_permissions=True)
			added.append(f"{doctype}:{role}")
	for doctype, role, perms in PORTAL_ROLE_DOCTYPE_PERMS:
		if not frappe.db.exists("DocType", doctype):
			continue
		meta = frappe.get_meta(doctype)
		existing = {(p.role, p.permlevel) for p in meta.permissions}
		if (role, 0) in existing:
			continue
		frappe.get_doc(
			{
				"doctype": "Custom DocPerm",
				"parent": doctype,
				"parenttype": "DocType",
				"parentfield": "permissions",
				"role": role,
				"permlevel": 0,
				**perms,
			}
		).insert(ignore_permissions=True)
		added.append(f"{doctype}:{role}")
	if added:
		frappe.clear_cache(doctype="DocType")
	return {"added": added, "count": len(added)}


def ensure_portal_roles_desk_access() -> None:
	for role in PORTAL_ROLES:
		if frappe.db.exists("Role", role):
			frappe.db.set_value("Role", role, "desk_access", 1, update_modified=False)


def ensure_user_branch_access(user: str, company: str, branch: str, *, is_default: int = 1) -> bool:
	if not user or not company or not branch:
		return False
	if not frappe.db.exists("DocType", "User Branch Access"):
		return False
	if frappe.db.exists("User Branch Access", {"user": user, "company": company, "branch": branch}):
		return False
	frappe.get_doc(
		{
			"doctype": "User Branch Access",
			"user": user,
			"company": company,
			"branch": branch,
			"is_default": int(is_default or 0),
		}
	).insert(ignore_permissions=True)
	return True


def _activate_portal_students(company: str, branch: str) -> int:
	updated = 0
	filters: dict = {"company": company, "status": "Active"}
	if branch:
		filters["branch"] = branch
	for row in frappe.get_all("Education Student", filters=filters, fields=["name", "account_access_status", "financial_hold"]):
		changes = {}
		if row.account_access_status not in ("Active",):
			changes["account_access_status"] = "Active"
		if row.financial_hold:
			changes["financial_hold"] = 0
		if changes:
			frappe.db.set_value("Education Student", row.name, changes, update_modified=False)
			updated += 1
	return updated


def ensure_full_portal_access(company: str | None = None, branch: str | None = None) -> dict:
	"""Roles, page access, DocPerms, branch access, and demo portal links."""
	from omnexa_education.api.education_portal_link import ensure_demo_portal_users_linked
	from omnexa_education.api.education_role_demo import ensure_education_roles, sync_journey_page_roles
	from omnexa_education.education_demo.education_demo_seed import _ensure_demo_user, _resolve_company_branch
	from omnexa_education.education_demo.role_specs import ROLE_SPECS

	company, branch = _resolve_company_branch(company, branch)
	roles_created = ensure_education_roles()
	ensure_portal_roles_desk_access()
	page_stats = sync_journey_page_roles()
	perm_stats = ensure_portal_doctype_permissions()

	branch_grants = []
	portal_users = []
	for spec in ROLE_SPECS:
		if spec.get("role") not in PORTAL_ROLES:
			continue
		email = _ensure_demo_user(spec, company, branch)
		portal_users.append(email)
		if ensure_user_branch_access(email, company, branch):
			branch_grants.append(email)

	link = ensure_demo_portal_users_linked(company=company, branch=branch)
	activated = _activate_portal_students(company, branch)
	frappe.db.commit()

	return {
		"ok": True,
		"company": company,
		"branch": branch,
		"roles_created": roles_created,
		"page_sync": page_stats,
		"permissions": perm_stats,
		"branch_grants": branch_grants,
		"portal_users": portal_users,
		"students_activated": activated,
		**link,
		"message": _("Student and parent portal access configured."),
	}


@frappe.whitelist()
def repair_portal_access(company: str | None = None, branch: str | None = None) -> dict:
	frappe.only_for(("System Manager", "Education Manager"))
	return ensure_full_portal_access(company=company, branch=branch)


def execute():
	return ensure_full_portal_access()
