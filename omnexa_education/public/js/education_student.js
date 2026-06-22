frappe.ui.form.on("Education Student", {
	refresh(frm) {
		if (frm.is_new()) return;
		const can_manage = frappe.user.has_role("Education Manager") || frappe.user.has_role("Accounts User") || frappe.user.has_role("System Manager");
		if (!can_manage) return;

		if (["Not Provisioned", "Provisioning", ""].includes(frm.doc.account_access_status)) {
			frm.add_custom_button(__("Provision Portal Account"), () => lifecycle_call(frm, "provision_student"));
		}
		if (["Active", "Financial Hold"].includes(frm.doc.account_access_status)) {
			frm.add_custom_button(__("Suspend Access"), () => {
				frappe.prompt(__("Reason"), (v) => lifecycle_call(frm, "suspend_student", { reason: v.value || "" }), __("Suspend"), __("Reason"));
			});
		}
		if (["Suspended", "Financial Hold"].includes(frm.doc.account_access_status)) {
			frm.add_custom_button(__("Resume Access"), () => lifecycle_call(frm, "resume_student"), __("Resume"));
		}
		if (frm.doc.account_access_status === "Active") {
			frm.add_custom_button(__("Sync Laravel Enrollments"), () => {
				frappe.call({
					method: "omnexa_education.api.education_lms.sync_all_laravel_enrollments",
					args: { student: frm.doc.name },
					callback(r) {
						frappe.show_alert({ message: __("Synced {0} links", [r.message.count || 0]), indicator: "green" });
					},
				});
			});
		}
	},
});

function lifecycle_call(frm, method, extra = {}) {
	frappe.call({
		method: `omnexa_education.api.student_account_lifecycle.${method}`,
		args: { student: frm.doc.name, ...extra },
		freeze: true,
		callback() {
			frm.reload_doc();
		},
	});
}
