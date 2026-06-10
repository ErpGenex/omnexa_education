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


@frappe.whitelist()
def compute_student_gpa(student: str, academic_year: str | None = None, term: str | None = None) -> dict:
	if not student:
		frappe.throw(_("Student is required"))
	filters: dict = {"student": student}
	if academic_year:
		filters["academic_year"] = academic_year
	if term:
		filters["term"] = term
	results = frappe.get_all(
		"Education Assessment Result",
		filters=filters,
		fields=["name", "score", "max_score", "course", "subject"],
	)
	if not results:
		return {"student": student, "gpa": 0.0, "credits": 0, "courses": 0}
	total_points = 0.0
	total_credits = 0.0
	rows = []
	for r in results:
		max_score = float(r.max_score or 100)
		pct = (float(r.score or 0) / max_score * 100) if max_score else 0
		conv = percentage_to_gpa(pct)
		credits = float(frappe.db.get_value("Education Course", r.course, "credit_hours") or 1)
		total_points += conv["gpa"] * credits
		total_credits += credits
		rows.append({**r, "percentage": round(pct, 2), **conv, "credits": credits})
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
