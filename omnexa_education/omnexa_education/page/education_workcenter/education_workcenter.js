frappe.pages["education-workcenter"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const $mount = OJ.mountDeskPage(wrapper, __("Education Workcenter"));

		async function render() {
			const ctx = await OJ.call("omnexa_education.api.education_portal_catalog.get_workcenter_context");
			const groups = ctx.grouped_portals || [];
			const steps = ctx.journey_steps || [];
			const kpis = (ctx.kpis || []).map((k) => ({
				value: k.value ?? "—",
				label: OJ.t(k.label_ar, k.label_en),
			}));

			const $body = $('<div class="education-workcenter-journey"></div>');
			$body.append(`
				<p class="oj-muted">${OJ.t(
					"نظام البوابات — كل مستخدم يدخل حسب دوره",
					"Portal system — each user enters through their role portal"
				)}</p>`);

			if (steps.length) {
				$body.append(
					`<h4 class="oj-section-title">${OJ.t("رحلة التعليم — 12 مرحلة", "Education Journey — 12 Stages")}</h4>`
				);
				$body.append(
					OJ.workflowJourneyGrid(steps, (step) => {
						if (step.route) OJ.navigateRoute(step.route);
					})
				);
			}

			$body.append(`<h4 class="oj-section-title">${OJ.t("بوابات الأدوار", "Role Portals")}</h4>`);
			$body.append(OJ.portalCategoryGrid(groups));

			const $shell = OJ.shell({
				title: OJ.t("ErpGenEx Education", "ErpGenEx Education"),
				subtitle: OJ.t("ErpGenEx — EduSphere", "ErpGenEx — EduSphere"),
				role: OJ.t("مركز العمل", "Workcenter"),
				brandLogoUrl: ctx.logo_url || OJ.educationLogo,
				kpis,
				sidebarRole: "workcenter",
				currentPage: "education-workcenter",
				bodyEl: $body,
				homeRoute: "/app/education-workcenter",
			});
			$mount.empty().append($shell);
		}

		render().catch((e) => OJ.showCallError(e));
	});
};
