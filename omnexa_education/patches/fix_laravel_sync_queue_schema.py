# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Fix Education Laravel Sync Queue insert failures (supporting_attachment column mismatch)."""

from __future__ import annotations

import frappe


def execute():
	dt = "Education Laravel Sync Queue"
	if not frappe.db.exists("DocType", dt):
		return

	for fieldname in ("supporting_attachment", "attachments_section"):
		cf_name = frappe.db.get_value("Custom Field", {"dt": dt, "fieldname": fieldname}, "name")
		if cf_name:
			frappe.delete_doc("Custom Field", cf_name, force=1, ignore_permissions=True)

	try:
		frappe.db.updatedb(dt)
	except Exception:
		frappe.log_error(frappe.get_traceback(), f"Omnexa Education: updatedb {dt}")

	frappe.clear_cache(doctype=dt)
