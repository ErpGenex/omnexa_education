# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Demo role users — internal desk + website portal roles."""

from __future__ import annotations

DEMO_PASSWORD = "Education@Demo2026"

ROLE_SPECS: list[dict] = [
	{
		"role": "Education Manager",
		"workspace": "Education Executive",
		"title": "📊 Education Executive",
		"default_route": "/app/education-executive-dashboard",
		"email": "executive@demo.education",
		"first_name": "Karim",
		"last_name": "Executive",
		"portal_label_ar": "المدير التنفيذي",
		"portal_label_en": "Executive",
	},
	{
		"role": "Education User",
		"workspace": "Education Admissions",
		"title": "📋 Admissions",
		"default_route": "/app/education-admissions-portal",
		"email": "admissions@demo.education",
		"first_name": "Nadia",
		"last_name": "Admissions",
		"portal_label_ar": "مسؤول القبول",
		"portal_label_en": "Admissions Officer",
	},
	{
		"role": "Education User",
		"workspace": "Education Registrar",
		"title": "📚 Registrar",
		"default_route": "/app/education-registrar-desk",
		"email": "registrar@demo.education",
		"first_name": "Omar",
		"last_name": "Registrar",
		"portal_label_ar": "مسؤول القيد",
		"portal_label_en": "Registrar",
	},
	{
		"role": "Teacher",
		"workspace": "Education Teacher",
		"title": "👩‍🏫 Teacher",
		"default_route": "/app/education-teacher-gradebook",
		"email": "teacher@demo.education",
		"first_name": "Sara",
		"last_name": "Teacher",
		"portal_label_ar": "معلّم",
		"portal_label_en": "Teacher",
	},
	{
		"role": "Education Finance Officer",
		"workspace": "Education Finance",
		"title": "💰 Finance Desk",
		"default_route": "/app/education-finance-desk",
		"email": "finance@demo.education",
		"first_name": "Hana",
		"last_name": "Finance",
		"portal_label_ar": "مسؤول مالي",
		"portal_label_en": "Finance Officer",
	},
	{
		"role": "Education Student Portal",
		"workspace": "Education Student",
		"title": "🎓 Student Portal",
		"default_route": "/app/education-student-portal",
		"email": "student@demo.education",
		"first_name": "Ahmed",
		"last_name": "Student",
		"student_code": "STU-DEMO-001",
		"portal_label_ar": "بوابة الطالب",
		"portal_label_en": "Student Portal",
	},
	{
		"role": "Education Parent Portal",
		"workspace": "Education Parent",
		"title": "👪 Parent Portal",
		"default_route": "/app/education-parent-mobile",
		"email": "parent@demo.education",
		"first_name": "Layla",
		"last_name": "Parent",
		"guardian_email": "parent@demo.education",
		"portal_label_ar": "بوابة ولي الأمر",
		"portal_label_en": "Parent Portal",
	},
	{
		"role": "Education Manager",
		"workspace": "Education Analytics",
		"title": "📈 Analytics",
		"default_route": "/app/education-analytics-dashboard",
		"email": "analytics@demo.education",
		"first_name": "Youssef",
		"last_name": "Analytics",
		"portal_label_ar": "التحليلات",
		"portal_label_en": "Analytics",
	},
]

WEBSITE_PORTAL_SPECS: list[dict] = [
	{
		"id": "apply",
		"label_ar": "التقديم الإلكتروني",
		"label_en": "Online Application",
		"route": "/education/apply",
		"icon": "🌐",
		"method": "omnexa_education.api.education_admissions.get_admissions_portal_config",
	},
	{
		"id": "parent_pwa",
		"label_ar": "بوابة ولي الأمر (PWA)",
		"label_en": "Parent PWA",
		"route": "/app/education-parent-mobile",
		"icon": "📱",
	},
	{
		"id": "student_pwa",
		"label_ar": "بوابة الطالب",
		"label_en": "Student Portal",
		"route": "/app/education-student-portal",
		"icon": "🎓",
	},
]
