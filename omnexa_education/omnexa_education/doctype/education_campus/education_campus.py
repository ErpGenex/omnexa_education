# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EducationCampus(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_institution_company_match()
		self._validate_code_unique_per_company()

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch {0} does not exist.").format(self.branch), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Branch"))

	def _validate_institution_company_match(self):
		inst_company = frappe.db.get_value("Education Institution", self.institution, "company")
		if inst_company and inst_company != self.company:
			frappe.throw(_("Institution must belong to the same company."), title=_("Company"))

	def _validate_code_unique_per_company(self):
		if not self.company or not self.campus_code:
			return
		filters = {"company": self.company, "campus_code": self.campus_code}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Education Campus", filters):
			frappe.throw(
				_("Campus Code {0} already exists for this company.").format(self.campus_code),
				title=_("Duplicate"),
			)

