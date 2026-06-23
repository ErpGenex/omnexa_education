# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Seed multi-institution education demo data + role users."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, getdate, nowdate, today

from omnexa_education.education_demo.institution_specs import (
	DEMO_MARKER,
	INSTITUTION_DEMO_SPECS,
)
from omnexa_education.education_demo.role_specs import DEMO_PASSWORD, ROLE_SPECS


def _resolve_company_branch(company: str | None = None, branch: str | None = None) -> tuple[str, str]:
	company = company or frappe.defaults.get_user_default("Company") or ""
	branch = branch or frappe.defaults.get_user_default("Branch") or ""
	if not company:
		company = frappe.db.get_value("Company", {}, "name", order_by="creation asc") or ""
	if company and not branch:
		branch = frappe.db.get_value("Branch", {"company": company}, "name", order_by="creation asc") or ""
	if not branch:
		branch = frappe.db.get_value("Branch", {}, "name", order_by="creation asc") or ""
	if not company:
		frappe.throw(_("No Company found. Set Global Defaults → Company or pass company=."))
	if not branch:
		frappe.throw(_("No Branch found for {0}.").format(company))
	return company, branch


def _get_or_insert(doctype: str, filters: dict, doc_dict: dict) -> str:
	existing = frappe.db.get_value(doctype, filters, "name")
	if existing:
		return existing
	doc = frappe.get_doc({"doctype": doctype, **doc_dict})
	doc.insert(ignore_permissions=True)
	return doc.name


def _ensure_curriculum(company: str, framework: str) -> str:
	fw_map = {
		"International Baccalaureate": "IB",
		"Higher Education": "Custom",
		"Professional Skills": "Custom",
		"National": "National",
		"Corporate Training": "Custom",
	}
	fw = fw_map.get(framework, "Custom")
	code = f"{DEMO_MARKER}-{fw}"
	return _get_or_insert(
		"Education Curriculum",
		{"company": company, "curriculum_code": code},
		{
			"curriculum_code": code,
			"curriculum_name": f"{framework} ({DEMO_MARKER})",
			"company": company,
			"framework": fw,
			"grading_scheme": "Percentage",
			"status": "Active",
		},
	)


def _ensure_institution(company: str, spec: dict, curriculum: str) -> str:
	inst_type = spec["institution_type"]
	allowed = frappe.get_meta("Education Institution").get_field("institution_type").options.split("\n")
	db_type = inst_type if inst_type in allowed else "School"
	payload = {
		"institution_code": f"{DEMO_MARKER}-{spec['code']}",
		"institution_name": spec["name"],
		"company": company,
		"institution_type": db_type,
		"curriculum_default": curriculum,
		"status": "Active",
		"language": "ar-EG",
		"timezone": "Africa/Cairo",
		"website": f"https://demo.erpgenex.education/{spec.get('website_slug', 'school')}",
		"regulatory_code": DEMO_MARKER,
	}
	if frappe.get_meta("Education Institution").has_field("institution_subtype"):
		payload["institution_subtype"] = inst_type
	if frappe.get_meta("Education Institution").has_field("academy_type") and spec.get("academy_type"):
		payload["academy_type"] = spec["academy_type"]
	return _get_or_insert(
		"Education Institution",
		{"company": company, "institution_code": payload["institution_code"]},
		payload,
	)


def _ensure_campus(company: str, branch: str, institution: str, code: str) -> str:
	return _get_or_insert(
		"Education Campus",
		{"company": company, "institution": institution, "campus_code": code},
		{
			"campus_code": code,
			"campus_name": "Main Campus",
			"company": company,
			"branch": branch,
			"institution": institution,
			"campus_type": "Main",
			"status": "Active",
		},
	)


def _ensure_academic_year(company: str, institution: str, curriculum: str, suffix: str = "AY") -> str:
	code = f"{DEMO_MARKER}-{suffix}"
	start = getdate(today())
	return _get_or_insert(
		"Education Academic Year",
		{"company": company, "institution": institution, "year_code": code},
		{
			"year_code": code,
			"title": f"Demo AY {start.year} ({suffix})",
			"company": company,
			"institution": institution,
			"curriculum": curriculum,
			"start_date": start,
			"end_date": add_days(start, 300),
			"status": "Active",
		},
	)


