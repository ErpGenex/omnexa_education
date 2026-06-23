# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Institution types, academy taxonomy, and demo scale targets."""

from __future__ import annotations

INSTITUTION_TYPES: tuple[str, ...] = (
	"University",
	"Institute",
	"International School",
	"Training Center",
	"Academy",
)

ACADEMY_TYPES: tuple[str, ...] = (
	"Professional Academy",
	"Technical Academy",
	"Business Academy",
	"Tourism Academy",
	"Healthcare Academy",
	"IT Academy",
	"Artificial Intelligence Academy",
	"Media Academy",
	"Sports Academy",
	"Arts Academy",
)

# Full demo scale — 500 students per college/faculty across 4 academic years (125 per year)
DEMO_STUDENTS_PER_COLLEGE = 500
DEMO_ACADEMIC_YEARS = 4
DEMO_STUDENTS_PER_YEAR = DEMO_STUDENTS_PER_COLLEGE // DEMO_ACADEMIC_YEARS

UNIVERSITY_COLLEGES: tuple[dict, ...] = (
	{"code": "ENG", "name": "Faculty of Engineering", "name_ar": "كلية الهندسة"},
	{"code": "BUS", "name": "Faculty of Business", "name_ar": "كلية إدارة الأعمال"},
	{"code": "MED", "name": "Faculty of Medicine", "name_ar": "كلية الطب"},
	{"code": "ART", "name": "Faculty of Arts & Humanities", "name_ar": "كلية الآداب والعلوم الإنسانية"},
)

HE_YEAR_LABELS: tuple[str, ...] = ("Year 1", "Year 2", "Year 3", "Year 4")
HE_YEAR_LABELS_AR: tuple[str, ...] = ("الفرقة الأولى", "الفرقة الثانية", "الفرقة الثالثة", "الفرقة الرابعة")

ACADEMY_LIFECYCLE_PHASES: list[dict] = [
	{"key": "lead", "icon": "📣", "label_ar": "توليد العملاء", "label_en": "Lead Generation", "role_ar": "التسويق", "role_en": "Marketing"},
	{"key": "application", "icon": "📋", "label_ar": "التقديم", "label_en": "Application", "role_ar": "مسؤول القبول", "role_en": "Admissions"},
	{"key": "review", "icon": "🔍", "label_ar": "مراجعة القبول", "label_en": "Admission Review", "role_ar": "لجنة القبول", "role_en": "Review Board"},
	{"key": "enrollment", "icon": "🎓", "label_ar": "التسجيل", "label_en": "Enrollment", "role_ar": "المسجل", "role_en": "Registrar"},
	{"key": "program_reg", "icon": "📚", "label_ar": "تسجيل البرنامج", "label_en": "Program Registration", "role_ar": "منسق أكاديمي", "role_en": "Academic Coordinator"},
	{"key": "delivery", "icon": "💻", "label_ar": "التعلّم", "label_en": "Learning Delivery", "role_ar": "مدرّب", "role_en": "Instructor"},
	{"key": "assessment", "icon": "📝", "label_ar": "التقييم", "label_en": "Assessment", "role_ar": "مدرّب", "role_en": "Instructor"},
	{"key": "certification", "icon": "🏅", "label_ar": "الشهادات", "label_en": "Certification", "role_ar": "ضمان الجودة", "role_en": "QA Officer"},
	{"key": "alumni", "icon": "🤝", "label_ar": "الخريجون والتوظيف", "label_en": "Alumni & Careers", "role_ar": "خدمات مهنية", "role_en": "Career Services"},
]

ACADEMY_QA_METRICS: list[dict] = [
	{"key": "completion_rate", "label_ar": "معدل الإكمال", "label_en": "Completion Rate", "target": 92, "unit": "%"},
	{"key": "certification_rate", "label_ar": "معدل الشهادات", "label_en": "Certification Rate", "target": 88, "unit": "%"},
	{"key": "employment_rate", "label_ar": "معدل التوظيف", "label_en": "Employment Rate", "target": 78, "unit": "%"},
	{"key": "learner_satisfaction", "label_ar": "رضا المتعلمين", "label_en": "Learner Satisfaction", "target": 4.6, "unit": "/5"},
	{"key": "instructor_satisfaction", "label_ar": "رضا المدرّسين", "label_en": "Instructor Satisfaction", "target": 4.5, "unit": "/5"},
	{"key": "industry_alignment", "label_ar": "مواءمة الصناعة", "label_en": "Industry Alignment", "target": 4.7, "unit": "/5"},
]

