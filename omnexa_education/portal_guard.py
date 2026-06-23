# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Restrict student/parent portal users to allowed desk routes and APIs."""

from __future__ import annotations

import json

import frappe
from frappe import _

from omnexa_education.permissions import PORTAL_ROLES, STAFF_EDUCATION_ROLES, _portal_only

STUDENT_PORTAL_ROLE = "Education Student Portal"
PARENT_PORTAL_ROLE = "Education Parent Portal"

PORTAL_HOME_ROUTES: dict[str, str] = {
	STUDENT_PORTAL_ROLE: "/app/education-student-portal",
	PARENT_PORTAL_ROLE: "/app/education-parent-mobile",
}

# Workspace name/title must not slug-conflict with desk Pages (see frappe.desk.utils.validate_route_conflict).
LEGACY_PORTAL_WORKSPACES = frozenset({"education-student-portal", "education-parent-portal"})
PORTAL_WORKSPACE_SPECS: dict[str, dict] = {
	STUDENT_PORTAL_ROLE: {
		"name": "edu-ws-student",
		"title": "Edu Student Hub",
		"label": "Student Portal",
		"icon": "education-student",
	},
	PARENT_PORTAL_ROLE: {
		"name": "edu-ws-parent",
		"title": "Edu Parent Hub",
		"label": "Parent Portal",
		"icon": "education-parent",
	},
}

# Desk Page names (slug after /app/)
STUDENT_ALLOWED_PAGES = frozenset(
	{
		"education-student-portal",
		"education-timetable-board",
	}
)

PARENT_ALLOWED_PAGES = frozenset(
	{
		"education-parent-mobile",
		"education-timetable-board",
	}
)

# List/Form routes allowed for portal users (doctype slugs).
STUDENT_ALLOWED_DOCTYPES = frozenset(
	{
		"education-timetable-entry",
		"education-assessment-result",
	}
)

PARENT_ALLOWED_DOCTYPES = frozenset(
	{
		"education-timetable-entry",
		"education-assessment-result",
		"sales-invoice",
	}
)

# Staff-only whitelisted APIs — portal users get PermissionError.
STAFF_ONLY_API_PREFIXES = (
	"omnexa_education.api.education_portal_catalog.get_workcenter_context",
	"omnexa_education.api.journey_role_desks.get_finance_dashboard",
	"omnexa_education.api.journey_role_desks.get_admissions_dashboard",
	"omnexa_education.api.journey_role_desks.get_registrar_dashboard",
	"omnexa_education.api.journey_role_desks.get_teacher_dashboard",
	"omnexa_education.api.journey_role_desks.get_laravel_integration_dashboard",
	"omnexa_education.api.lifecycle_role_desks.",
	"omnexa_education.api.education_analytics.",
	"omnexa_education.api.education_demo.get_demo_hub_context",
	"omnexa_education.api.education_demo.seed_demo",
	"omnexa_education.api.portal_validation.",
	"omnexa_education.api.education_laravel_full_sync.",
	"omnexa_education.api.education_laravel_bootstrap.",
	"omnexa_education.api.laravel_client.process_sync_queue",
	"omnexa_education.api.education_portal_link.ensure_demo_portal_users_linked",
	"omnexa_education.api.education_portal_link.repair_portal_access",
	"omnexa_education.workspace.",
)


def portal_role_for_user(user: str | None = None) -> str | None:
	user = user or frappe.session.user
	if not user or user == "Guest":
		return None
	roles = set(frappe.get_roles(user))
	if STUDENT_PORTAL_ROLE in roles and not roles & STAFF_EDUCATION_ROLES:
		return STUDENT_PORTAL_ROLE
	if PARENT_PORTAL_ROLE in roles and not roles & STAFF_EDUCATION_ROLES:
		return PARENT_PORTAL_ROLE
	return None


def portal_allowed_pages(role: str | None) -> frozenset[str]:
	if role == STUDENT_PORTAL_ROLE:
		return STUDENT_ALLOWED_PAGES
	if role == PARENT_PORTAL_ROLE:
		return PARENT_ALLOWED_PAGES
	return frozenset()


def portal_allowed_doctypes(role: str | None) -> frozenset[str]:
	if role == STUDENT_PORTAL_ROLE:
		return STUDENT_ALLOWED_DOCTYPES
	if role == PARENT_PORTAL_ROLE:
		return PARENT_ALLOWED_DOCTYPES
	return frozenset()


def portal_home_route(user: str | None = None) -> str | None:
	role = portal_role_for_user(user)
	return PORTAL_HOME_ROUTES.get(role or "") if role else None


def is_staff_only_api(method: str) -> bool:
	return any(method.startswith(prefix) for prefix in STAFF_ONLY_API_PREFIXES)


