"""
Centralized Client Manager
Singleton pattern for shared database and analytics connections.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


class ClientManager:
    """
    Singleton manager for shared client instances.
    Provides centralized access to Supabase and Analytics connections.
    """
    _supabase_client: Optional[Client] = None
    _analytics_connector = None

    @classmethod
    def get_supabase(cls) -> Client:
        """
        Get or create the shared Supabase client.

        Returns:
            Supabase Client instance

        Raises:
            ValueError: If required environment variables are missing
        """
        if cls._supabase_client is None:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SECRET_KEY')

            if not supabase_url or not supabase_key:
                raise ValueError(
                    "Missing required environment variables: "
                    "SUPABASE_URL and SUPABASE_SECRET_KEY must be set"
                )

            cls._supabase_client = create_client(supabase_url, supabase_key)

        return cls._supabase_client

    @classmethod
    def get_analytics(cls):
        """
        Get or create the shared AnalyticsConnector instance.

        Returns:
            AnalyticsConnector instance
        """
        if cls._analytics_connector is None:
            from utils.db_analytics import AnalyticsConnector
            cls._analytics_connector = AnalyticsConnector()

        return cls._analytics_connector

    @classmethod
    def reset(cls):
        """
        Reset all cached clients. Useful for testing.
        """
        cls._supabase_client = None
        cls._analytics_connector = None
