frappe.pages["education-admissions-portal"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const { company, branch } = OJ.resolveCompanyBranch();
		const $mount = OJ.mountDeskPage(wrapper, __("Admissions Portal"));
		const $body = $('<div></div>');
		$body.append(OJ.linkGrid([
			{ label: OJ.t("طلبات القبول", "Applications"), icon: "📋", route: "List/Education Admission Application" },
			{ label: OJ.t("قائمة الانتظار", "Waitlist"), icon: "⏳", route: "List/Education Waitlist Pool" },
			{ label: OJ.t("القبول الإلكتروني", "Online Applications"), icon: "🌐", route: "List/Education Online Application" },
			{ label: OJ.t("رسوم القبول", "Admission Fees"), icon: "💳", route: "List/Education Fee Item" },
		]));
		const $shell = OJ.shell({
			title: OJ.t("بوابة القبول", "Admissions Portal"),
			subtitle: OJ.t("ErpGenEx — EduSphere", "ErpGenEx — EduSphere"),
			role: OJ.t("مسؤول القبول", "Admissions Officer"),
			brandLogoUrl: OJ.educationLogo,
			kpis: [
				{ value: "…", label: OJ.t("الطلبات", "Applications") },
				{ value: "…", label: OJ.t("انتظار", "Waitlist") },
			],
			sidebarRole: "admissions",
			currentPage: "education-admissions-portal",
			bodyEl: $body,
			homeRoute: "/app/education-workcenter",
		});
		$mount.empty().append($shell);
		OJ.call("omnexa_education.api.journey_role_desks.get_admissions_dashboard", { company, branch })
			.then((data) => {
				$shell.find(".oj-kpi-card").eq(0).find(".oj-kpi-value").text(data.applications ?? "0");
				$shell.find(".oj-kpi-card").eq(1).find(".oj-kpi-value").text(data.waitlist ?? "0");
			})
			.catch((e) => OJ.showCallError(e));
	});
};
