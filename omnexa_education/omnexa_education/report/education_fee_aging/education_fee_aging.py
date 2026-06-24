# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import cint, flt, getdate, today
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company filter is required."), title=_("Filters"))

	report_date = getdate(filters.get("report_date") or today())
	bucket_1 = cint(filters.get("bucket_1") or 30)
	bucket_2 = cint(filters.get("bucket_2") or 60)
	bucket_3 = cint(filters.get("bucket_3") or 90)

	conditions = [
		"si.docstatus = 1",
		"si.company = %(company)s",
		"si.outstanding_amount > 0",
	]
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
			si.name AS sales_invoice,
			si.posting_date,
			si.due_date,
			si.branch,
			es.name AS student,
			es.student_name,
			es.grade_level,
			si.grand_total,
			si.outstanding_amount
		FROM `tabSales Invoice` si
		INNER JOIN `tabEducation Student` es ON es.customer = si.customer AND es.company = si.company
		WHERE {' AND '.join(conditions)}
		ORDER BY si.due_date asc, si.name asc
		""",
		filters,
		as_dict=True,
	)

	data = []
	for row in rows:
		due_date = getdate(row.due_date) if row.due_date else report_date
		days_overdue = max(0, (report_date - due_date).days)
		age_0 = flt(row.outstanding_amount) if days_overdue <= bucket_1 else 0
		age_1 = flt(row.outstanding_amount) if bucket_1 < days_overdue <= bucket_2 else 0
		age_2 = flt(row.outstanding_amount) if bucket_2 < days_overdue <= bucket_3 else 0
		age_3 = flt(row.outstanding_amount) if days_overdue > bucket_3 else 0
		data.append(
			{
				"sales_invoice": row.sales_invoice,
				"student": row.student,
				"student_name": row.student_name,
				"grade_level": row.grade_level,
				"branch": row.branch,
				"posting_date": row.posting_date,
				"due_date": row.due_date,
				"days_overdue": days_overdue,
				"grand_total": flt(row.grand_total),
				"outstanding_amount": flt(row.outstanding_amount),
				"age_0": age_0,
				"age_1": age_1,
				"age_2": age_2,
				"age_3": age_3,
			}
		)

	return _columns(bucket_1, bucket_2, bucket_3), data


def _columns(bucket_1=30, bucket_2=60, bucket_3=90):
	return [
		{"label": _("Sales Invoice"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 140},
		{"label": _("Student"), "fieldname": "student", "fieldtype": "Link", "options": "Education Student", "width": 150},
		{"label": _("Student Name"), "fieldname": "student_name", "fieldtype": "Data", "width": 160},
		{"label": _("Grade Level"), "fieldname": "grade_level", "fieldtype": "Link", "options": "Education Grade Level", "width": 140},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
		{"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Date", "width": 100},
		{"label": _("Days Overdue"), "fieldname": "days_overdue", "fieldtype": "Int", "width": 110},
		{"label": _("Invoice Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 120},
		{"label": _("Outstanding"), "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 120},
		{"label": _("0-{0} Days").format(bucket_1), "fieldname": "age_0", "fieldtype": "Currency", "width": 120},
		{"label": _("{0}-{1} Days").format(bucket_1 + 1, bucket_2), "fieldname": "age_1", "fieldtype": "Currency", "width": 120},
		{"label": _("{0}-{1} Days").format(bucket_2 + 1, bucket_3), "fieldname": "age_2", "fieldtype": "Currency", "width": 120},
		{"label": _("Above {0} Days").format(bucket_3), "fieldname": "age_3", "fieldtype": "Currency", "width": 130},
	]

