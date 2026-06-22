/**
 * Education portal factory — healthcare-parity Journey shell + API data
 */
frappe.provide("omnexa_education.portal");

omnexa_education.portal.mount = function (wrapper, config) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) {
			frappe.msgprint(__("Run: bench build --app omnexa_education"));
			return;
		}
		const { company, branch } = OJ.resolveCompanyBranch();
		const $mount = OJ.mountDeskPage(wrapper, config.deskTitle || config.titleEn || __("Portal"));

		async function render() {
			const args = Object.assign({ company, branch }, config.apiArgs || {});
			const data = config.api ? await OJ.call(config.api, args) : {};
			const kpis = (config.kpis || []).map((k) => ({
				value: data[k.field] ?? k.value ?? "—",
				label: OJ.t(k.labelAr, k.labelEn),
			}));
			if (data.count != null && !config.kpis?.length) {
				kpis.push({ value: data.count, label: OJ.t("السجلات", "Records") });
			}
			const $body = $("<div></div>");
			if (config.links) {
				$body.append(
					OJ.linkGrid(
						config.links.map((l) => ({
							icon: l.icon,
							label: OJ.t(l.labelAr, l.labelEn),
							route: l.route,
						}))
					)
				);
			}
			if (config.columns && config.rowsField) {
				$body.append(`<h4 class="oj-section-title">${OJ.t(config.tableTitleAr || "", config.tableTitleEn || "")}</h4>`);
				$body.append(
					OJ.dataTable(
						config.columns.map((c) => ({ field: c.field, label: OJ.t(c.ar, c.en) })),
						data[config.rowsField] || []
					)
				);
			}
			if (config.renderExtra) config.renderExtra($body, data);
			const $shell = OJ.shell({
				title: OJ.t(config.titleAr, config.titleEn),
				subtitle: OJ.t("ErpGenEx — EduSphere", "ErpGenEx — EduSphere"),
				role: OJ.t(config.roleAr || "", config.roleEn || ""),
				brandLogoUrl: OJ.educationLogo,
				kpis,
				sidebarRole: config.sidebarRole || "workcenter",
				currentPage: config.currentPage || "",
				bodyEl: $body,
				homeRoute: config.homeRoute || "/app/education-workcenter",
			});
			$mount.empty().append($shell);
		}

		render().catch((e) => OJ.showCallError(e));
	});
};
