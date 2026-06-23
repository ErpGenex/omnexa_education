# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Ensure portal page roles and student/parent read permissions exist."""

from __future__ import annotations


def execute():
	from omnexa_education.api.portal_access import ensure_full_portal_access

	return ensure_full_portal_access()
