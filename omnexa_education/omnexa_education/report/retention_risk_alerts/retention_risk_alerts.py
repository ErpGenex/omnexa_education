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

	conditions = ["pa.company = %(company)s"]
	if filters.get("branch"):
		conditions.append("pa.branch = %(branch)s")
	if filters.get("alert_type"):
		conditions.append("pa.alert_type = %(alert_type)s")
	if filters.get("status"):
		conditions.append("pa.status = %(status)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("pa.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			pa.branch,
			pa.alert_type,
			pa.status,
			COUNT(*) AS alert_count,
			AVG(pa.score) AS avg_score
		FROM `tabEducation Predictive Alert` pa
		WHERE {' AND '.join(conditions)}
		GROUP BY pa.branch, pa.alert_type, pa.status
		ORDER BY alert_count DESC, pa.branch
		""",
		filters,
		as_dict=True,
	)
	for row in data:
		row["avg_score"] = flt(row.avg_score, 2)
	chart = grouped_sum_chart(data, group_field="alert_type", value_field="alert_count", title="Alerts by Type")
	return _columns(), data, None, chart


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Alert Type"), "fieldname": "alert_type", "fieldtype": "Data", "width": 150},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
		{"label": _("Alerts"), "fieldname": "alert_count", "fieldtype": "Int", "width": 90},
		{"label": _("Avg Score"), "fieldname": "avg_score", "fieldtype": "Float", "width": 100},
	]
