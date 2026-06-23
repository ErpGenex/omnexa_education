# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Validate all education role portal pages and APIs."""

from __future__ import annotations

import frappe

from omnexa_education.api.education_portal_catalog import get_portal_catalog
from omnexa_education.education_enhancement.lifecycle_catalog import FULL_LIFECYCLE_STEPS, ROLE_HOME_ROUTES


PORTAL_PAGES = [
	"education-workcenter",
	"education-finance-desk",
	"education-laravel-integration",
	"education-admissions-portal",
	"education-registrar-desk",
	"education-teacher-gradebook",
	"education-student-portal",
	"education-parent-mobile",
	"education-timetable-board",
	"education-executive-dashboard",
	"education-analytics-dashboard",
	"education-graduation-desk",
	"education-alumni-desk",
	"education-qa-desk",
]

PORTAL_APIS = [
	"omnexa_education.api.education_portal_catalog.get_workcenter_context",
	"omnexa_education.api.journey_role_desks.get_admissions_dashboard",
	"omnexa_education.api.journey_role_desks.get_registrar_dashboard",
	"omnexa_education.api.journey_role_desks.get_finance_dashboard",
	"omnexa_education.api.journey_role_desks.get_teacher_dashboard",
	"omnexa_education.api.journey_role_desks.get_student_portal_dashboard",
	"omnexa_education.api.journey_role_desks.get_parent_portal_dashboard",
	"omnexa_education.api.journey_role_desks.get_laravel_integration_dashboard",
	"omnexa_education.api.lifecycle_role_desks.get_graduation_dashboard",
	"omnexa_education.api.lifecycle_role_desks.get_alumni_dashboard",
	"omnexa_education.api.lifecycle_role_desks.get_qa_dashboard",
	"omnexa_education.api.education_admissions.get_public_apply_context",
	"omnexa_education.api.education_analytics.get_executive_dashboard",
	"omnexa_education.api.education_analytics.evaluate_at_risk_students",
	"omnexa_education.api.education_demo.get_demo_hub_context",
	"omnexa_education.api.education_unified_inbox.get_unified_inbox",
	"omnexa_education.api.laravel_integration_e2e.run_laravel_integration_e2e",
]


@frappe.whitelist()
def validate_all_portals() -> dict:
	"""Smoke-test portal pages, catalog, lifecycle routes, role homes."""
	pages = []
	for name in PORTAL_PAGES:
		exists = bool(frappe.db.exists("Page", name))
		pages.append({"page": name, "exists": exists, "route": f"/app/{name}"})

	catalog = get_portal_catalog(include_missing=1)
	missing_portals = [p for p in catalog if not p.get("exists")]

	lifecycle = []
	for step in FULL_LIFECYCLE_STEPS:
		route = step.get("route") or ""
		ok = True
		if route.startswith("/app/"):
			ok = bool(frappe.db.exists("Page", route.replace("/app/", "")))
		lifecycle.append({"key": step["key"], "route": route, "ok": ok, "external": bool(step.get("external"))})

	role_homes = []
	for role, route in ROLE_HOME_ROUTES.items():
		page = route.replace("/app/", "")
		role_homes.append({"role": role, "route": route, "page_exists": bool(frappe.db.exists("Page", page))})

	api_results = []
	for method in PORTAL_APIS:
		try:
			frappe.get_attr(method)()
			api_results.append({"method": method, "ok": True})
		except Exception as exc:
			api_results.append({"method": method, "ok": False, "error": str(exc)[:200]})

	pages_ok = sum(1 for p in pages if p["exists"])
	apis_ok = sum(1 for a in api_results if a["ok"])
	score = round((pages_ok / max(len(pages), 1) * 50 + apis_ok / max(len(PORTAL_APIS), 1) * 50), 1)

	return {
		"ok": pages_ok == len(pages) and not missing_portals,
		"portal_score": score,
		"pages": pages,
		"pages_ok": pages_ok,
		"pages_total": len(pages),
		"missing_catalog_portals": missing_portals,
		"lifecycle_routes": lifecycle,
		"role_home_routes": role_homes,
		"apis": api_results,
		"external_apply": "/education/apply",
		"demo_password": "Education@Demo2026",
	}
