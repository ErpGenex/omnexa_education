frappe.pages["education-student-portal"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const $mount = OJ.mountDeskPage(wrapper, __("Student Portal"));
		const $body = $('<div></div>');
		const $shell = OJ.shell({
			title: OJ.t("بوابة الطالب", "Student Portal"),
			subtitle: OJ.t("ErpGenEx — EduSphere", "ErpGenEx — EduSphere"),
			role: OJ.t("طالب", "Student"),
			brandLogoUrl: OJ.educationLogo,
			sidebarRole: "student",
			currentPage: "education-student-portal",
			bodyEl: $body,
			homeRoute: "/app/education-workcenter",
		});
		$mount.empty().append($shell);
		OJ.call("omnexa_education.api.journey_role_desks.get_student_portal_dashboard")
			.then((data) => {
				$body.empty();
				const blocked = data.financial_hold || ["Suspended", "Financial Hold", "Not Provisioned"].includes(data.account_access_status);
				if (!data.student) {
					$body.html(`<p class="oj-muted">${OJ.t("لا يوجد سجل طالب مرتبط بحسابك", "No student record linked to your account")}</p>`);
					return;
				}
				$body.append(`<p><strong>${OJ.esc(data.student_name)}</strong> · ${OJ.esc(data.grade_level || "")} · ${OJ.esc(data.section || "")}</p>`);
				$body.append(`<p>${OJ.t("حالة الحساب", "Account")}: <strong>${OJ.esc(data.account_access_status || "")}</strong></p>`);
				if (blocked) {
					$body.append(`<div class="alert alert-warning">${OJ.t("الوصول مقيّد — راجع الشؤون المالية", "Access restricted — contact finance office")}</div>`);
				} else {
					$body.append(OJ.linkGrid([
						{ label: OJ.t("الجدول", "Timetable"), icon: "📅", route: "/app/education-timetable-board" },
						{ label: OJ.t("الدرجات", "Grades"), icon: "📝", route: "List/Education Assessment Result" },
					]));
				}
			})
			.catch((e) => OJ.showCallError(e));
	});
};
