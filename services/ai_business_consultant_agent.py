"""
AI Business Consultant Agent (Refactored)
Uses LangChain agent architecture with Gemini and custom tools
Enhanced with Pydantic schemas for structured outputs
"""

import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from langchain_google_vertexai import ChatVertexAI
from langchain.agents import create_agent
from langsmith import traceable
from langfuse import observe
import logging
import json
import re

# Import Pydantic schemas for structured outputs
from services.schemas.ba_agent_schemas import (
    HealthAnalysisOutput,
    IssuesAnalysisOutput,
    RecommendationsOutput,
    FixesOutput,
)
from services.prompts import load_prompt

# Import query tools (read-only analytics)
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

# Import generation tools (content generation & actions)
from services.tools.business_generation_tools import (
    generate_customer_email,
    generate_inventory_alert_email,
    cancel_transaction,
    recommend_restock_quantity,
)

load_dotenv()

MODEL = os.getenv('VERTEX_MODEL', 'gemini-2.0-flash')
PROJECT_ID = os.getenv('GCP_PROJECT_ID')
LOCATION = os.getenv('GCP_LOCATION', 'us-central1')

# Silence OpenTelemetry (Langfuse) errors
logging.getLogger("opentelemetry.sdk._shared_internal").setLevel(logging.CRITICAL)


