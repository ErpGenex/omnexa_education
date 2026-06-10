# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Online admissions, waitlist, and lottery."""

from __future__ import annotations

import json
import random

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def submit_online_application(
	applicant_name: str,
	institution: str,
	academic_year: str,
	grade_level: str | None = None,
	program: str | None = None,
	guardian_email: str | None = None,
	payload: str | None = None,
) -> dict:
	if not (applicant_name and institution and academic_year):
		frappe.throw(_("applicant_name, institution, and academic_year are required"))
	student_payload = {}
	if payload:
		try:
			student_payload = json.loads(payload)
		except json.JSONDecodeError:
			frappe.throw(_("Invalid payload JSON"))
	company = frappe.db.get_value("Education Institution", institution, "company")
	branch = frappe.db.get_value("Education Institution", institution, "branch")
	doc = frappe.get_doc(
		{
			"doctype": "Education Online Application",
			"applicant_name": applicant_name,
			"institution": institution,
			"academic_year": academic_year,
			"grade_level": grade_level,
			"program": program,
			"guardian_email": guardian_email,
			"application_payload": json.dumps(student_payload) if student_payload else None,
			"company": company,
			"branch": branch,
			"status": "Submitted",
		}
	).insert(ignore_permissions=True)
	return {"application": doc.name, "status": doc.status}


@frappe.whitelist()
def promote_online_application(application: str) -> dict:
	doc = frappe.get_doc("Education Online Application", application)
	if doc.admission_application:
		return {"admission_application": doc.admission_application, "already_linked": True}
	admission = frappe.get_doc(
		{
			"doctype": "Education Admission Application",
			"student_name": doc.applicant_name,
			"institution": doc.institution,
			"academic_year": doc.academic_year,
			"grade_level": doc.grade_level,
			"program": doc.program,
			"company": doc.company,
			"branch": doc.branch,
			"status": "Submitted",
		}
	).insert(ignore_permissions=True)
	doc.admission_application = admission.name
	doc.status = "Reviewed"
	doc.save(ignore_permissions=True)
	return {"admission_application": admission.name}


@frappe.whitelist()
def sync_waitlist_count(pool: str) -> dict:
	doc = frappe.get_doc("Education Waitlist Pool", pool)
	count = frappe.db.count(
		"Education Admission Application",
		{
			"institution": doc.institution,
			"academic_year": doc.academic_year,
			"status": "Waitlisted",
		},
	)
	doc.waitlist_count = count
	doc.save(ignore_permissions=True)
	return {"pool": pool, "waitlist_count": count}


@frappe.whitelist()
def run_lottery(pool: str, seats: int | None = None) -> dict:
	pool_doc = frappe.get_doc("Education Waitlist Pool", pool)
	seats = int(seats or pool_doc.capacity or 0)
	if seats <= 0:
		frappe.throw(_("seats must be greater than zero"))
	applicants = frappe.get_all(
		"Education Admission Application",
		filters={
			"institution": pool_doc.institution,
			"academic_year": pool_doc.academic_year,
			"status": "Waitlisted",
		},
		pluck="name",
	)
	random.shuffle(applicants)
	winners = applicants[:seats]
	for name in winners:
		frappe.db.set_value("Education Admission Application", name, "status", "Accepted")
	run = frappe.get_doc(
		{
			"doctype": "Education Lottery Run",
			"waitlist_pool": pool,
			"run_date": frappe.utils.now_datetime(),
			"seats_offered": len(winners),
			"status": "Completed",
			"institution": pool_doc.institution,
			"company": pool_doc.company,
			"branch": pool_doc.branch,
		}
	).insert(ignore_permissions=True)
	run.submit()
	sync_waitlist_count(pool)
	return {"lottery_run": run.name, "winners": winners, "seats_offered": len(winners)}


@frappe.whitelist()
def get_admissions_portal_config(institution: str | None = None) -> dict:
	return {
		"submit_method": "omnexa_education.api.education_admissions.submit_online_application",
		"institution": institution,
		"fields": ["applicant_name", "academic_year", "grade_level", "program", "guardian_email"],
	}
