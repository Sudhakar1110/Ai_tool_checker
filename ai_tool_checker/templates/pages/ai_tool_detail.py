import frappe


def get_context(context):
    context.no_cache = 1
    context.tool_name = frappe.form_dict.get("name") or ""
    context.show_sidebar = False
