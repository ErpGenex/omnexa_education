# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate, today


class TestEducationMasterData(FrappeTestCase):
	def setUp(self):
		super().setUp()
		self._ensure_geo()
		sfx = frappe.generate_hash(length=4).upper()
		self.company = self._create_company(f"ED{sfx}")
		self.branch = self._create_branch(self.company, f"E{sfx[:3]}", f"Campus {sfx}")

	def _ensure_geo(self):
		if not frappe.db.exists("Currency", "EGP"):
			frappe.get_doc(
				{"doctype": "Currency", "currency_name": "EGP", "symbol": "E£", "enabled": 1}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("Country", "Egypt"):
			frappe.get_doc({"doctype": "Country", "country_name": "Egypt", "code": "EG"}).insert(
				ignore_permissions=True
			)

	def _create_company(self, abbr: str):
		doc = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": f"Education Co {abbr}",
				"abbr": abbr[:10],
				"default_currency": "EGP",
				"country": "Egypt",
				"status": "Active",
			}
		)
		doc.insert(ignore_permissions=True)
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
		doc = frappe.get_doc(payload)
		doc.insert(ignore_permissions=True)
		return doc.name

	def test_master_data_chain_inserts(self):
		cur = frappe.get_doc(
			{
				"doctype": "Education Curriculum",
				"curriculum_code": "BRIT",
				"curriculum_name": "British Curriculum",
				"company": self.company,
				"framework": "British",
				"grading_scheme": "Percentage",
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		inst = frappe.get_doc(
			{
				"doctype": "Education Institution",
				"institution_code": "SCH1",
				"institution_name": "Global School",
				"company": self.company,
				"institution_type": "School",
				"curriculum_default": cur.name,
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		campus = frappe.get_doc(
			{
				"doctype": "Education Campus",
				"campus_code": "C1",
				"campus_name": "Main Campus",
				"company": self.company,
				"branch": self.branch,
				"institution": inst.name,
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		dept = frappe.get_doc(
			{
				"doctype": "Education Department",
				"department_code": "SCI",
				"department_name": "Science",
				"company": self.company,
				"branch": self.branch,
				"campus": campus.name,
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		start = getdate(today())
		end = add_days(start, 300)
		year = frappe.get_doc(
			{
				"doctype": "Education Academic Year",
				"year_code": "2026-2027",
				"title": "AY 2026-2027",
				"company": self.company,
				"institution": inst.name,
				"curriculum": cur.name,
				"start_date": start,
				"end_date": end,
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		term = frappe.get_doc(
			{
				"doctype": "Education Term",
				"term_code": "T1",
				"term_name": "Term 1",
				"company": self.company,
				"institution": inst.name,
				"academic_year": year.name,
				"term_type": "Term",
				"start_date": start,
				"end_date": add_days(start, 90),
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		grade = frappe.get_doc(
			{
				"doctype": "Education Grade Level",
				"grade_code": "G1",
				"grade_name": "Grade 1",
				"company": self.company,
				"institution": inst.name,
				"curriculum": cur.name,
				"stage": "Primary",
				"sequence": 1,
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		section = frappe.get_doc(
			{
				"doctype": "Education Section",
				"section_code": "G1-A",
				"section_name": "Grade 1 - A",
				"company": self.company,
				"branch": self.branch,
				"campus": campus.name,
				"academic_year": year.name,
				"grade_level": grade.name,
				"capacity": 30,
				"homeroom_department": dept.name,
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		subj = frappe.get_doc(
			{
				"doctype": "Education Subject",
				"subject_code": "MATH",
				"subject_name": "Mathematics",
				"company": self.company,
				"curriculum": cur.name,
				"subject_area": "Mathematics",
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		self.assertTrue(inst.name)
		self.assertEqual(campus.branch, self.branch)
		self.assertEqual(section.grade_level, grade.name)
		self.assertEqual(term.academic_year, year.name)
		self.assertEqual(subj.curriculum, cur.name)

	def test_billing_invoice_creates_sales_invoice(self):
		# Minimal setup: GL accounts + fee item + student -> billing invoice -> sales invoice
		inc = frappe.get_doc(
			{
				"doctype": "GL Account",
				"company": self.company,
				"account_number": f"ED{frappe.generate_hash(length=4)}",
				"account_name": "Education Revenue",
				"is_group": 0,
			}
		).insert(ignore_permissions=True)

		fee = frappe.get_doc(
			{
				"doctype": "Education Fee Item",
				"fee_code": "BUS",
				"fee_name": "Bus Transport Fee",
				"company": self.company,
				"fee_category": "Transport (Bus)",
				"default_rate": 500,
				"income_account": inc.name,
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		inst = frappe.get_doc(
			{
				"doctype": "Education Institution",
				"institution_code": "SCH2",
				"institution_name": "Billing School",
				"company": self.company,
				"institution_type": "School",
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		student = frappe.get_doc(
			{
				"doctype": "Education Student",
				"student_code": "ST-1",
				"student_name": "Student One",
				"company": self.company,
				"branch": self.branch,
				"institution": inst.name,
				"guardian_email": "payer@example.com",
				"status": "Active",
			}
		).insert(ignore_permissions=True)
		student.reload()
		self.assertTrue(student.customer)

		inv = frappe.get_doc(
			{
				"doctype": "Education Billing Invoice",
				"naming_series": "EDINV-.#####",
				"company": self.company,
				"branch": self.branch,
				"student": student.name,
				"posting_date": today(),
				"currency": "EGP",
				"conversion_rate": 1,
				"items": [{"fee_item": fee.name, "qty": 1, "rate": 500}],
			}
		).insert(ignore_permissions=True)
		inv.submit()
		inv.reload()
		self.assertTrue(inv.sales_invoice)

		si = frappe.get_doc("Sales Invoice", inv.sales_invoice)
		self.assertEqual(si.docstatus, 1)
		self.assertEqual(si.company, self.company)
		self.assertEqual(si.branch, self.branch)
		self.assertEqual(si.customer, student.customer)
		self.assertEqual(float(si.grand_total), 500.0)

	def test_billing_cycle_generates_bulk_invoices_with_discount(self):
		inc = frappe.get_doc(
			{
				"doctype": "GL Account",
				"company": self.company,
				"account_number": f"ED{frappe.generate_hash(length=4)}",
				"account_name": "Education Revenue Cycle",
				"is_group": 0,
			}
		).insert(ignore_permissions=True)

		fee_tuition = frappe.get_doc(
			{
				"doctype": "Education Fee Item",
				"fee_code": "TUITION",
				"fee_name": "Tuition Fee",
				"company": self.company,
				"fee_category": "Tuition",
				"is_recurring": 1,
				"default_rate": 1000,
				"income_account": inc.name,
				"status": "Active",
			}
		).insert(ignore_permissions=True)
		fee_bus = frappe.get_doc(
			{
				"doctype": "Education Fee Item",
				"fee_code": "BUS2",
				"fee_name": "Bus Fee",
				"company": self.company,
				"fee_category": "Transport (Bus)",
				"default_rate": 200,
				"income_account": inc.name,
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		inst = frappe.get_doc(
			{
				"doctype": "Education Institution",
				"institution_code": "SCH3",
				"institution_name": "Cycle School",
				"company": self.company,
				"institution_type": "School",
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		start = getdate(today())
		year = frappe.get_doc(
			{
				"doctype": "Education Academic Year",
				"year_code": "2027-2028",
				"title": "AY 2027-2028",
				"company": self.company,
				"institution": inst.name,
				"curriculum": frappe.get_doc(
					{
						"doctype": "Education Curriculum",
						"curriculum_code": "NAT2",
						"curriculum_name": "National Curriculum 2",
						"company": self.company,
						"framework": "National",
						"grading_scheme": "Percentage",
						"status": "Active",
					}
				).insert(ignore_permissions=True).name,
				"start_date": start,
				"end_date": add_days(start, 320),
				"status": "Active",
			}
		).insert(ignore_permissions=True)

		plan = frappe.get_doc(
			{
				"doctype": "Education Fee Plan",
				"plan_code": "PLAN-A",
				"plan_name": "Plan A",
				"company": self.company,
				"branch": self.branch,
				"academic_year": year.name,
				"currency": "EGP",
				"installments_count": 2,
				"is_active": 1,
				"items": [
					{"fee_item": fee_tuition.name, "qty": 1, "rate": 1000},
					{"fee_item": fee_bus.name, "qty": 1, "rate": 200},
				],
			}
		).insert(ignore_permissions=True)

		disc = frappe.get_doc(
			{
				"doctype": "Education Discount Rule",
				"rule_code": "DISC10",
				"rule_name": "10% on Tuition",
				"company": self.company,
				"branch": self.branch,
				"discount_type": "Percent",
				"discount_value": 10,
				"scope": "Fee Category",
				"fee_category": "Tuition",
				"is_active": 1,
			}
		).insert(ignore_permissions=True)

		for idx in ("A", "B"):
			frappe.get_doc(
				{
					"doctype": "Education Student",
					"student_code": f"ST-C-{idx}",
					"student_name": f"Cycle Student {idx}",
					"company": self.company,
					"branch": self.branch,
					"institution": inst.name,
					"status": "Active",
				}
			).insert(ignore_permissions=True)

		cycle = frappe.get_doc(
			{
				"doctype": "Education Billing Cycle",
				"naming_series": "EDCYC-.#####",
				"company": self.company,
				"branch": self.branch,
				"academic_year": year.name,
				"cycle_name": "September Cycle",
				"posting_date": today(),
				"due_date": add_days(getdate(today()), 10),
				"fee_plan": plan.name,
				"installment_no": 1,
				"discount_rule": disc.name,
				"submit_invoices": 1,
			}
		).insert(ignore_permissions=True)
		cycle.submit()
		cycle.reload()
		self.assertEqual(int(cycle.generated_count), 2)

