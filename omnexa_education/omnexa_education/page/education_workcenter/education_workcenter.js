frappe.pages["education-workcenter"].on_page_load = function (wrapper) {
	omnexa_education.boot.ready(function (OJ) {
		if (!OJ || !OJ.mountDeskPage) return;
		const $mount = OJ.mountDeskPage(wrapper, __("Education Workcenter"));

		async function render() {
			const ctx = await OJ.call("omnexa_education.api.education_portal_catalog.get_workcenter_context");
			const groups = ctx.grouped_portals || [];
			const steps = ctx.journey_steps || [];
			const fullLifecycle = ctx.full_lifecycle || [];
			const externalPortals = ctx.external_portals || [];
			const readiness = ctx.live_readiness || {};
			const demo = ctx.demo || {};
			const kpis = (ctx.kpis || []).map((k) => ({
				value: k.value ?? "—",
				label: OJ.t(k.label_ar, k.label_en),
			}));

			const $body = $('<div class="education-workcenter-journey"></div>');
			$body.append(`
				<p class="oj-muted">${OJ.t(
					"EduSphere — 5 أنواع مؤسسات · 8 بوابات أدوار · معيار عالمي 4.85",
					"EduSphere — 5 institution types · 8 role portals · global benchmark 4.85"
				)}</p>`);

			// Global benchmark bar
			const bm = demo.global_benchmark || {};
			if (bm.weighted_score) {
				$body.append(`
					<div class="oj-panel oj-benchmark-bar" style="margin-bottom:16px;padding:12px 16px;background:#fff;border-radius:12px">
						<strong>${OJ.t("التقييم العالمي SIS", "Global SIS Score")}:</strong>
						<span style="font-size:1.4rem;font-weight:800;color:#003366;margin:0 8px">${OJ.esc(String(bm.weighted_score))}</span>
						<span class="oj-muted">${OJ.t("الهدف", "Target")} ${OJ.esc(String(bm.global_leader_target || "4.85"))} ·
						${OJ.t("Workday", "Workday")} ${bm.reference_leaders?.workday_student || "—"} ·
						${OJ.t("Banner", "Banner")} ${bm.reference_leaders?.ellucian_banner || "—"} ·
						PowerSchool ${bm.reference_leaders?.powerschool || "—"}</span>
					</div>`);
			}

			// Institution type cards
			const institutions = demo.institutions || [];
			if (institutions.length) {
				$body.append(`<h4 class="oj-section-title">${OJ.t("أنواع المؤسسات التعليمية", "Education Institution Types")}</h4>`);
				const $instGrid = $('<div class="oj-clinic-grid oj-institution-grid"></div>');
				institutions.forEach((inst) => {
					const icon = {
						"International School": "🏫",
						University: "🎓",
						Academy: "🏛️",
						Institute: "📖",
						"Training Center": "🛠️",
					}[inst.institution_type] || "🏢";
					const seeded = inst.seeded;
					$instGrid.append(`
						<div class="oj-clinic-card ${seeded ? "" : "oj-muted-card"}">
							<div class="oj-clinic-icon">${icon}</div>
							<h4>${OJ.esc(inst.name || inst.institution_type)}</h4>
							<p class="oj-muted">${OJ.esc(inst.institution_type)}${inst.academy_type ? " · " + OJ.esc(inst.academy_type) : ""}</p>
							<div class="oj-clinic-stats">
								<span>👨‍🎓 ${inst.students || 0}</span>
								<span>👩‍🏫 ${inst.teachers || 0}</span>
								<span>📋 ${inst.applications || 0}</span>
							</div>
							<span class="oj-pill">${seeded ? OJ.t("مزروع", "Seeded") : OJ.t("غير مزروع", "Not seeded")}</span>
						</div>`);
				});
				$body.append($instGrid);
			}

			// Demo seed + credentials
			if (demo.can_seed) {
				const $demoPanel = $(`<div class="oj-panel" style="margin:16px 0;padding:16px;background:#fff;border-radius:12px"></div>`);
				$demoPanel.append(`<h4>${OJ.t("🎯 محاكاة الديمو", "Demo Simulation")}</h4>`);
				$demoPanel.append(`<p class="oj-muted">${OJ.t(
					"زرع مؤسسات + مستخدمي جميع الأدوار (كلمة المرور: Education@Demo2026)",
					"Seed institutions + all role users (password: Education@Demo2026)"
				)}</p>`);
				const typeOpts = (demo.institution_type_options || ["All 5 Types"]).map((t) =>
					`<option value="${OJ.esc(t)}">${OJ.esc(t)}</option>`
				).join("");
				$demoPanel.append(`
					<div class="form-group" style="max-width:320px;margin-bottom:12px">
						<label class="oj-muted">${OJ.t("نوع المؤسسة", "Institution Type")}</label>
						<select id="edu-demo-inst-type" class="form-control">${typeOpts}</select>
					</div>`);
				const $seedBtn = $(`<button type="button" class="btn btn-primary">${OJ.t("تفعيل الديمو", "Activate Demo")}</button>`);
				$seedBtn.on("click", async () => {
					const institution_type = $("#edu-demo-inst-type").val() || "All 5 Types";
					$seedBtn.prop("disabled", true).text(OJ.t("جاري الزرع...", "Seeding..."));
					try {
						const res = await OJ.call("omnexa_education.api.education_demo.seed_demo", { institution_type });
						frappe.show_alert({ message: res.message || OJ.t("تم", "Done"), indicator: "green" });
						render();
					} catch (e) {
						OJ.showCallError(e);
					} finally {
						$seedBtn.prop("disabled", false).text(OJ.t("تفعيل الديمو", "Activate Demo"));
					}
				});
				$demoPanel.append($seedBtn);
				const $laravelSync = $(`<button type="button" class="btn btn-success" style="margin-left:8px">${OJ.t("مزامنة → Laravel", "Sync → Laravel")}</button>`);
				$laravelSync.on("click", async () => {
					$laravelSync.prop("disabled", true).text(OJ.t("جاري المزامنة...", "Syncing..."));
					try {
						const res = await OJ.call("omnexa_education.api.education_laravel_full_sync.sync_all_data_to_laravel");
						frappe.show_alert({ message: res.message || OJ.t("تم", "Done"), indicator: res.ok ? "green" : "orange" });
						render();
					} catch (e) {
						OJ.showCallError(e);
					} finally {
						$laravelSync.prop("disabled", false).text(OJ.t("مزامنة → Laravel", "Sync → Laravel"));
					}
				});
				$demoPanel.append($laravelSync);
				$demoPanel.append(`<p class="oj-muted" style="margin-top:8px">${OJ.t(
					"أو من فرع: Branch → Demo data → Education → تفعيل ديمو EduSphere",
					"Or from Branch → Demo data → Education → Activate EduSphere Demo"
				)}</p>`);

				const creds = (demo.credentials || {}).users || [];
				if (creds.length) {
					$demoPanel.append(`<h4 style="margin-top:16px">${OJ.t("حسابات الأدوار", "Role Accounts")}</h4>`);
					const rows = creds.map((u) => `<tr>
						<td>${OJ.esc(u.name)}</td>
						<td><code>${OJ.esc(u.email)}</code></td>
						<td>${OJ.esc(OJ.t(u.label_ar, u.label_en))}</td>
						<td><a href="${OJ.esc(u.route)}" class="oj-btn oj-btn-sm oj-btn-outline">${OJ.t("فتح", "Open")}</a></td>
					</tr>`).join("");
					$demoPanel.append(`<table class="oj-data-table"><thead><tr>
						<th>${OJ.t("الاسم", "Name")}</th><th>${OJ.t("البريد", "Email")}</th>
						<th>${OJ.t("الدور", "Role")}</th><th></th>
					</tr></thead><tbody>${rows}</tbody></table>`);
					$demoPanel.append(`<p class="oj-muted" style="margin-top:8px">${OJ.t("كلمة المرور", "Password")}: <code>Education@Demo2026</code></p>`);
				}
				$body.append($demoPanel);
			}

			// Academy lifecycle (9 phases)
			const academyPhases = demo.academy_lifecycle || [];
			if (academyPhases.length) {
				$body.append(`<h4 class="oj-section-title">${OJ.t("رحلة الأكاديمية — 9 مراحل", "Academy Lifecycle — 9 Phases")}</h4>`);
				$body.append(
					OJ.workflowJourneyGrid(
						academyPhases.map((p) => ({
							key: p.key,
							icon: p.icon,
							label_ar: p.label_ar,
							label_en: p.label_en,
							role_ar: p.role_ar,
							role_en: p.role_en,
						})),
						() => {}
					)
				);
			}

			if (readiness.portal_readiness_pct != null) {
				$body.append(`
					<div class="oj-panel" style="margin-bottom:16px;padding:10px 14px;background:#fff;border-radius:12px;font-size:0.9rem">
						<strong>${OJ.t("جاهزية البوابات", "Portal Readiness")}:</strong>
						${OJ.esc(String(readiness.portal_readiness_pct))}% ·
						<strong>${OJ.t("مسار الرحلة", "Lifecycle Routing")}:</strong>
						${OJ.esc(String(readiness.lifecycle_routing_pct || "—"))}%
					</div>`);
			}

			if (fullLifecycle.length) {
				$body.append(
					`<h4 class="oj-section-title">${OJ.t("الرحلة الكاملة — من الموقع إلى التخرج", "Full Lifecycle — Website to Graduation")}</h4>`
				);
				$body.append(
					OJ.workflowJourneyGrid(fullLifecycle, (step) => {
						if (step.route) {
							if (step.external) window.open(step.route, "_blank");
							else OJ.navigateRoute(step.route);
						}
					})
				);
			}

			if (steps.length) {
				$body.append(
					`<h4 class="oj-section-title">${OJ.t("رحلة SIS — 12 مرحلة", "SIS Journey — 12 Stages")}</h4>`
				);
				$body.append(
					OJ.workflowJourneyGrid(steps, (step) => {
						if (step.route) OJ.navigateRoute(step.route);
					})
				);
			}

			$body.append(`<h4 class="oj-section-title">${OJ.t("بوابات الأدوار", "Role Portals")}</h4>`);
			$body.append(OJ.portalCategoryGrid(groups));

			// Website portals
			$body.append(`<h4 class="oj-section-title">${OJ.t("بوابات الموقع الخارجي", "External Website Portals")}</h4>`);
			const extLinks = (externalPortals.length ? externalPortals : [
				{ label_ar: "التقديم الإلكتروني", label_en: "Online Application", route: "/education/apply", icon: "🌐" },
			]).map((p) => ({
				label: OJ.t(p.label_ar, p.label_en),
				icon: p.icon || "🌐",
				route: p.route,
			}));
			extLinks.push(
				{ label: OJ.t("بوابة ولي الأمر PWA", "Parent PWA"), icon: "📱", route: "/app/education-parent-mobile" },
				{ label: OJ.t("بوابة الطالب", "Student Portal"), icon: "🎓", route: "/app/education-student-portal" }
			);
			$body.append(OJ.linkGrid(extLinks));

			const $shell = OJ.shell({
				title: OJ.t("ErpGenEx Education", "ErpGenEx Education"),
				subtitle: OJ.t("ErpGenEx — EduSphere", "ErpGenEx — EduSphere"),
				role: OJ.t("مركز العمل", "Workcenter"),
				brandLogoUrl: ctx.logo_url || OJ.educationLogo,
				kpis,
				sidebarRole: "workcenter",
				currentPage: "education-workcenter",
				bodyEl: $body,
				homeRoute: "/app/education-workcenter",
			});
			$mount.empty().append($shell);
		}

		render().catch((e) => OJ.showCallError(e));
	});
};
