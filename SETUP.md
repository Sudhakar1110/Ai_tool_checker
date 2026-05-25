# 🚀 Complete Setup Guide — AI Tool Checker for ERPNext v15+

This document walks you through every step to install, configure, and extend the **AI Tool Checker** Frappe/ERPNext app from scratch.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Bench & Site Setup](#bench--site-setup)
3. [App Installation](#app-installation)
4. [Database Migration](#database-migration)
5. [Fixture / Demo Data Loading](#fixture--demo-data-loading)
6. [Asset Build](#asset-build)
7. [DocTypes Explained](#doctypes-explained)
8. [Reports Explained](#reports-explained)
9. [Workspace Setup](#workspace-setup)
10. [Notifications Setup](#notifications-setup)
11. [Custom Page (Dashboard)](#custom-page-dashboard)
12. [Web Portal](#web-portal)
13. [Roles & Permissions](#roles--permissions)
14. [Scheduled Tasks](#scheduled-tasks)
15. [API Reference](#api-reference)
16. [Git Workflow](#git-workflow)
17. [Extending the App](#extending-the-app)
18. [Troubleshooting](#troubleshooting)

---

## 1. Prerequisites

| Requirement | Version |
|---|---|
| Ubuntu / Debian | 20.04+ |
| Python | 3.10+ |
| Node.js | 18+ |
| MariaDB | 10.6+ |
| Redis | 6+ |
| Frappe Framework | v15+ |
| ERPNext | v15+ |
| frappe-bench | Latest |

```bash
# Check versions
python3 --version        # >= 3.10
node --version           # >= 18
bench --version          # >= 5.x
mysql --version          # >= 10.6
```

---

## 2. Bench & Site Setup

> Skip if you already have a running bench with ERPNext v15.

```bash
# Install bench
pip install frappe-bench

# Init a new bench
bench init frappe-bench --frappe-branch version-15
cd frappe-bench

# Get ERPNext
bench get-app erpnext --branch version-15

# Create a new site
bench new-site your-site.localhost \
    --db-root-password YOUR_MYSQL_ROOT_PASS \
    --admin-password YOUR_ADMIN_PASS

# Install ERPNext on the site
bench --site your-site.localhost install-app erpnext

# Start the bench (dev mode)
bench start
```

---

## 3. App Installation

### Option A — From Git (recommended)
```bash
cd /home/frappe/frappe-bench

# Clone the app
bench get-app ai_tool_checker https://github.com/YOUR_ORG/ai_tool_checker.git

# Install on your site
bench --site your-site.localhost install-app ai_tool_checker
```

### Option B — Local Development (copy files)
```bash
# Copy app to apps/ directory
cp -r /path/to/ai_tool_checker /home/frappe/frappe-bench/apps/

# Install
bench --site your-site.localhost install-app ai_tool_checker
```

---

## 4. Database Migration

After installing, run migrations to create all database tables for the new DocTypes.

```bash
bench --site your-site.localhost migrate
```

This will create the following tables in MariaDB:
- `tabAI Tool`
- `tabAI Tool Industry`
- `tabAI Tool Category`
- `tabAI Tool Check Log`
- `tabAI Tool Review`

**Verify tables exist:**
```bash
bench --site your-site.localhost mariadb
# Inside MariaDB:
SHOW TABLES LIKE 'tabAI Tool%';
```

---

## 5. Fixture / Demo Data Loading

Load seed data (roles, industries, categories, demo tools):

```bash
# Via bench execute
bench --site your-site.localhost execute ai_tool_checker.fixtures.install.load_fixtures

# OR via bench migrate (auto-runs after_install hook)
```

**What gets seeded:**
- 2 Roles: `AI Tool Manager`, `AI Tool User`
- 10 AI Tool Categories (NLP, Vision, Code Gen, etc.)
- 12 Industries (Manufacturing, Healthcare, Retail, etc.)
- 5 Demo AI Tools (ChatGPT, GitHub Copilot, Jasper, etc.)

**Load fixtures from JSON (if exporting/importing between sites):**
```bash
bench --site your-site.localhost import-fixtures --app ai_tool_checker
```

---

## 6. Asset Build

Build CSS/JS assets so the custom styles and scripts are served correctly.

```bash
# Full build
bench build --app ai_tool_checker

# Production build (minified)
bench build --app ai_tool_checker --production

# Watch mode (dev)
bench watch
```

After building, verify assets exist:
```bash
ls frappe-bench/sites/assets/ai_tool_checker/
# Should show: css/ai_tool_checker.css, js/ai_tool_checker.js
```

---

## 7. DocTypes Explained

### 7.1 AI Tool (Master)
**Path:** `ai_tool_checker/doctype/ai_tool/`

The core record for each AI tool.

| Field | Type | Notes |
|---|---|---|
| tool_name | Data | Unique, autoname key |
| short_description | Small Text | Shown in cards |
| category | Link → AI Tool Category | Required |
| industry | Link → AI Tool Industry | Primary industry |
| tool_url | URL | External link |
| logo_image | Attach Image | Shown in portal |
| pricing_model | Select | Free/Freemium/Paid/Enterprise/Open Source |
| is_active | Check | Default: 1 |
| availability_status | Select | Auto-updated by daily job |
| average_rating | Float | Auto-calculated from reviews |
| review_count | Int | Auto-calculated |
| check_count | Int | Auto-incremented on check log |
| tags | Data | Comma-separated for search |
| full_description | Text Editor | Rich text |
| key_features | Table | Child table: AI Tool Feature |
| supported_industries | Table MultiSelect | Multiple industries |

**Custom buttons in form:**
- `Actions > Visit Tool` — Opens tool URL in new tab
- `Actions > Log a Check` — Creates a Check Log entry
- `Actions > View Reviews` — Navigates to filtered review list

### 7.2 AI Tool Industry (Master)
**Path:** `ai_tool_checker/doctype/ai_tool_industry/`

Industry definitions used to categorise tools.

| Field | Type | Notes |
|---|---|---|
| industry_name | Data | Unique, autoname key |
| icon | Data | Emoji or CSS icon class |
| is_active | Check | Controls portal visibility |
| sort_order | Int | Controls tab order in portal |
| description | Text | Optional |

### 7.3 AI Tool Category (Master)
**Path:** `ai_tool_checker/doctype/ai_tool_category/`

Technology categories for tools (NLP, Vision, Code, etc.).

### 7.4 AI Tool Check Log (Transactional)
**Path:** `ai_tool_checker/doctype/ai_tool_check_log/`

Records every time a user "checks" or views a tool.

| Field | Notes |
|---|---|
| ai_tool | Linked tool |
| checked_by | User who checked (defaults to session user) |
| check_date | Defaults to today |
| industry_context | Which industry context the check was in |
| notes | Optional free text |

**Auto-numbering:** `AI-CHECK-2024-00001`

### 7.5 AI Tool Review (Transactional, Submittable)
**Path:** `ai_tool_checker/doctype/ai_tool_review/`

User ratings and written reviews. Submittable workflow ensures reviews are "locked" once submitted.

| Field | Notes |
|---|---|
| ai_tool | Linked tool |
| reviewer | User link |
| reviewer_name | Fetched from User.full_name |
| rating | Rating field (1–5) |
| review_date | Defaults to today |
| review_text | Required |

**Validation:** Prevents duplicate reviews from the same user per tool.

---

## 8. Reports Explained

### 8.1 AI Tool Industry Summary
**Type:** Script Report  
**Ref DocType:** AI Tool

Shows each industry with tool count, active tools, average rating, total checks, top tool, and pricing breakdown.

**Filters:**
- Industry (Link)
- Category (Link)
- Active Only (Check)

**Chart:** Bar chart — Tools per Industry vs Avg Rating

**Access:** AI Tool Manager, AI Tool User, System Manager

### 8.2 AI Tool Usage Report
**Type:** Script Report  
**Ref DocType:** AI Tool Check Log

Time-series report of check log activity.

**Filters:**
- From Date / To Date (required)
- AI Tool (optional)
- User (optional)
- Industry (optional)

**Chart:** Line chart — Daily checks over time

**Access:** AI Tool Manager, System Manager

---

## 9. Workspace Setup

The workspace is auto-created via fixtures. To manually create or recreate:

```bash
# Export workspace from source site
bench --site source-site.localhost export-fixtures --app ai_tool_checker

# Import on target site
bench --site target-site.localhost import-fixtures --app ai_tool_checker
```

**Workspace contents:**
- Shortcut: AI Tool (DocType)
- Shortcut: AI Tool Industry (DocType)
- Shortcut: AI Tool Category (DocType)
- Shortcut: AI Tool Review (DocType)
- Shortcut: AI Tool Check Log (DocType)
- Shortcut: Industry Summary (Report)
- Shortcut: Usage Report (Report)
- Shortcut: AI Tool Dashboard (Page)

**Manual steps if needed:**
1. Go to **Build > Workspace** in ERPNext
2. Create new workspace named `AI Tool Checker`
3. Set module to `AI Tool Checker`
4. Add shortcuts using the UI

---

## 10. Notifications Setup

Notifications are loaded as fixtures. To verify:

1. Go to **Settings > Notifications**
2. Confirm these exist and are enabled:
   - `AI Tool - New Tool Added`
   - `AI Tool - Review Submitted`

**Manual creation:**

### Notification: New Tool Added
- Document Type: `AI Tool`
- Event: `New`
- Recipients: Role → `AI Tool Manager`
- Subject: `New AI Tool Added: {{ doc.tool_name }}`

### Notification: Review Submitted
- Document Type: `AI Tool Review`
- Event: `New`
- Recipients: Role → `AI Tool Manager`
- Subject: `New Review for {{ doc.ai_tool }}: {{ doc.rating }}/5 stars`

**Email setup prerequisite:**
```bash
# Configure outgoing email in ERPNext
# Settings > Email > Outgoing Mail Server
```

---

## 11. Custom Page (Dashboard)

The `ai-tool-dashboard` page is registered in `hooks.py` and rendered as a Frappe Page.

**Access:** `https://your-site/app/ai-tool-dashboard`

**Features:**
- Stat cards: total tools, industries, categories, reviews, checks
- Top 5 tools by usage
- Bar chart: tools per industry
- Recent check logs table (last 10)

The page auto-loads data via `frappe.call` to whitelisted Python methods.

---

## 12. Web Portal

The portal provides a **public-facing** tool explorer at `/ai-tools`.

**Access:** `https://your-site/ai-tools`

**Features:**
- Full-text search across tool name, description, tags
- Industry filter tabs
- Tool cards with logo, pricing badge, rating stars
- Infinite scroll (load more)
- Responsive grid layout

**To enable the web portal:**
1. Go to **Settings > Website Settings**
2. Ensure "Enable Frappe Web" is checked

**Route:** Defined in `hooks.py`:
```python
website_route_rules = [
    {"from_route": "/ai-tools", "to_route": "ai_tool_portal"},
]
```

---

## 13. Roles & Permissions

| Role | Create | Read | Write | Delete | Submit |
|---|---|---|---|---|---|
| AI Tool Manager | ✅ | ✅ | ✅ | ✅ | ✅ |
| AI Tool User | ✅ (Log/Review) | ✅ | ❌ | ❌ | ✅ (Review) |
| System Manager | ✅ | ✅ | ✅ | ✅ | ✅ |

**Assign roles to users:**
1. Go to **Users** in ERPNext
2. Open the user record
3. Under **Roles**, add `AI Tool Manager` or `AI Tool User`

---

## 14. Scheduled Tasks

Configured in `hooks.py`:

| Frequency | Function | Purpose |
|---|---|---|
| Daily | `sync_tool_metadata` | Pings each tool URL, updates availability_status |
| Weekly | `generate_weekly_summary` | Sends email summary to AI Tool Managers |

**Manual trigger (for testing):**
```bash
bench --site your-site.localhost execute ai_tool_checker.utils.sync_tool_metadata
bench --site your-site.localhost execute ai_tool_checker.utils.generate_weekly_summary
```

---

## 15. API Reference

All methods are whitelisted via `@frappe.whitelist()`.

### Public Methods (allow_guest=True)

| Method | Parameters | Returns |
|---|---|---|
| `get_tools_by_industry` | industry, limit, offset | {tools[], total} |
| `get_all_industries` | — | industry[] |
| `get_tool_detail` | tool_name | {tool, reviews[]} |
| `search_tools` | query, industry, category, pricing | tool[] |
| `get_dashboard_stats` | — | stats object |

### Authenticated Methods

| Method | Parameters | Returns |
|---|---|---|
| `log_tool_check` | ai_tool, industry, notes | {status, log_id} |
| `submit_review` | ai_tool, rating, review_text | {status, review_id} |

**Example cURL call:**
```bash
curl -X POST https://your-site/api/method/ai_tool_checker.utils.get_tools_by_industry \
  -H "Content-Type: application/json" \
  -d '{"industry": "Healthcare", "limit": 10, "offset": 0}'
```

---

## 16. Git Workflow

### Initial push
```bash
cd /home/frappe/frappe-bench/apps/ai_tool_checker
git init
git add .
git commit -m "feat: initial AI Tool Checker app"
git remote add origin https://github.com/YOUR_ORG/ai_tool_checker.git
git push -u origin main
```

### Branch strategy
```
main          → stable, production-ready
develop       → integration branch
feature/*     → new features
fix/*         → bug fixes
release/*     → release preparation
```

### Export fixtures before committing
```bash
bench --site your-site.localhost export-fixtures --app ai_tool_checker
git add ai_tool_checker/fixtures/
git commit -m "chore: update fixtures"
```

### .gitignore
```
__pycache__/
*.pyc
*.pyo
.env
node_modules/
dist/
*.egg-info/
```

---

## 17. Extending the App

### Add a new DocType (e.g., AI Tool Comparison)
```bash
bench --site your-site.localhost new-doctype "AI Tool Comparison" --module "AI Tool Checker"
```

### Add a new Report
```bash
bench --site your-site.localhost new-report "AI Tool Price Analysis" \
  --ref-doctype "AI Tool" --type "Script Report"
```

### Add an OpenAI-powered recommendation
In `utils.py`:
```python
import openai

@frappe.whitelist(allow_guest=True)
def get_ai_recommendation(industry, use_case):
    client = openai.OpenAI(api_key=frappe.conf.get("openai_api_key"))
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI tool advisor."},
            {"role": "user", "content": f"Recommend AI tools for {industry} to achieve: {use_case}"}
        ]
    )
    return response.choices[0].message.content
```

---

## 18. Troubleshooting

### App not showing in workspace
```bash
bench --site your-site.localhost clear-cache
bench restart
```

### Migrations failing
```bash
bench --site your-site.localhost migrate --skip-failing
# Check logs:
tail -f frappe-bench/logs/worker.error.log
```

### Assets not loading
```bash
bench build --app ai_tool_checker --force
bench --site your-site.localhost clear-cache
```

### Permission denied errors
```bash
# Re-run fixtures
bench --site your-site.localhost execute ai_tool_checker.fixtures.install.after_install
```

### Portal page 404
```bash
# Ensure website is enabled
bench --site your-site.localhost set-config allow_guests_to_sign_up 1
bench --site your-site.localhost set-config website_status 1
```

### Check bench logs
```bash
tail -f frappe-bench/logs/web.error.log
tail -f frappe-bench/logs/worker.error.log
bench --site your-site.localhost console   # interactive Python shell
```

---

## 📞 Support

- Open issues at: `https://github.com/YOUR_ORG/ai_tool_checker/issues`
- ERPNext community: `https://discuss.erpnext.com`
- Frappe docs: `https://frappeframework.com/docs`
