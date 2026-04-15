# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EducationSubject(Document):
	def validate(self):
		self._validate_company_matches_curriculum()
		self._validate_code_unique_per_company()

	def _validate_company_matches_curriculum(self):
		cur_company = frappe.db.get_value("Education Curriculum", self.curriculum, "company")
		if cur_company and cur_company != self.company:
			frappe.throw(_("Curriculum must belong to the same company."), title=_("Company"))

	def _validate_code_unique_per_company(self):
		if not self.company or not self.subject_code:
			return
		filters = {"company": self.company, "subject_code": self.subject_code}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Education Subject", filters):
			frappe.throw(
				_("Subject Code {0} already exists for this company.").format(self.subject_code),
				title=_("Duplicate"),
			)

