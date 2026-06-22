/**
 * Re-apply education Journey shell after other vertical kits (healthcare/finance) load globally.
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

omnexa_education.boot.ready = function (callback) {
	frappe.require("/assets/omnexa_education/js/education-journey-kit.js", function () {
		omnexa_education.boot.ensureKit();
		callback(window.OmnexaJourney);
	});
};

if (frappe.router) {
	frappe.router.on("change", () => {
		if (omnexa_education.boot.isEducationRoute()) {
			omnexa_education.boot.ensureKit();
		}
	});
}
