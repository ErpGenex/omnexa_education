frappe.pages["education-qa-desk"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const { company, branch } = OJ.resolveCompanyBranch();
		const $mount = OJ.mountDeskPage(wrapper, __("QA Desk"));

		OJ.call("omnexa_education.api.lifecycle_role_desks.get_qa_dashboard", { company, branch }).then((data) => {
			const $body = $('<div></div>');
			$body.append(`<h4 class="oj-section-title">${OJ.t("مؤشرات الجودة الحية", "Live QA Indicators")}</h4>`);
			const $qa = $('<div class="oj-kpi-row"></div>');
			(data.qa_metrics || []).forEach((m) => {
				$qa.append(`<div class="oj-kpi-card"><div class="oj-kpi-value">${OJ.esc(String(m.live_value ?? m.target))}${OJ.esc(m.unit || "")}</div><div class="oj-kpi-label">${OJ.esc(OJ.t(m.label_ar, m.label_en))}</div></div>`);
			});
			$body.append($qa);
			$body.append(OJ.linkGrid([
				{ label: OJ.t("التحليلات", "Analytics"), icon: "📈", route: "/app/education-analytics-dashboard" },
				{ label: OJ.t("تنبيهات المخاطر", "Risk Alerts"), icon: "⚠️", route: "List/Education Predictive Alert" },
				{ label: OJ.t("FERPA", "FERPA Audit"), icon: "🔒", route: "query-report/Education FERPA Audit" },
				{ label: OJ.t("GPA Summary", "GPA Summary"), icon: "📊", route: "query-report/Education GPA Summary" },
			]));
			$body.append(`<h4 class="oj-section-title" style="margin-top:16px">${OJ.t("المصفوفة الدولية", "Global Matrix")}</h4>`);
			$body.append(OJ.dataTable(
				[
					{ field: "label", label: OJ.t("المجال", "Domain") },
					{ field: "score", label: OJ.t("الدرجة", "Score") },
					{ field: "weight", label: OJ.t("الوزن", "Weight") },
				],
				data.matrix || []
			));
			$mount.empty().append(OJ.shell({
				title: OJ.t("ضمان الجودة والاعتماد", "QA & Accreditation"),
				subtitle: OJ.t("OBE · اعتماد · تحسين مستمر", "OBE · accreditation · CI"),
				role: OJ.t("ضمان الجودة", "QA Officer"),
				brandLogoUrl: OJ.educationLogo,
				kpis: [
					{ value: data.global_score, label: OJ.t("SIS Score", "SIS Score") },
					{ value: data.open_alerts, label: OJ.t("تنبيهات", "Alerts") },
					{ value: data.students, label: OJ.t("طلاب", "Students") },
				],
				sidebarRole: "workcenter",
				currentPage: "education-qa-desk",
				bodyEl: $body,
				homeRoute: "/app/education-workcenter",
			}));
		}).catch((e) => OJ.showCallError(e));
	});
};
