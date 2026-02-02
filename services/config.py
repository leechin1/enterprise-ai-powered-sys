"""
Centralized Configuration for AI Services
All configurable values are defined here for easy management
"""

import os
from dotenv import load_dotenv

load_dotenv()


# =============================================================================
# GCP / VERTEX AI CONFIGURATION
# =============================================================================

class GCPConfig:
    """Google Cloud Platform configuration"""
    PROJECT_ID: str = os.getenv('GCP_PROJECT_ID', '')
    LOCATION: str = os.getenv('GCP_LOCATION', 'us-central1')
    VERTEX_MODEL: str = os.getenv('VERTEX_MODEL', 'gemini-2.5-flash')


# =============================================================================
# MODEL CONFIGURATION
# Centralized temperatures and generation parameters for all agents
# =============================================================================

class ModelConfig:
    """LLM model settings - temperatures and generation parameters"""

    # Default generation parameters
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_TOP_P: float = 0.95
    DEFAULT_TOP_K: int = 40

    # Agent-specific temperatures
    TEMPERATURES = {
        'business_consultant': 0.7,
        'conversational': 0.7,
        'health': 0.7,
        'issues': 0.7,
        'review_response': 0.7,
        'jazz_research': 0.7,
        'marketing': 0.8,  # Slightly higher for creative content
        'rag': 0.7,
    }

    @classmethod
    def get_temperature(cls, agent_name: str) -> float:
        """Get temperature for a specific agent"""
        return cls.TEMPERATURES.get(agent_name, cls.DEFAULT_TEMPERATURE)


# =============================================================================
# RAG CONFIGURATION
# =============================================================================

class RAGConfig:
    """RAG (Retrieval Augmented Generation) settings"""
    EMBEDDING_MODEL: str = 'text-embedding-004'
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    EMBEDDING_DIMENSION: int = 768
    MATCH_COUNT: int = 5
    MATCH_THRESHOLD: float = 0.3


# =============================================================================
# REVIEW RESPONSE CONFIGURATION
# =============================================================================

class ReviewResponseConfig:
    """Review response agent thresholds and settings"""
    SENTIMENT_POSITIVE_THRESHOLD: float = 0.15
    SENTIMENT_NEGATIVE_THRESHOLD: float = -0.15
    STAR_HIGH_THRESHOLD: int = 4
    STAR_MEDIUM_THRESHOLD: int = 3
    STAR_LOW_THRESHOLD: int = 2
    MAX_RETRIES: int = 3
    RATE_LIMIT_DELAY: float = 1.5


# =============================================================================
# EMAIL SERVICE CONFIGURATION
# =============================================================================

class EmailConfig:
    """Email service settings"""
    API_URL: str = 'https://api.emailjs.com/api/v1.0/email/send'
    SERVICE_ID: str = os.getenv('EMAILJS_SERVICE_ID', '')
    TEMPLATE_ID: str = os.getenv('EMAILJS_TEMPLATE_ID', '')
    PUBLIC_KEY: str = os.getenv('EMAILJS_PUBLIC_KEY', '')
    PRIVATE_KEY: str = os.getenv('EMAILJS_PRIVATE_KEY', '')
    PLACEBO_MODE: bool = os.getenv('PLACEBO_MODE', 'true').lower() == 'true'
    PLACEBO_EMAIL: str = os.getenv('PLACEBO_EMAIL', '')
    REQUEST_TIMEOUT: int = 30
    CORS_ORIGIN: str = 'http://localhost'

    # Default email for all external communications (customers, suppliers, etc.)
    # All emails are routed here - the agent displays hi@mistyrecords.com but delivers here
    DEFAULT_EXTERNAL_EMAIL: str = 'carolinaleedev@gmail.com'


# =============================================================================
# ACTIVITY LOG CONFIGURATION
# =============================================================================

class ActivityLogConfig:
    """Activity logging settings"""
    TABLE_NAME: str = 'activity_logs'
    DEFAULT_DAYS_TO_KEEP: int = 30
    DEFAULT_QUERY_LIMIT: int = 1000


# =============================================================================
# MARKETING SERVICE CONFIGURATION
# =============================================================================

class MarketingConfig:
    """Marketing service settings"""
    DEFAULT_QUERY_LIMIT: int = 15
    PROMO_QUERY_LIMIT: int = 10


# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================

class ValidationConfig:
    """Validation and business logic constants"""

    # SQL validation - forbidden keywords for read-only queries
    FORBIDDEN_SQL_KEYWORDS: tuple = (
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE',
        'ALTER', 'CREATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
    )

    # Valid roles for email recipients
    VALID_RECIPIENT_ROLES: set = {'customer', 'supplier', 'staff', 'manager'}

    # Valid email types
    VALID_EMAIL_TYPES: set = {
        'customer_notification',
        'inventory_alert',
        'payment_followup',
        'management_report'
    }

    # Issue severities
    VALID_SEVERITIES: set = {'critical', 'high', 'medium', 'low'}

    # Issue categories
    VALID_CATEGORIES: set = {
        'inventory', 'payments', 'customers',
        'revenue', 'operations', 'data_quality', 'financial'
    }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_model_config(agent_name: str) -> dict:
    """
    Get model configuration for a specific agent

    Args:
        agent_name: Name of the agent (e.g., 'business_consultant', 'rag', 'marketing')

    Returns:
        Dict with temperature, top_p, top_k settings
    """
    return {
        'temperature': ModelConfig.get_temperature(agent_name),
        'top_p': ModelConfig.DEFAULT_TOP_P,
        'top_k': ModelConfig.DEFAULT_TOP_K,
    }


def get_gcp_config() -> dict:
    """Get GCP configuration as a dictionary"""
    return {
        'project_id': GCPConfig.PROJECT_ID,
        'location': GCPConfig.LOCATION,
        'model': GCPConfig.VERTEX_MODEL,
    }
