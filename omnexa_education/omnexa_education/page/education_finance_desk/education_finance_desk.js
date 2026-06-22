frappe.pages["education-finance-desk"].on_page_load = function (wrapper) {
	const OJ = window.OmnexaJourney;
	if (!OJ || !OJ.mountDeskPage) return;
	const { company, branch } = OJ.resolveCompanyBranch();
	const $mount = OJ.mountDeskPage(wrapper, __("Education Finance Desk"));

	async function render() {
		const data = await OJ.call("omnexa_education.api.journey_role_desks.get_finance_dashboard", { company, branch });
		const kpis = [
			{ value: data.total_students, label: OJ.t("الطلاب", "Students") },
			{ value: data.active_portal, label: OJ.t("حسابات نشطة", "Active Accounts") },
			{ value: data.financial_hold, label: OJ.t("حجز مالي", "Financial Hold") },
			{ value: data.overdue_candidates, label: OJ.t("متأخرون", "Overdue") },
			{ value: data.outstanding_fees, label: OJ.t("مستحقات", "Outstanding") },
		];
		const $body = $('<div class="education-finance-desk"></div>');
		$body.append(`<h4 class="oj-section-title">${OJ.t("💰 الشؤون المالية والحسابات", "Fees & Student Accounts")}</h4>`);
		$body.append(
			OJ.linkGrid([
				{ label: OJ.t("الطلاب", "Students"), icon: "🎓", route: "List/Education Student" },
				{ label: OJ.t("فواتير الرسوم", "Fee Invoices"), icon: "🧾", route: "List/Sales Invoice" },
				{ label: OJ.t("دورات الفوترة", "Billing Cycles"), icon: "🔄", route: "List/Education Billing Cycle" },
				{ label: OJ.t("سجل الوصول", "Access Log"), icon: "🔒", route: "List/Education Account Access Log" },
				{ label: OJ.t("ربط Laravel", "Laravel Integration"), icon: "🔗", route: "/app/education-laravel-integration" },
				{ label: OJ.t("إعدادات التعليم", "Education Settings"), icon: "⚙️", route: "Form/Education Settings/Education Settings" },
			])
		);
		$body.append(`<h4 class="oj-section-title" style="margin-top:20px">${OJ.t("طلاب متأخرون", "Overdue Students")}</h4>`);
		$body.append(
			OJ.dataTable(
				[
					{ field: "student_name", label: OJ.t("الطالب", "Student") },
					{ field: "outstanding", label: OJ.t("المستحق", "Outstanding") },
					{ field: "oldest_due", label: OJ.t("أقدم استحقاق", "Oldest Due") },
				],
				data.overdue_students || []
			)
		);
		const $actions = $(`<div class="oj-actions" style="margin-top:16px"></div>`);
		const $bulk = $(`<button type="button" class="btn btn-primary">${OJ.t("إيقاف المتأخرين", "Suspend Overdue")}</button>`);
		$bulk.on("click", async () => {
			await OJ.call("omnexa_education.api.student_account_lifecycle.bulk_suspend_overdue", { company, branch });
			frappe.show_alert({ message: OJ.t("تم التحديث", "Updated"), indicator: "green" });
			render();
		});
		$actions.append($bulk);
		$body.append($actions);
		const $shell = OJ.shell({
			title: OJ.t("مركز الشؤون المالية", "Finance Workcenter"),
			subtitle: OJ.t("التحكم في حسابات الطلاب والرسوم", "Student account & fee control"),
			role: OJ.t("مسؤول مالي", "Finance Officer"),
			brandLogoUrl: OJ.educationLogo,
			kpis,
			sidebar: OJ.defaultSidebar("finance", "/app/education-finance-desk"),
			bodyEl: $body,
			currentPage: "education-finance-desk",
		});
		$mount.empty().append($shell);
		$shell.find(".oj-sidebar-item[data-nav-route]").off("click").on("click", function (e) {
			e.preventDefault();
			OJ.navigateRoute($(this).attr("data-nav-route"));
		});
	}
	render().catch((err) => OJ.showCallError(err));
};
