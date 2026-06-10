frappe.pages["education-teacher-gradebook"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({ parent: wrapper, title: __("Education Teacher Gradebook"), single_column: true });
	$(page.body).html(`<div class="p-3"><p class="text-muted">${__("Wave 1 desk portal")}</p></div>`);
};
