app_name = "omnexa_education"
app_title = "ErpGenEx — Education"
app_publisher = "ErpGenEx"
app_description = "Education vertical"
app_email = "dev@erpgenex.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["omnexa_core", "omnexa_accounting"]

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "omnexa_education",
		"logo": "/assets/omnexa_education/logo.png",
		"title": "EduSphere",
		"route": "/app/education-workcenter",
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
	"/assets/omnexa_education/css/education-rtl.css",
	"/assets/omnexa_education/css/omnexa-journey.css",
]
app_include_js = [
	"/assets/omnexa_education/js/omnexa-journey.js",
	"/assets/omnexa_education/js/education-journey-kit.js",
	"/assets/omnexa_education/js/education-portal-boot.js",
	"/assets/omnexa_education/js/education-portal-factory.js",
]

# Re-apply education shell after other vertical kits on portal pages
page_js = {
	"education-workcenter": "public/js/education-journey-kit.js",
	"education-finance-desk": "public/js/education-journey-kit.js",
	"education-admissions-portal": "public/js/education-journey-kit.js",
	"education-registrar-desk": "public/js/education-journey-kit.js",
	"education-laravel-integration": "public/js/education-journey-kit.js",
	"education-teacher-gradebook": "public/js/education-journey-kit.js",
	"education-student-portal": "public/js/education-journey-kit.js",
	"education-parent-mobile": "public/js/education-journey-kit.js",
	"education-timetable-board": "public/js/education-journey-kit.js",
	"education-executive-dashboard": "public/js/education-journey-kit.js",
	"education-analytics-dashboard": "public/js/education-journey-kit.js",
	"education-graduation-desk": "public/js/education-journey-kit.js",
	"education-alumni-desk": "public/js/education-journey-kit.js",
	"education-qa-desk": "public/js/education-journey-kit.js",
}

# Public website — online application entry
website_route_rules = [
	{"from_route": "/education/apply", "to_route": "education/apply"},
]

web_include_css = [
	"/assets/omnexa_education/css/education-rtl.css",
	"/assets/omnexa_education/css/omnexa-journey.css",
]

# include js, css files in header of web template
# web_include_js = "/assets/omnexa_education/js/omnexa_education.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "omnexa_education/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Education Settings": "public/js/education_settings.js",
	"Education Student": "public/js/education_student.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "omnexa_education/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
