# Misty AI Enterprise System

![Bravedatum](assets/bravedatum.jpg)

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39-FF4B4B?logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1.2-1C3C3C)
![LangGraph](https://img.shields.io/badge/LangGraph-1.0-purple)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.5--flash-4285F4?logo=google&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3FCF8E?logo=supabase&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

AI-powered enterprise automation platform for jazz vinyl retail operations.

[![Deployment](https://img.shields.io/badge/Deployment-Live%20App-blue?style=for-the-badge&logo=streamlit)](https://misty-erp.streamlit.app/)
## Overview

Misty AI Enterprise System is an internal operations platform for Misty Jazz Records. It consolidates business intelligence, customer relationship management, and AI-assisted workflows into a single interface. The system enables operations staff to monitor sales metrics, generate marketing content, query internal knowledge bases, and receive AI-driven business recommendations without requiring technical expertise.

**What problem does it solve?**
- Replaces manual business reporting with automated AI-powered analysis
- Centralizes scattered knowledge documents into a searchable RAG system
- Automates repetitive marketing tasks like email generation and review responses
- Provides real-time visibility into business health across financial, customer, and inventory dimensions

## Features

### AI Issues Agent (Main Feature)

The AI Issues Agent is the core intelligence system of this platform. It provides autonomous business issue detection and resolution through a sophisticated multi-stage pipeline:

**How It Works:**
1. **SQL Generation (Stage 0)** - AI analyzes database schema and generates targeted SQL queries for specific business domains
2. **Issue Identification (Stage 1)** - Query results are analyzed to identify critical business issues with severity levels
3. **Fix Proposals (Stage 2)** - Automated fix proposals with pre-generated emails ready for management approval

**Key Capabilities:**
- Domain-focused analysis (inventory, payments, customers, revenue, or comprehensive)
- Real-time data dashboard with query results
- On-demand email generation for any identified issue
- Four email types: management, supplier, customer, team notifications
- Template-based email system using `tools_templates/`

**Two Operating Modes:**
- **Classic Mode** - Three-stage UI with step-by-step analysis
- **Conversational Mode** - Multi-turn ReAct agent dialogue with natural language interaction

See [docs/TOOLS.md](docs/TOOLS.md) for complete documentation of all 26 function calling tools.

### Other Features

- **Real-time Analytics Dashboard** - Sales, inventory, customer, and payment metrics with interactive visualizations
- **RAG Knowledge Base** - Query 15+ enterprise documents and jazz domain research with source citations
- **Marketing Automation** - Customer segmentation and AI-generated email campaigns
- **Review Response Management** - Batch sentiment analysis and automated response generation
- **Document Management** - Upload, index, and view PDF/Markdown/Text documents in cloud storage
- **Activity Logging** - Comprehensive audit trails for all system actions
- **Token-based Authentication** - Enterprise invitation workflows with role-based access control

## Tech Stack

**Backend:**
- Python 3.13
- Google Gemini API under GCP Vertex AI
- Supabase (PostgreSQL with pgvector)
- EmailJS for transactional email

**Frontend:**
- Streamlit 1.39.0

**Database:**
- Supabase PostgreSQL with row-level security
- pgvector extension for RAG embeddings
- Cloud storage buckets for document files

**AI/ML:**
- Google Vertex AI / Gemini 2.5-flash for LLM inference
- LangChain 1.2.1 for agent orchestration
- LangGraph 1.0.5 for agentic workflows (ReAct pattern)
- Google text-embedding-004 for vector embeddings
- TextBlob for sentiment analysis
- PyMuPDF for PDF text extraction
- Langfuse and LangSmith for LLM observability

## Architecture

The system implements a three-tier architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│  Streamlit Components (Dashboard, Analytics, RAG, CRM, Admin)   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                              │
│  AI Agents (6) │ Core Services (6) │ Function Tools (23)        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                │
│  Supabase PostgreSQL │ pgvector │ Storage Buckets               │
└─────────────────────────────────────────────────────────────────┘
```

**Key Design Decisions:**
- Streamlit over SPA frameworks for rapid internal tooling iteration
- LangChain agents with separated query (read-only) and generation (write) tools
- Custom authentication over Supabase Auth for enterprise invitation workflows
- Dual observability stack (Langfuse + LangSmith) for LLM tracing
- Singleton ClientManager pattern for shared database connections

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture decisions and technical justifications.

## Installation & Setup

### Prerequisites
- Python 3.11+
- Supabase project with pgvector extension
- Google Cloud project with Vertex AI API enabled
- EmailJS account (for email features)

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/leechin1/enterprise-ai-powered-sys.git
cd enterprise-ai-powered-sys
```

2. Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit both files with your credentials
```

**Required environment variables:**
```toml
# Google Cloud / Vertex AI
[gcp]
GCP_PROJECT_ID = "your-project-id"
GCP_LOCATION = "us-central1"
VERTEX_MODEL = "gemini-2.5-flash"
GOOGLE_APPLICATION_CREDENTIALS_JSON = '{"type": "service_account", ...}'

# Supabase
[supabase]
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_SECRET_KEY = "your-service-role-key"

# EmailJS
[emailjs]
EMAILJS_SERVICE_ID = "service_xxxxx"
EMAILJS_TEMPLATE_ID = "template_xxxxx"
EMAILJS_PUBLIC_KEY = "your-public-key"
EMAILJS_PRIVATE_KEY = "your-private-key"
PLACEBO_MODE = "true"
PLACEBO_EMAIL = "test@example.com"

# Observability (Optional)
[langfuse]
LANGFUSE_SECRET_KEY = "sk-lf-xxxxx"
LANGFUSE_PUBLIC_KEY = "pk-lf-xxxxx"
LANGFUSE_HOST = "https://cloud.langfuse.com"
```

4. Run the application:
```bash
streamlit run main.py
```

Access at `http://localhost:8501`

## Usage

1. **Login** with credentials or use an invitation token for first-time access
2. **Dashboard**: View KPIs, recent activity, and system health at a glance
3. **Analytics**: Explore interactive charts for sales, customers, inventory, and payments
4. **Business Reporting**:
   - Classic Mode: Three-stage AI analysis (SQL generation → issue identification → fix proposals)
   - Conversational Mode: Multi-turn dialogue with ReAct agent
5. **Knowledge**: Query enterprise documents or research jazz topics with RAG
6. **Marketing & CRM**: Segment customers, generate AI emails, manage review responses
7. **Configure**: Manage users, view activity logs, adjust settings

## Deployment

**Live Application:** Deployed on Streamlit Community Cloud

**Deployment Platform:** Streamlit Cloud

**Deployment Steps:**
1. Push code to GitHub repository
2. Connect repository at [share.streamlit.io](https://share.streamlit.io)
3. Configure secrets in Streamlit Cloud dashboard (Settings > Secrets)
4. Ensure `.streamlit/config.toml` contains `headless = true`

**Production Considerations:**
- Set `PLACEBO_MODE=false` for real email delivery
- All external emails route to `hi@mistyrecords.com` (configurable in `services/config.py`)
- Configure proper GCP service account permissions
- Enable Supabase RLS policies

## Project Structure

```
enterprise-ai-powered-sys/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
│
├── .streamlit/
│   ├── config.toml                  # Streamlit configuration
│   └── secrets.toml                 # Environment secrets (gitignored)
│
├── assets/
│   └── enterprise_documents/        # RAG knowledge base (15 MD files + PDFs)
│       ├── 01_company_manifesto.md
│       ├── 02_active_personnel.md
│       ├── ...                      # 15 enterprise policy documents
│       └── 15_team_profiles.md
│
├── auth/
│   └── auth_service.py              # Authentication (Argon2, tokens, sessions)
│
├── db_configure/
│   ├── migrations/                  # SQL migrations
│   │   ├── 01_core_tables.sql       # Albums, customers, orders, reviews
│   │   ├── 02_workflow_tables.sql   # Workflow tracking
│   │   ├── 03_indexes.sql           # Performance indexes
│   │   ├── 04_rls_policies.sql      # Row-level security
│   │   ├── 05_activity_logs_table.sql
│   │   ├── 06_auth_tables.sql       # Users, tokens, invitations
│   │   ├── create_readonly_sql_function.sql
│   │   ├── create_saved_queries_table.sql
│   │   └── setup_vector_embeddings.sql  # pgvector for RAG
│   └── data-gen/                    # Synthetic test data generation
│       ├── config.py
│       ├── db_connector.py
│       └── prompts/                 # LLM prompts for data generation
│
├── docs/
│   ├── ARCHITECTURE.md              # Architecture decisions
│   ├── TOOLS.md                     # Function calling tools reference (26 tools)
│   └── agent_architecture.md        # Agent design patterns
│
├── frontend/
│   ├── styles.py                    # CSS theming
│   └── components/                  # UI modules
│       ├── dashboard.py             # KPIs and overview
│       ├── analytics.py             # Charts and visualizations
│       ├── ai_reporting_agent.py    # Business intelligence UI
│       ├── rag.py                   # Knowledge base & document management
│       ├── marketing_emails.py      # CRM and email campaigns
│       ├── activity.py              # Activity logs viewer
│       ├── authentication.py        # Login/signup forms
│       ├── admin_configure.py       # System settings
│       └── admin_user_management.py # User administration
│
├── scripts/
│   ├── index_documents.py           # RAG document indexing
│   └── migrate_users_to_supabase.py # User migration utility
│
├── services/
│   ├── config.py                    # Centralized configuration
│   │
│   ├── # AI Agents (5)
│   ├── ai_business_consultant_agent.py  # Main business analysis agent
│   ├── ai_issues_agent.py               # Issue detection pipeline
│   ├── ai_conversational_issues_agent.py # ReAct conversational agent
│   ├── ai_health_agent.py               # Business health scoring
│   ├── ai_review_response_agent.py      # Review response generation
│   │
│   ├── # Core Services (6)
│   ├── rag_service.py               # RAG with PDF/MD/TXT support
│   ├── marketing_service.py         # Customer segmentation & emails
│   ├── email_service.py             # EmailJS integration
│   ├── auth_email_service.py        # Auth notification emails
│   ├── activity_log_service.py      # Audit trail logging
│   ├── jazz_research_service.py     # Jazz domain research
│   │
│   ├── prompts/                     # LLM prompt templates (15 files)
│   │   ├── conversational_issues_agent_prompt.txt
│   │   ├── marketing_email_system_instructions.txt
│   │   ├── rag_chatbot_system_prompt.txt
│   │   └── ...
│   │
│   ├── schemas/                     # Pydantic response models
│   │   ├── ba_agent_schemas.py      # Business agent responses
│   │   ├── marketing_schemas.py     # Email campaign schemas
│   │   └── review_agent_schemas.py  # Review response schemas
│   │
│   ├── tools/                       # LangChain function tools (26 tools)
│   │   ├── __init__.py              # Tool exports
│   │   ├── base.py                  # Base tools class
│   │   ├── query_tools.py           # 11 read-only analytics tools
│   │   ├── generation_tools.py      # 4 content generation tools
│   │   ├── issues_query_tools.py    # SQL generation & execution (2 tools)
│   │   ├── issues_analysis_tools.py # Issue identification (4 tools)
│   │   ├── issues_fix_tools.py      # Fix proposals & email sending (4 tools)
│   │   ├── issues_utility_tools.py  # State management (2 tools)
│   │   ├── issues_state.py          # Shared state singleton
│   │   └── prompts/                 # Issues agent prompts
│   │       ├── __init__.py          # Prompt loader
│   │       ├── issues_stage0_sql_generation_prompt.txt
│   │       ├── issues_stage1_analysis_prompt.txt
│   │       └── issues_stage2_fixes_prompt.txt
│   │
│   └── tools_templates/             # Email/report templates (8 templates)
│       ├── customer_email_template.txt
│       ├── customer_notification_template.txt
│       ├── inventory_alert_email_template.txt
│       ├── management_notification_template.txt
│       ├── restock_recommendation_template.txt
│       ├── supplier_notification_template.txt
│       ├── team_notification_template.txt
│       └── transaction_cancelled_template.txt
│
└── utils/
    ├── clients.py                   # ClientManager singleton (Supabase, Vertex AI)
    ├── db_analytics.py              # Analytics query layer
    └── database_schema.py           # Schema documentation for LLM context
```

## Team

- **Carolina Lee Chin** - Project Lead
- **Cicero Dias dos Santos** - Backend Development
- **Luis Soeiro** - AI/ML Engineering
- **Ishak Soltani** - Frontend & UX

## License

MIT License

Copyright (c) 2025 Bravedatum

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
