"""
AI Business Consultant Agent (Refactored)
Uses LangChain agent architecture with Gemini 2.5-flash and custom tools
"""

import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langsmith import traceable
from langfuse import observe
import logging

# Import tools
from services.business_agent_tools import (
    scan_business_metrics,
    get_top_performing_products,
    get_top_customers,
    get_low_stock_items,
    get_failed_payments,
    get_pending_payments,
    get_genre_performance,
    generate_customer_email,
    generate_inventory_alert_email,
    cancel_transaction,
    recommend_restock_quantity,
)

load_dotenv()

# Silence OpenTelemetry (Langfuse) errors
logging.getLogger("opentelemetry.sdk._shared_internal").setLevel(logging.CRITICAL)


class AIBusinessConsultantAgent:
    """AI agent that analyzes business data using LangChain agent architecture"""

    def __init__(self):
        # Initialize Gemini model via LangChain
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            api_key=os.getenv('GEMINI_API_KEY'),
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
            generate_customer_email,
            generate_inventory_alert_email,
            cancel_transaction,
            recommend_restock_quantity,
        ]

        # System prompts
        self.system_prompt_health = """You are an expert business consultant for Misty Jazz Records, a premium vinyl record company.

Your role is to analyze business health and provide actionable recommendations.

ANALYSIS FOCUS: Overall Business Health
REPORTING STYLE: Concise boxes/cards for UI display

STRICT REQUIREMENTS:
- Generate EXACTLY 6 key insights (no more, no less)
- Each insight must be concise (2-3 sentences max)
- Focus on the most critical business metrics
- Identify both strengths and areas of concern
- Be specific with numbers and percentages when relevant

Use the available tools to scan business data and analyze performance.

Format your response as a JSON object with this structure:
{
  "insights": [
    {
      "title": "Brief title (4-6 words)",
      "content": "Concise insight content (2-3 sentences)",
      "priority": "high|medium|low",
      "metric_type": "financial|customer|inventory|product"
    }
  ]
}
"""

        self.system_prompt_issues = """You are an expert business consultant for Misty Jazz Records, a premium vinyl record company.

Your role is to identify critical business issues and provide actionable solutions.

ANALYSIS FOCUS: Business Issues & Problems
REPORTING STYLE: Concise problem identification with solution paths

STRICT REQUIREMENTS:
- Identify EXACTLY 7 critical issues (no more, no less)
- Each issue must be actionable and specific
- Prioritize issues by business impact
- Consider: failed payments, low inventory, customer satisfaction, revenue issues
- Focus on problems that can be solved with available tools

Use the available tools to scan for issues in the business data.

Format your response as a JSON object with this structure:
{
  "issues": [
    {
      "title": "Issue title (4-6 words)",
      "description": "Brief description of the issue (2-3 sentences)",
      "impact": "high|medium|low",
      "category": "payment|inventory|customer|financial",
      "affected_count": "Number of items/customers/transactions affected"
    }
  ]
}
"""

        self.system_prompt_recommendations = """You are an expert business strategist for Misty Jazz Records.

Based on the business health analysis provided, generate strategic recommendations.

STRICT REQUIREMENTS:
- Generate 5-7 strategic recommendations
- Each recommendation must be specific and actionable
- Include expected impact and implementation difficulty
- Prioritize by potential business value
- Be concise (2-3 sentences per recommendation)

Format your response as a JSON object with this structure:
{
  "recommendations": [
    {
      "title": "Recommendation title",
      "description": "Detailed recommendation (2-3 sentences)",
      "priority": "high|medium|low",
      "expected_impact": "Brief impact description",
      "difficulty": "easy|medium|hard"
    }
  ]
}
"""

        self.system_prompt_fixes = """You are an expert business problem solver for Misty Jazz Records.

Based on the issues identified, recommend specific fixes using available tools.

STRICT REQUIREMENTS:
- Provide specific, actionable fixes for each issue
- Suggest which tools to use for each fix
- Include step-by-step actions
- Be realistic about what can be automated vs manual work
- Prioritize fixes by impact and feasibility

Available action tools:
- generate_customer_email: Send communications to customers
- generate_inventory_alert_email: Alert inventory team
- cancel_transaction: Cancel failed/pending payments
- recommend_restock_quantity: Get restock recommendations

Format your response as a JSON object with this structure:
{
  "fixes": [
    {
      "issue_title": "Related issue from issues analysis",
      "fix_title": "Fix action title",
      "description": "How to fix this issue (2-3 sentences)",
      "tool_to_use": "Tool name or 'manual'",
      "automation_level": "full|partial|manual",
      "estimated_impact": "Expected improvement"
    }
  ]
}
"""

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

            # Extract the response - handle both string and message object
            import json
            import re

            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                agent_response = last_message.content
            elif isinstance(last_message, dict):
                agent_response = last_message.get('content', str(last_message))
            else:
                agent_response = str(last_message)

            # Handle case where content is a list (e.g., content blocks)
            if isinstance(agent_response, list):
                # Join list items or extract text from content blocks
                agent_response = ' '.join([
                    item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    for item in agent_response
                ])

            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', str(agent_response))
            if json_match:
                insights_data = json.loads(json_match.group(0))
            else:
                # Fallback: create structured response from text
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
                "model": "gemini-3-flash-preview"
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

            # Extract the response - handle both string and message object
            import json
            import re

            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                agent_response = last_message.content
            elif isinstance(last_message, dict):
                agent_response = last_message.get('content', str(last_message))
            else:
                agent_response = str(last_message)

            # Handle case where content is a list (e.g., content blocks)
            if isinstance(agent_response, list):
                # Join list items or extract text from content blocks
                agent_response = ' '.join([
                    item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    for item in agent_response
                ])

            # Parse JSON response
            json_match = re.search(r'\{[\s\S]*\}', str(agent_response))
            if json_match:
                issues_data = json.loads(json_match.group(0))
            else:
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
                "model": "gemini-3-flash-preview"
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

            # Extract the response - handle both string and message object
            import json
            import re

            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                agent_response = last_message.content
            elif isinstance(last_message, dict):
                agent_response = last_message.get('content', str(last_message))
            else:
                agent_response = str(last_message)

            # Handle case where content is a list (e.g., content blocks)
            if isinstance(agent_response, list):
                # Join list items or extract text from content blocks
                agent_response = ' '.join([
                    item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    for item in agent_response
                ])

            # Parse JSON response
            json_match = re.search(r'\{[\s\S]*\}', str(agent_response))
            if json_match:
                recommendations_data = json.loads(json_match.group(0))
            else:
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
                "model": "gemini-3-flash-preview"
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

            # Extract the response - handle both string and message object
            import json
            import re

            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                agent_response = last_message.content
            elif isinstance(last_message, dict):
                agent_response = last_message.get('content', str(last_message))
            else:
                agent_response = str(last_message)

            # Handle case where content is a list (e.g., content blocks)
            if isinstance(agent_response, list):
                # Join list items or extract text from content blocks
                agent_response = ' '.join([
                    item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    for item in agent_response
                ])

            # Parse JSON response
            json_match = re.search(r'\{[\s\S]*\}', str(agent_response))
            if json_match:
                fixes_data = json.loads(json_match.group(0))
            else:
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
                "model": "gemini-3-flash-preview"
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
