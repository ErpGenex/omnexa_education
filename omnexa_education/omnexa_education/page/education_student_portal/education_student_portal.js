frappe.pages["education-student-portal"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const $mount = OJ.mountDeskPage(wrapper, __("Student Portal"));

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

		const $body = $('<div class="education-student-desk"></div>');
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
				if (data.gpa) {
					$body.append(`<p>${OJ.t("المعدل", "GPA")}: <strong>${data.gpa}%</strong></p>`);
				}
				if (blocked) {
					$body.append(`<div class="alert alert-warning">${OJ.t("الوصول مقيّد — راجع الشؤون المالية", "Access restricted — contact finance office")}</div>`);
				} else {
					$body.append(OJ.linkGrid([
						{ label: OJ.t("الجدول", "Timetable"), icon: "📅", route: "/app/education-timetable-board" },
						{ label: OJ.t("الدرجات", "Grades"), icon: "📝", route: "List/Education Assessment Result" },
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
					$body.append(`<h4 class="oj-section-title">${OJ.t("صندوق الوارد", "Unified Inbox")}</h4>`);
					const $inbox = $(`<div class="student-inbox"></div>`);
					renderInbox(data.inbox, $inbox);
					$body.append($inbox);
					if (data.sso_available && data.laravel_enabled) {
						const $sso = $(`<button type="button" class="btn btn-primary" style="margin-top:16px">${OJ.t("فتح LMS", "Open LMS")}</button>`);
						$sso.on("click", async () => {
							const handoff = await OJ.call("omnexa_education.api.laravel_sso.get_laravel_sso_handoff", { target: "student-dashboard" });
							if (handoff.redirect_url) window.open(handoff.redirect_url, "_blank");
						});
						$body.append($sso);
					}
				}
			})
			.catch((e) => OJ.showCallError(e));
	});
};
