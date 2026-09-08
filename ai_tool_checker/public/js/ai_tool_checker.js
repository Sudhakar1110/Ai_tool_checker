// ai_tool_checker/public/js/ai_tool_checker.js
// Global helpers and portal logic

window.AIToolChecker = window.AIToolChecker || {};

AIToolChecker.Portal = {
    currentIndustry: "All",
    currentPage: 0,
    pageSize: 12,
    searchQuery: "",

    init() {
        this.bindEvents();
        this.loadIndustries();
        this.loadTools();
    },

    bindEvents() {
        const searchInput = document.getElementById("ai-search-input");
        const searchBtn = document.getElementById("ai-search-btn");
        if (searchInput) {
            searchInput.addEventListener("keydown", (e) => {
                if (e.key === "Enter") this.doSearch();
            });
        }
        if (searchBtn) searchBtn.addEventListener("click", () => this.doSearch());
    },

    doSearch() {
        const q = document.getElementById("ai-search-input")?.value || "";
        this.searchQuery = q.trim();
        this.currentPage = 0;
        this.loadTools(true);
    },

    loadIndustries() {
        frappe.call({
            method: "ai_tool_checker.utils.get_all_industries",
            callback: (r) => {
                if (!r.message) return;
                const container = document.getElementById("ai-industry-tabs");
                if (!container) return;
                const allBtn = `<button class="ai-industry-tab active" data-industry="All">🌐 All</button>`;
                const tabs = r.message
                    .map(
                        (i) =>
                            `<button class="ai-industry-tab" data-industry="${i.name}">${i.icon || ""} ${i.industry_name}</button>`
                    )
                    .join("");
                container.innerHTML = allBtn + tabs;
                container.querySelectorAll(".ai-industry-tab").forEach((btn) => {
                    btn.addEventListener("click", () => {
                        container.querySelectorAll(".ai-industry-tab").forEach((b) => b.classList.remove("active"));
                        btn.classList.add("active");
                        this.currentIndustry = btn.dataset.industry;
                        this.currentPage = 0;
                        this.loadTools(true);
                    });
                });
            },
        });
    },

    loadTools(reset = false) {
        const grid = document.getElementById("ai-tools-grid");
        if (!grid) return;
        if (reset) grid.innerHTML = "";

        if (this.searchQuery) {
            frappe.call({
                method: "ai_tool_checker.utils.search_tools",
                args: {
                    query: this.searchQuery,
                    industry: this.currentIndustry !== "All" ? this.currentIndustry : null,
                },
                callback: (r) => {
                    if (r.message) this.renderTools(r.message, true);
                },
            });
        } else {
            frappe.call({
                method: "ai_tool_checker.utils.get_tools_by_industry",
                args: {
                    industry: this.currentIndustry,
                    limit: this.pageSize,
                    offset: this.currentPage * this.pageSize,
                },
                callback: (r) => {
                    if (r.message) {
                        this.renderTools(r.message.tools, false);
                        const loadMore = document.getElementById("ai-load-more-btn");
                        if (loadMore) {
                            const shown = (this.currentPage + 1) * this.pageSize;
                            loadMore.style.display = shown < r.message.total ? "inline-block" : "none";
                        }
                    }
                },
            });
        }
    },

    loadMore() {
        this.currentPage++;
        this.loadTools(false);
    },

    renderTools(tools, replace = false) {
        const grid = document.getElementById("ai-tools-grid");
        if (!grid) return;
        if (replace) grid.innerHTML = "";
        if (!tools.length && replace) {
            grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-muted)">No tools found.</div>`;
            return;
        }
        tools.forEach((t) => {
            const stars = t.average_rating
                ? "★".repeat(Math.round(t.average_rating)) + "☆".repeat(5 - Math.round(t.average_rating))
                : "☆☆☆☆☆";
            const logo = t.logo_image
                ? `<img class="ai-tool-logo" src="${t.logo_image}" alt="${t.tool_name}" />`
                : `<div class="ai-tool-logo-placeholder">🤖</div>`;
            const card = document.createElement("a");
            card.href = `/ai-tools/${t.name}`;
            card.className = "ai-tool-card";
            card.innerHTML = `
                <div class="ai-tool-card-header">
                    ${logo}
                    <div>
                        <div class="ai-tool-title">${t.tool_name}</div>
                    </div>
                    <span class="ai-tool-pricing">${t.pricing_model || "N/A"}</span>
                </div>
                <div class="ai-tool-desc">${t.short_description || ""}</div>
                <div class="ai-tool-meta">
                    <span class="ai-tool-rating">${stars} ${t.average_rating ? t.average_rating.toFixed(1) : "0.0"}</span>
                    <span class="ai-tool-industry">${t.industry || t.category || ""}</span>
                </div>`;
            grid.appendChild(card);
        });
    },
};

