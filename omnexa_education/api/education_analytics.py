# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Predictive analytics — at-risk students, retention KPIs."""

from __future__ import annotations

import frappe
from frappe import _


@frappe.whitelist()
def evaluate_at_risk_students(institution: str | None = None) -> dict:
	filters: dict = {"status": "Active"}
	if institution:
		filters["institution"] = institution
	students = frappe.get_all("Education Student", filters=filters, pluck="name")
	alerts = []
	for student in students:
		absent = frappe.db.count(
			"Education Attendance Record",
			{"student": student, "status": "Absent"},
		)
		if absent >= 5:
			alert = _upsert_alert(student, "Chronic Absence", min(absent / 20, 1.0), f"{absent} absences")
			alerts.append(alert)
		gpa_out = frappe.call(
			"omnexa_education.api.education_grading.compute_student_gpa",
			student=student,
		)
		if gpa_out.get("gpa", 4) < 2.0:
			alert = _upsert_alert(
				student,
				"Grade Drop",
				round(1 - gpa_out["gpa"] / 4, 2),
				f"GPA {gpa_out['gpa']}",
			)
			alerts.append(alert)
	return {"evaluated": len(students), "alerts": alerts}


def _upsert_alert(student: str, alert_type: str, score: float, details: str) -> dict:
	student_doc = frappe.get_doc("Education Student", student)
	existing = frappe.db.get_value(
		"Education Predictive Alert",
		{"student": student, "alert_type": alert_type, "status": "Open"},
		"name",
	)
	payload = {
		"student": student,
		"alert_type": alert_type,
		"score": score,
		"details": details,
		"status": "Open",
		"institution": student_doc.institution,
		"company": student_doc.company,
		"branch": student_doc.branch,
	}
	if existing:
		doc = frappe.get_doc("Education Predictive Alert", existing)
		doc.update(payload)
		doc.save(ignore_permissions=True)
	else:
		doc = frappe.get_doc({"doctype": "Education Predictive Alert", **payload}).insert(
			ignore_permissions=True
		)
	return {"name": doc.name, "alert_type": alert_type, "score": score}


@frappe.whitelist()
def get_executive_dashboard(institution: str | None = None) -> dict:
	filters = {"institution": institution} if institution else {}
	return {
		"students": frappe.db.count("Education Student", filters),
		"teachers": frappe.db.count("Education Teacher", filters),
		"open_applications": frappe.db.count(
			"Education Admission Application",
			{**filters, "status": ["in", ["Submitted", "Waitlisted"]]},
		),
		"open_alerts": frappe.db.count("Education Predictive Alert", {**filters, "status": "Open"}),
		"issued_transcripts": frappe.db.count(
			"Education Official Transcript",
			{**filters, "status": "Issued"},
		),
	}
