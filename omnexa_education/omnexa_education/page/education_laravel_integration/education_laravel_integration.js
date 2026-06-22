frappe.pages["education-laravel-integration"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const $mount = OJ.mountDeskPage(wrapper, __("Laravel TLMS Integration"));

		async function render() {
			const data = await OJ.call("omnexa_education.api.journey_role_desks.get_laravel_integration_dashboard");
			const kpis = [
				{ value: data.enable_laravel_tlms ? OJ.t("مفعّل", "On") : OJ.t("معطّل", "Off"), label: OJ.t("Laravel TLMS", "Laravel TLMS") },
				{ value: data.queue_stats?.queued || 0, label: OJ.t("في الانتظار", "Queued") },
				{ value: data.queue_stats?.failed || 0, label: OJ.t("فشل", "Failed") },
				{ value: data.laravel_last_ping_status || "—", label: OJ.t("آخر Ping", "Last Ping") },
			];
			const $body = $('<div class="education-laravel-desk"></div>');
			$body.append(`<p class="oj-muted"><strong>${OJ.t("Webhook URL", "Webhook URL")}:</strong> ${OJ.esc(data.webhook_url || "")}</p>`);
			$body.append(`<p class="oj-muted"><strong>${OJ.t("Base URL", "Base URL")}:</strong> ${OJ.esc(data.laravel_base_url || "—")}</p>`);
			$body.append(
				OJ.linkGrid([
					{ label: OJ.t("إعدادات التعليم", "Education Settings"), icon: "⚙️", route: "Form/Education Settings/Education Settings" },
					{ label: OJ.t("روابط LMS", "LMS Course Links"), icon: "📚", route: "List/Education Lms Course Link" },
					{ label: OJ.t("طابور المزامنة", "Sync Queue"), icon: "⏳", route: "List/Education Laravel Sync Queue" },
					{ label: OJ.t("سجل الوصول", "Access Log"), icon: "🔒", route: "List/Education Account Access Log" },
					{ label: OJ.t("مركز المالية", "Finance Desk"), icon: "💰", route: "/app/education-finance-desk" },
				])
			);
			const $actions = $(`<div class="oj-actions" style="margin-top:16px;display:flex;gap:8px"></div>`);
			const $ping = $(`<button type="button" class="btn btn-primary">${OJ.t("اختبار الاتصال", "Test Connection")}</button>`);
			$ping.on("click", async () => {
				const res = await OJ.call("omnexa_education.omnexa_education.doctype.education_settings.education_settings.test_laravel_connection");
				frappe.show_alert({
					message: res.ok ? OJ.t("الاتصال ناجح", "Connection OK") : (res.error || OJ.t("فشل", "Failed")),
					indicator: res.ok ? "green" : "red",
				});
				render();
			});
			const $sync = $(`<button type="button" class="btn btn-default">${OJ.t("معالجة الطابور", "Process Queue")}</button>`);
			$sync.on("click", async () => {
				await OJ.call("omnexa_education.api.laravel_client.process_sync_queue");
				frappe.show_alert({ message: OJ.t("تمت المعالجة", "Processed"), indicator: "green" });
				render();
			});
			$actions.append($ping, $sync);
			$body.append($actions);
			$body.append(`<h4 class="oj-section-title" style="margin-top:20px">${OJ.t("روابط Laravel TLMS", "Laravel TLMS Links")}</h4>`);
			$body.append(
				OJ.dataTable(
					[
						{ field: "name", label: "ID" },
						{ field: "course", label: OJ.t("المقرر", "Course") },
						{ field: "external_course_id", label: OJ.t("External ID", "External ID") },
					],
					data.lms_links || []
				)
			);
			const $shell = OJ.shell({
				title: OJ.t("ربط Laravel TLMS", "Laravel TLMS Integration"),
				subtitle: OJ.t("إعدادات §5 إدارة التدريس والتعلّم", "ISMS §5 Teaching & Learning"),
				role: OJ.t("مسؤول النظام", "System Admin"),
				brandLogoUrl: OJ.educationLogo,
				kpis,
				sidebarRole: "laravel",
				currentPage: "education-laravel-integration",
				bodyEl: $body,
				homeRoute: "/app/education-workcenter",
			});
			$mount.empty().append($shell);
		}
		render().catch((err) => OJ.showCallError(err));
	});
};
