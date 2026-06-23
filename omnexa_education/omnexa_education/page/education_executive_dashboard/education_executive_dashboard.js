frappe.pages["education-executive-dashboard"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const $mount = OJ.mountDeskPage(wrapper, __("Education Executive Dashboard"));

		async function render() {
			const [data, benchmark, demo] = await Promise.all([
				OJ.call("omnexa_education.api.education_analytics.get_executive_dashboard"),
				OJ.call("omnexa_education.education_global_benchmark.get_global_sis_score"),
				OJ.call("omnexa_education.api.education_demo.get_demo_hub_context"),
			]);
			const kpis = [
				{ value: data.students, label: OJ.t("الطلاب", "Students") },
				{ value: data.teachers, label: OJ.t("المعلّمون", "Teachers") },
				{ value: data.open_applications, label: OJ.t("طلبات مفتوحة", "Open Applications") },
				{ value: data.open_alerts, label: OJ.t("تنبيهات", "Alerts") },
				{ value: benchmark.weighted_score, label: OJ.t("التقييم العالمي", "Global Score") },
			];
			const $body = $('<div class="education-executive-dashboard"></div>');
			$body.append(`<h4 class="oj-section-title">${OJ.t("مؤشرات تنفيذية", "Executive KPIs")}</h4>`);
			$body.append(
				OJ.linkGrid([
					{ label: OJ.t("مركز العمل", "Workcenter"), icon: "🏢", route: "/app/education-workcenter" },
					{ label: OJ.t("التحليلات", "Analytics"), icon: "📈", route: "/app/education-analytics-dashboard" },
					{ label: OJ.t("الشؤون المالية", "Finance"), icon: "💰", route: "/app/education-finance-desk" },
					{ label: OJ.t("القبول", "Admissions"), icon: "📋", route: "/app/education-admissions-portal" },
				])
			);
			if ((demo.institutions || []).length) {
				$body.append(`<h4 class="oj-section-title" style="margin-top:16px">${OJ.t("المؤسسات", "Institutions")}</h4>`);
				$body.append(
					OJ.dataTable(
						[
							{ field: "name", label: OJ.t("المؤسسة", "Institution") },
							{ field: "institution_type", label: OJ.t("النوع", "Type") },
							{ field: "students", label: OJ.t("طلاب", "Students") },
							{ field: "applications", label: OJ.t("طلبات", "Apps") },
						],
						demo.institutions.map((i) => ({
							name: i.name,
							institution_type: i.institution_type,
							students: i.students || 0,
							applications: i.applications || 0,
						}))
					)
				);
			}
			const $shell = OJ.shell({
				title: OJ.t("لوحة المدير التنفيذي", "Executive Dashboard"),
				subtitle: OJ.t("ErpGenEx — EduSphere", "ErpGenEx — EduSphere"),
				role: OJ.t("مدير تعليم", "Education Executive"),
				brandLogoUrl: OJ.educationLogo,
				kpis,
				sidebarRole: "workcenter",
				currentPage: "education-executive-dashboard",
				bodyEl: $body,
				homeRoute: "/app/education-workcenter",
			});
			$mount.empty().append($shell);
		}
		render().catch((e) => OJ.showCallError(e));
	});
};
