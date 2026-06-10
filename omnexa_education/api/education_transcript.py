# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Official transcript PDF generation."""

from __future__ import annotations

import frappe
from frappe import _


@frappe.whitelist()
def issue_official_transcript(student: str) -> dict:
	if not student:
		frappe.throw(_("Student is required"))
	from omnexa_education.api.education_grading import compute_student_cgpa

	cgpa_out = compute_student_cgpa(student)
	student_doc = frappe.get_doc("Education Student", student)
	doc = frappe.get_doc(
		{
			"doctype": "Education Official Transcript",
			"student": student,
			"institution": student_doc.institution,
			"company": student_doc.company,
			"branch": student_doc.branch,
			"cgpa": cgpa_out["cgpa"],
			"total_credits": cgpa_out["total_credits"],
			"issue_date": frappe.utils.today(),
			"status": "Issued",
		}
	).insert(ignore_permissions=True)
	doc.submit()
	return {
		"transcript": doc.name,
		"cgpa": doc.cgpa,
		"print_format": "Education Official Transcript",
		"pdf_url": f"/api/method/frappe.utils.print_format.download_pdf?doctype=Education%20Official%20Transcript&name={doc.name}&format=Education%20Official%20Transcript",
	}


@frappe.whitelist()
def get_transcript_data(student: str) -> dict:
	from omnexa_education.api.education_grading import compute_student_cgpa

	student_doc = frappe.get_doc("Education Student", student)
	cgpa = compute_student_cgpa(student)
	enrollments = frappe.get_all(
		"Education Course Enrollment",
		filters={"student": student, "docstatus": 1},
		fields=["course", "academic_year", "term", "grade", "status"],
	)
	return {
		"student": student,
		"student_name": student_doc.student_name,
		"institution": student_doc.institution,
		"cgpa": cgpa,
		"enrollments": enrollments,
	}
