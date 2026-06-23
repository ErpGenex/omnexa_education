/* global frappe */
(function () {
	const STORAGE_LANG = "edu_site_lang";

	window.EduSphereSite = {
		config: null,
		lang: localStorage.getItem(STORAGE_LANG) || "ar",
		page: "home",

		init(page) {
			this.page = page || "home";
			this.loadConfig().then(() => {
				this.applyTheme();
				this.renderChrome();
				const fn = this[`init_${this.page}`];
				if (typeof fn === "function") fn.call(this);
			});
		},

		t(key) {
			const map = {
				home: { ar: "الرئيسية", en: "Home" },
				programs: { ar: "البرامج", en: "Programs" },
				institutions: { ar: "المؤسسات", en: "Institutions" },
				apply: { ar: "التقديم", en: "Apply" },
				apply_now: { ar: "قدّم الآن", en: "Apply Now" },
				login: { ar: "دخول", en: "Login" },
				desk: { ar: "مركز العمل", en: "Workcenter" },
				features: { ar: "مميزات EduSphere", en: "EduSphere Features" },
				our_institutions: { ar: "مؤسساتنا التعليمية", en: "Our Institutions" },
				our_programs: { ar: "البرامج الأكاديمية", en: "Academic Programs" },
				students: { ar: "طلاب", en: "Students" },
				teachers: { ar: "معلّمون", en: "Teachers" },
				loading: { ar: "جاري التحميل...", en: "Loading..." },
				submit: { ar: "إرسال الطلب", en: "Submit Application" },
				applicant: { ar: "اسم المتقدّم", en: "Applicant Name" },
				institution: { ar: "المؤسسة", en: "Institution" },
				academic_year: { ar: "السنة الأكاديمية", en: "Academic Year" },
				grade: { ar: "الصف / البرنامج", en: "Grade / Program" },
				guardian_email: { ar: "بريد ولي الأمر", en: "Guardian Email" },
				select: { ar: "اختر", en: "Select" },
				success: { ar: "تم استلام طلبك", en: "Application received" },
				admissions: { ar: "القبول والتسجيل", en: "Admissions" },
				journey: { ar: "رحلة تعليمية متكاملة", en: "Complete education journey" },
				online_apply: { ar: "تقديم أونلاين", en: "Online Application" },
				parent_portal: { ar: "بوابة أولياء الأمور", en: "Parent Portal" },
				student_portal: { ar: "بوابة الطالب", en: "Student Portal" },
				analytics: { ar: "تحليلات وتقارير", en: "Analytics & Reports" },
			};
			return (map[key] && map[key][this.lang]) || key;
		},

		esc(v) {
			return frappe.utils.escape_html(v == null ? "" : String(v));
		},

		nameField() {
			return this.lang === "ar" ? "brand_name_ar" : "brand_name_en";
		},

		textField(base) {
			return this.lang === "ar" ? `${base}_ar` : `${base}_en`;
		},

		async loadConfig() {
			const r = await frappe.call({
				method: "omnexa_education.api.public_education_site.get_site_config",
			});
			this.config = r.message || {};
			if (this.config.primary_color) {
				document.documentElement.style.setProperty("--edu-primary", this.config.primary_color);
			}
		},

		applyTheme() {
			const root = document.querySelector(".edu-site");
			if (!root) return;
			root.dir = this.lang === "ar" ? "rtl" : "ltr";
			root.lang = this.lang;
		},

		toggleLang() {
			this.lang = this.lang === "ar" ? "en" : "ar";
			localStorage.setItem(STORAGE_LANG, this.lang);
			this.applyTheme();
			this.renderChrome();
			const fn = this[`init_${this.page}`];
			if (typeof fn === "function") fn.call(this);
		},

		renderChrome() {
			const cfg = this.config || {};
			const name = cfg[this.nameField()] || "EduSphere";
			const logo = cfg.logo
				? `<img src="${this.esc(cfg.logo)}" alt="" onerror="this.style.display='none'">`
				: "🎓";
			const nav = [
				{ href: "/education", key: "home", page: "home" },
				{ href: "/education/programs", key: "programs", page: "programs" },
				{ href: "/education/apply", key: "apply", page: "apply" },
			];

			const header = document.getElementById("edu-header");
			if (header) {
				header.innerHTML = `
					<div class="edu-wrap edu-header-inner">
						<a class="edu-brand" href="/education">${logo}<span>${this.esc(name)}</span></a>
						<button type="button" class="edu-mobile-toggle" id="edu-menu-toggle">☰</button>
						<nav class="edu-nav" id="edu-nav">
							${nav
								.map(
									(n) =>
										`<a href="${n.href}" class="${this.page === n.page ? "active" : ""}">${this.t(n.key)}</a>`
								)
								.join("")}
						</nav>
						<div class="edu-actions">
							<button type="button" class="edu-lang" id="edu-lang-toggle">${this.lang === "ar" ? "EN" : "AR"}</button>
							<a class="edu-btn edu-btn-outline" href="/login">${this.t("login")}</a>
							<a class="edu-btn edu-btn-primary" href="/education/apply">${this.t("apply_now")}</a>
						</div>
					</div>`;
				document.getElementById("edu-lang-toggle")?.addEventListener("click", () => this.toggleLang());
				document.getElementById("edu-menu-toggle")?.addEventListener("click", () => {
					document.getElementById("edu-nav")?.classList.toggle("open");
				});
			}

			const footer = document.getElementById("edu-footer");
			if (footer) {
				footer.innerHTML = `
					<div class="edu-wrap edu-footer-grid">
						<div>
							<h3>${this.esc(name)}</h3>
							<p>${this.esc(cfg[this.textField("tagline")] || "")}</p>
						</div>
						<div>
							<h4>${this.t("programs")}</h4>
							<p><a href="/education/programs">${this.t("our_programs")}</a></p>
							<p><a href="/education/apply">${this.t("apply_now")}</a></p>
						</div>
						<div>
							<h4>${this.t("desk")}</h4>
							<p><a href="${cfg.urls?.desk || "/app/education-workcenter"}">${this.t("desk")}</a></p>
						</div>
						<div>
							<h4>Eschools</h4>
							<p><a href="${cfg.urls?.laravel_portal || "https://kemetgate.com"}" target="_blank" rel="noopener">kemetgate.com</a></p>
							<p><a href="${cfg.urls?.laravel_login || "https://kemetgate.com/login"}" target="_blank" rel="noopener">${this.t("login")}</a></p>
						</div>
					</div>`;
			}
		},

		init_home() {
			const cfg = this.config || {};
			const hero = document.getElementById("edu-hero");
			if (hero) {
				hero.innerHTML = `
					<div class="edu-wrap edu-hero-grid">
						<div>
							<h1>${this.esc(cfg[this.textField("tagline")] || this.t("journey"))}</h1>
							<p>${this.esc(cfg[this.textField("hero_text")] || "")}</p>
							<div class="edu-hero-cta">
								<a class="edu-btn edu-btn-primary" href="/education/apply">${this.t("apply_now")}</a>
								<a class="edu-btn edu-btn-outline" href="/education/programs" style="color:#fff;border-color:#fff">${this.t("programs")}</a>
								<a class="edu-btn edu-btn-primary" href="${cfg.urls?.laravel_login || "https://kemetgate.com/login"}" target="_blank" rel="noopener">${this.t("student_portal")}</a>
							</div>
						</div>
						<div class="edu-hero-img">
							<img src="${this.esc(cfg.hero_image || "")}" alt="" />
						</div>
					</div>`;
			}

			const features = document.getElementById("edu-features-bar");
			if (features) {
				const items = [
					{ icon: "📋", key: "online_apply" },
					{ icon: "👨‍👩‍👧", key: "parent_portal" },
					{ icon: "🎓", key: "student_portal" },
					{ icon: "📊", key: "analytics" },
				];
				features.innerHTML = items
					.map(
						(i) =>
							`<div class="edu-feature"><div class="edu-feature-icon">${i.icon}</div><strong>${this.t(i.key)}</strong></div>`
					)
					.join("");
			}

			const stats = document.getElementById("edu-stats");
			if (stats && cfg.stats) {
				const s = cfg.stats;
				stats.innerHTML = `
					<div class="edu-wrap edu-stats-grid">
						<div><div class="edu-stat-num">${s.institutions || 0}</div><div>${this.t("institutions")}</div></div>
						<div><div class="edu-stat-num">${s.programs || 0}</div><div>${this.t("programs")}</div></div>
						<div><div class="edu-stat-num">${s.students || 0}</div><div>${this.t("students")}</div></div>
						<div><div class="edu-stat-num">${s.teachers || 0}</div><div>${this.t("teachers")}</div></div>
					</div>`;
			}

			this.renderInstitutions("edu-institutions");
		},

		async renderInstitutions(hostId) {
			const host = document.getElementById(hostId);
			if (!host) return;
			host.innerHTML = `<p>${this.t("loading")}</p>`;
			const r = await frappe.call({
				method: "omnexa_education.api.public_education_site.get_public_institutions",
			});
			const rows = r.message || [];
			host.innerHTML = `
				<div class="edu-card-grid">
					${rows
						.map(
							(row) => `
						<div class="edu-card">
							<span class="edu-badge">${this.esc(row.institution_type || "")}</span>
							<h3>${this.esc(row.institution_name)}</h3>
							<p>${this.esc(row.city || "")}</p>
							<p style="margin-top:12px"><a href="/education/apply?institution=${this.esc(row.name)}">${this.t("apply_now")} →</a></p>
						</div>`
						)
						.join("") || `<p>${this.t("loading")}</p>`}
				</div>`;
		},

		async init_programs() {
			const host = document.getElementById("edu-programs-list");
			if (!host) return;
			host.innerHTML = `<p>${this.t("loading")}</p>`;
			const r = await frappe.call({
				method: "omnexa_education.api.public_education_site.get_public_programs",
			});
			const rows = r.message || [];
			host.innerHTML = `
				<div class="edu-card-grid">
					${rows
						.map(
							(row) => `
						<div class="edu-card">
							<span class="edu-badge">${this.esc(row.program_type || "")}</span>
							<h3>${this.esc(row.program_name)}</h3>
							<p>${this.esc(row.institution_name || row.institution)}</p>
							${row.duration_years ? `<p>${row.duration_years} ${this.lang === "ar" ? "سنوات" : "years"}</p>` : ""}
						</div>`
						)
						.join("") || `<p>—</p>`}
				</div>`;
		},

		init_apply() {
			const host = document.getElementById("edu-apply-form-host");
			if (!host) return;
			const params = new URLSearchParams(window.location.search);
			const preInst = params.get("institution");

			frappe.call({
				method: "omnexa_education.api.education_admissions.get_public_apply_context",
				callback: (r) => {
					const ctx = r.message || {};
					const institutions = ctx.institutions || [];
					const instOpts = institutions
						.map(
							(i) =>
								`<option value="${this.esc(i.name)}" ${preInst === i.name ? "selected" : ""}>${this.esc(i.institution_name)}</option>`
						)
						.join("");

					host.innerHTML = `
						<form id="edu-apply-form">
							<div class="edu-form-group"><label>${this.t("applicant")} *</label>
								<input type="text" name="applicant_name" required /></div>
							<div class="edu-form-group"><label>${this.t("institution")} *</label>
								<select name="institution" required><option value="">${this.t("select")}</option>${instOpts}</select></div>
							<div class="edu-form-group"><label>${this.t("academic_year")} *</label>
								<select name="academic_year" required><option value="">${this.t("select")}</option></select></div>
							<div class="edu-form-group"><label>${this.t("grade")}</label>
								<input type="text" name="grade_level" /></div>
							<div class="edu-form-group"><label>${this.t("guardian_email")}</label>
								<input type="email" name="guardian_email" /></div>
							<button type="submit" class="edu-btn edu-btn-primary" style="width:100%;margin-top:8px">${this.t("submit")}</button>
						</form>
						<div id="edu-apply-result" style="margin-top:12px"></div>`;

					const $inst = host.querySelector('[name="institution"]');
					const $year = host.querySelector('[name="academic_year"]');
					const yearsMap = ctx.academic_years || {};

					const fillYears = () => {
						const inst = $inst.value;
						const years = yearsMap[inst] || [];
						$year.innerHTML =
							`<option value="">${this.t("select")}</option>` +
							years.map((y) => `<option value="${this.esc(y.name)}">${this.esc(y.title || y.name)}</option>`).join("");
					};
					$inst.addEventListener("change", fillYears);
					if (preInst) fillYears();

					host.querySelector("#edu-apply-form").addEventListener("submit", (e) => {
						e.preventDefault();
						const fd = Object.fromEntries(new FormData(e.target).entries());
						frappe.call({
							method: "omnexa_education.api.education_admissions.submit_online_application",
							args: fd,
							callback(res) {
								document.getElementById("edu-apply-result").innerHTML = `<div style="color:#0d6e3a;padding:12px;background:#e8f5e9;border-radius:8px">${EduSphereSite.t("success")}: <strong>${EduSphereSite.esc(res.message.application)}</strong></div>`;
							},
							error(err) {
								document.getElementById("edu-apply-result").innerHTML = `<div style="color:#c62828">${EduSphereSite.esc(err.message || "Error")}</div>`;
							},
						});
					});
				},
			});
		},
	};
})();
