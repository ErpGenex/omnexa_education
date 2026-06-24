# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns

from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["fl.company = %(company)s"]
	if filters.get("branch"):
		conditions.append("fl.branch = %(branch)s")
	if filters.get("from_date"):
		conditions.append("DATE(fl.access_datetime) >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("DATE(fl.access_datetime) <= %(to_date)s")
	if filters.get("student"):
		conditions.append("fl.student = %(student)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("fl.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			fl.name,
			fl.student,
			fl.accessed_by,
			fl.access_datetime,
			fl.resource_type,
			fl.resource_name,
			fl.purpose,
			fl.branch,
			fl.company,
			fl.institution
		FROM `tabEducation Ferpa Access Log` fl
		WHERE {' AND '.join(conditions)}
		ORDER BY fl.access_datetime DESC
		LIMIT 500
		""",
		filters,
		as_dict=True,
	)
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Student"), "fieldname": "student", "fieldtype": "Link", "options": "Education Student", "width": 160},
		{"label": _("Accessed By"), "fieldname": "accessed_by", "fieldtype": "Link", "options": "User", "width": 140},
		{"label": _("Access Time"), "fieldname": "access_datetime", "fieldtype": "Datetime", "width": 160},
		{"label": _("Resource"), "fieldname": "resource_type", "fieldtype": "Data", "width": 140},
		{"label": _("Resource Name"), "fieldname": "resource_name", "fieldtype": "Data", "width": 160},
		{"label": _("Purpose"), "fieldname": "purpose", "fieldtype": "Data", "width": 180},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 120},
		{"label": _("Institution"), "fieldname": "institution", "fieldtype": "Link", "options": "Education Institution", "width": 140},
	]
