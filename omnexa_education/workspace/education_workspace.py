# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Full Education workspace — K12 + University SIS menus (Workday/Banner/PowerSchool parity)."""

from __future__ import annotations

import json
import re

import frappe

from omnexa_core.omnexa_core.vertical_workspace_sync import drop_missing_workspace_dashboard_links

WorkspaceLink = tuple[str, str, str]  # link_type, link_to, label

# Curated sections (priority order) — anything missing is auto-added at the end.
WORKSPACE_SECTIONS: list[tuple[str, list[WorkspaceLink]]] = [
	(
		"✨ Omnexa Journey Experience",
		[
			("Page", "education-workcenter", "Education Workcenter"),
			("Page", "education-finance-desk", "Finance Workcenter"),
			("Page", "education-laravel-integration", "Laravel TLMS Integration"),
			("Page", "education-registrar-desk", "Registrar Desk"),
			("Page", "education-admissions-portal", "Admissions Portal"),
			("Page", "education-teacher-gradebook", "Teacher Gradebook"),
			("Page", "education-student-portal", "Student Portal"),
			("Page", "education-parent-mobile", "Parent Portal (PWA)"),
		],
	),
	(
		"📊 Dashboards & Portals",
		[
			("Page", "education-registrar-desk", "Registrar Desk"),
			("Page", "education-teacher-gradebook", "Teacher Gradebook"),
			("Page", "education-student-portal", "Student Portal"),
			("Page", "education-timetable-board", "Timetable Board"),
			("Page", "education-parent-mobile", "Parent Mobile (PWA)"),
			("Page", "education-admissions-portal", "Admissions Portal"),
			("Page", "education-analytics-dashboard", "Analytics Dashboard"),
			("Page", "education-executive-dashboard", "Executive Dashboard"),
		],
	),
	(
		"🏫 Institution Setup (All)",
		[
			("DocType", "Company", "Company"),
			("DocType", "Branch", "Branch"),
			("DocType", "Education Settings", "Education Settings"),
			("DocType", "Education Institution", "Institution"),
			("DocType", "Education Campus", "Campus"),
			("DocType", "Education Department", "Department"),
			("DocType", "Education Curriculum", "Curriculum"),
			("DocType", "Education Academic Year", "Academic Year"),
			("DocType", "Education Term", "Term"),
			("DocType", "Education Grade Level", "Grade Level"),
			("DocType", "Education Subject", "Subject"),
			("DocType", "Education Room", "Room"),
		],
	),
	(
		"🎓 University (Banner / Workday)",
		[
			("DocType", "Education Program", "Program"),
			("DocType", "Education Course", "Course"),
			("DocType", "Education Course Enrollment", "Course Enrollment"),
			("DocType", "Education Transcript Request", "Transcript Request"),
		],
	),
	(
		"🏫 K12 School (PowerSchool)",
		[
			("DocType", "Education Section", "Section / Homeroom"),
			("DocType", "Education Teacher Assignment", "Teacher Assignment"),
			("DocType", "Education Timetable Entry", "Timetable"),
			("DocType", "Education Attendance Session", "Attendance Session"),
		],
	),
	(
		"👨‍🎓 Admissions & Enrollment",
		[
			("DocType", "Education Admission Application", "Admission Application"),
			("DocType", "Education Online Application", "Online Application"),
			("DocType", "Education Waitlist Pool", "Waitlist Pool"),
			("DocType", "Education Lottery Run", "Lottery Run"),
			("DocType", "Education Student Enrollment", "Student Enrollment"),
			("DocType", "Education Student", "Student"),
			("DocType", "Customer", "Customer (ERP)"),
		],
	),
	(
		"👩‍🏫 Faculty",
		[("DocType", "Education Teacher", "Teacher"), ("DocType", "Employee", "Employee (HR)")],
	),
	(
		"📝 Assessment & Grades",
		[
			("DocType", "Education Assessment Plan", "Assessment Plan"),
			("DocType", "Education Assessment Result", "Assessment Result"),
			("DocType", "Education Grading Scale", "Grading Scale"),
			("DocType", "Education Academic Standing", "Academic Standing"),
			("DocType", "Education Report Card", "Report Card"),
			("DocType", "Education Official Transcript", "Official Transcript"),
		],
	),
	(
		"📅 Scheduling & Timetable",
		[
			("DocType", "Education Timetable Template", "Timetable Template"),
		],
	),
	(
		"🔒 Compliance & FERPA",
		[
			("DocType", "Education Ferpa Access Log", "FERPA Access Log"),
			("DocType", "Education Student Consent", "Student Consent"),
		],
	),
	(
		"📚 Library · Transport · Hostel",
		[
			("DocType", "Education Library Book", "Library Book"),
			("DocType", "Education Library Loan", "Library Loan"),
			("DocType", "Education Transport Route", "Transport Route"),
			("DocType", "Education Hostel Room", "Hostel Room"),
			("DocType", "Education Hostel Allocation", "Hostel Allocation"),
		],
	),
	(
		"🎯 Student Life & Alumni",
		[
			("DocType", "Education Discipline Incident", "Discipline Incident"),
			("DocType", "Education Credit Transfer", "Credit Transfer"),
			("DocType", "Education Alumni Record", "Alumni Record"),
			("DocType", "Education Scholarship", "Scholarship"),
			("DocType", "Education Scholarship Award", "Scholarship Award"),
			("DocType", "Education Announcement", "Announcement"),
		],
	),
	(
		"🔗 LMS · Mobile · Analytics",
		[
			("DocType", "Education Lms Course Link", "LMS Course Link"),
			("DocType", "Education Laravel Sync Queue", "Laravel Sync Queue"),
			("DocType", "Education Account Access Log", "Account Access Log"),
			("DocType", "Education Mobile Device Token", "Mobile Device Token"),
			("DocType", "Education Predictive Alert", "Predictive Alert"),
		],
	),
	(
		"💰 Fees & Finance",
		[
			("DocType", "Education Fee Item", "Fee Item"),
			("DocType", "Education Fee Plan", "Fee Plan"),
			("DocType", "Education Discount Rule", "Discount Rule"),
			("DocType", "Education Late Fee Rule", "Late Fee Rule"),
			("DocType", "Education Billing Cycle", "Billing Cycle"),
			("DocType", "Education Billing Invoice", "Billing Invoice"),
			("DocType", "Sales Invoice", "Sales Invoice"),
			("DocType", "Payment Entry", "Payment Entry"),
			("DocType", "Journal Entry", "Journal Entry"),
			("DocType", "Purchase Invoice", "Purchase Invoice"),
			("DocType", "Supplier", "Supplier"),
			("DocType", "Cost Center", "Cost Center"),
		],
	),
	(
		"👥 Administration",
		[("DocType", "User", "User"), ("DocType", "Role", "Role"), ("DocType", "Leave Policy", "Leave Policy")],
	),
]

