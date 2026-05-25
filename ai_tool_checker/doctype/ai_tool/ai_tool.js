// ai_tool_checker/doctype/ai_tool/ai_tool.js

frappe.ui.form.on("AI Tool", {
    refresh(frm) {
        frm.add_custom_button(__("Visit Tool"), () => {
            if (frm.doc.tool_url) {
                window.open(frm.doc.tool_url, "_blank");
            } else {
                frappe.msgprint(__("No URL configured for this tool."));
            }
        }, __("Actions"));

        frm.add_custom_button(__("Log a Check"), () => {
            frappe.call({
                method: "ai_tool_checker.utils.log_tool_check",
                args: { ai_tool: frm.doc.name },
                callback(r) {
                    if (!r.exc) frappe.show_alert({ message: __("Check logged!"), indicator: "green" });
                },
            });
        }, __("Actions"));

        frm.add_custom_button(__("View Reviews"), () => {
            frappe.route_options = { ai_tool: frm.doc.name };
            frappe.set_route("List", "AI Tool Review");
        }, __("Actions"));

        // Rating indicator
        if (frm.doc.average_rating) {
            const stars = "★".repeat(Math.round(frm.doc.average_rating)) +
                          "☆".repeat(5 - Math.round(frm.doc.average_rating));
            frm.set_intro(
                `<strong>Rating:</strong> ${stars} ${frm.doc.average_rating}/5 
                 (${frm.doc.review_count || 0} reviews, ${frm.doc.check_count || 0} checks)`,
                "blue"
            );
        }
    },

    tool_url(frm) {
        if (frm.doc.tool_url && !frm.doc.logo_image) {
            // Try to auto-suggest favicon
            const domain = new URL(frm.doc.tool_url).hostname;
            frm.set_intro(`Tip: Add a logo or use https://www.google.com/s2/favicons?domain=${domain}`, "yellow");
        }
    },
});
