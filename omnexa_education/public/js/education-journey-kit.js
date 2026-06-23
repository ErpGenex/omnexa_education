/**
 * Education Journey Kit — healthcare-parity desk UI (OmnexaJourney shell override)
 */
/* global frappe */
(function (window) {
	"use strict";
	const OJ = window.OmnexaJourney;
	if (!OJ) return;

	const LOGO = "/assets/omnexa_education/logo.png";

	function navigateRoute(route) {
		if (!route || route === "#") return;
		if (route.startsWith("/app/") || route.startsWith("/education/")) {
			window.location.href = route;
			return;
		}
		if (route.startsWith("List/")) {
			frappe.set_route("List", route.slice(5));
			return;
		}
		if (route.startsWith("Form/")) {
			const parts = route.split("/");
			frappe.set_route("Form", parts[1], parts[2] || "");
			return;
		}
		frappe.set_route(route);
	}

	function resolveCompanyBranch() {
		return {
			company: frappe.defaults.get_user_default("Company") || "",
			branch: frappe.defaults.get_user_default("Branch") || "",
		};
	}

	function showCallError(err, fallback) {
		const msg = (err && (err.message || err._error_message)) || fallback || OJ.t("تعذر التحميل", "Could not load data");
		frappe.msgprint({ title: OJ.t("خطأ", "Error"), indicator: "red", message: msg });
	}

	function dataTable(columns, rows) {
		const cols = columns || [];
		const head = cols.map((c) => `<th>${OJ.esc(c.label)}</th>`).join("");
		const body = (rows || [])
			.map((row) => {
				const cells = cols.map((c) => `<td>${OJ.esc(row[c.field] ?? "—")}</td>`).join("");
				return `<tr>${cells}</tr>`;
			})
			.join("");
		return `<div class="oj-table-wrap"><table class="oj-data-table"><thead><tr>${head}</tr></thead><tbody>${body || `<tr><td colspan="${cols.length || 1}" class="oj-muted">${OJ.t("لا بيانات", "No data")}</td></tr>`}</tbody></table></div>`;
	}

	function linkGrid(links) {
		const $g = $('<div class="oj-link-grid"></div>');
		(links || []).forEach((link) => {
			const $card = $(`<div class="oj-link-card"><div class="oj-link-icon">${link.icon || "•"}</div><div class="oj-link-label">${OJ.esc(link.label)}</div></div>`);
			$card.on("click", () => navigateRoute(link.route));
			$g.append($card);
		});
		return $g;
	}

	function workflowJourneyGrid(steps, onSelect) {
		const $g = $('<div class="oj-workflow-grid"></div>');
		(steps || []).forEach((s) => {
			const $card = $(`
				<div class="oj-workflow-card" data-step="${OJ.esc(s.key || "")}">
					<div class="oj-workflow-icon">${OJ.esc(s.icon || "•")}</div>
					<div class="oj-workflow-title">${OJ.esc(OJ.t(s.label_ar, s.label_en))}</div>
					<div class="oj-workflow-role oj-muted">${OJ.esc(OJ.t(s.role_ar, s.role_en))}</div>
				</div>`);
			$card.on("click", () => onSelect && onSelect(s));
			$g.append($card);
		});
		return $g;
	}

	function portalCategoryGrid(groups) {
		const $root = $('<div class="oj-portal-catalog oj-demo-portals oj-education-portals"></div>');
		(groups || []).forEach((g) => {
			const title = OJ.lang() === "ar" ? g.label_ar : g.label_en;
			const $sec = $(`<div class="oj-portal-section"><h4 class="oj-portal-cat-title">${OJ.esc(title)}</h4></div>`);
			const clinics = (g.portals || []).map((p) => ({
				id: p.id,
				name: OJ.lang() === "ar" ? p.label_ar : p.label_en,
				subtitle: OJ.t(p.subtitle_ar || "", p.subtitle_en || ""),
				icon: p.icon || "🎓",
				doctor_count: 0,
				waiting_count: 0,
				route: p.route,
				_disabled: p.exists === false,
			}));
			const $grid = $('<div class="oj-clinic-grid"></div>');
			clinics.forEach((c) => {
				const $card = $(`
					<div class="oj-clinic-card ${c._disabled ? "oj-muted-card" : ""}">
						<div class="oj-clinic-icon">${c.icon || "🎓"}</div>
						<h4>${OJ.esc(c.name)}</h4>
						<p class="oj-muted">${OJ.esc(c.subtitle)}</p>
						<button type="button" class="oj-btn oj-btn-primary oj-btn-sm">${OJ.t("فتح", "Open")}</button>
					</div>`);
				if (!c._disabled) $card.on("click", () => navigateRoute(c.route));
				$grid.append($card);
			});
			$sec.append($grid);
			$root.append($sec);
		});
		return $root;
	}

	function bindSidebarNav($root, homeRoute) {
		$root.find(".oj-sidebar-item[data-nav-route]").on("click", function (e) {
			e.preventDefault();
			navigateRoute($(this).attr("data-nav-route"));
		});
		if (homeRoute) {
			$root.find("[data-oj-home]").on("click", function (e) {
				e.preventDefault();
				navigateRoute(homeRoute);
			});
		}
	}

	function userMenuHtml() {
		const name = frappe.session.user_fullname || frappe.session.user;
		return `<div class="oj-user-menu">
			<button type="button" class="oj-user-btn" aria-haspopup="true" aria-expanded="false">
				<span class="oj-user-avatar">${OJ.esc((name || "U").charAt(0).toUpperCase())}</span>
				<span class="oj-user-name">${OJ.esc(name)}</span>
				<span class="oj-user-caret">▾</span>
			</button>
			<div class="oj-user-dropdown" role="menu">
				<div class="oj-user-dropdown-title">${OJ.t("الحساب", "Account")}</div>
				<a href="/app/user-profile" class="oj-user-dropdown-item" role="menuitem">⚙ ${OJ.t("الملف الشخصي", "Profile")}</a>
			</div>
		</div>`;
	}

	function bindUserMenu($root) {
		const $menu = $root.find(".oj-user-menu");
		$menu.find(".oj-user-btn").on("click", function (e) {
			e.stopPropagation();
			$menu.toggleClass("open");
			$(this).attr("aria-expanded", $menu.hasClass("open"));
		});
		$(document).on("click.ojEduUserMenu", () => $menu.removeClass("open"));
	}

	function installEducationKit() {
		OJ.shell = function (options) {
		const opts = options || {};
		const sidebar = opts.sidebar || OJ.defaultSidebar(opts.sidebarRole || "workcenter", opts.currentPage);
		const navHtml = sidebar
			.map(
				(n) =>
					`<a class="oj-sidebar-item ${n.active ? "active" : ""}" href="#" data-nav-route="${OJ.esc(n.route || "")}"><span class="oj-sidebar-icon">${n.icon || "•"}</span><span>${OJ.esc(n.label)}</span></a>`
			)
			.join("");
		const isRtl = OJ.lang() === "ar";
		const brandLogo = `<img class="oj-brand-logo" src="${OJ.esc(opts.brandLogoUrl || LOGO)}" alt="" />`;
		const $root = $(`<div class="oj-shell oj-desk-page oj-education-shell ${isRtl ? "oj-rtl" : "oj-ltr"}" dir="${isRtl ? "rtl" : "ltr"}"></div>`);
		const kpiHtml = (opts.kpis || [])
			.map((k) => `<div class="oj-kpi-card"><div class="oj-kpi-value">${OJ.esc(k.value)}</div><div class="oj-kpi-label">${OJ.esc(k.label)}</div></div>`)
			.join("");
		const logoutHref =
			typeof omnexa_education !== "undefined" &&
			omnexa_education.boot &&
			omnexa_education.boot.isPortalOnly &&
			omnexa_education.boot.isPortalOnly()
				? "/login"
				: "/app";
		$root.html(`
			<aside class="oj-sidebar">${navHtml}<div class="oj-sidebar-spacer"></div>
				<a class="oj-sidebar-item" href="#" data-oj-home="1">🏠 ${OJ.t("الرئيسية", "Home")}</a>
				<a class="oj-sidebar-item oj-logout" href="${logoutHref}">⏻ ${OJ.t("خروج", "Logout")}</a>
			</aside>
			<div class="oj-main">
				<header class="oj-topbar">
					<div class="oj-topbar-brand">${brandLogo}<div><strong>ErpGenEx Education</strong><small>${OJ.esc(opts.subtitle || OJ.t("EduSphere", "EduSphere"))}</small></div></div>
					<div class="oj-topbar-meta"><span class="oj-pill">${OJ.esc(opts.role || "")}</span>${userMenuHtml()}</div>
				</header>
				<div class="oj-title-row"><h1>${OJ.esc(opts.title || "")}</h1></div>
				${kpiHtml ? `<div class="oj-kpi-row">${kpiHtml}</div>` : ""}
				<div class="oj-body"></div>
			</div>`);
		const $body = $root.find(".oj-body");
		if (opts.bodyEl) $body.append(opts.bodyEl);
		else if (opts.body) $body.html(opts.body);
		bindSidebarNav($root, opts.homeRoute || "/app/education-workcenter");
		bindUserMenu($root);
		return $root;
	};

	function defaultSidebar(role, currentPage) {
		const page = (currentPage || "").replace(/^\/app\//, "");
		const mark = (items) =>
			items.map((item) => ({
				...item,
				active: item.route === `/app/${page}` || (page && item.route.includes(page)),
			}));
		const menus = {
			workcenter: [
				{ label: OJ.t("مركز العمل", "Workcenter"), icon: "🏢", route: "/app/education-workcenter" },
				{ label: OJ.t("التقديم الإلكتروني", "Online Apply"), icon: "🌐", route: "/education/apply" },
				{ label: OJ.t("المدير التنفيذي", "Executive"), icon: "📊", route: "/app/education-executive-dashboard" },
				{ label: OJ.t("ضمان الجودة", "QA Desk"), icon: "⭐", route: "/app/education-qa-desk" },
				{ label: OJ.t("التحليلات", "Analytics"), icon: "📈", route: "/app/education-analytics-dashboard" },
			],
			finance: [
				{ label: OJ.t("مركز العمل", "Workcenter"), icon: "🏢", route: "/app/education-workcenter" },
				{ label: OJ.t("الشؤون المالية", "Finance Desk"), icon: "💰", route: "/app/education-finance-desk" },
				{ label: OJ.t("ربط Laravel", "Laravel"), icon: "🔗", route: "/app/education-laravel-integration" },
				{ label: OJ.t("الطلاب", "Students"), icon: "🎓", route: "List/Education Student" },
			],
			laravel: [
				{ label: OJ.t("مركز العمل", "Workcenter"), icon: "🏢", route: "/app/education-workcenter" },
				{ label: OJ.t("ربط Laravel", "Laravel"), icon: "🔗", route: "/app/education-laravel-integration" },
				{ label: OJ.t("الشؤون المالية", "Finance Desk"), icon: "💰", route: "/app/education-finance-desk" },
			],
			admissions: [
				{ label: OJ.t("مركز العمل", "Workcenter"), icon: "🏢", route: "/app/education-workcenter" },
				{ label: OJ.t("بوابة القبول", "Admissions"), icon: "📋", route: "/app/education-admissions-portal" },
				{ label: OJ.t("التقديم الخارجي", "Public Apply"), icon: "🌐", route: "/education/apply" },
				{ label: OJ.t("الطلبات", "Applications"), icon: "📄", route: "List/Education Admission Application" },
			],
			registrar: [
				{ label: OJ.t("مركز العمل", "Workcenter"), icon: "🏢", route: "/app/education-workcenter" },
				{ label: OJ.t("مكتب المسجل", "Registrar"), icon: "📚", route: "/app/education-registrar-desk" },
				{ label: OJ.t("مكتب التخرج", "Graduation"), icon: "🎓", route: "/app/education-graduation-desk" },
				{ label: OJ.t("الخريجون", "Alumni"), icon: "🤝", route: "/app/education-alumni-desk" },
				{ label: OJ.t("الطلاب", "Students"), icon: "🎓", route: "List/Education Student" },
			],
			teacher: [
				{ label: OJ.t("مركز العمل", "Workcenter"), icon: "🏢", route: "/app/education-workcenter" },
				{ label: OJ.t("سجل الدرجات", "Gradebook"), icon: "📝", route: "/app/education-teacher-gradebook" },
				{ label: OJ.t("الجدول", "Timetable"), icon: "📅", route: "/app/education-timetable-board" },
			],
			student: [
				{ label: OJ.t("بوابة الطالب", "Student Portal"), icon: "🎓", route: "/app/education-student-portal" },
				{ label: OJ.t("الجدول", "Timetable"), icon: "📅", route: "/app/education-timetable-board" },
			],
			parent: [
				{ label: OJ.t("بوابة ولي الأمر", "Parent Portal"), icon: "👪", route: "/app/education-parent-mobile" },
				{ label: OJ.t("الجدول", "Timetable"), icon: "📅", route: "/app/education-timetable-board" },
			],
		};
		return mark(menus[role] || menus.workcenter);
	}

	Object.assign(OJ, {
			navigateRoute,
		resolveCompanyBranch,
		showCallError,
		dataTable,
		linkGrid,
			workflowJourneyGrid,
			portalCategoryGrid,
		defaultSidebar,
			educationLogo: LOGO,
			installEducationKit,
	});
	}

	installEducationKit();
})(window);
