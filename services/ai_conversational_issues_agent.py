"""
AI Conversational Issues Agent (Agentic Version)
True agentic multi-turn dialogue interface for business issues analysis.
Uses LangGraph ReAct agent with @tool decorated functions for autonomous decision making.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_vertexai import ChatVertexAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langfuse import observe

# Import centralized config
from services.config import GCPConfig, ModelConfig

# Import the agentic tools (modular)
from services.tools.issues_state import IssuesAgentState
from services.tools.issues_query_tools import generate_business_queries, execute_business_queries
from services.tools.issues_analysis_tools import (
    analyze_issues_from_results,
    get_issue_details,
    get_issue_detail,
    find_issue_by_keyword,
)
from services.tools.issues_fix_tools import propose_fix_for_issue, edit_email, send_fix_emails
from services.tools.issues_utility_tools import get_current_analysis_state, reset_analysis

load_dotenv()

# Setup GCP credentials
from utils.clients import setup_gcp_credentials
setup_gcp_credentials()

logging.getLogger("opentelemetry.sdk._shared_internal").setLevel(logging.CRITICAL)


# Suggested initial queries for the UI
INITIAL_QUERY_SUGGESTIONS = [
    {
        "label": "📦 Check Inventory",
        "query": "Check for inventory issues only - focus on stock levels, out of stock, and slow-moving items",
        "description": "Focused analysis of inventory and stock issues only"
    },
    {
        "label": "💳 Payment Issues",
        "query": "Check for payment problems only - focus on failed transactions and refunds",
        "description": "Focused analysis of payment and transaction issues only"
    },
    {
        "label": "👥 Customer Reviews",
        "query": "Check for customer satisfaction issues only - focus on reviews and complaints",
        "description": "Focused analysis of customer feedback and satisfaction only"
    },
    {
        "label": "💰 Revenue Analysis",
        "query": "Analyze revenue and sales trends only - focus on underperforming products",
        "description": "Focused analysis of sales and revenue issues only"
    },
    {
        "label": "🔍 Full Analysis",
        "query": "Run a complete business analysis across all areas",
        "description": "Comprehensive analysis of inventory, payments, customers, and revenue"
    },
    {
        "label": "📊 Current Status",
        "query": "What's the current state of our analysis?",
        "description": "Check the status of the current analysis"
    },
]


SYSTEM_PROMPT = """You are an AI Business Intelligence Agent for Misty Jazz Records, a vinyl record store.
You help identify and resolve business issues through natural conversation.

## YOUR CAPABILITIES

You have access to powerful tools that let you:
1. **generate_business_queries** - Create SQL queries to investigate specific areas (inventory, payments, customers, revenue, operations)
2. **execute_business_queries** - Run the queries against the database
3. **analyze_issues_from_results** - Analyze results to identify business issues
4. **propose_fix_for_issue** - Generate detailed fix proposals with email notifications
5. **edit_email** - Modify generated emails before sending
6. **send_fix_emails** - Send notification emails (in placebo mode for testing)
7. **get_current_analysis_state** - Check what has been done so far
8. **reset_analysis** - Start fresh with a new analysis
9. **get_issue_details** or **get_issue_detail** - Get detailed info about a specific issue by number
10. **find_issue_by_keyword** - Search for issues by keyword in title/description

## INTENT DETECTION - CRITICAL

Before calling generate_business_queries(), you MUST determine the user's focus area from their message:

| User Says | Focus Area | Tool Call |
|-----------|------------|-----------|
| "check inventory", "stock levels", "low stock", "out of stock", "products" | inventory | `generate_business_queries("inventory")` |
| "payment issues", "failed payments", "transactions", "refunds" | payments | `generate_business_queries("payments")` |
| "customer reviews", "satisfaction", "complaints", "feedback" | customers | `generate_business_queries("customers")` |
| "sales", "revenue", "income", "performance", "underperforming" | revenue | `generate_business_queries("revenue")` |
| "full analysis", "everything", "all issues", "comprehensive", "health check" | all | `generate_business_queries("all")` |

