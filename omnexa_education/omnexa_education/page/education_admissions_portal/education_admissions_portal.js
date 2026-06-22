frappe.pages["education-admissions-portal"].on_page_load = function (wrapper) {
	const OJ = window.OmnexaJourney;
	if (!OJ) return;
	const { company, branch } = OJ.resolveCompanyBranch();
	const $mount = OJ.mountDeskPage(wrapper, __("Admissions Portal"));
	OJ.call("omnexa_education.api.journey_role_desks.get_admissions_dashboard", { company, branch }).then((data) => {
		const $body = $('<div></div>');
		$body.append(OJ.linkGrid([
			{ label: OJ.t("طلبات القبول", "Applications"), icon: "📋", route: "List/Education Admission Application" },
			{ label: OJ.t("قائمة الانتظار", "Waitlist"), icon: "⏳", route: "List/Education Waitlist Pool" },
			{ label: OJ.t("القبول الإلكتروني", "Online Applications"), icon: "🌐", route: "List/Education Online Application" },
			{ label: OJ.t("رسوم القبول", "Admission Fees"), icon: "💳", route: "List/Education Fee Item" },
		]));
		$mount.append(OJ.shell({
			title: OJ.t("بوابة القبول", "Admissions Portal"),
			subtitle: OJ.t("ErpGenEx — EduSphere", "ErpGenEx — EduSphere"),
			role: OJ.t("مسؤول القبول", "Admissions Officer"),
			brandLogoUrl: OJ.educationLogo,
			kpis: [
				{ value: data.applications, label: OJ.t("الطلبات", "Applications") },
				{ value: data.waitlist, label: OJ.t("انتظار", "Waitlist") },
			],
			sidebar: OJ.defaultSidebar("admissions", "/app/education-admissions-portal"),
			bodyEl: $body,
			currentPage: "education-admissions-portal",
		}));
	}).catch((e) => OJ.showCallError(e));
};