INSTITUTION_TYPE_IMAGES: dict[str, str] = {
	"International School": "https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&w=800&q=80",
	"University": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=800&q=80",
	"Academy": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=80",
	"Institute": "https://images.unsplash.com/photo-1498243691581-b145c016f997?auto=format&fit=crop&w=800&q=80",
	"Training Center": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=800&q=80",
}

# Demo institutions — one per supported type
INSTITUTION_DEMO_SPECS: list[dict] = [
	{
		"code": "INTSCH",
		"name": "ErpGenEx International School",
		"institution_type": "International School",
		"curriculum_framework": "International Baccalaureate",
		"mode": "k12",
		"website_slug": "international-school",
		"demo_students": DEMO_STUDENTS_PER_COLLEGE,
		"demo_teachers": 40,
		"grade_stages": ["Early Years", "Primary", "Middle", "Secondary"],
	},
	{
		"code": "UNIV",
		"name": "ErpGenEx University",
		"institution_type": "University",
		"curriculum_framework": "Higher Education",
		"mode": "he",
		"website_slug": "university",
		"demo_students": DEMO_STUDENTS_PER_COLLEGE * len(UNIVERSITY_COLLEGES),
		"demo_teachers": 80,
		"colleges": list(UNIVERSITY_COLLEGES),
		"students_per_college": DEMO_STUDENTS_PER_COLLEGE,
		"programs": [
			{"code": "BSC-CS", "name": "BSc Computer Science", "degree_level": "Bachelor", "college": "ENG"},
			{"code": "BSC-EE", "name": "BSc Electrical Engineering", "degree_level": "Bachelor", "college": "ENG"},
			{"code": "MBA", "name": "MBA Business Administration", "degree_level": "Master", "college": "BUS"},
			{"code": "BBA", "name": "BBA Business Administration", "degree_level": "Bachelor", "college": "BUS"},
			{"code": "MBBS", "name": "MBBS Medicine", "degree_level": "Bachelor", "college": "MED"},
			{"code": "BA-ARTS", "name": "BA Arts & Humanities", "degree_level": "Bachelor", "college": "ART"},
		],
	},
	{
		"code": "ACADIT",
		"name": "ErpGenEx IT Academy",
		"institution_type": "Academy",
		"academy_type": "IT Academy",
		"curriculum_framework": "Professional Skills",
		"mode": "academy",
		"website_slug": "it-academy",
		"demo_students": DEMO_STUDENTS_PER_COLLEGE,
		"demo_teachers": 30,
		"programs": [
			{"code": "DIP-WEB", "name": "Web Development Diploma", "degree_level": "Diploma"},
			{"code": "CERT-DATA", "name": "Data Analytics Certificate", "degree_level": "Certificate"},
			{"code": "BOOT-AI", "name": "AI Bootcamp", "degree_level": "Certificate"},
		],
	},
	{
		"code": "INST",
		"name": "ErpGenEx Professional Institute",
		"institution_type": "Institute",
		"curriculum_framework": "National",
		"mode": "mixed",
		"website_slug": "institute",
		"demo_students": DEMO_STUDENTS_PER_COLLEGE,
		"demo_teachers": 25,
		"programs": [
			{"code": "DIP-BUS", "name": "Business Diploma", "degree_level": "Diploma"},
			{"code": "DIP-ACC", "name": "Accounting Diploma", "degree_level": "Diploma"},
		],
	},
	{
		"code": "TRAIN",
		"name": "ErpGenEx Training Center",
		"institution_type": "Training Center",
		"curriculum_framework": "Corporate Training",
		"mode": "training",
		"website_slug": "training-center",
		"demo_students": DEMO_STUDENTS_PER_COLLEGE,
		"demo_teachers": 20,
		"programs": [{"code": "WS-LEAD", "name": "Leadership Workshop Series", "degree_level": "Certificate"}],
	},
]

DEMO_MARKER = "EDU-DEMO"
