/* global frappe */
(function () {
	const STORAGE_LANG = "edu_site_lang";

	const JOURNEY_STEPS = [
		{ ar: "استفسار", en: "Inquiry", desc_ar: "تقديم أونلاين", desc_en: "Online apply", icon: "📩" },
		{ ar: "قبول", en: "Admission", desc_ar: "مراجعة الطلب", desc_en: "Application review", icon: "📋" },
		{ ar: "تسجيل", en: "Enrollment", desc_ar: "المسجل الأكاديمي", desc_en: "Registrar desk", icon: "🎓" },
		{ ar: "جدول", en: "Timetable", desc_ar: "محاضرات وحصص", desc_en: "Classes & labs", icon: "📅" },
		{ ar: "حضور", en: "Attendance", desc_ar: "متابعة يومية", desc_en: "Daily tracking", icon: "✅" },
		{ ar: "تقييم", en: "Assessment", desc_ar: "اختبارات ومشاريع", desc_en: "Exams & projects", icon: "📝" },
		{ ar: "درجات", en: "Grading", desc_ar: "كشوف النتائج", desc_en: "Grade reports", icon: "📊" },
		{ ar: "تعلّم", en: "Learning", desc_ar: "kemetgate TLMS", desc_en: "kemetgate TLMS", icon: "💻" },
		{ ar: "تخرج", en: "Graduation", desc_ar: "شهادات وخريجون", desc_en: "Alumni & credentials", icon: "🏅" },
	];

	const NAV_MEGA = [
		{
			key: "about",
			ar: "عن الجامعة",
			en: "About",
			items: [
				{ href: "/education#edu-colleges-section", ar: "الكليات والمدارس", en: "Colleges & Schools" },
				{ href: "/education#edu-partners-section", ar: "شركاؤنا", en: "Partners" },
				{ href: "/education#edu-news-section", ar: "الأخبار", en: "News" },
			],
		},
		{
			key: "academics",
			ar: "أكاديمي",
			en: "Academics",
			items: [
				{ href: "/education/programs", ar: "البرامج والتخصصات", en: "Programs & Majors" },
				{ href: "/education#edu-colleges-section", ar: "الكليات", en: "Colleges" },
				{ href: "/education#edu-scholarships-section", ar: "المنح الدراسية", en: "Scholarships" },
			],
		},
		{
			key: "admissions",
			ar: "القبول والتسجيل",
			en: "Admissions",
			items: [
				{ href: "/education/apply", ar: "التقديم الأونلاين", en: "Online Application" },
				{ href: "/education#edu-admission-band", ar: "خطوات القبول", en: "Admission Steps" },
				{ href: "/education#edu-international-section", ar: "الطلاب الدوليون", en: "International Students" },
			],
		},
		{
			key: "portals",
			ar: "البوابات",
			en: "Portals",
			items: [
				{ href: "__DESK__/education-student-portal", ar: "بوابة الطالب", en: "Student Portal" },
				{ href: "__DESK__/education-parent-mobile", ar: "بوابة ولي الأمر", en: "Parent Portal" },
				{ href: "__DESK__/education-teacher-gradebook", ar: "بوابة أعضاء هيئة التدريس", en: "Faculty Portal" },
				{ href: "__DESK__/education-workcenter", ar: "الإدارة", en: "Administration" },
			],
		},
	];

	const DEFAULT_CATALOG = {
		colleges: [
			{ key: "medicine", name_ar: "كلية الطب", name_en: "Faculty of Medicine", programs: 12, image: "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=800&q=80" },
			{ key: "engineering", name_ar: "كلية الهندسة", name_en: "Faculty of Engineering", programs: 18, image: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80" },
			{ key: "ai", name_ar: "كلية الذكاء الاصطناعي", name_en: "Faculty of AI", programs: 9, image: "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=800&q=80" },
			{ key: "business", name_ar: "كلية الأعمال", name_en: "Faculty of Business", programs: 14, image: "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=800&q=80" },
			{ key: "cs", name_ar: "كلية الحاسبات", name_en: "Faculty of Computing", programs: 11, image: "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=800&q=80" },
			{ key: "science", name_ar: "كلية العلوم", name_en: "Faculty of Science", programs: 10, image: "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=800&q=80" },
		],
		gallery: [
			"https://images.unsplash.com/photo-1541339907198-e08756dedf6d?auto=format&fit=crop&w=800&q=80",
			"https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=800&q=80",
			"https://images.unsplash.com/photo-1571260899304-425eee4c7efc?auto=format&fit=crop&w=800&q=80",
			"https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=800&q=80",
		],
		news: [
			{ tag_ar: "إعلان", tag_en: "Announcement", title_ar: "فتح باب القبول للفصل الجديد", title_en: "New Semester Admissions Open", date: "2026-06-01", image: "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=600&q=70" },
			{ tag_ar: "خبر", tag_en: "News", title_ar: "اعتماد دولي جديد للبرامج الأكاديمية", title_en: "New International Accreditation", date: "2026-05-15", image: "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=600&q=70" },
		],
		scholarships: [
			{ name_ar: "منح التفوق الأكاديمي", name_en: "Merit Scholarships", desc_ar: "للطلاب المتفوقين أكاديمياً", desc_en: "For academically outstanding students" },
			{ name_ar: "منح الرياضة", name_en: "Sports Scholarships", desc_ar: "دعم المواهب الرياضية", desc_en: "Supporting athletic talent" },
		],
		institution_types: [
			{ institution_type: "University", name: "University", name_ar: "جامعة", active: false, inactive: false, seeded: false, image: "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=800&q=80" },
			{ institution_type: "International School", name: "International School", name_ar: "مدرسة دولية", active: false, inactive: false, seeded: false, image: "https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&w=800&q=80" },
			{ institution_type: "Academy", name: "Academy", name_ar: "أكاديمية", active: false, inactive: false, seeded: false, image: "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=80" },
		],
	};

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
			this.config = this.defaultConfig();
			this.applyTheme();
			this.renderChrome();
			this.loadConfig()
				.then(() => {
					this.applyTheme();
					this.renderChrome();
					const fn = this[`init_${this.page}`];
					if (typeof fn === "function") fn.call(this);
					this.setupReveal();
				})
				.catch(() => {
					this.config = this.config || this.defaultConfig();
					this.renderChrome();
					const fn = this[`init_${this.page}`];
					if (typeof fn === "function") fn.call(this);
					this.setupReveal();
				});
		},

		defaultConfig() {
			return {
				brand_name_ar: "Omnexa Education",
				brand_name_en: "Omnexa Education",
				tagline_ar: "ابنِ مستقبلك مع مؤسسة تعليمية عالمية",
				tagline_en: "Build your future with a world-class education institution",
				hero_text_ar: "القبول والتسجيل والتعلم والخدمات الطلابية في منصة واحدة متكاملة",
				hero_text_en: "Admissions, enrollment, learning, and student services in one integrated platform",
				hero_image: "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=1920&q=85",
				hero_video_poster: "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=1920&q=85",
				logo: "/assets/omnexa_education/logo.png",
				primary_color: "#003366",
				secondary_color: "#0A5FA8",
				accent_color: "#00B4D8",
				gold_color: "#D4AF37",
				colleges: DEFAULT_CATALOG.colleges,
				gallery: DEFAULT_CATALOG.gallery,
				news: DEFAULT_CATALOG.news,
				scholarships: DEFAULT_CATALOG.scholarships,
				institution_types: DEFAULT_CATALOG.institution_types,
				hero_stats: { students: 100000, programs: 500, colleges: 25, countries: 50 },
				stats: { institutions: 5, programs: 0, students: 0, teachers: 0 },
				urls: {
					home: "/education",
					programs: "/education/programs",
					apply: "/education/apply",
					desk: "/app/education-workcenter",
					student_portal: "/app/education-student-portal",
					parent_portal: "/app/education-parent-mobile",
					faculty_portal: "/app/education-teacher-gradebook",
					laravel_portal: "https://kemetgate.com",
					laravel_login: "https://kemetgate.com/login",
				},
			};
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
			if (typeof frappe !== "undefined" && frappe.utils && frappe.utils.escape_html) {
				return frappe.utils.escape_html(v == null ? "" : String(v));
			}
			const d = document.createElement("div");
			d.textContent = v == null ? "" : String(v);
			return d.innerHTML;
		},

		deskPortalHref(page) {
			const dest = `/app/${String(page || "").replace(/^\/+/, "")}`;
			const user = typeof frappe !== "undefined" && frappe.session ? frappe.session.user : "Guest";
			if (user && user !== "Guest") return dest;
			return `/login?redirect-to=${encodeURIComponent(dest)}`;
		},

		resolveHref(href) {
			if (!href) return "#";
			if (href.startsWith("__DESK__/")) {
				return this.deskPortalHref(href.slice("__DESK__/".length));
			}
			return href;
		},

		nameField() {
			return this.lang === "ar" ? "brand_name_ar" : "brand_name_en";
		},

		textField(base) {
			return this.lang === "ar" ? `${base}_ar` : `${base}_en`;
		},

		async loadConfig() {
			try {
				if (typeof frappe !== "undefined" && frappe.call) {
					const r = await frappe.call({
						method: "omnexa_education.api.public_education_site.get_site_config",
					});
					this.config = Object.assign(this.defaultConfig(), r.message || {});
				} else {
					const res = await fetch("/api/method/omnexa_education.api.public_education_site.get_site_config");
					const data = await res.json();
					this.config = Object.assign(this.defaultConfig(), data.message || {});
				}
			} catch (e) {
				this.config = this.config || this.defaultConfig();
			}
			if (this.config.primary_color) {
				document.documentElement.style.setProperty("--edu-primary", this.config.primary_color);
			}
			if (this.config.secondary_color) {
				document.documentElement.style.setProperty("--edu-secondary", this.config.secondary_color);
			}
			if (this.config.accent_color) {
				document.documentElement.style.setProperty("--edu-teal", this.config.accent_color);
			}
			if (this.config.gold_color) {
				document.documentElement.style.setProperty("--edu-gold", this.config.gold_color);
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
			const cfg = this.config || this.defaultConfig();
			const name = cfg[this.nameField()] || "EduSphere";
			const logo = cfg.logo
				? `<img src="${this.esc(cfg.logo)}" alt="" onerror="this.style.display='none'">`
				: "🎓";
			const nav = [
				{ href: "/education", key: "home", page: "home" },
				{ href: "/education#edu-colleges-section", ar: "الكليات", en: "Colleges", page: "" },
				{ href: "/education/programs", key: "programs", page: "programs" },
				{ href: "/education#edu-gallery-section", ar: "الأنشطة", en: "Activities", page: "" },
				{ href: "/education#edu-news-section", ar: "الأخبار", en: "News", page: "" },
				{ href: "/education/apply", key: "apply", page: "apply" },
			];
			const megaHtml = NAV_MEGA.map(
				(m) => `
				<div class="edu-mega-item">
					<button type="button" class="edu-mega-trigger">${this.lang === "ar" ? m.ar : m.en} ▾</button>
					<div class="edu-mega-panel">
						${m.items
							.map(
								(it) =>
									`<a href="${this.esc(this.resolveHref(it.href))}" ${it.external ? 'target="_blank" rel="noopener"' : ""}>${this.lang === "ar" ? it.ar : it.en}</a>`
							)
							.join("")}
					</div>
				</div>`
			).join("");

			const header = document.getElementById("edu-header");
			if (header) {
				header.innerHTML = `
					<div class="edu-topbar"><div class="edu-wrap edu-topbar-inner">
						<span>📞 +966 11 000 0000</span>
						<span>✉ admissions@omnexa.education</span>
						<span class="edu-topbar-links">
							<a href="${this.esc(this.deskPortalHref("education-teacher-gradebook"))}">${this.lang === "ar" ? "أعضاء هيئة التدريس" : "Faculty"}</a>
							<a href="${this.esc(this.deskPortalHref("education-student-portal"))}">${this.lang === "ar" ? "الطلاب" : "Students"}</a>
							<a href="${this.esc(this.deskPortalHref("education-parent-mobile"))}">${this.lang === "ar" ? "أولياء الأمور" : "Parents"}</a>
						</span>
					</div></div>
					<div class="edu-wrap edu-header-inner">
						<a class="edu-brand" href="/education">${logo}<span>${this.esc(name)}</span></a>
						<button type="button" class="edu-mobile-toggle" id="edu-menu-toggle" aria-label="Menu">☰</button>
						<nav class="edu-nav" id="edu-nav">
							${nav
								.map((n) => {
									const label = n.key ? this.t(n.key) : this.lang === "ar" ? n.ar : n.en;
									const active = n.page && this.page === n.page ? "active" : "";
									return `<a href="${n.href}" class="${active}">${label}</a>`;
								})
								.join("")}
							${megaHtml}
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
				const u = cfg.urls || {};
				footer.innerHTML = `
					<div class="edu-wrap edu-footer-grid edu-footer-premium">
						<div>
							<h3>${this.esc(name)}</h3>
							<p>${this.esc(cfg[this.textField("hero_text")] || "")}</p>
							<p class="edu-footer-contact">📞 +966 11 000 0000 · ✉ admissions@omnexa.education</p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "الكليات" : "Colleges"}</h4>
							<p><a href="/education#edu-colleges-section">${this.lang === "ar" ? "الطب والهندسة" : "Medicine & Engineering"}</a></p>
							<p><a href="/education/programs">${this.t("programs")}</a></p>
							<p><a href="/education#edu-scholarships-section">${this.lang === "ar" ? "المنح" : "Scholarships"}</a></p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "القبول" : "Admissions"}</h4>
							<p><a href="/education/apply">${this.t("apply_now")}</a></p>
							<p><a href="/education#edu-admission-band">${this.lang === "ar" ? "خطوات التقديم" : "How to Apply"}</a></p>
							<p><a href="/education#edu-international-section">${this.lang === "ar" ? "الطلاب الدوليون" : "International"}</a></p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "البوابات" : "Portals"}</h4>
							<p><a href="${this.esc(this.deskPortalHref("education-student-portal"))}">${this.t("student_portal")}</a></p>
							<p><a href="${this.esc(this.deskPortalHref("education-parent-mobile"))}">${this.t("parent_portal")}</a></p>
							<p><a href="${this.esc(this.deskPortalHref("education-teacher-gradebook"))}">${this.lang === "ar" ? "هيئة التدريس" : "Faculty"}</a></p>
							<p><a href="${this.esc(this.deskPortalHref("education-workcenter"))}">${this.t("desk")}</a></p>
						</div>
					</div>
					<div class="edu-wrap edu-footer-bottom">© ${new Date().getFullYear()} ${this.esc(name)} · Omnexa · ErpGenEx</div>`;
			}
		},

		init_home() {
			const cfg = this.config || {};
			const heroImg = cfg.hero_video_poster || cfg.hero_image || "";
			const hs = cfg.hero_stats || {};
			const hero = document.getElementById("edu-hero");
			if (hero) {
				hero.innerHTML = `
					<div class="edu-hero-bg" style="background-image:url('${this.esc(heroImg)}')"></div>
					<div class="edu-hero-overlay"></div>
					<div class="edu-wrap edu-hero-premium-inner">
						<span class="edu-eyebrow edu-eyebrow-light">Omnexa Education · World-Class</span>
						<h1>${this.esc(cfg[this.textField("tagline")] || "")}</h1>
						<p class="edu-hero-lead">${this.esc(cfg[this.textField("hero_text")] || "")}</p>
						<div class="edu-hero-cta">
							<a class="edu-btn edu-btn-accent" href="/education/apply">${this.lang === "ar" ? "ابدأ التقديم" : "Start Application"}</a>
							<a class="edu-btn edu-btn-ghost-light" href="/education/programs">${this.lang === "ar" ? "استكشف البرامج" : "Explore Programs"}</a>
						</div>
						<div class="edu-hero-stats">
							<div><strong>${this._fmtNum(hs.students || 100000)}+</strong><span>${this.t("students")}</span></div>
							<div><strong>${this._fmtNum(hs.programs || 500)}+</strong><span>${this.t("programs")}</span></div>
							<div><strong>${hs.colleges || 25}+</strong><span>${this.lang === "ar" ? "كلية" : "Colleges"}</span></div>
							<div><strong>${hs.countries || 50}+</strong><span>${this.lang === "ar" ? "دولة" : "Countries"}</span></div>
						</div>
					</div>`;
			}

			const trust = document.getElementById("edu-trust-strip");
			if (trust) {
				const values = [
					{ icon: "🌍", ar: "تعليم عالمي", en: "Global Education" },
					{ icon: "🏛️", ar: "كليات متنوعة", en: "Diverse Colleges" },
					{ icon: "🏫", ar: "مدارس دولية", en: "International Schools" },
					{ icon: "🎓", ar: "حياة طلابية", en: "Student Life" },
					{ icon: "🤝", ar: "دعم متكامل", en: "Integrated Support" },
				];
				trust.innerHTML = `<div class="edu-wrap edu-value-inner">${values
					.map((v) => `<div class="edu-value-item"><span>${v.icon}</span><strong>${this.lang === "ar" ? v.ar : v.en}</strong></div>`)
					.join("")}</div>`;
			}

			this.renderColleges("edu-colleges-section");

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
				const steps = (cfg.lifecycle_phases || JOURNEY_STEPS).map((step, i) => ({
					icon: step.icon || JOURNEY_STEPS[i % JOURNEY_STEPS.length]?.icon || "•",
					ar: step.label_ar || step.ar,
					en: step.label_en || step.en,
					desc_ar: step.role_ar || step.desc_ar,
					desc_en: step.role_en || step.desc_en,
				}));
				journey.innerHTML = `
					<div class="edu-wrap">
						<div class="edu-section-title">
							<span class="edu-eyebrow">Student Lifecycle</span>
							<h2>${this.t("journey_title")}</h2>
							<p>${this.t("journey_sub")}</p>
						</div>
						<div class="edu-journey edu-journey-full">
							${steps
								.map(
									(step, i) => `
								<div class="edu-journey-step">
									<div class="edu-journey-num">${step.icon || i + 1}</div>
									<h4>${this.lang === "ar" ? step.ar : step.en}</h4>
									<p>${this.lang === "ar" ? step.desc_ar : step.desc_en}</p>
								</div>`
								)
								.join("")}
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

			this.renderInstitutionTypes("edu-institution-types");
			this.renderAdmissionBand("edu-admission-band");
			this.renderServices("edu-services-section");
			this.renderGallery("edu-gallery-section");
			this.renderInternational("edu-international-section");
			this.renderOnlineLearning("edu-online-section");
			this.renderScholarships("edu-scholarships-section");
			this.renderNews("edu-news-section");
			this.renderPartners("edu-partners-section");
			this.renderInstitutions("edu-institutions");
		},

		_fmtNum(n) {
			const v = Number(n) || 0;
			return v >= 1000 ? Math.round(v / 1000) + "K" : String(v);
		},

		renderColleges(hostId) {
			const host = document.getElementById(hostId);
			if (!host) return;
			const colleges = (this.config && this.config.colleges) || [];
			host.innerHTML = `
				<div class="edu-wrap">
					<div class="edu-section-title">
						<span class="edu-eyebrow">Academic Excellence</span>
						<h2>${this.lang === "ar" ? "الكليات والمدارس" : "Colleges & Schools"}</h2>
						<p>${this.lang === "ar" ? "برامج أكاديمية متميزة في بيئة تعليمية عالمية" : "Premium academic programs in a world-class environment"}</p>
					</div>
					<div class="edu-college-grid">
						${colleges
							.map(
								(c) => `
							<div class="edu-college-card">
								<div class="edu-college-img"><img src="${this.esc(c.image)}" alt="" loading="lazy" onerror="this.src='/assets/omnexa_education/logo.png'" /></div>
								<div class="edu-college-body">
									<h3>${this.esc(this.lang === "ar" ? c.name_ar : c.name_en)}</h3>
									<p>${c.programs || 0} ${this.lang === "ar" ? "برنامج" : "programs"}</p>
									<a class="edu-btn edu-btn-sm edu-btn-primary" href="/education/apply">${this.t("apply_now")}</a>
								</div>
							</div>`
							)
							.join("")}
					</div>
					<div class="edu-section-cta"><a class="edu-btn edu-btn-outline" href="/education/programs">${this.lang === "ar" ? "عرض جميع الكليات" : "View All Colleges"}</a></div>
				</div>`;
		},

		renderAdmissionBand(hostId) {
			const host = document.getElementById(hostId);
			if (!host) return;
			const steps =
				this.lang === "ar"
					? [
							{ icon: "👤", t: "إنشاء حساب" },
							{ icon: "📚", t: "اختيار البرنامج" },
							{ icon: "📄", t: "رفع المستندات" },
							{ icon: "💳", t: "سداد الرسوم" },
							{ icon: "🎤", t: "المقابلة" },
							{ icon: "✅", t: "استلام القبول" },
						]
					: [
							{ icon: "👤", t: "Create Account" },
							{ icon: "📚", t: "Choose Program" },
							{ icon: "📄", t: "Upload Documents" },
							{ icon: "💳", t: "Pay Fees" },
							{ icon: "🎤", t: "Interview" },
							{ icon: "✅", t: "Receive Admission" },
						];
			host.innerHTML = `
				<div class="edu-wrap">
					<h2>${this.lang === "ar" ? "ابدأ رحلتك الأكاديمية" : "Start Your Academic Journey"}</h2>
					<div class="edu-admission-steps">
						${steps.map((s, i) => `<div class="edu-adm-step"><span class="edu-adm-icon">${s.icon}</span><span class="edu-adm-num">${i + 1}</span><p>${s.t}</p></div>`).join("")}
					</div>
					<a class="edu-btn edu-btn-gold edu-btn-lg" href="/education/apply">${this.t("apply_now")}</a>
				</div>`;
		},

		renderServices(hostId) {
			const host = document.getElementById(hostId);
			if (!host) return;
			const items =
				this.lang === "ar"
					? ["التسجيل", "الجدول", "الحضور", "الاختبارات", "النتائج", "الشهادات", "الإرشاد الأكاديمي", "شؤون الطلاب"]
					: ["Registration", "Schedule", "Attendance", "Exams", "Results", "Certificates", "Advising", "Student Affairs"];
			host.innerHTML = `
				<div class="edu-wrap">
					<div class="edu-section-title">
						<span class="edu-eyebrow">Student Services</span>
						<h2>${this.lang === "ar" ? "الخدمات الطلابية" : "Student Services"}</h2>
					</div>
					<div class="edu-services-grid">
						${items.map((t) => `<div class="edu-service-card"><span>✓</span>${t}</div>`).join("")}
					</div>
				</div>`;
		},

		renderInternational(hostId) {
			const host = document.getElementById(hostId);
			if (!host) return;
			const items =
				this.lang === "ar"
					? ["خدمات التأشيرة", "التأمين الصحي", "السكن", "الاستقبال من المطار", "البرنامج التعريفي"]
					: ["Visa Services", "Health Insurance", "Accommodation", "Airport Pickup", "Orientation"];
			host.innerHTML = `
				<div class="edu-wrap edu-split-section">
					<div>
						<span class="edu-eyebrow">Global Campus</span>
						<h2>${this.lang === "ar" ? "الطلاب الدوليون" : "International Students"}</h2>
						<ul class="edu-check-list">${items.map((i) => `<li>${i}</li>`).join("")}</ul>
						<a class="edu-btn edu-btn-primary" href="/education/apply">${this.t("apply_now")}</a>
					</div>
					<div class="edu-split-img"><img src="https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=800&q=80" alt="" loading="lazy" /></div>
				</div>`;
		},

		renderOnlineLearning(hostId) {
			const host = document.getElementById(hostId);
			if (!host) return;
			const items =
				this.lang === "ar"
					? ["محاضرات مباشرة", "دورات مسجّلة", "واجبات", "اختبارات", "شهادات معتمدة"]
					: ["Live Classes", "Recorded Courses", "Assignments", "Exams", "Certificates"];
			host.innerHTML = `
				<div class="edu-wrap">
					<div class="edu-section-title">
						<span class="edu-eyebrow">Digital Learning</span>
						<h2>${this.lang === "ar" ? "التعلّم الإلكتروني" : "Online Learning"}</h2>
					</div>
					<div class="edu-online-grid">
						${items.map((t) => `<div class="edu-online-card">💻 ${t}</div>`).join("")}
					</div>
					<p class="edu-center"><a href="${(this.config && this.config.urls && this.config.urls.laravel_portal) || "https://kemetgate.com"}" class="edu-card-link" target="_blank" rel="noopener">kemetgate LMS →</a></p>
				</div>`;
		},

		renderScholarships(hostId) {
			const host = document.getElementById(hostId);
			if (!host) return;
			const rows = (this.config && this.config.scholarships) || [];
			host.innerHTML = `
				<div class="edu-wrap">
					<div class="edu-section-title">
						<span class="edu-eyebrow">Scholarships</span>
						<h2>${this.lang === "ar" ? "المنح الدراسية" : "Scholarships"}</h2>
					</div>
					<div class="edu-scholarship-grid">
						${rows
							.map(
								(s) => `
							<div class="edu-scholarship-card">
								<h3>${this.esc(this.lang === "ar" ? s.name_ar : s.name_en)}</h3>
								<p>${this.esc(this.lang === "ar" ? s.desc_ar : s.desc_en)}</p>
							</div>`
							)
							.join("")}
					</div>
				</div>`;
		},

		renderNews(hostId) {
			const host = document.getElementById(hostId);
			if (!host) return;
			const rows = (this.config && this.config.news) || [];
			host.innerHTML = `
				<div class="edu-wrap">
					<div class="edu-section-title">
						<span class="edu-eyebrow">News & Events</span>
						<h2>${this.lang === "ar" ? "آخر الأخبار والإعلانات" : "Latest News & Announcements"}</h2>
					</div>
					<div class="edu-news-grid">
						${rows
							.map(
								(n) => `
							<article class="edu-news-card">
								<div class="edu-news-img"><img src="${this.esc(n.image)}" alt="" loading="lazy" /></div>
								<div class="edu-news-body">
									<span class="edu-badge">${this.esc(this.lang === "ar" ? n.tag_ar : n.tag_en)}</span>
									<h3>${this.esc(this.lang === "ar" ? n.title_ar : n.title_en)}</h3>
									<time>${this.esc(n.date)}</time>
								</div>
							</article>`
							)
							.join("")}
					</div>
				</div>`;
		},

		renderPartners(hostId) {
			const host = document.getElementById(hostId);
			if (!host) return;
			const partners =
				this.lang === "ar"
					? ["وزارة التعليم", "القطاع الخاص", "جامعات دولية", "Microsoft", "Oracle", "AWS"]
					: ["Ministry of Education", "Industry Partners", "International Universities", "Microsoft", "Oracle", "AWS"];
			host.innerHTML = `
				<div class="edu-wrap">
					<div class="edu-section-title">
						<span class="edu-eyebrow">Partners</span>
						<h2>${this.lang === "ar" ? "شركاؤنا" : "Our Partners"}</h2>
					</div>
					<div class="edu-partners-row">${partners.map((p) => `<span class="edu-partner-pill">${p}</span>`).join("")}</div>
				</div>`;
		},

		renderInstitutionTypes(hostId) {
			const host = document.getElementById(hostId);
			if (!host) return;
			const types = (this.config && this.config.institution_types) || [];
			if (types.length) {
				this._paintInstitutionTypes(host, types);
				return;
			}
			if (typeof frappe !== "undefined" && frappe.call) {
				frappe.call({
					method: "omnexa_education.api.public_education_site.get_public_institution_types",
					callback: (r) => {
						this._paintInstitutionTypes(host, r.message || DEFAULT_CATALOG.institution_types);
					},
					error: () => {
						this._paintInstitutionTypes(host, DEFAULT_CATALOG.institution_types);
					},
				});
				return;
			}
			this._paintInstitutionTypes(host, DEFAULT_CATALOG.institution_types);
		},

		_paintInstitutionTypes(host, types) {
			const typeIcons = {
				"International School": "🏫",
				University: "🎓",
				Academy: "🏛️",
				Institute: "📖",
				"Training Center": "🛠️",
			};
			host.innerHTML = `
				<div class="edu-type-grid">
					${types
						.map((row) => {
							const active = !!row.active;
							const inactive = !!row.inactive || (row.seeded && !active);
							const statusClass = active ? "edu-status-active" : inactive ? "edu-status-inactive" : "edu-status-off";
							const statusLabel = active
								? this.lang === "ar"
									? "نشط"
									: "Active"
								: inactive
									? this.lang === "ar"
										? "غير نشط"
										: "Inactive"
									: this.lang === "ar"
										? "غير مفعّل"
										: "Not active";
							return `
						<div class="edu-type-card ${statusClass}">
							<div class="edu-type-img"><img src="${this.esc(row.image)}" alt="" loading="lazy" onerror="this.src='/assets/omnexa_education/logo.png'" /></div>
							<div class="edu-type-body">
								<span class="edu-type-icon">${typeIcons[row.institution_type] || "🏢"}</span>
								<span class="edu-status-pill ${statusClass}">${statusLabel}</span>
								<h3>${this.esc(row.name)}</h3>
								<p class="edu-muted">${this.esc(row.institution_type)}${row.academy_type ? " · " + this.esc(row.academy_type) : ""}</p>
								<div class="edu-type-stats">
									<span>👨‍🎓 ${row.students || 0}</span>
									<span>👩‍🏫 ${row.teachers || 0}</span>
									<span>📋 ${row.applications || 0}</span>
								</div>
								${row.institution ? `<a class="edu-card-link" href="/education/apply?institution=${encodeURIComponent(row.institution)}">${this.t("apply_now")} →</a>` : ""}
							</div>
						</div>`;
						})
						.join("")}
				</div>`;
		},

		renderGallery(hostId) {
			const host = document.getElementById(hostId);
			if (!host) return;
			const imgs = (this.config && this.config.gallery) || [];
			host.innerHTML = `
				<div class="edu-wrap">
					<div class="edu-section-title">
						<span class="edu-eyebrow">Campus Life</span>
						<h2>${this.lang === "ar" ? "حياة جامعية متميزة" : "Excellence in Campus Life"}</h2>
						<p>${this.lang === "ar" ? "بيئة تعليمية راقية تليق بأفضل الجامعات العالمية" : "A premium learning environment worthy of world-class universities"}</p>
					</div>
					<div class="edu-gallery-grid">
						${imgs
							.map(
								(src, i) =>
									`<div class="edu-gallery-item ${i === 0 ? "edu-gallery-featured" : ""}"><img src="${this.esc(src)}" alt="" loading="lazy" /></div>`
							)
							.join("")}
					</div>
				</div>`;
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
						<div class="edu-card edu-card-rich">
							<div class="edu-card-img"><img src="https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=600&q=70" alt="" loading="lazy" /></div>
							<div class="edu-card-body">
							<span class="edu-badge">${this.esc(row.institution_type || "")}</span>
							<h3>${this.esc(row.institution_name)}</h3>
							<p>${this.esc(row.city || "")}</p>
							<a class="edu-card-link" href="/education/apply?institution=${encodeURIComponent(row.name)}">${this.t("apply_now")} →</a>
							</div>
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
