# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class EducationTerm(Document):
	def validate(self):
		self._validate_company_matches_links()
		self._validate_dates_within_year()
		self._validate_term_code_unique_per_year()

	def _validate_company_matches_links(self):
		inst_company = frappe.db.get_value("Education Institution", self.institution, "company")
		if inst_company and inst_company != self.company:
			frappe.throw(_("Institution must belong to the same company."), title=_("Company"))
		year = frappe.db.get_value(
			"Education Academic Year", self.academic_year, ["company", "institution", "start_date", "end_date"], as_dict=True
		)
		if year:
			if year.company != self.company:
				frappe.throw(_("Academic year must belong to the same company."), title=_("Company"))
			if year.institution != self.institution:
				frappe.throw(_("Academic year must belong to the same institution."), title=_("Institution"))

	def _validate_dates_within_year(self):
		if self.start_date and self.end_date and getdate(self.start_date) > getdate(self.end_date):
			frappe.throw(_("Start Date cannot be after End Date."), title=_("Dates"))
		year = frappe.db.get_value(
			"Education Academic Year", self.academic_year, ["start_date", "end_date"], as_dict=True
		)
		if not year:
			return
		if self.start_date and year.start_date and getdate(self.start_date) < getdate(year.start_date):
			frappe.throw(_("Term cannot start before academic year."), title=_("Dates"))
		if self.end_date and year.end_date and getdate(self.end_date) > getdate(year.end_date):
			frappe.throw(_("Term cannot end after academic year."), title=_("Dates"))

	def _validate_term_code_unique_per_year(self):
		if not self.academic_year or not self.term_code:
			return
		filters = {"academic_year": self.academic_year, "term_code": self.term_code}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Education Term", filters):
			frappe.throw(
				_("Term Code {0} already exists for this academic year.").format(self.term_code),
				title=_("Duplicate"),
			)

