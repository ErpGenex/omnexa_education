# Copyright (c) 2026, Omnexa and contributors
# License: MIT

from omnexa_education.www.education_portal_redirect import redirect_to_desk


def get_context(context):
	redirect_to_desk("education-parent-mobile")
