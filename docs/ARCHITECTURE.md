# Architecture Documentation

## System Overview

Misty AI Enterprise System is a Streamlit-based platform providing AI-powered business automation for jazz vinyl retail operations. The system implements a three-tier architecture: presentation layer (Streamlit components), service layer (AI agents and business logic), and data layer (Supabase PostgreSQL).

## Directory Structure

```
enterprise-ai-powered-sys/
├── main.py                     # Application entry point
├── frontend/
│   ├── components/             # UI modules (dashboard, analytics, rag, etc.)
│   └── styles.py               # CSS theming
├── services/
│   ├── prompts/                # LLM prompt templates
│   ├── schemas/                # Pydantic response validation
│   ├── tools/                  # LangChain tool definitions
│   ├── *_service.py            # Service implementations
│   └── *_agent.py              # AI agent implementations
├── auth/
│   └── auth_service.py         # Authentication logic
├── utils/
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

**Decision**: Use Supabase (hosted PostgreSQL) for database, authentication infrastructure, and real-time subscriptions.

**Rationale**: Eliminates backend infrastructure management. Built-in row-level security (RLS) policies provide fine-grained access control without custom middleware. Native Python SDK reduces integration complexity. Managed vector search capability supports RAG implementation.

**Trade-offs**: Vendor lock-in to Supabase. Mitigated by standard PostgreSQL compatibility for potential migration.

### 3. LangChain Agent Architecture

**Decision**: Implement AI capabilities as LangChain agents with defined tool sets.

**Rationale**: LangChain provides a standardized abstraction for LLM orchestration, tool binding, and conversation memory. Separating tools into query (read-only) and generation (write) categories enforces clear boundaries. Agent architecture supports complex multi-step reasoning without custom state management.

**Trade-offs**: LangChain adds abstraction overhead. Justified by reduced development time and maintainability for multi-agent workflows.

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

## Component Architecture

### Presentation Layer

| Component | Responsibility |
|-----------|----------------|
| `dashboard.py` | KPI display, recent activity feed |
| `analytics.py` | Sales, customer, inventory visualizations |
| `rag.py` | Document retrieval chat, jazz research |
| `marketing_emails.py` | Customer segmentation, email generation |
| `ai_reporting_agent.py` | Business health analysis, issue detection |
| `activity.py` | Activity log visualization |
| `admin_configure.py` | User management, settings |

### Service Layer

| Service | Function | External Dependencies |
|---------|----------|----------------------|
| `rag_service.py` | Document chunking, embedding, retrieval | Vertex AI Embeddings, Supabase Vector |
| `jazz_research_service.py` | Domain expertise via search | GenAI with Google Search |
| `marketing_service.py` | Segmentation, email drafting | Vertex AI GenerativeModel |
| `ai_health_agent.py` | Business metrics analysis | LangChain, Vertex AI |
| `ai_issues_agent.py` | Problem identification | LangChain, Vertex AI |
| `email_service.py` | Email dispatch | EmailJS API |
| `activity_log_service.py` | Activity persistence | Supabase |

### Data Layer

| Table Category | Tables |
|----------------|--------|
| Core Business | customers, albums, genres, labels, inventory, orders, order_items, payments, sales, reviews |
| Authentication | users, verification_tokens |
| Operations | activity_logs |

## Data Flow

### Authentication

```
Login Form -> check_usr_pass() -> Supabase users lookup
           -> Argon2 verification -> Cookie creation -> Session state
```

### Analytics Query

```
Component -> AnalyticsConnector -> Supabase REST API
          -> DataFrame transformation -> Plotly visualization
```

### AI Agent Execution

```
User Input -> LangChain Agent -> Tool Selection
           -> business_query_tools.py (data retrieval)
           -> Gemini inference -> Pydantic validation -> Response
```

### RAG Pipeline

```
Query -> text-embedding-004 -> Supabase vector search
      -> Context assembly -> Gemini completion -> Response
```

## Security Model

| Layer | Mechanism |
|-------|-----------|
| Password Storage | Argon2id hashing |
| Session Management | AES-encrypted cookies |
| Token Verification | SHA-256 hashed tokens with expiry |
| Database Access | Row-level security policies |
| Secrets Management | Streamlit secrets (production), .env (development) |

## Deployment Configuration

**Streamlit Cloud Requirements**:
- `headless = true` in `.streamlit/config.toml`
- Port 8501 (default)
- Secrets configured via Streamlit Cloud dashboard
- `requirements.txt` for dependency resolution

## External Service Dependencies

| Service | Purpose | Failure Mode |
|---------|---------|--------------|
| Supabase | Database, auth | Application unavailable |
| Vertex AI | LLM inference | AI features degraded |
| EmailJS | Email dispatch | Email features unavailable |
| Langfuse | Observability | Monitoring only, no user impact |

## Scalability Considerations

- **Stateless Design**: Streamlit session state is per-user; horizontal scaling supported via Streamlit Cloud
- **Database**: Supabase managed scaling; connection pooling handled by SDK
- **LLM Calls**: Vertex AI rate limits apply; implement retry logic in production
- **Embedding Storage**: Supabase pgvector scales with database tier

## Development Modes

**Placebo Mode**: EmailJS redirects all emails to `PLACEBO_EMAIL` when `PLACEBO_MODE=true`. Original recipient preserved in subject line for testing verification.

## Future Considerations

- Implement caching layer (Redis) for analytics queries
- Add webhook support for real-time Supabase events
- Consider async agent execution for long-running analyses
- Evaluate migration to dedicated vector database if RAG corpus exceeds current tier limits
