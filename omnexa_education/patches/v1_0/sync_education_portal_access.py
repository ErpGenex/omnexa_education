# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Ensure portal page roles and Education Student read permissions exist."""

from __future__ import annotations

import frappe


def execute():
	from omnexa_education.api.education_role_demo import ensure_education_roles, sync_journey_page_roles

	ensure_education_roles()
	sync_journey_page_roles()
	_ensure_student_portal_permissions()
	frappe.db.commit()


def _ensure_student_portal_permissions():
	meta = frappe.get_meta("Education Student")
	existing = {(p.role, p.permlevel) for p in meta.permissions}
	for role in ("Education Student Portal", "Education Parent Portal"):
		if (role, 0) in existing:
			continue
		frappe.get_doc(
			{
				"doctype": "Custom DocPerm",
				"parent": "Education Student",
				"parenttype": "DocType",
				"parentfield": "permissions",
				"role": role,
				"read": 1,
			}
		).insert(ignore_permissions=True)
