# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Document event handlers for Laravel sync."""

from __future__ import annotations

import frappe


def on_course_enrollment_submit(doc, method=None):
	from omnexa_education.api.laravel_sync import sync_single_course_enrollment

	sync_single_course_enrollment(doc)


def on_section_update(doc, method=None):
	from omnexa_education.api.laravel_sync import sync_institution_classes_to_laravel

	if not doc.campus:
		return
	institution = frappe.db.get_value("Education Campus", doc.campus, "institution")
	if institution:
		sync_institution_classes_to_laravel(institution)


def on_program_update(doc, method=None):
	from omnexa_education.api.laravel_client import sync_institution_programs_to_laravel

	if doc.institution:
		sync_institution_programs_to_laravel(doc.institution)

