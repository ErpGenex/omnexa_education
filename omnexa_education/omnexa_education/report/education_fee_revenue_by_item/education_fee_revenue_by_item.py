# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.utils import flt
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	conditions = [
		"inv.docstatus = 1",
		"inv.company = %(company)s",
		"child.parenttype = 'Education Billing Invoice'",
	]
	if filters.get("from_date"):
		conditions.append("inv.posting_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("inv.posting_date <= %(to_date)s")
	if filters.get("branch"):
		conditions.append("inv.branch = %(branch)s")
	if filters.get("fee_item"):
		conditions.append("child.fee_item = %(fee_item)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("inv.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			child.fee_item,
			COUNT(*) AS line_count,
			SUM(child.qty) AS total_qty,
			SUM(child.amount) AS amount
		FROM `tabEducation Billing Invoice Item` child
		INNER JOIN `tabEducation Billing Invoice` inv ON inv.name = child.parent
		WHERE {' AND '.join(conditions)}
		GROUP BY child.fee_item
		ORDER BY amount DESC
		""",
		filters,
		as_dict=True,
	)

	for row in data:
		row["total_qty"] = flt(row.total_qty)
		row["amount"] = flt(row.amount)

	return _columns(), data


def _columns():
	return [
		{"label": _("Fee Item"), "fieldname": "fee_item", "fieldtype": "Link", "options": "Education Fee Item", "width": 200},
		{"label": _("Lines"), "fieldname": "line_count", "fieldtype": "Int", "width": 80},
		{"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
		{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 130},
	]
