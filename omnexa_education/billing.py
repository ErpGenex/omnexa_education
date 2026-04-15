# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

from __future__ import annotations

import frappe
from frappe.utils import flt, getdate


def _is_rule_valid_on(rule, posting_date) -> bool:
	pd = getdate(posting_date)
	if rule.get("valid_from") and pd < getdate(rule.get("valid_from")):
		return False
	if rule.get("valid_to") and pd > getdate(rule.get("valid_to")):
		return False
	return True


def calculate_discount_amount(base_amount: float, fee_item_doc: dict, discount_rule_doc: dict | None, posting_date) -> float:
	if not discount_rule_doc or not discount_rule_doc.get("is_active"):
		return 0.0
	if not _is_rule_valid_on(discount_rule_doc, posting_date):
		return 0.0
	scope = discount_rule_doc.get("scope")
	if scope == "Fee Item" and discount_rule_doc.get("fee_item") != fee_item_doc.get("name"):
		return 0.0
	if scope == "Fee Category" and discount_rule_doc.get("fee_category") != fee_item_doc.get("fee_category"):
		return 0.0

	val = flt(discount_rule_doc.get("discount_value"))
	if val <= 0:
		return 0.0
	if discount_rule_doc.get("discount_type") == "Percent":
		return min(flt(base_amount), flt(base_amount) * val / 100.0)
	return min(flt(base_amount), val)


def calculate_late_fee_amount(*, customer: str, posting_date, late_fee_rule_doc: dict | None) -> float:
	if not late_fee_rule_doc or not late_fee_rule_doc.get("is_active"):
		return 0.0
	grace = int(late_fee_rule_doc.get("grace_days") or 0)
	pd = getdate(posting_date)
	rows = frappe.db.sql(
		"""
		SELECT due_date, outstanding_amount
		FROM `tabSales Invoice`
		WHERE customer = %s
		  AND docstatus = 1
		  AND outstanding_amount > 0
		  AND due_date < %s
		""",
		(customer, pd),
		as_dict=True,
	)
	if not rows:
		return 0.0
	oldest_due = min(getdate(r.due_date) for r in rows if r.get("due_date"))
	overdue_days = (pd - oldest_due).days
	if overdue_days <= grace:
		return 0.0
	outstanding = sum(flt(r.outstanding_amount) for r in rows)
	if outstanding <= 0:
		return 0.0
	val = flt(late_fee_rule_doc.get("charge_value"))
	if val <= 0:
		return 0.0
	if late_fee_rule_doc.get("charge_type") == "Percent":
		amount = flt(outstanding * val / 100.0)
	else:
		amount = val
	max_charge = flt(late_fee_rule_doc.get("max_charge"))
	if max_charge > 0:
		amount = min(amount, max_charge)
	return max(0.0, amount)

