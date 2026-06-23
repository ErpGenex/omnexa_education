# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Branch-scoped education demo seed — invoked from Branch → Demo data tab."""

from __future__ import annotations

import frappe
from frappe import _

from omnexa_education.education_demo.education_demo_seed import (
	_link_portal_users,
	_resolve_company_branch,
	_seed_institution,
	get_demo_credentials,
)
from omnexa_education.education_demo.institution_specs import INSTITUTION_DEMO_SPECS, INSTITUTION_TYPES
from omnexa_education.education_demo.role_specs import ROLE_SPECS


def _filter_specs(institution_type: str | None) -> list[dict]:
	mode = (institution_type or "All 5 Types").strip()
	if mode in ("", "All 5 Types", "All"):
		return list(INSTITUTION_DEMO_SPECS)
	return [s for s in INSTITUTION_DEMO_SPECS if s.get("institution_type") == mode]


def seed_education_branch_demo(
	company: str,
	branch: str,
	*,
	institution_type: str | None = "All 5 Types",
	seed_roles: int = 1,
	sync_laravel: int = 0,
) -> dict:
	"""Seed education demo for one branch (System Manager only — caller must enforce)."""
	if not frappe.db.exists("Company", company):
		frappe.throw(_("Company {0} not found").format(company))
	if not frappe.db.exists("Branch", branch):
		frappe.throw(_("Branch {0} not found").format(branch))
	if frappe.db.get_value("Branch", branch, "company") != company:
		frappe.throw(_("Branch does not belong to company {0}").format(company))

	from omnexa_education.api.education_role_demo import ensure_education_roles, sync_journey_page_roles

	ensure_education_roles()
	sync_journey_page_roles()

	specs = _filter_specs(institution_type)
	if not specs:
		frappe.throw(_("No demo spec for institution type: {0}").format(institution_type))

	institutions = []
	for spec in specs:
		institutions.append(_seed_institution(company, branch, spec))

	users = []
	if seed_roles:
		from omnexa_education.education_demo.education_demo_seed import _ensure_demo_user

		for spec in ROLE_SPECS:
			users.append(_ensure_demo_user(spec, company, branch))
		_link_portal_users(company, branch)

	settings = frappe.get_single("Education Settings")
	settings.enable_k12_modules = 1
	settings.enable_university_modules = 1
	if institution_type and institution_type not in ("All 5 Types", "All", ""):
		settings.default_institution_type = institution_type if institution_type in (
			"School",
			"Academy",
			"University",
			"Training Center",
			"Institute",
		) else settings.default_institution_type or "University"
	settings.save(ignore_permissions=True)

	laravel_queued = 0
	if sync_laravel and frappe.get_single("Education Settings").enable_laravel_tlms:
		laravel_queued = _queue_laravel_program_sync(company, branch, institutions)

	frappe.db.commit()
	return {
		"ok": True,
		"company": company,
		"branch": branch,
		"institution_type": institution_type or "All 5 Types",
		"institutions_seeded": len(institutions),
		"institutions": institutions,
		"users": get_demo_credentials()["users"] if seed_roles else [],
		"laravel_queued": laravel_queued,
		"message": _("Education demo seeded for branch {0} — {1} institution(s).").format(branch, len(institutions)),
	}


def _queue_laravel_program_sync(company: str, branch: str, institution_stats: list[dict]) -> int:
	from omnexa_education.api import laravel_client

	if not laravel_client.is_laravel_enabled():
		return 0
	queued = 0
	for row in institution_stats:
		inst = row.get("institution")
		if not inst:
			continue
		programs = frappe.get_all(
			"Education Program",
			filters={"institution": inst, "company": company},
			fields=["name", "program_code", "program_name", "degree_level"],
		)
		if programs:
			laravel_client.enqueue_sync(
				"sync_programs",
				"Education Institution",
				inst,
				{"institution": inst, "company": company, "branch": branch, "programs": programs},
			)
			queued += 1
	return queued


def get_branch_education_demo_options() -> dict:
	return {
		"institution_types": ["All 5 Types", *INSTITUTION_TYPES],
		"password": "Education@Demo2026",
		"workcenter_route": "/app/education-workcenter",
	}
