// ai_tool_industry_summary.js
frappe.query_reports["AI Tool Industry Summary"] = {
    filters: [
        {
            fieldname: "industry",
            label: __("Industry"),
            fieldtype: "Link",
            options: "AI Tool Industry",
        },
        {
            fieldname: "category",
            label: __("Category"),
            fieldtype: "Link",
            options: "AI Tool Category",
        },
        {
            fieldname: "is_active",
            label: __("Active Only"),
            fieldtype: "Check",
            default: 1,
        },
    ],
};
