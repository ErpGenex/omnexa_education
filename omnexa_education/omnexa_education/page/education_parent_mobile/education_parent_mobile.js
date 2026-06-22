frappe.pages["education-parent-mobile"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const $mount = OJ.mountDeskPage(wrapper, __("Parent Portal"));
		const $body = $('<div></div>');
		const $shell = OJ.shell({
			title: OJ.t("بوابة ولي الأمر", "Parent Portal"),
			subtitle: OJ.t("ErpGenEx — EduSphere", "ErpGenEx — EduSphere"),
			role: OJ.t("ولي أمر", "Parent"),
			brandLogoUrl: OJ.educationLogo,
			sidebarRole: "parent",
			currentPage: "education-parent-mobile",
			bodyEl: $body,
			homeRoute: "/app/education-workcenter",
		});
		$mount.empty().append($shell);
		OJ.call("omnexa_education.api.journey_role_desks.get_parent_portal_dashboard")
			.then((data) => {
				$body.empty();
				if (!data.student) {
					$body.html(`<p class="oj-muted">${OJ.t("اربط بريد ولي الأمر بسجل الطالب", "Link guardian email on student record")}</p>`);
					return;
				}
				$body.append(`<h4>${OJ.esc(data.student_name || data.student)}</h4>`);
				$body.append(OJ.linkGrid([
					{ label: OJ.t("الرسوم والفواتير", "Fees & Invoices"), icon: "💳", route: "List/Sales Invoice" },
					{ label: OJ.t("الدرجات", "Grades"), icon: "📝", route: "List/Education Assessment Result" },
					{ label: OJ.t("الحضور", "Attendance"), icon: "✅", route: "List/Education Attendance Session" },
				]));
				if (data.invoices && data.invoices.length) {
					$body.append(`<h4 class="oj-section-title">${OJ.t("آخر الفواتير", "Recent Invoices")}</h4>`);
					$body.append(OJ.dataTable(
						[
							{ field: "name", label: OJ.t("الفاتورة", "Invoice") },
							{ field: "grand_total", label: OJ.t("الإجمالي", "Total") },
							{ field: "outstanding_amount", label: OJ.t("المتبقي", "Outstanding") },
						],
						data.invoices
					));
				}
			})
			.catch((e) => OJ.showCallError(e));
	});
};
