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

	conditions = ["l.company = %(company)s"]
	if filters.get("branch"):
		conditions.append("l.branch = %(branch)s")
	if filters.get("lms_provider"):
		conditions.append("l.lms_provider = %(lms_provider)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("l.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			l.branch,
			l.lms_provider,
			SUM(CASE WHEN l.is_active = 1 THEN 1 ELSE 0 END) AS active_links,
			SUM(CASE WHEN IFNULL(l.external_course_id, '') = '' THEN 1 ELSE 0 END) AS missing_external_id
		FROM `tabEducation Lms Course Link` l
		WHERE {' AND '.join(conditions)}
		GROUP BY l.branch, l.lms_provider
		ORDER BY l.branch, l.lms_provider
		""",
		filters,
		as_dict=True,
	)
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("LMS Provider"), "fieldname": "lms_provider", "fieldtype": "Data", "width": 140},
		{"label": _("Active Links"), "fieldname": "active_links", "fieldtype": "Int", "width": 110},
		{"label": _("Missing External ID"), "fieldname": "missing_external_id", "fieldtype": "Int", "width": 150},
	]
