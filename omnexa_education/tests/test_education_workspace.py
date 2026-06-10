# Copyright (c) 2026, Omnexa

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_education.workspace.education_workspace import get_workspace_coverage, sync_education_workspace_menu


class TestEducationWorkspace(FrappeTestCase):
	def test_workspace_sync_rebuilds(self):
		stats = sync_education_workspace_menu(save=True, rebuild=True)
		self.assertGreater(stats["sections"], 10)
		self.assertGreater(stats["total_links"], 40)
		self.assertGreater(stats["shortcuts"], 40)

	def test_workspace_coverage(self):
		cov = get_workspace_coverage()
		self.assertEqual(cov["education_doctypes_missing"], [])
		self.assertGreaterEqual(cov["doctypes"], 30)

	def test_education_workspace_exists(self):
		self.assertTrue(frappe.db.exists("Workspace", "Education"))
