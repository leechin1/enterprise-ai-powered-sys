# Architecture Documentation

## System Overview

Misty AI Enterprise System is a Streamlit-based platform providing AI-powered business automation for jazz vinyl retail operations. The system implements a three-tier architecture: presentation layer (Streamlit components), service layer (AI agents and business logic), and data layer (Supabase PostgreSQL).

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │  Dashboard  │ │  Analytics  │ │  Business   │ │      Knowledge          ││
│  │   (KPIs)    │ │  (Charts)   │ │  Reporting  │ │   (RAG + Jazz)          ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────────┘│
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │  Marketing  │ │  Activity   │ │    Auth     │ │    Admin Config         ││
│  │    & CRM    │ │    Logs     │ │   (Login)   │ │  (User Management)      ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SERVICE LAYER                                    │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         AI AGENTS (6)                                  │ │
│  │  Business Consultant │ Issues Agent │ Conversational │ Health Agent   │ │
│  │  Review Response     │ Jazz Research                                   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      CORE SERVICES (6)                                 │ │
│  │  RAG │ Marketing │ Email │ Auth Email │ Activity Log │ Config         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    FUNCTION TOOLS (26)                                 │ │
│  │  Query Tools (11) │ Generation Tools (4) │ Issues Tools (11)          │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             DATA LAYER                                      │
│  ┌──────────────────────┐ ┌──────────────────┐ ┌──────────────────────────┐│
│  │  Supabase PostgreSQL │ │  pgvector for    │ │  Supabase Storage        ││
│  │  (10 Core Tables)    │ │  RAG Embeddings  │ │  (Document Bucket)       ││
│  └──────────────────────┘ └──────────────────┘ └──────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
enterprise-ai-powered-sys/
├── main.py                     # Application entry point
├── frontend/
│   ├── components/             # UI modules (dashboard, analytics, rag, etc.)
│   └── styles.py               # CSS theming
├── services/
│   ├── config.py               # Centralized configuration
│   ├── prompts/                # LLM prompt templates (general agents)
│   ├── schemas/                # Pydantic response validation
│   ├── tools/                  # LangChain tool definitions (26 tools)
│   │   ├── __init__.py         # Package exports
│   │   ├── base.py             # BaseBusinessTools class
│   │   ├── query_tools.py      # Read-only query tools (11 tools)
│   │   ├── generation_tools.py # Content generation tools (4 tools)
│   │   ├── issues_query_tools.py    # SQL generation & execution (2 tools)
│   │   ├── issues_analysis_tools.py # Issue identification (4 tools)
│   │   ├── issues_fix_tools.py      # Fix proposals & emails (4 tools)
│   │   ├── issues_utility_tools.py  # State utilities (2 tools)
│   │   ├── issues_state.py          # Shared agentic state
│   │   └── prompts/                 # Issues agent prompts
│   │       ├── issues_stage0_sql_generation_prompt.txt
│   │       ├── issues_stage1_analysis_prompt.txt
│   │       └── issues_stage2_fixes_prompt.txt
│   ├── tools_templates/        # Email/report templates (8 templates)
│   │   ├── management_notification_template.txt
│   │   ├── supplier_notification_template.txt
│   │   ├── customer_notification_template.txt
│   │   ├── team_notification_template.txt
│   │   └── ... (4 more templates)
│   ├── *_service.py            # Service implementations
│   └── *_agent.py              # AI agent implementations
├── auth/
│   └── auth_service.py         # Authentication logic
├── utils/
│   ├── clients.py              # ClientManager singleton for DB connections
│   ├── db_analytics.py         # Analytics query layer
│   └── database_schema.py      # Schema documentation for LLMs
├── db_configure/
│   ├── migrations/             # SQL migration files
│   └── data-gen/               # Test data generation
├── assets/
│   └── enterprise_documents/   # RAG knowledge base
└── .streamlit/
    ├── config.toml             # Streamlit configuration
    └── secrets.toml            # Environment secrets
