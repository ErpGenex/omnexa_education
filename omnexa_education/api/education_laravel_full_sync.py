# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""One-click full sync: ErpGenEx SIS → Laravel TLMS + portal provisioning."""

from __future__ import annotations

import frappe
from frappe import _

from omnexa_education.api import laravel_client
from omnexa_education.api.education_laravel_bootstrap import (
	DEFAULT_API_KEY,
	DEFAULT_JWT_SECRET,
	DEFAULT_LARAVEL_URL,
	DEFAULT_WEBHOOK_SECRET,
	_configure_education_settings,
	_provision_all_parents,
	_seed_demo_inbox,
)
from omnexa_education.api.education_portal_link import ensure_demo_portal_users_linked
from omnexa_education.api.laravel_sync import sync_institution_full_to_laravel, sync_institutions_to_laravel
from omnexa_education.api.student_account_lifecycle import bulk_provision_students
from omnexa_education.api.teacher_account_lifecycle import bulk_provision_teachers


def _active_institutions(company: str | None = None, branch: str | None = None) -> list[str]:
	filters: dict = {"status": "Active"}
	if company:
		filters["company"] = company
	if branch:
		filters["branch"] = branch
	return frappe.get_all("Education Institution", filters=filters, pluck="name", limit=100)


@frappe.whitelist()
def sync_all_data_to_laravel(
	seed_demo_if_empty: int = 1,
	institution_type: str = "All 5 Types",
	process_queue: int = 1,
	configure_laravel: int = 1,
	company: str | None = None,
	branch: str | None = None,
) -> dict:
	"""Seed (if needed), link portal users, provision accounts, push all SIS data to Laravel."""
	frappe.only_for(("System Manager", "Education Manager"))

	company = company or frappe.defaults.get_user_default("Company") or ""
	branch = branch or frappe.defaults.get_user_default("Branch") or ""

	if configure_laravel and not laravel_client.is_laravel_enabled():
		_configure_education_settings(
			DEFAULT_LARAVEL_URL,
			DEFAULT_API_KEY,
			DEFAULT_WEBHOOK_SECRET,
			DEFAULT_JWT_SECRET,
		)

	if not laravel_client.is_laravel_enabled():
		frappe.throw(_("Enable Laravel TLMS in Education Settings first."))

	seed_result = None
	institutions = _active_institutions(company or None, branch or None)
	if not institutions and seed_demo_if_empty:
		from omnexa_education.api.education_demo import seed_demo

		seed_result = seed_demo(company=company or None, branch=branch or None, institution_type=institution_type)
		institutions = _active_institutions(company or None, branch or None)

	if not institutions:
		frappe.throw(_("No active Education Institution. Run Demo Simulation first."))

	portal_link = ensure_demo_portal_users_linked(company or None, branch or None)
	ping = laravel_client.ping()

	institutions_sync = sync_institutions_to_laravel(institutions)
	sync_results = []
	for inst in institutions:
		try:
			sync_results.append(sync_institution_full_to_laravel(inst))
		except Exception as exc:
			sync_results.append({"institution": inst, "ok": False, "error": str(exc)[:300]})
			frappe.log_error(frappe.get_traceback(), f"Laravel full sync failed: {inst}")

	students = bulk_provision_students(company=company or None, branch=branch or None)
	parents = _provision_all_parents()
	teachers = bulk_provision_teachers(company=company or None, branch=branch or None)

	queue_stats = None
	if process_queue:
		queue_stats = laravel_client.process_sync_queue(batch_size=20)

	inbox_seeded = _seed_demo_inbox()
	frappe.db.commit()

	ok_syncs = sum(1 for r in sync_results if r.get("ok"))
	laravel_ok = bool(ping.get("ok"))
	portals_ready = bool(portal_link.get("student_linked")) and portal_link.get("parent_children", 0) > 0

	return {
		"ok": laravel_ok and ok_syncs > 0,
		"message": _(
			"Synced {0}/{1} institutions · Students {2} · Parents {3} · Teachers {4}"
		).format(
			ok_syncs,
			len(institutions),
			students.get("provisioned", 0),
			parents.get("parents_ok", 0),
			teachers.get("provisioned", 0),
		),
		"ping": ping,
		"seed": seed_result,
		"institutions": institutions,
		"institutions_sync": institutions_sync,
		"sync_results": sync_results,
		"students": students,
		"parents": parents,
		"teachers": teachers,
		"portal_link": portal_link,
		"queue": queue_stats,
		"inbox_seeded": inbox_seeded,
		"portals_ready": portals_ready,
		"portal_hint": {
			"student_login": portal_link.get("student_email"),
			"parent_login": portal_link.get("parent_email"),
			"password": portal_link.get("demo_password"),
			"note": _(
				"Log out from Administrator and sign in with demo portal accounts to view Student/Parent portals."
			),
		},
	}


def execute():
	return sync_all_data_to_laravel()
