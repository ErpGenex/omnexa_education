# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe.model.document import Document


class EducationSettings(Document):
	pass


@frappe.whitelist()
def test_laravel_connection() -> dict:
	from omnexa_education.api.laravel_client import ping

	return ping()
