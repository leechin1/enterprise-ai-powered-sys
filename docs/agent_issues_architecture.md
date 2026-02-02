# Conversational Agent Architecture

The AI Conversational Issues Agent is a LangGraph ReAct-based chatbot that autonomously investigates business issues through natural language dialogue.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                              │
│                  (Streamlit Chat UI)                            │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              AIConversationalIssuesAgent                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   LangGraph ReAct Agent                   │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │  │
│  │  │ ChatVertexAI│  │ Tool Binding│  │ Message History │   │  │
│  │  │ (Gemini 2.5)│  │  (12 tools) │  │   (20 msgs)     │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TOOL LAYER (12 Tools)                        │
│  Query Tools │ Analysis Tools │ Fix Tools │ Utility Tools       │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  IssuesAgentState (Singleton)                   │
│  queries │ query_results │ issues │ proposed_fixes │ focus      │
└─────────────────────────────────────────────────────────────────┘
```

## ReAct Pattern

The agent uses the **ReAct** (Reasoning + Acting) pattern from LangGraph:

```
User Message → Reason → Act (Tool Call) → Observe → Reason → Act → ... → Final Response
```

**ReAct Loop:**
1. **Reason** - LLM decides what to do based on context
2. **Act** - Execute a tool call
3. **Observe** - Process tool output
4. Repeat until task complete
5. **Respond** - Generate final user-facing response

## Message Flow

```
┌──────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│  User    │────▶│  process_    │────▶│  LangGraph  │────▶│  Tools   │
│  Message │     │  message()   │     │  ReAct Loop │     │          │
└──────────┘     └──────────────┘     └─────────────┘     └──────────┘
                        │                    │                  │
                        │                    │◀─────────────────┘
                        │                    │    Tool Results
                        │                    ▼
                        │              ┌─────────────┐
                        │◀─────────────│  Final AI   │
                        │              │  Response   │
                        ▼              └─────────────┘
                 ┌──────────────┐
                 │   Return     │
                 │   {response, │
                 │   tools_used}│
                 └──────────────┘
```

## Core Components

### 1. LLM Configuration

```python
self.llm = ChatVertexAI(
    model="gemini-2.5-flash",
    project=GCP_PROJECT_ID,
    location="us-central1",
    temperature=0.7,
)
```

### 2. Agent Creation

```python
from langgraph.prebuilt import create_react_agent

self.agent = create_react_agent(
    model=self.llm,
    tools=self.tools,      # 12 @tool decorated functions
    prompt=SYSTEM_PROMPT,  # Behavior instructions
)
```

### 3. Message Processing

```python
def process_message(self, user_message, conversation_history):
    # Convert history to LangChain format
    lc_history = self._convert_history_to_messages(history)
    lc_history.append(HumanMessage(content=user_message))

    # Invoke ReAct agent
    result = self.agent.invoke({"messages": lc_history})

    # Extract final response and tools used
    return {
        "response": final_response,
        "tools_used": tools_used,
        "tool_results": tool_results,
    }
```

## Tool Orchestration

The agent autonomously chains tools based on user intent:

```
User: "Check the inventory"
    │
    ▼
Agent Reasoning: User wants inventory analysis
    │
    ▼
Tool: generate_business_queries("inventory")
    │
    ▼
Tool: execute_business_queries()
    │
    ▼
Tool: analyze_issues_from_results()
    │
    ▼
Response: "Found 3 inventory issues: ..."
```

## Available Tools

| Tool | Purpose | Auto-chained |
|------|---------|--------------|
| `generate_business_queries` | Create SQL for focus area | Yes |
| `execute_business_queries` | Run SQL against database | Yes |
| `analyze_issues_from_results` | Identify issues from data | Yes |
| `propose_fix_for_issue` | Generate fix + emails | On request |
| `generate_email_for_issue` | On-demand email creation | On request |
| `edit_email` | Modify email before send | On request |
| `send_fix_emails` | Dispatch notifications | On approval |
| `get_issue_details` | View specific issue | On request |
| `find_issue_by_keyword` | Search issues | On request |
| `get_current_analysis_state` | Check progress | On request |
| `reset_analysis` | Clear state | On request |

## Intent Detection

The system prompt guides intent detection:

| User Says | Detected Intent | Tool Call |
|-----------|-----------------|-----------|
| "check inventory" | inventory | `generate_business_queries("inventory")` |
| "payment problems" | payments | `generate_business_queries("payments")` |
| "customer reviews" | customers | `generate_business_queries("customers")` |
| "sales trends" | revenue | `generate_business_queries("revenue")` |
| "full analysis" | all | `generate_business_queries("all")` |

## State Persistence

State is maintained via singleton across tool invocations:

```python
class IssuesAgentState:
    _instance = None

    queries: List[Dict]        # SQL queries
    query_results: List[Dict]  # Query output
    issues: List[Dict]         # Identified issues
    proposed_fixes: List[Dict] # Fix proposals
    focus_areas: List[str]     # Current focus
```

## Conversation Memory

The agent maintains context through message history:

```python
def _convert_history_to_messages(self, history):
    messages = []
    for msg in history[-20:]:  # Last 20 messages
        if msg['role'] == 'user':
            messages.append(HumanMessage(content=msg['content']))
        else:
            messages.append(AIMessage(content=msg['content']))
    return messages
```

## File Structure

```
services/
├── ai_conversational_issues_agent.py  # Main agent class
│   ├── SYSTEM_PROMPT                  # Behavior instructions
│   ├── AIConversationalIssuesAgent    # ReAct agent wrapper
│   └── INITIAL_QUERY_SUGGESTIONS      # UI quick actions
│
├── tools/
│   ├── issues_state.py                # Shared singleton state
│   ├── issues_query_tools.py          # SQL tools (2)
│   ├── issues_analysis_tools.py       # Analysis tools (4)
│   ├── issues_fix_tools.py            # Fix/email tools (4)
│   └── issues_utility_tools.py        # Utility tools (2)
│
frontend/
└── components/
    └── ai_reporting_agent.py          # Chat UI component
```

## Email Safety

**The agent can NEVER send emails to arbitrary addresses.** All emails are intercepted by `EmailService`:

```
Agent displays: hi@mistyrecords.com (hardcoded)
         │
         ▼
EmailService intercepts
         │
         ▼
Actual delivery: carolinaleedev@gmail.com
```

**Configuration:** `PLACEBO_MODE=false`, `DEFAULT_EXTERNAL_EMAIL=carolinaleedev@gmail.com`

## Key Design Decisions

1. **LangGraph ReAct** - Provides reliable multi-step tool orchestration
2. **Singleton State** - Enables tool chaining without parameter passing
3. **System Prompt** - Controls intent detection and response style
4. **20-message Context** - Balances memory with token limits
5. **Tool Decorators** - LangChain `@tool` for automatic schema generation
6. **Email Safety** - All emails routed to safe address, never arbitrary recipients
