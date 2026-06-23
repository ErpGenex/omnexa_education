# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Full education lifecycle routing — enhancement layer (non-destructive SSOT)."""

from __future__ import annotations

# Complete lifecycle: external website → graduation → alumni (Phase 4 + Phases 10–12)
FULL_LIFECYCLE_STEPS: list[dict] = [
	{"key": "lead", "icon": "📣", "label_ar": "عميل محتمل", "label_en": "Lead / Inquiry", "role_ar": "التسويق", "role_en": "Marketing", "route": "/education/apply", "external": True, "modes": ["all"]},
	{"key": "apply", "icon": "🌐", "label_ar": "التقديم الإلكتروني", "label_en": "Online Application", "role_ar": "متقدّم", "role_en": "Applicant", "route": "/education/apply", "external": True, "modes": ["all"]},
	{"key": "review", "icon": "🔍", "label_ar": "مراجعة القبول", "label_en": "Admission Review", "role_ar": "مسؤول القبول", "role_en": "Admissions", "route": "/app/education-admissions-portal", "modes": ["all"]},
	{"key": "assess_adm", "icon": "📝", "label_ar": "اختبار/مقابلة", "label_en": "Placement / Interview", "role_ar": "لجنة القبول", "role_en": "Review Board", "route": "/app/education-admissions-portal", "modes": ["University", "Institute", "Academy", "International School"]},
	{"key": "accept", "icon": "✅", "label_ar": "القبول", "label_en": "Acceptance", "role_ar": "مسؤول القبول", "role_en": "Admissions", "route": "/app/education-admissions-portal", "modes": ["all"]},
	{"key": "enroll", "icon": "🎓", "label_ar": "التسجيل", "label_en": "Enrollment", "role_ar": "المسجل", "role_en": "Registrar", "route": "/app/education-registrar-desk", "modes": ["all"]},
	{"key": "finance_reg", "icon": "💳", "label_ar": "التسجيل المالي", "label_en": "Financial Registration", "role_ar": "مسؤول مالي", "role_en": "Finance", "route": "/app/education-finance-desk", "modes": ["all"]},
	{"key": "orient", "icon": "🧭", "label_ar": "التوجيه", "label_en": "Orientation", "role_ar": "شؤون الطلاب", "role_en": "Student Affairs", "route": "/app/education-registrar-desk", "modes": ["University", "International School", "Academy"]},
	{"key": "plan", "icon": "📐", "label_ar": "التخطيط الأكademic", "label_en": "Academic Planning", "role_ar": "منسق أكاديمي", "role_en": "Coordinator", "route": "/app/education-registrar-desk", "modes": ["University", "Institute", "Academy"]},
	{"key": "schedule", "icon": "📅", "label_ar": "الجدول", "label_en": "Scheduling", "role_ar": "منسق", "role_en": "Scheduler", "route": "/app/education-timetable-board", "modes": ["all"]},
	{"key": "attend", "icon": "✅", "label_ar": "الحضور", "label_en": "Attendance", "role_ar": "معلّم", "role_en": "Teacher", "route": "/app/education-teacher-gradebook", "modes": ["all"]},
	{"key": "assess", "icon": "📊", "label_ar": "التقييم", "label_en": "Assessment", "role_ar": "معلّم", "role_en": "Teacher", "route": "/app/education-teacher-gradebook", "modes": ["all"]},
	{"key": "exam", "icon": "📋", "label_ar": "الامتحانات", "label_en": "Examinations", "role_ar": "معلّم", "role_en": "Teacher", "route": "/app/education-teacher-gradebook", "modes": ["all"]},
	{"key": "results", "icon": "📑", "label_ar": "النتائج", "label_en": "Results", "role_ar": "معلّم", "role_en": "Teacher", "route": "/app/education-teacher-gradebook", "modes": ["all"]},
	{"key": "advise", "icon": "🎯", "label_ar": "الإرشاد الأكademic", "label_en": "Advising", "role_ar": "مرشد", "role_en": "Advisor", "route": "/app/education-analytics-dashboard", "modes": ["University", "Institute"]},
	{"key": "warning", "icon": "⚠️", "label_ar": "إنذار أكademic", "label_en": "Academic Warning", "role_ar": "مرشد", "role_en": "Advisor", "route": "/app/education-analytics-dashboard", "modes": ["University", "International School"]},
	{"key": "grad_audit", "icon": "🎓", "label_ar": "مراجعة التخرج", "label_en": "Graduation Audit", "role_ar": "المسجل", "role_en": "Registrar", "route": "/app/education-graduation-desk", "modes": ["all"]},
	{"key": "grad_approve", "icon": "🏅", "label_ar": "اعتماد التخرج", "label_en": "Graduation Approval", "role_ar": "المسجل", "role_en": "Registrar", "route": "/app/education-graduation-desk", "modes": ["all"]},
	{"key": "cert", "icon": "📜", "label_ar": "الشهادات", "label_en": "Certificates", "role_ar": "المسجل", "role_en": "Registrar", "route": "/app/education-graduation-desk", "modes": ["all"]},
	{"key": "alumni", "icon": "🤝", "label_ar": "الخريجون", "label_en": "Alumni & Careers", "role_ar": "خدمات مهنية", "role_en": "Career Services", "route": "/app/education-alumni-desk", "modes": ["all"]},
	{"key": "qa", "icon": "⭐", "label_ar": "ضمان الجودة", "label_en": "Quality Assurance", "role_ar": "ضمان الجودة", "role_en": "QA Officer", "route": "/app/education-qa-desk", "modes": ["all"]},
	{"key": "accredit", "icon": "🏛️", "label_ar": "الاعتماد", "label_en": "Accreditation", "role_ar": "الاعتماد", "role_en": "Accreditation", "route": "/app/education-qa-desk", "modes": ["University", "Institute", "Academy"]},
]

