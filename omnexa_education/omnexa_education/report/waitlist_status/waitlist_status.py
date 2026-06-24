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

	conditions = ["wp.company = %(company)s"]
	if filters.get("branch"):
		conditions.append("wp.branch = %(branch)s")
	if filters.get("academic_year"):
		conditions.append("wp.academic_year = %(academic_year)s")
	if filters.get("grade_level"):
		conditions.append("wp.grade_level = %(grade_level)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("wp.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			wp.branch,
			wp.grade_level,
			wp.program,
			SUM(wp.capacity) AS total_capacity,
			SUM(wp.waitlist_count) AS total_waitlist,
			ROUND(SUM(wp.waitlist_count) / NULLIF(SUM(wp.capacity), 0) * 100, 2) AS fill_pressure_percent
		FROM `tabEducation Waitlist Pool` wp
		WHERE {' AND '.join(conditions)}
		GROUP BY wp.branch, wp.grade_level, wp.program
		ORDER BY total_waitlist DESC, wp.branch
		""",
		filters,
		as_dict=True,
	)
	for row in data:
		row["total_capacity"] = int(row.total_capacity or 0)
		row["total_waitlist"] = int(row.total_waitlist or 0)
		row["fill_pressure_percent"] = flt(row.fill_pressure_percent)
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Grade Level"), "fieldname": "grade_level", "fieldtype": "Link", "options": "Education Grade Level", "width": 150},
		{"label": _("Program"), "fieldname": "program", "fieldtype": "Link", "options": "Education Program", "width": 150},
		{"label": _("Capacity"), "fieldname": "total_capacity", "fieldtype": "Int", "width": 100},
		{"label": _("Waitlist"), "fieldname": "total_waitlist", "fieldtype": "Int", "width": 100},
		{"label": _("Pressure %"), "fieldname": "fill_pressure_percent", "fieldtype": "Percent", "width": 110},
	]
