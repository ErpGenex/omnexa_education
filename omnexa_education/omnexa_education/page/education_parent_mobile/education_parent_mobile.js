frappe.pages["education-parent-mobile"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const $mount = OJ.mountDeskPage(wrapper, __("Parent Portal"));
		let selectedStudent = null;

		function channelLabel(ch) {
			const map = {
				Administrative: OJ.t("إداري", "Administrative"),
				Academic: OJ.t("تعليمي", "Academic"),
				Financial: OJ.t("مالي", "Financial"),
			};
			return map[ch] || ch;
		}

		function renderInbox(inbox, $container) {
			const messages = (inbox && inbox.messages) || [];
			if (!messages.length) {
				$container.append(`<p class="oj-muted">${OJ.t("لا رسائل", "No messages")}</p>`);
				return;
			}
			const byChannel = { Administrative: [], Academic: [], Financial: [] };
			messages.forEach((m) => {
				const ch = m.channel || "Administrative";
				if (!byChannel[ch]) byChannel[ch] = [];
				byChannel[ch].push(m);
			});
			const $tabs = $(`<div class="oj-tabs" style="display:flex;gap:8px;margin-bottom:12px"></div>`);
			const $panels = $(`<div class="oj-tab-panels"></div>`);
			Object.keys(byChannel).forEach((ch, idx) => {
				const $btn = $(`<button type="button" class="btn btn-sm ${idx === 0 ? "btn-primary" : "btn-default"}">${channelLabel(ch)} (${byChannel[ch].length})</button>`);
				const $panel = $(`<div class="oj-tab-panel" style="${idx === 0 ? "" : "display:none"}"></div>`);
				if (byChannel[ch].length) {
					$panel.append(
						OJ.dataTable(
							[
								{ field: "title", label: OJ.t("الموضوع", "Subject") },
								{ field: "channel", label: OJ.t("القناة", "Channel") },
								{ field: "source", label: OJ.t("المصدر", "Source") },
							],
							byChannel[ch]
						)
					);
				} else {
					$panel.append(`<p class="oj-muted">${OJ.t("لا رسائل", "No messages")}</p>`);
				}
				$btn.on("click", () => {
					$tabs.find("button").removeClass("btn-primary").addClass("btn-default");
					$btn.removeClass("btn-default").addClass("btn-primary");
					$panels.find(".oj-tab-panel").hide();
					$panel.show();
				});
				$tabs.append($btn);
				$panels.append($panel);
			});
			$container.append($tabs, $panels);
		}

		async function loadDashboard(student) {
			const data = await OJ.call("omnexa_education.api.journey_role_desks.get_parent_portal_dashboard", { student });
			const $body = $('<div class="education-parent-desk"></div>');
			if (!data.student && !data.children?.length) {
				const hint = await OJ.call("omnexa_education.api.education_portal_link.get_portal_empty_hint");
				$body.append(`<p class="oj-muted">${OJ.t("اربط بريد ولي الأمر بسجل الطالب", "Link guardian email on student record")}</p>`);
				$body.append(`<p>${OJ.t("المستخدم الحالي", "Current user")}: <strong>${OJ.esc(hint.current_user || "")}</strong></p>`);
				$body.append(`<p>${OJ.t("للتجربة سجّل الخروج وادخل كولي أمر ديمو", "For demo, log out and sign in as")}: <code>${OJ.esc(hint.demo_parent_email || "parent@demo.education")}</code> · ${OJ.t("كلمة المرور", "Password")}: <code>${OJ.esc(hint.demo_password || "Education@Demo2026")}</code></p>`);
				if (hint.can_manage) {
					const $link = $(`<button type="button" class="btn btn-primary" style="margin-top:12px">${OJ.t("ربط حسابات البوابات", "Link Portal Accounts")}</button>`);
					$link.on("click", async () => {
						const res = await OJ.call("omnexa_education.api.education_portal_link.ensure_demo_portal_users_linked");
						frappe.show_alert({
							message: `${OJ.t("أولياء", "Parents")}: ${res.parent_children || 0}`,
							indicator: res.parent_children ? "green" : "orange",
						});
					});
					$body.append($link);
				}
				return $body;
			}
			if (data.children?.length > 1) {
				const $sel = $(`<select class="form-control" style="max-width:320px;margin-bottom:12px"></select>`);
				data.children.forEach((c) => {
					$sel.append(`<option value="${OJ.esc(c.name)}" ${c.name === data.student ? "selected" : ""}>${OJ.esc(c.student_name)}</option>`);
				});
				$sel.on("change", async () => {
					selectedStudent = $sel.val();
					const $new = await loadDashboard(selectedStudent);
					$mount.find(".education-parent-desk").replaceWith($new);
				});
				$body.append(`<label class="oj-muted">${OJ.t("اختر الطفل", "Select child")}</label>`, $sel);
			}
			$body.append(`<h4>${OJ.esc(data.student_name || data.student)}</h4>`);
			if (data.gpa) {
				$body.append(`<p>${OJ.t("المعدل", "GPA")}: <strong>${data.gpa}%</strong></p>`);
			}
			$body.append(OJ.linkGrid([
				{ label: OJ.t("الرسوم والفواتير", "Fees & Invoices"), icon: "💳", route: "List/Sales Invoice" },
				{ label: OJ.t("الدرجات", "Grades"), icon: "📝", route: "List/Education Assessment Result" },
				{ label: OJ.t("الحضور", "Attendance"), icon: "✅", route: "List/Education Attendance Session" },
			]));
			if (data.today_schedule?.length) {
				$body.append(`<h4 class="oj-section-title">${OJ.t("جدول اليوم", "Today's Schedule")}</h4>`);
				$body.append(OJ.dataTable(
					[
						{ field: "subject", label: OJ.t("المادة", "Subject") },
						{ field: "start_time", label: OJ.t("من", "From") },
						{ field: "end_time", label: OJ.t("إلى", "To") },
						{ field: "room", label: OJ.t("القاعة", "Room") },
					],
					data.today_schedule
				));
			}
			if (data.invoices?.length) {
				$body.append(`<h4 class="oj-section-title">${OJ.t("آخر الفواتير", "Recent Invoices")}</h4>`);
				$body.append(OJ.dataTable(
					[
						{ field: "name", label: OJ.t("الفاتورة", "Invoice") },
						{ field: "grand_total", label: OJ.t("الإجمالي", "Total") },
						{ field: "outstanding_amount", label: OJ.t("المتبقي", "Outstanding") },
					],
					data.invoices
				));
			}
			$body.append(`<h4 class="oj-section-title">${OJ.t("صندوق الوارد", "Unified Inbox")}</h4>`);
			const $inbox = $(`<div class="parent-inbox"></div>`);
			renderInbox(data.inbox, $inbox);
			$body.append($inbox);
			if (data.sso_available && data.laravel_enabled) {
				const $sso = $(`<button type="button" class="btn btn-primary" style="margin-top:16px">${OJ.t("فتح LMS", "Open LMS")}</button>`);
				$sso.on("click", async () => {
					const handoff = await OJ.call("omnexa_education.api.laravel_sso.get_laravel_sso_handoff", { target: "parent-dashboard" });
					if (handoff.redirect_url) window.open(handoff.redirect_url, "_blank");
				});
				$body.append($sso);
			}
			$body.addClass("education-parent-desk");
			return $body;
		}

		const $shell = OJ.shell({
			title: OJ.t("بوابة ولي الأمر", "Parent Portal"),
			subtitle: OJ.t("ErpGenEx — EduSphere", "ErpGenEx — EduSphere"),
			role: OJ.t("ولي أمر", "Parent"),
			brandLogoUrl: OJ.educationLogo,
			sidebarRole: "parent",
			currentPage: "education-parent-mobile",
			bodyEl: $('<div class="education-parent-desk"></div>'),
			homeRoute: "/app/education-workcenter",
		});
		$mount.empty().append($shell);
		loadDashboard(selectedStudent)
			.then(($body) => $mount.find(".education-parent-desk").replaceWith($body))
			.catch((e) => OJ.showCallError(e));
	});
};
