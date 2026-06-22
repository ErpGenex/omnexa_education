frappe.pages["education-registrar-desk"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const { company, branch } = OJ.resolveCompanyBranch();
		const $mount = OJ.mountDeskPage(wrapper, __("Registrar Desk"));
		const $body = $('<div></div>');
		$body.append(OJ.linkGrid([
			{ label: OJ.t("الطلاب", "Students"), icon: "🎓", route: "List/Education Student" },
			{ label: OJ.t("التسجيل", "Enrollments"), icon: "📚", route: "List/Education Student Enrollment" },
			{ label: OJ.t("كشوف الدرجات", "Report Cards"), icon: "📄", route: "List/Education Report Card" },
			{ label: OJ.t("الشهادات", "Transcripts"), icon: "🎓", route: "List/Education Transcript Request" },
		]));

		const $shell = OJ.shell({
			title: OJ.t("مكتب القيد", "Registrar Desk"),
			subtitle: OJ.t("ErpGenEx — EduSphere", "ErpGenEx — EduSphere"),
			role: OJ.t("مسؤول القيد", "Registrar"),
			brandLogoUrl: OJ.educationLogo,
			kpis: [
				{ value: "…", label: OJ.t("طلاب نشطون", "Active Students") },
				{ value: "…", label: OJ.t("تسجيلات", "Enrollments") },
			],
			sidebarRole: "registrar",
			currentPage: "education-registrar-desk",
			bodyEl: $body,
			homeRoute: "/app/education-workcenter",
		});
		$mount.empty().append($shell);

		OJ.call("omnexa_education.api.journey_role_desks.get_registrar_dashboard", { company, branch })
			.then((data) => {
				$shell.find(".oj-kpi-card").eq(0).find(".oj-kpi-value").text(data.active_students ?? "0");
				$shell.find(".oj-kpi-card").eq(1).find(".oj-kpi-value").text(data.enrollments ?? "0");
			})
			.catch((e) => OJ.showCallError(e));
	});
};
