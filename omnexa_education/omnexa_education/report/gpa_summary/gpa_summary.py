# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import flt

from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["st.company = %(company)s"]
	if filters.get("branch"):
		conditions.append("st.branch = %(branch)s")
	if filters.get("academic_year"):
		conditions.append("st.academic_year = %(academic_year)s")
	if filters.get("term"):
		conditions.append("st.term = %(term)s")
	if filters.get("standing"):
		conditions.append("st.standing = %(standing)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("st.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			st.branch,
			st.standing,
			COUNT(*) AS student_count,
			AVG(st.gpa) AS avg_gpa
		FROM `tabEducation Academic Standing` st
		WHERE {' AND '.join(conditions)}
		GROUP BY st.branch, st.standing
		ORDER BY st.branch, st.standing
		""",
		filters,
		as_dict=True,
	)
	for row in data:
		row["avg_gpa"] = flt(row.avg_gpa, 2)
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Standing"), "fieldname": "standing", "fieldtype": "Data", "width": 140},
		{"label": _("Students"), "fieldname": "student_count", "fieldtype": "Int", "width": 100},
		{"label": _("Avg GPA"), "fieldname": "avg_gpa", "fieldtype": "Float", "width": 100},
	]
