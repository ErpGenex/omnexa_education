#!/usr/bin/env python3
"""Wave 1 — Workday Student + Banner + PowerSchool unified SIS scaffold."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "omnexa_education" / "doctype"
PERMS = [
	{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1},
	{"role": "Education Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1},
	{"role": "Education User", "read": 1, "write": 1, "create": 1, "delete": 0, "submit": 1, "cancel": 0},
	{"role": "Teacher", "read": 1, "write": 1, "create": 1, "delete": 0, "submit": 1, "cancel": 0},
	{"role": "Desk User", "read": 1, "write": 1, "create": 1, "delete": 0},
]
CB = {"fieldname": "company", "fieldtype": "Link", "label": "Company", "options": "Company", "reqd": 1}
BR = {"fieldname": "branch", "fieldtype": "Link", "label": "Branch", "options": "Branch", "reqd": 1, "in_list_view": 1}
INST = {"fieldname": "institution", "fieldtype": "Link", "label": "Institution", "options": "Education Institution", "reqd": 1}

SPECS: list[tuple[str, dict]] = [
	("education_settings", {
		"issingle": 1,
		"fields": [
			{"fieldname": "default_institution_type", "fieldtype": "Select", "label": "Default Institution Type",
			 "options": "School\nAcademy\nUniversity\nTraining Center\nInstitute"},
			{"default": "1", "fieldname": "enable_university_modules", "fieldtype": "Check", "label": "Enable University (Banner/Workday)"},
			{"default": "1", "fieldname": "enable_k12_modules", "fieldtype": "Check", "label": "Enable K12 (PowerSchool)"},
			{"default": "1", "fieldname": "auto_create_customer", "fieldtype": "Check", "label": "Auto-create Customer for Students"},
			{"fieldname": "attendance_lock_days", "fieldtype": "Int", "label": "Attendance lock after (days)", "default": "7"},
			{"fieldname": "grade_publish_requires_approval", "fieldtype": "Check", "label": "Grades require approval before publish"},
		],
	}),
	("education_program", {
		"autoname": "field:program_code",
		"fields": [
			{"fieldname": "program_code", "fieldtype": "Data", "label": "Program Code", "reqd": 1, "unique": 1, "in_list_view": 1},
			{"fieldname": "program_name", "fieldtype": "Data", "label": "Program Name", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "department", "fieldtype": "Link", "label": "Department", "options": "Education Department"},
			{"fieldname": "degree_level", "fieldtype": "Select", "label": "Degree Level",
			 "options": "Certificate\nDiploma\nAssociate\nBachelor\nMaster\nDoctorate\nProfessional"},
			{"fieldname": "total_credits", "fieldtype": "Float", "label": "Total Credits Required"},
			{"default": "1", "fieldname": "is_active", "fieldtype": "Check", "label": "Active"},
		],
	}),
	("education_course", {
		"autoname": "field:course_code",
		"fields": [
			{"fieldname": "course_code", "fieldtype": "Data", "label": "Course Code", "reqd": 1, "unique": 1, "in_list_view": 1},
			{"fieldname": "course_title", "fieldtype": "Data", "label": "Course Title", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "subject", "fieldtype": "Link", "label": "Subject", "options": "Education Subject"},
			{"fieldname": "program", "fieldtype": "Link", "label": "Program", "options": "Education Program"},
			{"fieldname": "credit_hours", "fieldtype": "Float", "label": "Credit Hours"},
			{"fieldname": "grade_level", "fieldtype": "Link", "label": "Grade Level (K12)", "options": "Education Grade Level"},
			{"default": "1", "fieldname": "is_active", "fieldtype": "Check", "label": "Active"},
		],
	}),
	("education_room", {
		"autoname": "field:room_code",
		"fields": [
			{"fieldname": "room_code", "fieldtype": "Data", "label": "Room Code", "reqd": 1, "unique": 1, "in_list_view": 1},
			{"fieldname": "room_name", "fieldtype": "Data", "label": "Room Name", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "campus", "fieldtype": "Link", "label": "Campus", "options": "Education Campus"},
			{"fieldname": "capacity", "fieldtype": "Int", "label": "Capacity"},
			{"fieldname": "room_type", "fieldtype": "Select", "label": "Type", "options": "Classroom\nLab\nAuditorium\nGym\nOnline"},
		],
	}),
	("education_admission_application", {
		"autoname": "format:ADM-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "applicant_name", "fieldtype": "Data", "label": "Applicant Name", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year", "options": "Education Academic Year", "reqd": 1},
			{"fieldname": "grade_level", "fieldtype": "Link", "label": "Grade Level", "options": "Education Grade Level"},
			{"fieldname": "program", "fieldtype": "Link", "label": "Program", "options": "Education Program"},
			{"fieldname": "application_date", "fieldtype": "Date", "label": "Application Date", "reqd": 1, "default": "Today"},
			{"default": "Submitted", "fieldname": "status", "fieldtype": "Select", "label": "Status",
			 "options": "Draft\nSubmitted\nUnder Review\nWaitlisted\nAccepted\nRejected\nEnrolled\nWithdrawn", "in_list_view": 1},
			{"fieldname": "guardian_name", "fieldtype": "Data", "label": "Guardian Name"},
			{"fieldname": "guardian_phone", "fieldtype": "Data", "label": "Guardian Phone"},
			{"fieldname": "guardian_email", "fieldtype": "Data", "label": "Guardian Email"},
			{"fieldname": "student", "fieldtype": "Link", "label": "Student (after enroll)", "options": "Education Student"},
		],
	}),
	("education_student_enrollment", {
		"autoname": "format:ENR-{YYYY}-{#####}",
		"is_submittable": 1,
		"fields": [
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year", "options": "Education Academic Year", "reqd": 1},
			{"fieldname": "term", "fieldtype": "Link", "label": "Term", "options": "Education Term"},
			{"fieldname": "grade_level", "fieldtype": "Link", "label": "Grade Level", "options": "Education Grade Level"},
			{"fieldname": "section", "fieldtype": "Link", "label": "Section", "options": "Education Section"},
			{"fieldname": "program", "fieldtype": "Link", "label": "Program", "options": "Education Program"},
			{"default": "Enrolled", "fieldname": "enrollment_status", "fieldtype": "Select", "label": "Status",
			 "options": "Enrolled\nPromoted\nTransferred\nWithdrawn\nGraduated\nAlumni", "in_list_view": 1},
			{"fieldname": "enrollment_date", "fieldtype": "Date", "label": "Enrollment Date", "default": "Today"},
		],
	}),
	("education_course_enrollment", {
		"autoname": "format:CEN-{YYYY}-{#####}",
		"is_submittable": 1,
		"fields": [
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			{"fieldname": "course", "fieldtype": "Link", "label": "Course", "options": "Education Course", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year", "options": "Education Academic Year", "reqd": 1},
			{"fieldname": "term", "fieldtype": "Link", "label": "Term", "options": "Education Term", "reqd": 1},
			{"default": "Registered", "fieldname": "status", "fieldtype": "Select", "label": "Status",
			 "options": "Registered\nDropped\nCompleted\nFailed\nIn Progress", "in_list_view": 1},
			{"fieldname": "credits_earned", "fieldtype": "Float", "label": "Credits Earned"},
		],
	}),
	("education_teacher_assignment", {
		"autoname": "format:TAS-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "teacher", "fieldtype": "Link", "label": "Teacher", "options": "Education Teacher", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year", "options": "Education Academic Year", "reqd": 1},
			{"fieldname": "term", "fieldtype": "Link", "label": "Term", "options": "Education Term"},
			{"fieldname": "section", "fieldtype": "Link", "label": "Section (K12)", "options": "Education Section"},
			{"fieldname": "course", "fieldtype": "Link", "label": "Course (University)", "options": "Education Course"},
			{"fieldname": "subject", "fieldtype": "Link", "label": "Subject", "options": "Education Subject"},
			{"default": "Primary", "fieldname": "role", "fieldtype": "Select", "label": "Role", "options": "Primary\nCo-Teacher\nSubstitute\nAdvisor"},
		],
	}),
	("education_timetable_entry", {
		"autoname": "format:TTB-{YYYY}-{#####}",
		"fields": [
			INST, CB, BR,
			{"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year", "options": "Education Academic Year", "reqd": 1},
			{"fieldname": "term", "fieldtype": "Link", "label": "Term", "options": "Education Term"},
			{"fieldname": "section", "fieldtype": "Link", "label": "Section", "options": "Education Section"},
			{"fieldname": "course", "fieldtype": "Link", "label": "Course", "options": "Education Course"},
			{"fieldname": "subject", "fieldtype": "Link", "label": "Subject", "options": "Education Subject", "reqd": 1},
			{"fieldname": "teacher", "fieldtype": "Link", "label": "Teacher", "options": "Education Teacher"},
			{"fieldname": "room", "fieldtype": "Link", "label": "Room", "options": "Education Room"},
			{"fieldname": "weekday", "fieldtype": "Select", "label": "Weekday",
			 "options": "Sunday\nMonday\nTuesday\nWednesday\nThursday\nFriday\nSaturday", "reqd": 1, "in_list_view": 1},
			{"fieldname": "from_time", "fieldtype": "Time", "label": "From", "reqd": 1},
			{"fieldname": "to_time", "fieldtype": "Time", "label": "To", "reqd": 1},
		],
	}),
	("education_attendance_record", {
		"istable": 1,
		"fields": [
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			{"default": "Present", "fieldname": "status", "fieldtype": "Select", "label": "Status",
			 "options": "Present\nAbsent\nLate\nExcused\nRemote", "in_list_view": 1},
			{"fieldname": "remarks", "fieldtype": "Small Text", "label": "Remarks"},
		],
	}),
	("education_attendance_session", {
		"autoname": "format:ATT-{YYYY}-{#####}",
		"is_submittable": 1,
		"fields": [
			INST, CB, BR,
			{"fieldname": "session_date", "fieldtype": "Date", "label": "Date", "reqd": 1, "default": "Today", "in_list_view": 1},
			{"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year", "options": "Education Academic Year", "reqd": 1},
			{"fieldname": "section", "fieldtype": "Link", "label": "Section", "options": "Education Section"},
			{"fieldname": "course", "fieldtype": "Link", "label": "Course", "options": "Education Course"},
			{"fieldname": "subject", "fieldtype": "Link", "label": "Subject", "options": "Education Subject"},
			{"fieldname": "teacher", "fieldtype": "Link", "label": "Teacher", "options": "Education Teacher"},
			{"fieldname": "attendance_records", "fieldtype": "Table", "label": "Attendance", "options": "Education Attendance Record"},
		],
	}),
	("education_assessment_plan", {
		"autoname": "format:APL-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "plan_name", "fieldtype": "Data", "label": "Plan Name", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year", "options": "Education Academic Year", "reqd": 1},
			{"fieldname": "term", "fieldtype": "Link", "label": "Term", "options": "Education Term"},
			{"fieldname": "section", "fieldtype": "Link", "label": "Section", "options": "Education Section"},
			{"fieldname": "course", "fieldtype": "Link", "label": "Course", "options": "Education Course"},
			{"fieldname": "subject", "fieldtype": "Link", "label": "Subject", "options": "Education Subject", "reqd": 1},
			{"fieldname": "assessment_type", "fieldtype": "Select", "label": "Type",
			 "options": "Quiz\nExam\nAssignment\nProject\nParticipation\nFinal", "reqd": 1},
			{"fieldname": "max_score", "fieldtype": "Float", "label": "Max Score", "default": "100"},
			{"fieldname": "weight_percent", "fieldtype": "Percent", "label": "Weight %"},
			{"fieldname": "due_date", "fieldtype": "Date", "label": "Due Date"},
		],
	}),
	("education_assessment_result", {
		"autoname": "format:RES-{YYYY}-{#####}",
		"is_submittable": 1,
		"fields": [
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			{"fieldname": "assessment_plan", "fieldtype": "Link", "label": "Assessment Plan", "options": "Education Assessment Plan", "reqd": 1},
			INST, CB, BR,
			{"fieldname": "score", "fieldtype": "Float", "label": "Score", "in_list_view": 1},
			{"fieldname": "grade_letter", "fieldtype": "Data", "label": "Grade Letter"},
			{"fieldname": "gpa_points", "fieldtype": "Float", "label": "GPA Points"},
			{"default": "Draft", "fieldname": "status", "fieldtype": "Select", "label": "Status",
			 "options": "Draft\nSubmitted\nPublished\nLocked", "in_list_view": 1},
			{"fieldname": "remarks", "fieldtype": "Small Text", "label": "Remarks"},
		],
	}),
	("education_report_card", {
		"autoname": "format:RC-{YYYY}-{#####}",
		"is_submittable": 1,
		"fields": [
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year", "options": "Education Academic Year", "reqd": 1},
			{"fieldname": "term", "fieldtype": "Link", "label": "Term", "options": "Education Term"},
			{"fieldname": "section", "fieldtype": "Link", "label": "Section", "options": "Education Section"},
			{"fieldname": "gpa", "fieldtype": "Float", "label": "Term GPA"},
			{"fieldname": "cgpa", "fieldtype": "Float", "label": "Cumulative GPA"},
			{"default": "Draft", "fieldname": "status", "fieldtype": "Select", "label": "Status",
			 "options": "Draft\nPublished\nArchived", "in_list_view": 1},
			{"fieldname": "comments", "fieldtype": "Text Editor", "label": "Comments"},
		],
	}),
	("education_transcript_request", {
		"autoname": "format:TRQ-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "request_date", "fieldtype": "Date", "label": "Request Date", "default": "Today"},
			{"default": "Requested", "fieldname": "status", "fieldtype": "Select", "label": "Status",
			 "options": "Requested\nIn Progress\nIssued\nRejected", "in_list_view": 1},
			{"fieldname": "purpose", "fieldtype": "Small Text", "label": "Purpose"},
			{"fieldname": "delivery_method", "fieldtype": "Select", "label": "Delivery", "options": "Pickup\nEmail\nCourier"},
		],
	}),
]


def class_name(folder: str) -> str:
	return "Education" + "".join(p.capitalize() for p in folder.replace("education_", "").split("_"))


def main() -> None:
	for folder, spec in SPECS:
		path = ROOT / folder
		path.mkdir(parents=True, exist_ok=True)
		parts = folder.replace("education_", "").split("_")
		title = "Education " + " ".join(p.capitalize() for p in parts)
		doc = {
			"actions": [],
			"doctype": "DocType",
			"engine": "InnoDB",
			"module": "Omnexa Education",
			"name": title,
			"permissions": [] if spec.get("istable") else PERMS,
			"track_changes": 1,
			**{k: v for k, v in spec.items() if k not in ("fields", "istable")},
			"fields": spec["fields"],
		}
		(path / f"{folder}.json").write_text(json.dumps(doc, indent="\t") + "\n")
		py = path / f"{folder}.py"
		if not py.exists():
			cls = class_name(folder)
			py.write_text(
				f"# Copyright (c) 2026, Omnexa and contributors\n# License: MIT\nfrom frappe.model.document import Document\n\n\nclass {cls}(Document):\n\tpass\n"
			)
		init = path / "__init__.py"
		if not init.exists():
			init.write_text("")
	print(f"Scaffolded {len(SPECS)} Wave-1 SIS doctypes")


if __name__ == "__main__":
	main()
