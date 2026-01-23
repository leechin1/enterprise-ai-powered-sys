"""
AI Issues Analysis Agent
Three-stage reasoning: SQL Generation → Issues Identification → Fix Proposals
Uses database schema awareness and executes custom SQL queries
"""

import os
import logging
from typing import Dict, List, Any
from dotenv import load_dotenv
from langchain_google_vertexai import ChatVertexAI
from langchain.agents import create_agent
from langfuse import observe
import json
import re

# Import database schema
from utils.database_schema import get_schema

# Import Pydantic schemas
from services.schemas.ba_agent_schemas import SQLQueriesOutput, IssuesAnalysisOutput, FixesOutput
from services.prompts import load_prompt

# Import Supabase for SQL execution
from supabase import create_client, Client

# Import query tools (for executing generated SQL)
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

# Import generation tools (for proposed fixes)
from services.tools.business_generation_tools import (
    generate_customer_email,
    generate_inventory_alert_email,
    cancel_transaction,
    recommend_restock_quantity,
)

load_dotenv()

MODEL = os.getenv('VERTEX_MODEL')
PROJECT_ID = os.getenv('GCP_PROJECT_ID')
LOCATION = os.getenv('GCP_LOCATION', 'us-central1')

# Silence OpenTelemetry (Langfuse) errors
logging.getLogger("opentelemetry.sdk._shared_internal").setLevel(logging.CRITICAL)