REPORT_SECTIONS: list[tuple[str, list[WorkspaceLink]]] = [
	("📈 Reports · Enrollment & Admissions", []),
	("📈 Reports · Attendance & Academics", []),
	("📈 Reports · Billing & Finance", []),
	("📈 Reports · Operations", []),
]

_REPORT_BUCKETS: list[tuple[str, tuple[str, ...]]] = [
	("📈 Reports · Enrollment & Admissions", ("enrollment", "admission", "section utilization", "grade level")),
	("📈 Reports · Attendance & Academics", ("attendance", "grade", "assessment", "transcript")),
	("📈 Reports · Billing & Finance", ("fee", "billing", "revenue", "aging", "expense", "profitability")),
	("📈 Reports · Operations", ("branch", "campus", "teacher")),
]

_SHORTCUT_COLORS = ("Blue", "Green", "Orange", "Red", "Cyan", "Purple", "Teal", "Pink", "Yellow")


def _link_exists(link_type: str, link_to: str) -> bool:
	if link_type == "DocType":
		if not frappe.db.exists("DocType", link_to):
			return False
		meta = frappe.get_meta(link_to, cached=True)
		return bool(meta and not meta.istable)
	if link_type == "Page":
		return bool(frappe.db.exists("Page", link_to))
	if link_type == "Report":
		return bool(frappe.db.exists("Report", link_to))
	if link_type == "Dashboard":
		return bool(frappe.db.exists("Dashboard", link_to))
	return False


def _human_label(name: str) -> str:
	return name.replace("Education ", "").strip()


def _report_ref_doctype(report_name: str) -> str | None:
	return frappe.db.get_value("Report", report_name, "ref_doctype")


def _discover_education_doctypes(seen: set[tuple[str, str]]) -> list[WorkspaceLink]:
	out: list[WorkspaceLink] = []
	for name in frappe.get_all(
		"DocType",
		filters={"module": "Omnexa Education", "istable": 0},
		pluck="name",
		order_by="name",
	):
		key = ("DocType", name)
		if key in seen:
			continue
		if _link_exists("DocType", name):
			out.append(("DocType", name, _human_label(name)))
	return out


