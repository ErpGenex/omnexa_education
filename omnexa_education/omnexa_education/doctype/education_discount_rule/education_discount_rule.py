import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class EducationDiscountRule(Document):
	def validate(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if not branch_company:
			frappe.throw(_("Branch {0} does not exist.").format(self.branch), title=_("Branch"))
		if branch_company != self.company:
			frappe.throw(_("Branch belongs to a different company."), title=_("Branch"))
		if self.scope == "Fee Item" and not self.fee_item:
			frappe.throw(_("Set Fee Item when scope is Fee Item."), title=_("Scope"))
		if self.scope == "Fee Category" and not self.fee_category:
			frappe.throw(_("Set Fee Category when scope is Fee Category."), title=_("Scope"))
		if self.valid_from and self.valid_to and getdate(self.valid_from) > getdate(self.valid_to):
			frappe.throw(_("Valid From cannot be after Valid To."), title=_("Dates"))
		if self.discount_value is None or float(self.discount_value) < 0:
			frappe.throw(_("Discount Value cannot be negative."), title=_("Discount"))

