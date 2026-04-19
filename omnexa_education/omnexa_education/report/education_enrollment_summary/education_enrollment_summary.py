# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["es.company = %(company)s"]
	if filters.get("branch"):
		conditions.append("es.branch = %(branch)s")
	if filters.get("status"):
		conditions.append("es.status = %(status)s")
	if filters.get("grade_level"):
		conditions.append("es.grade_level = %(grade_level)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("es.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			es.branch,
			COALESCE(es.grade_level, '') AS grade_level,
			es.status,
			COUNT(*) AS student_count
		FROM `tabEducation Student` es
		WHERE {' AND '.join(conditions)}
		GROUP BY es.branch, COALESCE(es.grade_level, ''), es.status
		ORDER BY es.branch, grade_level, es.status
		""",
		filters,
		as_dict=True,
	)

	return _columns(), data


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 140},
		{"label": _("Grade Level"), "fieldname": "grade_level", "fieldtype": "Link", "options": "Education Grade Level", "width": 160},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
		{"label": _("Students"), "fieldname": "student_count", "fieldtype": "Int", "width": 100},
	]
