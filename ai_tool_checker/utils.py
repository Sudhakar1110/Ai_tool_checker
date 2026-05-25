"""
ai_tool_checker/utils.py
Shared utilities, doc event handlers, and whitelisted API methods.
"""

import frappe
from frappe import _
from frappe.utils import nowdate, flt, cint
import requests
import json


# ─────────────────────────────────────────────
# Doc Event Handlers
# ─────────────────────────────────────────────

def on_ai_tool_insert(doc, method=None):
    """Triggered after a new AI Tool is saved."""
    frappe.publish_realtime(
        "ai_tool_added",
        {"tool_name": doc.name, "tool_title": doc.tool_name},
        after_commit=True,
    )


def on_ai_tool_update(doc, method=None):
    """Triggered on AI Tool update — clear cache."""
    frappe.cache().delete_key(f"ai_tool_{doc.name}")


def on_check_log_insert(doc, method=None):
    """Triggered after a Check Log entry is created."""
    # Increment the check count on the AI Tool
    frappe.db.sql(
        """UPDATE `tabAI Tool`
           SET check_count = COALESCE(check_count, 0) + 1
           WHERE name = %s""",
        doc.ai_tool,
    )
    frappe.db.commit()


def on_review_insert(doc, method=None):
    """Triggered after a review is submitted."""
    recalculate_tool_rating(doc, method)


def recalculate_tool_rating(doc, method=None):
    """Recalculate the average rating for an AI Tool."""
    avg = frappe.db.sql(
        """SELECT AVG(rating) as avg_rating, COUNT(*) as review_count
           FROM `tabAI Tool Review`
           WHERE ai_tool = %s AND docstatus < 2""",
        doc.ai_tool,
        as_dict=True,
    )
    if avg:
        frappe.db.set_value(
            "AI Tool",
            doc.ai_tool,
            {
                "average_rating": flt(avg[0].avg_rating, 2),
                "review_count": cint(avg[0].review_count),
            },
        )
        frappe.db.commit()


def has_permission(doc, ptype, user):
    """Custom permission check for AI Tool."""
    if frappe.has_role("System Manager", user):
        return True
    if ptype in ("read", "write") and frappe.has_role("AI Tool Manager", user):
        return True
    if ptype == "read" and frappe.has_role("AI Tool User", user):
        return True
    return False


# ─────────────────────────────────────────────
# Scheduler Jobs
# ─────────────────────────────────────────────

def sync_tool_metadata():
    """Daily job: re-fetch metadata for enabled tools with an external URL."""
    tools = frappe.get_all(
        "AI Tool",
        filters={"is_active": 1, "tool_url": ["!=", ""]},
        fields=["name", "tool_url"],
    )
    for tool in tools:
        try:
            resp = requests.head(tool.tool_url, timeout=5)
            status = "Online" if resp.status_code < 400 else "Offline"
            frappe.db.set_value("AI Tool", tool.name, "availability_status", status)
        except Exception:
            frappe.db.set_value("AI Tool", tool.name, "availability_status", "Unknown")
    frappe.db.commit()


def generate_weekly_summary():
    """Weekly: create a summary notification for AI Tool Managers."""
    total_tools = frappe.db.count("AI Tool", {"is_active": 1})
    total_checks = frappe.db.count("AI Tool Check Log", {"creation": [">=", frappe.utils.add_days(nowdate(), -7)]})
    total_reviews = frappe.db.count("AI Tool Review", {"creation": [">=", frappe.utils.add_days(nowdate(), -7)]})

    msg = _(
        f"Weekly AI Tool Summary: {total_tools} active tools, "
        f"{total_checks} checks, {total_reviews} new reviews in the last 7 days."
    )
    frappe.sendmail(
        recipients=frappe.get_all("Has Role", filters={"role": "AI Tool Manager"}, pluck="parent"),
        subject=_("Weekly AI Tool Summary"),
        message=msg,
        now=True,
    )


