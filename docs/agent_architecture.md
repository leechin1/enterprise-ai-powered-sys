# AI Business Consultant Agent Architecture (Refactored with LangChain)

## Overview

The AI Business Consultant has been **refactored** to use **LangChain agent architecture** with **Gemini 2.5-flash** as the LLM. This new architecture provides intelligent reasoning, autonomous tool selection, and structured analysis with strict token limits.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend UI                              │
│                  (ai_reporting_agent.py)                         │
│                                                                   │
│  ┌───────────────────┐         ┌───────────────────┐            │
│  │ Business Health   │         │  Issues &         │            │
│  │    Analysis       │         │  Problems         │            │
│  └─────────┬─────────┘         └─────────┬─────────┘            │
└────────────┼───────────────────────────────┼──────────────────────┘
             │                               │
             ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              AI Business Consultant Agent                        │
│          (ai_business_consultant_agent.py)                       │
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Health Agent   │  │  Issues Agent   │  │  Recommendations│ │
│  │  (6 insights)   │  │  (7 issues)     │  │     Agent       │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                     │           │
│           └────────────────────┼─────────────────────┘           │
│                                │                                 │
│                    ┌───────────▼──────────┐                      │
│                    │   Gemini 2.5-flash   │                      │
│                    │   (LangChain LLM)    │                      │
│                    └───────────┬──────────┘                      │
│                                │                                 │
│                    ┌───────────▼──────────┐                      │
│                    │   Business Tools     │                      │
│                    │  (11 specialized     │                      │
│                    │      tools)          │                      │
│                    └───────────┬──────────┘                      │
└────────────────────────────────┼──────────────────────────────────┘
                                 │
                    ┌────────────▼──────────┐
                    │   Supabase Database   │
                    │   (via Analytics &    │
                    │    Connector)         │
                    └───────────────────────┘
```

## Core Pattern: ReAct (Reasoning + Acting)

The system uses LangGraph's `create_react_agent` implementing the ReAct pattern:

```
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│  THINK   │ ───> │  ACTION  │ ───> │ OBSERVE  │ ───> │  REPEAT  │
│          │      │          │      │          │      │          │
│ Reason   │      │ Use Tool │      │ Get      │      │ Until    │
│ about    │      │          │      │ Result   │      │ Complete │
│ problem  │      │          │      │          │      │          │
└──────────┘      └──────────┘      └──────────┘      └──────────┘
```

**Example Agent Flow:**
```
User: "Analyze business health"
  ↓
Agent Thought: "I need to scan business metrics first"
  ↓
Agent Action: scan_business_metrics()
  ↓
Agent Observation: "Revenue: $X, Customers: Y, ..."
  ↓
Agent Thought: "I should also check top products"
  ↓
Agent Action: get_top_performing_products()
  ↓
Agent Observation: "1. Album A - $X revenue..."
  ↓
Agent Thought: "I have enough data, generating 6 insights"
  ↓
Agent Output: JSON with 6 structured insights
```

## Components

### 1. Frontend UI (`frontend/components/ai_reporting_agent.py`)

**Purpose:** Streamlit interface for user interaction

**Features:**
- Simplified analysis selection (2 options only):
  - **Overall Business Health** (6 insights + recommendations)
  - **Issues & Problems** (7 issues + suggested fixes)
- Concise box-based UI for displaying insights
- Progressive disclosure with action buttons
- Session state management for multi-step flows

**User Flow:**

```
1. Select Analysis Focus → 2. Generate Analysis → 3. View Results
                                                        ↓
                                     ┌──────────────────┴───────────────────┐
                                     ▼                                      ▼
                          Business Health Path                    Issues Path
                                     ↓                                      ↓
                     Click "Business Recommendations"         Click "Suggested Fixes"
                                     ↓                                      ↓
                          View Recommendations              View Automated Solutions
                                                                            ↓
                                                          Click "Accept and Take Action"
                                                                            ↓
                                                                Success Message (Placebo)
