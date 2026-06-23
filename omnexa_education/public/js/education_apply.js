/**
 * Public online application — /education/apply (guest)
 */
frappe.ready(function () {
	const $host = $("#education-apply-form-host");
	if (!$host.length) return;

	function t(ar, en) {
		return frappe.boot.lang === "ar" ? ar : en;
	}

	function renderForm(ctx) {
		const institutions = ctx.institutions || [];
		const instOpts = institutions
			.map((i) => `<option value="${frappe.utils.escape_html(i.name)}">${frappe.utils.escape_html(i.institution_name)} (${frappe.utils.escape_html(i.institution_type || "")})</option>`)
			.join("");
		$host.html(`
			<form id="edu-apply-form">
				<div class="form-group"><label>${t("اسم المتقدّم", "Applicant Name")} *</label>
					<input type="text" class="form-control" name="applicant_name" required /></div>
				<div class="form-group"><label>${t("المؤسسة", "Institution")} *</label>
					<select class="form-control" name="institution" required><option value="">${t("اختر", "Select")}</option>${instOpts}</select></div>
				<div class="form-group"><label>${t("السنة الأكademic", "Academic Year")} *</label>
					<select class="form-control" name="academic_year" required><option value="">${t("اختر", "Select")}</option></select></div>
				<div class="form-group"><label>${t("الصف / البرنامج", "Grade / Program")}</label>
					<input type="text" class="form-control" name="grade_level" /></div>
				<div class="form-group"><label>${t("بريد ولي الأمر", "Guardian Email")}</label>
					<input type="email" class="form-control" name="guardian_email" /></div>
				<button type="submit" class="btn btn-primary btn-block" style="margin-top:16px">${t("إرسال الطلب", "Submit Application")}</button>
			</form>
			<div id="edu-apply-result" style="margin-top:12px"></div>`);

		$host.find('[name="institution"]').on("change", function () {
			const inst = $(this).val();
			const years = (ctx.academic_years || {})[inst] || [];
			const yOpts = years.map((y) => `<option value="${frappe.utils.escape_html(y.name)}">${frappe.utils.escape_html(y.title || y.name)}</option>`).join("");
			$host.find('[name="academic_year"]').html(`<option value="">${t("اختر", "Select")}</option>${yOpts}`);
		});

		$host.find("#edu-apply-form").on("submit", function (e) {
			e.preventDefault();
			const fd = Object.fromEntries(new FormData(this).entries());
			frappe.call({
				method: "omnexa_education.api.education_admissions.submit_online_application",
				args: fd,
				callback(r) {
					$("#edu-apply-result").html(
						`<div class="alert alert-success">${t("تم استلام طلبك", "Application received")}: <strong>${frappe.utils.escape_html(r.message.application)}</strong></div>`
					);
				},
				error(err) {
					$("#edu-apply-result").html(`<div class="alert alert-danger">${frappe.utils.escape_html(err.message || "Error")}</div>`);
				},
			});
		});
	}

	frappe.call({
		method: "omnexa_education.api.education_admissions.get_public_apply_context",
		callback(r) {
			renderForm(r.message || {});
		},
	});
});