AIToolChecker.Detail = {
    init() {
        const root = document.getElementById("ai-tool-detail");
        const body = document.getElementById("ai-tool-detail-body");
        if (!root || !body) return;

        const toolName = root.dataset.tool;
        if (!toolName) {
            body.innerHTML = `<p>Tool not found.</p>`;
            return;
        }

        frappe.call({
            method: "ai_tool_checker.utils.get_tool_detail",
            args: { tool_name: toolName },
            callback: (r) => {
                if (!r.message || !r.message.tool) {
                    body.innerHTML = `<p>Tool not found.</p>`;
                    return;
                }
                this.render(body, r.message.tool, r.message.reviews || []);
            },
            error: () => {
                body.innerHTML = `<p>Unable to load this tool.</p>`;
            },
        });
    },

    render(body, tool, reviews) {
        const stars = tool.average_rating
            ? "★".repeat(Math.round(tool.average_rating)) + "☆".repeat(5 - Math.round(tool.average_rating))
            : "☆☆☆☆☆";
        const logo = tool.logo_image
            ? `<img class="ai-tool-logo" src="${tool.logo_image}" alt="${tool.tool_name || ""}" />`
            : `<div class="ai-tool-logo-placeholder">🤖</div>`;
        const features = (tool.key_features || [])
            .map((f) => `<li><strong>${f.feature || ""}</strong>${f.description ? ` — ${f.description}` : ""}</li>`)
            .join("");
        const reviewHtml = reviews.length
            ? reviews
                  .map(
                      (rev) => `<div class="ai-review-card">
                    <div class="ai-tool-rating">${"★".repeat(Math.round(rev.rating || 0))}${"☆".repeat(5 - Math.round(rev.rating || 0))}</div>
                    <p>${rev.review_text || ""}</p>
                    <small>${rev.reviewer_name || "Anonymous"} · ${rev.creation || ""}</small>
                </div>`
                  )
                  .join("")
            : `<p>No reviews yet.</p>`;

        body.innerHTML = `
            <div class="ai-tool-detail-header">
                ${logo}
                <div>
                    <h1>${tool.tool_name || toolNameFallback(tool)}</h1>
                    <div class="ai-tool-meta">
                        <span class="ai-tool-rating">${stars} ${tool.average_rating ? Number(tool.average_rating).toFixed(1) : "0.0"}</span>
                        <span class="ai-tool-industry">${tool.industry || tool.category || ""}</span>
                        <span class="ai-tool-pricing">${tool.pricing_model || "N/A"}</span>
                    </div>
                </div>
            </div>
            <p class="ai-tool-desc">${tool.short_description || ""}</p>
            ${tool.full_description ? `<div class="ai-tool-full-desc">${tool.full_description}</div>` : ""}
            ${features ? `<h3>Key Features</h3><ul>${features}</ul>` : ""}
            ${tool.tool_url ? `<p><a class="ai-detail-link" href="${tool.tool_url}" target="_blank" rel="noopener">Visit tool</a></p>` : ""}
            <h3>Reviews</h3>
            ${reviewHtml}
        `;
    },
};

function toolNameFallback(tool) {
    return tool.name || "AI Tool";
}

// Auto-init on portal page
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        if (document.getElementById("ai-tools-portal")) AIToolChecker.Portal.init();
        if (document.getElementById("ai-tool-detail")) AIToolChecker.Detail.init();
    });
} else {
    if (document.getElementById("ai-tools-portal")) AIToolChecker.Portal.init();
    if (document.getElementById("ai-tool-detail")) AIToolChecker.Detail.init();
}