def _ensure_grade_level(company: str, institution: str, curriculum: str, stage: str, seq: int) -> str:
	code = f"{DEMO_MARKER}-G{seq}"
	return _get_or_insert(
		"Education Grade Level",
		{"company": company, "institution": institution, "grade_code": code},
		{
			"grade_code": code,
			"grade_name": f"{stage} {seq}",
			"company": company,
			"institution": institution,
			"curriculum": curriculum,
			"stage": stage,
			"sequence": seq,
			"status": "Active",
		},
	)


def _ensure_section(company: str, branch: str, campus: str, year: str, grade: str, suffix: str) -> str:
	code = f"{DEMO_MARKER}-{suffix}"
	return _get_or_insert(
		"Education Section",
		{"company": company, "section_code": code},
		{
			"section_code": code,
			"section_name": f"Section {suffix}",
			"company": company,
			"branch": branch,
			"campus": campus,
			"academic_year": year,
			"grade_level": grade,
			"capacity": 30,
			"status": "Active",
		},
	)


def _ensure_program(company: str, branch: str, institution: str, prog: dict, department: str | None = None) -> str:
	payload = {
		"program_code": f"{DEMO_MARKER}-{prog['code']}",
		"program_name": prog["name"],
		"company": company,
		"branch": branch,
		"institution": institution,
		"degree_level": prog.get("degree_level", "Certificate"),
		"is_active": 1,
	}
	if department and frappe.get_meta("Education Program").has_field("department"):
		payload["department"] = department
	return _get_or_insert(
		"Education Program",
		{"company": company, "program_code": payload["program_code"]},
		payload,
	)


def _ensure_teacher(company: str, branch: str, campus: str, code: str, name: str) -> str:
	return _get_or_insert(
		"Education Teacher",
		{"company": company, "teacher_code": f"{DEMO_MARKER}-{code}"},
		{
			"teacher_code": f"{DEMO_MARKER}-{code}",
			"teacher_name": name,
			"company": company,
			"branch": branch,
			"campus": campus,
			"status": "Active",
		},
	)


def _ensure_student(
	company: str,
	branch: str,
	institution: str,
	campus: str,
	code: str,
	name: str,
	*,
	grade_level: str | None = None,
	section: str | None = None,
	guardian_email: str | None = None,
	user: str | None = None,
) -> str:
	payload = {
		"student_code": f"{DEMO_MARKER}-{code}",
		"student_name": name,
		"company": company,
		"branch": branch,
		"institution": institution,
		"campus": campus,
		"status": "Active",
		"account_access_status": "Active",
	}
	if grade_level:
		payload["grade_level"] = grade_level
	if section:
		payload["section"] = section
	if guardian_email:
		payload["guardian_email"] = guardian_email
		payload["guardian_name"] = "Demo Guardian"
	if user:
		payload["user"] = user
	return _get_or_insert(
		"Education Student",
		{"company": company, "student_code": payload["student_code"]},
		payload,
	)


def _ensure_application(company: str, branch: str, institution: str, year: str, applicant: str, grade: str | None = None) -> str:
	return _get_or_insert(
		"Education Admission Application",
		{"company": company, "institution": institution, "applicant_name": applicant},
		{
			"applicant_name": applicant,
			"institution": institution,
			"company": company,
			"branch": branch,
			"academic_year": year,
			"grade_level": grade,
			"application_date": nowdate(),
			"status": "Submitted",
			"guardian_name": "Demo Applicant Guardian",
			"guardian_email": f"applicant-{frappe.generate_hash(length=4)}@demo.education",
		},
	)


def _ensure_subject(company: str, institution: str, curriculum: str, code: str, name: str) -> str:
	payload = {
		"subject_code": f"{DEMO_MARKER}-{code}",
		"subject_name": name,
		"company": company,
		"status": "Active",
	}
	if frappe.get_meta("Education Subject").has_field("curriculum"):
		payload["curriculum"] = curriculum
	if frappe.get_meta("Education Subject").has_field("institution"):
		payload["institution"] = institution
	return _get_or_insert(
		"Education Subject",
		{"company": company, "subject_code": payload["subject_code"]},
		payload,
	)


