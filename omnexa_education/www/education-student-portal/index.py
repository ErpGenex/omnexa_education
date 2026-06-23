# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from omnexa_education.api.education_portal_redirect import redirect_to_desk


def get_context(context):
	redirect_to_desk("education-student-portal")
