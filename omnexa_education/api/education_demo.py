# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Education demo hub API — multi-institution context, seed, credentials."""

from __future__ import annotations

import frappe
from frappe import _

from omnexa_education.education_demo.institution_specs import (
	ACADEMY_LIFECYCLE_PHASES,
	ACADEMY_QA_METRICS,
	ACADEMY_TYPES,
	INSTITUTION_TYPES,
)
from omnexa_education.education_demo.education_demo_seed import (
	get_demo_credentials,
	get_institution_demo_stats,
	seed_education_demo,
	_resolve_company_branch,
)
from omnexa_education.education_global_benchmark import get_global_sis_score


@frappe.whitelist()
def seed_demo(company: str | None = None, branch: str | None = None, institution_type: str | None = None) -> dict:
	frappe.only_for(("System Manager", "Education Manager"))
	from omnexa_education.education_demo.branch_demo_seed import seed_education_branch_demo, _filter_specs

	specs = _filter_specs(institution_type)
	total_students = sum(s.get("demo_students", 500) for s in specs)
	company, branch = _resolve_company_branch(company, branch)

	if total_students > 300:
		job = frappe.enqueue(
			"omnexa_education.education_demo.branch_demo_seed.seed_education_branch_demo",
			queue="long",
			timeout=7200,
			company=company,
			branch=branch,
			institution_type=institution_type or "All 5 Types",
			seed_roles=1,
			sync_laravel=0,
		)
		return {
			"ok": True,
			"queued": True,
			"job_id": job,
			"message": _("Full lifecycle demo seed started in background (~{0} students). Refresh Workcenter in a few minutes.").format(
				total_students
			),
		}

	return seed_education_demo(company=company, branch=branch, institution_type=institution_type)


@frappe.whitelist()
def get_demo_credentials_api() -> dict:
	frappe.only_for("System Manager")
	return get_demo_credentials()


@frappe.whitelist()
def get_demo_hub_context(company: str | None = None, branch: str | None = None) -> dict:
	from omnexa_education.education_demo.education_demo_seed import _resolve_company_branch

	try:
		company, branch = _resolve_company_branch(company, branch)
	except Exception:
		company = company or frappe.defaults.get_user_default("Company") or ""
		branch = branch or frappe.defaults.get_user_default("Branch") or ""
	benchmark = get_global_sis_score()
	institutions = get_institution_demo_stats(company)
	seeded_count = sum(1 for i in institutions if i.get("seeded"))
	return {
		"company": company,
		"branch": branch,
		"institution_types": list(INSTITUTION_TYPES),
		"academy_types": list(ACADEMY_TYPES),
		"academy_lifecycle": ACADEMY_LIFECYCLE_PHASES,
		"academy_qa_metrics": ACADEMY_QA_METRICS,
		"institutions": institutions,
		"demo_seeded": seeded_count >= len(institutions) and seeded_count > 0,
		"global_benchmark": benchmark,
		"credentials": get_demo_credentials() if frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles() else {"password": "", "users": []},
		"can_seed": bool(
			frappe.session.user == "Administrator"
			or "System Manager" in frappe.get_roles()
			or "Education Manager" in frappe.get_roles()
		),
		"institution_type_options": ["All 5 Types", *INSTITUTION_TYPES],
	}