```

### 2. AI Business Consultant Agent (`services/ai_business_consultant_agent.py`)

**Purpose:** LangChain-based intelligent agent using Gemini 2.5-flash

**Key Methods:**

#### `analyze_business_health() -> Dict`
- Generates exactly **6 key insights**
- Uses `health_agent` (LangChain ReAct agent)
- Scans all business metrics via tools
- Returns structured JSON with insights

**Output Format:**
```json
{
  "success": true,
  "type": "health_analysis",
  "data": {
    "insights": [
      {
        "title": "Revenue Growth Strong",
        "content": "Total revenue of $X with Y% growth...",
        "priority": "high|medium|low",
        "metric_type": "financial|customer|inventory|product"
      }
    ]
  },
  "model": "gemini-2.0-flash-exp"
}
```

#### `analyze_business_issues() -> Dict`
- Identifies exactly **7 critical issues**
- Uses `issues_agent` (LangChain ReAct agent)
- Scans for problems in payments, inventory, customers, financials
- Returns structured JSON with issues

**Output Format:**
```json
{
  "success": true,
  "type": "issues_analysis",
  "data": {
    "issues": [
      {
        "title": "Failed Payment Transactions",
        "description": "15 payments have failed requiring attention...",
        "impact": "high|medium|low",
        "category": "payment|inventory|customer|financial",
        "affected_count": "15 transactions"
      }
    ]
  }
}
```

#### `generate_recommendations(health_analysis) -> Dict`
- Generates 5-7 strategic recommendations
- Based on health analysis insights
- Uses `recommendations_agent`
- Returns actionable business strategies

#### `generate_fixes(issues_analysis) -> Dict`
- Generates specific fixes for each issue
- Recommends which tools to use
- Uses `fixes_agent`
- Includes automation level (full/partial/manual)

#### `execute_fix_action(fix_data) -> Dict`
- **Placebo function** - simulates action execution
- Returns success message for demo purposes
- Future: Will execute real actions (emails, cancellations, etc.)

### 3. Business Tools (`services/business_agent_tools.py`)

**Purpose:** Provide the agent with tools to interact with the database and perform actions

**Available Tools (11 total):**

#### Data Retrieval Tools
1. **`scan_business_metrics()`** - Comprehensive business metrics summary
   - Financial: revenue, orders, AOV
   - Customers: count, ratings, reviews
   - Inventory: stock levels, value, low stock count
   - Payments: completed, pending, failed

2. **`get_top_performing_products(limit=5)`** - Top-selling albums with revenue

3. **`get_top_customers(limit=5)`** - Top customers by total spending

4. **`get_low_stock_items(threshold=10)`** - Albums with low inventory

5. **`get_failed_payments()`** - Failed payment transactions needing attention

6. **`get_pending_payments()`** - Pending payment transactions

7. **`get_genre_performance()`** - Sales performance by music genre

#### Action Tools
8. **`generate_customer_email(customer_id, email_type, context)`**
   - Email template generation for customers
   - Types: low_stock_notification, thank_you, promotion

9. **`generate_inventory_alert_email(album_ids)`**
   - Inventory alert emails for restock team
   - Lists low-stock items with quantities

10. **`cancel_transaction(payment_id, reason)`**
    - Cancel failed/pending payment transactions
    - Updates payment status to 'cancelled'

11. **`recommend_restock_quantity(album_id)`**
    - Restock recommendations based on sales history
    - Calculates optimal order quantity

**Tool Design:**
- Each tool is a standalone function
- Returns formatted strings for LLM consumption
- Handles errors gracefully with try/except
- Uses `AnalyticsConnector` and Supabase client

## Token Management & Limits

### Strict Limits Enforced

**Overall Business Health:**
- Exactly **6 insights** (no more, no less)
- Enforced in system prompt
- Concise content (2-3 sentences per insight)
- Structured JSON output

**Issues & Problems:**
- Exactly **7 issues** (no more, no less)
- Enforced in system prompt
- Brief descriptions (2-3 sentences per issue)
- Structured JSON output

**Why These Limits?**
1. **UI Design:** Fits perfectly in 2-column box layout
2. **Token Efficiency:** Reduces API costs significantly
3. **User Experience:** Digestible, actionable information
4. **Consistency:** Predictable response structure
5. **Focus:** Forces agent to prioritize most critical items

## System Prompts

Each agent has a specialized system prompt that defines its behavior:

### Health Agent Prompt
```
You are an expert business consultant for Misty Jazz Records.

