#!/usr/bin/env python3
"""Scaffold Wave 2+3 pages, reports, print format."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "omnexa_education"
PAGES = [
	("education_parent_mobile", "education-parent-mobile", "Education Parent Mobile"),
	("education_admissions_portal", "education-admissions-portal", "Education Admissions Portal"),
	("education_analytics_dashboard", "education-analytics-dashboard", "Education Analytics Dashboard"),
	("education_executive_dashboard", "education-executive-dashboard", "Education Executive Dashboard"),
]
REPORTS = [
	("waitlist_status", "Education Waitlist Pool", "Waitlist Status"),
	("gpa_summary", "Education Academic Standing", "GPA Summary"),
	("ferpa_audit_trail", "Education Ferpa Access Log", "FERPA Audit Trail"),
	("retention_risk_alerts", "Education Predictive Alert", "Retention Risk Alerts"),
	("lms_sync_status", "Education Lms Course Link", "LMS Sync Status"),
]
ROLES = [{"role": "System Manager"}, {"role": "Education Manager"}, {"role": "Education User"}, {"role": "Teacher"}]


def _page(folder: str, page_name: str, title: str, body_hint: str) -> None:
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
	js.write_text(
		f'frappe.pages["{page_name}"].on_page_load = function (wrapper) {{\n'
		f'\tconst page = frappe.ui.make_app_page({{ parent: wrapper, title: __("{title}"), single_column: true }});\n'
		f'\t$(page.body).html(`<div class="p-3"><p class="text-muted">${{__("{body_hint}")}}</p></div>`);\n'
		f"}};\n"
	)
	(path / f"{folder}.py").write_text("")
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
	py.write_text(
		f'import frappe\n\n\ndef execute(filters=None):\n\tcolumns = [\n'
		f'\t\t{{"label": "Name", "fieldname": "name", "fieldtype": "Data", "width": 180}},\n'
		f'\t\t{{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120}},\n'
		f'\t]\n\tdata = frappe.get_all("{ref}", fields=["name"], limit=100)\n'
		f'\tfor row in data:\n\t\trow["status"] = "OK"\n\treturn columns, data\n'
	)
	(path / f"{folder}.html").write_text("")
	(path / "__init__.py").write_text("")


def _print_format() -> None:
	path = ROOT / "print_format" / "education_official_transcript"
	path.mkdir(parents=True, exist_ok=True)
	(path / "education_official_transcript.json").write_text(
		json.dumps(
			{
				"absolute_value": 0,
				"align_labels_right": 0,
				"css": ".transcript-header { font-size: 18px; font-weight: bold; }",
				"custom_format": 1,
				"default_print_language": "en",
				"disabled": 0,
				"doc_type": "Education Official Transcript",
				"doctype": "Print Format",
				"font": "Default",
				"font_size": 12,
				"format_data": '[{"fieldname": "print_heading", "fieldtype": "HTML", "options": "<h2>Official Transcript</h2>"}]',
				"html": '<div class="transcript-header">Official Academic Transcript</div><p>Student: {{ doc.student }}</p><p>CGPA: {{ doc.cgpa }}</p><p>Credits: {{ doc.total_credits }}</p><p>Issue Date: {{ doc.issue_date }}</p>',
				"line_breaks": 0,
				"margin_bottom": 15,
				"margin_left": 15,
				"margin_right": 15,
				"margin_top": 15,
				"module": "Omnexa Education",
				"name": "Education Official Transcript",
				"print_format_builder": 0,
				"print_format_type": "Jinja",
				"raw_printing": 0,
				"show_section_headings": 0,
				"standard": "Yes",
			},
			indent="\t",
		)
		+ "\n"
	)
	(path / "__init__.py").write_text("")


def main() -> None:
	for folder, page_name, title in PAGES:
		_page(folder, page_name, title, "Global SIS Wave 2+3 portal")
	for folder, ref, title in REPORTS:
		_report(folder, ref, title)
	_print_format()
	print(f"Scaffolded {len(PAGES)} pages, {len(REPORTS)} reports, 1 print format")


if __name__ == "__main__":
	main()
