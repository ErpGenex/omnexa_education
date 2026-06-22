# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Financial hold engine — overdue invoice detection and auto suspend."""

from __future__ import annotations

import frappe
from frappe.utils import add_days, flt, getdate, nowdate, today

from omnexa_education.api.student_account_lifecycle import apply_financial_hold, release_financial_hold


def _grace_days() -> int:
	s = frappe.get_single("Education Settings")
	if s.financial_hold_grace_days is not None:
		return int(s.financial_hold_grace_days or 0)
	return 7


def get_overdue_students(company: str | None = None, branch: str | None = None) -> list[dict]:
	grace = _grace_days()
	cutoff = add_days(today(), -grace)
	filters = {"status": "Active", "financial_hold": 0}
	if company:
		filters["company"] = company
	if branch:
		filters["branch"] = branch
	students = frappe.get_all(
		"Education Student",
		filters=filters,
		fields=["name", "student_name", "customer", "company", "branch"],
	)
	out: list[dict] = []
	for st in students:
		if not st.customer:
			continue
		overdue = frappe.db.sql(
			"""
			SELECT MIN(due_date) AS oldest_due, SUM(outstanding_amount) AS outstanding
			FROM `tabSales Invoice`
			WHERE customer = %s AND docstatus = 1 AND outstanding_amount > 0 AND due_date < %s
			""",
			(st.customer, cutoff),
			as_dict=True,
		)
		if not overdue or not flt(overdue[0].outstanding):
			continue
		out.append(
			{
				"student": st.name,
				"student_name": st.student_name,
				"outstanding": flt(overdue[0].outstanding),
				"oldest_due": overdue[0].oldest_due,
				"reason": frappe._("Overdue fees — oldest due {0}").format(overdue[0].oldest_due),
			}
		)
	return out


def customer_has_overdue(customer: str) -> bool:
	if not customer:
		return False
	grace = _grace_days()
	cutoff = add_days(today(), -grace)
	row = frappe.db.sql(
		"""
		SELECT SUM(outstanding_amount) AS outstanding
		FROM `tabSales Invoice`
		WHERE customer = %s AND docstatus = 1 AND outstanding_amount > 0 AND due_date < %s
		""",
		(customer, cutoff),
		as_dict=True,
	)
	return bool(row and flt(row[0].outstanding))


def sync_student_financial_hold(student_name: str, trigger: str = "Financial"):
	s = frappe.get_single("Education Settings")
	if not s.auto_suspend_on_overdue:
		return
	student = frappe.get_doc("Education Student", student_name)
	if not student.customer or student.status != "Active":
		return
	if customer_has_overdue(student.customer):
		if not student.financial_hold:
			apply_financial_hold(student_name, frappe._("Overdue student fees"), trigger=trigger)
	else:
		if student.financial_hold:
			release_financial_hold(student_name, trigger=trigger)


def run_daily_financial_hold_scan():
	s = frappe.get_single("Education Settings")
	if not s.auto_suspend_on_overdue:
		return
	for row in get_overdue_students():
		apply_financial_hold(row["student"], row["reason"], trigger="Scheduler")


def on_payment_entry_submit(doc, method=None):
	if doc.party_type != "Customer" or not doc.party:
		return
	students = frappe.get_all("Education Student", filters={"customer": doc.party}, pluck="name")
	for name in students:
		sync_student_financial_hold(name, trigger="Financial")


def on_sales_invoice_update(doc, method=None):
	if doc.docstatus != 1 or not doc.customer:
		return
	students = frappe.get_all("Education Student", filters={"customer": doc.customer}, pluck="name")
	for name in students:
		sync_student_financial_hold(name, trigger="Financial")
