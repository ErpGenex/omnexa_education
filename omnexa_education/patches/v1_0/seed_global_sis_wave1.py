# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe


def execute():
	"""Ensure Education Settings singleton exists after Wave 1 migrate."""
	if not frappe.db.exists("DocType", "Education Settings"):
		return
	if frappe.db.exists("Education Settings", "Education Settings"):
		return
	doc = frappe.get_doc(
		{
			"doctype": "Education Settings",
			"enable_university_modules": 1,
			"enable_k12_modules": 1,
			"auto_create_customer": 1,
			"attendance_lock_days": 7,
		}
	)
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
