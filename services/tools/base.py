"""
Base Business Tools
Shared base class for all business tool classes.
"""

from typing import List, Dict, Any
from supabase import Client
from utils.clients import ClientManager


class BaseBusinessTools:
    """
    Base class providing shared initialization and utilities for business tools.

    All business tool classes should inherit from this to ensure:
    - Consistent client initialization via ClientManager singleton
    - Shared formatting utilities
    - DRY principle for common operations
    """

    def __init__(self):
        """Initialize with shared clients from ClientManager."""
        self.analytics = ClientManager.get_analytics()
        self.supabase: Client = ClientManager.get_supabase()

    def _format_list_result(
        self,
        title: str,
        items: List[Dict[str, Any]],
        fields: List[tuple]
    ) -> str:
        """
        Format a list of items into a readable string for LLM output.

        Args:
            title: Header title for the output
            items: List of dictionaries containing item data
            fields: List of (key, label, format_spec) tuples defining output format
                   format_spec can be: 'str', 'int', 'currency', 'rating'

        Returns:
            Formatted string suitable for LLM consumption

        Example:
            fields = [
                ('title', 'Title', 'str'),
                ('revenue', 'Revenue', 'currency'),
                ('rating', 'Rating', 'rating')
            ]
        """
        if not items:
            return f"No {title.lower()} data available."

        result = f"{title}:\n\n"
        for i, item in enumerate(items, 1):
            # First field as the main identifier
            first_key, _, _ = fields[0]
            result += f"{i}. {item.get(first_key, 'N/A')}\n"

            # Remaining fields as details
            for key, label, fmt in fields[1:]:
                value = item.get(key, 'N/A')
                if fmt == 'currency' and value != 'N/A':
                    result += f"   - {label}: ${value:,.2f}\n"
                elif fmt == 'rating' and value != 'N/A':
                    result += f"   - {label}: {value:.2f}/5.0\n"
                elif fmt == 'int' and value != 'N/A':
                    result += f"   - {label}: {value}\n"
                else:
                    result += f"   - {label}: {value}\n"

            result += "\n"

        return result

    def _format_metrics_section(
        self,
        title: str,
        metrics: Dict[str, Any],
        format_specs: Dict[str, str]
    ) -> str:
        """
        Format a metrics dictionary into a readable section.

        Args:
            title: Section title
            metrics: Dictionary of metric_name -> value
            format_specs: Dictionary of metric_name -> format_type
                         ('currency', 'int', 'rating', 'str')

        Returns:
            Formatted string section
        """
        result = f"{title}:\n"
        for key, value in metrics.items():
            label = key.replace('_', ' ').title()
            fmt = format_specs.get(key, 'str')

            if fmt == 'currency':
                result += f"- {label}: ${value:,.2f}\n"
            elif fmt == 'rating':
                result += f"- {label}: {value:.2f}/5.0\n"
            elif fmt == 'int':
                result += f"- {label}: {value}\n"
            else:
                result += f"- {label}: {value}\n"

        return result
