# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""High-volume demo seeding — colleges, year levels, bulk students, lifecycle samples."""

from __future__ import annotations

import frappe
from frappe.utils import now, nowdate

from omnexa_education.education_demo.institution_specs import (
	DEMO_ACADEMIC_YEARS,
	DEMO_MARKER,
	DEMO_STUDENTS_PER_YEAR,
	HE_YEAR_LABELS,
)


def _ensure_department(company: str, branch: str, campus: str, code: str, name: str) -> str:
	from omnexa_education.education_demo.education_demo_seed import _get_or_insert

	return _get_or_insert(
		"Education Department",
		{"company": company, "department_code": f"{DEMO_MARKER}-{code}"},
		{
			"department_code": f"{DEMO_MARKER}-{code}",
			"department_name": name,
			"company": company,
			"branch": branch,
			"campus": campus,
			"status": "Active",
		},
	)


def _ensure_he_year_levels(company: str, institution: str, curriculum: str, spec_code: str) -> list[str]:
	from omnexa_education.education_demo.education_demo_seed import _get_or_insert

	levels = []
	for seq, label in enumerate(HE_YEAR_LABELS, start=1):
		code = f"{DEMO_MARKER}-{spec_code}-Y{seq}"
		levels.append(
			_get_or_insert(
				"Education Grade Level",
				{"company": company, "institution": institution, "grade_code": code},
				{
					"grade_code": code,
					"grade_name": label,
					"company": company,
					"institution": institution,
					"curriculum": curriculum,
					"stage": "Higher Education",
					"sequence": seq,
					"status": "Active",
				},
			)
		)
	return levels


def _existing_student_count(company: str, institution: str, spec_code: str) -> int:
	return frappe.db.count(
		"Education Student",
		{
			"company": company,
			"institution": institution,
			"student_code": ["like", f"%{DEMO_MARKER}-{spec_code}-S%"],
		},
	)


def bulk_seed_students(
	company: str,
	branch: str,
	institution: str,
	campus: str,
	spec_code: str,
	total: int,
	*,
	grade_levels: list[str] | None = None,
	section: str | None = None,
	batch_size: int = 100,
) -> tuple[int, list[str]]:
	"""Insert students in batches; returns (created_count, sample_ids for assessments)."""
	if total <= 0:
		return 0, []

	existing = _existing_student_count(company, institution, spec_code)
	if existing >= total:
		return 0, []

	start_idx = existing + 1
	remaining = total - existing
	created = 0
	sample_ids: list[str] = []
	ts = now()
	owner = frappe.session.user or "Administrator"
	levels = grade_levels or []

	for batch_start in range(0, remaining, batch_size):
		batch_end = min(batch_start + batch_size, remaining)
		rows = []
		for offset in range(batch_start, batch_end):
			i = start_idx + offset
			student_code = f"{DEMO_MARKER}-{spec_code}-S{i:05d}"
			name = f"{company}-{student_code}"
			if frappe.db.exists("Education Student", name):
				continue
			year_idx = (i - 1) % max(len(levels), DEMO_ACADEMIC_YEARS)
			grade = levels[year_idx] if levels else None
			rows.append(
				{
					"name": name,
					"student_code": student_code,
					"student_name": f"Student {spec_code} {i}",
					"company": company,
					"branch": branch,
					"institution": institution,
					"campus": campus,
					"grade_level": grade,
					"section": section,
					"status": "Active",
					"account_access_status": "Active",
					"guardian_email": f"parent-{spec_code.lower()}-{i % 500}@demo.education",
					"guardian_name": "Demo Guardian",
					"creation": ts,
					"modified": ts,
					"owner": owner,
					"modified_by": owner,
					"docstatus": 0,
				}
			)
		if not rows:
			continue
		frappe.db.bulk_insert("Education Student", list(rows[0].keys()), [tuple(r.values()) for r in rows])
		created += len(rows)
		if len(sample_ids) < 50:
			sample_ids.extend([r["name"] for r in rows[: max(0, 50 - len(sample_ids))]])
		if created % 500 == 0:
			frappe.db.commit()
			frappe.publish_progress(min(99, int(created / remaining * 100)), title="Seeding students")

	frappe.db.commit()
	return created, sample_ids


def seed_college_students(
	company: str,
	branch: str,
	institution: str,
	campus: str,
	spec_code: str,
	college: dict,
	year_levels: list[str],
) -> tuple[int, list[str]]:
	"""500 students per college across 4 year levels (125 each)."""
	per_year = DEMO_STUDENTS_PER_YEAR
	college_code = college["code"]
	total = per_year * len(year_levels)
	return bulk_seed_students(
		company,
		branch,
		institution,
		campus,
		f"{spec_code}-{college_code}",
		total,
		grade_levels=year_levels,
	)


def seed_lifecycle_pipeline(
	company: str,
	branch: str,
	institution: str,
	year: str,
	spec_code: str,
	*,
	applications: int = 40,
) -> dict:
	"""Sample applications across admission lifecycle statuses."""
	from omnexa_education.education_demo.education_demo_seed import _get_or_insert

	statuses = ["Submitted", "Under Review", "Accepted", "Enrolled", "Rejected"]
	created = 0
	for i in range(applications):
		status = statuses[i % len(statuses)]
		applicant = f"Applicant {spec_code}-{i+1:03d}"
		_get_or_insert(
			"Education Admission Application",
			{"company": company, "institution": institution, "applicant_name": applicant},
			{
				"applicant_name": applicant,
				"institution": institution,
				"company": company,
				"branch": branch,
				"academic_year": year,
				"application_date": nowdate(),
				"status": status,
				"guardian_name": "Demo Applicant Guardian",
				"guardian_email": f"applicant-{spec_code.lower()}-{i+1}@demo.education",
			},
		)
		created += 1
	return {"applications": created}
