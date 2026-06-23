# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Role-based education workcenter dashboards."""

from __future__ import annotations

import frappe
from frappe.utils import flt, today

from omnexa_education.api import laravel_client
from omnexa_education.api.education_unified_inbox import get_unified_inbox
from omnexa_education.financial_hold import get_overdue_students


def _student_gpa(student: str) -> float | None:
	if not frappe.db.exists("DocType", "Education Assessment Result"):
		return None
	meta = frappe.get_meta("Education Assessment Result")
	if not meta.has_field("score"):
		return None
	rows = frappe.get_all(
		"Education Assessment Result",
		filters={"student": student},
		fields=["score", "max_score"],
		limit=100,
	)
	if not rows:
		return None
	total_score = 0.0
	total_max = 0.0
	for row in rows:
		score = flt(row.score)
		max_score = flt(row.max_score) or 100.0
		if max_score:
			total_score += score
			total_max += max_score
	if not total_max:
		return None
	return round((total_score / total_max) * 100, 1)


def _today_schedule(section: str | None) -> list:
	if not section or not frappe.db.exists("DocType", "Education Timetable Entry"):
		return []

	meta = frappe.get_meta("Education Timetable Entry")
	day_field = "weekday" if meta.has_field("weekday") else ("day_of_week" if meta.has_field("day_of_week") else None)
	if not day_field:
		return []

	day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
	day = day_names[frappe.utils.getdate(today()).weekday()]

	fields = ["name", "subject", "teacher", "room"]
	if meta.has_field("from_time"):
		fields.extend(["from_time", "to_time"])
		order_by = "from_time asc"
	elif meta.has_field("start_time"):
		fields.extend(["start_time", "end_time"])
		order_by = "start_time asc"
	else:
		order_by = "name asc"

	rows = frappe.get_all(
		"Education Timetable Entry",
		filters={"section": section, day_field: day},
		fields=fields,
		order_by=order_by,
		limit=20,
	)
	for row in rows:
		if row.get("from_time") is not None and row.get("start_time") is None:
			row["start_time"] = row.get("from_time")
			row["end_time"] = row.get("to_time")
	return rows


def _education_settings_doc():
	doc = frappe.get_doc("Education Settings", "Education Settings")
	doc.flags.ignore_permissions = True
	return doc


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

	settings = _education_settings_doc()
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
	settings = _education_settings_doc()
	queue_stats = {"queued": 0, "failed": 0, "success": 0}
	if frappe.db.exists("DocType", "Education Laravel Sync Queue"):
		for status in ("Queued", "Failed", "Success"):
			queue_stats[status.lower()] = frappe.db.count("Education Laravel Sync Queue", {"status": status})

	links = frappe.get_all(
		"Education Lms Course Link",
		filters={"is_active": 1, "lms_provider": "Laravel TLMS"},
		fields=["name", "course", "external_course_id", "institution"],
		limit=20,
		ignore_permissions=True,
	)
	institutions = frappe.get_all(
		"Education Institution",
		filters={"status": "Active"},
		fields=["name", "institution_name", "institution_type"],
		limit=10,
		ignore_permissions=True,
	)
	return {
		"enable_laravel_tlms": bool(settings.enable_laravel_tlms),
		"laravel_base_url": settings.laravel_base_url,
		"laravel_last_ping_at": settings.laravel_last_ping_at,
		"laravel_last_ping_status": settings.laravel_last_ping_status,
		"queue_stats": queue_stats,
		"lms_links": links,
		"institutions": institutions,
		"university_prompt": "/assets/omnexa_education/docs/LARAVEL_UNIVERSITY_SIS_DEVELOPMENT_PROMPT.md",
		"webhook_url": frappe.utils.get_url(
			"/api/method/omnexa_education.api.laravel_webhooks.receive"
		),
	}


def _sales_invoice_portal_fields() -> list[str]:
	if not frappe.db.exists("DocType", "Sales Invoice"):
		return []
	meta = frappe.get_meta("Sales Invoice")
	return [f for f in ("name", "posting_date", "grand_total", "outstanding_amount", "status") if meta.has_field(f)]


def _parent_child_invoices(customer: str | None) -> list[dict]:
	if not customer or not frappe.db.exists("DocType", "Sales Invoice"):
		return []
	fields = _sales_invoice_portal_fields()
	if not fields:
		return []
	try:
		return frappe.get_all(
			"Sales Invoice",
			filters={"customer": customer, "docstatus": 1},
			fields=fields,
			order_by="posting_date desc",
			limit=10,
		)
	except frappe.PermissionError:
		return []


