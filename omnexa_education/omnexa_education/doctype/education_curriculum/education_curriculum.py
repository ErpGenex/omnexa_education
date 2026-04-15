# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EducationCurriculum(Document):
	def validate(self):
		self._validate_code_unique_per_company()

	def _validate_code_unique_per_company(self):
		if not self.company or not self.curriculum_code:
			return
		filters = {"company": self.company, "curriculum_code": self.curriculum_code}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Education Curriculum", filters):
			frappe.throw(
				_("Curriculum Code {0} already exists for this company.").format(self.curriculum_code),
				title=_("Duplicate"),
			)

