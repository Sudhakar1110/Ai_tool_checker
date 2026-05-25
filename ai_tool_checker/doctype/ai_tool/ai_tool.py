"""
ai_tool_checker/doctype/ai_tool/ai_tool.py
Controller for the AI Tool doctype.
"""

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt


class AITool(Document):

    def validate(self):
        self.validate_url()
        self.validate_rating()

    def validate_url(self):
        if self.tool_url and not self.tool_url.startswith(("http://", "https://")):
            frappe.throw(_("Tool URL must start with http:// or https://"))

    def validate_rating(self):
        if self.average_rating and not (0 <= flt(self.average_rating) <= 5):
            frappe.throw(_("Average Rating must be between 0 and 5."))

    def before_save(self):
        # Normalise tags — strip whitespace
        if self.tags:
            self.tags = ", ".join(t.strip() for t in self.tags.split(",") if t.strip())

    def on_trash(self):
        # Prevent deletion if there are reviews
        review_count = frappe.db.count("AI Tool Review", {"ai_tool": self.name})
        if review_count:
            frappe.throw(
                _("Cannot delete AI Tool '{0}' as it has {1} review(s). Deactivate it instead.").format(
                    self.tool_name, review_count
                )
            )

    @frappe.whitelist()
    def get_related_tools(self):
        """Return tools with the same category or industry (for 'You may also like')."""
        return frappe.get_all(
            "AI Tool",
            filters={
                "name": ["!=", self.name],
                "is_active": 1,
                "category": self.category,
            },
            fields=["name", "tool_name", "short_description", "average_rating", "logo_image"],
            limit=5,
        )
