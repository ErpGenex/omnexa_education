frappe.pages["education-admissions-portal"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const { company, branch } = OJ.resolveCompanyBranch();
		const $mount = OJ.mountDeskPage(wrapper, __("Admissions Portal"));
		const $body = $('<div></div>');
		$body.append(OJ.linkGrid([
			{ label: OJ.t("طلبات القبول", "Applications"), icon: "📋", route: "List/Education Admission Application" },
			{ label: OJ.t("قائمة الانتظار", "Waitlist"), icon: "⏳", route: "List/Education Waitlist Pool" },
			{ label: OJ.t("التقديم الخارجي", "Public Apply Page"), icon: "🌐", route: "/education/apply" },
			{ label: OJ.t("القبول الإلكتروني", "Online Applications"), icon: "📨", route: "List/Education Online Application" },
			{ label: OJ.t("رسوم القبول", "Admission Fees"), icon: "💳", route: "List/Education Fee Item" },
		]));

		async function loadOnlineApps() {
			const $sec = $(`<div style="margin-top:20px"><h4 class="oj-section-title">${OJ.t("طلبات الموقع الإلكتروني", "Website Applications")}</h4></div>`);
			$body.find(".oj-online-apps").remove();
			const $wrap = $('<div class="oj-online-apps"></div>');
			try {
				const apps = await frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "Education Online Application",
						filters: { company, status: ["in", ["Submitted", "Reviewed"]] },
						fields: ["name", "applicant_name", "institution", "status", "academic_year"],
						limit_page_length: 10,
						order_by: "creation desc",
					},
				});
				const rows = (apps.message || []).map((a) => ({
					name: a.name,
					applicant_name: a.applicant_name,
					institution: a.institution,
					status: a.status,
					action: a.status === "Submitted" ? "promote" : "",
				}));
				if (!rows.length) {
					$wrap.append(`<p class="oj-muted">${OJ.t("لا طلبات", "No applications")}</p>`);
				} else {
					const $tbl = $(`<table class="oj-data-table"><thead><tr>
						<th>${OJ.t("المتقدّم", "Applicant")}</th><th>${OJ.t("المؤسسة", "Institution")}</th>
						<th>${OJ.t("الحالة", "Status")}</th><th></th>
					</tr></thead><tbody></tbody></table>`);
					rows.forEach((r) => {
						const $tr = $(`<tr><td>${OJ.esc(r.applicant_name)}</td><td>${OJ.esc(r.institution)}</td><td>${OJ.esc(r.status)}</td><td></td></tr>`);
						if (r.action === "promote") {
							const $btn = $(`<button type="button" class="btn btn-xs btn-primary">${OJ.t("ترقية", "Promote")}</button>`);
							$btn.on("click", async () => {
								await OJ.call("omnexa_education.api.education_admissions.promote_online_application", { application: r.name });
								frappe.show_alert({ message: OJ.t("تم", "Promoted"), indicator: "green" });
								loadOnlineApps();
							});
							$tr.find("td:last").append($btn);
						}
						$tbl.find("tbody").append($tr);
					});
					$wrap.append($tbl);
				}
			} catch (e) {
				$wrap.append(`<p class="oj-muted">${OJ.t("تعذر التحميل", "Could not load")}</p>`);
			}
			$sec.append($wrap);
			$body.append($sec);
		}

		const $shell = OJ.shell({
			title: OJ.t("بوابة القبول", "Admissions Portal"),
			subtitle: OJ.t("ErpGenEx — EduSphere", "ErpGenEx — EduSphere"),
			role: OJ.t("مسؤول القبول", "Admissions Officer"),
			brandLogoUrl: OJ.educationLogo,
			kpis: [
				{ value: "…", label: OJ.t("الطلبات", "Applications") },
				{ value: "…", label: OJ.t("انتظار", "Waitlist") },
				{ value: "…", label: OJ.t("إلكتروني", "Online") },
			],
			sidebarRole: "admissions",
			currentPage: "education-admissions-portal",
			bodyEl: $body,
			homeRoute: "/app/education-workcenter",
		});
		$mount.empty().append($shell);
		OJ.call("omnexa_education.api.journey_role_desks.get_admissions_dashboard", { company, branch })
			.then((data) => {
				$shell.find(".oj-kpi-card").eq(0).find(".oj-kpi-value").text(data.applications ?? "0");
				$shell.find(".oj-kpi-card").eq(1).find(".oj-kpi-value").text(data.waitlist ?? "0");
				$shell.find(".oj-kpi-card").eq(2).find(".oj-kpi-value").text(data.online_applications ?? "0");
				loadOnlineApps();
			})
			.catch((e) => OJ.showCallError(e));
	});
};
