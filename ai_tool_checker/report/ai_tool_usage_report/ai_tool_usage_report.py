"""
AI Tool Usage Report
Trend of check logs over a date range, grouped by tool or user.
"""

import frappe
from frappe import _
from frappe.utils import getdate, nowdate, add_months


def execute(filters=None):
    filters = filters or {}
    filters.setdefault("from_date", str(add_months(nowdate(), -3)))
    filters.setdefault("to_date", str(nowdate()))

    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart(data, filters)
    return columns, data, None, chart


def get_columns(filters):
    cols = [
        {"fieldname": "check_date", "label": _("Date"), "fieldtype": "Date", "width": 120},
        {"fieldname": "ai_tool", "label": _("AI Tool"), "fieldtype": "Link", "options": "AI Tool", "width": 200},
        {"fieldname": "checked_by", "label": _("Checked By"), "fieldtype": "Link", "options": "User", "width": 180},
        {"fieldname": "industry_context", "label": _("Industry"), "fieldtype": "Link", "options": "AI Tool Industry", "width": 150},
        {"fieldname": "notes", "label": _("Notes"), "fieldtype": "Data", "width": 250},
    ]
    return cols


def get_data(filters):
    conditions = "WHERE l.check_date BETWEEN %(from_date)s AND %(to_date)s"
    if filters.get("ai_tool"):
        conditions += " AND l.ai_tool = %(ai_tool)s"
    if filters.get("checked_by"):
        conditions += " AND l.checked_by = %(checked_by)s"
    if filters.get("industry"):
        conditions += " AND l.industry_context = %(industry)s"

    return frappe.db.sql(
        f"""
        SELECT
            l.check_date,
            l.ai_tool,
            l.checked_by,
            l.industry_context,
            l.notes
        FROM `tabAI Tool Check Log` l
        {conditions}
        ORDER BY l.check_date DESC
        LIMIT 500
        """,
        filters,
        as_dict=True,
    )


def get_chart(data, filters):
    # Daily check counts
    from collections import defaultdict
    daily = defaultdict(int)
    for row in data:
        daily[str(row.check_date)] += 1

    sorted_dates = sorted(daily.keys())
    return {
        "data": {
            "labels": sorted_dates,
            "datasets": [{"name": _("Checks"), "values": [daily[d] for d in sorted_dates]}],
        },
        "type": "line",
        "colors": ["#5e64ff"],
        "lineOptions": {"regionFill": 1},
    }