role_home_page = {
	"Education Manager": "education-executive-dashboard",
	"Education User": "education-admissions-portal",
	"Education Finance Officer": "education-finance-desk",
	"Education Student Portal": "education-student-portal",
	"Education Parent Portal": "education-parent-mobile",
	"Teacher": "education-teacher-gradebook",
	"Accounts User": "education-finance-desk",
	"Accounts Manager": "education-finance-desk",
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "omnexa_education.utils.jinja_methods",
# 	"filters": "omnexa_education.utils.jinja_filters"
# }

# Installation
# ------------

before_install = "omnexa_education.install.enforce_supported_frappe_version"
before_migrate = "omnexa_education.install.enforce_supported_frappe_version"
after_migrate = "omnexa_education.install.after_migrate"

# Uninstallation
# ------------

# before_uninstall = "omnexa_education.uninstall.before_uninstall"
# after_uninstall = "omnexa_education.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "omnexa_education.utils.before_app_install"
# after_app_install = "omnexa_education.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "omnexa_education.utils.before_app_uninstall"
# after_app_uninstall = "omnexa_education.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "omnexa_education.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Education Institution": "omnexa_education.permissions.education_institution_query_conditions",
	"Education Campus": "omnexa_education.permissions.education_campus_query_conditions",
	"Education Department": "omnexa_education.permissions.education_department_query_conditions",
	"Education Curriculum": "omnexa_education.permissions.education_curriculum_query_conditions",
	"Education Academic Year": "omnexa_education.permissions.education_academic_year_query_conditions",
	"Education Term": "omnexa_education.permissions.education_term_query_conditions",
	"Education Grade Level": "omnexa_education.permissions.education_grade_level_query_conditions",
	"Education Section": "omnexa_education.permissions.education_section_query_conditions",
	"Education Subject": "omnexa_education.permissions.education_subject_query_conditions",
	"Education Student": "omnexa_education.permissions.education_student_query_conditions",
	"Education Fee Item": "omnexa_education.permissions.education_fee_item_query_conditions",
	"Education Billing Invoice": "omnexa_education.permissions.education_billing_invoice_query_conditions",
	"Education Fee Plan": "omnexa_education.permissions.education_fee_plan_query_conditions",
	"Education Discount Rule": "omnexa_education.permissions.education_discount_rule_query_conditions",
	"Education Late Fee Rule": "omnexa_education.permissions.education_late_fee_rule_query_conditions",
	"Education Billing Cycle": "omnexa_education.permissions.education_billing_cycle_query_conditions",
	"Education Teacher": "omnexa_education.permissions.education_teacher_query_conditions",
	"Education Program": "omnexa_education.permissions.education_program_query_conditions",
	"Education Course": "omnexa_education.permissions.education_course_query_conditions",
	"Education Room": "omnexa_education.permissions.education_room_query_conditions",
	"Education Admission Application": "omnexa_education.permissions.education_admission_application_query_conditions",
	"Education Student Enrollment": "omnexa_education.permissions.education_student_enrollment_query_conditions",
	"Education Course Enrollment": "omnexa_education.permissions.education_course_enrollment_query_conditions",
	"Education Teacher Assignment": "omnexa_education.permissions.education_teacher_assignment_query_conditions",
	"Education Timetable Entry": "omnexa_education.permissions.education_timetable_entry_query_conditions",
	"Education Attendance Session": "omnexa_education.permissions.education_attendance_session_query_conditions",
	"Education Assessment Plan": "omnexa_education.permissions.education_assessment_plan_query_conditions",
	"Education Assessment Result": "omnexa_education.permissions.education_assessment_result_query_conditions",
	"Education Report Card": "omnexa_education.permissions.education_report_card_query_conditions",
	"Education Transcript Request": "omnexa_education.permissions.education_transcript_request_query_conditions",
}
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Education Institution": {
		"before_validate": "omnexa_education.permissions.populate_company_branch_from_user_context",
	},
	"Education Campus": {
		"before_validate": "omnexa_education.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_education.permissions.enforce_branch_access_for_doc",
	},
	"Education Department": {
		"before_validate": "omnexa_education.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_education.permissions.enforce_branch_access_for_doc",
	},
	"Education Section": {
		"before_validate": "omnexa_education.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_education.permissions.enforce_branch_access_for_doc",
		"on_update": "omnexa_education.api.laravel_doc_events.on_section_update",
	},
	"Education Course Enrollment": {
		"on_submit": "omnexa_education.api.laravel_doc_events.on_course_enrollment_submit",
	},
	"Education Program": {
		"on_update": "omnexa_education.api.laravel_doc_events.on_program_update",
	},
	"Education Student": {
		"before_validate": "omnexa_education.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_education.permissions.enforce_branch_access_for_doc",
	},
	"Payment Entry": {
		"on_submit": "omnexa_education.financial_hold.on_payment_entry_submit",
	},
	"Sales Invoice": {
		"on_submit": "omnexa_education.financial_hold.on_sales_invoice_update",
		"on_cancel": "omnexa_education.financial_hold.on_sales_invoice_update",
	},
	"Education Billing Invoice": {
		"before_validate": "omnexa_education.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_education.permissions.enforce_branch_access_for_doc",
	},
	"Education Fee Plan": {
		"before_validate": "omnexa_education.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_education.permissions.enforce_branch_access_for_doc",
	},
	"Education Discount Rule": {
		"before_validate": "omnexa_education.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_education.permissions.enforce_branch_access_for_doc",
	},
	"Education Late Fee Rule": {
		"before_validate": "omnexa_education.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_education.permissions.enforce_branch_access_for_doc",
	},
	"Education Billing Cycle": {
		"before_validate": "omnexa_education.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_education.permissions.enforce_branch_access_for_doc",
	},
	"Education Teacher": {
		"before_validate": "omnexa_education.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_education.permissions.enforce_branch_access_for_doc",
	},
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"omnexa_education.financial_hold.run_daily_financial_hold_scan",
	],
	"hourly": [
		"omnexa_education.api.laravel_client.process_sync_queue",
	],
}

# Testing
# -------

# before_tests = "omnexa_education.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "omnexa_education.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "omnexa_education.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
before_request = ["omnexa_education.license_gate.before_request"]
# after_request = ["omnexa_education.utils.after_request"]

# Job Events
# ----------
# before_job = ["omnexa_education.utils.before_job"]
# after_job = ["omnexa_education.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"omnexa_education.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

