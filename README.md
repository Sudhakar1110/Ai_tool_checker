# 🤖 AI Tool Checker — ERPNext v15+ Frappe App

A comprehensive **AI Tool Discovery & Industry Compatibility Checker** built on the Frappe Framework v15+ and ERPNext v15+. This app lets users search, evaluate, and manage AI tools mapped to specific industries — similar in spirit to tools like ChatGPT's plugin/tool explorer, but fully embedded inside your ERPNext ecosystem.

---

## 📁 Project Structure

```
ai_tool_checker/
├── ai_tool_checker/                   # Main app module
│   ├── config/
│   │   ├── __init__.py
│   │   └── desktop.py                 # Workspace / Desktop config
│   ├── doctype/
│   │   ├── ai_tool/                   # Master: AI Tool
│   │   ├── ai_tool_industry/          # Master: Industry mapping
│   │   ├── ai_tool_category/          # Master: Category
│   │   ├── ai_tool_check_log/         # Transactional: Check Log
│   │   └── ai_tool_review/            # Transactional: User Review
│   ├── report/
│   │   ├── ai_tool_industry_summary/  # Report: Tools per Industry
│   │   └── ai_tool_usage_report/      # Report: Usage analytics
│   ├── page/
│   │   └── ai_tool_dashboard/         # Custom Page: Dashboard
│   ├── notification/                  # Notification configs
│   ├── fixtures/                      # Demo/seed data
│   ├── public/
│   │   ├── css/ai_tool_checker.css
│   │   └── js/ai_tool_checker.js
│   ├── templates/pages/
│   │   └── ai_tool_portal.html        # Web portal page
│   ├── hooks.py                       # App hooks
│   ├── __init__.py
│   └── utils.py                       # Shared utilities
├── setup.py
├── MANIFEST.in
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Setup

### 1. Prerequisites
- Frappe Framework v15+
- ERPNext v15+
- Python 3.10+
- Node.js 18+

### 2. Install the App

```bash
# From your frappe-bench directory
cd /home/frappe/frappe-bench

# Get the app
bench get-app ai_tool_checker https://github.com/YOUR_ORG/ai_tool_checker

# Install on your site
bench --site your-site.localhost install-app ai_tool_checker

# Run migrations
bench --site your-site.localhost migrate

# Load fixtures (demo data)
bench --site your-site.localhost execute ai_tool_checker.fixtures.install.load_fixtures

# Build assets
bench build --app ai_tool_checker

# Restart
bench restart
```

### 3. Access the App
- Navigate to **AI Tool Checker** workspace in ERPNext
- Or visit `https://your-site/ai-tools` for the web portal

---

## 📦 DocTypes Overview

| DocType | Type | Purpose |
|---|---|---|
| AI Tool | Master | Core AI tool record (name, URL, description, pricing) |
| AI Tool Industry | Master | Industry definitions and tags |
| AI Tool Category | Master | Categories (NLP, Vision, Code, etc.) |
| AI Tool Check Log | Transactional | Log of user checks/queries |
| AI Tool Review | Transactional | User ratings and reviews |

---

## 📊 Reports

| Report | Type | Description |
|---|---|---|
| AI Tool Industry Summary | Script Report | Tools grouped by industry with scores |
| AI Tool Usage Report | Script Report | Usage analytics over time |

---

## 🔔 Notifications

| Notification | Trigger | Recipients |
|---|---|---|
| New AI Tool Added | On Insert (AI Tool) | All Users with AI Tool Checker role |
| Review Submitted | On Insert (AI Tool Review) | Tool Owner |

---

## 🏗️ Workspace
- **AI Tool Checker** workspace with shortcuts to all DocTypes, Reports, and the Dashboard page.

---

## 🌐 Web Portal
- `/ai-tools` — Public-facing tool explorer portal

---

## 🧩 Roles & Permissions

| Role | Permissions |
|---|---|
| AI Tool Manager | Full CRUD on all DocTypes |
| AI Tool User | Read + Create Check Log + Create Review |
| System Manager | Full access |

---

## 🔧 Configuration

Set these keys in **ERPNext > AI Tool Checker Settings**:

```python
# Optional: OpenAI API key for AI-powered recommendations
OPENAI_API_KEY = "sk-..."

# Default industries to show on portal
DEFAULT_INDUSTRIES = ["Manufacturing", "Healthcare", "Retail", "Finance", "Education"]
```

---

## 📄 License
MIT License — Free to use and modify.
