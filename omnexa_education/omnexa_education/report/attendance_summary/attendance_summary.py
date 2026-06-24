# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _
from frappe.utils import flt

from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["s.company = %(company)s", "s.docstatus = 1"]
	if filters.get("branch"):
		conditions.append("s.branch = %(branch)s")
	if filters.get("from_date"):
		conditions.append("s.session_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("s.session_date <= %(to_date)s")
	if filters.get("section"):
		conditions.append("s.section = %(section)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("s.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			s.branch,
			s.section,
			COUNT(DISTINCT s.name) AS session_count,
			SUM(CASE WHEN ar.status = 'Present' THEN 1 ELSE 0 END) AS present_total,
			SUM(CASE WHEN ar.status = 'Absent' THEN 1 ELSE 0 END) AS absent_total,
			SUM(CASE WHEN ar.status = 'Late' THEN 1 ELSE 0 END) AS late_total
		FROM `tabEducation Attendance Session` s
		LEFT JOIN `tabEducation Attendance Record` ar ON ar.parent = s.name
		WHERE {' AND '.join(conditions)}
		GROUP BY s.branch, s.section
		ORDER BY s.branch, s.section
		""",
		filters,
		as_dict=True,
	)
	for row in data:
		total = flt(row.present_total) + flt(row.absent_total) + flt(row.late_total)
		row["attendance_rate"] = flt((flt(row.present_total) / total) * 100.0, 2) if total else 0
	return _columns(), data


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Section"), "fieldname": "section", "fieldtype": "Link", "options": "Education Section", "width": 150},
		{"label": _("Sessions"), "fieldname": "session_count", "fieldtype": "Int", "width": 100},
		{"label": _("Present"), "fieldname": "present_total", "fieldtype": "Int", "width": 90},
		{"label": _("Absent"), "fieldname": "absent_total", "fieldtype": "Int", "width": 90},
		{"label": _("Late"), "fieldname": "late_total", "fieldtype": "Int", "width": 80},
		{"label": _("Attendance %"), "fieldname": "attendance_rate", "fieldtype": "Percent", "width": 110},
	]