def _discover_education_pages(seen: set[tuple[str, str]]) -> list[WorkspaceLink]:
	out: list[WorkspaceLink] = []
	for name in frappe.get_all("Page", filters={"module": "Omnexa Education"}, pluck="name", order_by="name"):
		key = ("Page", name)
		if key in seen:
			continue
		label = name.replace("education-", "").replace("-", " ").title()
		out.append(("Page", name, label))
	return out


def _discover_education_reports(seen: set[tuple[str, str]]) -> list[WorkspaceLink]:
	out: list[WorkspaceLink] = []
	for name in frappe.get_all("Report", filters={"module": "Omnexa Education"}, pluck="name", order_by="name"):
		key = ("Report", name)
		if key in seen:
			continue
		out.append(("Report", name, _human_label(name)))
	return out


def _bucket_report(report_name: str) -> str:
	low = report_name.lower()
	for section, keywords in _REPORT_BUCKETS:
		if any(k in low for k in keywords):
			return section
	return "📈 Reports · Other"


def _build_report_sections(seen: set[tuple[str, str]]) -> list[tuple[str, list[WorkspaceLink]]]:
	buckets: dict[str, list[WorkspaceLink]] = {s: list(items) for s, items in REPORT_SECTIONS}
	buckets["📈 Reports · Other"] = []
	for name in frappe.get_all("Report", filters={"module": "Omnexa Education"}, pluck="name", order_by="name"):
		key = ("Report", name)
		if key in seen:
			continue
		section = _bucket_report(name)
		buckets.setdefault(section, []).append(("Report", name, _human_label(name)))
	return [(s, items) for s, items in buckets.items() if items]


def _row_from_link(link_type: str, link_to: str, label: str) -> dict:
	row = {"label": label, "type": "Link", "link_type": link_type, "link_to": link_to}
	if link_type == "Report":
		row["is_query_report"] = 1
		ref = _report_ref_doctype(link_to)
		if ref:
			row["report_ref_doctype"] = ref
	return row


def _build_link_rows() -> list[dict]:
	rows: list[dict] = []
	seen: set[tuple[str, str]] = set()

	def add_section(section_label: str, items: list[WorkspaceLink]) -> None:
		valid = [(t, to, label) for t, to, label in items if _link_exists(t, to)]
		if not valid:
			return
		rows.append({"label": section_label, "type": "Card Break", "link_type": "DocType"})
		for link_type, link_to, label in valid:
			key = (link_type, link_to)
			if key in seen:
				continue
			seen.add(key)
			rows.append(_row_from_link(link_type, link_to, label))

	for section_label, items in WORKSPACE_SECTIONS:
		add_section(section_label, items)

	# Auto: any education pages not yet listed
	extra_pages = _discover_education_pages(seen)
	if extra_pages:
		add_section("📱 Pages (auto)", extra_pages)

	# Auto: any education doctypes not yet listed
	extra_dt = _discover_education_doctypes(seen)
	if extra_dt:
		add_section("📁 Education DocTypes (auto)", extra_dt)

	# Reports — bucketed + full coverage
	for section_label, items in _build_report_sections(seen):
		add_section(section_label, items)

	return rows


def _build_shortcuts(link_rows: list[dict]) -> list[dict]:
	"""Workspace home shortcuts — one per link (pages & doctypes first)."""
	shortcuts: list[dict] = []
	idx = 0
	priority_types = ("Page", "DocType", "Report", "Dashboard")
	links = [r for r in link_rows if r.get("type") == "Link"]
	for lt in priority_types:
		for row in links:
			if row.get("link_type") != lt:
				continue
			entry = {
				"label": row["label"],
				"link_to": row["link_to"],
				"type": row["link_type"],
				"color": _SHORTCUT_COLORS[idx % len(_SHORTCUT_COLORS)],
			}
			if lt == "DocType":
				entry["doc_view"] = "List"
			if lt == "Report" and row.get("report_ref_doctype"):
				entry["report_ref_doctype"] = row["report_ref_doctype"]
			shortcuts.append(entry)
			idx += 1
	return shortcuts


def _onboarding_blocks(existing_content: str | None) -> list[dict]:
	if not existing_content:
		return []
	try:
		blocks = json.loads(existing_content)
	except json.JSONDecodeError:
		return []
	return [b for b in blocks if b.get("type") == "onboarding"]


