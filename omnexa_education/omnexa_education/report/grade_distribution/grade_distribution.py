# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _
from frappe.utils import flt

from omnexa_core.omnexa_core.branch_access import get_allowed_branches
from omnexa_core.omnexa_core.utils.report_charts import grouped_sum_chart


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["ar.company = %(company)s", "ar.docstatus = 1"]
	if filters.get("branch"):
		conditions.append("ar.branch = %(branch)s")
	if filters.get("academic_year"):
		conditions.append("ar.academic_year = %(academic_year)s")
	if filters.get("term"):
		conditions.append("ar.term = %(term)s")
	if filters.get("subject"):
		conditions.append("ar.subject = %(subject)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("ar.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			COALESCE(ar.grade_letter, 'Ungraded') AS grade_letter,
			COUNT(*) AS result_count,
			AVG(ar.gpa_points) AS avg_gpa_points
		FROM `tabEducation Assessment Result` ar
		WHERE {' AND '.join(conditions)}
		GROUP BY COALESCE(ar.grade_letter, 'Ungraded')
		ORDER BY grade_letter
		""",
		filters,
		as_dict=True,
	)
	for row in data:
		row["avg_gpa_points"] = flt(row.avg_gpa_points, 2)
	chart = grouped_sum_chart(data, group_field="grade_letter", value_field="result_count", title="Results by Grade")
	return _columns(), data, None, chart


def _columns():
	return [
		{"label": _("Grade"), "fieldname": "grade_letter", "fieldtype": "Data", "width": 100},
		{"label": _("Results"), "fieldname": "result_count", "fieldtype": "Int", "width": 100},
		{"label": _("Avg GPA Points"), "fieldname": "avg_gpa_points", "fieldtype": "Float", "width": 120},
	]
