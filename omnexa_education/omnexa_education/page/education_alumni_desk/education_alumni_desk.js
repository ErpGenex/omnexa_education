frappe.pages["education-alumni-desk"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const { company, branch } = OJ.resolveCompanyBranch();
		const $mount = OJ.mountDeskPage(wrapper, __("Alumni Desk"));

		OJ.call("omnexa_education.api.lifecycle_role_desks.get_alumni_dashboard", { company, branch }).then((data) => {
			const $body = $('<div></div>');
			$body.append(OJ.linkGrid([
				{ label: OJ.t("سجل الخريجين", "Alumni Records"), icon: "🤝", route: "List/Education Alumni Record" },
				{ label: OJ.t("التوظيف", "Careers"), icon: "💼", route: "List/Education Alumni Record" },
				{ label: OJ.t("مركز العمل", "Workcenter"), icon: "🏢", route: "/app/education-workcenter" },
			]));
			$body.append(`<h4 class="oj-section-title" style="margin-top:16px">${OJ.t("آخر الخريجين", "Recent Alumni")}</h4>`);
			$body.append(OJ.dataTable(
				[
					{ field: "student", label: OJ.t("الطالب", "Student") },
					{ field: "graduation_date", label: OJ.t("التخرج", "Graduation") },
					{ field: "current_employer", label: OJ.t("جهة العمل", "Employer") },
				],
				data.records || []
			));
			$mount.empty().append(OJ.shell({
				title: OJ.t("بوابة الخريجين", "Alumni & Careers"),
				subtitle: OJ.t("شبكة · توظيف · متابعة", "Network · employment · engagement"),
				role: OJ.t("خدمات مهنية", "Career Services"),
				brandLogoUrl: OJ.educationLogo,
				kpis: [
					{ value: data.alumni_count, label: OJ.t("خريجون", "Alumni") },
					{ value: data.employed_count, label: OJ.t("موظّفون", "Employed") },
					{ value: (data.employment_rate || 0) + "%", label: OJ.t("معدل التوظيف", "Employment Rate") },
				],
				sidebarRole: "registrar",
				currentPage: "education-alumni-desk",
				bodyEl: $body,
				homeRoute: "/app/education-workcenter",
			}));
		}).catch((e) => OJ.showCallError(e));
	});
};
