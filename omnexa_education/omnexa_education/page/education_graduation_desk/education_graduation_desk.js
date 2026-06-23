frappe.pages["education-graduation-desk"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const { company, branch } = OJ.resolveCompanyBranch();
		const $mount = OJ.mountDeskPage(wrapper, __("Graduation Desk"));

		async function render() {
			const data = await OJ.call("omnexa_education.api.lifecycle_role_desks.get_graduation_dashboard", { company, branch });
			const $body = $('<div></div>');
			$body.append(OJ.linkGrid([
				{ label: OJ.t("الطلاب", "Students"), icon: "🎓", route: "List/Education Student" },
				{ label: OJ.t("طلبات الشهادات", "Transcript Requests"), icon: "📜", route: "List/Education Transcript Request" },
				{ label: OJ.t("الشهادات الرسمية", "Official Transcripts"), icon: "📄", route: "List/Education Official Transcript" },
				{ label: OJ.t("الخريجون", "Alumni"), icon: "🤝", route: "/app/education-alumni-desk" },
			]));
			$body.append(`<h4 class="oj-section-title" style="margin-top:16px">${OJ.t("قائمة التخرج", "Graduation Queue")}</h4>`);
			const rows = data.graduation_queue || [];
			if (!rows.length) {
				$body.append(`<p class="oj-muted">${OJ.t("لا طلاب", "No students")}</p>`);
			} else {
				const $tbl = $(`<table class="oj-data-table"><thead><tr>
					<th>${OJ.t("الطالب", "Student")}</th><th>${OJ.t("المؤسسة", "Institution")}</th><th></th>
				</tr></thead><tbody></tbody></table>`);
				rows.forEach((r) => {
					const $tr = $(`<tr><td>${OJ.esc(r.student_name)}</td><td>${OJ.esc(r.institution || "")}</td><td></td></tr>`);
					const $btn = $(`<button type="button" class="btn btn-sm btn-primary">${OJ.t("تخرّج", "Graduate")}</button>`);
					$btn.on("click", async () => {
						await OJ.call("omnexa_education.api.lifecycle_role_desks.mark_student_graduated", { student: r.name });
						frappe.show_alert({ message: OJ.t("تم", "Done"), indicator: "green" });
						render();
					});
					$tr.find("td:last").append($btn);
					$tbl.find("tbody").append($tr);
				});
				$body.append($tbl);
			}
			$mount.empty().append(OJ.shell({
				title: OJ.t("مكتب التخرج", "Graduation Desk"),
				subtitle: OJ.t("مراجعة · اعتماد · شهادات", "Audit · approval · certificates"),
				role: OJ.t("مسؤول القيد", "Registrar"),
				brandLogoUrl: OJ.educationLogo,
				kpis: [
					{ value: data.active_students, label: OJ.t("نشطون", "Active") },
					{ value: data.graduated, label: OJ.t("خريجون", "Graduated") },
					{ value: data.transcript_pending, label: OJ.t("شهادات معلقة", "Pending Transcripts") },
				],
				sidebarRole: "registrar",
				currentPage: "education-graduation-desk",
				bodyEl: $body,
				homeRoute: "/app/education-workcenter",
			}));
		}
		render().catch((e) => OJ.showCallError(e));
	});
};
