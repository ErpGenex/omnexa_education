/* global frappe */
(function () {
	const STORAGE_LANG = "edu_site_lang";

	const JOURNEY_STEPS = [
		{ ar: "استفسار", en: "Inquiry", desc_ar: "تقديم أونلاين", desc_en: "Online apply" },
		{ ar: "قبول", en: "Admission", desc_ar: "مراجعة الطلب", desc_en: "Application review" },
		{ ar: "تسجيل", en: "Enrollment", desc_ar: "المسجل الأكاديمي", desc_en: "Registrar desk" },
		{ ar: "تعلّم", en: "Learning", desc_ar: "kemetgate TLMS", desc_en: "kemetgate TLMS" },
		{ ar: "تخرج", en: "Graduation", desc_ar: "شهادات وخريجون", desc_en: "Alumni & credentials" },
	];

	const ROLES = [
		{ icon: "🏛️", ar: "تنفيذي", en: "Executive" },
		{ icon: "📋", ar: "قبول", en: "Admissions" },
		{ icon: "📚", ar: "مسجل", en: "Registrar" },
		{ icon: "👨‍🏫", ar: "معلّم", en: "Teacher" },
		{ icon: "🎓", ar: "طالب", en: "Student" },
		{ icon: "👨‍👩‍👧", ar: "ولي أمر", en: "Parent" },
		{ icon: "💰", ar: "مالية", en: "Finance" },
		{ icon: "📊", ar: "تحليلات", en: "Analytics" },
		{ icon: "✅", ar: "جودة", en: "QA" },
	];

	window.EduSphereSite = {
		config: null,
		lang: localStorage.getItem(STORAGE_LANG) || "ar",
		page: "home",
		_programsCache: null,
		_programFilter: "all",

		init(page) {
			this.page = page || "home";
			this.loadConfig().then(() => {
				this.applyTheme();
				this.renderChrome();
				this.setupReveal();
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
				journey_title: { ar: "رحلة الطالب المتكاملة", en: "Complete Student Journey" },
				journey_sub: { ar: "من أول استفسار حتى التخرج — إدارة واحدة", en: "From first inquiry to graduation" },
				roles_title: { ar: "بوابات لكل دور", en: "Portal for Every Role" },
				roles_sub: { ar: "تسعة أدوار — لوحة مخصصة لكل مستوى", en: "Nine roles — tailored dashboards" },
				cta_title: { ar: "جاهزون لرفع تجربة التعليم؟", en: "Ready to elevate education?" },
				cta_sub: {
					ar: "انضم إلى مؤسسات EduSphere أو سجّل دخولك إلى المنصة التعليمية",
					en: "Join EduSphere institutions or sign in to the learning platform",
				},
				online_apply: { ar: "تقديم أونلاين", en: "Online Application" },
				parent_portal: { ar: "بوابة أولياء الأمور", en: "Parent Portal" },
				student_portal: { ar: "بوابة الطالب", en: "Student Portal" },
				analytics: { ar: "تحليلات وتقارير", en: "Analytics & Reports" },
				lms: { ar: "منصة التعلّم", en: "Learning Platform" },
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
				all_programs: { ar: "الكل", en: "All" },
				trust_iso: { ar: "معايير دولية", en: "Global Standards" },
				trust_sis: { ar: "SIS متكامل", en: "Integrated SIS" },
				trust_lms: { ar: "ربط kemetgate", en: "kemetgate Linked" },
				trust_secure: { ar: "أمان وحوكمة", en: "Security & Governance" },
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

		setupReveal() {
			const els = document.querySelectorAll(".edu-reveal");
			if (!els.length || !("IntersectionObserver" in window)) {
				els.forEach((el) => el.classList.add("edu-visible"));
				return;
			}
			const obs = new IntersectionObserver(
				(entries) => {
					entries.forEach((e) => {
						if (e.isIntersecting) {
							e.target.classList.add("edu-visible");
							obs.unobserve(e.target);
						}
					});
				},
				{ threshold: 0.12 }
			);
			els.forEach((el) => obs.observe(el));
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
						<button type="button" class="edu-mobile-toggle" id="edu-menu-toggle" aria-label="Menu">☰</button>
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
							<p style="margin-top:12px;opacity:0.7">EduSphere · ErpGenEx Education</p>
						</div>
						<div>
							<h4>${this.t("programs")}</h4>
							<p><a href="/education/programs">${this.t("programs")}</a></p>
							<p><a href="/education/apply">${this.t("apply_now")}</a></p>
						</div>
						<div>
							<h4>${this.t("desk")}</h4>
							<p><a href="${cfg.urls?.desk || "/app/education-workcenter"}">${this.t("desk")}</a></p>
						</div>
						<div>
							<h4>Eschools · kemetgate</h4>
							<p><a href="${cfg.urls?.laravel_portal || "https://kemetgate.com"}" target="_blank" rel="noopener">kemetgate.com</a></p>
							<p><a href="${cfg.urls?.laravel_login || "https://kemetgate.com/login"}" target="_blank" rel="noopener">${this.t("login")}</a></p>
						</div>
					</div>
					<div class="edu-wrap edu-footer-bottom">© ${new Date().getFullYear()} ${this.esc(name)} · ${this.lang === "ar" ? "جميع الحقوق محفوظة" : "All rights reserved"}</div>`;
			}
		},

		init_home() {
			const cfg = this.config || {};
			const hero = document.getElementById("edu-hero");
			if (hero) {
				hero.innerHTML = `
					<div class="edu-wrap edu-hero-grid">
						<div>
							<span class="edu-eyebrow">EduSphere · World-Class SIS</span>
							<h1>${this.esc(cfg[this.textField("tagline")] || "")}</h1>
							<p class="edu-hero-lead">${this.esc(cfg[this.textField("hero_text")] || "")}</p>
							<div class="edu-hero-cta">
								<a class="edu-btn edu-btn-gold" href="/education/apply">${this.t("apply_now")}</a>
								<a class="edu-btn edu-btn-ghost-light" href="/education/programs">${this.t("programs")}</a>
								<a class="edu-btn edu-btn-ghost-light" href="${cfg.urls?.laravel_portal || "https://kemetgate.com"}" target="_blank" rel="noopener">${this.t("lms")}</a>
							</div>
						</div>
						<div class="edu-hero-visual">
							<div class="edu-hero-img">
								<img src="${this.esc(cfg.hero_image || "")}" alt="" loading="lazy" />
							</div>
							<div class="edu-hero-float"><span>🎓</span> ${this.lang === "ar" ? "من القبول إلى التخرج" : "Admissions to Alumni"}</div>
						</div>
					</div>`;
			}

			const trust = document.getElementById("edu-trust-strip");
			if (trust) {
				trust.innerHTML = `
					<div class="edu-wrap edu-trust-inner">
						<span>✓ <strong>${this.t("trust_iso")}</strong></span>
						<span>✓ <strong>${this.t("trust_sis")}</strong></span>
						<span>✓ <strong>${this.t("trust_lms")}</strong></span>
						<span>✓ <strong>${this.t("trust_secure")}</strong></span>
					</div>`;
			}

			const features = document.getElementById("edu-features-bar");
			if (features) {
				const items = [
					{ icon: "📋", key: "online_apply", sub_ar: "طلب قبول رقمي", sub_en: "Digital admissions" },
					{ icon: "👨‍👩‍👧", key: "parent_portal", sub_ar: "متابعة الأبناء", sub_en: "Child progress" },
					{ icon: "🎓", key: "student_portal", sub_ar: "تعلّم ونتائج", sub_en: "Learning & grades" },
					{ icon: "📊", key: "analytics", sub_ar: "قرارات مبنية على بيانات", sub_en: "Data-driven decisions" },
				];
				features.innerHTML = items
					.map(
						(i) => `
					<div class="edu-feature">
						<div class="edu-feature-icon">${i.icon}</div>
						<strong>${this.t(i.key)}</strong>
						<small>${this.lang === "ar" ? i.sub_ar : i.sub_en}</small>
					</div>`
					)
					.join("");
			}

			const stats = document.getElementById("edu-stats");
			if (stats && cfg.stats) {
				const s = cfg.stats;
				stats.innerHTML = `
					<div class="edu-wrap edu-stats-grid">
						<div><div class="edu-stat-num">${s.institutions || 0}</div><div class="edu-stat-label">${this.t("institutions")}</div></div>
						<div><div class="edu-stat-num">${s.programs || 0}</div><div class="edu-stat-label">${this.t("programs")}</div></div>
						<div><div class="edu-stat-num">${s.students || 0}</div><div class="edu-stat-label">${this.t("students")}</div></div>
						<div><div class="edu-stat-num">${s.teachers || 0}</div><div class="edu-stat-label">${this.t("teachers")}</div></div>
					</div>`;
			}

			const journey = document.getElementById("edu-journey-section");
			if (journey) {
				journey.innerHTML = `
					<div class="edu-wrap">
						<div class="edu-section-title">
							<span class="edu-eyebrow">Student Lifecycle</span>
							<h2>${this.t("journey_title")}</h2>
							<p>${this.t("journey_sub")}</p>
						</div>
						<div class="edu-journey">
							${JOURNEY_STEPS.map(
								(step, i) => `
								<div class="edu-journey-step">
									<div class="edu-journey-num">${i + 1}</div>
									<h4>${this.lang === "ar" ? step.ar : step.en}</h4>
									<p>${this.lang === "ar" ? step.desc_ar : step.desc_en}</p>
								</div>`
							).join("")}
						</div>
					</div>`;
			}

			const roles = document.getElementById("edu-roles-section");
			if (roles) {
				roles.innerHTML = `
					<div class="edu-wrap">
						<div class="edu-section-title">
							<span class="edu-eyebrow edu-eyebrow-light">Role-Based Access</span>
							<h2>${this.t("roles_title")}</h2>
							<p>${this.t("roles_sub")}</p>
						</div>
						<div class="edu-roles-grid">
							${ROLES.map(
								(r) => `
								<div class="edu-role-card">
									<div class="edu-role-icon">${r.icon}</div>
									<span>${this.lang === "ar" ? r.ar : r.en}</span>
								</div>`
							).join("")}
						</div>
					</div>`;
			}

			const cta = document.getElementById("edu-cta-band");
			if (cta) {
				cta.innerHTML = `
					<div class="edu-wrap">
						<h2>${this.t("cta_title")}</h2>
						<p>${this.t("cta_sub")}</p>
						<div class="edu-cta-actions">
							<a class="edu-btn edu-btn-gold" href="/education/apply">${this.t("apply_now")}</a>
							<a class="edu-btn edu-btn-ghost-light" href="${cfg.urls?.laravel_login || "https://kemetgate.com/login"}" target="_blank" rel="noopener">${this.t("login")}</a>
						</div>
					</div>`;
			}

			this.renderInstitutions("edu-institutions");
		},

		async renderInstitutions(hostId) {
			const host = document.getElementById(hostId);
			if (!host) return;
			host.innerHTML = `<p style="text-align:center">${this.t("loading")}</p>`;
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
							<a class="edu-card-link" href="/education/apply?institution=${encodeURIComponent(row.name)}">${this.t("apply_now")} →</a>
						</div>`
						)
						.join("") || `<p style="text-align:center">—</p>`}
				</div>`;
		},

		async init_programs() {
			const filterHost = document.getElementById("edu-program-filters");
			const host = document.getElementById("edu-programs-list");
			if (!host) return;

			host.innerHTML = `<p style="text-align:center">${this.t("loading")}</p>`;
			const r = await frappe.call({
				method: "omnexa_education.api.public_education_site.get_public_programs",
			});
			this._programsCache = r.message || [];
			const types = [...new Set(this._programsCache.map((p) => p.program_type || p.institution_type).filter(Boolean))];

			if (filterHost) {
				filterHost.innerHTML = `
					<button type="button" class="edu-filter-btn active" data-filter="all">${this.t("all_programs")}</button>
					${types
						.map((t) => `<button type="button" class="edu-filter-btn" data-filter="${this.esc(t)}">${this.esc(t)}</button>`)
						.join("")}`;
				filterHost.querySelectorAll(".edu-filter-btn").forEach((btn) => {
					btn.addEventListener("click", () => {
						filterHost.querySelectorAll(".edu-filter-btn").forEach((b) => b.classList.remove("active"));
						btn.classList.add("active");
						this._programFilter = btn.dataset.filter;
						this._renderProgramsList(host);
					});
				});
			}
			this._renderProgramsList(host);
		},

		_renderProgramsList(host) {
			let rows = this._programsCache || [];
			if (this._programFilter !== "all") {
				rows = rows.filter(
					(p) => (p.program_type || p.institution_type) === this._programFilter
				);
			}
			host.innerHTML = `
				<div class="edu-card-grid">
					${rows
						.map(
							(row) => `
						<div class="edu-card">
							<span class="edu-badge">${this.esc(row.program_type || row.degree_level || "")}</span>
							<h3>${this.esc(row.program_name)}</h3>
							<p>${this.esc(row.institution_name || row.institution)}</p>
							${row.duration_years ? `<p>${row.duration_years} ${this.lang === "ar" ? "سنوات" : "years"}</p>` : ""}
							<a class="edu-card-link" href="/education/apply?institution=${encodeURIComponent(row.institution || "")}">${this.t("apply_now")} →</a>
						</div>`
						)
						.join("") || `<p style="text-align:center">—</p>`}
				</div>`;
		},

		init_apply() {
			const aside = document.getElementById("edu-apply-aside");
			if (aside) {
				const steps =
					this.lang === "ar"
						? [
								"املأ بيانات المتقدّم والمؤسسة",
								"اختر السنة الأكاديمية والبرنامج",
								"سيتم مراجعة طلبك من القبول",
								"بعد القبول: حساب طالب + بوابة kemetgate",
							]
						: [
								"Fill applicant and institution details",
								"Select academic year and program",
								"Admissions team will review your application",
								"After acceptance: student account + kemetgate portal",
							];
				aside.innerHTML = `
					<h3>${this.lang === "ar" ? "خطوات التقديم" : "Application Steps"}</h3>
					<ul>${steps.map((s, i) => `<li><span>${i + 1}.</span> ${s}</li>`).join("")}</ul>`;
			}

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
								<input type="text" name="applicant_name" required autocomplete="name" /></div>
							<div class="edu-form-group"><label>${this.t("institution")} *</label>
								<select name="institution" required><option value="">${this.t("select")}</option>${instOpts}</select></div>
							<div class="edu-form-group"><label>${this.t("academic_year")} *</label>
								<select name="academic_year" required><option value="">${this.t("select")}</option></select></div>
							<div class="edu-form-group"><label>${this.t("grade")}</label>
								<input type="text" name="grade_level" /></div>
							<div class="edu-form-group"><label>${this.t("guardian_email")}</label>
								<input type="email" name="guardian_email" autocomplete="email" /></div>
							<button type="submit" class="edu-btn edu-btn-primary" style="width:100%;margin-top:12px;padding:14px">${this.t("submit")}</button>
						</form>
						<div id="edu-apply-result" style="margin-top:16px"></div>`;

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
								document.getElementById("edu-apply-result").innerHTML = `<div style="color:#0d6e3a;padding:16px;background:#ecfdf5;border-radius:12px;border:1px solid #a7f3d0">${EduSphereSite.t("success")}: <strong>${EduSphereSite.esc(res.message.application)}</strong></div>`;
							},
							error(err) {
								document.getElementById("edu-apply-result").innerHTML = `<div style="color:#c62828;padding:12px">${EduSphereSite.esc(err.message || "Error")}</div>`;
							},
						});
					});
				},
			});
		},
	};
})();
