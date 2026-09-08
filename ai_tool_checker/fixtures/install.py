"""
ai_tool_checker/fixtures/install.py
Post-install and post-migrate hooks to seed demo data.
"""

import frappe
from frappe import _


CATEGORIES = [
    {"category_name": "Natural Language Processing", "icon": "💬"},
    {"category_name": "Image & Vision", "icon": "🖼️"},
    {"category_name": "Code Generation", "icon": "💻"},
    {"category_name": "Data Analytics", "icon": "📊"},
    {"category_name": "Audio & Speech", "icon": "🎙️"},
    {"category_name": "Automation & Workflow", "icon": "⚙️"},
    {"category_name": "Customer Support", "icon": "🎧"},
    {"category_name": "Marketing & Content", "icon": "📣"},
    {"category_name": "Finance & Forecasting", "icon": "💹"},
    {"category_name": "Healthcare AI", "icon": "🏥"},
]

INDUSTRIES = [
    {"industry_name": "Manufacturing", "icon": "🏭", "sort_order": 1},
    {"industry_name": "Healthcare", "icon": "🏥", "sort_order": 2},
    {"industry_name": "Retail & E-Commerce", "icon": "🛍️", "sort_order": 3},
    {"industry_name": "Finance & Banking", "icon": "🏦", "sort_order": 4},
    {"industry_name": "Education", "icon": "🎓", "sort_order": 5},
    {"industry_name": "Logistics & Supply Chain", "icon": "🚚", "sort_order": 6},
    {"industry_name": "Real Estate", "icon": "🏠", "sort_order": 7},
    {"industry_name": "Legal", "icon": "⚖️", "sort_order": 8},
    {"industry_name": "HR & Recruitment", "icon": "👥", "sort_order": 9},
    {"industry_name": "Marketing & Advertising", "icon": "📣", "sort_order": 10},
    {"industry_name": "Agriculture", "icon": "🌾", "sort_order": 11},
    {"industry_name": "Energy & Utilities", "icon": "⚡", "sort_order": 12},
]

DEMO_TOOLS = [
    {
        "tool_name": "ChatGPT",
        "short_description": "Conversational AI for drafting, analysis, coding, and more.",
        "category": "Natural Language Processing",
        "industry": "Education",
        "tool_url": "https://chat.openai.com",
        "pricing_model": "Freemium",
        "is_active": 1,
        "tags": "nlp, chatbot, openai, gpt",
    },
    {
        "tool_name": "GitHub Copilot",
        "short_description": "AI pair programmer that helps write code faster.",
        "category": "Code Generation",
        "industry": "Manufacturing",
        "tool_url": "https://github.com/features/copilot",
        "pricing_model": "Paid",
        "is_active": 1,
        "tags": "code, programming, github, copilot",
    },
    {
        "tool_name": "Jasper AI",
        "short_description": "AI writing assistant for marketing copy and content.",
        "category": "Marketing & Content",
        "industry": "Marketing & Advertising",
        "tool_url": "https://jasper.ai",
        "pricing_model": "Paid",
        "is_active": 1,
        "tags": "marketing, content, writing, copy",
    },
    {
        "tool_name": "Runway ML",
        "short_description": "AI video and image generation for creatives.",
        "category": "Image & Vision",
        "industry": "Marketing & Advertising",
        "tool_url": "https://runwayml.com",
        "pricing_model": "Freemium",
        "is_active": 1,
        "tags": "video, image, creative, generative",
    },
    {
        "tool_name": "Otter.ai",
        "short_description": "AI meeting transcription and note-taking.",
        "category": "Audio & Speech",
        "industry": "HR & Recruitment",
        "tool_url": "https://otter.ai",
        "pricing_model": "Freemium",
        "is_active": 1,
        "tags": "transcription, meetings, speech, notes",
    },
]


def before_migrate():
    """Hook required by hooks.py. Keep migrate from failing on a missing symbol."""
    pass


def after_install():
    """Seed roles, categories, industries, and demo tools."""
    _create_roles()
    _seed_categories()
    _seed_industries()
    _seed_demo_tools()
    frappe.db.commit()
    frappe.msgprint(_("AI Tool Checker installed and seeded successfully!"))


def after_migrate():
    """Re-seed only if data is missing."""
    if not frappe.db.count("AI Tool Category"):
        _seed_categories()
    if not frappe.db.count("AI Tool Industry"):
        _seed_industries()
    frappe.db.commit()


def load_fixtures():
    """Callable from bench execute."""
    _create_roles()
    _seed_categories()
    _seed_industries()
    _seed_demo_tools()
    frappe.db.commit()
    print("Fixtures loaded.")


def _create_roles():
    for role_name in ("AI Tool Manager", "AI Tool User"):
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(ignore_permissions=True)


def _seed_categories():
    for cat in CATEGORIES:
        if not frappe.db.exists("AI Tool Category", cat["category_name"]):
            frappe.get_doc({"doctype": "AI Tool Category", **cat, "is_active": 1}).insert(ignore_permissions=True)


def _seed_industries():
    for ind in INDUSTRIES:
        if not frappe.db.exists("AI Tool Industry", ind["industry_name"]):
            frappe.get_doc({"doctype": "AI Tool Industry", **ind, "is_active": 1}).insert(ignore_permissions=True)


def _seed_demo_tools():
    for tool in DEMO_TOOLS:
        if not frappe.db.exists("AI Tool", tool["tool_name"]):
            frappe.get_doc({"doctype": "AI Tool", **tool}).insert(ignore_permissions=True)
