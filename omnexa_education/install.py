import frappe


SUPPORTED_FRAPPE_MAJOR = 15


def enforce_supported_frappe_version():
	"""Fail fast when running on unsupported Frappe major versions."""
	version_text = (getattr(frappe, "__version__", "") or "").strip()
	if not version_text:
		return

	major_token = version_text.split(".", 1)[0]
	try:
		major = int(major_token)
	except ValueError:
		return

	if major != SUPPORTED_FRAPPE_MAJOR:
		frappe.throw(
			f"Unsupported Frappe version '{version_text}' for omnexa_education. "
			"Supported range is >=15.0,<16.0.",
			frappe.ValidationError,
		)


def after_migrate():
	try:
		from omnexa_education.workspace.education_workspace import sync_education_workspace_menu

		sync_education_workspace_menu(save=True)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Omnexa Education: workspace sync failed")

	try:
		from omnexa_education.patches.v1_0.sync_education_portal_access import execute as sync_portal_access

		sync_portal_access()
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Omnexa Education: portal access sync failed")

	try:
		from omnexa_education.patches.v1_0.sync_education_report_roles import execute as sync_report_roles

		sync_report_roles()
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Omnexa Education: report role sync failed")

	try:
		from omnexa_education.api.education_role_demo import ensure_education_roles, sync_journey_page_roles

		ensure_education_roles()
		sync_journey_page_roles()
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Omnexa Education: role sync failed")