STRICT REQUIREMENTS:
- Generate EXACTLY 6 key insights (no more, no less)
- Each insight must be concise (2-3 sentences max)
- Focus on the most critical business metrics
- Identify both strengths and areas of concern
- Be specific with numbers and percentages

Use available tools to scan business data.
```

### Issues Agent Prompt
```
You are an expert business consultant identifying critical issues.

STRICT REQUIREMENTS:
- Identify EXACTLY 7 critical issues (no more, no less)
- Each issue must be actionable and specific
- Prioritize by business impact
- Consider: failed payments, low inventory, customer satisfaction
- Focus on problems solvable with available tools
```

### Recommendations Agent Prompt
```
Generate strategic recommendations based on health analysis.

REQUIREMENTS:
- Generate 5-7 strategic recommendations
- Specific and actionable
- Include expected impact and difficulty
- Prioritize by potential business value
```

### Fixes Agent Prompt
```
Recommend specific fixes for identified issues.

REQUIREMENTS:
- Provide specific, actionable fixes
- Suggest which tools to use
- Step-by-step actions
- Realistic automation vs manual work
```

## Database Integration

### Analytics Connector (`utils/db_analytics.py`)
High-level analytics queries used by tools:
- `get_total_revenue()`
- `get_top_customers(limit)`
- `get_low_stock_albums(threshold)`
- `get_genre_performance()`
- etc.

### Direct Supabase Access
For action tools, direct Supabase client is used:
- Payment cancellations
- Email generation (fetching customer/album data)
- Inventory lookups

## Traceability & Observability

### LangSmith Integration
All agent invocations traced with `@traceable`:
- Tool calls and selections
- Agent reasoning steps
- Execution time
- Errors and retries

### Langfuse Integration
All methods decorated with `@observe`:
- Business metrics gathering
- Report generation
- Recommendation creation

**Dashboard Access:**
- **LangSmith:** Track agent reasoning and tool usage
- **Langfuse:** Monitor performance and costs

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

**New Dependencies Added:**
- `langchain-google-genai>=2.0.0` - LangChain integration for Gemini
- `langgraph>=0.2.0` - Agent creation and orchestration
- `langfuse>=2.0.0` - Observability and tracing

### 2. Environment Variables
```bash
# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_SECRET_KEY=your_supabase_service_key

# LangSmith (optional)
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true

# Langfuse
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 3. Run Application
```bash
streamlit run frontend/app.py
```

## Usage Example

```python
from services.ai_business_consultant_agent import AIBusinessConsultantAgent

# Initialize agent
agent = AIBusinessConsultantAgent()

# Analyze business health (6 insights)
health_result = agent.analyze_business_health()
print(health_result["data"]["insights"])

# Get recommendations (5-7 recommendations)
recommendations = agent.generate_recommendations(health_result)
print(recommendations["data"]["recommendations"])

# Analyze issues (7 issues)
issues_result = agent.analyze_business_issues()
print(issues_result["data"]["issues"])

# Get fixes (specific solutions)
fixes = agent.generate_fixes(issues_result)
print(fixes["data"]["fixes"])

# Execute fix (placebo - simulates action)
success = agent.execute_fix_action(fixes["data"]["fixes"][0])
print(success["message"])  # "Successfully executed fix: ..."
```

## Key Improvements Over Previous Architecture

### Before (Old System - Deprecated)
- ❌ Manual prompt building
- ❌ No tool usage or reasoning
- ❌ Fixed, unstructured report format
- ❌ Limited actionability
- ❌ No multi-step workflows
- ❌ Verbose, token-heavy outputs
- ❌ Single-shot analysis only

### After (New Agent System - Current)
- ✅ LangChain ReAct agent with autonomous tool selection
- ✅ Intelligent reasoning about which data to fetch
- ✅ Structured JSON outputs for UI rendering
- ✅ 11 action tools for automated fixes
- ✅ Multi-step flows (analysis → recommendations → fixes)
- ✅ Token-optimized responses (6 insights, 7 issues max)
- ✅ Full traceability with LangSmith + Langfuse
- ✅ Progressive disclosure UI pattern
- ✅ Action simulation (placebo) ready for real implementation