class AIBusinessConsultantAgent:
    """AI agent that analyzes business data using LangChain agent architecture with structured outputs"""

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
            # Query tools (analytics)
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
            # Generation tools (actions)
            generate_customer_email,
            generate_inventory_alert_email,
            cancel_transaction,
            recommend_restock_quantity,
        ]

        # Load system prompts from files
        self.system_prompt_health = load_prompt('business_consultant_health_prompt.txt')

        self.system_prompt_issues = load_prompt('business_consultant_issues_prompt.txt')

        self.system_prompt_recommendations = load_prompt('business_consultant_recommendations_prompt.txt')

        self.system_prompt_fixes = load_prompt('business_consultant_fixes_prompt.txt')

        # Create agents for different analysis types
        self.health_agent = create_agent(
            self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt_health
        )

        self.issues_agent = create_agent(
            self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt_issues
        )

        self.recommendations_agent = create_agent(
            self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt_recommendations
        )

        self.fixes_agent = create_agent(
            self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt_fixes
        )

    def _extract_and_validate_json(self, response_text: str, schema_class, max_retries: int = 2):
        """
        Extract JSON from response and validate against Pydantic schema.
        Supports both plain JSON and JSON within code blocks (```json ... ```).

        Args:
            response_text: Raw text response from LLM
            schema_class: Pydantic model class to validate against
            max_retries: Maximum retry attempts if validation fails

        Returns:
            Validated Pydantic model instance or dict on failure
        """
        # Try to extract JSON from code blocks first (```json ... ```)
        json_block_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
        code_block_match = re.search(json_block_pattern, response_text, re.DOTALL)

        if code_block_match:
            json_text = code_block_match.group(1).strip()
        else:
            # Fallback to finding any JSON object
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            json_text = json_match.group(0) if json_match else response_text

        try:
            # Parse JSON
            data = json.loads(json_text)

            # Validate with Pydantic schema
            validated_data = schema_class(**data)
            return validated_data.model_dump()

        except (json.JSONDecodeError, Exception) as e:
            logging.warning(f"JSON extraction/validation failed: {e}")
            # Return raw data as fallback
            try:
                return json.loads(json_text) if json_text else {}
            except:
                return {}

    @traceable(name="analyze_business_health")
    @observe()
    def analyze_business_health(self) -> Dict[str, Any]:
        """
        Analyze overall business health and generate 6 key insights.

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

            # Handle case where content is a list (e.g., content blocks)
            if isinstance(agent_response, list):
                agent_response = ' '.join([
                    item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    for item in agent_response
                ])

            # Use helper to extract and validate JSON against Pydantic schema
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

    @traceable(name="analyze_business_issues")
    @observe()
    def analyze_business_issues(self) -> Dict[str, Any]:
        """
        Identify critical business issues (exactly 7).

        Returns:
            Dictionary with issues and metadata
        """
        try:
            result = self.issues_agent.invoke({
                "messages": [("user", "Identify exactly 7 critical business issues at Misty Jazz Records. Use the available tools to scan for problems in payments, inventory, customers, and financials.")]
            })

            # Extract and validate response
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                agent_response = last_message.content
            elif isinstance(last_message, dict):
                agent_response = last_message.get('content', str(last_message))
            else:
                agent_response = str(last_message)

            # Handle case where content is a list (e.g., content blocks)
            if isinstance(agent_response, list):
                agent_response = ' '.join([
                    item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    for item in agent_response
                ])

            # Use helper to extract and validate JSON against Pydantic schema
            issues_data = self._extract_and_validate_json(agent_response, IssuesAnalysisOutput)

            # Fallback if validation failed
            if not issues_data or 'issues' not in issues_data:
                issues_data = {
                    "issues": [
                        {
                            "title": "Analysis Complete",
                            "description": str(agent_response)[:200] if agent_response else "No response",
                            "impact": "medium",
                            "category": "general",
                            "affected_count": "N/A"
                        }
                    ]
                }

            return {
                "success": True,
                "type": "issues_analysis",
                "data": issues_data,
                "raw_response": agent_response,
                "model": MODEL
            }

        except Exception as e:
            return {
                "success": False,
                "type": "issues_analysis",
                "error": str(e)
            }

    @traceable(name="generate_recommendations")
    @observe()
    def generate_recommendations(self, health_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate strategic recommendations based on health analysis.

        Args:
            health_analysis: Results from analyze_business_health()

        Returns:
            Dictionary with recommendations
        """
        try:
            # Format health insights for context
            insights_summary = str(health_analysis.get("data", {}).get("insights", []))

            result = self.recommendations_agent.invoke({
                "messages": [(
                    "user",
                    f"Based on this business health analysis, generate 5-7 strategic recommendations:\n\n{insights_summary}"
                )]
            })

            # Extract and validate response
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                agent_response = last_message.content
            elif isinstance(last_message, dict):
                agent_response = last_message.get('content', str(last_message))
            else:
                agent_response = str(last_message)

            # Handle case where content is a list (e.g., content blocks)
            if isinstance(agent_response, list):
                agent_response = ' '.join([
                    item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    for item in agent_response
                ])

            # Use helper to extract and validate JSON against Pydantic schema
            recommendations_data = self._extract_and_validate_json(agent_response, RecommendationsOutput)

            # Fallback if validation failed
            if not recommendations_data or 'recommendations' not in recommendations_data:
                recommendations_data = {
                    "recommendations": [
                        {
                            "title": "Recommendations Available",
                            "description": str(agent_response)[:200] if agent_response else "No response",
                            "priority": "medium",
                            "expected_impact": "See details",
                            "difficulty": "medium"
                        }
                    ]
                }

            return {
                "success": True,
                "type": "recommendations",
                "data": recommendations_data,
                "raw_response": agent_response,
                "model": MODEL
            }

        except Exception as e:
            return {
                "success": False,
                "type": "recommendations",
                "error": str(e)
            }

    @traceable(name="generate_fixes")
    @observe()
    def generate_fixes(self, issues_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate specific fixes for identified issues.

        Args:
            issues_analysis: Results from analyze_business_issues()

        Returns:
            Dictionary with suggested fixes
        """
        try:
            issues_summary = str(issues_analysis.get("data", {}).get("issues", []))

            result = self.fixes_agent.invoke({
                "messages": [(
                    "user",
                    f"Based on these identified issues, recommend specific fixes using available tools:\n\n{issues_summary}"
                )]
            })

            # Extract and validate response
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                agent_response = last_message.content
            elif isinstance(last_message, dict):
                agent_response = last_message.get('content', str(last_message))
            else:
                agent_response = str(last_message)

            # Handle case where content is a list (e.g., content blocks)
            if isinstance(agent_response, list):
                agent_response = ' '.join([
                    item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    for item in agent_response
                ])

            # Use helper to extract and validate JSON against Pydantic schema
            fixes_data = self._extract_and_validate_json(agent_response, FixesOutput)

            # Fallback if validation failed
            if not fixes_data or 'fixes' not in fixes_data:
                fixes_data = {
                    "fixes": [
                        {
                            "issue_title": "General Issues",
                            "fix_title": "Review Required",
                            "description": str(agent_response)[:200] if agent_response else "No response",
                            "tool_to_use": "manual",
                            "automation_level": "manual",
                            "estimated_impact": "TBD"
                        }
                    ]
                }

            return {
                "success": True,
                "type": "fixes",
                "data": fixes_data,
                "raw_response": agent_response,
                "model": MODEL
            }

        except Exception as e:
            return {
                "success": False,
                "type": "fixes",
                "error": str(e)
            }

    def execute_fix_action(self, fix_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific fix action (placebo for now).

        Args:
            fix_data: Fix details from generate_fixes()

        Returns:
            Success confirmation
        """
        # This is a placebo function that simulates taking action
        return {
            "success": True,
            "message": f"Successfully executed fix: {fix_data.get('fix_title', 'Unknown')}",
            "action_taken": fix_data.get('tool_to_use', 'manual'),
            "note": "Action simulated for demonstration purposes"
        }
