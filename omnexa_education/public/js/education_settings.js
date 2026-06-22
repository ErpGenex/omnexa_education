frappe.ui.form.on("Education Settings", {
	refresh(frm) {
		if (!frm.doc.enable_laravel_tlms) return;
		frm.add_custom_button(__("Test Laravel Connection"), () => {
			frappe.call({
				method: "omnexa_education.omnexa_education.doctype.education_settings.education_settings.test_laravel_connection",
				freeze: true,
				callback(r) {
					const res = r.message || {};
					if (res.ok) {
						frappe.show_alert({
							message: __("Laravel connection OK: {0}", [res.message || "pong"]),
							indicator: "green",
						});
						frm.reload_doc();
					} else {
						frappe.msgprint({
							title: __("Connection Failed"),
							indicator: "red",
							message: res.error || __("Unknown error"),
						});
					}
				},
			});
		}).addClass("btn-primary");
		frm.add_custom_button(__("Open Laravel Integration Desk"), () => {
			frappe.set_route("education-laravel-integration");
		});
	},
});
