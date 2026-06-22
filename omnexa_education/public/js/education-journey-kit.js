/**
 * Education Journey Kit — Finance-parity desk UI for education role portals
 */
/* global frappe */
(function (window) {
	"use strict";

	const FINANCE_ASSETS = [
		"/assets/omnexa_core/css/omnexa-finance-journey.css",
		"/assets/omnexa_core/js/omnexa-finance-journey.js",
	];

	function journeyEngine() {
		return window.OmnexaFinanceJourney || window.OmnexaJourney;
	}

	function ensureFinanceAssets(callback, attempt) {
		const tries = attempt || 0;
		if (window.OmnexaFinanceJourney) {
			callback();
			return;
		}
		if (tries >= 80) {
			callback();
			return;
		}
		frappe.require(FINANCE_ASSETS).then(() => {
			if (window.OmnexaFinanceJourney) callback();
			else setTimeout(() => ensureFinanceAssets(callback, tries + 1), 50);
		});
	}

	function navigateRoute(route) {
		if (!route || route === "#") return;
		if (route.startsWith("/app/")) {
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
		const OJ = journeyEngine();
		const msg = (err && (err.message || err._error_message)) || fallback || OJ.t("تعذر التحميل", "Could not load data");
		frappe.msgprint({ title: OJ.t("خطأ", "Error"), indicator: "red", message: msg });
	}

	function call(method, args) {
		const OJ = journeyEngine();
		if (OJ.call) return OJ.call(method, args);
		return new Promise((resolve, reject) => {
			frappe.call({ method, args: args || {}, callback: (r) => resolve(r.message), error: reject });
		});
	}

	function dataTable(columns, rows) {
		const OJ = journeyEngine();
		if (OJ.dataTable) {
			const result = OJ.dataTable(columns, rows);
			if (result && result.jquery) return result;
		}
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
		const OJ = journeyEngine();
		if (OJ.linkGrid) return OJ.linkGrid(links);
		const $g = $('<div class="oj-link-grid"></div>');
		(links || []).forEach((link) => {
			const icon = link.logoUrl
				? `<img class="oj-link-logo" src="${OJ.esc(link.logoUrl)}" alt="" />`
				: `<div class="oj-link-icon">${link.icon || "•"}</div>`;
			const $card = $(`<div class="oj-link-card">${icon}<div class="oj-link-label">${OJ.esc(link.label)}</div></div>`);
			$card.on("click", () => navigateRoute(link.route));
			$g.append($card);
		});
		return $g;
	}

	function portalCardGrid(portals, onSelect) {
		const OJ = journeyEngine();
		if (OJ.portalCardGrid) return OJ.portalCardGrid(portals, onSelect);
		const $g = $('<div class="oj-clinic-grid oj-finance-portal-grid"></div>');
		(portals || []).forEach((p) => {
			const icon = p.logoUrl
				? `<img class="oj-portal-logo" src="${OJ.esc(p.logoUrl)}" alt="" />`
				: `<div class="oj-clinic-icon">${p.icon || "🎓"}</div>`;
			const $card = $(`
				<div class="oj-clinic-card">
					${icon}
					<h4>${OJ.esc(p.name)}</h4>
					<p class="oj-muted">${OJ.esc(p.subtitle || "")}</p>
					<button type="button" class="oj-btn oj-btn-primary oj-btn-sm">${OJ.t("فتح", "Open")}</button>
				</div>`);
			$card.on("click", () => (onSelect ? onSelect(p) : navigateRoute(p.route)));
			$g.append($card);
		});
		return $g;
	}

	function workflowJourneyGrid(steps, onSelect) {
		const OJ = journeyEngine();
		if (OJ.workflowJourneyGrid) return OJ.workflowJourneyGrid(steps, onSelect);
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
		const OJ = journeyEngine();
		if (OJ.portalCategoryGrid) return OJ.portalCategoryGrid(groups, (p) => navigateRoute(p.route));
		const $root = $('<div class="oj-portal-catalog oj-education-workcenter-portals"></div>');
		(groups || []).forEach((g) => {
			const title = OJ.lang && OJ.lang() === "ar" ? g.label_ar : g.label_en;
			const $sec = $(`<div class="oj-portal-section"><h4 class="oj-portal-cat-title">${OJ.esc(title)}</h4></div>`);
			const portals = (g.portals || []).map((p) => ({
				name: OJ.t(p.label_ar, p.label_en),
				subtitle: OJ.t(p.subtitle_ar, p.subtitle_en),
				logoUrl: p.logo_url,
				route: p.route,
				icon: "🎓",
			}));
			$sec.append(portalCardGrid(portals));
			$root.append($sec);
		});
		return $root;
	}

	function mountDeskPage(wrapper, title) {
		const OJ = journeyEngine();
		if (OJ.mountDeskPage) return OJ.mountDeskPage(wrapper, title);
		frappe.ui.make_app_page({ parent: wrapper, title: title, single_column: true });
		$(wrapper).find(".page-head").hide();
		return $(wrapper).find(".layout-main-section");
	}

	const LOGO = "/assets/omnexa_education/logo.png";

	const SIDEBARS = {
		finance: [
			{ label_ar: "مركز العمل", label_en: "Workcenter", route: "/app/education-workcenter", icon: "🏢" },
			{ label_ar: "الشؤون المالية", label_en: "Finance Desk", route: "/app/education-finance-desk", logoUrl: LOGO },
			{ label_ar: "ربط Laravel", label_en: "Laravel Integration", route: "/app/education-laravel-integration", icon: "🔗" },
		],
		laravel: [
			{ label_ar: "مركز العمل", label_en: "Workcenter", route: "/app/education-workcenter", icon: "🏢" },
			{ label_ar: "ربط Laravel", label_en: "Laravel Integration", route: "/app/education-laravel-integration", logoUrl: LOGO },
			{ label_ar: "الشؤون المالية", label_en: "Finance Desk", route: "/app/education-finance-desk", icon: "💰" },
		],
		parent: [
			{ label_ar: "بوابة ولي الأمر", label_en: "Parent Portal", route: "/app/education-parent-mobile", logoUrl: LOGO },
			{ label_ar: "مركز العمل", label_en: "Workcenter", route: "/app/education-workcenter", icon: "🏢" },
		],
		student: [
			{ label_ar: "بوابة الطالب", label_en: "Student Portal", route: "/app/education-student-portal", logoUrl: LOGO },
			{ label_ar: "مركز العمل", label_en: "Workcenter", route: "/app/education-workcenter", icon: "🏢" },
		],
		teacher: [
			{ label_ar: "سجل الدرجات", label_en: "Gradebook", route: "/app/education-teacher-gradebook", logoUrl: LOGO },
			{ label_ar: "الجدول", label_en: "Timetable", route: "/app/education-timetable-board", icon: "📅" },
			{ label_ar: "مركز العمل", label_en: "Workcenter", route: "/app/education-workcenter", icon: "🏢" },
		],
		admissions: [
			{ label_ar: "بوابة القبول", label_en: "Admissions Portal", route: "/app/education-admissions-portal", logoUrl: LOGO },
			{ label_ar: "مركز العمل", label_en: "Workcenter", route: "/app/education-workcenter", icon: "🏢" },
		],
		registrar: [
			{ label_ar: "مكتب المسجل", label_en: "Registrar Desk", route: "/app/education-registrar-desk", logoUrl: LOGO },
			{ label_ar: "مركز العمل", label_en: "Workcenter", route: "/app/education-workcenter", icon: "🏢" },
		],
		workcenter: [
			{ label_ar: "مركز العمل", label_en: "Workcenter", route: "/app/education-workcenter", logoUrl: LOGO },
			{ label_ar: "الشؤون المالية", label_en: "Finance Desk", route: "/app/education-finance-desk", icon: "💰" },
			{ label_ar: "بوابة القبول", label_en: "Admissions", route: "/app/education-admissions-portal", icon: "📋" },
		],
	};

	function defaultSidebar(role, activeRoute) {
		const OJ = journeyEngine();
		const route = activeRoute || "";
		const items = SIDEBARS[role] || SIDEBARS.workcenter;
		return items.map((item) => ({
			label: OJ.t(item.label_ar, item.label_en),
			route: item.route,
			icon: item.icon || "•",
			logoUrl: item.logoUrl || "",
			active: route && (item.route === route || route.includes(item.route.replace("/app/", ""))),
		}));
	}

	function shell(options) {
		const OJ = journeyEngine();
		const opts = options || {};
		const sidebarItems = typeof opts.sidebar === "object" && opts.sidebar.jquery ? null : opts.sidebar;
		if (OJ.shell && sidebarItems) {
			const roleLabel =
				typeof opts.role === "string" && opts.role.length <= 32
					? opts.role
					: OJ.t(opts.roleAr || "", opts.roleEn || opts.role || "");
			const $shell = OJ.shell({
				title: opts.title,
				subtitle: opts.subtitle || OJ.t("ErpGenEx — EduSphere", "ErpGenEx — EduSphere"),
				role: roleLabel,
				brandLogoUrl: opts.brandLogoUrl || LOGO,
				kpis: opts.kpis,
				sidebar: sidebarItems,
				bodyEl: opts.bodyEl,
				currentPage: opts.currentPage || "",
			});
			$shell.find(".oj-topbar-brand strong").text(OJ.t("ErpGenEx Education", "ErpGenEx Education"));
			return $shell;
		}
		const $wrap = $('<div class="oj-shell education-journey-shell"></div>');
		if (opts.bodyEl) $wrap.append(opts.bodyEl);
		return $wrap;
	}

	function bootEducationJourney(callback) {
		ensureFinanceAssets(() => {
			const OJ = journeyEngine();
			if (!window.OmnexaJourney) window.OmnexaJourney = {};
			Object.assign(window.OmnexaJourney, OJ, {
				resolveCompanyBranch,
				showCallError,
				dataTable,
				linkGrid,
				portalCardGrid,
				portalCategoryGrid,
				workflowJourneyGrid,
				mountDeskPage,
				defaultSidebar,
				shell,
				navigateRoute,
				call,
				educationLogo: LOGO,
			});
			if (callback) callback(window.OmnexaJourney);
		});
	}

	window.EducationJourney = { boot: bootEducationJourney, LOGO };
	bootEducationJourney();
})(window);
