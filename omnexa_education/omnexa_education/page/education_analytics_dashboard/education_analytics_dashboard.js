frappe.pages["education-analytics-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Education Analytics Dashboard"), single_column: true });
	$(page.body).html(`<div class="p-3"><p class="text-muted">${__("Global SIS Wave 2+3 portal")}</p></div>`);
};
