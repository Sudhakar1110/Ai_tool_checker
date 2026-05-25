// ai_tool_checker/page/ai_tool_dashboard/ai_tool_dashboard.js
frappe.pages["ai-tool-dashboard"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: "AI Tool Dashboard",
        single_column: true,
    });

    page.main.html(`
        <div id="ai-tool-dashboard" class="ai-dashboard-wrapper">
            <div class="ai-stats-row" id="stats-row"></div>
            <div class="ai-content-row">
                <div class="ai-panel" id="top-tools-panel">
                    <h4>🏆 Top Tools by Usage</h4>
                    <div id="top-tools-list"></div>
                </div>
                <div class="ai-panel" id="industry-chart-panel">
                    <h4>📊 Tools by Industry</h4>
                    <div id="industry-chart"></div>
                </div>
            </div>
            <div class="ai-panel" id="recent-logs-panel">
                <h4>🕒 Recent Check Logs</h4>
                <div id="recent-logs-table"></div>
            </div>
        </div>
    `);

    load_dashboard_data(page);
};

function load_dashboard_data(page) {
    frappe.call({
        method: "ai_tool_checker.utils.get_dashboard_stats",
        callback(r) {
            if (r.exc || !r.message) return;
            const s = r.message;
            render_stats(s);
            render_top_tools(s.top_tools);
        },
    });

    // Load industry chart data via the report
    frappe.call({
        method: "frappe.desk.query_report.run",
        args: { report_name: "AI Tool Industry Summary", filters: {} },
        callback(r) {
            if (r.message && r.message.result) {
                render_industry_chart(r.message.result, r.message.columns);
            }
        },
    });

    // Recent check logs
    frappe.db.get_list("AI Tool Check Log", {
        fields: ["ai_tool", "checked_by", "check_date", "industry_context"],
        order_by: "check_date desc",
        limit: 10,
    }).then((rows) => render_recent_logs(rows));
}

function render_stats(s) {
    const cards = [
        { label: "Total Tools", value: s.total_tools, icon: "🛠️", color: "#5e64ff" },
        { label: "Industries", value: s.total_industries, icon: "🏭", color: "#00BCD4" },
        { label: "Categories", value: s.total_categories, icon: "📂", color: "#4CAF50" },
        { label: "Reviews", value: s.total_reviews, icon: "⭐", color: "#FF9800" },
        { label: "Check Logs", value: s.total_checks, icon: "📋", color: "#9C27B0" },
    ];
    document.getElementById("stats-row").innerHTML = cards
        .map(
            (c) => `
        <div class="ai-stat-card" style="border-top: 3px solid ${c.color}">
            <div class="ai-stat-icon">${c.icon}</div>
            <div class="ai-stat-value">${c.value}</div>
            <div class="ai-stat-label">${c.label}</div>
        </div>`
        )
        .join("");
}

function render_top_tools(tools) {
    if (!tools || !tools.length) {
        document.getElementById("top-tools-list").innerHTML = "<p>No data yet.</p>";
        return;
    }
    document.getElementById("top-tools-list").innerHTML = `
        <table class="table table-bordered table-sm">
            <thead><tr><th>#</th><th>Tool</th><th>Industry</th><th>Rating</th><th>Checks</th></tr></thead>
            <tbody>
                ${tools
                    .map(
                        (t, i) => `<tr>
                    <td>${i + 1}</td>
                    <td><a href="/app/ai-tool/${t.name}">${t.tool_name}</a></td>
                    <td>${t.industry || "-"}</td>
                    <td>${t.average_rating ? "★".repeat(Math.round(t.average_rating)) : "-"}</td>
                    <td>${t.check_count || 0}</td>
                </tr>`
                    )
                    .join("")}
            </tbody>
        </table>`;
}

function render_industry_chart(result, columns) {
    // Use Frappe Charts
    const labels = result.map((r) => r[0] || "Unknown");
    const values = result.map((r) => r[1] || 0);
    const el = document.getElementById("industry-chart");
    if (!labels.length) {
        el.innerHTML = "<p>No industry data.</p>";
        return;
    }
    new frappe.Chart(el, {
        type: "bar",
        data: {
            labels,
            datasets: [{ values }],
        },
        colors: ["#5e64ff"],
        height: 260,
        axisOptions: { xIsSeries: false },
    });
}

function render_recent_logs(rows) {
    if (!rows.length) {
        document.getElementById("recent-logs-table").innerHTML = "<p>No logs yet.</p>";
        return;
    }
    document.getElementById("recent-logs-table").innerHTML = `
        <table class="table table-bordered table-sm">
            <thead><tr><th>Date</th><th>Tool</th><th>User</th><th>Industry</th></tr></thead>
            <tbody>
                ${rows
                    .map(
                        (r) => `<tr>
                    <td>${r.check_date}</td>
                    <td><a href="/app/ai-tool/${r.ai_tool}">${r.ai_tool}</a></td>
                    <td>${r.checked_by}</td>
                    <td>${r.industry_context || "-"}</td>
                </tr>`
                    )
                    .join("")}
            </tbody>
        </table>`;
}