# ─────────────────────────────────────────────
# Whitelisted API Methods (called from JS/Portal)
# ─────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def get_tools_by_industry(industry, limit=20, offset=0):
    """Return AI tools filtered by industry."""
    filters = {"is_active": 1}
    if industry and industry != "All":
        filters["industry"] = industry

    tools = frappe.get_all(
        "AI Tool",
        filters=filters,
        fields=[
            "name", "tool_name", "short_description", "tool_url",
            "logo_image", "pricing_model", "average_rating",
            "review_count", "industry", "category", "check_count",
        ],
        order_by="average_rating desc, check_count desc",
        limit=int(limit),
        start=int(offset),
    )
    total = frappe.db.count("AI Tool", filters)
    return {"tools": tools, "total": total}


@frappe.whitelist(allow_guest=True)
def get_all_industries():
    """Return all active industries."""
    return frappe.get_all(
        "AI Tool Industry",
        filters={"is_active": 1},
        fields=["name", "industry_name", "icon", "description"],
        order_by="sort_order asc",
    )


@frappe.whitelist(allow_guest=True)
def get_tool_detail(tool_name):
    """Return full detail for a single AI Tool."""
    doc = frappe.get_doc("AI Tool", tool_name)
    reviews = frappe.get_all(
        "AI Tool Review",
        filters={"ai_tool": tool_name, "docstatus": 1},
        fields=["reviewer_name", "rating", "review_text", "creation"],
        order_by="creation desc",
        limit=10,
    )
    return {"tool": doc.as_dict(), "reviews": reviews}


@frappe.whitelist()
def log_tool_check(ai_tool, industry=None, notes=None):
    """Log a user's check/visit for an AI Tool."""
    log = frappe.new_doc("AI Tool Check Log")
    log.ai_tool = ai_tool
    log.checked_by = frappe.session.user
    log.check_date = nowdate()
    log.industry_context = industry
    log.notes = notes
    log.insert(ignore_permissions=True)
    return {"status": "ok", "log_id": log.name}


@frappe.whitelist()
def submit_review(ai_tool, rating, review_text):
    """Submit a review for an AI Tool."""
    # Check if user already reviewed
    existing = frappe.db.exists(
        "AI Tool Review",
        {"ai_tool": ai_tool, "reviewer": frappe.session.user},
    )
    if existing:
        frappe.throw(_("You have already submitted a review for this tool."))

    review = frappe.new_doc("AI Tool Review")
    review.ai_tool = ai_tool
    review.reviewer = frappe.session.user
    review.reviewer_name = frappe.db.get_value("User", frappe.session.user, "full_name")
    review.rating = flt(rating)
    review.review_text = review_text
    review.review_date = nowdate()
    review.insert(ignore_permissions=True)
    review.submit()
    return {"status": "ok", "review_id": review.name}


@frappe.whitelist(allow_guest=True)
def search_tools(query, industry=None, category=None, pricing=None):
    """Full-text search for AI Tools."""
    conditions = ["is_active = 1"]
    values = {}

    if query:
        conditions.append(
            "(tool_name LIKE %(query)s OR short_description LIKE %(query)s OR tags LIKE %(query)s)"
        )
        values["query"] = f"%{query}%"
    if industry:
        conditions.append("industry = %(industry)s")
        values["industry"] = industry
    if category:
        conditions.append("category = %(category)s")
        values["category"] = category
    if pricing:
        conditions.append("pricing_model = %(pricing)s")
        values["pricing"] = pricing

    where_clause = " AND ".join(conditions)
    tools = frappe.db.sql(
        f"""SELECT name, tool_name, short_description, tool_url,
                   logo_image, pricing_model, average_rating,
                   review_count, industry, category
            FROM `tabAI Tool`
            WHERE {where_clause}
            ORDER BY average_rating DESC, check_count DESC
            LIMIT 50""",
        values,
        as_dict=True,
    )
    return tools


@frappe.whitelist(allow_guest=True)
def get_dashboard_stats():
    """Return summary stats for the dashboard."""
    return {
        "total_tools": frappe.db.count("AI Tool", {"is_active": 1}),
        "total_industries": frappe.db.count("AI Tool Industry", {"is_active": 1}),
        "total_categories": frappe.db.count("AI Tool Category", {"is_active": 1}),
        "total_reviews": frappe.db.count("AI Tool Review"),
        "total_checks": frappe.db.count("AI Tool Check Log"),
        "top_tools": frappe.get_all(
            "AI Tool",
            filters={"is_active": 1},
            fields=["tool_name", "average_rating", "check_count", "industry"],
            order_by="check_count desc",
            limit=5,
        ),
    }
