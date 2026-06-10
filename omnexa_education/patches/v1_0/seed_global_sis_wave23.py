# Copyright (c) 2026, Omnexa

import json

import frappe


def execute():
	"""Seed default grading scale and Wave 2+3 baseline records."""
	inst = frappe.db.get_value("Education Institution", {}, "name")
	company = frappe.db.get_value("Education Institution", inst, "company") if inst else None
	branch = frappe.db.get_value("Education Institution", inst, "branch") if inst else None

	if inst and not frappe.db.exists("Education Grading Scale", "GPA 4.0 Standard"):
		frappe.get_doc(
			{
				"doctype": "Education Grading Scale",
				"scale_name": "GPA 4.0 Standard",
				"scale_type": "GPA 4.0",
				"institution": inst,
				"company": company,
				"grade_mappings": json.dumps(
					[
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
				),
			}
		).insert(ignore_permissions=True)

	if inst and not frappe.db.exists("Education Timetable Template", "Standard 8-Period"):
		frappe.get_doc(
				{
					"doctype": "Education Timetable Template",
					"template_name": "Standard 8-Period",
					"institution": inst,
					"company": company,
					"branch": branch,
				"periods_per_day": 8,
			}
		).insert(ignore_permissions=True)

	frappe.db.commit()
