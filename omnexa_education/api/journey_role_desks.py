# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Role-based education workcenter dashboards."""

from __future__ import annotations

import frappe
from frappe.utils import flt, today

from omnexa_education.api import laravel_client
from omnexa_education.financial_hold import get_overdue_students


def _scope(company: str | None, branch: str | None) -> tuple[str, str]:
	return (
		company or frappe.defaults.get_user_default("Company") or "",
		branch or frappe.defaults.get_user_default("Branch") or "",
	)


@frappe.whitelist()
def get_finance_dashboard(company: str | None = None, branch: str | None = None) -> dict:
	company, branch = _scope(company, branch)
	student_filters = {"status": "Active"}
	if company:
		student_filters["company"] = company
	if branch:
		student_filters["branch"] = branch

	total_students = frappe.db.count("Education Student", student_filters)
	on_hold = frappe.db.count("Education Student", {**student_filters, "financial_hold": 1})
	suspended = frappe.db.count("Education Student", {**student_filters, "account_access_status": "Suspended"})
	active_portal = frappe.db.count("Education Student", {**student_filters, "account_access_status": "Active"})
	overdue_rows = get_overdue_students(company=company or None, branch=branch or None)

	outstanding = 0.0
	if frappe.db.exists("DocType", "Sales Invoice"):
		conds = ["docstatus = 1", "outstanding_amount > 0"]
		vals: list = []
		if company:
			conds.append("company = %s")
			vals.append(company)
		row = frappe.db.sql(
			f"SELECT SUM(outstanding_amount) FROM `tabSales Invoice` WHERE {' AND '.join(conds)}",
			vals,
			as_dict=True,
		)
		outstanding = flt(row[0]["SUM(outstanding_amount)"]) if row else 0.0

	recent_logs = frappe.get_all(
		"Education Account Access Log",
		fields=["name", "student", "action", "status_after", "modified"],
		order_by="modified desc",
		limit=15,
	)

	settings = frappe.get_single("Education Settings")
	return {
		"total_students": total_students,
		"active_portal": active_portal,
		"financial_hold": on_hold,
		"suspended": suspended,
		"overdue_candidates": len(overdue_rows),
		"outstanding_fees": outstanding,
		"laravel_enabled": bool(settings.enable_laravel_tlms),
		"laravel_ping_status": settings.laravel_last_ping_status,
		"overdue_students": overdue_rows[:20],
		"recent_access_logs": recent_logs,
	}


@frappe.whitelist()
def get_laravel_integration_dashboard() -> dict:
	settings = frappe.get_single("Education Settings")
	queue_stats = {"queued": 0, "failed": 0, "success": 0}
	if frappe.db.exists("DocType", "Education Laravel Sync Queue"):
		for status in ("Queued", "Failed", "Success"):
			queue_stats[status.lower()] = frappe.db.count("Education Laravel Sync Queue", {"status": status})

	links = frappe.get_all(
		"Education Lms Course Link",
		filters={"is_active": 1, "lms_provider": "Laravel TLMS"},
		fields=["name", "course", "external_course_id"],
		limit=20,
	)
	return {
		"enable_laravel_tlms": bool(settings.enable_laravel_tlms),
		"laravel_base_url": settings.laravel_base_url,
		"laravel_last_ping_at": settings.laravel_last_ping_at,
		"laravel_last_ping_status": settings.laravel_last_ping_status,
		"queue_stats": queue_stats,
		"lms_links": links,
		"webhook_url": frappe.utils.get_url(
			"/api/method/omnexa_education.api.laravel_webhooks.receive"
		),
	}


@frappe.whitelist()
def get_parent_portal_dashboard(student: str | None = None) -> dict:
	user = frappe.session.user
	if not student:
		student = frappe.db.get_value("Education Student", {"guardian_email": user}, "name")
	out = {"student": student, "grades": [], "attendance": [], "invoices": []}
	if not student:
		return out
	st = frappe.get_doc("Education Student", student)
	out["student_name"] = st.student_name
	out["account_access_status"] = st.account_access_status
	out["financial_hold"] = st.financial_hold
	if st.customer and frappe.db.exists("DocType", "Sales Invoice"):
		out["invoices"] = frappe.get_all(
			"Sales Invoice",
			filters={"customer": st.customer, "docstatus": 1},
			fields=["name", "posting_date", "grand_total", "outstanding_amount", "status"],
			order_by="posting_date desc",
			limit=10,
		)
	if frappe.db.exists("DocType", "Education Assessment Result"):
		out["grades"] = frappe.get_all(
			"Education Assessment Result",
			filters={"student": student},
			fields=["name", "score", "max_score", "modified"],
			order_by="modified desc",
			limit=10,
		)
	return out


@frappe.whitelist()
def get_student_portal_dashboard() -> dict:
	student = frappe.db.get_value("Education Student", {"user": frappe.session.user}, "name")
	if not student:
		return {"student": None}
	st = frappe.get_doc("Education Student", student)
	return {
		"student": student,
		"student_name": st.student_name,
		"grade_level": st.grade_level,
		"section": st.section,
		"account_access_status": st.account_access_status,
		"financial_hold": st.financial_hold,
		"laravel_enabled": laravel_client.is_laravel_enabled(),
	}


@frappe.whitelist()
def get_teacher_dashboard(company: str | None = None, branch: str | None = None) -> dict:
	company, branch = _scope(company, branch)
	filters = {}
	if company:
		filters["company"] = company
	if branch:
		filters["branch"] = branch
	teachers = frappe.db.count("Education Teacher", filters) if frappe.db.exists("DocType", "Education Teacher") else 0
	sections = frappe.db.count("Education Section", filters) if frappe.db.exists("DocType", "Education Section") else 0
	return {
		"teachers": teachers,
		"sections": sections,
		"today": today(),
		"laravel_enabled": laravel_client.is_laravel_enabled(),
	}


@frappe.whitelist()
def get_admissions_dashboard(company: str | None = None, branch: str | None = None) -> dict:
	company, branch = _scope(company, branch)
	filters = {}
	if company:
		filters["company"] = company
	if branch:
		filters["branch"] = branch
	applications = 0
	waitlist = 0
	if frappe.db.exists("DocType", "Education Admission Application"):
		applications = frappe.db.count("Education Admission Application", filters)
	if frappe.db.exists("DocType", "Education Waitlist Pool"):
		waitlist = frappe.db.count("Education Waitlist Pool", filters)
	return {"applications": applications, "waitlist": waitlist, "company": company, "branch": branch}


@frappe.whitelist()
def get_registrar_dashboard(company: str | None = None, branch: str | None = None) -> dict:
	company, branch = _scope(company, branch)
	filters = {"status": "Active"}
	if company:
		filters["company"] = company
	if branch:
		filters["branch"] = branch
	return {
		"active_students": frappe.db.count("Education Student", filters),
		"enrollments": frappe.db.count("Education Student Enrollment", filters)
		if frappe.db.exists("DocType", "Education Student Enrollment")
		else 0,
	}


@frappe.whitelist()
def get_portal_catalog() -> dict:
	from omnexa_education.api.education_portal_catalog import get_portal_catalog as _catalog

	return {"portals": _catalog()}
