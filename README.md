# Misty AI Enterprise System

![Bravedatum](assets/bravedatum.jpg)

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39-FF4B4B?logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-🦜-1C3C3C)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.5--flash-4285F4?logo=google&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3FCF8E?logo=supabase&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

AI-powered enterprise automation platform for jazz vinyl retail operations.

## Overview

Misty AI Enterprise System is an internal operations platform for Misty Jazz Records. It consolidates business intelligence, customer relationship management, and AI-assisted workflows into a single interface. The system enables operations staff to monitor sales metrics, generate marketing content, query internal knowledge bases, and receive AI-driven business recommendations without requiring technical expertise.

## Features

- Real-time analytics dashboard with sales, inventory, customer, and payment metrics
- AI business reporting with automated health analysis and issue detection
- RAG-powered knowledge base for enterprise documents and jazz domain research
- CRM with AI-generated marketing emails and review response automation
- Activity logging with comprehensive audit trails
- Token-based user management with invitation workflows and role-based access

## Tech Stack

**Backend:**
- Python 3.13
- Google Gemini API under GCP Vertex
- Supabase (PostgreSQL)
- EmailJS for transactional email

**Frontend:**
- Streamlit 1.39.0

**Database:**
- Supabase PostgreSQL with row-level security
- pgvector for RAG embeddings

**AI/ML:**
- Google Vertex AI / Gemini 2.5-flash
- LangChain and LangGraph for agent orchestration
- Google text-embedding-004 for embeddings
- Langfuse and LangSmith for observability

## Architecture

The system implements a three-tier architecture:

```
Presentation Layer (Streamlit Components)
                |
Service Layer (AI Agents, Business Logic)
                |
Data Layer (Supabase PostgreSQL)
```

Key design decisions:
- Streamlit over SPA frameworks for rapid internal tooling iteration
- LangChain agents with separated query (read-only) and generation (write) tools
- Custom authentication over Supabase Auth for enterprise invitation workflows
- Dual observability stack (Langfuse + LangSmith) for LLM tracing

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture decisions and technical justifications.

## Installation & Setup

### Prerequisites
- Python 3.11+
- Supabase project
- Google Cloud project with Vertex AI enabled
- EmailJS account

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/leechin1/enterprise-ai-powered-sys.git
cd enterprise-ai-powered-sys
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
cp .env.example .env
# Edit .env and secrets.toml with your credentials
```

**Required environment variables:**
```toml
[gemini]
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

[gcp]
GCP_PROJECT_ID=your_project_id
GCP_LOCATION=us-central1
VERTEX_MODEL=gemini-2.5-flash

[supabase]
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SECRET_KEY=your_secret_key
SUPABASE_PUBLISHABLE_KEY=your_publishable_key

[langfuse]
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_HOST=https://cloud.langfuse.com

