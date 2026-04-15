# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class EducationAcademicYear(Document):
	def validate(self):
		self._validate_company_matches_institution_curriculum()
		self._validate_dates()
		self._validate_year_code_unique_per_institution()

	def _validate_company_matches_institution_curriculum(self):
		inst_company = frappe.db.get_value("Education Institution", self.institution, "company")
		if inst_company and inst_company != self.company:
			frappe.throw(_("Institution must belong to the same company."), title=_("Company"))
		cur_company = frappe.db.get_value("Education Curriculum", self.curriculum, "company")
		if cur_company and cur_company != self.company:
			frappe.throw(_("Curriculum must belong to the same company."), title=_("Company"))

	def _validate_dates(self):
		if self.start_date and self.end_date and getdate(self.start_date) > getdate(self.end_date):
			frappe.throw(_("Start Date cannot be after End Date."), title=_("Dates"))

	def _validate_year_code_unique_per_institution(self):
		if not self.institution or not self.year_code:
			return
		filters = {"institution": self.institution, "year_code": self.year_code}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Education Academic Year", filters):
			frappe.throw(
				_("Year Code {0} already exists for this institution.").format(self.year_code),
				title=_("Duplicate"),
			)

