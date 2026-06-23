# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Public EduSphere education website APIs."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint, get_url

from omnexa_education.education_demo.institution_specs import (
	ACADEMY_LIFECYCLE_PHASES,
	INSTITUTION_DEMO_SPECS,
	INSTITUTION_TYPE_IMAGES,
)

DEFAULT_HERO = (
	"https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=1920&q=85"
)

CAMPUS_GALLERY = [
	"https://images.unsplash.com/photo-1541339907198-e08756dedf6d?auto=format&fit=crop&w=800&q=80",
	"https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=800&q=80",
	"https://images.unsplash.com/photo-1571260899304-425eee4c7efc?auto=format&fit=crop&w=800&q=80",
	"https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=800&q=80",
	"https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=800&q=80",
	"https://images.unsplash.com/photo-1434030214721-735608b96805?auto=format&fit=crop&w=800&q=80",
]


def _public_url(path: str | None) -> str:
	if not path:
		return ""
	if path.startswith(("http://", "https://")):
		return path
	return get_url(path)


def _institution_type_catalog() -> list[dict]:
	from omnexa_education.education_demo.education_demo_seed import get_institution_demo_stats

	stats = {row["institution_type"]: row for row in get_institution_demo_stats()}
	out = []
	for spec in INSTITUTION_DEMO_SPECS:
		itype = spec["institution_type"]
		row = stats.get(itype, {})
		active = bool(row.get("active"))
		seeded = bool(row.get("seeded"))
		out.append(
			{
				"institution_type": itype,
				"name": spec["name"],
				"name_ar": spec.get("name_ar", spec["name"]),
				"code": spec["code"],
				"active": active,
				"inactive": seeded and not active,
				"seeded": seeded,
				"students": cint(row.get("students")),
				"teachers": cint(row.get("teachers")),
				"applications": cint(row.get("applications")),
				"programs": cint(row.get("programs")),
				"image": INSTITUTION_TYPE_IMAGES.get(itype, DEFAULT_HERO),
				"institution": row.get("institution"),
				"academy_type": spec.get("academy_type"),
			}
		)
	return out


@frappe.whitelist(allow_guest=True)
def get_site_config(institution: str | None = None) -> dict:
	institutions = frappe.get_all(
		"Education Institution",
		filters={"status": "Active"},
		fields=["name", "institution_name", "institution_type", "company", "city"],
		limit=30,
		order_by="institution_name asc",
	)
	program_count = frappe.db.count(
		"Education Program",
		{"is_active": 1} if frappe.get_meta("Education Program").has_field("is_active") else {"status": "Active"},
	)
	student_count = frappe.db.count("Education Student", {"status": "Active"})
	teacher_count = frappe.db.count("Education Teacher", {"status": "Active"})
	type_catalog = _institution_type_catalog()

	selected = None
	if institution and frappe.db.exists("Education Institution", institution):
		selected = frappe.get_doc("Education Institution", institution)

	return {
		"brand_name_ar": "EduSphere",
		"brand_name_en": "EduSphere",
		"tagline_ar": "من الاستفسار إلى التخرج — رحلة تعليمية متكاملة على مستوى عالمي",
		"tagline_en": "From inquiry to graduation — a world-class integrated education journey",
		"hero_text_ar": "بوابة القبول والتسجيل الأكاديمي للجامعات والمدارس والأكاديميات — تصميم يليق بمؤسسات التعليم الرائدة",
		"hero_text_en": "Admissions and academic enrollment for universities, schools, and academies — built for excellence",
		"hero_image": DEFAULT_HERO,
		"logo": _public_url("/assets/omnexa_education/logo.png"),
		"primary_color": "#0b1f3a",
		"institution": institution,
		"selected_institution": selected.as_dict() if selected else None,
		"institutions": institutions,
		"institution_types": type_catalog,
		"lifecycle_phases": ACADEMY_LIFECYCLE_PHASES,
		"gallery": CAMPUS_GALLERY,
		"stats": {
			"institutions": len(institutions) or len([t for t in type_catalog if t.get("seeded")]),
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
			"laravel_portal": "https://kemetgate.com",
			"laravel_login": "https://kemetgate.com/login",
			"laravel_student": "https://kemetgate.com/student-portal/dashboard",
			"laravel_parent": "https://kemetgate.com/parent-dashboard",
		},
	}


@frappe.whitelist(allow_guest=True)
def get_public_programs(institution: str | None = None) -> list[dict]:
	filters: dict = {}
	if frappe.get_meta("Education Program").has_field("is_active"):
		filters["is_active"] = 1
	elif frappe.get_meta("Education Program").has_field("status"):
		filters["status"] = "Active"
	if institution:
		filters["institution"] = institution
	rows = frappe.get_all(
		"Education Program",
		filters=filters,
		fields=["name", "program_name", "institution", "program_type", "duration_years", "degree_level"],
		limit=200,
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


@frappe.whitelist(allow_guest=True)
def get_public_institution_types() -> list[dict]:
	return _institution_type_catalog()
