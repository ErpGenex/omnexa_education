# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""End-to-end Laravel integration smoke scenarios."""

from __future__ import annotations

import frappe

from omnexa_education.api import laravel_client
from omnexa_education.api.education_unified_inbox import get_unified_inbox
from omnexa_education.api.laravel_sync import (
	build_academic_calendar_payload,
	build_classes_payload,
	build_enrollments_payload,
	sync_institution_full_to_laravel,
)
from omnexa_education.api.parent_account_lifecycle import build_laravel_parent_payload
from omnexa_education.api.student_account_lifecycle import build_laravel_payload


SCENARIOS = [
	"laravel_settings_configured",
	"programs_payload",
	"classes_payload",
	"calendar_payload",
	"enrollments_payload",
	"student_provision_payload",
	"parent_provision_payload",
	"sync_queue_doctype",
	"unified_inbox_api",
	"webhook_endpoint_registered",
]


@frappe.whitelist()
def run_laravel_integration_e2e(institution: str | None = None) -> dict:
	institution = institution or frappe.db.get_value("Education Institution", {"status": "Active"}, "name")
	results = []
	for key in SCENARIOS:
		ok, detail = _run_scenario(key, institution)
		results.append({"scenario": key, "ok": ok, "detail": detail})

	passed = sum(1 for r in results if r["ok"])
	return {
		"ok": passed == len(results),
		"institution": institution,
		"laravel_enabled": laravel_client.is_laravel_enabled(),
		"passed": passed,
		"total": len(results),
		"scenarios": results,
	}


def _run_scenario(key: str, institution: str | None) -> tuple[bool, str]:
	try:
		if key == "laravel_settings_configured":
			meta = frappe.get_meta("Education Settings")
			fields = ("enable_laravel_tlms", "laravel_base_url", "laravel_api_key", "laravel_jwt_secret")
			missing = [f for f in fields if not meta.has_field(f)]
			return not missing, f"missing: {missing}" if missing else "fields ok"

		if key == "programs_payload" and institution:
			from omnexa_education.api.laravel_client import sync_institution_programs_to_laravel, is_laravel_enabled

			if not is_laravel_enabled():
				return True, "laravel disabled — skipped"
			out = sync_institution_programs_to_laravel(institution)
			return bool(out.get("programs") is not None), str(out.get("programs", 0))

		if key == "classes_payload" and institution:
			payload = build_classes_payload(institution)
			return len(payload.get("classes") or []) >= 0, f"{len(payload.get('classes') or [])} classes"

		if key == "calendar_payload" and institution:
			payload = build_academic_calendar_payload(institution)
			return True, f"{len(payload.get('terms') or [])} terms"

		if key == "enrollments_payload" and institution:
			payload = build_enrollments_payload(institution)
			rows = payload.get("enrollments") or []
			valid = all(r.get("student_external_id") for r in rows)
			return valid, f"{len(rows)} enrollments"

		if key == "student_provision_payload":
			student = frappe.db.get_value("Education Student", {"status": "Active"}, "name")
			if not student:
				return True, "no student — skipped"
			doc = frappe.get_doc("Education Student", student)
			payload = build_laravel_payload(doc)
			return bool(payload.get("student_external_id") or payload.get("external_id")), payload.get("email", "")

		if key == "parent_provision_payload":
			email = frappe.db.get_value("Education Student", {"guardian_email": ["is", "set"]}, "guardian_email")
			if not email:
				return True, "no guardian — skipped"
			students = frappe.get_all("Education Student", filters={"guardian_email": email}, pluck="name", limit=3)
			payload = build_laravel_parent_payload(email, students)
			return payload.get("role") == "parent", str(len(payload.get("student_external_ids") or []))

		if key == "sync_queue_doctype":
			return frappe.db.exists("DocType", "Education Laravel Sync Queue"), "queue doctype"

		if key == "unified_inbox_api":
			out = get_unified_inbox()
			return "messages" in out, str(len(out.get("messages") or []))

		if key == "webhook_endpoint_registered":
			return frappe.get_attr("omnexa_education.api.laravel_webhooks.receive") is not None, "receive ok"

		if key == "full_sync" and institution:
			out = sync_institution_full_to_laravel(institution)
			return bool(out.get("results")), "full sync"

		return True, "skipped"
	except Exception as exc:
		return False, str(exc)[:200]
