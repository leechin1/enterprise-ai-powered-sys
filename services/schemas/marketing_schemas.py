"""
Pydantic schemas for Marketing Service outputs
Ensures type safety and structured responses from LLM for email generation
"""

from pydantic import BaseModel, Field


class MarketingEmailOutput(BaseModel):
    """Structured marketing email output"""
    subject: str = Field(
        ...,
        description="Compelling email subject line",
        min_length=10,
        max_length=150
    )
    body: str = Field(
        ...,
        description="Full email body content with proper formatting and paragraphs",
        min_length=100,
        max_length=3000
    )
    call_to_action: str = Field(
        ...,
        description="Clear and specific call-to-action",
        min_length=10,
        max_length=200
    )
