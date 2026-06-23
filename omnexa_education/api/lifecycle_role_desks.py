# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Lifecycle role desks — graduation, alumni, QA."""

from __future__ import annotations

import frappe
from frappe.utils import flt, today

from omnexa_education.education_demo.institution_specs import ACADEMY_QA_METRICS
from omnexa_education.education_global_benchmark import GLOBAL_SIS_MATRIX, get_global_sis_score


def _scope(company: str | None, branch: str | None) -> tuple[str, str]:
	return (
		company or frappe.defaults.get_user_default("Company") or "",
		branch or frappe.defaults.get_user_default("Branch") or "",
	)


@frappe.whitelist()
def get_graduation_dashboard(company: str | None = None, branch: str | None = None) -> dict:
	company, branch = _scope(company, branch)
	student_filters: dict = {"company": company, "status": "Active"}
	if branch:
		student_filters["branch"] = branch
	candidates = frappe.db.count("Education Student", student_filters)
	graduated = frappe.db.count("Education Student", {**student_filters, "status": "Graduated"})
	transcript_pending = 0
	if frappe.db.exists("DocType", "Education Transcript Request"):
		transcript_pending = frappe.db.count(
			"Education Transcript Request",
			{"company": company, "status": ["in", ["Submitted", "In Progress"]]},
		)
	issued = 0
	if frappe.db.exists("DocType", "Education Official Transcript"):
		issued = frappe.db.count("Education Official Transcript", {"company": company, "status": "Issued"})
	queue = frappe.get_all(
		"Education Student",
		filters=student_filters,
		fields=["name", "student_name", "institution", "grade_level", "section"],
		limit=15,
		order_by="modified desc",
	)
	return {
		"active_students": candidates,
		"graduated": graduated,
		"transcript_pending": transcript_pending,
		"transcripts_issued": issued,
		"graduation_queue": queue,
	}


@frappe.whitelist()
def get_alumni_dashboard(company: str | None = None, branch: str | None = None) -> dict:
	company, branch = _scope(company, branch)
	filters: dict = {"company": company}
	if branch:
		filters["branch"] = branch
	alumni_count = 0
	if frappe.db.exists("DocType", "Education Alumni Record"):
		alumni_count = frappe.db.count("Education Alumni Record", filters)
	employed = 0
	if alumni_count and frappe.db.exists("DocType", "Education Alumni Record"):
		employed = frappe.db.count("Education Alumni Record", {**filters, "current_employer": ["!=", ""]})
	records = []
	if frappe.db.exists("DocType", "Education Alumni Record"):
		records = frappe.get_all(
			"Education Alumni Record",
			filters=filters,
			fields=["name", "student", "graduation_date", "program", "current_employer", "contact_email"],
			limit=20,
			order_by="graduation_date desc",
		)
	return {
		"alumni_count": alumni_count,
		"employed_count": employed,
		"employment_rate": round(employed / alumni_count * 100, 1) if alumni_count else 0,
		"records": records,
	}


@frappe.whitelist()
def get_qa_dashboard(company: str | None = None, branch: str | None = None) -> dict:
	company, branch = _scope(company, branch)
	benchmark = get_global_sis_score()
	students = frappe.db.count("Education Student", {"company": company, "status": "Active"}) if company else 0
	alerts = frappe.db.count("Education Predictive Alert", {"company": company, "status": "Open"}) if frappe.db.exists("DocType", "Education Predictive Alert") else 0
	enrolled = 0
	if frappe.db.exists("DocType", "Education Student Enrollment"):
		enrolled = frappe.db.count(
			"Education Student Enrollment",
			{"company": company, "enrollment_status": "Enrolled", "docstatus": 1},
		)
	completion_rate = round(min(100, (enrolled / students * 100) if students else 0), 1)
	metrics = []
	for m in ACADEMY_QA_METRICS:
		live = m["target"]
		if m["key"] == "completion_rate":
			live = completion_rate
		elif m["key"] == "employment_rate":
			alumni = get_alumni_dashboard(company, branch)
			live = alumni.get("employment_rate") or m["target"]
		metrics.append({**m, "live_value": live})
	return {
		"global_score": benchmark.get("weighted_score"),
		"matrix": GLOBAL_SIS_MATRIX,
		"open_alerts": alerts,
		"qa_metrics": metrics,
		"students": students,
	}


@frappe.whitelist()
def mark_student_graduated(student: str) -> dict:
	frappe.only_for(("System Manager", "Education Manager", "Education User"))
	doc = frappe.get_doc("Education Student", student)
	doc.status = "Graduated"
	doc.save(ignore_permissions=True)
	if frappe.db.exists("DocType", "Education Alumni Record"):
		existing = frappe.db.get_value("Education Alumni Record", {"student": student}, "name")
		if not existing:
			frappe.get_doc(
				{
					"doctype": "Education Alumni Record",
					"student": student,
					"institution": doc.institution,
					"company": doc.company,
					"branch": doc.branch,
					"graduation_date": today(),
					"contact_email": doc.guardian_email or "",
				}
			).insert(ignore_permissions=True)
	return {"student": student, "status": "Graduated"}
