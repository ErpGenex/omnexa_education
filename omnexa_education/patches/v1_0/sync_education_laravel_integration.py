# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Post-migrate: education roles + Laravel integration defaults."""

from __future__ import annotations

import frappe


def execute():
	from omnexa_education.api.education_role_demo import ensure_education_roles, sync_journey_page_roles

	ensure_education_roles()
	sync_journey_page_roles()

	settings = frappe.get_single("Education Settings")
	updates = {}
	if not settings.laravel_institution_header:
		updates["laravel_institution_header"] = "X-ErpGenEx-School"
	if settings.laravel_sync_batch_size is None:
		updates["laravel_sync_batch_size"] = 50
	if settings.financial_hold_grace_days is None:
		updates["financial_hold_grace_days"] = 7
	if updates:
		for k, v in updates.items():
			setattr(settings, k, v)
		settings.save(ignore_permissions=True)
