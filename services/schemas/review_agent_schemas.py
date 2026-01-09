"""
Pydantic schemas for AI Review Response Agent outputs
Ensures type safety and structured responses for customer review management
"""

from typing import Literal
from pydantic import BaseModel, Field


class ReviewResponseOutput(BaseModel):
    """Structured review response output"""
    response_text: str = Field(
        ...,
        description="AI-generated response to customer review",
        min_length=50,
        max_length=1000
    )
    tone: Literal["apologetic", "grateful", "encouraging", "supportive"] = Field(
        ...,
        description="Tone of the response"
    )
    includes_support_contact: bool = Field(
        ...,
        description="Whether the response includes a support contact request"
    )
