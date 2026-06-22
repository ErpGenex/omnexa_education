frappe.pages["education-teacher-gradebook"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const { company, branch } = OJ.resolveCompanyBranch();
		const $mount = OJ.mountDeskPage(wrapper, __("Teacher Gradebook"));
		const $body = $('<div></div>');
		$body.append(OJ.linkGrid([
			{ label: OJ.t("خطط التقييم", "Assessment Plans"), icon: "📋", route: "List/Education Assessment Plan" },
			{ label: OJ.t("نتائج التقييم", "Assessment Results"), icon: "📝", route: "List/Education Assessment Result" },
			{ label: OJ.t("الجدول", "Timetable"), icon: "📅", route: "/app/education-timetable-board" },
			{ label: OJ.t("الحضور", "Attendance"), icon: "✅", route: "List/Education Attendance Session" },
		]));
		const $shell = OJ.shell({
			title: OJ.t("سجل المعلّم", "Teacher Gradebook"),
			subtitle: OJ.t("ErpGenEx — EduSphere", "ErpGenEx — EduSphere"),
			role: OJ.t("معلّم", "Teacher"),
			brandLogoUrl: OJ.educationLogo,
			kpis: [
				{ value: "…", label: OJ.t("المعلّمون", "Teachers") },
				{ value: "…", label: OJ.t("الشعب", "Sections") },
			],
			sidebarRole: "teacher",
			currentPage: "education-teacher-gradebook",
			bodyEl: $body,
			homeRoute: "/app/education-workcenter",
		});
		$mount.empty().append($shell);
		OJ.call("omnexa_education.api.journey_role_desks.get_teacher_dashboard", { company, branch })
			.then((data) => {
				if (data.laravel_enabled) {
					$body.append(`<p class="oj-muted">${OJ.t("التدريس والتعلّم عبر Laravel TLMS", "Teaching & learning via Laravel TLMS")}</p>`);
				}
				$shell.find(".oj-kpi-card").eq(0).find(".oj-kpi-value").text(data.teachers ?? "0");
				$shell.find(".oj-kpi-card").eq(1).find(".oj-kpi-value").text(data.sections ?? "0");
			})
			.catch((e) => OJ.showCallError(e));
	});
};
