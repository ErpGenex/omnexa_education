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

	conditions = ["tr.company = %(company)s", "tr.docstatus < 2"]
	if filters.get("branch"):
		conditions.append("tr.branch = %(branch)s")
	if filters.get("from_date"):
		conditions.append("tr.request_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("tr.request_date <= %(to_date)s")
	if filters.get("status"):
		conditions.append("tr.status = %(status)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("tr.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			tr.branch,
			tr.status,
			tr.delivery_method,
			COUNT(*) AS request_count
		FROM `tabEducation Transcript Request` tr
		WHERE {' AND '.join(conditions)}
		GROUP BY tr.branch, tr.status, tr.delivery_method
		ORDER BY tr.branch, tr.status, tr.delivery_method
		""",
		filters,
		as_dict=True,
	)
	chart = grouped_sum_chart(data, group_field="status", value_field="request_count", title="Transcript Requests by Status")
	return _columns(), data, None, chart


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": _("Delivery"), "fieldname": "delivery_method", "fieldtype": "Data", "width": 130},
		{"label": _("Requests"), "fieldname": "request_count", "fieldtype": "Int", "width": 100},
	]
