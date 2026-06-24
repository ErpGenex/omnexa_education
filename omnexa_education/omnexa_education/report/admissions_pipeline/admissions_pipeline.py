# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _

from omnexa_core.omnexa_core.branch_access import get_allowed_branches
from omnexa_core.omnexa_core.utils.report_charts import grouped_sum_chart


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["aa.company = %(company)s", "aa.docstatus < 2"]
	if filters.get("branch"):
		conditions.append("aa.branch = %(branch)s")
	if filters.get("academic_year"):
		conditions.append("aa.academic_year = %(academic_year)s")
	if filters.get("grade_level"):
		conditions.append("aa.grade_level = %(grade_level)s")
	if filters.get("from_date"):
		conditions.append("aa.application_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("aa.application_date <= %(to_date)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("aa.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			aa.branch,
			COALESCE(aa.grade_level, '') AS grade_level,
			aa.status,
			COUNT(*) AS application_count
		FROM `tabEducation Admission Application` aa
		WHERE {' AND '.join(conditions)}
		GROUP BY aa.branch, COALESCE(aa.grade_level, ''), aa.status
		ORDER BY aa.branch, grade_level, aa.status
		""",
		filters,
		as_dict=True,
	)
	chart = grouped_sum_chart(data, group_field="status", value_field="application_count", title="Applications by Status")
	return _columns(), data, None, chart


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 140},
		{"label": _("Grade Level"), "fieldname": "grade_level", "fieldtype": "Link", "options": "Education Grade Level", "width": 160},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": _("Applications"), "fieldname": "application_count", "fieldtype": "Int", "width": 110},
	]