```

## Architectural Decisions

### 1. Streamlit as Application Framework

**Decision**: Use Streamlit rather than a traditional frontend/backend separation.

**Rationale**: Streamlit provides rapid prototyping with minimal frontend code while maintaining sufficient interactivity for enterprise dashboards. The target user base (internal operations staff) does not require complex client-side interactions. Server-side rendering simplifies deployment and eliminates API versioning concerns.

**Trade-offs**: Limited customization compared to React/Vue applications. Acceptable given the internal tooling use case.

### 2. Supabase as Backend-as-a-Service

**Decision**: Use Supabase (hosted PostgreSQL) for database, authentication infrastructure, storage, and real-time subscriptions.

**Rationale**: Eliminates backend infrastructure management. Built-in row-level security (RLS) policies provide fine-grained access control without custom middleware. Native Python SDK reduces integration complexity. Managed vector search capability supports RAG implementation. Storage buckets provide document hosting with public URLs.

**Trade-offs**: Vendor lock-in to Supabase. Mitigated by standard PostgreSQL compatibility for potential migration.

### 3. LangChain Agent Architecture

**Decision**: Implement AI capabilities as LangChain agents with defined tool sets.

**Rationale**: LangChain provides a standardized abstraction for LLM orchestration, tool binding, and conversation memory. Separating tools into query (read-only) and generation (write) categories enforces clear boundaries. Agent architecture supports complex multi-step reasoning without custom state management.

**Trade-offs**: LangChain adds abstraction overhead. Justified by reduced development time and maintainability for multi-agent workflows.

### 3.1 Centralized Client Management

**Decision**: Use singleton pattern (`ClientManager`) for database connections shared across all tools.

**Rationale**: Eliminates redundant connection initialization. Each tool class was previously creating its own Supabase client and AnalyticsConnector instance. Centralized management reduces memory footprint, ensures consistent connection configuration, and simplifies testing via `ClientManager.reset()`.

**Implementation**:
```python
from utils.clients import ClientManager

class BaseBusinessTools:
    def __init__(self):
        self.analytics = ClientManager.get_analytics()
        self.supabase = ClientManager.get_supabase()
```

### 3.2 Tool Class Inheritance

**Decision**: All tool classes inherit from `BaseBusinessTools` which handles client initialization.

**Rationale**: DRY principle - shared initialization code lives in one place. `BusinessQueryTools` (11 read-only methods) and `BusinessGenerationTools` (4 write methods) both inherit common setup. Clean import path: `from services.tools import scan_business_metrics`.

**Trade-offs**: Slight indirection. Justified by 60% code reduction in tools layer.

### 3.3 Issues Agent Agentic Architecture

**Decision**: Implement a separate agentic workflow for issue detection using LangGraph's ReAct pattern.

**Rationale**: Issue detection requires multi-step reasoning:
1. Generate SQL queries based on business focus areas
2. Execute queries and collect results
3. Analyze results to identify issues
4. Propose fixes with automated actions
5. Generate and send notification emails

LangGraph provides state management and tool orchestration for this complex workflow.

**Components**:
- `IssuesAgentState`: Shared state singleton across tool invocations
- `issues_query_tools.py`: SQL generation and execution (2 tools)
- `issues_analysis_tools.py`: Issue identification logic (4 tools)
- `issues_fix_tools.py`: Fix proposals and email composition (4 tools)
- `issues_utility_tools.py`: State reset and utilities (2 tools)
- `tools/prompts/`: Issues-specific prompt templates

### 3.4 Domain-Focused Analysis

**Decision**: Implement domain filtering for focused business analysis.

**Rationale**: Users often want to investigate specific business areas (inventory, payments, customers, revenue) rather than running comprehensive analysis. Domain filtering ensures:
- SQL queries are generated only for the requested domain
- Issue identification is limited to the focused area
- Reports are concise and actionable

**Implementation**:
- Focus area detection from user intent
- Domain-specific SQL generation (3-5 queries vs 5-10 for full analysis)
- Category filtering in issue analysis
- Configurable thresholds per domain

### 3.5 Template-Based Email System

**Decision**: Use file-based templates from `tools_templates/` for all email generation.

**Rationale**: Email templates should be:
- Easily editable without code changes
- Consistent across the application
- Testable independently of business logic

**Implementation**:
```python
# In issues_fix_tools.py
TEMPLATES_DIR = Path(__file__).parent.parent / "tools_templates"

