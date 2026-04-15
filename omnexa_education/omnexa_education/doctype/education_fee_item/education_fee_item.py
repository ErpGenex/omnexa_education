# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class EducationFeeItem(Document):
	def validate(self):
		self._validate_income_account()
		self._validate_code_unique_per_company()
		if flt(self.default_rate) < 0:
			frappe.throw(_("Default Rate cannot be negative."), title=_("Rate"))

	def _validate_income_account(self):
		row = frappe.db.get_value("GL Account", self.income_account, ["company", "is_group"], as_dict=True)
		if not row or row.company != self.company:
			frappe.throw(_("Income account must belong to the same company."), title=_("GL"))
		if row.is_group:
			frappe.throw(_("Income account must be a leaf account."), title=_("GL"))

	def _validate_code_unique_per_company(self):
		if not self.company or not self.fee_code:
			return
		filters = {"company": self.company, "fee_code": self.fee_code}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Education Fee Item", filters):
			frappe.throw(
				_("Fee Code {0} already exists for this company.").format(self.fee_code),
				title=_("Duplicate"),
			)

