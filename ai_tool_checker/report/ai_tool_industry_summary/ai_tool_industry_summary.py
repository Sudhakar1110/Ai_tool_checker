"""
AI Tool Industry Summary Report
Shows a breakdown of AI tools per industry with avg rating and check counts.
"""

import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)
    return columns, data, None, chart, summary


def get_columns():
    return [
        {
            "fieldname": "industry_name",
            "label": _("Industry"),
            "fieldtype": "Link",
            "options": "AI Tool Industry",
            "width": 180,
        },
        {
            "fieldname": "tool_count",
            "label": _("Total Tools"),
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "fieldname": "active_tools",
            "label": _("Active Tools"),
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "fieldname": "avg_rating",
            "label": _("Avg Rating"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 120,
        },
        {
            "fieldname": "total_checks",
            "label": _("Total Checks"),
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "fieldname": "total_reviews",
            "label": _("Total Reviews"),
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "fieldname": "top_tool",
            "label": _("Top Tool"),
            "fieldtype": "Link",
            "options": "AI Tool",
            "width": 200,
        },
        {
            "fieldname": "pricing_breakdown",
            "label": _("Pricing Mix"),
            "fieldtype": "Data",
            "width": 200,
        },
    ]


def get_data(filters):
    conditions = ""
    if filters.get("industry"):
        conditions += f" AND i.name = '{filters['industry']}'"
    if filters.get("category"):
        conditions += f" AND t.category = '{filters['category']}'"
    if filters.get("is_active") is not None:
        conditions += f" AND t.is_active = {1 if filters['is_active'] else 0}"

    raw = frappe.db.sql(
        f"""
        SELECT
            i.name                          AS industry_name,
            COUNT(t.name)                   AS tool_count,
            SUM(t.is_active)                AS active_tools,
            ROUND(AVG(t.average_rating), 2) AS avg_rating,
            SUM(COALESCE(t.check_count, 0)) AS total_checks,
            SUM(COALESCE(t.review_count, 0))AS total_reviews
        FROM `tabAI Tool Industry` i
        LEFT JOIN `tabAI Tool` t ON t.industry = i.name
        WHERE i.is_active = 1
        {conditions}
        GROUP BY i.name
        ORDER BY tool_count DESC
        """,
        as_dict=True,
    )

    # Enrich: top tool per industry and pricing breakdown
    for row in raw:
        top = frappe.db.sql(
            """SELECT tool_name FROM `tabAI Tool`
               WHERE industry = %s AND is_active = 1
               ORDER BY check_count DESC LIMIT 1""",
            row.industry_name,
        )
        row["top_tool"] = top[0][0] if top else ""

        pricing = frappe.db.sql(
            """SELECT pricing_model, COUNT(*) AS cnt
               FROM `tabAI Tool`
               WHERE industry = %s AND is_active = 1
               GROUP BY pricing_model""",
            row.industry_name,
            as_dict=True,
        )
        row["pricing_breakdown"] = ", ".join(
            f"{p.pricing_model}:{p.cnt}" for p in pricing if p.pricing_model
        )

    return raw


def get_chart(data):
    labels = [d.get("industry_name") for d in data]
    tool_counts = [d.get("tool_count", 0) for d in data]
    avg_ratings = [d.get("avg_rating") or 0 for d in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": _("Total Tools"), "values": tool_counts},
                {"name": _("Avg Rating"), "values": avg_ratings},
            ],
        },
        "type": "bar",
        "colors": ["#5e64ff", "#f5a623"],
        "barOptions": {"stacked": 0},
    }


def get_summary(data):
    total_tools = sum(d.get("tool_count", 0) or 0 for d in data)
    total_checks = sum(d.get("total_checks", 0) or 0 for d in data)
    best = max(data, key=lambda d: d.get("avg_rating") or 0, default={})
    return [
        {"label": _("Total Tools"), "value": total_tools, "indicator": "blue"},
        {"label": _("Total Checks"), "value": total_checks, "indicator": "green"},
        {
            "label": _("Best Rated Industry"),
            "value": best.get("industry_name", "N/A"),
            "indicator": "orange",
        },
    ]
