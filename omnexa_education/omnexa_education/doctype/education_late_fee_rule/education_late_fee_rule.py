import frappe
from frappe import _
from frappe.model.document import Document


class EducationLateFeeRule(Document):
	def validate(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch {0} does not exist.").format(self.branch), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Branch"))
		if int(self.grace_days or 0) < 0:
			frappe.throw(_("Grace Days cannot be negative."), title=_("Late Fee"))
		if float(self.charge_value or 0) < 0:
			frappe.throw(_("Charge Value cannot be negative."), title=_("Late Fee"))
		if float(self.max_charge or 0) < 0:
			frappe.throw(_("Max Charge cannot be negative."), title=_("Late Fee"))
		fee_company = frappe.db.get_value("Education Fee Item", self.late_fee_item, "company")
		if fee_company and fee_company != self.company:
			frappe.throw(_("Late Fee Item must belong to the same company."), title=_("Late Fee"))

