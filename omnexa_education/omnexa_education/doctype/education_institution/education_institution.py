# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EducationInstitution(Document):
	def validate(self):
		self._validate_code_unique_per_company()

	def _validate_code_unique_per_company(self):
		if not self.company or not self.institution_code:
			return
		filters = {"company": self.company, "institution_code": self.institution_code}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Education Institution", filters):
			frappe.throw(
				_("Institution Code {0} already exists for this company.").format(self.institution_code),
				title=_("Duplicate"),
			)

