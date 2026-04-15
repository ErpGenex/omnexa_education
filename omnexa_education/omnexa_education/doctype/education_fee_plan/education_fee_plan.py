# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class EducationFeePlan(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_year_company_branch()
		self._validate_plan_code_unique()
		self._sync_items()
		self._validate_installments()

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch {0} does not exist.").format(self.branch), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Branch"))

	def _validate_year_company_branch(self):
		year = frappe.db.get_value(
			"Education Academic Year",
			self.academic_year,
			["company", "start_date", "end_date"],
			as_dict=True,
		)
		if year and year.company != self.company:
			frappe.throw(_("Academic year must belong to the same company."), title=_("Company"))

	def _validate_plan_code_unique(self):
		filters = {"company": self.company, "branch": self.branch, "plan_code": self.plan_code}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Education Fee Plan", filters):
			frappe.throw(_("Plan Code must be unique per company/branch."), title=_("Duplicate"))

	def _sync_items(self):
		for row in self.items or []:
			it = frappe.db.get_value(
				"Education Fee Item",
				row.fee_item,
				["company", "fee_name", "default_rate", "status"],
				as_dict=True,
			)
			if not it:
				continue
			if it.company != self.company:
				frappe.throw(_("Row {0}: Fee Item company mismatch.").format(row.idx), title=_("Fee Item"))
			if it.status != "Active":
				frappe.throw(_("Row {0}: Fee Item is inactive.").format(row.idx), title=_("Fee Item"))
			if not row.description:
				row.description = it.fee_name
			if not flt(row.rate):
				row.rate = flt(it.default_rate)
			row.amount = flt(row.qty) * flt(row.rate)

	def _validate_installments(self):
		if not self.installments_count or int(self.installments_count) < 1:
			frappe.throw(_("Installments Count must be at least 1."), title=_("Installments"))

