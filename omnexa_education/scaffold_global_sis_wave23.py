#!/usr/bin/env python3
"""Wave 2+3 — close all SIS gaps (Workday + Banner + PowerSchool parity)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "omnexa_education" / "doctype"
PERMS = [
	{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1},
	{"role": "Education Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1},
	{"role": "Education User", "read": 1, "write": 1, "create": 1, "delete": 0, "submit": 1, "cancel": 0},
	{"role": "Teacher", "read": 1, "write": 1, "create": 1, "delete": 0},
	{"role": "Desk User", "read": 1, "write": 1, "create": 1, "delete": 0},
]
CB = {"fieldname": "company", "fieldtype": "Link", "label": "Company", "options": "Company", "reqd": 1}
BR = {"fieldname": "branch", "fieldtype": "Link", "label": "Branch", "options": "Branch", "reqd": 1, "in_list_view": 1}
INST = {"fieldname": "institution", "fieldtype": "Link", "label": "Institution", "options": "Education Institution", "reqd": 1}

SPECS: list[tuple[str, dict]] = [
	("education_waitlist_pool", {
		"autoname": "format:WLP-{YYYY}-{#####}",
		"fields": [
			INST, CB, BR,
			{"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year", "options": "Education Academic Year", "reqd": 1},
			{"fieldname": "grade_level", "fieldtype": "Link", "label": "Grade Level", "options": "Education Grade Level"},
			{"fieldname": "program", "fieldtype": "Link", "label": "Program", "options": "Education Program"},
			{"fieldname": "capacity", "fieldtype": "Int", "label": "Capacity", "reqd": 1},
			{"fieldname": "waitlist_count", "fieldtype": "Int", "label": "Waitlist Count", "read_only": 1},
		],
	}),
	("education_lottery_run", {
		"autoname": "format:LOT-{YYYY}-{#####}",
		"is_submittable": 1,
		"fields": [
			INST, CB, BR,
			{"fieldname": "waitlist_pool", "fieldtype": "Link", "label": "Waitlist Pool", "options": "Education Waitlist Pool", "reqd": 1},
			{"fieldname": "run_date", "fieldtype": "Datetime", "label": "Run Date", "reqd": 1},
			{"fieldname": "seats_offered", "fieldtype": "Int", "label": "Seats Offered"},
			{"default": "Draft", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Draft\nCompleted\nCancelled", "in_list_view": 1},
		],
	}),
	("education_online_application", {
		"autoname": "format:WEB-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "applicant_name", "fieldtype": "Data", "label": "Applicant Name", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year", "options": "Education Academic Year", "reqd": 1},
			{"fieldname": "grade_level", "fieldtype": "Link", "label": "Grade Level", "options": "Education Grade Level"},
			{"fieldname": "program", "fieldtype": "Link", "label": "Program", "options": "Education Program"},
			{"fieldname": "guardian_email", "fieldtype": "Data", "label": "Guardian Email"},
			{"fieldname": "application_payload", "fieldtype": "Code", "label": "Payload JSON", "options": "JSON"},
			{"default": "Submitted", "fieldname": "status", "fieldtype": "Select", "label": "Status",
			 "options": "Submitted\nReviewed\nAccepted\nRejected", "in_list_view": 1},
			{"fieldname": "admission_application", "fieldtype": "Link", "label": "Admission Application", "options": "Education Admission Application"},
		],
	}),
	("education_timetable_template", {
		"autoname": "field:template_name",
		"fields": [
			{"fieldname": "template_name", "fieldtype": "Data", "label": "Template Name", "reqd": 1, "unique": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "periods_per_day", "fieldtype": "Int", "label": "Periods per Day", "default": "8"},
			{"fieldname": "weekdays", "fieldtype": "Data", "label": "Weekdays", "default": "Sunday,Monday,Tuesday,Wednesday,Thursday"},
		],
	}),
	("education_grading_scale", {
		"autoname": "field:scale_name",
		"fields": [
			{"fieldname": "scale_name", "fieldtype": "Data", "label": "Scale Name", "reqd": 1, "unique": 1, "in_list_view": 1},
			INST, CB,
			{"fieldname": "scale_type", "fieldtype": "Select", "label": "Type",
			 "options": "Percentage\nGPA 4.0\nGPA 5.0\nLetter\nRubric", "reqd": 1},
			{"fieldname": "grade_mappings", "fieldtype": "Code", "label": "Grade Mappings JSON", "options": "JSON"},
		],
	}),
	("education_official_transcript", {
		"autoname": "format:TRN-{YYYY}-{#####}",
		"is_submittable": 1,
		"fields": [
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "issue_date", "fieldtype": "Date", "label": "Issue Date", "default": "Today"},
			{"fieldname": "cgpa", "fieldtype": "Float", "label": "CGPA"},
			{"fieldname": "total_credits", "fieldtype": "Float", "label": "Total Credits"},
			{"default": "Draft", "fieldname": "status", "fieldtype": "Select", "label": "Status",
			 "options": "Draft\nIssued\nRevoked", "in_list_view": 1},
		],
	}),
	("education_ferpa_access_log", {
		"autoname": "hash",
		"fields": [
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			{"fieldname": "accessed_by", "fieldtype": "Link", "label": "Accessed By", "options": "User", "reqd": 1},
			{"fieldname": "access_datetime", "fieldtype": "Datetime", "label": "Access Time", "reqd": 1, "in_list_view": 1},
			{"fieldname": "resource_type", "fieldtype": "Data", "label": "Resource", "reqd": 1},
			{"fieldname": "resource_name", "fieldtype": "Data", "label": "Resource Name"},
			{"fieldname": "purpose", "fieldtype": "Small Text", "label": "Purpose"},
			INST, CB, BR,
		],
	}),
	("education_student_consent", {
		"autoname": "format:CNS-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			{"fieldname": "consent_type", "fieldtype": "Select", "label": "Consent Type",
			 "options": "FERPA Directory\nPhoto/Media\nData Sharing\nMedical\nOther", "reqd": 1},
			{"default": "1", "fieldname": "consent_given", "fieldtype": "Check", "label": "Consent Given"},
			{"fieldname": "signed_on", "fieldtype": "Date", "label": "Signed On"},
			{"fieldname": "guardian_name", "fieldtype": "Data", "label": "Guardian Name"},
			INST, CB, BR,
		],
	}),
	("education_announcement", {
		"autoname": "format:ANN-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "title", "fieldtype": "Data", "label": "Title", "reqd": 1, "in_list_view": 1},
			{"fieldname": "message", "fieldtype": "Text Editor", "label": "Message", "reqd": 1},
			INST, CB, BR,
			{"fieldname": "audience", "fieldtype": "Select", "label": "Audience",
			 "options": "All\nStudents\nParents\nTeachers\nStaff", "default": "All"},
			{"fieldname": "publish_date", "fieldtype": "Date", "label": "Publish Date", "default": "Today"},
		],
	}),
	("education_library_book", {
		"autoname": "field:isbn",
		"fields": [
			{"fieldname": "isbn", "fieldtype": "Data", "label": "ISBN / Code", "reqd": 1, "unique": 1, "in_list_view": 1},
			{"fieldname": "title", "fieldtype": "Data", "label": "Title", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "copies_total", "fieldtype": "Int", "label": "Total Copies", "default": "1"},
			{"fieldname": "copies_available", "fieldtype": "Int", "label": "Available", "default": "1"},
		],
	}),
	("education_library_loan", {
		"autoname": "format:LIB-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "book", "fieldtype": "Link", "label": "Book", "options": "Education Library Book", "reqd": 1},
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "loan_date", "fieldtype": "Date", "label": "Loan Date", "default": "Today"},
			{"fieldname": "due_date", "fieldtype": "Date", "label": "Due Date"},
			{"fieldname": "return_date", "fieldtype": "Date", "label": "Return Date"},
			{"default": "On Loan", "fieldname": "status", "fieldtype": "Select", "label": "Status",
			 "options": "On Loan\nReturned\nOverdue\nLost", "in_list_view": 1},
		],
	}),
	("education_transport_route", {
		"autoname": "field:route_code",
		"fields": [
			{"fieldname": "route_code", "fieldtype": "Data", "label": "Route Code", "reqd": 1, "unique": 1, "in_list_view": 1},
			{"fieldname": "route_name", "fieldtype": "Data", "label": "Route Name", "reqd": 1},
			INST, CB, BR,
			{"fieldname": "driver_name", "fieldtype": "Data", "label": "Driver"},
			{"fieldname": "vehicle_number", "fieldtype": "Data", "label": "Vehicle"},
			{"fieldname": "capacity", "fieldtype": "Int", "label": "Capacity"},
		],
	}),
	("education_hostel_room", {
		"autoname": "field:room_code",
		"fields": [
			{"fieldname": "room_code", "fieldtype": "Data", "label": "Room Code", "reqd": 1, "unique": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "campus", "fieldtype": "Link", "label": "Campus", "options": "Education Campus"},
			{"fieldname": "capacity", "fieldtype": "Int", "label": "Beds", "default": "2"},
			{"fieldname": "gender", "fieldtype": "Select", "label": "Gender", "options": "Male\nFemale\nMixed"},
		],
	}),
	("education_hostel_allocation", {
		"autoname": "format:HST-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			{"fieldname": "hostel_room", "fieldtype": "Link", "label": "Hostel Room", "options": "Education Hostel Room", "reqd": 1},
			INST, CB, BR,
			{"fieldname": "from_date", "fieldtype": "Date", "label": "From", "reqd": 1},
			{"fieldname": "to_date", "fieldtype": "Date", "label": "To"},
			{"default": "Active", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Active\nVacated"},
		],
	}),
	("education_discipline_incident", {
		"autoname": "format:DIS-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "incident_date", "fieldtype": "Date", "label": "Date", "reqd": 1, "default": "Today"},
			{"fieldname": "category", "fieldtype": "Select", "label": "Category",
			 "options": "Minor\nMajor\nBullying\nSafety\nOther", "reqd": 1},
			{"fieldname": "description", "fieldtype": "Text", "label": "Description", "reqd": 1},
			{"fieldname": "action_taken", "fieldtype": "Small Text", "label": "Action Taken"},
		],
	}),
	("education_credit_transfer", {
		"autoname": "format:CTR-{YYYY}-{#####}",
		"is_submittable": 1,
		"fields": [
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "external_institution", "fieldtype": "Data", "label": "External Institution", "reqd": 1},
			{"fieldname": "external_course", "fieldtype": "Data", "label": "External Course", "reqd": 1},
			{"fieldname": "internal_course", "fieldtype": "Link", "label": "Internal Course", "options": "Education Course"},
			{"fieldname": "credits_transferred", "fieldtype": "Float", "label": "Credits", "reqd": 1},
			{"default": "Draft", "fieldname": "status", "fieldtype": "Select", "label": "Status",
			 "options": "Draft\nApproved\nRejected", "in_list_view": 1},
		],
	}),
	("education_academic_standing", {
		"autoname": "format:STD-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year", "options": "Education Academic Year", "reqd": 1},
			{"fieldname": "term", "fieldtype": "Link", "label": "Term", "options": "Education Term"},
			{"fieldname": "gpa", "fieldtype": "Float", "label": "GPA"},
			{"default": "Good Standing", "fieldname": "standing", "fieldtype": "Select", "label": "Standing",
			 "options": "Good Standing\nDean's List\nProbation\nSuspension\nHonors", "in_list_view": 1},
		],
	}),
	("education_alumni_record", {
		"autoname": "format:ALM-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "graduation_date", "fieldtype": "Date", "label": "Graduation Date"},
			{"fieldname": "program", "fieldtype": "Link", "label": "Program", "options": "Education Program"},
			{"fieldname": "current_employer", "fieldtype": "Data", "label": "Employer"},
			{"fieldname": "contact_email", "fieldtype": "Data", "label": "Contact Email"},
		],
	}),
	("education_lms_course_link", {
		"autoname": "format:LMS-{#####}",
		"fields": [
			{"fieldname": "course", "fieldtype": "Link", "label": "Course", "options": "Education Course", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "lms_provider", "fieldtype": "Select", "label": "LMS Provider",
			 "options": "Moodle\nCanvas\nGoogle Classroom\nBlackboard\nCustom API", "reqd": 1},
			{"fieldname": "external_course_id", "fieldtype": "Data", "label": "External Course ID", "reqd": 1},
			{"fieldname": "sync_url", "fieldtype": "Data", "label": "Sync URL"},
			{"default": "1", "fieldname": "is_active", "fieldtype": "Check", "label": "Active"},
		],
	}),
	("education_mobile_device_token", {
		"autoname": "hash",
		"fields": [
			{"fieldname": "user", "fieldtype": "Link", "label": "User", "options": "User", "reqd": 1, "in_list_view": 1},
			{"fieldname": "device_id", "fieldtype": "Data", "label": "Device ID", "reqd": 1},
			{"fieldname": "platform", "fieldtype": "Select", "label": "Platform", "options": "ios\nandroid\nweb", "reqd": 1},
			{"fieldname": "push_token", "fieldtype": "Data", "label": "Push Token"},
			{"default": "1", "fieldname": "is_active", "fieldtype": "Check", "label": "Active"},
		],
	}),
	("education_predictive_alert", {
		"autoname": "format:ALT-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			INST, CB, BR,
			{"fieldname": "alert_type", "fieldtype": "Select", "label": "Alert Type",
			 "options": "At-Risk\nChronic Absence\nFee Default\nGrade Drop", "reqd": 1, "in_list_view": 1},
			{"fieldname": "score", "fieldtype": "Float", "label": "Risk Score"},
			{"fieldname": "details", "fieldtype": "Small Text", "label": "Details"},
			{"default": "Open", "fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Open\nAcknowledged\nClosed"},
		],
	}),
	("education_scholarship", {
		"autoname": "field:scholarship_code",
		"fields": [
			{"fieldname": "scholarship_code", "fieldtype": "Data", "label": "Code", "reqd": 1, "unique": 1, "in_list_view": 1},
			{"fieldname": "scholarship_name", "fieldtype": "Data", "label": "Name", "reqd": 1},
			INST, CB, BR,
			{"fieldname": "amount", "fieldtype": "Currency", "label": "Amount"},
			{"fieldname": "percent_discount", "fieldtype": "Percent", "label": "Discount %"},
		],
	}),
	("education_scholarship_award", {
		"autoname": "format:AWD-{YYYY}-{#####}",
		"fields": [
			{"fieldname": "student", "fieldtype": "Link", "label": "Student", "options": "Education Student", "reqd": 1, "in_list_view": 1},
			{"fieldname": "scholarship", "fieldtype": "Link", "label": "Scholarship", "options": "Education Scholarship", "reqd": 1},
			INST, CB, BR,
			{"fieldname": "academic_year", "fieldtype": "Link", "label": "Academic Year", "options": "Education Academic Year", "reqd": 1},
			{"fieldname": "award_date", "fieldtype": "Date", "label": "Award Date", "default": "Today"},
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
				f"# Copyright (c) 2026, Omnexa\nfrom frappe.model.document import Document\n\n\nclass {cls}(Document):\n\tpass\n"
			)
		(path / "__init__.py").write_text("")
	print(f"Scaffolded {len(SPECS)} Wave 2+3 doctypes")


if __name__ == "__main__":
	main()
