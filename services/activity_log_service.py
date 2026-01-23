"""
Activity Log Service - Tracks all actions in the enterprise system
Stores activity logs in Supabase for persistence and analysis
"""

import os
import logging
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SECRET_KEY = os.getenv('SUPABASE_SECRET_KEY')

logger = logging.getLogger(__name__)

# Activity types
ActivityType = Literal[
    "fix_proposed",
    "fix_approved",
    "fix_declined",
    "email_sent",
    "email_failed",
    "issue_identified",
    "sql_generated",
    "sql_executed",
    "health_analysis",
    "document_indexed",
    "rag_query",
    "system_event"
]

# Activity categories
ActivityCategory = Literal[
    "ai_reporting",
    "email",
    "issues",
    "fixes",
    "knowledge",
    "analytics",
    "system"
]


class ActivityLogService:
    """
    Activity logging service for tracking all actions in the enterprise system.
    Stores logs in Supabase 'activity_logs' table.
    """

    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_SECRET_KEY must be set")

        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
        self.table_name = "activity_logs"

    def log_activity(
        self,
        action_type: str,
        description: str,
        category: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[str] = None,
        status: str = "success"
    ) -> Dict[str, Any]:
        """
        Log an activity to the database.

        Args:
            action_type: Type of action (fix_proposed, email_sent, etc.)
            description: Human-readable description of the activity
            category: Category of activity (ai_reporting, email, etc.)
            metadata: Additional data about the activity
            user_id: Optional user identifier
            related_entity_type: Type of related entity (issue, fix, email, etc.)
            related_entity_id: ID of related entity
            status: Status of the activity (success, failed, pending)

        Returns:
            Result dict with success status and log ID
        """
        try:
            log_entry = {
                "action_type": action_type,
                "description": description,
                "category": category,
                "metadata": metadata or {},
                "user_id": user_id,
                "related_entity_type": related_entity_type,
                "related_entity_id": related_entity_id,
                "status": status,
                "created_at": datetime.now().isoformat()
            }

            result = self.supabase.table(self.table_name).insert(log_entry).execute()

            if result.data:
                logger.info(f"Activity logged: {action_type} - {description}")
                return {
                    "success": True,
                    "log_id": result.data[0].get("id"),
                    "timestamp": log_entry["created_at"]
                }
            else:
                return {
                    "success": False,
                    "error": "No data returned from insert"
                }

        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def log_fix_proposed(
        self,
        issue_title: str,
        fix_title: str,
        fix_id: Optional[str] = None,
        recipients_count: int = 0,
        emails_count: int = 0
    ) -> Dict[str, Any]:
        """Log when a fix is proposed"""
        return self.log_activity(
            action_type="fix_proposed",
            description=f"Fix proposed for issue: {issue_title}",
            category="fixes",
            metadata={
                "issue_title": issue_title,
                "fix_title": fix_title,
                "recipients_count": recipients_count,
                "emails_count": emails_count
            },
            related_entity_type="fix",
            related_entity_id=fix_id
        )

    def log_fix_approved(
        self,
        issue_title: str,
        fix_title: str,
        fix_id: Optional[str] = None,
        emails_sent: int = 0,
        recipients: List[str] = None
    ) -> Dict[str, Any]:
        """Log when a fix is approved and executed"""
        return self.log_activity(
            action_type="fix_approved",
            description=f"Fix approved and executed: {fix_title}",
            category="fixes",
            metadata={
                "issue_title": issue_title,
                "fix_title": fix_title,
                "emails_sent": emails_sent,
                "recipients": recipients or []
            },
            related_entity_type="fix",
            related_entity_id=fix_id
        )

    def log_fix_declined(
        self,
        issue_title: str,
        fix_title: str,
        fix_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log when a fix is declined"""
        return self.log_activity(
            action_type="fix_declined",
            description=f"Fix declined: {fix_title}",
            category="fixes",
            metadata={
                "issue_title": issue_title,
                "fix_title": fix_title,
                "reason": reason
            },
            related_entity_type="fix",
            related_entity_id=fix_id,
            status="declined"
        )

    def log_email_sent(
        self,
        to_email: str,
        subject: str,
        email_type: str,
        placebo_mode: bool = False,
        related_fix_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log when an email is sent"""
        return self.log_activity(
            action_type="email_sent",
            description=f"Email sent to {to_email}: {subject[:50]}...",
            category="email",
            metadata={
                "to_email": to_email,
                "subject": subject,
                "email_type": email_type,
                "placebo_mode": placebo_mode
            },
            related_entity_type="email",
            related_entity_id=related_fix_id
        )

    def log_email_failed(
        self,
        to_email: str,
        subject: str,
        error: str,
        related_fix_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log when an email fails to send"""
        return self.log_activity(
            action_type="email_failed",
            description=f"Email failed to {to_email}: {error[:50]}",
            category="email",
            metadata={
                "to_email": to_email,
                "subject": subject,
                "error": error
            },
            related_entity_type="email",
            related_entity_id=related_fix_id,
            status="failed"
        )

    def log_issue_identified(
        self,
        issue_title: str,
        severity: str,
        category: str,
        issue_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log when a business issue is identified"""
        return self.log_activity(
            action_type="issue_identified",
            description=f"Issue identified: {issue_title} ({severity})",
            category="issues",
            metadata={
                "issue_title": issue_title,
                "severity": severity,
                "issue_category": category
            },
            related_entity_type="issue",
            related_entity_id=issue_id
        )

    def log_sql_generated(
        self,
        query_count: int,
        model: str
    ) -> Dict[str, Any]:
        """Log when SQL queries are generated"""
        return self.log_activity(
            action_type="sql_generated",
            description=f"Generated {query_count} SQL queries using {model}",
            category="ai_reporting",
            metadata={
                "query_count": query_count,
                "model": model
            }
        )

    def log_sql_executed(
        self,
        total_queries: int,
        successful_queries: int
    ) -> Dict[str, Any]:
        """Log when SQL queries are executed"""
        status = "success" if successful_queries == total_queries else "partial"
        return self.log_activity(
            action_type="sql_executed",
            description=f"Executed {successful_queries}/{total_queries} SQL queries",
            category="ai_reporting",
            metadata={
                "total_queries": total_queries,
                "successful_queries": successful_queries
            },
            status=status
        )

    def log_health_analysis(
        self,
        insights_count: int,
        model: str
    ) -> Dict[str, Any]:
        """Log when health analysis is performed"""
        return self.log_activity(
            action_type="health_analysis",
            description=f"Business health analysis completed with {insights_count} insights",
            category="ai_reporting",
            metadata={
                "insights_count": insights_count,
                "model": model
            }
        )

    def log_rag_query(
        self,
        query: str,
        sources_used: int,
        success: bool
    ) -> Dict[str, Any]:
        """Log when a RAG knowledge query is made"""
        return self.log_activity(
            action_type="rag_query",
            description=f"Knowledge query: {query[:50]}...",
            category="knowledge",
            metadata={
                "query": query,
                "sources_used": sources_used
            },
            status="success" if success else "failed"
        )

    def get_recent_activities(
        self,
        limit: int = 50,
        category: Optional[str] = None,
        action_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent activity logs.

        Args:
            limit: Maximum number of logs to return
            category: Optional filter by category
            action_type: Optional filter by action type

        Returns:
            List of activity log entries
        """
        try:
            query = self.supabase.table(self.table_name).select("*")

            if category:
                query = query.eq("category", category)
            if action_type:
                query = query.eq("action_type", action_type)

            result = query.order("created_at", desc=True).limit(limit).execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to get activities: {e}")
            return []

    def get_activity_summary(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get a summary of activities over the past N days.

        Args:
            days: Number of days to summarize

        Returns:
            Summary dict with counts by category and type
        """
        try:
            # Get all recent activities
            activities = self.get_recent_activities(limit=1000)

            # Filter by date
            from datetime import timedelta
            cutoff = datetime.now() - timedelta(days=days)

            recent = []
            for activity in activities:
                created_at = activity.get("created_at", "")
                try:
                    activity_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    if activity_date.replace(tzinfo=None) >= cutoff:
                        recent.append(activity)
                except:
                    continue

            # Count by category
            by_category = {}
            by_type = {}
            by_status = {}

            for activity in recent:
                cat = activity.get("category", "unknown")
                by_category[cat] = by_category.get(cat, 0) + 1

                action = activity.get("action_type", "unknown")
                by_type[action] = by_type.get(action, 0) + 1

                status = activity.get("status", "unknown")
                by_status[status] = by_status.get(status, 0) + 1

            return {
                "total_activities": len(recent),
                "days": days,
                "by_category": by_category,
                "by_type": by_type,
                "by_status": by_status
            }

        except Exception as e:
            logger.error(f"Failed to get activity summary: {e}")
            return {
                "total_activities": 0,
                "error": str(e)
            }

    def clear_old_logs(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """
        Clear activity logs older than specified days.

        Args:
            days_to_keep: Number of days of logs to keep

        Returns:
            Result dict with deletion count
        """
        try:
            from datetime import timedelta
            cutoff = datetime.now() - timedelta(days=days_to_keep)
            cutoff_str = cutoff.isoformat()

            result = self.supabase.table(self.table_name) \
                .delete() \
                .lt("created_at", cutoff_str) \
                .execute()

            deleted_count = len(result.data) if result.data else 0

            return {
                "success": True,
                "deleted_count": deleted_count,
                "cutoff_date": cutoff_str
            }

        except Exception as e:
            logger.error(f"Failed to clear old logs: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
_activity_log_service = None


def get_activity_log_service() -> ActivityLogService:
    """Get the singleton activity log service instance"""
    global _activity_log_service
    if _activity_log_service is None:
        _activity_log_service = ActivityLogService()
    return _activity_log_service