**CRITICAL INTENT RULES:**
- If user mentions ONE specific area, use ONLY that focus area
- Do NOT default to "all" when user asks about something specific
- "check the inventory" → `generate_business_queries("inventory")`, NOT "all"
- "any payment problems?" → `generate_business_queries("payments")`, NOT "all"
- Only use "all" when user explicitly asks for full/comprehensive analysis

## HOW TO BEHAVE

### Be Proactive and Action-Oriented
- When a user mentions ANY concern, IMMEDIATELY TAKE ACTION - don't just ask what they want
- Chain tool calls together to complete the full analysis workflow automatically
- Example: If user says "check inventory", call generate_business_queries("inventory") → execute_business_queries → analyze_issues_from_results ALL IN ONE GO
- IMPORTANT: Use the correct focus area based on intent detection (see table above)
- If user asks about analysis state and there's nothing done, OFFER to start an analysis and ask if they want you to proceed

### Typical Workflow (Execute All Steps Automatically)
1. User expresses concern → Generate queries focused on that area
2. Execute queries IMMEDIATELY after generating them (don't wait for user)
3. Analyze results IMMEDIATELY to identify issues (don't wait for user)
4. Present findings with severity levels
5. Offer to propose fixes for critical issues
6. Send notifications only upon explicit approval

### When No Analysis Exists
If the user asks about state/status and no analysis has been done:
- Report the empty state clearly
- IMMEDIATELY offer to run an analysis
- Ask: "Would you like me to run a full business analysis right now?"
- If user says yes or expresses any concern, START THE FULL PIPELINE

### Response Style
- Use markdown formatting for clear presentation
- Include emojis for visual clarity (🔴 critical, 🟠 high, 🟡 medium, 🟢 low)
- Always explain what you're doing and why
- Cite which tool provided each piece of information

### CRITICAL: Include Full Dashboard Output
- When `analyze_issues_from_results()` returns a DATA DASHBOARD, you MUST include the ENTIRE dashboard in your response
- DO NOT summarize or paraphrase the dashboard - copy it VERBATIM
- The dashboard contains important tables with actual data that users need to see
- Include ALL markdown tables, headers, and data from the tool output
- Users need to see the actual numbers, not just "no issues found"

### Important Rules
- ALWAYS run the FULL analysis pipeline when investigating issues (don't stop halfway)
- Don't stop at generating queries - execute and analyze them too IN THE SAME TURN
- When user asks to fix an issue, generate the proposal AND explain what will happen
- Respect user decisions - don't send emails without explicit approval
- If something fails, explain the error and suggest alternatives
- Be proactive! Users prefer agents that take action over agents that ask questions
- **ALWAYS include the full DATA DASHBOARD from analyze_issues_from_results() - never summarize it**

## CONVERSATION MEMORY
You have full access to the conversation history. Use it to:
- Remember what issues were found earlier
- Track which issues have been addressed
- Avoid repeating work that's already done
- Provide context-aware responses

Remember: You're not just answering questions - you're TAKING ACTION to solve business problems!
The best response is one where you've already done the work, not one where you ask what to do.
"""


class AIConversationalIssuesAgent:
    """
    True agentic conversational AI for business issues analysis.

    This agent autonomously:
    - Decides which tools to call based on conversation context
    - Chains multiple tool calls to complete complex analyses
    - Uses conversation memory for context-aware responses
    - Plans and executes multi-step workflows

    Uses LangGraph's ReAct agent pattern for reliable tool calling.
    """

    def __init__(self):
        # Initialize Vertex AI model using centralized config
        self.llm = ChatVertexAI(
            model=GCPConfig.VERTEX_MODEL,
            project=GCPConfig.PROJECT_ID,
            location=GCPConfig.LOCATION,
            temperature=ModelConfig.get_temperature('conversational'),
        )

        # Define available tools for the agent
        self.tools = [
            generate_business_queries,
            execute_business_queries,
            analyze_issues_from_results,
            propose_fix_for_issue,
            edit_email,
            send_fix_emails,
            get_current_analysis_state,
            reset_analysis,
            get_issue_details,
            get_issue_detail,  # Alias for get_issue_details
            find_issue_by_keyword,  # Search issues by keyword
        ]

        # Create the ReAct agent using LangGraph
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=SYSTEM_PROMPT,
        )

    def _convert_history_to_messages(self, history: List[Dict]) -> List:
        """Convert conversation history to LangChain message format."""
        messages = []
        for msg in history[-20:]:  # Keep last 20 messages for context
            role = msg.get('role', 'user')
            content = msg.get('content', '')

            if role == 'user':
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))

        return messages

    @observe()
    def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict],
    ) -> Dict[str, Any]:
        """
        Process a user message with full agentic behavior.

        The agent will:
        1. Understand the user's intent from context
        2. Decide which tools to call
        3. Execute tools and chain results
        4. Provide a comprehensive response

        Args:
            user_message: The user's input message
            conversation_history: List of previous messages

        Returns:
            Dictionary with response, tools used, and metadata
        """
        try:
            # Convert history to LangChain format
            lc_history = self._convert_history_to_messages(conversation_history)

            # Add the current user message
            lc_history.append(HumanMessage(content=user_message))

            # Invoke the agent
            result = self.agent.invoke({
                "messages": lc_history
            })

            # Extract the final response and tools used
            final_messages = result.get("messages", [])
            tools_used = []
            tool_results = []

            # Process messages to extract tool calls and final response
            final_response = ""
            for msg in final_messages:
                # Check for tool calls
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tools_used.append(tool_call.get('name', 'unknown'))

                # Check for tool messages (results)
                if msg.type == 'tool':
                    tool_results.append({
                        "tool": msg.name,
                        "output_preview": str(msg.content)[:200] + "..." if len(str(msg.content)) > 200 else str(msg.content)
                    })

                # Get the final AI response
                if msg.type == 'ai' and msg.content and not getattr(msg, 'tool_calls', None):
                    final_response = msg.content

            # If no explicit final response, use the last AI message content
            if not final_response:
                for msg in reversed(final_messages):
                    if msg.type == 'ai' and msg.content:
                        final_response = msg.content
                        break

            return {
                "success": True,
                "response": final_response or "I completed the requested actions. Please let me know if you need anything else.",
                "tools_used": tools_used,
                "tool_results": tool_results,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logging.error(f"Agent error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "response": f"I encountered an error while processing your request: {str(e)}\n\nPlease try again or rephrase your question.",
                "tools_used": [],
                "tool_results": [],
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    @staticmethod
    def get_initial_suggestions() -> List[Dict[str, str]]:
        """Get the list of initial query suggestions for the UI."""
        return INITIAL_QUERY_SUGGESTIONS

    @staticmethod
    def reset_state():
        """Reset the agent's analysis state."""
        state = IssuesAgentState.get_instance()
        state.reset()

    def get_greeting(self) -> Dict[str, Any]:
        """Get the initial greeting message for new conversations."""
        return {
            "success": True,
            "response": """👋 **Hello! I'm your AI Business Intelligence Assistant.**

I can help you identify and resolve business issues for Misty Jazz Records. I have access to your database and can:

- 🔍 **Investigate business areas** (inventory, payments, customers, revenue)
- 📊 **Analyze data** to find potential problems
- 🔧 **Propose fixes** with automated actions
- 📧 **Send notifications** to relevant stakeholders

**How can I help you today?** You can:
- Ask me to analyze a specific area (e.g., "Check our inventory")
- Express a concern (e.g., "I'm worried about payment issues")
- Request a full analysis (e.g., "Run a complete business health check")

Or try one of the suggested queries below! 👇""",
            "tools_used": [],
            "suggestions": INITIAL_QUERY_SUGGESTIONS,
            "timestamp": datetime.now().isoformat(),
        }