[emailjs]
EMAILJS_SERVICE_ID=your_service_id
EMAILJS_TEMPLATE_ID=your_template_id
EMAILJS_PUBLIC_KEY=your_public_key
EMAILJS_PRIVATE_KEY=your_private_key
```

4. Run the application:
```bash
streamlit run main.py
```

## Usage

1. Login with credentials or use an invitation token for first-time access
2. Navigate via the sidebar menu to access different modules
3. **Dashboard**: View KPIs, recent activity, and system health
4. **Analytics**: Explore sales trends, customer segments, and inventory levels
5. **Business Reporting**: Request AI analysis of business health or issues
6. **Knowledge**: Query enterprise documents or research jazz topics
7. **CRM**: Segment customers and generate marketing emails
8. **Configure**: Manage user settings and admin functions

## Deployment

**Live Application:** Streamlit Community Cloud

**Deployment Platform:** Streamlit Cloud

**Requirements:**
- Set `headless = true` in `.streamlit/config.toml`
- Configure secrets via Streamlit Cloud dashboard (Settings > Secrets)
- Ensure `requirements.txt` is complete

## Project Structure

```
enterprise-ai-powered-sys/
├── main.py                                 # Application entry point
├── requirements.txt                        # Python dependencies
├── README.md                               # This file
│
├── .streamlit/
│   ├── config.toml                         # Streamlit configuration
│   └── secrets.toml                        # Environment secrets (gitignored)
│
├── assets/
│   └── enterprise_documents/               # RAG knowledge base documents
│       ├── pdfs/                           # PDF documents for RAG
│       ├── 01_company_manifesto.md
│       ├── 02_active_personnel.md
│       ├── 03_refund_return_policy.md
│       ├── 04_employee_handbook.md
│       ├── 05_vinyl_grading_guide.md
│       ├── 06_shipping_packaging_policy.md
│       ├── 07_trade_in_consignment_policy.md
│       ├── 08_customer_privacy_policy.md
│       ├── 09_store_events_programs.md
│       ├── 10_inventory_sourcing_guide.md
│       ├── 11_customer_service_standards.md
│       ├── 12_financial_operations_guide.md
│       ├── 13_emergency_security_procedures.md
│       └── 14_online_store_operations.md
│
├── auth/
│   └── auth_service.py                     # Authentication logic
│
├── db_configure/
│   ├── migrations/                         # SQL migration files
│   │   ├── 01_core_tables.sql
│   │   ├── 02_workflow_tables.sql
│   │   ├── 03_indexes.sql
│   │   ├── 04_rls_policies.sql
│   │   ├── 05_activity_logs_table.sql
│   │   ├── 06_auth_tables.sql
│   │   ├── create_readonly_sql_function.sql
│   │   ├── create_saved_queries_table.sql
│   │   └── setup_vector_embeddings.sql
│   └── data-gen/                           # Synthetic data generation
│       ├── config.py
│       ├── db_connector.py
│       ├── pyproject.toml
│       └── prompts/                        # Data generation prompts
│           ├── album_prompt.txt
│           ├── customer_prompt.txt
│           ├── genre_prompt.txt
│           ├── label_prompt.txt
│           ├── order_item_prompt.txt
│           ├── order_prompt.txt
│           ├── payment_prompt.txt
│           ├── review_prompt.txt
│           └── workflow_prompt.txt
│
├── docs/
│   ├── ARCHITECTURE.md                     # Architecture decisions
│   └── agent_architecture.md               # AI agent design docs
│
├── frontend/
│   ├── __init__.py
│   ├── styles.py                           # Custom CSS theming
│   └── components/                         # Streamlit UI modules
│       ├── __init__.py
│       ├── activity.py                     # Activity log viewer
│       ├── admin_configure.py              # Admin configuration panel
│       ├── admin_user_management.py        # User management UI
│       ├── ai_reporting_agent.py           # AI business reporting UI
│       ├── analytics.py                    # Analytics dashboard
│       ├── authentication.py               # Login/signup UI
│       ├── dashboard.py                    # Main dashboard
│       ├── marketing_emails.py             # Email campaign UI
│       └── rag.py                          # Knowledge base chat UI
│
├── scripts/
│   ├── index_documents.py                  # Document indexing for RAG
│   └── migrate_users_to_supabase.py        # User migration utility
│
├── services/
│   ├── __init__.py
│   ├── activity_log_service.py             # Activity logging
│   ├── ai_business_consultant_agent.py     # Main business AI agent
│   ├── ai_health_agent.py                  # Health analysis agent
│   ├── ai_issues_agent.py                  # Issue detection agent
│   ├── ai_review_response_agent.py         # Review response generator
│   ├── auth_email_service.py               # Auth email notifications
│   ├── email_service.py                    # EmailJS integration
│   ├── jazz_research_service.py            # Jazz domain research
│   ├── marketing_service.py                # Marketing automation
│   ├── rag_service.py                      # RAG pipeline service
│   │
│   ├── prompts/                            # LLM prompt templates
│   │   ├── __init__.py
│   │   ├── business_consultant_fixes_prompt.txt
│   │   ├── business_consultant_health_prompt.txt
│   │   ├── business_consultant_issues_prompt.txt
│   │   ├── business_consultant_recommendations_prompt.txt
│   │   ├── health_analysis_system_prompt.txt
│   │   ├── issues_stage0_sql_generation_prompt.txt
│   │   ├── issues_stage1_analysis_prompt.txt
│   │   ├── issues_stage2_fixes_prompt.txt
│   │   ├── marketing_email_system_instructions.txt
│   │   ├── rag_chatbot_system_prompt.txt
│   │   └── review_response_system_instructions.txt
│   │
│   ├── schemas/                            # Pydantic response models
│   │   ├── ba_agent_schemas.py
│   │   ├── marketing_schemas.py
│   │   └── review_agent_schemas.py
│   │
│   ├── tools/                              # LangChain tool definitions
│   │   ├── business_agent_tools.py
│   │   ├── business_generation_tools.py
│   │   └── business_query_tools.py
│   │
│   └── tools_templates/                    # Email/report templates
│       ├── customer_email_template.txt
│       ├── inventory_alert_email_template.txt
│       ├── restock_recommendation_template.txt
│       └── transaction_cancelled_template.txt
│
└── utils/
    ├── __init__.py
    ├── database_schema.py                  # Schema documentation for LLMs
    └── db_analytics.py                     # Analytics query layer
```

## Team

- Carolina Lee Chin 
- Cícero Dias dos Santos
- Luís Soeiro
- Ishak Soltani

## Brave License

MIT License

Copyright (c) 2025 bravedatum

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
