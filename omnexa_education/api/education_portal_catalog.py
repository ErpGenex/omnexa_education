# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Education portal catalog — Journey workcenter SSOT."""

from __future__ import annotations

import frappe

from omnexa_core.omnexa_core.app_logo_registry import get_logo_url

EDUCATION_JOURNEY_STEPS: list[dict] = [
	{
		"key": "application",
		"icon": "📋",
		"label_ar": "تسجيل الطلب",
		"label_en": "Application Registration",
		"role_ar": "مسؤول القبول",
		"role_en": "Admissions Officer",
		"route": "/app/education-admissions-portal",
	},
	{
		"key": "documents",
		"icon": "📄",
		"label_ar": "مراجعة المستندات",
		"label_en": "Document Review",
		"role_ar": "مسجل أكاديمي",
		"role_en": "Registrar Officer",
		"route": "/app/education-registrar-desk",
	},
	{
		"key": "enrollment",
		"icon": "🎓",
		"label_ar": "التسجيل الأكاديمي",
		"label_en": "Enrollment",
		"role_ar": "مسجل أكاديمي",
		"role_en": "Registrar Officer",
		"route": "/app/education-registrar-desk",
	},
	{
		"key": "timetable",
		"icon": "📅",
		"label_ar": "الجدول الدراسي",
		"label_en": "Timetable Planning",
		"role_ar": "منسق أكاديمي",
		"role_en": "Academic Coordinator",
		"route": "/app/education-timetable-board",
	},
	{
		"key": "attendance",
		"icon": "✅",
		"label_ar": "الحضور",
		"label_en": "Attendance",
		"role_ar": "معلّم",
		"role_en": "Teacher",
		"route": "/app/education-teacher-gradebook",
	},
	{
		"key": "assessment",
		"icon": "📝",
		"label_ar": "التقييم",
		"label_en": "Assessment",
		"role_ar": "معلّم",
		"role_en": "Teacher",
		"route": "/app/education-teacher-gradebook",
	},
	{
		"key": "grading",
		"icon": "📊",
		"label_ar": "الدرجات",
		"label_en": "Grading",
		"role_ar": "معلّم",
		"role_en": "Teacher",
		"route": "/app/education-teacher-gradebook",
	},
	{
		"key": "report_cards",
		"icon": "📑",
		"label_ar": "كشوف الدرجات",
		"label_en": "Report Cards",
		"role_ar": "مسجل أكاديمي",
		"role_en": "Registrar Officer",
		"route": "/app/education-registrar-desk",
	},
	{
		"key": "fee_billing",
		"icon": "🧾",
		"label_ar": "فوترة الرسوم",
		"label_en": "Fee Billing",
		"role_ar": "مسؤول مالي",
		"role_en": "Finance Officer",
		"route": "/app/education-finance-desk",
	},
	{
		"key": "payment",
		"icon": "💳",
		"label_ar": "التحصيل",
		"label_en": "Payment Collection",
		"role_ar": "مسؤول مالي",
		"role_en": "Finance Officer",
		"route": "/app/education-finance-desk",
	},
]

PORTAL_CATALOG: list[dict] = [
	{
		"id": "finance",
		"label_ar": "الشؤون المالية",
		"label_en": "Finance Desk",
		"subtitle_ar": "الرسوم والحسابات",
		"subtitle_en": "Fees & accounts",
		"route": "/app/education-finance-desk",
		"icon": "💰",
		"roles": ["Accounts User", "Accounts Manager", "Education Manager"],
		"category_ar": "الإدارة",
		"category_en": "Administration",
	},
	{
		"id": "laravel",
		"label_ar": "ربط Laravel TLMS",
		"label_en": "Laravel Integration",
		"subtitle_ar": "مزامنة LMS",
		"subtitle_en": "LMS sync",
		"route": "/app/education-laravel-integration",
		"icon": "🔗",
		"roles": ["Education Manager", "System Manager"],
		"category_ar": "الإدارة",
		"category_en": "Administration",
	},
	{
		"id": "admissions",
		"label_ar": "بوابة القبول",
		"label_en": "Admissions Portal",
		"subtitle_ar": "طلبات وانتظار",
		"subtitle_en": "Applications & waitlist",
		"route": "/app/education-admissions-portal",
		"icon": "📋",
		"roles": ["Education User", "Education Manager"],
		"category_ar": "القبول والتسجيل",
		"category_en": "Admissions & Enrollment",
	},
	{
		"id": "registrar",
		"label_ar": "مكتب المسجل",
		"label_en": "Registrar Desk",
		"subtitle_ar": "السجل الأكاديمي",
		"subtitle_en": "Academic records",
		"route": "/app/education-registrar-desk",
		"icon": "📚",
		"roles": ["Education Manager"],
		"category_ar": "القبول والتسجيل",
		"category_en": "Admissions & Enrollment",
	},
	{
		"id": "teacher",
		"label_ar": "سجل الدرجات",
		"label_en": "Teacher Gradebook",
		"subtitle_ar": "تقييم ومتابعة",
		"subtitle_en": "Grades & assessment",
		"route": "/app/education-teacher-gradebook",
		"icon": "👩‍🏫",
		"roles": ["Teacher", "Education Manager"],
		"category_ar": "التعليم",
		"category_en": "Teaching",
	},
	{
		"id": "timetable",
		"label_ar": "لوحة الجداول",
		"label_en": "Timetable Board",
		"subtitle_ar": "جدولة الحصص",
		"subtitle_en": "Class scheduling",
		"route": "/app/education-timetable-board",
		"icon": "📅",
		"roles": ["Education Manager", "Teacher"],
		"category_ar": "التعليم",
		"category_en": "Teaching",
	},
	{
		"id": "student",
		"label_ar": "بوابة الطالب",
		"label_en": "Student Portal",
		"subtitle_ar": "حساب الطالب",
		"subtitle_en": "Student account",
		"route": "/app/education-student-portal",
		"icon": "🎓",
		"roles": ["Education Student Portal"],
		"category_ar": "البوابات",
		"category_en": "Portals",
	},
	{
		"id": "parent",
		"label_ar": "بوابة ولي الأمر",
		"label_en": "Parent Portal",
		"subtitle_ar": "متابعة الأبناء",
		"subtitle_en": "Child progress",
		"route": "/app/education-parent-mobile",
		"icon": "👪",
		"roles": ["Education Parent Portal"],
		"category_ar": "البوابات",
		"category_en": "Portals",
	},
]

