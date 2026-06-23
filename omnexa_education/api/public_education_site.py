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

COLLEGES_CATALOG = [
	{"key": "medicine", "name_ar": "كلية الطب", "name_en": "Faculty of Medicine", "programs": 10, "image": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=800&q=80"},
	{"key": "engineering", "name_ar": "كلية الهندسة", "name_en": "Faculty of Engineering", "programs": 10, "image": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80"},
	{"key": "ai", "name_ar": "كلية الذكاء الاصطناعي", "name_en": "Faculty of AI", "programs": 10, "image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=800&q=80"},
	{"key": "business", "name_ar": "كلية الأعمال", "name_en": "Faculty of Business", "programs": 10, "image": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=800&q=80"},
	{"key": "cs", "name_ar": "كلية الحاسبات", "name_en": "Faculty of Computing", "programs": 10, "image": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=800&q=80"},
	{"key": "science", "name_ar": "كلية العلوم", "name_en": "Faculty of Science", "programs": 10, "image": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=800&q=80"},
	{"key": "law", "name_ar": "كلية القانون", "name_en": "Faculty of Law", "programs": 10, "image": "https://images.unsplash.com/photo-1589829545855-d10d557cf95f?auto=format&fit=crop&w=800&q=80"},
	{"key": "media", "name_ar": "كلية الإعلام", "name_en": "Faculty of Media", "programs": 10, "image": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80"},
	{"key": "intschool", "name_ar": "المدارس الدولية", "name_en": "International Schools", "programs": 20, "image": "https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&w=800&q=80"},
	{"key": "academy", "name_ar": "الأكاديمية المهنية", "name_en": "Professional Academy", "programs": 25, "image": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=80"},
]

NEWS_ITEMS = [
	{"tag_ar": "إعلان", "tag_en": "Announcement", "title_ar": "فتح باب القبول للفصل الجديد", "title_en": "New Semester Admissions Open", "date": "2026-06-01", "image": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=600&q=70"},
	{"tag_ar": "خبر", "tag_en": "News", "title_ar": "اعتماد دولي جديد للبرامج الأكاديمية", "title_en": "New International Accreditation", "date": "2026-05-15", "image": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=600&q=70"},
	{"tag_ar": "فعالية", "tag_en": "Event", "title_ar": "معرض التوظيف السنوي 2026", "title_en": "Annual Career Fair 2026", "date": "2026-04-20", "image": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600&q=70"},
]

SCHOLARSHIPS = [
	{"name_ar": "منح التفوق الأكاديمي", "name_en": "Merit Scholarships", "desc_ar": "للطلاب المتفوقين أكاديمياً", "desc_en": "For academically outstanding students"},
	{"name_ar": "منح الرياضة", "name_en": "Sports Scholarships", "desc_ar": "دعم المواهب الرياضية", "desc_en": "Supporting athletic talent"},
	{"name_ar": "منح الطلاب الدوليين", "name_en": "International Scholarships", "desc_ar": "برامج خاصة للطلاب الوافدين", "desc_en": "Programs for international students"},
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
		"brand_name_ar": "Omnexa Education",
		"brand_name_en": "Omnexa Education",
		"tagline_ar": "ابنِ مستقبلك مع مؤسسة تعليمية عالمية",
		"tagline_en": "Build your future with a world-class education institution",
		"hero_text_ar": "القبول والتسجيل والتعلم والخدمات الطلابية في منصة واحدة متكاملة",
		"hero_text_en": "Admissions, enrollment, learning, and student services in one integrated platform",
		"hero_image": DEFAULT_HERO,
		"hero_video_poster": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=1920&q=85",
		"logo": _public_url("/assets/omnexa_education/education.svg"),
		"primary_color": "#003366",
		"secondary_color": "#0A5FA8",
		"accent_color": "#00B4D8",
		"gold_color": "#D4AF37",
		"institution": institution,
		"selected_institution": selected.as_dict() if selected else None,
		"institutions": institutions,
		"institution_types": type_catalog,
		"colleges": COLLEGES_CATALOG,
		"news": NEWS_ITEMS,
		"scholarships": SCHOLARSHIPS,
		"lifecycle_phases": ACADEMY_LIFECYCLE_PHASES,
		"gallery": CAMPUS_GALLERY,
		"hero_stats": {
			"students": max(student_count, 100000),
			"programs": max(program_count, 500),
			"colleges": max(len(COLLEGES_CATALOG), 25),
			"countries": 50,
		},
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
			"student_portal": "/app/education-student-portal",
			"parent_portal": "/app/education-parent-mobile",
			"faculty_portal": "/app/education-teacher-gradebook",
			"laravel_portal": "https://kemetgate.com",
			"laravel_login": "https://kemetgate.com/login",
			"laravel_student": "https://kemetgate.com/student-portal/dashboard",
			"laravel_parent": "https://kemetgate.com/parent-dashboard",
		},
	}


@frappe.whitelist(allow_guest=True)
def get_public_programs(institution: str | None = None) -> list[dict]:
	from omnexa_education.education_demo.institution_specs import get_demo_program_catalog

	meta = frappe.get_meta("Education Program")
	fields = ["name", "program_name", "institution", "degree_level"]
	for fieldname in ("program_type", "duration_years", "department", "total_credits"):
		if meta.has_field(fieldname):
			fields.append(fieldname)

	filters: dict = {}
	if meta.has_field("is_active"):
		filters["is_active"] = 1
	elif meta.has_field("status"):
		filters["status"] = "Active"
	if institution:
		filters["institution"] = institution

	rows = frappe.get_all(
		"Education Program",
		filters=filters,
		fields=fields,
		limit=500,
		order_by="program_name asc",
		ignore_permissions=True,
	)
	if not rows:
		return get_demo_program_catalog()

	for row in rows:
		inst = frappe.db.get_value(
			"Education Institution",
			row.institution,
			["institution_name", "institution_type"],
			as_dict=True,
		)
		if inst:
			row["institution_name"] = inst.institution_name
			row["institution_type"] = inst.institution_type
			row["program_type"] = row.get("program_type") or inst.institution_type
		if row.get("department"):
			row["department_name"] = frappe.db.get_value("Education Department", row.department, "department_name")
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
