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

PROGRAMS_PER_UNIVERSITY_COLLEGE = 10
PROGRAMS_PER_DEPARTMENT = 5

_UNIVERSITY_TRACKS = (
	"Computer Science",
	"Electrical Engineering",
	"Mechanical Engineering",
	"Civil Engineering",
	"Business Administration",
	"Economics",
	"Medicine",
	"Pharmacy",
	"Law",
	"Architecture",
)
_DEGREE_CYCLE = ("Bachelor", "Bachelor", "Master", "Bachelor", "Diploma", "Bachelor", "Master", "Bachelor", "Doctorate", "Professional")
_DEGREE_PREFIX = {
	"Bachelor": "BSc",
	"Master": "MSc",
	"Doctorate": "PhD",
	"Diploma": "Dip",
	"Professional": "Prof",
	"Certificate": "Cert",
}


def programs_for_university_college(college: dict, count: int = PROGRAMS_PER_UNIVERSITY_COLLEGE) -> list[dict]:
	programs: list[dict] = []
	for i in range(count):
		track = _UNIVERSITY_TRACKS[i % len(_UNIVERSITY_TRACKS)]
		level = _DEGREE_CYCLE[i % len(_DEGREE_CYCLE)]
		prefix = _DEGREE_PREFIX.get(level, "Prog")
		programs.append(
			{
				"code": f"{college['code']}-P{i + 1:02d}",
				"name": f"{prefix} {track}",
				"degree_level": level,
				"college": college["code"],
			}
		)
	return programs


def programs_for_department(inst_code: str, department: dict, count: int = PROGRAMS_PER_DEPARTMENT) -> list[dict]:
	programs: list[dict] = []
	levels = ("Certificate", "Diploma", "Bachelor", "Certificate", "Diploma")
	for i in range(count):
		level = levels[i % len(levels)]
		programs.append(
			{
				"code": f"{inst_code}-{department['code']}-P{i + 1}",
				"name": f"{department['name']} — Program {i + 1}",
				"degree_level": level,
				"department": department["code"],
			}
		)
	return programs


def build_university_program_catalog(colleges: tuple[dict, ...] | list[dict] | None = None) -> list[dict]:
	colleges = colleges or UNIVERSITY_COLLEGES
	return [prog for college in colleges for prog in programs_for_university_college(college)]


def build_department_program_catalog(inst_code: str, departments: list[dict]) -> list[dict]:
	return [prog for dept in departments for prog in programs_for_department(inst_code, dept)]


def get_demo_program_catalog() -> list[dict]:
	"""Public website fallback when DB has no seeded programs yet."""
	rows: list[dict] = []
	for spec in INSTITUTION_DEMO_SPECS:
		inst_label = spec.get("name") or spec["code"]
		inst_type = spec.get("institution_type", "")
		for prog in spec.get("programs") or []:
			dept_label = prog.get("department") or prog.get("college") or ""
			rows.append(
				{
					"name": f"{DEMO_MARKER}-{prog['code']}",
					"program_name": prog["name"],
					"institution": inst_label,
					"institution_name": inst_label,
					"institution_type": inst_type,
					"degree_level": prog.get("degree_level", "Certificate"),
					"program_type": inst_type,
					"department_name": str(dept_label),
					"duration_years": 4 if prog.get("degree_level") in ("Bachelor", "Master", "Doctorate") else 2,
				}
			)
	return rows


INTSCH_DEPARTMENTS: list[dict] = [
	{"code": "EY", "name": "Early Years"},
	{"code": "PRI", "name": "Primary"},
	{"code": "MID", "name": "Middle School"},
	{"code": "SEC", "name": "Secondary"},
]

ACADEMY_DEPARTMENTS: list[dict] = [
	{"code": "SW", "name": "Software Engineering"},
	{"code": "DATA", "name": "Data & AI"},
	{"code": "CLOUD", "name": "Cloud & DevOps"},
	{"code": "SEC", "name": "Cybersecurity"},
	{"code": "PM", "name": "IT Project Management"},
]

INSTITUTE_DEPARTMENTS: list[dict] = [
	{"code": "BUS", "name": "Business Studies"},
	{"code": "ACC", "name": "Accounting"},
	{"code": "HR", "name": "Human Resources"},
	{"code": "MKT", "name": "Marketing"},
]

TRAINING_DEPARTMENTS: list[dict] = [
	{"code": "LEAD", "name": "Leadership"},
	{"code": "TECH", "name": "Technical Skills"},
	{"code": "SOFT", "name": "Soft Skills"},
]

DEMO_MARKER = "EDU-DEMO"

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
		"departments": INTSCH_DEPARTMENTS,
		"programs": build_department_program_catalog("INTSCH", INTSCH_DEPARTMENTS),
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
		"programs": build_university_program_catalog(),
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
		"departments": ACADEMY_DEPARTMENTS,
		"programs": build_department_program_catalog("ACADIT", ACADEMY_DEPARTMENTS),
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
		"departments": INSTITUTE_DEPARTMENTS,
		"programs": build_department_program_catalog("INST", INSTITUTE_DEPARTMENTS),
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
		"departments": TRAINING_DEPARTMENTS,
		"programs": build_department_program_catalog("TRAIN", TRAINING_DEPARTMENTS),
	},
]