def _ensure_course(
	company: str,
	branch: str,
	institution: str,
	subject: str,
	code: str,
	title: str,
	*,
	program: str | None = None,
	credit_hours: float = 3,
) -> str:
	return _get_or_insert(
		"Education Course",
		{"course_code": f"{DEMO_MARKER}-{code}"},
		{
			"course_code": f"{DEMO_MARKER}-{code}",
			"course_title": title,
			"company": company,
			"branch": branch,
			"institution": institution,
			"subject": subject,
			"program": program,
			"credit_hours": credit_hours,
			"is_active": 1,
		},
	)


def _seed_demo_assessments(
	company: str,
	branch: str,
	institution: str,
	year: str,
	student_ids: list[str],
	*,
	subject: str,
	course: str | None = None,
	scores: tuple[float, ...] = (88, 76, 92, 65, 81),
) -> int:
	if not student_ids or not frappe.db.exists("DocType", "Education Assessment Plan"):
		return 0
	created = 0
	for idx, student in enumerate(student_ids[: len(scores)]):
		plan_name = f"{DEMO_MARKER}-{institution[-6:]}-PLN-{idx+1}"
		plan = _get_or_insert(
			"Education Assessment Plan",
			{"company": company, "plan_name": plan_name},
			{
				"plan_name": plan_name,
				"institution": institution,
				"company": company,
				"branch": branch,
				"academic_year": year,
				"subject": subject,
				"course": course,
				"assessment_type": "Exam",
				"max_score": 100,
			},
		)
		score = scores[idx % len(scores)]
		result_filters = {"student": student, "assessment_plan": plan}
		payload = {
			"student": student,
			"assessment_plan": plan,
			"institution": institution,
			"company": company,
			"branch": branch,
			"score": score,
			"max_score": 100,
			"subject": subject,
			"course": course,
			"academic_year": year,
			"status": "Published",
			"grade_letter": "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D",
			"gpa_points": round(score / 25, 2),
		}
		meta = frappe.get_meta("Education Assessment Result")
		payload = {k: v for k, v in payload.items() if meta.has_field(k)}
		_get_or_insert("Education Assessment Result", result_filters, payload)
		created += 1
	return created


def _seed_institution(company: str, branch: str, spec: dict) -> dict:
	from omnexa_education.education_demo.education_demo_bulk import (
		bulk_seed_students,
		seed_college_students,
		seed_lifecycle_pipeline,
		_ensure_department,
		_ensure_he_year_levels,
	)

	curriculum = _ensure_curriculum(company, spec["curriculum_framework"])
	institution = _ensure_institution(company, spec, curriculum)
	campus = _ensure_campus(company, branch, institution, f"{spec['code']}-MAIN")
	year = _ensure_academic_year(company, institution, curriculum, spec["code"])
	stats = {"institution": institution, "students": 0, "teachers": 0, "applications": 0, "programs": 0, "courses": 0}
	student_ids: list[str] = []

	for i in range(spec.get("demo_teachers", 2)):
		_ensure_teacher(company, branch, campus, f"{spec['code']}-T{i+1}", f"Instructor {spec['code']}-{i+1}")
		stats["teachers"] += 1

	mode = spec.get("mode", "k12")
	if mode == "k12":
		grades = []
		dept_map: dict[str, str] = {}
		for idx, stage in enumerate(spec.get("grade_stages") or ["Primary"], start=1):
			grades.append(_ensure_grade_level(company, institution, curriculum, stage, idx))
		for dept in spec.get("departments") or []:
			dept_map[dept["code"]] = _ensure_department(
				company, branch, campus, f"{spec['code']}-{dept['code']}", dept["name"]
			)
		for prog in spec.get("programs") or []:
			dept = dept_map.get(prog.get("department", ""))
			_ensure_program(company, branch, institution, prog, department=dept)
			stats["programs"] += 1
		section = _ensure_section(company, branch, campus, year, grades[0], f"{spec['code']}-A")
		subject = _ensure_subject(company, institution, curriculum, f"{spec['code']}-MATH", "Mathematics")
		course = _ensure_course(
			company, branch, institution, subject, f"{spec['code']}-MATH101", "Mathematics 101", credit_hours=1
		)
		stats["courses"] += 1
		created, student_ids = bulk_seed_students(
			company,
			branch,
			institution,
			campus,
			spec["code"],
			spec.get("demo_students", 500),
			grade_levels=grades,
			section=section,
		)
		stats["students"] += created
		_seed_demo_assessments(company, branch, institution, year, student_ids, subject=subject, course=course)
	else:
		program_ids = []
		college_map: dict[str, str] = {}
		for college in spec.get("colleges") or []:
			college_map[college["code"]] = _ensure_department(
				company, branch, campus, f"{spec['code']}-{college['code']}", college["name"]
			)
		for dept in spec.get("departments") or []:
			college_map[dept["code"]] = _ensure_department(
				company, branch, campus, f"{spec['code']}-{dept['code']}", dept["name"]
			)
		year_levels = _ensure_he_year_levels(company, institution, curriculum, spec["code"]) if mode == "he" else []

		for prog in spec.get("programs") or []:
			prog_payload = {**prog}
			dept = college_map.get(prog.get("college", "")) or college_map.get(prog.get("department", ""))
			program_ids.append(_ensure_program(company, branch, institution, prog_payload, department=dept))
			stats["programs"] += 1

		subject = _ensure_subject(company, institution, curriculum, f"{spec['code']}-CORE", "Core Studies")
		course = _ensure_course(
			company,
			branch,
			institution,
			subject,
			f"{spec['code']}-CORE101",
			f"{spec['name']} Core",
			program=program_ids[0] if program_ids else None,
			credit_hours=3,
		)
		stats["courses"] += 1

		if spec.get("colleges") and year_levels:
			for college in spec["colleges"]:
				created, samples = seed_college_students(
					company, branch, institution, campus, spec["code"], college, year_levels
				)
				stats["students"] += created
				student_ids.extend(samples[:10])
		else:
			created, student_ids = bulk_seed_students(
				company,
				branch,
				institution,
				campus,
				spec["code"],
				spec.get("demo_students", 500),
				grade_levels=year_levels or None,
			)
			stats["students"] += created

		_seed_demo_assessments(company, branch, institution, year, student_ids, subject=subject, course=course)

	lifecycle = seed_lifecycle_pipeline(company, branch, institution, year, spec["code"], applications=40)
	stats["applications"] = lifecycle.get("applications", 0)

	return stats


