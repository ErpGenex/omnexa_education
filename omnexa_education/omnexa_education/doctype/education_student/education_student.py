# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from omnexa_education.api.student_account_lifecycle import (
	auto_provision_if_needed,
	deprovision_student,
)
from omnexa_education.api.parent_account_lifecycle import auto_provision_parent_for_student


class EducationStudent(Document):
	def validate(self):
		self._validate_branch_company_match()
		self._validate_campus_matches_branch_company()
		self._validate_section_matches_branch_company()
		self._validate_code_unique_per_company()

	def after_insert(self):
		self._ensure_customer()
		auto_provision_if_needed(self.name)
		auto_provision_parent_for_student(self.name)

	def on_update(self):
		if self.customer and self.student_name:
			frappe.db.set_value(
				"Customer",
				self.customer,
				"customer_name",
				self._customer_display_name(),
				update_modified=False,
			)
		if self.status in ("Withdrawn", "Graduated") and self.account_access_status not in (
			"Withdrawn",
			None,
			"",
		):
			deprovision_student(self.name, trigger="Withdrawal")
		elif self.status == "Active" and self.account_access_status in (None, "", "Not Provisioned"):
			auto_provision_if_needed(self.name)
		if self.guardian_email:
			auto_provision_parent_for_student(self.name)

	def _customer_display_name(self) -> str:
		return f"{self.student_name} ({self.student_code})" if self.student_code else self.student_name

	def _validate_branch_company_match(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch {0} does not exist.").format(self.branch), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Branch"))

	def _validate_campus_matches_branch_company(self):
		if not self.campus:
			return
		row = frappe.db.get_value("Education Campus", self.campus, ["company", "branch"], as_dict=True)
		if not row:
			frappe.throw(_("Campus does not exist."), title=_("Campus"))
		if row.company != self.company or row.branch != self.branch:
			frappe.throw(_("Campus must belong to the same company and branch."), title=_("Campus"))

	def _validate_code_unique_per_company(self):
		if not self.company or not self.student_code:
			return
		filters = {"company": self.company, "student_code": self.student_code}
		if self.name:
			filters["name"] = ["!=", self.name]
		if frappe.db.exists("Education Student", filters):
			frappe.throw(
				_("Student Code {0} already exists for this company.").format(self.student_code),
				title=_("Duplicate"),
			)

	def _validate_section_matches_branch_company(self):
		if not self.section:
			return
		row = frappe.db.get_value("Education Section", self.section, ["company", "branch"], as_dict=True)
		if not row:
			frappe.throw(_("Section does not exist."), title=_("Section"))
		if row.company != self.company or row.branch != self.branch:
			frappe.throw(_("Section must belong to the same company and branch."), title=_("Section"))

	def _ensure_customer(self):
		if self.customer:
			return
		customer_name = self._customer_display_name()
		existing = frappe.db.get_value(
			"Customer",
			{"company": self.company, "customer_name": customer_name},
			"name",
		)
		if existing:
			self.db_set("customer", existing, update_modified=False)
			return
		c = frappe.get_doc(
			{
				"doctype": "Customer",
				"company": self.company,
				"customer_name": customer_name,
				"status": "Active",
				"email": self.guardian_email,
				"phone": self.guardian_phone,
			}
		).insert(ignore_permissions=True)
		self.db_set("customer", c.name, update_modified=False)
