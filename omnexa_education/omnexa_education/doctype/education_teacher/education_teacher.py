# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EducationTeacher(Document):
	def after_insert(self):
		from omnexa_education.api.teacher_account_lifecycle import auto_provision_teacher_if_needed

		auto_provision_teacher_if_needed(self.name)

	def validate(self):
		self._validate_branch_company_match()
		self._validate_campus_department_match()
		self._validate_employee_company_match()
		self._validate_teacher_code_unique_per_company()

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch {0} does not exist.").format(self.branch), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Branch"))

	def _validate_campus_department_match(self):
		if self.campus:
			campus = frappe.db.get_value("Education Campus", self.campus, ["company", "branch"], as_dict=True)
			if not campus:
				frappe.throw(_("Campus does not exist."), title=_("Campus"))
			if campus.company != self.company or campus.branch != self.branch:
				frappe.throw(_("Campus must belong to the same company and branch."), title=_("Campus"))
		if self.department:
			dept = frappe.db.get_value(
				"Education Department", self.department, ["company", "branch"], as_dict=True
			)
			if not dept:
				frappe.throw(_("Department does not exist."), title=_("Department"))
			if dept.company != self.company or dept.branch != self.branch:
				frappe.throw(_("Department must belong to the same company and branch."), title=_("Department"))

	def _validate_employee_company_match(self):
		if not self.employee:
			return
		employee_company = frappe.db.get_value("Employee", self.employee, "company")
		if employee_company and employee_company != self.company:
			frappe.throw(_("Employee must belong to the same company."), title=_("Employee"))

	def _validate_teacher_code_unique_per_company(self):
		filters = {"company": self.company, "teacher_code": self.teacher_code}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Education Teacher", filters):
			frappe.throw(
				_("Teacher Code {0} already exists for this company.").format(self.teacher_code),
				title=_("Duplicate"),
			)

