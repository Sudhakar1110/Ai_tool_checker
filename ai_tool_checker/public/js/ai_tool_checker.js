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

// Auto-init on portal page
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        if (document.getElementById("ai-tools-portal")) AIToolChecker.Portal.init();
    });
} else {
    if (document.getElementById("ai-tools-portal")) AIToolChecker.Portal.init();
}
