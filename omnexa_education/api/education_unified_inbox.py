# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Unified portal inbox — administrative, academic, and financial messages."""

from __future__ import annotations

import frappe
from frappe.utils import today


def _audience_match(audience: str, role: str) -> bool:
	if not audience or audience == "All":
		return True
	mapping = {
		"student": "Students",
		"parent": "Parents",
		"teacher": "Teachers",
	}
	return audience == mapping.get(role, audience)


@frappe.whitelist()
def get_unified_inbox(
	student: str | None = None,
	channel: str | None = None,
	limit: int = 30,
) -> dict:
	user = frappe.session.user
	role = "student"
	if frappe.db.exists("Education Student", {"user": user}):
		role = "student"
	elif frappe.db.exists("Education Student", {"guardian_email": user}):
		role = "parent"

	if not student and role == "student":
		student = frappe.db.get_value("Education Student", {"user": user}, "name")
	elif not student and role == "parent":
		student = frappe.db.get_value("Education Student", {"guardian_email": user}, "name")

	messages = []
	if frappe.db.exists("DocType", "Education Portal Message"):
		filters: dict = {}
		if student:
			filters["student"] = student
		if channel:
			filters["channel"] = channel
		rows = frappe.get_all(
			"Education Portal Message",
			filters=filters,
			fields=[
				"name",
				"title",
				"message",
				"channel",
				"source",
				"is_read",
				"creation",
				"student",
			],
			order_by="creation desc",
			limit=limit,
		)
		for row in rows:
			messages.append(
				{
					"id": row.name,
					"title": row.title,
					"body": row.message,
					"channel": row.channel or "Administrative",
					"source": row.source or "ErpGenEx",
					"is_read": bool(row.is_read),
					"date": row.creation,
					"type": "message",
				}
			)

	if frappe.db.exists("DocType", "Education Announcement"):
		ann_filters = {"publish_date": ["<=", today()]}
		if student:
			institution = frappe.db.get_value("Education Student", student, "institution")
			if institution:
				ann_filters["institution"] = institution
		announcements = frappe.get_all(
			"Education Announcement",
			filters=ann_filters,
			fields=["name", "title", "message", "audience", "portal_channel", "publish_date"],
			order_by="publish_date desc",
			limit=limit,
		)
		for ann in announcements:
			audience = ann.audience or "All"
			if not _audience_match(audience, role):
				continue
			ch = ann.portal_channel or "Administrative"
			if channel and ch != channel:
				continue
			messages.append(
				{
					"id": ann.name,
					"title": ann.title,
					"body": ann.message,
					"channel": ch,
					"source": "Announcement",
					"is_read": True,
					"date": ann.publish_date,
					"type": "announcement",
				}
			)

	messages.sort(key=lambda m: str(m.get("date") or ""), reverse=True)
	return {
		"student": student,
		"role": role,
		"messages": messages[:limit],
		"counts": {
			"total": len(messages),
			"unread": sum(1 for m in messages if not m.get("is_read")),
		},
	}


@frappe.whitelist()
def mark_message_read(message_id: str) -> dict:
	if not frappe.db.exists("Education Portal Message", message_id):
		return {"ok": False}
	frappe.db.set_value("Education Portal Message", message_id, "is_read", 1)
	return {"ok": True, "message_id": message_id}


def create_portal_message(
	title: str,
	message: str,
	channel: str = "Administrative",
	student: str | None = None,
	source: str = "ErpGenEx",
	**kwargs,
) -> str:
	if not frappe.db.exists("DocType", "Education Portal Message"):
		return ""
	student_doc = frappe.get_doc("Education Student", student) if student else None
	doc = frappe.get_doc(
		{
			"doctype": "Education Portal Message",
			"title": title,
			"message": message,
			"channel": channel,
			"source": source,
			"student": student,
			"institution": kwargs.get("institution") or (student_doc.institution if student_doc else None),
			"company": kwargs.get("company") or (student_doc.company if student_doc else None),
			"branch": kwargs.get("branch") or (student_doc.branch if student_doc else None),
			"guardian_email": kwargs.get("guardian_email") or (student_doc.guardian_email if student_doc else None),
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name

