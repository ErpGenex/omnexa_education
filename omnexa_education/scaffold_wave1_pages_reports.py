#!/usr/bin/env python3
"""Scaffold Wave 1 desk pages and script reports."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "omnexa_education"
PAGES = [
	("education_registrar_desk", "education-registrar-desk", "Education Registrar Desk"),
	("education_teacher_gradebook", "education-teacher-gradebook", "Education Teacher Gradebook"),
	("education_student_portal", "education-student-portal", "Education Student Portal"),
	("education_timetable_board", "education-timetable-board", "Education Timetable Board"),
]
REPORTS = [
	("education_admissions_pipeline", "Education Admission Application", "Admissions Pipeline"),
	("education_attendance_summary", "Education Attendance Session", "Attendance Summary"),
	("education_grade_distribution", "Education Assessment Result", "Grade Distribution"),
	("education_transcript_status", "Education Transcript Request", "Transcript Status"),
]
ROLES = [{"role": "System Manager"}, {"role": "Education Manager"}, {"role": "Education User"}, {"role": "Teacher"}]


def _page(folder: str, page_name: str, title: str) -> None:
	path = ROOT / "page" / folder
	path.mkdir(parents=True, exist_ok=True)
	(path / f"{folder}.json").write_text(
		json.dumps(
			{
				"doctype": "Page",
				"module": "Omnexa Education",
				"name": page_name,
				"page_name": page_name,
				"standard": "Yes",
				"title": title,
				"roles": ROLES,
			},
			indent="\t",
		)
		+ "\n"
	)
	js = path / f"{folder}.js"
	if not js.exists():
		js.write_text(
			f'frappe.pages["{page_name}"].on_page_load = function (wrapper) {{\n'
			f'\tconst page = frappe.ui.make_app_page({{ parent: wrapper, title: __("{title}"), single_column: true }});\n'
			f'\t$(page.body).html(`<div class="p-3"><p class="text-muted">${{__("Wave 1 desk portal")}}</p></div>`);\n'
			f"}};\n"
		)
	py = path / f"{folder}.py"
	if not py.exists():
		py.write_text("")
	(path / "__init__.py").write_text("")


def _report(folder: str, ref: str, title: str) -> None:
	path = ROOT / "report" / folder
	path.mkdir(parents=True, exist_ok=True)
	(path / f"{folder}.json").write_text(
		json.dumps(
			{
				"add_total_row": 0,
				"columns": [],
				"disabled": 0,
				"doctype": "Report",
				"is_standard": "Yes",
				"module": "Omnexa Education",
				"name": title,
				"ref_doctype": ref,
				"report_name": title,
				"report_type": "Script Report",
				"roles": [{"role": "System Manager"}, {"role": "Education Manager"}, {"role": "Report Manager"}],
			},
			indent="\t",
		)
		+ "\n"
	)
	py = path / f"{folder}.py"
	if not py.exists():
		py.write_text(
			f'# Copyright (c) 2026, Omnexa\nimport frappe\nfrom frappe import _\n\n'
			f"def execute(filters=None):\n\tfilters = frappe._dict(filters or {{}})\n"
			f'\treturn _columns(), []\n\n'
			f"def _columns():\n\treturn [{{'label': _('Status'), 'fieldname': 'status', 'fieldtype': 'Data', 'width': 140}}]\n"
		)
	(path / f"{folder}.html").write_text("")
	(path / "__init__.py").write_text("")


def main() -> None:
	for folder, page_name, title in PAGES:
		_page(folder, page_name, title)
	for folder, ref, title in REPORTS:
		_report(folder, ref, title)
	print(f"Scaffolded {len(PAGES)} pages and {len(REPORTS)} reports")


if __name__ == "__main__":
	main()