def _ensure_demo_user(spec: dict, company: str, branch: str) -> str:
	email = spec["email"]
	role = spec["role"]
	if frappe.db.exists("User", email):
		user = frappe.get_doc("User", email)
	else:
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": spec["first_name"],
				"last_name": spec["last_name"],
				"send_welcome_email": 0,
				"user_type": "System User",
			}
		)
		user.insert(ignore_permissions=True)
	user.enabled = 1
	user.new_password = DEMO_PASSWORD
	roles = {r.role for r in user.roles}
	if role not in roles:
		user.append("roles", {"role": role})
	if spec.get("default_route"):
		user.default_home_page = spec["default_route"]
	if role in ("Education Student Portal", "Education Parent Portal"):
		if frappe.get_meta("User").has_field("default_app"):
			user.default_app = "omnexa_education"
	user.save(ignore_permissions=True)
	frappe.defaults.set_user_default("Company", company, email)
	frappe.defaults.set_user_default("Branch", branch, email)
	if role in ("Education Student Portal", "Education Parent Portal"):
		from omnexa_education.api.portal_access import ensure_user_branch_access

		ensure_user_branch_access(email, company, branch)
	return email


def _link_portal_users(company: str, branch: str) -> None:
	"""Link student/parent demo users to Education Student records."""
	intsch = frappe.db.get_value(
		"Education Institution",
		{"company": company, "institution_code": f"{DEMO_MARKER}-INTSCH"},
		"name",
	)
	if not intsch:
		return
	campus = frappe.db.get_value("Education Campus", {"institution": intsch}, "name")
	grade = frappe.db.get_value("Education Grade Level", {"institution": intsch}, "name")
	section = frappe.db.get_value("Education Section", {"company": company, "section_code": f"{DEMO_MARKER}-INTSCH-A"}, "name")

	student_user = "student@demo.education"
	if frappe.db.exists("User", student_user):
		_ensure_student(
			company,
			branch,
			intsch,
			campus or "",
			"STU-DEMO-001",
			"Ahmed Demo Student",
			grade_level=grade,
			section=section,
			user=student_user,
		)

	parent_email = "parent@demo.education"
	child = frappe.db.get_value(
		"Education Student",
		{"company": company, "institution": intsch, "student_code": f"{DEMO_MARKER}-INTSCH-S01"},
		"name",
	)
	if not child:
		child = frappe.db.sql(
			"""
			SELECT name FROM `tabEducation Student`
			WHERE company = %s AND institution = %s AND status = 'Active'
			ORDER BY creation ASC LIMIT 1
			""",
			(company, intsch),
		)
		child = child[0][0] if child else None
	if child:
		frappe.db.set_value("Education Student", child, "guardian_email", parent_email)