FUNCTION_PORTALS: list[dict] = [
	{"id": "executive", "label_ar": "المدير التنفيذي", "label_en": "Executive", "subtitle_ar": "KPIs استراتيجية", "subtitle_en": "Strategic KPIs", "route": "/app/education-executive-dashboard", "icon": "📊", "roles": ["Education Manager", "Company Admin"], "category_ar": "الإدارة", "category_en": "Administration", "function": "admin"},
	{"id": "analytics", "label_ar": "التحليلات", "label_en": "Analytics", "subtitle_ar": "تنبؤات ومخاطر", "subtitle_en": "Predictive analytics", "route": "/app/education-analytics-dashboard", "icon": "📈", "roles": ["Education Manager", "Education User"], "category_ar": "الجودة", "category_en": "Quality", "function": "qa"},
	{"id": "qa", "label_ar": "ضمان الجودة", "label_en": "QA Desk", "subtitle_ar": "مؤشرات · اعتماد · OBE", "subtitle_en": "Indicators · accreditation · OBE", "route": "/app/education-qa-desk", "icon": "⭐", "roles": ["Education Manager", "Education User"], "category_ar": "الجودة", "category_en": "Quality", "function": "qa"},
	{"id": "graduation", "label_ar": "التخرج", "label_en": "Graduation Desk", "subtitle_ar": "مراجعة · شهادات", "subtitle_en": "Audit · certificates", "route": "/app/education-graduation-desk", "icon": "🎓", "roles": ["Education Manager", "Education User"], "category_ar": "القبول والتسجيل", "category_en": "Admissions & Enrollment", "function": "registrar"},
	{"id": "alumni", "label_ar": "الخريجون", "label_en": "Alumni Desk", "subtitle_ar": "توظيف · شبكة", "subtitle_en": "Careers · network", "route": "/app/education-alumni-desk", "icon": "🤝", "roles": ["Education Manager", "Education User"], "category_ar": "الخريجون", "category_en": "Alumni", "function": "alumni"},
]

ROLE_HOME_ROUTES: dict[str, str] = {
	"Education Manager": "/app/education-executive-dashboard",
	"Education User": "/app/education-admissions-portal",
	"Education Finance Officer": "/app/education-finance-desk",
	"Education Student Portal": "/app/education-student-portal",
	"Education Parent Portal": "/app/education-parent-mobile",
	"Teacher": "/app/education-teacher-gradebook",
	"Accounts User": "/app/education-finance-desk",
	"Accounts Manager": "/app/education-finance-desk",
}


def filter_lifecycle_for_institution(institution_type: str | None, enable_k12: bool = True, enable_he: bool = True) -> list[dict]:
	itype = institution_type or "School"
	steps = []
	for step in FULL_LIFECYCLE_STEPS:
		modes = step.get("modes") or ["all"]
		if "all" not in modes and itype not in modes:
			# International School treated as K12 for filtering
			if itype == "International School" and "International School" in modes:
				pass
			elif itype == "School" and "International School" in modes:
				pass
			else:
				continue
		if not enable_k12 and itype in ("School", "International School") and step["key"] in ("orient",):
			continue
		if not enable_he and itype in ("University", "Institute") and step["key"] in ("plan", "advise"):
			continue
		steps.append(step)
	return steps
