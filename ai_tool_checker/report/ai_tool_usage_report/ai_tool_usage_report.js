// ai_tool_usage_report.js
frappe.query_reports["AI Tool Usage Report"] = {
    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.nowdate(), -3),
            reqd: 1,
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.nowdate(),
            reqd: 1,
        },
        {
            fieldname: "ai_tool",
            label: __("AI Tool"),
            fieldtype: "Link",
            options: "AI Tool",
        },
        {
            fieldname: "checked_by",
            label: __("User"),
            fieldtype: "Link",
            options: "User",
        },
        {
            fieldname: "industry",
            label: __("Industry"),
            fieldtype: "Link",
            options: "AI Tool Industry",
        },
    ],
};
