# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EducationSection(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_campus_matches_branch_company()
		self._validate_year_grade_company_match()
		self._validate_code_unique_per_branch_year()

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch {0} does not exist.").format(self.branch), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Branch"))

	def _validate_campus_matches_branch_company(self):
		row = frappe.db.get_value("Education Campus", self.campus, ["company", "branch"], as_dict=True)
		if not row:
			frappe.throw(_("Campus does not exist."), title=_("Campus"))
		if row.company != self.company or row.branch != self.branch:
			frappe.throw(_("Campus must belong to the same company and branch."), title=_("Campus"))

	def _validate_year_grade_company_match(self):
		year = frappe.db.get_value("Education Academic Year", self.academic_year, ["company", "institution"], as_dict=True)
		if year and year.company != self.company:
			frappe.throw(_("Academic year must belong to the same company."), title=_("Company"))
		grade = frappe.db.get_value("Education Grade Level", self.grade_level, ["company", "institution"], as_dict=True)
		if grade and grade.company != self.company:
			frappe.throw(_("Grade level must belong to the same company."), title=_("Company"))
		if year and grade and year.institution != grade.institution:
			frappe.throw(_("Grade level and academic year must belong to the same institution."), title=_("Institution"))

	def _validate_code_unique_per_branch_year(self):
		if not self.branch or not self.academic_year or not self.section_code:
			return
		filters = {"branch": self.branch, "academic_year": self.academic_year, "section_code": self.section_code}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Education Section", filters):
			frappe.throw(
				_("Section Code {0} already exists for this branch and academic year.").format(self.section_code),
				title=_("Duplicate"),
			)