class AIIssuesAgent:
    """AI agent for identifying business issues using three-stage reasoning"""

    def __init__(self):
        # Initialize Vertex AI model (uses GCP credits)
        self.llm = ChatVertexAI(
            model=MODEL,
            project=PROJECT_ID,
            location=LOCATION,
            temperature=0.7,
        )

        # Initialize Supabase client for SQL execution
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SECRET_KEY')
        self.supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

        # Define available tools for both stages
        self.query_tools = [
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

        self.fix_tools = [
            generate_customer_email,
            generate_inventory_alert_email,
            cancel_transaction,
            recommend_restock_quantity,
        ]

        # Load system prompts from files
        self.stage0_prompt = f"""You are an expert business analyst and SQL developer for Misty Jazz Records.

**DATABASE SCHEMA:**
{get_schema()}

{load_prompt('issues_stage0_sql_generation_prompt.txt')}
"""

        self.stage1_prompt = load_prompt('issues_stage1_analysis_prompt.txt')
        self.stage2_prompt = load_prompt('issues_stage2_fixes_prompt.txt')

        # Create agents for all stages
        # Stage 0: SQL Generation (no tools needed)
        self.sql_generation_agent = create_agent(
            self.llm,
            tools=[],  # No tools, just LLM reasoning
            system_prompt=self.stage0_prompt
        )

        # Stage 1: Issues Analysis (no tools, just analyzes query results)
        self.issues_agent = create_agent(
            self.llm,
            tools=[],  # No tools, analyzes provided query results
            system_prompt=self.stage1_prompt
        )

        # Stage 2: Fix Proposals
        self.fixes_agent = create_agent(
            self.llm,
            tools=self.fix_tools,
            system_prompt=self.stage2_prompt
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
    def generate_sql_queries(self) -> Dict[str, Any]:
        """
        STAGE 0: Generate SQL queries based on database schema

        Returns:
            Dictionary with SQL queries and metadata
        """
        try:
            # Invoke SQL Generation agent
            result = self.sql_generation_agent.invoke({
                "messages": [("user", "Based on the database schema provided, generate 5-10 SQL queries to investigate potential business issues. Return only the JSON response as specified in the prompt.")]
            })

            # Extract response
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                agent_response = last_message.content
            elif isinstance(last_message, dict):
                agent_response = last_message.get('content', str(last_message))
            else:
                agent_response = str(last_message)

            # Handle list content
            if isinstance(agent_response, list):
                agent_response = ' '.join([
                    item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    for item in agent_response
                ])

            # Extract and validate JSON
            queries_data = self._extract_and_validate_json(agent_response, SQLQueriesOutput)

            # Fallback if validation failed
            if not queries_data or 'queries' not in queries_data:
                queries_data = {
                    "queries": [
                        {
                            "query_id": "Q1",
                            "purpose": "Failed to generate queries",
                            "explanation": str(agent_response)[:200] if agent_response else "No response",
                            "sql_query": "SELECT 1;",
                            "priority": "medium"
                        }
                    ]
                }

            return {
                "success": True,
                "type": "sql_queries",
                "stage": 0,
                "data": queries_data,
                "raw_response": agent_response,
                "model": MODEL
            }

        except Exception as e:
            return {
                "success": False,
                "type": "sql_queries",
                "stage": 0,
                "error": str(e)
            }

    def _validate_read_only_query(self, sql_query: str) -> tuple[bool, str]:
        """
        Validate that SQL query is read-only (SELECT statements only)

        Args:
            sql_query: The SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """

        # Strip trailing semicolons (single trailing semicolon is acceptable)
        sql_query = sql_query.strip().rstrip(';')

        # Convert to uppercase and strip whitespace for checking
        query_upper = sql_query.upper()

        # Remove comments
        query_upper = re.sub(r'--.*$', '', query_upper, flags=re.MULTILINE)
        query_upper = re.sub(r'/\*.*?\*/', '', query_upper, flags=re.DOTALL)

        # Check for semicolons in the middle (multi-statement attempts)
        if ';' in query_upper:
            return False, "READ-ONLY VIOLATION: Multiple statements not allowed"

        # List of forbidden SQL keywords that modify data
        forbidden_keywords = [
            'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
            'TRUNCATE', 'GRANT', 'REVOKE', 'EXECUTE', 'EXEC',
            'MERGE', 'REPLACE', 'COPY', 'CALL'
        ]

        # Check if query contains any forbidden keywords using word boundaries
        # This prevents false positives like "created_at" matching "CREATE"
        for keyword in forbidden_keywords:
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, query_upper):
                return False, f"READ-ONLY VIOLATION: Query contains forbidden keyword '{keyword}'"

        # Ensure query starts with SELECT (after potential WITH clauses)
        if not re.match(r'^\s*(SELECT|WITH)\b', query_upper):
            return False, "READ-ONLY VIOLATION: Only SELECT queries are allowed"

        return True, ""

    def execute_sql_queries(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute SQL queries with READ-ONLY enforcement and return results

        Args:
            queries: List of SQL query objects from generate_sql_queries()

        Returns:
            Dictionary with query execution results
        """
        if not self.supabase:
            return {
                "success": False,
                "error": "Supabase client not initialized"
            }

        results = []
        for query_obj in queries:
            try:
                query_id = query_obj['query_id']
                sql_query = query_obj['sql_query']

                # ENFORCE READ-ONLY: Validate query before execution
                is_valid, error_msg = self._validate_read_only_query(sql_query)
                if not is_valid:
                    results.append({
                        "query_id": query_id,
                        "purpose": query_obj['purpose'],
                        "explanation": query_obj['explanation'],
                        "sql_query": sql_query,
                        "priority": query_obj['priority'],
                        "success": False,
                        "error": error_msg,
                        "data": [],
                        "row_count": 0
                    })
                    continue

                # Execute query using Supabase RPC with read-only function
                result = self.supabase.rpc('execute_readonly_sql', {'sql_query': sql_query}).execute()

                results.append({
                    "query_id": query_id,
                    "purpose": query_obj['purpose'],
                    "explanation": query_obj['explanation'],
                    "sql_query": sql_query,
                    "priority": query_obj['priority'],
                    "success": True,
                    "data": result.data if result.data else [],
                    "row_count": len(result.data) if result.data else 0
                })

            except Exception as e:
                results.append({
                    "query_id": query_obj['query_id'],
                    "purpose": query_obj['purpose'],
                    "explanation": query_obj['explanation'],
                    "sql_query": query_obj['sql_query'],
                    "priority": query_obj['priority'],
                    "success": False,
                    "error": str(e),
                    "data": [],
                    "row_count": 0
                })

        return {
            "success": True,
            "total_queries": len(queries),
            "successful_queries": sum(1 for r in results if r['success']),
            "results": results
        }

    @observe()
    def identify_business_issues(self, query_results: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        STAGE 1: Identify critical business issues based on SQL query results

        Args:
            query_results: Results from execute_sql_queries()

        Returns:
            Dictionary with identified issues and metadata
        """
        if not query_results:
            return {
                "success": False,
                "type": "issues_analysis",
                "stage": 1,
                "error": "No query results provided"
            }

        try:
            # Format query results for the agent
            results_summary = "\n\n".join([
                f"Query {res['query_id']}: {res['purpose']}\n"
                f"Explanation: {res['explanation']}\n"
                f"SQL: {res['sql_query']}\n"
                f"Results ({res['row_count']} rows): {json.dumps(res['data'][:10], indent=2) if res['success'] else 'Query failed: ' + res.get('error', 'Unknown error')}"
                for res in query_results
            ])

            # Invoke Stage 1 agent with query results
            result = self.issues_agent.invoke({
                "messages": [("user", f"Based on these SQL query results, identify exactly 7 critical business issues:\n\n{results_summary}")]
            })

            # Extract response
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                agent_response = last_message.content
            elif isinstance(last_message, dict):
                agent_response = last_message.get('content', str(last_message))
            else:
                agent_response = str(last_message)

            # Handle list content
            if isinstance(agent_response, list):
                agent_response = ' '.join([
                    item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    for item in agent_response
                ])

            # Extract and validate JSON
            issues_data = self._extract_and_validate_json(agent_response, IssuesAnalysisOutput)

            # Fallback if validation failed
            if not issues_data or 'issues' not in issues_data:
                issues_data = {
                    "issues": [
                        {
                            "title": "Analysis Complete",
                            "description": str(agent_response)[:200] if agent_response else "No response",
                            "severity": "medium",
                            "category": "operations",
                            "affected_metrics": [],
                            "requires_action": True
                        }
                    ]
                }

            return {
                "success": True,
                "type": "issues_analysis",
                "stage": 1,
                "data": issues_data,
                "raw_response": agent_response,
                "model": MODEL
            }

        except Exception as e:
            return {
                "success": False,
                "type": "issues_analysis",
                "stage": 1,
                "error": str(e)
            }

    @observe()
    def propose_fixes(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        STAGE 2: Propose concrete fixes for identified issues using available tools

        Args:
            issues: List of identified issues from Stage 1

        Returns:
            Dictionary with proposed fixes and metadata
        """
        try:
            # Format issues for the agent
            issues_summary = "\n\n".join([
                f"Issue {i+1}: {issue['title']}\n"
                f"Description: {issue['description']}\n"
                f"Severity: {issue['severity']}\n"
                f"Category: {issue['category']}"
                for i, issue in enumerate(issues[:7])  # Limit to 7 issues
            ])

            # Invoke Stage 2 agent
            result = self.fixes_agent.invoke({
                "messages": [("user", f"Based on these identified business issues, propose concrete fixes using the available tools:\n\n{issues_summary}\n\nProvide actionable solutions that a non-technical user can understand and execute.")]
            })

            # Extract response
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                agent_response = last_message.content
            elif isinstance(last_message, dict):
                agent_response = last_message.get('content', str(last_message))
            else:
                agent_response = str(last_message)

            # Handle list content
            if isinstance(agent_response, list):
                agent_response = ' '.join([
                    item.get('text', str(item)) if isinstance(item, dict) else str(item)
                    for item in agent_response
                ])

            # Extract and validate JSON
            fixes_data = self._extract_and_validate_json(agent_response, FixesOutput)

            # Fallback if validation failed
            if not fixes_data or 'fixes' not in fixes_data:
                fixes_data = {
                    "fixes": [
                        {
                            "issue_id": issue['title'],
                            "fix_title": f"Address {issue['title']}",
                            "fix_description": "Manual intervention required",
                            "tools_to_use": [],
                            "action_steps": ["Review the issue", "Take appropriate action"],
                            "expected_outcome": "Issue resolution",
                            "priority": "urgent"
                        }
                        for issue in issues[:7]
                    ]
                }

            return {
                "success": True,
                "type": "fixes_proposals",
                "stage": 2,
                "data": fixes_data,
                "raw_response": agent_response,
                "model": MODEL
            }

        except Exception as e:
            return {
                "success": False,
                "type": "fixes_proposals",
                "stage": 2,
                "error": str(e)
            }

    @observe()
    def analyze_and_propose_fixes(self) -> Dict[str, Any]:
        """
        Complete two-stage analysis: Identify issues → Propose fixes

        Returns:
            Dictionary with both issues and fixes
        """
        # Stage 1: Identify issues
        issues_result = self.identify_business_issues()

        if not issues_result["success"]:
            return issues_result

        # Extract issues
        issues = issues_result["data"]["issues"]

        # Stage 2: Propose fixes
        fixes_result = self.propose_fixes(issues)

        # Combine results
        return {
            "success": True,
            "type": "complete_analysis",
            "issues": issues_result,
            "fixes": fixes_result,
            "model": MODEL
        }
