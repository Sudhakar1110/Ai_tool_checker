import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import nowdate


class AIToolReview(Document):
    def validate(self):
        if not (1 <= self.rating <= 5):
            frappe.throw(_("Rating must be between 1 and 5."))
        if not self.review_date:
            self.review_date = nowdate()

    def before_insert(self):
        # Prevent duplicate reviews from the same user
        existing = frappe.db.exists(
            "AI Tool Review",
            {"ai_tool": self.ai_tool, "reviewer": self.reviewer, "docstatus": ["<", 2]},
        )
        if existing:
            frappe.throw(
                _("You have already submitted a review for '{0}'.").format(self.ai_tool)
            )
