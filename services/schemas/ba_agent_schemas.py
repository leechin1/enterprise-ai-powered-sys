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


# ============ ISSUES ANALYSIS SCHEMAS ============

class BusinessIssue(BaseModel):
    """A single business issue or problem"""
    title: str = Field(..., description="Issue title (4-6 words)", min_length=5, max_length=100)
    description: str = Field(..., description="Brief description of the issue (2-3 sentences)", min_length=20, max_length=500)
    impact: Literal["high", "medium", "low"] = Field(..., description="Business impact level")
    category: Literal["payment", "inventory", "customer", "financial", "general"] = Field(
        ..., description="Category of the issue"
    )
    affected_count: str = Field(..., description="Number of items/customers/transactions affected (e.g., '5 payments', '12 albums')")


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
    issue_title: str = Field(..., description="Title of the issue being fixed", min_length=5, max_length=100)
    fix_title: str = Field(..., description="Clear action-oriented title for the fix", min_length=5, max_length=100)
    description: str = Field(
        ...,
        description="Non-technical, paragraph-formatted description for business users. Use plain language, proper paragraphs, no function names or code. Explain what needs to be done in business terms.",
        min_length=100,
        max_length=1000
    )
    technical_steps: str = Field(
        ...,
        description="Technical implementation steps with specific tool names and parameters for developers",
        min_length=50,
        max_length=800
    )
    tool_to_use: str = Field(
        ...,
        description="Tool name (e.g., 'cancel_transaction', 'generate_inventory_alert_email') or 'manual'",
        min_length=3,
        max_length=100
    )
    automation_level: Literal["full", "partial", "manual"] = Field(
        ..., description="Level of automation possible"
    )
    estimated_impact: str = Field(
        ...,
        description="Specific expected improvement with numbers",
        min_length=10,
        max_length=200
    )


class FixesOutput(BaseModel):
    """Fixes output - one fix per issue provided"""
    fixes: List[BusinessFix] = Field(
        ...,
        description="Fixes for the provided issues (one fix per issue)",
        min_length=1,
        max_length=10
    )
