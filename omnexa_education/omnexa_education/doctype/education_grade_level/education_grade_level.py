# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EducationGradeLevel(Document):
	def validate(self):
		self._validate_company_matches_links()
		self._validate_code_unique_per_institution_curriculum()
		self._validate_sequence_positive()

	def _validate_company_matches_links(self):
		inst_company = frappe.db.get_value("Education Institution", self.institution, "company")
		if inst_company and inst_company != self.company:
			frappe.throw(_("Institution must belong to the same company."), title=_("Company"))
		cur_company = frappe.db.get_value("Education Curriculum", self.curriculum, "company")
		if cur_company and cur_company != self.company:
			frappe.throw(_("Curriculum must belong to the same company."), title=_("Company"))

	def _validate_code_unique_per_institution_curriculum(self):
		if not self.institution or not self.curriculum or not self.grade_code:
			return
		filters = {"institution": self.institution, "curriculum": self.curriculum, "grade_code": self.grade_code}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Education Grade Level", filters):
			frappe.throw(
				_("Grade Code {0} already exists for this institution and curriculum.").format(self.grade_code),
				title=_("Duplicate"),
			)

	def _validate_sequence_positive(self):
		if self.sequence is None:
			return
		if int(self.sequence) < 1:
			frappe.throw(_("Sequence must be at least 1."), title=_("Sequence"))

