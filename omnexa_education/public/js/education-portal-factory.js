/**
 * Shared education portal page renderer — Finance Journey parity
 */
/* global frappe */
window.EducationPortal = {
	render(wrapper, { title, apiMethod, role, links, onData, pageRoute }) {
		function boot(OJ) {
			const { company, branch } = OJ.resolveCompanyBranch();
			const $mount = OJ.mountDeskPage(wrapper, title);

			async function renderBody() {
				const data = await OJ.call(apiMethod, { company, branch });
				if (onData) onData(data);
				const kpis = (data.kpis || []).map((k) => ({ value: k.value, label: OJ.t(k.label_ar, k.label_en) }));
				const $body = $('<div class="education-portal-body"></div>');
				if (links && links.length) {
					$body.append(
						OJ.linkGrid(
							links.map((l) => ({
								...l,
								label: OJ.t(l.label_ar, l.label_en),
								logoUrl: l.logoUrl || OJ.educationLogo,
							}))
						)
					);
				}
				if (data.table) {
					$body.append(`<h4 class="oj-section-title">${OJ.esc(data.table.title || "")}</h4>`);
					$body.append(OJ.dataTable(data.table.columns, data.table.rows));
				}
				if (data.html) $body.append(data.html);
				const active = pageRoute || window.location.pathname.replace(/^\//, "");
				const $shell = OJ.shell({
					title: OJ.t(data.title_ar || title, data.title_en || title),
					subtitle: data.subtitle ? OJ.t(data.subtitle_ar, data.subtitle_en) : OJ.t("ErpGenEx — EduSphere", "ErpGenEx — EduSphere"),
					role: role,
					brandLogoUrl: OJ.educationLogo,
					kpis,
					sidebar: OJ.defaultSidebar(role, active.startsWith("app/") ? `/${active}` : `/app/${active}`),
					bodyEl: $body,
					currentPage: (pageRoute || "").replace(/^\/app\//, ""),
				});
				$mount.empty().append($shell);
				$shell.find(".oj-sidebar-item[data-nav-route]").off("click").on("click", function (e) {
					e.preventDefault();
					OJ.navigateRoute($(this).attr("data-nav-route"));
				});
			}

			renderBody().catch((err) => OJ.showCallError(err));
		}

		if (window.OmnexaJourney && window.OmnexaJourney.shell) {
			boot(window.OmnexaJourney);
			return;
		}
		window.EducationJourney.boot(() => boot(window.OmnexaJourney));
	},
};
