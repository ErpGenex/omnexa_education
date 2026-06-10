import frappe


def execute(filters=None):
	columns = [
		{"label": "Name", "fieldname": "name", "fieldtype": "Data", "width": 180},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
	]
	data = frappe.get_all("Education Academic Standing", fields=["name"], limit=100)
	for row in data:
		row["status"] = "OK"
	return columns, data
