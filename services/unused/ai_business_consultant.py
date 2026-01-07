"""
AI Business Consultant Agent
Generates comprehensive business reports and recommendations using Gemini API
"""

import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from google import genai
from google.genai import types
import pandas as pd
from datetime import datetime
from langsmith import traceable, Client
import logging
from utils.db_analytics import AnalyticsConnector

load_dotenv()

# Silence OpenTelemetry (Langfuse) errors
logging.getLogger("opentelemetry.sdk._shared_internal").setLevel(logging.CRITICAL)

from langfuse import observe, get_client  # traceability

class AIBusinessConsultant:
    """AI agent that analyzes business data and generates consultation reports"""

    def __init__(self):
        self.gemini_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        self.analytics = AnalyticsConnector()

        # Initialize Langsmith for tracing
        self.langsmith_client = Client()

        # Load prompts from files
        self.prompts_dir = os.path.join(os.path.dirname(__file__), 'prompts')
        self.system_instruction = self._load_prompt('system_instruction.txt')
        self.focus_prompts = {
            'overall': self._load_prompt('focus_overall.txt'),
            'revenue': self._load_prompt('focus_revenue.txt'),
            'customer': self._load_prompt('focus_customer.txt'),
            'inventory': self._load_prompt('focus_inventory.txt')
        }
        self.quick_insights_template = self._load_prompt('quick_insights_template.txt')

        self.generation_config = types.GenerateContentConfig(
            system_instruction=self.system_instruction.split('\n'),
            temperature=0.7,
            top_p=0.95,
            top_k=40,
        )

    def _load_prompt(self, filename: str) -> str:
        """Load a prompt from the prompts directory"""
        filepath = os.path.join(self.prompts_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {filepath}")

    @traceable(name="gather_business_metrics")
    def gather_business_metrics(self) -> Dict[str, Any]:
        """Gather all relevant business metrics from the database"""

        metrics = {
            "financial": {
                "total_revenue": self.analytics.get_total_revenue(),
                "total_orders": self.analytics.get_total_orders(),
                "avg_order_value": self.analytics.get_average_order_value(),
            },
            "customers": {
                "total_customers": self.analytics.get_total_customers(),
                "top_customers": self.analytics.get_top_customers(limit=5).to_dict('records') if not self.analytics.get_top_customers(limit=5).empty else [],
                "avg_rating": self.analytics.get_average_rating(),
                "total_reviews": self.analytics.get_review_count(),
            },
            "inventory": {
                "summary": self.analytics.get_inventory_summary(),
                "total_value": self.analytics.get_total_inventory_value(),
                "low_stock_items": len(self.analytics.get_low_stock_albums(threshold=10)),
            },
            "products": {
                "top_selling_albums": self.analytics.get_top_selling_albums(limit=10).to_dict('records') if not self.analytics.get_top_selling_albums(limit=10).empty else [],
                "top_rated_albums": self.analytics.get_top_rated_albums(limit=5).to_dict('records') if not self.analytics.get_top_rated_albums(limit=5).empty else [],
            },
            "genres": {
                "performance": self.analytics.get_genre_performance().to_dict('records') if not self.analytics.get_genre_performance().empty else [],
            },
            "labels": {
                "performance": self.analytics.get_label_performance().to_dict('records') if not self.analytics.get_label_performance().empty else [],
            },
            "payments": {
                "methods": self.analytics.get_payment_method_distribution().to_dict('records') if not self.analytics.get_payment_method_distribution().empty else [],
                "status_summary": self.analytics.get_payment_status_summary(),
            }
        }

        return metrics

    @traceable(name="build_consultation_prompt")
    def build_consultation_prompt(self, metrics: Dict[str, Any], focus_area: str = "overall") -> str:
        """Build a detailed prompt for the AI consultant"""

        prompt = f"""# Business Consultation Request for Misty Jazz Records
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Business Overview Data

### Financial Metrics
- Total Revenue: ${metrics['financial']['total_revenue']:,.2f}
- Total Orders: {metrics['financial']['total_orders']}
- Average Order Value: ${metrics['financial']['avg_order_value']:,.2f}

### Customer Metrics
- Total Customers: {metrics['customers']['total_customers']}
- Average Customer Rating: {metrics['customers']['avg_rating']:.2f}/5.0
- Total Reviews: {metrics['customers']['total_reviews']}
- Top 5 Customers by Spending:
"""

        for i, customer in enumerate(metrics['customers']['top_customers'][:5], 1):
            prompt += f"\n  {i}. {customer.get('name', 'N/A')} - ${customer.get('total_spent', 0):,.2f} ({customer.get('order_count', 0)} orders)"

        prompt += f"""

### Inventory Metrics
- Total Albums in Catalog: {metrics['inventory']['summary']['total_items']}
- Total Inventory Value: ${metrics['inventory']['total_value']:,.2f}
- Optimal Stock Items: {metrics['inventory']['summary']['optimal_stock']}
- Low Stock Items (≤10 units): {metrics['inventory']['low_stock_items']}
- Out of Stock Items: {metrics['inventory']['summary']['out_of_stock']}

### Top Selling Albums
"""

        for i, album in enumerate(metrics['products']['top_selling_albums'][:5], 1):
            prompt += f"\n  {i}. '{album.get('title', 'N/A')}' by {album.get('artist', 'N/A')} - {album.get('units_sold', 0)} units, ${album.get('revenue', 0):,.2f} revenue"

        prompt += "\n\n### Genre Performance\n"

        for genre in metrics['genres']['performance'][:5]:
            prompt += f"\n  - {genre.get('genre', 'N/A')}: {genre.get('units_sold', 0)} units sold, ${genre.get('revenue', 0):,.2f} revenue"

        prompt += "\n\n### Record Label Performance (Top 5)\n"

        for label in metrics['labels']['performance'][:5]:
            prompt += f"\n  - {label.get('label', 'N/A')}: {label.get('units_sold', 0)} units sold, ${label.get('revenue', 0):,.2f} revenue"

        prompt += "\n\n### Payment Analytics\n"

        payment_status = metrics['payments']['status_summary']
        prompt += f"""
- Completed Payments: {payment_status.get('completed', 0)}
- Pending Payments: {payment_status.get('pending', 0)}
- Failed Payments: {payment_status.get('failed', 0)}
"""

        prompt += "\n\n" + self.focus_prompts.get(focus_area, self.focus_prompts["overall"])

        return prompt

    @traceable(name="generate_consultation_report")
    def generate_consultation_report(self, focus_area: str = "overall") -> Dict[str, Any]:
        """
        Generate a comprehensive business consultation report

        Args:
            focus_area: 'overall', 'revenue', 'customer', or 'inventory'

        Returns:
            Dictionary with report content and metadata
        """

        # Gather metrics
        metrics = self.gather_business_metrics()

        # Build prompt
        prompt = self.build_consultation_prompt(metrics, focus_area)

        # Generate consultation with Gemini
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt,
                config=self.generation_config
            )

            consultation_text = response.text

            return {
                "success": True,
                "report": consultation_text,
                "metrics": metrics,
                "focus_area": focus_area,
                "timestamp": datetime.now().isoformat(),
                "model": "gemini-3-flash-preview"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "metrics": metrics,
                "focus_area": focus_area,
                "timestamp": datetime.now().isoformat()
            }

    @traceable(name="generate_quick_insights")
    def generate_quick_insights(self, limit: int = 5) -> List[Dict[str, str]]:
        """
        Generate quick, actionable insights based on current data

        Args:
            limit: Maximum number of insights to generate

        Returns:
            List of insight dictionaries
        """

        metrics = self.gather_business_metrics()

        prompt = self.quick_insights_template.format(
            limit=limit,
            revenue=f"{metrics['financial']['total_revenue']:,.2f}",
            orders=metrics['financial']['total_orders'],
            customers=metrics['customers']['total_customers'],
            low_stock_items=metrics['inventory']['low_stock_items'],
            failed_payments=metrics['payments']['status_summary'].get('failed', 0)
        )

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt,
                config=self.generation_config
            )

            # Parse the response into structured insights
            insights_text = response.text
            insights = []

            for section in insights_text.split('---'):
                section = section.strip()
                if section:
                    insight = {
                        "priority": self._extract_field(section, "PRIORITY"),
                        "insight": self._extract_field(section, "INSIGHT"),
                        "action": self._extract_field(section, "ACTION"),
                        "impact": self._extract_field(section, "IMPACT")
                    }
                    if insight["insight"]:  # Only add if we got valid data
                        insights.append(insight)

            return insights[:limit]

        except Exception as e:
            print(f"Error generating insights: {e}")
            return []

    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract a field value from formatted text"""
        lines = text.split('\n')
        for line in lines:
            if line.startswith(f"{field_name}:"):
                return line.replace(f"{field_name}:", "").strip()
        return ""

    @traceable(name="compare_time_periods")
    def compare_time_periods(self) -> Dict[str, Any]:
        """
        Compare business metrics across time periods
        Note: This requires order_date filtering - placeholder for now
        """

        # This would require date-range queries to compare periods
        # For now, return current metrics with a note

        metrics = self.gather_business_metrics()

        return {
            "current_period": metrics,
            "note": "Time period comparison requires date range filtering - feature coming soon"
        }
