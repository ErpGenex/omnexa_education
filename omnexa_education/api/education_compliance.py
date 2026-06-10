# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""FERPA audit log and student consent."""

from __future__ import annotations

import frappe
from frappe import _


def log_ferpa_access(
	student: str,
	resource_type: str,
	resource_name: str | None = None,
	purpose: str | None = None,
) -> str:
	student_doc = frappe.get_doc("Education Student", student)
	doc = frappe.get_doc(
		{
			"doctype": "Education Ferpa Access Log",
			"student": student,
			"accessed_by": frappe.session.user,
			"access_datetime": frappe.utils.now_datetime(),
			"resource_type": resource_type,
			"resource_name": resource_name,
			"purpose": purpose,
			"institution": student_doc.institution,
			"company": student_doc.company,
			"branch": student_doc.branch,
		}
	).insert(ignore_permissions=True)
	return doc.name


@frappe.whitelist()
def record_student_consent(
	student: str,
	consent_type: str,
	consent_given: int = 1,
	guardian_name: str | None = None,
) -> dict:
	student_doc = frappe.get_doc("Education Student", student)
	doc = frappe.get_doc(
		{
			"doctype": "Education Student Consent",
			"student": student,
			"consent_type": consent_type,
			"consent_given": consent_given,
			"signed_on": frappe.utils.today(),
			"guardian_name": guardian_name,
			"institution": student_doc.institution,
			"company": student_doc.company,
			"branch": student_doc.branch,
		}
	).insert(ignore_permissions=True)
	return {"consent": doc.name}


@frappe.whitelist()
def check_ferpa_consent(student: str, consent_type: str = "FERPA Directory") -> dict:
	consent = frappe.db.get_value(
		"Education Student Consent",
		{"student": student, "consent_type": consent_type, "consent_given": 1},
		"name",
	)
	return {"student": student, "consent_type": consent_type, "has_consent": bool(consent)}


@frappe.whitelist()
def get_ferpa_audit_trail(student: str, limit: int = 50) -> list[dict]:
	log_ferpa_access(student, "Education Student", student, "Audit trail view")
	return frappe.get_all(
		"Education Ferpa Access Log",
		filters={"student": student},
		fields=["name", "accessed_by", "access_datetime", "resource_type", "resource_name", "purpose"],
		order_by="access_datetime desc",
		limit=int(limit),
	)


@frappe.whitelist()
def get_student_record(student: str) -> dict:
	if not check_ferpa_consent(student)["has_consent"] and frappe.session.user != "Administrator":
		frappe.throw(_("FERPA consent required to access student record"))
	log_ferpa_access(student, "Education Student", student, "Mobile/API read")
	doc = frappe.get_doc("Education Student", student)
	return doc.as_dict()
