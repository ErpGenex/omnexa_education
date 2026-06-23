# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Public EduSphere education website APIs."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint, get_url


DEFAULT_HERO = (
	"https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=1600&q=80"
)


def _public_url(path: str | None) -> str:
	if not path:
		return ""
	if path.startswith(("http://", "https://")):
		return path
	return get_url(path)


@frappe.whitelist(allow_guest=True)
def get_site_config(institution: str | None = None) -> dict:
	institutions = frappe.get_all(
		"Education Institution",
		filters={"status": "Active"},
		fields=["name", "institution_name", "institution_type", "company", "city"],
		limit=30,
		order_by="institution_name asc",
	)
	program_count = frappe.db.count("Education Program", {"status": "Active"})
	student_count = frappe.db.count("Education Student", {"status": "Active"})
	teacher_count = frappe.db.count("Education Teacher", {"status": "Active"})

	selected = None
	if institution and frappe.db.exists("Education Institution", institution):
		selected = frappe.get_doc("Education Institution", institution)

	return {
		"brand_name_ar": "EduSphere",
		"brand_name_en": "EduSphere",
		"tagline_ar": "من الاستفسار إلى التخرج — رحلة تعليمية متكاملة",
		"tagline_en": "From inquiry to graduation — a complete education journey",
		"hero_text_ar": "بوابة القبول والتسجيل الأكاديمي للمؤسسات التعليمية",
		"hero_text_en": "Admissions and academic enrollment portal for educational institutions",
		"hero_image": DEFAULT_HERO,
		"logo": _public_url("/assets/omnexa_education/logo.png"),
		"primary_color": "#003366",
		"institution": institution,
		"selected_institution": selected.as_dict() if selected else None,
		"institutions": institutions,
		"stats": {
			"institutions": len(institutions),
			"programs": program_count,
			"students": student_count,
			"teachers": teacher_count,
		},
		"features": {
			"online_apply": True,
			"programs": True,
			"laravel_portal": True,
		},
		"urls": {
			"home": "/education",
			"programs": "/education/programs",
			"apply": "/education/apply",
			"desk": "/app/education-workcenter",
			"login": "/login",
		},
	}


@frappe.whitelist(allow_guest=True)
def get_public_programs(institution: str | None = None) -> list[dict]:
	filters: dict = {"status": "Active"}
	if institution:
		filters["institution"] = institution
	rows = frappe.get_all(
		"Education Program",
		filters=filters,
		fields=["name", "program_name", "institution", "program_type", "duration_years"],
		limit=80,
		order_by="program_name asc",
	)
	for row in rows:
		row["institution_name"] = frappe.db.get_value(
			"Education Institution", row.institution, "institution_name"
		)
	return rows


@frappe.whitelist(allow_guest=True)
def get_public_institutions() -> list[dict]:
	return frappe.get_all(
		"Education Institution",
		filters={"status": "Active"},
		fields=["name", "institution_name", "institution_type", "city", "company"],
		limit=50,
		order_by="institution_name asc",
	)
