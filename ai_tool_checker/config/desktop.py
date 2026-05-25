"""
ai_tool_checker/config/desktop.py
Registers the AI Tool Checker module in the ERPNext desktop.
"""

from frappe import _


def get_data():
    return [
        {
            "module_name": "AI Tool Checker",
            "color": "#5e64ff",
            "icon": "octicon octicon-tools",
            "label": _("AI Tool Checker"),
            "link": "ai-tool-dashboard",
            "type": "module",
        }
    ]
