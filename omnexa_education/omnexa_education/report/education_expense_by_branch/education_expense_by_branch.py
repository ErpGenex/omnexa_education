# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = ["pi.docstatus = 1", "pi.company = %(company)s"]
	if filters.get("from_date"):
		conditions.append("pi.posting_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("pi.posting_date <= %(to_date)s")
	if filters.get("branch"):
		conditions.append("pi.branch = %(branch)s")
	if filters.get("supplier"):
		conditions.append("pi.supplier = %(supplier)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("pi.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			pi.branch,
			pi.supplier,
			COUNT(*) AS invoice_count,
			SUM(pi.grand_total) AS total_expense,
			SUM(pi.outstanding_amount) AS unpaid_amount
		FROM `tabPurchase Invoice` pi
		WHERE {' AND '.join(conditions)}
		GROUP BY pi.branch, pi.supplier
		ORDER BY total_expense DESC
		""",
		filters,
		as_dict=True,
	)

	return _columns(), data


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 140},
		{"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 200},
		{"label": _("Invoice Count"), "fieldname": "invoice_count", "fieldtype": "Int", "width": 110},
		{"label": _("Total Expense"), "fieldname": "total_expense", "fieldtype": "Currency", "width": 130},
		{"label": _("Unpaid Amount"), "fieldname": "unpaid_amount", "fieldtype": "Currency", "width": 130},
	]