## Future Enhancements

### 1. Real Action Execution
- Actually send emails via SMTP/SendGrid
- Execute transaction cancellations in production
- Automated restock order placement via supplier APIs

### 2. More Sophisticated Tools
- Customer segmentation analysis
- Predictive inventory forecasting with ML
- Revenue projection models
- Churn prediction and prevention

### 3. Memory & Context
- Remember previous analyses
- Track recommendation implementation over time
- Follow-up on suggested fixes
- Trend analysis across multiple reports

### 4. Advanced Agent Capabilities
- Multi-agent collaboration (finance agent + inventory agent)
- Specialized sub-agents per business domain
- Human-in-the-loop for critical decisions
- Self-reflection and iterative improvement

### 5. Integration Expansions
- Slack/Teams notifications
- Scheduled automated reports
- Webhook triggers for critical issues
- API endpoints for external access

## Troubleshooting

### Agent not using tools
**Symptoms:** Agent generates generic response without calling tools

**Solutions:**
- Check system prompts explicitly mention tool usage
- Verify tools are registered with `create_react_agent`
- Review LangSmith traces for reasoning steps
- Ensure LLM has tool-calling capabilities enabled

### JSON parsing errors
**Symptoms:** `KeyError` or malformed response data

**Solutions:**
- Agent response may include markdown code blocks
- Regex extraction is used as fallback
- Check LLM temperature (too high = inconsistent formats)
- Review system prompt for JSON format examples

### Exceeding token limits
**Symptoms:** More than 6 insights or 7 issues generated

**Solutions:**
- System prompts enforce strict limits
- If exceeded, strengthen prompt language ("EXACTLY", "NO MORE")
- Consider adding max_tokens in generation config
- Review LangSmith traces for prompt compliance

### Tool execution errors
**Symptoms:** Tools fail with database or connection errors

**Solutions:**
- Check Supabase connection and credentials
- Verify AnalyticsConnector is properly initialized
- Review tool error handling (should return error strings)
- Check database schema matches tool queries

## File Structure

```
enterprise-ai-powered-sys/
├── services/
│   ├── ai_business_consultant_agent.py    # NEW: LangChain agent
│   ├── business_agent_tools.py            # NEW: Agent tools
│   └── ai_business_consultant.py          # DEPRECATED: Old system
├── frontend/
│   └── components/
│       ├── ai_reporting_agent.py          # NEW: Updated UI
│       └── ai_reporting.py                # DEPRECATED: Old UI
├── utils/
│   └── db_analytics.py                    # Analytics queries
├── docs/
│   └── agent_architecture.md              # This document
└── requirements.txt                        # Updated dependencies
```

## Migration Notes

**From Old System to New Agent:**

1. **Import Changes:**
   ```python
   # OLD
   from services.ai_business_consultant import AIBusinessConsultant

   # NEW
   from services.ai_business_consultant_agent import AIBusinessConsultantAgent
   ```

2. **Method Changes:**
   ```python
   # OLD
   consultant = AIBusinessConsultant()
   result = consultant.generate_consultation_report(focus_area="overall")

   # NEW
   agent = AIBusinessConsultantAgent()
   health = agent.analyze_business_health()  # 6 insights
   issues = agent.analyze_business_issues()  # 7 issues
   recs = agent.generate_recommendations(health)
   fixes = agent.generate_fixes(issues)
   ```

3. **UI Changes:**
   - Only 2 analysis options now (was 4)
   - Box-based layout (was text-based)
   - Multi-step flows with buttons
   - Action simulation capability

## Contact & Support

**For questions about the agent architecture:**
- Review LangSmith traces: https://cloud.langsmith.com
- Check Langfuse observability: https://cloud.langfuse.com
- LangChain docs: https://python.langchain.com
- LangGraph docs: https://langchain-ai.github.io/langgraph/

**Project Repository:**
- Located at: `/Users/leechin/Documents/enterprise-ai-powered-sys`
- Main entry: `frontend/app.py`
- Agent logic: `services/ai_business_consultant_agent.py`
- Tools: `services/business_agent_tools.py`
