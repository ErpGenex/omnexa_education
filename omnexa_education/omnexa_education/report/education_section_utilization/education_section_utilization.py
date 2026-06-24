# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import flt
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["sec.company = %(company)s", "sec.status = 'Active'"]
	if filters.get("branch"):
		conditions.append("sec.branch = %(branch)s")
	if filters.get("academic_year"):
		conditions.append("sec.academic_year = %(academic_year)s")
	if filters.get("grade_level"):
		conditions.append("sec.grade_level = %(grade_level)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("sec.branch in %(allowed_branches)s")

	rows = frappe.db.sql(
		f"""
		SELECT
			sec.name AS section,
			sec.section_name,
			sec.branch,
			sec.campus,
			sec.academic_year,
			sec.grade_level,
			sec.capacity,
			COALESCE(SUM(CASE WHEN st.status = 'Active' THEN 1 ELSE 0 END), 0) AS enrolled_active
		FROM `tabEducation Section` sec
		LEFT JOIN `tabEducation Student` st
			ON st.section = sec.name AND st.company = sec.company
		WHERE {' AND '.join(conditions)}
		GROUP BY sec.name, sec.section_name, sec.branch, sec.campus, sec.academic_year, sec.grade_level, sec.capacity
		ORDER BY sec.branch, sec.grade_level, sec.name
		""",
		filters,
		as_dict=True,
	)

	data = []
	for row in rows:
		cap = int(row.capacity or 0)
		enr = int(row.enrolled_active or 0)
		vacant = max(cap - enr, 0) if cap else 0
		util = (enr / cap * 100.0) if cap > 0 else None
		data.append(
			{
				"section": row.section,
				"section_name": row.section_name,
				"branch": row.branch,
				"campus": row.campus,
				"academic_year": row.academic_year,
				"grade_level": row.grade_level,
				"capacity": cap,
				"enrolled_active": enr,
				"vacant_seats": vacant,
				"utilization_pct": flt(util, 2) if util is not None else None,
			}
		)
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Section"), "fieldname": "section", "fieldtype": "Link", "options": "Education Section", "width": 150},
		{"label": _("Section Name"), "fieldname": "section_name", "fieldtype": "Data", "width": 160},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Campus"), "fieldname": "campus", "fieldtype": "Link", "options": "Education Campus", "width": 130},
		{"label": _("Academic Year"), "fieldname": "academic_year", "fieldtype": "Link", "options": "Education Academic Year", "width": 140},
		{"label": _("Grade Level"), "fieldname": "grade_level", "fieldtype": "Link", "options": "Education Grade Level", "width": 140},
		{"label": _("Capacity"), "fieldname": "capacity", "fieldtype": "Int", "width": 90},
		{"label": _("Enrolled (Active)"), "fieldname": "enrolled_active", "fieldtype": "Int", "width": 130},
		{"label": _("Vacant Seats"), "fieldname": "vacant_seats", "fieldtype": "Int", "width": 110},
		{"label": _("Utilization %"), "fieldname": "utilization_pct", "fieldtype": "Percent", "width": 120},
	]
