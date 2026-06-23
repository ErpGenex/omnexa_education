frappe.pages["education-analytics-dashboard"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const $mount = OJ.mountDeskPage(wrapper, __("Education Analytics Dashboard"));

		async function render() {
			const [atRisk, benchmark, demo] = await Promise.all([
				OJ.call("omnexa_education.api.education_analytics.evaluate_at_risk_students"),
				OJ.call("omnexa_education.education_global_benchmark.get_global_sis_score"),
				OJ.call("omnexa_education.api.education_demo.get_demo_hub_context"),
			]);
			const qa = demo.academy_qa_metrics || [];
			const kpis = [
				{ value: atRisk.evaluated, label: OJ.t("تم تقييمهم", "Evaluated") },
				{ value: (atRisk.alerts || []).length, label: OJ.t("تنبيهات", "Alerts") },
				{ value: benchmark.weighted_score, label: OJ.t("SIS Score", "SIS Score") },
				{ value: benchmark.parity_pct_vs_leaders + "%", label: OJ.t("Parity", "Parity") },
			];
			const $body = $('<div class="education-analytics-dashboard"></div>');
			$body.append(`<h4 class="oj-section-title">${OJ.t("ضمان الجودة — الأكاديمية", "Academy Quality Assurance")}</h4>`);
			if (qa.length) {
				const $qa = $('<div class="oj-kpi-row"></div>');
				qa.forEach((m) => {
					$qa.append(`<div class="oj-kpi-card"><div class="oj-kpi-value">${OJ.esc(String(m.target))}${OJ.esc(m.unit || "")}</div><div class="oj-kpi-label">${OJ.esc(OJ.t(m.label_ar, m.label_en))}</div></div>`);
				});
				$body.append($qa);
			}
			$body.append(`<h4 class="oj-section-title" style="margin-top:16px">${OJ.t("مصفوفة المعايير الدولية", "Global Standards Matrix")}</h4>`);
			$body.append(
				OJ.dataTable(
					[
						{ field: "label", label: OJ.t("المجال", "Domain") },
						{ field: "score", label: OJ.t("الدرجة", "Score") },
						{ field: "weight", label: OJ.t("الوزن", "Weight") },
					],
					(benchmark.matrix || []).map((r) => ({ label: r.label, score: r.score, weight: r.weight }))
				)
			);
			const $shell = OJ.shell({
				title: OJ.t("لوحة التحليلات", "Analytics Dashboard"),
				subtitle: OJ.t("ErpGenEx — EduSphere QA", "ErpGenEx — EduSphere QA"),
				role: OJ.t("محلل", "Analyst"),
				brandLogoUrl: OJ.educationLogo,
				kpis,
				sidebarRole: "workcenter",
				currentPage: "education-analytics-dashboard",
				bodyEl: $body,
				homeRoute: "/app/education-workcenter",
			});
			$mount.empty().append($shell);
		}
		render().catch((e) => OJ.showCallError(e));
	});
};
