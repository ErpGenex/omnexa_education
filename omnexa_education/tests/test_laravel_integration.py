# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase


class TestLaravelIntegration(FrappeTestCase):
	def setUp(self):
		super().setUp()
		frappe.flags.in_import = True
		frappe.set_user("Administrator")
		frappe.defaults.set_user_default("omnexa_view_all_branches", 1, "Administrator")
		frappe.db.set_single_value("Education Settings", "enable_laravel_tlms", 0)
		frappe.db.set_single_value("Education Settings", "auto_provision_student_user", 1)
		sfx = frappe.generate_hash(length=4).upper()
		self.company = self._create_company(f"LR{sfx}")
		self.branch = self._create_branch(self.company, f"L{sfx[:3]}", f"Laravel Campus {sfx}")

	def test_laravel_disabled_by_default(self):
		from omnexa_education.api.laravel_client import is_laravel_enabled

		self.assertFalse(is_laravel_enabled())

	def test_provision_student_creates_user(self):
		from omnexa_education.api.student_account_lifecycle import provision_student

		code = frappe.generate_hash(length=6)
		student = self._create_student(f"T{code}", f"guardian.{code}@test.local")
		out = provision_student(student.name, trigger="System")
		self.assertEqual(out["account_access_status"], "Active")
		self.assertTrue(frappe.db.get_value("Education Student", student.name, "user"))

	def test_financial_hold(self):
		from omnexa_education.api.student_account_lifecycle import apply_financial_hold, provision_student

		code = frappe.generate_hash(length=6)
		student = self._create_student(f"H{code}")
		provision_student(student.name)
		apply_financial_hold(student.name, "Test overdue", trigger="Financial")
		self.assertEqual(frappe.db.get_value("Education Student", student.name, "financial_hold"), 1)
		self.assertEqual(
			frappe.db.get_value("Education Student", student.name, "account_access_status"),
			"Financial Hold",
		)

	def test_education_settings_has_laravel_fields(self):
		meta = frappe.get_meta("Education Settings")
		for field in ("enable_laravel_tlms", "laravel_base_url", "laravel_api_key", "auto_suspend_on_overdue"):
			self.assertTrue(meta.has_field(field), f"Missing field {field}")

	def test_lms_provider_includes_laravel(self):
		meta = frappe.get_meta("Education Lms Course Link")
		options = meta.get_field("lms_provider").options or ""
		self.assertIn("Laravel TLMS", options)

	def _create_company(self, abbr: str):
		if not frappe.db.exists("Currency", "EGP"):
			frappe.get_doc({"doctype": "Currency", "currency_name": "EGP", "symbol": "E£", "enabled": 1}).insert(
				ignore_permissions=True
			)
		if not frappe.db.exists("Country", "Egypt"):
			frappe.get_doc({"doctype": "Country", "country_name": "Egypt", "code": "EG"}).insert(ignore_permissions=True)
		doc = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": f"Laravel Test Co {abbr}",
				"abbr": abbr[:10],
				"default_currency": "EGP",
				"country": "Egypt",
				"status": "Active",
			}
		).insert(ignore_permissions=True)
		return doc.name

	def _create_branch(self, company: str, code: str, name: str):
		payload = {
			"doctype": "Branch",
			"company": company,
			"branch_name": name,
			"branch_code": code,
			"status": "Active",
		}
		if frappe.get_meta("Branch").has_field("eta_usb_signing_pin"):
			payload["eta_usb_signing_pin"] = "0000"
		return frappe.get_doc(payload).insert(ignore_permissions=True).name

	def _create_student(self, code: str, email: str | None = None):
		return frappe.get_doc(
			{
				"doctype": "Education Student",
				"student_code": code,
				"student_name": "Test Student Laravel",
				"company": self.company,
				"branch": self.branch,
				"status": "Active",
				"guardian_email": email,
			}
		).insert(ignore_permissions=True)
