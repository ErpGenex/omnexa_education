/**
 * Education portal boot — kit loader + route guard for student/parent users.
 */
frappe.provide("omnexa_education.boot");

omnexa_education.boot.isEducationRoute = function () {
	const route = frappe.get_route_str() || "";
	return route.startsWith("education-");
};

omnexa_education.boot.ensureKit = function () {
	const OJ = window.OmnexaJourney;
	if (OJ && typeof OJ.installEducationKit === "function") {
		OJ.installEducationKit();
	}
};

omnexa_education.boot.getPortalConfig = function () {
	return (frappe.boot && frappe.boot.education_portal) || null;
};

omnexa_education.boot.isPortalOnly = function () {
	const cfg = omnexa_education.boot.getPortalConfig();
	return !!(cfg && cfg.portal_only);
};

omnexa_education.boot.portalHome = function () {
	const cfg = omnexa_education.boot.getPortalConfig();
	return (cfg && cfg.home_route) || null;
};

omnexa_education.boot.isRouteAllowed = function (route) {
	const cfg = omnexa_education.boot.getPortalConfig();
	if (!cfg || !cfg.portal_only) return true;
	const allowedPages = new Set(cfg.allowed_pages || []);
	const allowedDoctypes = new Set(cfg.allowed_doctypes || []);
	const parts = (route || "").split("/").filter(Boolean);
	if (!parts.length) return true;
	if (parts[0] === "education-student-portal" || parts[0] === "education-parent-mobile") {
		return allowedPages.has(parts[0]);
	}
	if (parts[0] && parts[0].startsWith("education-")) {
		return allowedPages.has(parts[0]);
	}
	if (parts[0] === "List" && parts[1]) {
		const slug = frappe.router ? frappe.router.slug(parts[1]) : String(parts[1]).toLowerCase().replace(/ /g, "-");
		return allowedDoctypes.has(slug);
	}
	if (parts[0] === "Form" && parts[1]) {
		const slug = frappe.router ? frappe.router.slug(parts[1]) : String(parts[1]).toLowerCase().replace(/ /g, "-");
		return allowedDoctypes.has(slug);
	}
	// Block generic desk home and unrelated modules for portal-only users.
	if (parts[0] === "Workspaces" || parts[0] === "workspace" || route === "") {
		return false;
	}
	return false;
};

omnexa_education.boot.enforcePortalRoute = function () {
	if (!omnexa_education.boot.isPortalOnly()) return;
	const route = frappe.get_route_str() || "";
	if (!route) {
		const home = omnexa_education.boot.portalHome();
		if (home) frappe.set_route(home.replace(/^\/app\//, ""));
		return;
	}
	if (!omnexa_education.boot.isRouteAllowed(route)) {
		const home = omnexa_education.boot.portalHome();
		if (home) {
			frappe.show_alert({
				message: __("This area is not available for your account."),
				indicator: "orange",
			});
			frappe.set_route(home.replace(/^\/app\//, ""));
		}
	}
};

omnexa_education.boot.ready = function (callback) {
	frappe.require("/assets/omnexa_education/js/education-journey-kit.js", function () {
		omnexa_education.boot.ensureKit();
		omnexa_education.boot.enforcePortalRoute();
		callback(window.OmnexaJourney);
	});
};

if (frappe.router) {
	frappe.router.on("change", () => {
		if (omnexa_education.boot.isEducationRoute()) {
			omnexa_education.boot.ensureKit();
		}
		omnexa_education.boot.enforcePortalRoute();
	});
}