@frappe.whitelist()
def get_parent_portal_dashboard(student: str | None = None) -> dict:
	user = frappe.session.user
	children = frappe.get_all(
		"Education Student",
		filters={"guardian_email": user, "status": "Active"},
		fields=["name", "student_name", "grade_level", "section", "financial_hold", "account_access_status"],
		order_by="student_name asc",
	)
	if not student and children:
		student = children[0].name
	out = {
		"student": student,
		"children": children,
		"grades": [],
		"attendance": [],
		"invoices": [],
		"inbox": {},
		"today_schedule": [],
		"gpa": None,
		"laravel_enabled": laravel_client.is_laravel_enabled(),
		"sso_available": False,
	}
	if not student:
		return out
	st = frappe.get_doc("Education Student", student)
	out["student_name"] = st.student_name
	out["account_access_status"] = st.account_access_status
	out["financial_hold"] = st.financial_hold
	out["guardian_laravel_user_id"] = st.guardian_laravel_user_id
	out["sso_available"] = bool(st.guardian_laravel_user_id and _education_settings_doc().laravel_sso_enabled)
	out["gpa"] = _student_gpa(student)
	out["today_schedule"] = _today_schedule(st.section)
	out["inbox"] = get_unified_inbox(student=student)
	if st.customer:
		out["invoices"] = _parent_child_invoices(st.customer)
	if frappe.db.exists("DocType", "Education Assessment Result"):
		meta = frappe.get_meta("Education Assessment Result")
		fields = [f for f in ("name", "score", "max_score", "modified") if meta.has_field(f)]
		if fields:
			out["grades"] = frappe.get_all(
				"Education Assessment Result",
				filters={"student": student},
				fields=fields,
				order_by="modified desc",
				limit=10,
			)
			for row in out["grades"]:
				if not row.get("max_score") and meta.has_field("assessment_plan"):
					plan = frappe.db.get_value("Education Assessment Result", row.name, "assessment_plan")
					if plan:
						row.max_score = frappe.db.get_value("Education Assessment Plan", plan, "max_score") or 100
	return out


@frappe.whitelist()
def get_student_portal_dashboard() -> dict:
	student = frappe.db.get_value("Education Student", {"user": frappe.session.user}, "name")
	if not student:
		return {"student": None, "laravel_enabled": laravel_client.is_laravel_enabled()}
	st = frappe.get_doc("Education Student", student)
	settings = _education_settings_doc()
	return {
		"student": student,
		"student_name": st.student_name,
		"grade_level": st.grade_level,
		"section": st.section,
		"account_access_status": st.account_access_status,
		"financial_hold": st.financial_hold,
		"laravel_enabled": laravel_client.is_laravel_enabled(),
		"laravel_user_id": st.laravel_user_id,
		"sso_available": bool(st.laravel_user_id and settings.laravel_sso_enabled),
		"gpa": _student_gpa(student),
		"today_schedule": _today_schedule(st.section),
		"inbox": get_unified_inbox(student=student),
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
	online = 0
	if frappe.db.exists("DocType", "Education Online Application"):
		online = frappe.db.count("Education Online Application", {**filters, "status": ["in", ["Submitted", "Reviewed"]]})
	return {"applications": applications, "waitlist": waitlist, "online_applications": online, "company": company, "branch": branch}


@frappe.whitelist()
def get_registrar_dashboard(company: str | None = None, branch: str | None = None) -> dict:
	company, branch = _scope(company, branch)
	student_filters: dict = {"status": "Active"}
	enrollment_filters: dict = {"enrollment_status": "Enrolled", "docstatus": 1}
	if company:
		student_filters["company"] = company
		enrollment_filters["company"] = company
	if branch:
		student_filters["branch"] = branch
		enrollment_filters["branch"] = branch
	return {
		"active_students": frappe.db.count("Education Student", student_filters),
		"enrollments": frappe.db.count("Education Student Enrollment", enrollment_filters)
		if frappe.db.exists("DocType", "Education Student Enrollment")
		else 0,
	}


@frappe.whitelist()
def get_portal_catalog() -> dict:
	from omnexa_education.api.education_portal_catalog import get_portal_catalog as _catalog

	return {"portals": _catalog()}
