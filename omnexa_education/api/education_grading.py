# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""GPA / CGPA engine — grading scale + assessment results."""

from __future__ import annotations

import json

import frappe
from frappe import _


DEFAULT_GPA_MAP = [
	{"min": 93, "letter": "A", "gpa": 4.0},
	{"min": 90, "letter": "A-", "gpa": 3.7},
	{"min": 87, "letter": "B+", "gpa": 3.3},
	{"min": 83, "letter": "B", "gpa": 3.0},
	{"min": 80, "letter": "B-", "gpa": 2.7},
	{"min": 77, "letter": "C+", "gpa": 2.3},
	{"min": 73, "letter": "C", "gpa": 2.0},
	{"min": 70, "letter": "C-", "gpa": 1.7},
	{"min": 67, "letter": "D+", "gpa": 1.3},
	{"min": 60, "letter": "D", "gpa": 1.0},
	{"min": 0, "letter": "F", "gpa": 0.0},
]


def _load_scale(scale_name: str | None = None) -> list[dict]:
	if scale_name and frappe.db.exists("Education Grading Scale", scale_name):
		raw = frappe.db.get_value("Education Grading Scale", scale_name, "grade_mappings")
		if raw:
			try:
				data = json.loads(raw)
				if isinstance(data, list):
					return data
			except json.JSONDecodeError:
				pass
	return DEFAULT_GPA_MAP


def percentage_to_gpa(score: float, scale_name: str | None = None) -> dict:
	mappings = _load_scale(scale_name)
	for row in sorted(mappings, key=lambda r: r.get("min", 0), reverse=True):
		if score >= float(row.get("min", 0)):
			return {"letter": row.get("letter"), "gpa": float(row.get("gpa", 0))}
	return {"letter": "F", "gpa": 0.0}


def _result_select_fields() -> list[str]:
	meta = frappe.get_meta("Education Assessment Result")
	candidates = ["name", "score", "max_score", "course", "subject", "assessment_plan", "academic_year", "term"]
	return [f for f in candidates if meta.has_field(f)]


def _resolve_max_score(row: frappe._dict) -> float:
	if row.get("max_score"):
		return float(row.max_score)
	plan = row.get("assessment_plan")
	if plan and frappe.db.exists("Education Assessment Plan", plan):
		return float(frappe.db.get_value("Education Assessment Plan", plan, "max_score") or 100)
	return 100.0


def _fetch_assessment_results(filters: dict) -> list[frappe._dict]:
	fields = _result_select_fields()
	rows = frappe.get_all("Education Assessment Result", filters=filters, fields=fields)
	for row in rows:
		if "max_score" not in fields:
			row.max_score = _resolve_max_score(row)
		if not row.get("course") and row.get("assessment_plan"):
			row.course = frappe.db.get_value("Education Assessment Plan", row.assessment_plan, "course")
		if not row.get("subject") and row.get("assessment_plan"):
			row.subject = frappe.db.get_value("Education Assessment Plan", row.assessment_plan, "subject")
	return rows


@frappe.whitelist()
def compute_student_gpa(student: str, academic_year: str | None = None, term: str | None = None) -> dict:
	if not student:
		frappe.throw(_("Student is required"))
	filters: dict = {"student": student}
	if academic_year and frappe.get_meta("Education Assessment Result").has_field("academic_year"):
		filters["academic_year"] = academic_year
	if term and frappe.get_meta("Education Assessment Result").has_field("term"):
		filters["term"] = term
	results = _fetch_assessment_results(filters)
	if not results:
		return {"student": student, "gpa": 0.0, "credits": 0, "courses": 0, "breakdown": []}
	total_points = 0.0
	total_credits = 0.0
	rows = []
	for r in results:
		max_score = _resolve_max_score(r)
		pct = (float(r.score or 0) / max_score * 100) if max_score else 0
		conv = percentage_to_gpa(pct)
		credits = 1.0
		if r.get("course") and frappe.db.exists("Education Course", r.course):
			credits = float(frappe.db.get_value("Education Course", r.course, "credit_hours") or 1)
		total_points += conv["gpa"] * credits
		total_credits += credits
		rows.append(
			{
				"name": r.name,
				"score": r.score,
				"max_score": max_score,
				"course": r.get("course"),
				"subject": r.get("subject"),
				"percentage": round(pct, 2),
				**conv,
				"credits": credits,
			}
		)
	gpa = round(total_points / total_credits, 3) if total_credits else 0.0
	return {
		"student": student,
		"gpa": gpa,
		"credits": total_credits,
		"courses": len(rows),
		"breakdown": rows,
	}


@frappe.whitelist()
def compute_student_cgpa(student: str) -> dict:
	enrollments = frappe.get_all(
		"Education Course Enrollment",
		filters={"student": student, "docstatus": 1},
		fields=["academic_year"],
		pluck="academic_year",
	)
	years = sorted(set(enrollments))
	term_gpas = []
	for yr in years:
		out = compute_student_gpa(student, academic_year=yr)
		if out["credits"]:
			term_gpas.append(out)
	if not term_gpas:
		return {"student": student, "cgpa": 0.0, "total_credits": 0, "terms": []}
	total_points = sum(t["gpa"] * t["credits"] for t in term_gpas)
	total_credits = sum(t["credits"] for t in term_gpas)
	cgpa = round(total_points / total_credits, 3) if total_credits else 0.0
	return {"student": student, "cgpa": cgpa, "total_credits": total_credits, "terms": term_gpas}


@frappe.whitelist()
def upsert_academic_standing(student: str, academic_year: str) -> dict:
	gpa_out = compute_student_gpa(student, academic_year=academic_year)
	gpa = gpa_out["gpa"]
	if gpa >= 3.5:
		standing = "Dean's List"
	elif gpa >= 2.0:
		standing = "Good Standing"
	elif gpa >= 1.5:
		standing = "Probation"
	else:
		standing = "Suspension"
	existing = frappe.db.get_value(
		"Education Academic Standing",
		{"student": student, "academic_year": academic_year},
		"name",
	)
	payload = {
		"student": student,
		"academic_year": academic_year,
		"gpa": gpa,
		"standing": standing,
		"institution": frappe.db.get_value("Education Student", student, "institution"),
		"company": frappe.db.get_value("Education Student", student, "company"),
		"branch": frappe.db.get_value("Education Student", student, "branch"),
	}
	if existing:
		doc = frappe.get_doc("Education Academic Standing", existing)
		doc.update(payload)
		doc.save(ignore_permissions=True)
	else:
		doc = frappe.get_doc({"doctype": "Education Academic Standing", **payload}).insert(
			ignore_permissions=True
		)
	return {"name": doc.name, "gpa": gpa, "standing": standing}
