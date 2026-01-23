"""
AI Business Health Analysis Agent
Analyzes overall business health and provides key insights
Separated from issues analysis for focused health monitoring
"""

import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_google_vertexai import ChatVertexAI
from langchain.agents import create_agent
from langfuse import observe
import json
import re

# Import Pydantic schemas
from services.schemas.ba_agent_schemas import HealthAnalysisOutput
from services.prompts import load_prompt

# Import query tools
from services.tools.business_query_tools import (
    scan_business_metrics,
    get_top_performing_products,
    get_top_customers,
    get_low_stock_items,
    get_failed_payments,
    get_pending_payments,
    get_genre_performance,
    get_label_performance,
    get_top_rated_albums,
    get_payment_method_distribution,
    get_revenue_by_date,
)

load_dotenv()

MODEL = os.getenv('VERTEX_MODEL')
PROJECT_ID = os.getenv('GCP_PROJECT_ID')
LOCATION = os.getenv('GCP_LOCATION', 'us-central1')

# Silence OpenTelemetry (Langfuse) errors
logging.getLogger("opentelemetry.sdk._shared_internal").setLevel(logging.CRITICAL)


class AIHealthAgent:
    """AI agent for analyzing overall business health"""

    def __init__(self):
        # Initialize Vertex AI model (uses GCP credits)
        self.llm = ChatVertexAI(
            model=MODEL,
            project=PROJECT_ID,
            location=LOCATION,
            temperature=0.7,
        )

        # Define available tools
        self.tools = [
            scan_business_metrics,
            get_top_performing_products,
            get_top_customers,
            get_low_stock_items,
            get_failed_payments,
            get_pending_payments,
            get_genre_performance,
            get_label_performance,
            get_top_rated_albums,
            get_payment_method_distribution,
            get_revenue_by_date,
        ]

        # Load system prompt from file
        self.system_prompt = load_prompt('health_analysis_system_prompt.txt')

        # Create agent
        self.health_agent = create_agent(
            self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt
        )

    def _extract_and_validate_json(
        self,
        response_text: str,
        schema_class
    ) -> Dict[str, Any]:
        """Extract and validate JSON from agent response"""
        try:
            # Try to extract JSON from code blocks
            json_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
            json_match = re.search(json_pattern, response_text, re.DOTALL)

            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # Try to find JSON object directly
                json_str = response_text.strip()

            # Parse JSON
            data = json.loads(json_str)

            # Validate with Pydantic
            validated = schema_class(**data)
            return validated.model_dump()

        except Exception as e:
            print(f"JSON extraction/validation error: {e}")
            print(f"Response text: {response_text[:500]}")
            return None

    @observe()
    def analyze_business_health(self) -> Dict[str, Any]:
        """
        Analyze overall business health and generate 6 key insights

        Returns:
            Dictionary with insights and metadata
        """
        try:
            # Invoke the agent
            result = self.health_agent.invoke({
                "messages": [("user", "Analyze the overall business health of Misty Jazz Records. Use the available tools to gather data and provide exactly 6 key insights.")]
            })

            # Extract and validate response
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                agent_response = last_message.content
            elif isinstance(last_message, dict):
                agent_response = last_message.get('content', str(last_message))
            else:
                agent_response = str(last_message)

            # Handle case where content is a list
            if isinstance(agent_response, list):
                agent_response = ' '.join([
                    item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    for item in agent_response
                ])

            # Use helper to extract and validate JSON
            insights_data = self._extract_and_validate_json(agent_response, HealthAnalysisOutput)

            # Fallback if validation failed
            if not insights_data or 'insights' not in insights_data:
                insights_data = {
                    "insights": [
                        {
                            "title": "Analysis Complete",
                            "content": str(agent_response)[:200] if agent_response else "No response",
                            "priority": "medium",
                            "metric_type": "overall"
                        }
                    ]
                }

            return {
                "success": True,
                "type": "health_analysis",
                "data": insights_data,
                "raw_response": agent_response,
                "model": MODEL
            }

        except Exception as e:
            return {
                "success": False,
                "type": "health_analysis",
                "error": str(e)
            }