def _load_template(template_name: str) -> str:
    filepath = TEMPLATES_DIR / template_name
    return filepath.read_text() if filepath.exists() else None
```

**Template Types**:
- Management notifications (business alerts)
- Supplier notifications (inventory issues)
- Customer notifications (order/service updates)
- Team notifications (internal alerts)
- Inventory alerts, restock recommendations, transaction records

### 4. Google Vertex AI / Gemini Models

**Decision**: Use Gemini 2.5-flash as the primary LLM backend.

**Rationale**: Cost-effective for high-volume inference. Sufficient capability for business analysis, email generation, and document retrieval tasks. Google Cloud integration simplifies enterprise compliance requirements.

**Trade-offs**: Model vendor dependency. Abstracted via LangChain to enable model swapping if required.

### 5. Custom Authentication over Supabase Auth

**Decision**: Implement custom authentication layer (`auth_service.py`) using Supabase tables rather than Supabase Auth.

**Rationale**: Enables token-based user invitation workflows specific to enterprise onboarding. Provides granular control over user states (admin, active, deactivated). Allows custom password policies and audit logging.

**Trade-offs**: Requires manual security implementation. Mitigated by using Argon2 password hashing and encrypted cookie management.

### 6. Environment-Based Configuration

**Decision**: All secrets and configuration injected via Streamlit secrets (production) or `.env` (development).

**Rationale**: Secrets remain outside version control. Streamlit Cloud secrets integration provides secure deployment. Environment variable injection at startup allows existing `os.getenv()` patterns throughout codebase.

### 7. Observability via Langfuse/LangSmith

**Decision**: Integrate both Langfuse and LangSmith for LLM tracing.

**Rationale**: Langfuse provides cost tracking and production monitoring. LangSmith enables development-time debugging and prompt iteration. Dual integration provides flexibility during evaluation phase.

### 8. RAG with PDF Support

**Decision**: Extend RAG pipeline to support PDF documents alongside Markdown and text files.

**Rationale**: Enterprise documents often exist as PDFs. Supporting multiple formats increases knowledge base coverage without requiring document conversion.

**Implementation**:
- PyMuPDF (`fitz`) for PDF text extraction
- Automatic file type detection in `index_document()`
- Graceful fallback if PyMuPDF not installed
- Support in both single-document and batch indexing

```python
# In rag_service.py
def _extract_pdf_text(self, pdf_path: str) -> str:
    text_parts = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n\n".join(text_parts)
```

### 9. External Email Routing

**Decision**: Route all external emails to a single configurable address (`hi@mistyrecords.com`).

**Rationale**: AI agents may generate fabricated email addresses for customers or suppliers. Routing all external communications to a known address prevents emails to non-existent addresses while preserving the intended recipient in the subject line for tracking.

**Implementation**:
```python
# In services/config.py
class EmailConfig:
    DEFAULT_EXTERNAL_EMAIL: str = 'hi@mistyrecords.com'

# In email_service.py
if self.placebo_mode:
    actual_to_email = self.placebo_email
    actual_subject = f"[PLACEBO: {to_email}] {subject}"
else:
    actual_to_email = self.default_external_email
    actual_subject = f"[To: {to_email}] {subject}"
