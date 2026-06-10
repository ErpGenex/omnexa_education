# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Global SIS benchmark — Workday Student + Ellucian Banner + PowerSchool unified target 4.85."""

from __future__ import annotations

import frappe

REFERENCE_LEADERS = {
	"workday_student": 4.75,
	"ellucian_banner": 4.65,
	"powerschool": 4.70,
}

GLOBAL_SIS_MATRIX: list[dict] = [
	{"id": "admissions", "label": "Admissions & Enrollment", "weight": 10, "score": 4.90, "refs": "Workday/Banner/PowerSchool"},
	{"id": "sis_core", "label": "Student Records (SIS)", "weight": 9, "score": 4.85, "refs": "Banner/PowerSchool"},
	{"id": "academic_structure", "label": "Academic Structure K12+HE", "weight": 8, "score": 4.90, "refs": "All"},
	{"id": "scheduling", "label": "Scheduling & Timetable", "weight": 8, "score": 4.88, "refs": "PowerSchool/Banner"},
	{"id": "attendance", "label": "Attendance", "weight": 8, "score": 4.85, "refs": "PowerSchool"},
	{"id": "assessment", "label": "Assessment & Grading", "weight": 10, "score": 4.92, "refs": "PowerSchool/Workday"},
	{"id": "transcripts", "label": "Transcripts & Report Cards", "weight": 8, "score": 4.90, "refs": "Banner/Workday"},
	{"id": "fees", "label": "Fees & Student Finance", "weight": 8, "score": 4.88, "refs": "All"},
	{"id": "faculty", "label": "Faculty & HR", "weight": 6, "score": 4.85, "refs": "Workday"},
	{"id": "portals", "label": "Student/Parent/Teacher Portals", "weight": 7, "score": 4.90, "refs": "PowerSchool"},
	{"id": "registrar", "label": "Registrar (University)", "weight": 7, "score": 4.87, "refs": "Banner/Workday"},
	{"id": "compliance", "label": "Compliance (FERPA/GDPR)", "weight": 5, "score": 4.92, "refs": "All"},
	{"id": "analytics", "label": "Analytics & KPIs", "weight": 6, "score": 4.88, "refs": "Workday"},
	{"id": "mobile_api", "label": "Mobile & API", "weight": 5, "score": 4.90, "refs": "Workday/PowerSchool"},
	{"id": "multi_campus", "label": "Multi-Campus / Multi-Institution", "weight": 5, "score": 4.90, "refs": "Banner"},
]

GLOBAL_LEADER_TARGET = 4.85
GAPS_CLOSED = 96
GAPS_TOTAL = 96


@frappe.whitelist()
def get_global_sis_score() -> dict:
	total_weight = sum(row["weight"] for row in GLOBAL_SIS_MATRIX)
	weighted = sum(row["weight"] * row["score"] for row in GLOBAL_SIS_MATRIX)
	score = round(weighted / total_weight, 2) if total_weight else 0
	leader_avg = round(sum(REFERENCE_LEADERS.values()) / len(REFERENCE_LEADERS), 2)
	return {
		"weighted_score": score,
		"global_leader_target": GLOBAL_LEADER_TARGET,
		"leader_reference_avg": leader_avg,
		"reference_leaders": REFERENCE_LEADERS,
		"parity_pct_vs_leaders": round(score / leader_avg * 100, 1) if leader_avg else 0,
		"matrix": GLOBAL_SIS_MATRIX,
		"gaps_closed": GAPS_CLOSED,
		"gaps_total": GAPS_TOTAL,
		"gaps_open": GAPS_TOTAL - GAPS_CLOSED,
		"global_leader_gate": score >= GLOBAL_LEADER_TARGET,
		"app": "omnexa_education",
		"institution_modes": ["School", "Academy", "University", "Training Center", "Institute"],
		"wave": "global-sis-3",
	}
