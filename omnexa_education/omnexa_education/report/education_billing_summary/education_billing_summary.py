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

	conditions = ["inv.docstatus = 1", "inv.company = %(company)s"]
	if filters.get("from_date"):
		conditions.append("inv.posting_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("inv.posting_date <= %(to_date)s")
	if filters.get("branch"):
		conditions.append("inv.branch = %(branch)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("inv.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			inv.branch,
			DATE_FORMAT(inv.posting_date, '%%Y-%%m') AS period,
			COUNT(*) AS invoice_count,
			SUM(inv.net_total) AS net_total,
			SUM(inv.tax_total) AS tax_total,
			SUM(inv.grand_total) AS grand_total
		FROM `tabEducation Billing Invoice` inv
		WHERE {' AND '.join(conditions)}
		GROUP BY inv.branch, DATE_FORMAT(inv.posting_date, '%%Y-%%m')
		ORDER BY period DESC, inv.branch
		""",
		filters,
		as_dict=True,
	)

	for row in data:
		row["net_total"] = flt(row.net_total)
		row["tax_total"] = flt(row.tax_total)
		row["grand_total"] = flt(row.grand_total)
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 140},
		{"label": _("Period (YYYY-MM)"), "fieldname": "period", "fieldtype": "Data", "width": 120},
		{"label": _("Invoices"), "fieldname": "invoice_count", "fieldtype": "Int", "width": 90},
		{"label": _("Net Total"), "fieldname": "net_total", "fieldtype": "Currency", "width": 120},
		{"label": _("Tax Total"), "fieldname": "tax_total", "fieldtype": "Currency", "width": 120},
		{"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 120},
	]