```

### 10. Supabase Storage for Documents

**Decision**: Use Supabase Storage buckets for document file storage alongside local filesystem.

**Rationale**: Enables document viewing via public URLs. Users can click to view documents in a new browser tab. Provides cloud backup for knowledge base documents.

**Implementation**:
- `enterprise-documents` bucket in Supabase Storage
- Public URL generation for document viewing
- Automatic upload on document indexing
- Support for PDF, Markdown, and text files

## Component Architecture

### Presentation Layer

| Component | File | Responsibility |
|-----------|------|----------------|
| Dashboard | `dashboard.py` | KPI display, recent activity feed |
| Analytics | `analytics.py` | Sales, customer, inventory visualizations |
| Knowledge | `rag.py` | Document retrieval chat, jazz research, document management |
| Marketing | `marketing_emails.py` | Customer segmentation, email generation, review responses |
| Business Reporting | `ai_reporting_agent.py` | Business health analysis, issue detection |
| Activity | `activity.py` | Activity log visualization |
| Auth | `authentication.py` | Login, signup, password reset |
| Admin | `admin_configure.py` | User management, settings |

### Service Layer

| Service | File | Function | External Dependencies |
|---------|------|----------|----------------------|
| RAG Service | `rag_service.py` | Document chunking, embedding, retrieval, PDF extraction | Vertex AI Embeddings, Supabase Vector, Storage |
| Jazz Research | `jazz_research_service.py` | Domain expertise via search | GenAI with Google Search |
| Marketing | `marketing_service.py` | Segmentation, email drafting | Vertex AI GenerativeModel |
| Health Agent | `ai_health_agent.py` | Business metrics analysis | LangChain, Vertex AI |
| Issues Agent | `ai_issues_agent.py` | Problem identification | LangChain, Vertex AI |
| Conversational Agent | `ai_conversational_issues_agent.py` | Multi-turn dialogue | LangGraph, Vertex AI |
| Email Service | `email_service.py` | Email dispatch with routing | EmailJS API |
| Activity Log | `activity_log_service.py` | Activity persistence | Supabase |
| Config | `config.py` | Centralized configuration | Environment variables |

### Tools Layer

| Module | Function | Tool Count |
|--------|----------|------------|
| `tools/query_tools.py` | Read-only analytics (metrics, top products, payments) | 11 |
| `tools/generation_tools.py` | Content generation (emails, recommendations, actions) | 4 |
| `tools/issues_query_tools.py` | SQL generation and execution | 2 |
| `tools/issues_analysis_tools.py` | Issue identification, details, search | 4 |
| `tools/issues_fix_tools.py` | Fix proposals, email generation, sending | 4 |
| `tools/issues_utility_tools.py` | State management | 2 |
| `tools/base.py` | Shared initialization via ClientManager | - |
| `tools/prompts/` | Issues agent prompt templates | - |
| `tools_templates/` | Email and report templates | 8 |
| `utils/clients.py` | Singleton Supabase/Analytics connections | - |

### Data Layer

| Table Category | Tables |
|----------------|--------|
| Core Business | customers, albums, genres, labels, inventory, orders, order_items, payments, sales, reviews |
| Authentication | users, verification_tokens |
| Operations | activity_logs |
| RAG | document_embeddings |

## Data Flow

### Authentication

```
Login Form → check_usr_pass() → Supabase users lookup
           → Argon2 verification → Cookie creation → Session state
```

### Analytics Query

```
Component → AnalyticsConnector → Supabase REST API
          → DataFrame transformation → Plotly visualization
```

### AI Agent Execution

```
User Input → LangChain Agent → Tool Selection
           → services.tools (query_tools / generation_tools)
           → ClientManager.get_supabase() (singleton connection)
           → Gemini inference → Pydantic validation → Response
```

### Issues Agent Workflow

```
User Request → Conversational Agent (LangGraph ReAct)
             → generate_business_queries() → SQL generation
             → execute_business_queries() → Database execution
             → analyze_issues_from_results() → Issue identification
             → propose_fix_for_issue() → Fix proposal + emails
             → edit_email() / send_fix_emails() → Email dispatch
```

### RAG Pipeline

```
Query → text-embedding-004 → Supabase vector search
      → Context assembly → Gemini completion → Response
