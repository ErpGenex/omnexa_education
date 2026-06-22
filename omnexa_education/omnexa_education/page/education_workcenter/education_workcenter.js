frappe.pages["education-workcenter"].on_page_load = function (wrapper) {
	function start(OJ) {
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
				<h4>${OJ.t("مركز عمل التعليم", "Education Workcenter")}</h4>
				<p class="oj-muted">${OJ.t(
					"نظام البوابات — كل مستخدم يدخل حسب دوره",
					"Portal system — each user enters through their role portal"
				)}</p>`);

			if (steps.length) {
				$body.append(
					`<h4 class="oj-section-title">${OJ.t("رحلة التعليم — 12 مرحلة", "Education Journey — 12 Stages")}</h4>`
				);
				const $grid = OJ.workflowJourneyGrid(steps, (step) => {
					if (step.route) navigateRoute(step.route);
				});
				$body.append($grid);
			}

			$body.append(
				`<h4 class="oj-section-title">${OJ.t("بوابات الأدوار", "Role Portals")}</h4>`
			);
			$body.append(OJ.portalCategoryGrid(groups));

			const $shell = OJ.shell({
				title: OJ.t("ErpGenEx Education", "ErpGenEx Education"),
				subtitle: OJ.t("ErpGenEx — EduSphere", "ErpGenEx — EduSphere"),
				role: OJ.t("مركز العمل", "Workcenter"),
				brandLogoUrl: ctx.logo_url || OJ.educationLogo,
				kpis,
				sidebar: OJ.defaultSidebar("workcenter", "/app/education-workcenter"),
				bodyEl: $body,
				currentPage: "education-workcenter",
			});

			$mount.empty().append($shell);
			$shell.find(".oj-sidebar-item[data-nav-route]").off("click").on("click", function (e) {
				e.preventDefault();
				navigateRoute($(this).attr("data-nav-route"));
			});
		}

		function navigateRoute(route) {
			if (!route) return;
			if (route.startsWith("/app/")) window.location.href = route;
			else if (route.startsWith("List/")) frappe.set_route("List", route.slice(5));
			else if (route.startsWith("Form/")) {
				const p = route.split("/");
				frappe.set_route("Form", p[1], p[2] || "");
			} else frappe.set_route(route);
		}

		render().catch((e) => OJ.showCallError(e));
	}

	if (window.EducationJourney && window.EducationJourney.boot) {
		window.EducationJourney.boot(() => start(window.OmnexaJourney));
	} else {
		frappe.require(["/assets/omnexa_education/js/education-journey-kit.js"], () => {
			window.EducationJourney.boot(() => start(window.OmnexaJourney));
		});
	}
};