def enforce_portal_api_access():
	"""Block portal-only users from staff education APIs."""
	if frappe.session.user in (None, "Guest"):
		return
	if not _portal_only():
		return
	path = getattr(getattr(frappe.local, "request", None), "path", "") or ""
	if not path.startswith("/api/method/"):
		return
	method = path[len("/api/method/") :].split("?", 1)[0].strip("/")
	if not method.startswith("omnexa_education."):
		return
	if is_staff_only_api(method):
		frappe.throw(_("Not permitted"), frappe.PermissionError)


def extend_bootinfo(bootinfo):
	"""Expose portal restrictions to desk JS."""
	role = portal_role_for_user()
	if not role:
		return
	bootinfo.education_portal = {
		"portal_only": True,
		"portal_role": role,
		"home_route": PORTAL_HOME_ROUTES[role],
		"allowed_pages": sorted(portal_allowed_pages(role)),
		"allowed_doctypes": sorted(portal_allowed_doctypes(role)),
	}


def remove_legacy_portal_workspaces() -> list[str]:
	"""Drop portal workspaces that slug-conflict with desk Pages."""
	removed = []
	for name in LEGACY_PORTAL_WORKSPACES:
		if not frappe.db.exists("Workspace", name):
			continue
		frappe.delete_doc("Workspace", name, force=True, ignore_permissions=True)
		removed.append(name)
	if removed:
		frappe.clear_cache(doctype="Workspace")
	return removed


def ensure_education_workspace_portal_roles() -> dict:
	"""Hide full Education workspace from portal users; add minimal student/parent workspaces."""
	from omnexa_education.api.education_role_demo import EDUCATION_STAFF_ROLES

	stats = {"education_roles_set": 0, "student_ws": False, "parent_ws": False, "legacy_removed": []}
	staff_roles = [r for r in EDUCATION_STAFF_ROLES if frappe.db.exists("Role", r)]
	stats["legacy_removed"] = remove_legacy_portal_workspaces()

	if frappe.db.exists("Workspace", "Education"):
		ws = frappe.get_doc("Workspace", "Education")
		ws.set("roles", [])
		for role in staff_roles:
			ws.append("roles", {"role": role})
		ws.flags.ignore_permissions = True
		ws.save()
		stats["education_roles_set"] = len(staff_roles)
		frappe.db.commit()

	stats["student_ws"] = False
	stats["parent_ws"] = False
	try:
		stats["student_ws"] = _ensure_portal_workspace(
			STUDENT_PORTAL_ROLE,
			[
				("Page", "education-student-portal", "Student Portal"),
				("Page", "education-timetable-board", "Timetable"),
				("DocType", "Education Timetable Entry", "My Timetable"),
				("DocType", "Education Assessment Result", "My Grades"),
			],
		)
	except Exception as exc:
		stats["student_ws_error"] = str(exc)[:200]
	try:
		stats["parent_ws"] = _ensure_portal_workspace(
			PARENT_PORTAL_ROLE,
			[
				("Page", "education-parent-mobile", "Parent Portal"),
				("Page", "education-timetable-board", "Timetable"),
				("DocType", "Education Assessment Result", "Children Grades"),
				("DocType", "Sales Invoice", "Invoices"),
			],
		)
	except Exception as exc:
		stats["parent_ws_error"] = str(exc)[:200]
	frappe.clear_cache(doctype="Workspace")
	return stats


def _ensure_portal_workspace(role: str, links: list[tuple]) -> bool:
	if not frappe.db.exists("Role", role):
		return False
	spec = PORTAL_WORKSPACE_SPECS[role]
	name = spec["name"]
	if frappe.db.exists("Workspace", name):
		ws = frappe.get_doc("Workspace", name)
	else:
		ws = frappe.new_doc("Workspace")
		ws.update(
			{
				"name": name,
				"label": spec["label"],
				"title": spec["title"],
				"module": "Omnexa Education",
				"icon": spec["icon"],
				"public": 0,
				"is_hidden": 0,
			}
		)
	ws.set("roles", [])
	ws.append("roles", {"role": role})
	ws.set("links", [])
	for link_type, link_to, link_label in links:
		ws.append(
			"links",
			{
				"type": "Link",
				"link_type": link_type,
				"link_to": link_to,
				"label": link_label,
				"hidden": 0,
				"onboard": 0,
				"is_query_report": 0,
			},
		)
	shortcuts = []
	content = [{"id": "hdr", "type": "header", "data": {"text": f"<b>{spec['label']}</b>", "col": 12}}]
	for idx, (_lt, link_to, link_label) in enumerate(links):
		shortcuts.append(
			{
				"type": "DocType" if _lt == "DocType" else "Page",
				"link_to": link_to,
				"label": link_label,
				"color": "Blue",
			}
		)
		content.append(
			{
				"id": f"sc{idx}",
				"type": "shortcut",
				"data": {"shortcut_name": link_label, "col": 4},
			}
		)
	ws.shortcuts = []
	for sc in shortcuts:
		ws.append("shortcuts", sc)

	ws.content = json.dumps(content, separators=(",", ":"))
	ws.flags.ignore_permissions = True
	if ws.is_new():
		ws.insert()
	else:
		ws.save()
	return True
