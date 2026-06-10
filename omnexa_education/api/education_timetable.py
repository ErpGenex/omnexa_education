# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Auto timetable generator — sections, teachers, rooms."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import getdate


@frappe.whitelist()
def generate_timetable(
	section: str,
	academic_year: str,
	term: str,
	template: str | None = None,
	weekdays: str | None = None,
) -> dict:
	if not (section and academic_year and term):
		frappe.throw(_("section, academic_year, and term are required"))
	section_doc = frappe.get_doc("Education Section", section)
	assignments = frappe.get_all(
		"Education Teacher Assignment",
		filters={"section": section, "academic_year": academic_year, "term": term},
		fields=["teacher", "subject", "name"],
	)
	if not assignments:
		frappe.throw(_("No teacher assignments found for this section"))
	periods = 8
	if template and frappe.db.exists("Education Timetable Template", template):
		periods = int(frappe.db.get_value("Education Timetable Template", template, "periods_per_day") or 8)
		if not weekdays:
			weekdays = frappe.db.get_value("Education Timetable Template", template, "weekdays")
	day_list = [d.strip() for d in (weekdays or "Sunday,Monday,Tuesday,Wednesday,Thursday").split(",") if d.strip()]
	rooms = frappe.get_all(
		"Education Room",
		filters={"institution": section_doc.institution},
		pluck="name",
		limit=periods,
	)
	created = []
	slot = 0
	for assign in assignments:
		day = day_list[slot % len(day_list)]
		period = (slot % periods) + 1
		room = rooms[slot % len(rooms)] if rooms else None
		entry = frappe.get_doc(
			{
				"doctype": "Education Timetable Entry",
				"section": section,
				"academic_year": academic_year,
				"term": term,
				"subject": assign.subject,
				"teacher": assign.teacher,
				"weekday": day,
				"period_number": period,
				"room": room,
				"institution": section_doc.institution,
				"company": section_doc.company,
				"branch": section_doc.branch,
				"start_date": getdate(),
			}
		).insert(ignore_permissions=True)
		created.append(entry.name)
		slot += 1
	return {"section": section, "entries_created": len(created), "names": created}


@frappe.whitelist()
def get_section_timetable(section: str, academic_year: str | None = None) -> list[dict]:
	filters: dict = {"section": section}
	if academic_year:
		filters["academic_year"] = academic_year
	return frappe.get_all(
		"Education Timetable Entry",
		filters=filters,
		fields=[
			"name",
			"weekday",
			"period_number",
			"subject",
			"teacher",
			"room",
			"start_time",
			"end_time",
		],
		order_by="weekday asc, period_number asc",
	)
