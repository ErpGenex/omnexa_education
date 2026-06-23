# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.tests.utils import FrappeTestCase


class TestEducationDemoSeed(FrappeTestCase):
	def test_demo_seed_idempotent(self):
		from omnexa_education.education_demo.education_demo_seed import seed_education_demo

		frappe.set_user("Administrator")
		result = seed_education_demo()
		self.assertTrue(result.get("ok"))
		self.assertGreaterEqual(len(result.get("institutions") or []), 5)
		self.assertGreaterEqual(len(result.get("users") or []), 7)

		# Second run should not fail
		result2 = seed_education_demo()
		self.assertTrue(result2.get("ok"))