def _build_content(link_rows: list[dict], ws) -> str:
	"""Rebuild workspace home layout — content blocks must reference shortcut labels."""
	content: list[dict] = []
	content.extend(_onboarding_blocks(ws.content))
	content.append(
		{
			"id": "education-title",
			"type": "header",
			"data": {"text": '<span class="h4"><b>Education</b></span>', "col": 12},
		}
	)

	section_idx = 0
	link_idx = 0
	for row in link_rows:
		if row.get("type") == "Card Break":
			if section_idx:
				content.append({"id": f"education-sp-{section_idx}", "type": "spacer", "data": {"col": 12}})
			content.append(
				{
					"id": f"education-sec-{section_idx}",
					"type": "header",
					"data": {"text": f'<span class="h5"><b>{row["label"]}</b></span>', "col": 12},
				}
			)
			section_idx += 1
			continue
		content.append(
			{
				"id": f"education-lnk-{link_idx}",
				"type": "shortcut",
				"data": {"shortcut_name": row["label"], "col": 4},
			}
		)
		link_idx += 1

	if ws.number_cards:
		content.append({"id": "education-kpi-sp", "type": "spacer", "data": {"col": 12}})
		content.append(
			{
				"id": "education-kpi-h",
				"type": "header",
				"data": {"text": '<span class="h5"><b>📊 KPIs</b></span>', "col": 12},
			}
		)
		for idx, nc in enumerate(ws.number_cards):
			content.append(
				{
					"id": f"education-nc-{idx}",
					"type": "number_card",
					"data": {"number_card_name": nc.number_card_name, "col": 4},
				}
			)

	if ws.charts:
		content.append({"id": "education-ch-sp", "type": "spacer", "data": {"col": 12}})
		content.append(
			{
				"id": "education-ch-h",
				"type": "header",
				"data": {"text": '<span class="h5"><b>📈 Charts</b></span>', "col": 12},
			}
		)
		for idx, ch in enumerate(ws.charts):
			content.append(
				{
					"id": f"education-ch-{idx}",
					"type": "chart",
					"data": {"chart_name": ch.label or ch.chart_name, "col": 4},
				}
			)

	return json.dumps(content, separators=(",", ":"))


def sync_education_workspace_menu(*, save: bool = True, rebuild: bool = True) -> dict:
	"""Rebuild Education workspace sidebar + home shortcuts (full catalog)."""
	stats = {"sections": 0, "links": 0, "shortcuts": 0}
	if not frappe.db.exists("Workspace", "Education"):
		return stats

	new_rows = _build_link_rows()
	link_rows = [r for r in new_rows if r.get("type") == "Link"]
	new_shortcuts = _build_shortcuts(new_rows)

	ws = frappe.get_doc("Workspace", "Education")
	if rebuild:
		ws.set("links", [])
		ws.set("shortcuts", [])

	for row in new_rows:
		if row["type"] == "Card Break":
			stats["sections"] += 1
		else:
			stats["links"] += 1
		ws.append("links", row)

	for sc in new_shortcuts:
		ws.append("shortcuts", sc)
	stats["shortcuts"] = len(new_shortcuts)

	drop_missing_workspace_dashboard_links(ws)
	ws.content = _build_content(new_rows, ws)
	stats["content_blocks"] = len(json.loads(ws.content))

	if save:
		ws.flags.ignore_permissions = True
		ws.save()
		frappe.clear_cache(doctype="Workspace")

	stats["total_links"] = len(link_rows)
	return stats


@frappe.whitelist()
def get_workspace_coverage() -> dict:
	rows = _build_link_rows()
	link_rows = [r for r in rows if r.get("type") == "Link"]
	dts = frappe.get_all("DocType", filters={"module": "Omnexa Education", "istable": 0}, pluck="name")
	catalogued_dt = {r["link_to"] for r in link_rows if r.get("link_type") == "DocType"}
	reports = frappe.get_all("Report", filters={"module": "Omnexa Education"}, pluck="name")
	catalogued_reports = {r["link_to"] for r in link_rows if r.get("link_type") == "Report"}
	return {
		"sections": len([r for r in rows if r.get("type") == "Card Break"]),
		"links_catalogued": len(link_rows),
		"pages": len([r for r in link_rows if r.get("link_type") == "Page"]),
		"doctypes": len([r for r in link_rows if r.get("link_type") == "DocType"]),
		"reports": len([r for r in link_rows if r.get("link_type") == "Report"]),
		"education_doctypes_total": len(dts),
		"education_doctypes_missing": sorted(set(dts) - catalogued_dt),
		"education_reports_total": len(reports),
		"education_reports_missing": sorted(set(reports) - catalogued_reports),
		"shortcuts_planned": len(_build_shortcuts(rows)),
	}
