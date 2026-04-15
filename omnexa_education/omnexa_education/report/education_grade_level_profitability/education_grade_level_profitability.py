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

	conditions = ["si.docstatus = 1", "si.company = %(company)s"]
	if filters.get("from_date"):
		conditions.append("si.posting_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("si.posting_date <= %(to_date)s")
	if filters.get("branch"):
		conditions.append("si.branch = %(branch)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("si.branch in %(allowed_branches)s")

	rows = frappe.db.sql(
		f"""
		SELECT
			COALESCE(es.grade_level, 'Unassigned') AS grade_level,
			COUNT(DISTINCT es.name) AS student_count,
			COUNT(DISTINCT si.name) AS invoice_count,
			SUM(si.grand_total) AS billed_amount,
			SUM(si.grand_total - si.outstanding_amount) AS collected_amount,
			SUM(si.outstanding_amount) AS outstanding_amount
		FROM `tabSales Invoice` si
		INNER JOIN `tabEducation Student` es
			ON es.customer = si.customer AND es.company = si.company
		WHERE {' AND '.join(conditions)}
		GROUP BY COALESCE(es.grade_level, 'Unassigned')
		ORDER BY billed_amount DESC
		""",
		filters,
		as_dict=True,
	)

	data = []
	for row in rows:
		billed = flt(row.billed_amount)
		collected = flt(row.collected_amount)
		outstanding = flt(row.outstanding_amount)
		collection_rate = (collected / billed * 100.0) if billed else 0.0
		net_cash_position = collected - outstanding
		data.append(
			{
				"grade_level": row.grade_level,
				"student_count": row.student_count,
				"invoice_count": row.invoice_count,
				"billed_amount": billed,
				"collected_amount": collected,
				"outstanding_amount": outstanding,
				"collection_rate": collection_rate,
				"net_cash_position": net_cash_position,
			}
		)

	return _columns(), data


def _columns():
	return [
		{"label": _("Grade Level"), "fieldname": "grade_level", "fieldtype": "Data", "width": 170},
		{"label": _("Students"), "fieldname": "student_count", "fieldtype": "Int", "width": 90},
		{"label": _("Invoices"), "fieldname": "invoice_count", "fieldtype": "Int", "width": 90},
		{"label": _("Billed"), "fieldname": "billed_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("Collected"), "fieldname": "collected_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("Outstanding"), "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("Collection Rate %"), "fieldname": "collection_rate", "fieldtype": "Percent", "width": 130},
		{"label": _("Net Cash Position"), "fieldname": "net_cash_position", "fieldtype": "Currency", "width": 140},
	]

