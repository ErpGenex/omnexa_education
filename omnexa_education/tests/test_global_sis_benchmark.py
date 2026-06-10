# Copyright (c) 2026, Omnexa

import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_education.education_global_benchmark import GLOBAL_LEADER_TARGET, get_global_sis_score


class TestGlobalSisBenchmark(FrappeTestCase):
	def test_score_meets_global_leader_target(self):
		score = get_global_sis_score()
		self.assertGreaterEqual(score["weighted_score"], GLOBAL_LEADER_TARGET)
		self.assertTrue(score["global_leader_gate"])
		self.assertEqual(score["gaps_total"], 96)
		self.assertEqual(score["gaps_closed"], 96)
		self.assertEqual(score["gaps_open"], 0)
