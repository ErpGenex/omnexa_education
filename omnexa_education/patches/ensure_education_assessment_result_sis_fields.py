# Copyright (c) 2026, ErpGenEx
"""Add SIS grading fields to Education Assessment Result (GPA / analytics parity)."""

from __future__ import annotations

import frappe


def execute():
	meta = frappe.get_meta("Education Assessment Result")
	fields = [
		("max_score", "Float", "Max Score", {"default": "100", "in_list_view": 1}),
		("course", "Link", "Course", {"options": "Education Course"}),
		("subject", "Link", "Subject", {"options": "Education Subject"}),
		("academic_year", "Link", "Academic Year", {"options": "Education Academic Year"}),
		("term", "Link", "Term", {"options": "Education Term"}),
	]
	for fieldname, fieldtype, label, extra in fields:
		if meta.has_field(fieldname):
			continue
		frappe.get_doc(
			{
				"doctype": "Custom Field",
				"dt": "Education Assessment Result",
				"fieldname": fieldname,
				"fieldtype": fieldtype,
				"label": label,
				"insert_after": "score" if fieldname == "max_score" else fieldname,
				**extra,
			}
		).insert(ignore_permissions=True)
	frappe.db.commit()