def seed_education_demo(company: str | None = None, branch: str | None = None, institution_type: str | None = None) -> dict:
	"""Create institution demo + role users (idempotent)."""
	frappe.only_for(("System Manager", "Education Manager"))
	from omnexa_education.education_demo.branch_demo_seed import seed_education_branch_demo

	company, branch = _resolve_company_branch(company, branch)
	return seed_education_branch_demo(
		company,
		branch,
		institution_type=institution_type or "All 5 Types",
		seed_roles=1,
		sync_laravel=0,
	)


def get_demo_credentials() -> dict:
	return {
		"password": DEMO_PASSWORD,
		"users": [
			{
				"role": s["role"],
				"email": s["email"],
				"route": s["default_route"],
				"name": f"{s['first_name']} {s['last_name']}",
				"label_ar": s.get("portal_label_ar", ""),
				"label_en": s.get("portal_label_en", ""),
			}
			for s in ROLE_SPECS
		],
	}


def get_institution_demo_stats(company: str | None = None) -> list[dict]:
	try:
		company, _branch = _resolve_company_branch(company, None)
	except Exception:
		company = (company or "").strip() or frappe.db.get_value("Company", {}, "name", order_by="creation asc") or ""

	out = []
	for spec in INSTITUTION_DEMO_SPECS:
		inst = _find_demo_institution(company, spec)
		if not inst:
			out.append({**spec, "seeded": False, "active": False, "students": 0, "teachers": 0, "applications": 0})
			continue

		inst_company = frappe.db.get_value("Education Institution", inst, "company") or company
		campuses = frappe.get_all("Education Campus", filters={"institution": inst}, pluck="name") or []
		teacher_filters: dict = {"company": inst_company}
		if campuses:
			teacher_filters["campus"] = ["in", campuses]

		students = frappe.db.count("Education Student", {"institution": inst, "status": "Active"})
		inst_status = frappe.db.get_value("Education Institution", inst, "status") or "Active"
		out.append(
			{
				**spec,
				"seeded": True,
				"active": students > 0,
				"inactive": students == 0 and inst_status == "Active",
				"institution": inst,
				"students": students,
				"teachers": frappe.db.count("Education Teacher", teacher_filters) if frappe.db.exists("DocType", "Education Teacher") else 0,
				"applications": frappe.db.count("Education Admission Application", {"institution": inst}),
				"programs": frappe.db.count("Education Program", {"institution": inst}),
			}
		)
	return out


def _find_demo_institution(company: str | None, spec: dict) -> str | None:
	company = (company or "").strip()
	code_suffix = spec["code"]
	candidate_codes = [
		f"{DEMO_MARKER}-{code_suffix}",
		f"EDU-DEMO-{code_suffix}",
		f"ER-{DEMO_MARKER}-{code_suffix}",
		f"ER-EDU-DEMO-{code_suffix}",
		code_suffix,
	]

	def _lookup(filters: dict) -> str | None:
		return frappe.db.get_value("Education Institution", filters, "name", order_by="modified desc")

	if company:
		for code in candidate_codes:
			found = _lookup({"company": company, "institution_code": code})
			if found:
				return found
		found = _lookup({"company": company, "institution_name": spec["name"]})
		if found:
			return found

	for code in candidate_codes:
		found = _lookup({"institution_code": code})
		if found:
			return found

	for suffix in (f"EDU-DEMO-{code_suffix}", f"DEMO-{code_suffix}", code_suffix):
		rows = frappe.db.sql(
			"""
			SELECT name FROM `tabEducation Institution`
			WHERE (name LIKE %s OR institution_code LIKE %s)
				AND institution_type = %s
			ORDER BY modified DESC
			LIMIT 1
			""",
			(f"%{suffix}", f"%{suffix}", spec["institution_type"]),
		)
		if rows:
			return rows[0][0]

	found = _lookup({"institution_name": spec["name"]})
	if found:
		return found

	type_filters: dict = {"institution_type": spec["institution_type"], "status": "Active"}
	if company:
		type_filters["company"] = company
	return _lookup(type_filters)
