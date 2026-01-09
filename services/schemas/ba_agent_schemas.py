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
        description="5-10 SQL queries to identify business issues",
        min_length=5,
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
    """Complete issues analysis output with exactly 7 issues"""
    issues: List[BusinessIssue] = Field(
        ...,
        description="Exactly 7 critical business issues",
        min_length=7,
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

class BusinessFix(BaseModel):
    """A specific fix for a business issue"""
    issue_id: str = Field(..., description="Issue title or ID being addressed", min_length=5, max_length=100)
    fix_title: str = Field(..., description="Clear action-oriented title for the fix", min_length=5, max_length=100)
    fix_description: str = Field(
        ...,
        description="Non-technical explanation for business users in plain language",
        min_length=50,
        max_length=1000
    )
    tools_to_use: List[str] = Field(
        default_factory=list,
        description="List of tool names to execute (e.g., ['generate_customer_email', 'cancel_transaction'])"
    )
    action_steps: List[str] = Field(
        ...,
        description="Step-by-step action plan",
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


class FixesOutput(BaseModel):
    """Fixes output - one fix per issue provided"""
    fixes: List[BusinessFix] = Field(
        ...,
        description="Fixes for the provided issues (one fix per issue)",
        min_length=1,
        max_length=10
    )
