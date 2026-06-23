frappe.pages["education-timetable-board"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const $mount = OJ.mountDeskPage(wrapper, __("Timetable Board"));
		const $body = $('<div></div>');
		const roles = (frappe.boot && frappe.boot.user && frappe.boot.user.roles) || [];
		const portalOnly =
			(roles.includes("Education Student Portal") || roles.includes("Education Parent Portal")) &&
			!roles.some((r) => ["System Manager", "Education Manager", "Education User", "Teacher"].includes(r));
		const links = portalOnly
			? [{ label: OJ.t("جدول الحصص", "Timetable Entries"), icon: "📅", route: "List/Education Timetable Entry" }]
			: [
					{ label: OJ.t("جدول الحصص", "Timetable Entries"), icon: "📅", route: "List/Education Timetable Entry" },
					{ label: OJ.t("قوالب الجدول", "Templates"), icon: "📐", route: "List/Education Timetable Template" },
					{ label: OJ.t("ربط Laravel", "Laravel TLMS"), icon: "🔗", route: "/app/education-laravel-integration" },
				];
		$body.append(OJ.linkGrid(links));
		$mount.empty().append(OJ.shell({
			title: OJ.t("لوحة الجداول", "Timetable Board"),
			subtitle: OJ.t("ErpGenEx — EduSphere", "ErpGenEx — EduSphere"),
			role: OJ.t("معلّم", "Teacher"),
			brandLogoUrl: OJ.educationLogo,
			sidebarRole: "teacher",
			currentPage: "education-timetable-board",
			bodyEl: $body,
			homeRoute: "/app/education-workcenter",
		}));
	});
};
