# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe

from omnexa_core.omnexa_core.branch_access import enforce_branch_access, get_allowed_branches
from omnexa_core.omnexa_core.user_context import apply_company_branch_defaults

PORTAL_ROLES = frozenset({"Education Student Portal", "Education Parent Portal"})
STAFF_EDUCATION_ROLES = frozenset({"System Manager", "Education Manager", "Education User", "Teacher"})


def _user_roles(user=None):
	return set(frappe.get_roles(user or frappe.session.user))


def _portal_only(user=None) -> bool:
	roles = _user_roles(user)
	return bool(roles & PORTAL_ROLES) and not roles & STAFF_EDUCATION_ROLES


def _portal_student_names_subquery(user: str) -> str:
	return (
		f"SELECT name FROM `tabEducation Student` WHERE user = {frappe.db.escape(user)} "
		f"OR guardian_email = {frappe.db.escape(user)}"
	)


def _portal_student_field_filter(table: str, user=None) -> str | None:
	user = user or frappe.session.user
	if not _portal_only(user):
		return None
	return f"`tab{table}`.student in ({_portal_student_names_subquery(user)})"


def _portal_section_filter(table: str, user=None) -> str | None:
	user = user or frappe.session.user
	if not _portal_only(user):
		return None
	roles = _user_roles(user)
	if "Education Student Portal" in roles:
		section = frappe.db.get_value("Education Student", {"user": user}, "section")
		if section:
			return f"`tab{table}`.section = {frappe.db.escape(section)}"
		return "1=0"
	if "Education Parent Portal" in roles:
		sections = frappe.get_all(
			"Education Student",
			filters={"guardian_email": user, "status": "Active"},
			pluck="section",
		)
		sections = [s for s in sections if s]
		if sections:
			quoted = ", ".join(frappe.db.escape(s) for s in sections)
			return f"`tab{table}`.section in ({quoted})"
		return "1=0"
	return None


def enforce_branch_access_for_doc(doc, method=None):
	enforce_branch_access(doc)


def populate_company_branch_from_user_context(doc, method=None):
	apply_company_branch_defaults(doc)


def _get_query_for_table(table: str, user=None):
	user = user or frappe.session.user
	allowed = get_allowed_branches(user)
	if allowed is None:
		return ""
	if not allowed:
		return "1=0"
	quoted = ", ".join([frappe.db.escape(v) for v in allowed])
	return f"(`tab{table}`.branch in ({quoted}) or `tab{table}`.branch is null or `tab{table}`.branch = '')"


def _companies_for_allowed_branches(user=None):
	user = user or frappe.session.user
	allowed = get_allowed_branches(user)
	if allowed is None:
		return None
	if not allowed:
		return []
	companies = set()
	for b in allowed:
		c = frappe.db.get_value("Branch", b, "company")
		if c:
			companies.add(c)
	return companies


def _company_query(table: str, user=None):
	companies = _companies_for_allowed_branches(user)
	if companies is None:
		return ""
	if not companies:
		return "1=0"
	quoted = ", ".join([frappe.db.escape(c) for c in companies])
	return f"`tab{table}`.company in ({quoted})"


def education_institution_query_conditions(user=None):
	return _company_query("Education Institution", user)


def education_campus_query_conditions(user=None):
	return _get_query_for_table("Education Campus", user)


def education_department_query_conditions(user=None):
	return _get_query_for_table("Education Department", user)


def education_curriculum_query_conditions(user=None):
	return _company_query("Education Curriculum", user)


def education_academic_year_query_conditions(user=None):
	return _company_query("Education Academic Year", user)


def education_term_query_conditions(user=None):
	return _company_query("Education Term", user)


def education_grade_level_query_conditions(user=None):
	return _company_query("Education Grade Level", user)


def education_section_query_conditions(user=None):
	return _get_query_for_table("Education Section", user)


def education_subject_query_conditions(user=None):
	return _company_query("Education Subject", user)


def education_student_query_conditions(user=None):
	user = user or frappe.session.user
	roles = _user_roles(user)
	if "System Manager" not in roles and "Education Manager" not in roles and "Education User" not in roles:
		if "Education Student Portal" in roles:
			return f"`tabEducation Student`.user = {frappe.db.escape(user)}"
		if "Education Parent Portal" in roles:
			return f"`tabEducation Student`.guardian_email = {frappe.db.escape(user)}"
	return _get_query_for_table("Education Student", user)


def education_portal_message_query_conditions(user=None):
	portal = _portal_student_field_filter("Education Portal Message", user)
	if portal:
		return portal
	return _get_query_for_table("Education Portal Message", user)


def education_announcement_query_conditions(user=None):
	user = user or frappe.session.user
	if _portal_only(user):
		roles = _user_roles(user)
		filters: dict = {"status": "Active"}
		if "Education Student Portal" in roles:
			filters["user"] = user
		else:
			filters["guardian_email"] = user
		institutions = frappe.get_all("Education Student", filters=filters, pluck="institution")
		institutions = [i for i in institutions if i]
		if institutions:
			quoted = ", ".join(frappe.db.escape(i) for i in institutions)
			return (
				f"(`tabEducation Announcement`.institution in ({quoted}) "
				f"or `tabEducation Announcement`.institution is null "
				f"or `tabEducation Announcement`.institution = '')"
			)
		return "1=0"
	return _company_query("Education Announcement", user)


def education_fee_item_query_conditions(user=None):
	return _company_query("Education Fee Item", user)


def education_billing_invoice_query_conditions(user=None):
	return _get_query_for_table("Education Billing Invoice", user)


def education_fee_plan_query_conditions(user=None):
	return _get_query_for_table("Education Fee Plan", user)


def education_discount_rule_query_conditions(user=None):
	return _get_query_for_table("Education Discount Rule", user)


def education_late_fee_rule_query_conditions(user=None):
	return _get_query_for_table("Education Late Fee Rule", user)


def education_billing_cycle_query_conditions(user=None):
	return _get_query_for_table("Education Billing Cycle", user)


def education_teacher_query_conditions(user=None):
	return _get_query_for_table("Education Teacher", user)


def make_branch_query(doctype: str):
	def fn(user=None):
		return _get_query_for_table(doctype, user)

	return fn


education_program_query_conditions = make_branch_query("Education Program")
education_course_query_conditions = make_branch_query("Education Course")
education_room_query_conditions = make_branch_query("Education Room")
education_admission_application_query_conditions = make_branch_query("Education Admission Application")
education_student_enrollment_query_conditions = make_branch_query("Education Student Enrollment")
education_course_enrollment_query_conditions = make_branch_query("Education Course Enrollment")
education_teacher_assignment_query_conditions = make_branch_query("Education Teacher Assignment")


def education_timetable_entry_query_conditions(user=None):
	portal = _portal_section_filter("Education Timetable Entry", user)
	if portal:
		return portal
	return _get_query_for_table("Education Timetable Entry", user)


def education_assessment_result_query_conditions(user=None):
	portal = _portal_student_field_filter("Education Assessment Result", user)
	if portal:
		return portal
	return _get_query_for_table("Education Assessment Result", user)


def education_attendance_session_query_conditions(user=None):
	portal = _portal_section_filter("Education Attendance Session", user)
	if portal:
		return portal
	return _get_query_for_table("Education Attendance Session", user)


education_assessment_plan_query_conditions = make_branch_query("Education Assessment Plan")
education_report_card_query_conditions = make_branch_query("Education Report Card")
education_transcript_request_query_conditions = make_branch_query("Education Transcript Request")
