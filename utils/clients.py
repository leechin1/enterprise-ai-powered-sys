"""
Centralized Client Manager
Singleton pattern for shared database and analytics connections.
"""

import os
import json
import tempfile
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


def setup_gcp_credentials():
    """
    Set up GCP credentials for non-GCP environments.

    Checks for GOOGLE_APPLICATION_CREDENTIALS_JSON env var containing
    the service account JSON content. If found, writes it to a temp file
    and sets GOOGLE_APPLICATION_CREDENTIALS to point to it.

    This allows Vertex AI to work in production environments like
    Heroku, Railway, Render, etc. that don't have GCP metadata access.
    """
    # Skip if already configured
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        return

    credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if not credentials_json:
        return

    try:
        # Validate it's valid JSON
        creds = json.loads(credentials_json)

        # Write to a temp file
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        )
        json.dump(creds, temp_file)
        temp_file.close()

        # Set the environment variable
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_file.name

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in GOOGLE_APPLICATION_CREDENTIALS_JSON: {e}")


# Initialize GCP credentials on module load
setup_gcp_credentials()


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
