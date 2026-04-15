# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EducationDepartment(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_campus_matches_branch_company()
		self._validate_code_unique_per_branch()

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

	def _validate_code_unique_per_branch(self):
		if not self.branch or not self.department_code:
			return
		filters = {"branch": self.branch, "department_code": self.department_code}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Education Department", filters):
			frappe.throw(
				_("Department Code {0} already exists for this branch.").format(self.department_code),
				title=_("Duplicate"),
			)