```

### Document Upload Flow

```
File Upload → Supabase Storage Bucket → Public URL generation
            → Local filesystem save → PDF/Text extraction
            → Chunking → Embedding generation → Supabase vector store
```

### Email Dispatch Flow (Safety-Critical)

**The agent can NEVER send emails to arbitrary addresses.** All emails are intercepted and routed to a safe destination:

```
Agent displays: hi@mistyrecords.com (hardcoded)
         │
         ▼
EmailService.send_email() intercepts
         │
         ▼
Actual delivery → carolinaleedev@gmail.com
                  Subject: [To: hi@mistyrecords.com] Original Subject
```

**Current Configuration:**
- `PLACEBO_MODE = false` (production mode)
- `DEFAULT_EXTERNAL_EMAIL = carolinaleedev@gmail.com`
- Agent always displays `hi@mistyrecords.com` to users
- All emails actually delivered to `carolinaleedev@gmail.com`

The displayed recipient (hi@mistyrecords.com) is preserved in the email subject for tracking.

## Security Model

| Layer | Mechanism |
|-------|-----------|
| Password Storage | Argon2id hashing |
| Session Management | AES-encrypted cookies |
| Token Verification | SHA-256 hashed tokens with expiry |
| Database Access | Row-level security policies |
| Secrets Management | Streamlit secrets (production), .env (development) |
| **Email Safety** | **All emails routed to single safe address (never arbitrary recipients)** |

## Configuration Management

All configuration is centralized in `services/config.py`:

| Class | Purpose |
|-------|---------|
| `GCPConfig` | Google Cloud project settings |
| `ModelConfig` | LLM temperatures and generation parameters |
| `RAGConfig` | Embedding model, chunk size, match thresholds |
| `ReviewResponseConfig` | Sentiment thresholds and retry settings |
| `EmailConfig` | EmailJS credentials, placebo mode, external routing |
| `ActivityLogConfig` | Logging retention settings |
| `MarketingConfig` | Customer query limits |
| `ValidationConfig` | SQL validation, valid email types, severities |

## Deployment Configuration

**Streamlit Cloud Requirements**:
- `headless = true` in `.streamlit/config.toml`
- Port 8501 (default)
- Secrets configured via Streamlit Cloud dashboard
- `requirements.txt` for dependency resolution

**Production Settings**:
- `PLACEBO_MODE=false` for real email delivery
- `DEFAULT_EXTERNAL_EMAIL` for email routing
- Proper GCP service account permissions
- Supabase RLS policies enabled

## External Service Dependencies

| Service | Purpose | Failure Mode |
|---------|---------|--------------|
| Supabase | Database, auth, storage | Application unavailable |
| Vertex AI | LLM inference | AI features degraded |
| EmailJS | Email dispatch | Email features unavailable |
| Langfuse | Observability | Monitoring only, no user impact |

## Scalability Considerations

- **Stateless Design**: Streamlit session state is per-user; horizontal scaling supported via Streamlit Cloud
- **Database**: Supabase managed scaling; connection pooling handled by SDK
- **Connection Management**: `ClientManager` singleton ensures single Supabase connection per process, reducing connection overhead
- **LLM Calls**: Vertex AI rate limits apply; implement retry logic in production
- **Embedding Storage**: Supabase pgvector scales with database tier

## Development Modes

**Placebo Mode**: EmailJS redirects all emails to `PLACEBO_EMAIL` when `PLACEBO_MODE=true`. Original recipient preserved in subject line for testing verification.

**Production Mode**: All external emails route to `DEFAULT_EXTERNAL_EMAIL` (configurable). Intended recipient included in subject for tracking.

## Future Considerations

- Implement caching layer (Redis) for analytics queries
- Add webhook support for real-time Supabase events
- Consider async agent execution for long-running analyses
- Evaluate migration to dedicated vector database if RAG corpus exceeds current tier limits
- Add support for additional document formats (DOCX, HTML)