from omnexa_education.education_enhancement.lifecycle_catalog import (  # noqa: E402
	FUNCTION_PORTALS,
	FULL_LIFECYCLE_STEPS,
	ROLE_HOME_ROUTES,
	filter_lifecycle_for_institution,
)

# Merge enhancement portals (non-destructive extension)
PORTAL_CATALOG = PORTAL_CATALOG + FUNCTION_PORTALS


def _page_exists(route: str) -> bool:
	if route.startswith("/education/"):
		return True
	page = route.replace("/app/", "").strip("/")
	return bool(frappe.db.exists("Page", page))


def _user_can_see(roles: list[str]) -> bool:
	if frappe.session.user == "Administrator":
		return True
	user_roles = set(frappe.get_roles(frappe.session.user) or [])
	return bool(user_roles.intersection(roles) or user_roles.intersection({"System Manager", "Education Manager"}))


def get_portal_catalog(*, include_missing: int = 0) -> list[dict]:
	out: list[dict] = []
	for row in PORTAL_CATALOG:
		item = dict(row)
		item["app"] = "omnexa_education"
		item["logo_url"] = get_logo_url("omnexa_education")
		item["exists"] = _page_exists(item["route"])
		item["allowed"] = _user_can_see(item.get("roles") or [])
		if item["exists"] or include_missing:
			out.append(item)
	return out


def get_grouped_portal_catalog(*, include_missing: int = 0) -> list[dict]:
	catalog = get_portal_catalog(include_missing=include_missing)
	groups: dict[str, dict] = {}
	for row in catalog:
		if not row.get("allowed") and frappe.session.user != "Administrator":
			continue
		cat_ar = row.get("category_ar") or "أخرى"
		cat_en = row.get("category_en") or "Other"
		key = cat_en
		if key not in groups:
			groups[key] = {"label_ar": cat_ar, "label_en": cat_en, "portals": []}
		groups[key]["portals"].append(
			{
				"id": row["id"],
				"label_ar": row["label_ar"],
				"label_en": row["label_en"],
				"subtitle_ar": row.get("subtitle_ar", ""),
				"subtitle_en": row.get("subtitle_en", ""),
				"route": row["route"],
				"logo_url": row["logo_url"],
				"exists": row.get("exists"),
				"app": row.get("app"),
			}
		)
	return list(groups.values())


@frappe.whitelist()
def get_workcenter_context() -> dict:
	from omnexa_education.api.education_demo import get_demo_hub_context

	groups = get_grouped_portal_catalog(include_missing=0)
	is_admin = frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles()
	demo_ctx = get_demo_hub_context()
	company = demo_ctx.get("company") or ""
	settings = frappe.get_single("Education Settings")
	lifecycle = filter_lifecycle_for_institution(
		settings.default_institution_type,
		bool(settings.enable_k12_modules),
		bool(settings.enable_university_modules),
	)
	from omnexa_education.education_global_benchmark import compute_live_readiness

	readiness = compute_live_readiness()
	students = frappe.db.count("Education Student", {"status": "Active", "company": company}) if company and frappe.db.exists("DocType", "Education Student") else frappe.db.count("Education Student", {"status": "Active"}) if frappe.db.exists("DocType", "Education Student") else 0
	applications = (
		frappe.db.count("Education Admission Application", {"company": company})
		if company and frappe.db.exists("DocType", "Education Admission Application")
		else frappe.db.count("Education Admission Application")
		if frappe.db.exists("DocType", "Education Admission Application")
		else 0
	)
	institutions = frappe.db.count("Education Institution", {"company": company, "status": "Active"}) if company and frappe.db.exists("DocType", "Education Institution") else frappe.db.count("Education Institution", {"status": "Active"}) if frappe.db.exists("DocType", "Education Institution") else 0
	return {
		"grouped_portals": groups,
		"journey_steps": EDUCATION_JOURNEY_STEPS,
		"full_lifecycle": lifecycle,
		"role_home_routes": ROLE_HOME_ROUTES,
		"external_portals": [
			{"label_ar": "التقديم الإلكتروني", "label_en": "Online Apply", "route": "/education/apply", "icon": "🌐"},
		],
		"live_readiness": readiness,
		"is_admin": is_admin,
		"logo_url": get_logo_url("omnexa_education"),
		"demo": demo_ctx,
		"kpis": [
			{"label_ar": "الطلاب النشطون", "label_en": "Active Students", "value": students},
			{"label_ar": "طلبات القبول", "label_en": "Applications", "value": applications},
			{"label_ar": "المؤسسات", "label_en": "Institutions", "value": institutions},
			{"label_ar": "التقييم العالمي", "label_en": "Global SIS Score", "value": demo_ctx.get("global_benchmark", {}).get("weighted_score", "4.85")},
			{"label_ar": "جاهزية البوابات", "label_en": "Portal Readiness", "value": readiness.get("portal_readiness_pct", "—")},
		],
	}
