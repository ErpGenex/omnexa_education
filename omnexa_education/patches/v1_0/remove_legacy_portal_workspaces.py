# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Remove portal Workspaces whose slugs conflict with desk Pages."""


def execute():
	from omnexa_education.portal_guard import ensure_education_workspace_portal_roles, remove_legacy_portal_workspaces

	removed = remove_legacy_portal_workspaces()
	ensure_education_workspace_portal_roles()
	return {"legacy_removed": removed}
