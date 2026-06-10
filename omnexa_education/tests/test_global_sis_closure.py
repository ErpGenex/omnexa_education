# Copyright (c) 2026, Omnexa

"""Global SIS Wave 2+3 closure — score gate, APIs, DocTypes."""

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_education.education_global_benchmark import GLOBAL_LEADER_TARGET, get_global_sis_score

WAVE23_DOCTYPES = [
	"Education Waitlist Pool",
	"Education Lottery Run",
	"Education Online Application",
	"Education Timetable Template",
	"Education Grading Scale",
	"Education Official Transcript",
	"Education Ferpa Access Log",
	"Education Student Consent",
	"Education Mobile Device Token",
	"Education Lms Course Link",
	"Education Predictive Alert",
	"Education Announcement",
	"Education Library Book",
	"Education Transport Route",
	"Education Hostel Room",
	"Education Scholarship",
]


class TestGlobalSisClosure(FrappeTestCase):
	def setUp(self):
		super().setUp()
		frappe.set_user("Administrator")

	def test_global_sis_score_gate(self):
		score = get_global_sis_score()
		self.assertGreaterEqual(score["weighted_score"], GLOBAL_LEADER_TARGET)
		self.assertTrue(score["global_leader_gate"])
		self.assertEqual(score["gaps_closed"], 96)
		self.assertEqual(score["gaps_open"], 0)

	def test_wave23_doctypes_installed(self):
		for dt in WAVE23_DOCTYPES:
			self.assertTrue(frappe.db.exists("DocType", dt), msg=dt)

	def test_mobile_config_api(self):
		from omnexa_education.api.education_mobile_api import get_mobile_config

		out = get_mobile_config()
		self.assertIn("pwa_manifest", out)
		self.assertEqual(out["api_version"], "global-sis-3")

	def test_gpa_engine(self):
		student = frappe.db.get_value("Education Student", {}, "name")
		if not student:
			self.skipTest("no student")
		from omnexa_education.api.education_grading import compute_student_gpa

		out = compute_student_gpa(student)
		self.assertIn("gpa", out)

	def test_ferpa_audit_api(self):
		student = frappe.db.get_value("Education Student", {}, "name")
		if not student:
			self.skipTest("no student")
		from omnexa_education.api.education_compliance import get_ferpa_audit_trail, record_student_consent

		record_student_consent(student, "FERPA Directory")
		trail = get_ferpa_audit_trail(student, limit=5)
		self.assertIsInstance(trail, list)

	def test_admissions_portal_config(self):
		from omnexa_education.api.education_admissions import get_admissions_portal_config

		out = get_admissions_portal_config()
		self.assertIn("submit_method", out)

	def test_executive_dashboard(self):
		from omnexa_education.api.education_analytics import get_executive_dashboard

		out = get_executive_dashboard()
		self.assertIn("students", out)

	def test_wave23_pages_exist(self):
		for page in (
			"education-parent-mobile",
			"education-admissions-portal",
			"education-analytics-dashboard",
			"education-executive-dashboard",
		):
			self.assertTrue(frappe.db.exists("Page", page), msg=page)

	def test_print_format_transcript(self):
		self.assertTrue(frappe.db.exists("Print Format", "Education Official Transcript"))
