# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class EducationBillingInvoice(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_student_company_branch()
		self._validate_lifecycle_controls()
		self._sync_currency_defaults()
		self._sync_fee_items()
		self._set_amounts()
		self._validate_due_date()

	def _validate_lifecycle_controls(self):
		if not self.items:
			frappe.throw(_("At least one billing item is required."), title=_("Billing"))

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch {0} does not exist.").format(self.branch), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Branch"))

	def _validate_student_company_branch(self):
		row = frappe.db.get_value(
			"Education Student",
			self.student,
			["company", "branch", "customer"],
			as_dict=True,
		)
		if not row:
			frappe.throw(_("Student does not exist."), title=_("Student"))
		if row.company != self.company or row.branch != self.branch:
			frappe.throw(_("Student must belong to the same company and branch."), title=_("Student"))
		if not row.customer:
			frappe.throw(_("Student customer is missing; save the student first."), title=_("Billing"))

	def _sync_currency_defaults(self):
		if not self.currency:
			self.currency = frappe.db.get_value("Company", self.company, "default_currency")
		if not self.conversion_rate:
			self.conversion_rate = 1

	def _sync_fee_items(self):
		for row in self.items or []:
			it = frappe.db.get_value(
				"Education Fee Item",
				row.fee_item,
				["fee_code", "fee_name", "company", "income_account", "default_tax_rule", "default_rate", "status"],
				as_dict=True,
			)
			if not it:
				continue
			if it.company != self.company:
				frappe.throw(_("Row {0}: Fee Item belongs to a different company.").format(row.idx), title=_("Fee Item"))
			if it.status != "Active":
				frappe.throw(_("Row {0}: Fee Item is inactive.").format(row.idx), title=_("Fee Item"))
			row.income_account = it.income_account
			if not row.description:
				row.description = it.fee_name
			if not flt(row.rate) and flt(it.default_rate):
				row.rate = it.default_rate
			if not row.tax_rule and it.default_tax_rule:
				row.tax_rule = it.default_tax_rule

	def _set_amounts(self):
		net = 0
		tax = 0
		for row in self.items or []:
			row.amount = flt(row.qty) * flt(row.rate)
			net += flt(row.amount)
			rule_name = row.tax_rule or self.default_tax_rule
			if rule_name:
				rule = frappe.get_doc("Tax Rule", rule_name)
				if getdate(self.posting_date) < getdate(rule.valid_from) or getdate(self.posting_date) > getdate(
					rule.valid_to
				):
					frappe.throw(
						_("Row {0}: Tax Rule is not valid on posting date.").format(row.idx),
						title=_("Tax"),
					)
				if rule.tax_type == "standard" and flt(rule.rate):
					tax += flt(row.amount) * flt(rule.rate) / 100.0
		self.net_total = net
		self.tax_total = tax
		self.grand_total = net + tax
		if flt(self.grand_total) <= 0:
			frappe.throw(_("Grand Total must be greater than zero."), title=_("Billing"))

	def _validate_due_date(self):
		if not self.due_date:
			return
		if getdate(self.due_date) < getdate(self.posting_date):
			frappe.throw(_("Due Date cannot be before Posting Date."), title=_("Due Date"))

	def on_submit(self):
		self._create_and_submit_sales_invoice()

	def on_cancel(self):
		if self.sales_invoice:
			si = frappe.get_doc("Sales Invoice", self.sales_invoice)
			if si.docstatus == 1:
				si.cancel()
		self.db_set("sales_invoice", None, update_modified=False)

	def _create_and_submit_sales_invoice(self):
		if self.sales_invoice:
			return
		student = frappe.get_doc("Education Student", self.student)
		si = frappe.new_doc("Sales Invoice")
		si.company = self.company
		si.branch = self.branch
		si.customer = student.customer
		si.posting_date = self.posting_date
		si.due_date = self.due_date
		si.currency = self.currency
		si.conversion_rate = flt(self.conversion_rate)
		si.default_tax_rule = self.default_tax_rule
		for row in self.items or []:
			fee = frappe.get_cached_doc("Education Fee Item", row.fee_item)
			si.append(
				"items",
				{
					"item": None,
					"item_code": fee.fee_code,
					"qty": flt(row.qty),
					"rate": flt(row.rate),
					"tax_rule": row.tax_rule,
					"income_account": row.income_account,
				},
			)
		si.insert()
		si.submit()
		self.db_set("sales_invoice", si.name, update_modified=False)

