# Copyright (c) 2026, Omnexa
import frappe
from frappe import _

def execute(filters=None):
	filters = frappe._dict(filters or {})
	return _columns(), []

def _columns():
	return [{'label': _('Status'), 'fieldname': 'status', 'fieldtype': 'Data', 'width': 140}]
