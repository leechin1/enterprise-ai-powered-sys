"""
Pydantic schemas for AI Business Consultant Agent outputs
Ensures type safety and structured responses from LLM
"""

from typing import List, Literal
from pydantic import BaseModel, Field


# ============ HEALTH ANALYSIS SCHEMAS ============

class BusinessInsight(BaseModel):
    """A single business health insight"""
    title: str = Field(..., description="Brief title (4-6 words)", min_length=5, max_length=100)
    content: str = Field(..., description="Concise insight content (2-3 sentences)", min_length=20, max_length=500)
    priority: Literal["high", "medium", "low"] = Field(..., description="Priority level of this insight")
    metric_type: Literal["financial", "customer", "inventory", "product", "overall"] = Field(
        ..., description="Type of metric this insight relates to"
    )


class HealthAnalysisOutput(BaseModel):
    """Complete health analysis output with exactly 6 insights"""
    insights: List[BusinessInsight] = Field(
        ...,
        description="Exactly 6 key business insights",
        min_length=6,
        max_length=6
    )


# ============ SQL QUERIES SCHEMAS ============

class SQLQuery(BaseModel):
    """A single SQL query for business analysis"""
    query_id: str = Field(..., description="Unique identifier for this query (e.g., 'Q1', 'Q2')", min_length=2, max_length=10)
    purpose: str = Field(..., description="What business problem this query investigates", min_length=10, max_length=200)
    explanation: str = Field(..., description="Non-technical explanation for business users", min_length=20, max_length=500)
    sql_query: str = Field(..., description="The actual SQL query to execute", min_length=20, max_length=2000)
    priority: Literal["critical", "high", "medium"] = Field(..., description="Priority of this analysis")


class SQLQueriesOutput(BaseModel):
    """Collection of SQL queries for business analysis"""
    queries: List[SQLQuery] = Field(
        ...,
        description="SQL queries to identify business issues (1-10 for focused analysis, 5-10 for full)",
        min_length=1,
        max_length=10
    )


# ============ ISSUES ANALYSIS SCHEMAS ============

class BusinessIssue(BaseModel):
    """A single business issue or problem"""
    title: str = Field(..., description="Issue title (4-6 words)", min_length=5, max_length=100)
    description: str = Field(..., description="Brief description of the issue (2-3 sentences)", min_length=20, max_length=500)
    severity: Literal["critical", "high", "medium"] = Field(..., description="Issue severity level")
    category: Literal["inventory", "payments", "customers", "revenue", "operations", "data_quality", "financial"] = Field(
        ..., description="Category of the issue"
    )
    affected_metrics: List[str] = Field(default_factory=list, description="Specific metrics affected")
    requires_action: bool = Field(default=True, description="Whether immediate action is required")


class IssuesAnalysisOutput(BaseModel):
    """Complete issues analysis output with 0-7 issues (flexible for focused analysis)"""
    issues: List[BusinessIssue] = Field(
        default_factory=list,
        description="Business issues (0-7 for focused analysis, up to 7 for full analysis)",
        max_length=7
    )


# ============ RECOMMENDATIONS SCHEMAS ============

class StrategicRecommendation(BaseModel):
    """A strategic business recommendation"""
    title: str = Field(..., description="Recommendation title", min_length=5, max_length=100)
    description: str = Field(..., description="Detailed recommendation (2-3 sentences)", min_length=20, max_length=500)
    priority: Literal["high", "medium", "low"] = Field(..., description="Priority level")
    expected_impact: str = Field(..., description="Brief impact description", min_length=10, max_length=200)
    difficulty: Literal["easy", "medium", "hard"] = Field(..., description="Implementation difficulty")


class RecommendationsOutput(BaseModel):
    """Strategic recommendations output with 5-7 recommendations"""
    recommendations: List[StrategicRecommendation] = Field(
        ...,
        description="5-7 strategic recommendations",
        min_length=5,
        max_length=7
    )


# ============ FIXES SCHEMAS ============

class Recipient(BaseModel):
    """A recipient for fix-related communications"""
    name: str = Field(..., description="Full name of the recipient", min_length=2, max_length=100)
    email: str = Field(..., description="Email address of the recipient", min_length=5, max_length=100)
    role: Literal["customer", "supplier", "staff", "manager"] = Field(
        ..., description="Role of the recipient"
    )
    reason: str = Field(..., description="Why this person is receiving the communication", min_length=10, max_length=200)


