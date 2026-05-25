import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class AIToolCheckLog(Document):
    def before_insert(self):
        if not self.check_date:
            self.check_date = nowdate()
        if not self.checked_by:
            self.checked_by = frappe.session.user
