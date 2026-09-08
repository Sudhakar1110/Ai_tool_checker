app_name = "ai_tool_checker"
app_title = "AI Tool Checker"
app_publisher = "Your Organization"
app_description = "AI Tool Discovery & Industry Compatibility Checker for ERPNext v15+"
app_email = "dev@yourorg.com"
app_license = "MIT"
app_version = "1.0.0"

# Required Apps
required_apps = ["frappe", "erpnext"]

# ─────────────────────────────────────────────
# Includes in <head> — CSS & JS
# ─────────────────────────────────────────────
app_include_css = "/assets/ai_tool_checker/css/ai_tool_checker.css"
app_include_js = "/assets/ai_tool_checker/js/ai_tool_checker.js"
web_include_css = "/assets/ai_tool_checker/css/ai_tool_checker.css"
web_include_js = "/assets/ai_tool_checker/js/ai_tool_checker.js"

# ─────────────────────────────────────────────
# Website route rules
# ─────────────────────────────────────────────
website_route_rules = [
    {"from_route": "/ai-tools", "to_route": "ai_tool_portal"},
    {"from_route": "/ai-tools/<name>", "to_route": "ai_tool_detail"},
]

# ─────────────────────────────────────────────
# DocType JS overrides
# ─────────────────────────────────────────────
doctype_js = {
    "AI Tool": "public/js/ai_tool_checker.js",
}

# ─────────────────────────────────────────────
# Fixtures — data to export/import with app
# ─────────────────────────────────────────────
fixtures = [
    {"dt": "Role", "filters": [["name", "in", ["AI Tool Manager", "AI Tool User"]]]},
    {"dt": "AI Tool Category"},
    {"dt": "AI Tool Industry"},
    {"dt": "Workspace", "filters": [["name", "=", "AI Tool Checker"]]},
    {"dt": "Notification", "filters": [["name", "like", "AI Tool%"]]},
]

# ─────────────────────────────────────────────
# DocType Events (server-side hooks)
# ─────────────────────────────────────────────
doc_events = {
    "AI Tool": {
        "after_insert": "ai_tool_checker.utils.on_ai_tool_insert",
        "on_update": "ai_tool_checker.utils.on_ai_tool_update",
    },
    "AI Tool Check Log": {
        "after_insert": "ai_tool_checker.utils.on_check_log_insert",
    },
    "AI Tool Review": {
        "after_insert": "ai_tool_checker.utils.on_review_insert",
        "on_update": "ai_tool_checker.utils.recalculate_tool_rating",
    },
}

# ─────────────────────────────────────────────
# Scheduled tasks
# ─────────────────────────────────────────────
scheduler_events = {
    "daily": [
        "ai_tool_checker.utils.sync_tool_metadata",
    ],
    "weekly": [
        "ai_tool_checker.utils.generate_weekly_summary",
    ],
}

# ─────────────────────────────────────────────
# Permissions
# ─────────────────────────────────────────────
has_permission = {
    "AI Tool": "ai_tool_checker.utils.has_permission",
}

# ─────────────────────────────────────────────
# Override standard methods
# ─────────────────────────────────────────────
override_whitelisted_methods = {}

# ─────────────────────────────────────────────
# Installation hooks
# ─────────────────────────────────────────────
after_install = "ai_tool_checker.fixtures.install.after_install"
before_migrate = "ai_tool_checker.fixtures.install.before_migrate"
after_migrate = "ai_tool_checker.fixtures.install.after_migrate"