class GeneratedEmail(BaseModel):
    """A pre-generated email ready to be sent"""
    email_type: Literal["customer_notification", "inventory_alert", "payment_followup", "management_report"] = Field(
        ..., description="Type of email being sent"
    )
    subject: str = Field(..., description="Email subject line", min_length=5, max_length=150)
    body: str = Field(..., description="Complete email body content, ready to send", min_length=50, max_length=3000)
    recipient_emails: List[str] = Field(..., description="List of email addresses to send to", min_length=1)


class BusinessFix(BaseModel):
    """A specific fix for a business issue - fully automated with pre-generated communications"""
    issue_id: str = Field(..., description="Issue title or ID being addressed", min_length=5, max_length=100)
    fix_title: str = Field(..., description="Clear action-oriented title for the fix", min_length=5, max_length=100)
    fix_description: str = Field(
        ...,
        description="Non-technical explanation for business users in plain language",
        min_length=50,
        max_length=1000
    )
    automated_actions: List[str] = Field(
        ...,
        description="List of automated actions that WILL be executed upon approval",
        min_length=1,
        max_length=10
    )
    expected_outcome: str = Field(
        ...,
        description="What will improve after applying this fix",
        min_length=20,
        max_length=300
    )
    priority: Literal["immediate", "urgent", "scheduled"] = Field(
        ..., description="When to execute this fix"
    )
    recipients: List[Recipient] = Field(
        default_factory=list,
        description="List of people who will receive emails/communications for this fix"
    )
    generated_emails: List[GeneratedEmail] = Field(
        default_factory=list,
        description="Pre-generated emails ready to be sent upon approval"
    )


class FixesOutput(BaseModel):
    """Fixes output - one fix per issue provided"""
    fixes: List[BusinessFix] = Field(
        ...,
        description="Fixes for the provided issues (one fix per issue)",
        min_length=1,
        max_length=10
    )


# ============ CONVERSATIONAL AGENT SCHEMAS ============

class ConversationMessage(BaseModel):
    """A single message in the conversation history"""
    role: Literal["user", "assistant", "system"] = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(default="", description="ISO timestamp of message")
    source: str = Field(default="", description="Source of the action/reasoning for assistant messages")
    tool_calls: List[str] = Field(default_factory=list, description="List of tools called for this response")
    data: dict = Field(default_factory=dict, description="Any associated data (query results, issues, etc.)")


class AgentAction(BaseModel):
    """An action the agent can take"""
    action_type: Literal[
        "generate_queries", "execute_queries", "identify_issues",
        "propose_fix", "ask_clarification", "provide_summary",
        "request_user_choice", "complete_workflow"
    ] = Field(..., description="Type of action being taken")
    action_description: str = Field(..., description="Human-readable description of what the agent is doing")
    reasoning: str = Field(..., description="Why the agent is taking this action")
    requires_user_input: bool = Field(default=False, description="Whether this action requires user response")


class AgentResponse(BaseModel):
    """Complete response from the conversational agent"""
    message: str = Field(..., description="The assistant's response message to display")
    action: AgentAction = Field(..., description="The action being taken")
    options: List[str] = Field(default_factory=list, description="Options to present to user if requires_user_input")
    data: dict = Field(default_factory=dict, description="Any data associated with this response")
    source_reasoning: str = Field(..., description="Source and reasoning for this response")
    next_steps: List[str] = Field(default_factory=list, description="What the agent plans to do next")


class ConversationState(BaseModel):
    """Current state of the conversation workflow"""
    stage: Literal[
        "initial", "awaiting_generation_choice", "awaiting_focus_areas",
        "generating_queries", "queries_generated", "awaiting_query_approval",
        "executing_queries", "queries_executed", "identifying_issues",
        "issues_identified", "awaiting_fix_selection", "proposing_fix",
        "fix_proposed", "editing_emails", "workflow_complete"
    ] = Field(default="initial", description="Current stage of the workflow")
    focus_areas: List[str] = Field(default_factory=list, description="User-specified areas to focus on")
    generated_queries: List[dict] = Field(default_factory=list, description="Generated SQL queries")
    query_results: List[dict] = Field(default_factory=list, description="Results from executed queries")
    identified_issues: List[dict] = Field(default_factory=list, description="Identified business issues")
    selected_issue_index: int = Field(default=-1, description="Index of issue selected for fix")
    proposed_fixes: List[dict] = Field(default_factory=list, description="Proposed fixes")
    editing_email_index: int = Field(default=-1, description="Index of email being edited")
