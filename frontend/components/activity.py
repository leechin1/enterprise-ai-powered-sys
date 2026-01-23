"""
Activity Log component for Misty AI Enterprise System
Integrates with the activity log service for real activity tracking
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Try to import the activity log service
try:
    from services.activity_log_service import get_activity_log_service
    ACTIVITY_LOG_AVAILABLE = True
except Exception as e:
    ACTIVITY_LOG_AVAILABLE = False
    print(f"Activity log service not available: {e}")


def render_activity():
    """Render the activity log interface"""

    st.title("Activity Log")
    st.caption("Track all AI agent activities, fix approvals, and email communications")

    # Quick actions
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("🗑️ Clear Old Logs", use_container_width=True):
            if ACTIVITY_LOG_AVAILABLE:
                try:
                    activity_service = get_activity_log_service()
                    result = activity_service.clear_old_logs(days_to_keep=30)
                    if result.get('success'):
                        st.success(f"Cleared {result.get('deleted_count', 0)} old log entries")
                    else:
                        st.error(f"Failed to clear logs: {result.get('error')}")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")

    # Get real activity summary if available
    if ACTIVITY_LOG_AVAILABLE:
        try:
            activity_service = get_activity_log_service()
            summary = activity_service.get_activity_summary(days=7)
            recent_activities = activity_service.get_recent_activities(limit=50)

            # Calculate metrics from real data
            total_activities = summary.get('total_activities', 0)
            success_count = summary.get('by_status', {}).get('success', 0)
            failed_count = summary.get('by_status', {}).get('failed', 0)
            success_rate = (success_count / total_activities * 100) if total_activities > 0 else 100

            # Count by category
            fixes_count = summary.get('by_category', {}).get('fixes', 0)
            emails_count = summary.get('by_type', {}).get('email_sent', 0)
            issues_count = summary.get('by_type', {}).get('issue_identified', 0)
        except Exception as e:
            st.warning(f"Could not load activity data: {e}")
            total_activities = 0
            success_rate = 100
            fixes_count = 0
            emails_count = 0
            issues_count = 0
            recent_activities = []
    else:
        total_activities = 0
        success_rate = 100
        fixes_count = 0
        emails_count = 0
        issues_count = 0
        recent_activities = []

    # Metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Activities (7d)", f"{total_activities:,}", "")

    with col2:
        st.metric("Success Rate", f"{success_rate:.1f}%", "")

    with col3:
        st.metric("Fixes Processed", f"{fixes_count:,}", "")

    with col4:
        st.metric("Emails Sent", f"{emails_count:,}", "")

    with col5:
        st.metric("Issues Found", f"{issues_count:,}", "")

    st.markdown("---")

    # Tabs
    tab1, tab2 = st.tabs([
        "⚡ Activity Log",
        "📈 Performance"
    ])

    with tab1:
        render_activity_log(recent_activities if ACTIVITY_LOG_AVAILABLE else None)

    with tab2:
        render_performance()


def render_activity_log(activities=None):
    """Display real activity logs from the database"""

    st.subheader("Activity Log")
    st.caption("Real-time tracking of all system activities")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All", "ai_reporting", "email", "issues", "fixes", "knowledge", "analytics", "system"]
        )

    with col2:
        status_filter = st.multiselect(
            "Status",
            ["success", "failed", "pending", "declined"],
            default=["success", "failed", "pending", "declined"]
        )

    with col3:
        time_range = st.selectbox(
            "Time Range",
            ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"]
        )

    # Get activities from database
    if ACTIVITY_LOG_AVAILABLE and activities is None:
        try:
            activity_service = get_activity_log_service()
            activities = activity_service.get_recent_activities(
                limit=100,
                category=category_filter if category_filter != "All" else None
            )
        except Exception as e:
            st.error(f"Failed to load activities: {e}")
            activities = []

    if not activities:
        st.info("No activities recorded yet. Activities will appear here as you use the system.")

        # Show example of what will appear
        with st.expander("What gets logged?", expanded=False):
            st.markdown("""
            The activity log tracks:
            - **Fixes Proposed**: When AI generates fix proposals
            - **Fixes Approved/Declined**: When you approve or decline fixes
            - **Emails Sent**: When emails are sent (in placebo mode, to your email)
            - **Issues Identified**: When business issues are detected
            - **SQL Queries**: When analysis queries are generated and executed
            - **Knowledge Queries**: When RAG system is queried
            - **Health Analysis**: When business health reports are generated
            """)
        return

    # Filter activities
    filtered_activities = []
    for activity in activities:
        # Apply category filter
        if category_filter != "All" and activity.get('category') != category_filter:
            continue
        # Apply status filter
        if activity.get('status') not in status_filter:
            continue
        filtered_activities.append(activity)

    # Display activity count
    st.caption(f"Showing {len(filtered_activities)} activities")

    # Display activity cards
    for activity in filtered_activities:
        display_activity_card(activity)


def display_activity_card(activity: dict):
    """Display a single activity as a card"""

    action_type = activity.get('action_type', 'unknown')
    status = activity.get('status', 'unknown')
    category = activity.get('category', 'system')
    description = activity.get('description', 'No description')
    created_at = activity.get('created_at', '')
    metadata = activity.get('metadata', {})

    # Format timestamp
    try:
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        time_ago = get_time_ago(dt)
        formatted_time = dt.strftime('%b %d, %Y %I:%M %p')
    except:
        time_ago = 'Unknown'
        formatted_time = created_at

    # Icons and colors based on type
    type_icons = {
        'fix_proposed': '🔧',
        'fix_approved': '✅',
        'fix_declined': '❌',
        'email_sent': '📧',
        'email_failed': '📧',
        'issue_identified': '⚠️',
        'sql_generated': '📝',
        'sql_executed': '⚙️',
        'health_analysis': '📊',
        'document_indexed': '📄',
        'rag_query': '🔍',
        'system_event': '🔔'
    }

    status_colors = {
        'success': ('🟢', 'rgba(16, 185, 129, 0.1)'),
        'failed': ('🔴', 'rgba(239, 68, 68, 0.1)'),
        'pending': ('🟡', 'rgba(245, 158, 11, 0.1)'),
        'declined': ('🟠', 'rgba(251, 146, 60, 0.1)'),
        'partial': ('🟡', 'rgba(245, 158, 11, 0.1)')
    }

    category_labels = {
        'ai_reporting': 'AI Reporting',
        'email': 'Email',
        'issues': 'Issues',
        'fixes': 'Fixes',
        'knowledge': 'Knowledge',
        'analytics': 'Analytics',
        'system': 'System'
    }

    icon = type_icons.get(action_type, '📋')
    status_icon, bg_color = status_colors.get(status, ('⚪', 'rgba(148, 163, 184, 0.1)'))
    category_label = category_labels.get(category, category.title())

    # Build metadata string
    metadata_str = ""
    if metadata:
        if 'emails_sent' in metadata:
            metadata_str += f" | 📧 {metadata['emails_sent']} emails"
        if 'recipients_count' in metadata:
            metadata_str += f" | 👥 {metadata['recipients_count']} recipients"
        if 'query_count' in metadata:
            metadata_str += f" | 📝 {metadata['query_count']} queries"
        if 'model' in metadata:
            metadata_str += f" | 🤖 {metadata['model']}"

    st.markdown(
        f"""
        <div style="{bg_color}; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid {'#10B981' if status == 'success' else '#EF4444' if status == 'failed' else '#F59E0B'};">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="flex: 1;">
                    <strong>{icon} {action_type.replace('_', ' ').title()}</strong>
                    <span style="color: #64748B; font-size: 0.85em;"> • {category_label}</span><br/>
                    <span style="color: #CBD5E1;">{description}</span><br/>
                    <small style="color: #64748B;">🕒 {time_ago} ({formatted_time}){metadata_str}</small>
                </div>
                <div style="text-align: right; min-width: 80px;">
                    <span>{status_icon} {status.title()}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def get_time_ago(dt: datetime) -> str:
    """Get human-readable time ago string"""
    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
    diff = now - dt

    if diff.total_seconds() < 60:
        return "Just now"
    elif diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} min ago"
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    else:
        return dt.strftime('%b %d')


def render_performance():
    """Display activity performance metrics"""

    st.subheader("Activity Performance Analytics")

    # Get real data if available
    if ACTIVITY_LOG_AVAILABLE:
        try:
            activity_service = get_activity_log_service()
            summary = activity_service.get_activity_summary(days=30)

            # Build chart from real data
            by_type = summary.get('by_type', {})

            if by_type:
                # Activity types chart
                types = list(by_type.keys())
                counts = list(by_type.values())

                fig = go.Figure(data=[go.Bar(
                    x=types,
                    y=counts,
                    marker_color='#6366F1',
                    text=counts,
                    textposition='outside'
                )])

                fig.update_layout(
                    title="Activities by Type (Last 30 Days)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#F1F5F9',
                    height=300,
                    margin=dict(l=0, r=0, t=40, b=0),
                    xaxis=dict(showgrid=False, tickangle=45),
                    yaxis=dict(showgrid=True, gridcolor='#334155', title='Count')
                )

                st.plotly_chart(fig, use_container_width=True)

            # Status distribution
            by_status = summary.get('by_status', {})
            if by_status:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### Status Distribution")

                    statuses = list(by_status.keys())
                    status_counts = list(by_status.values())
                    colors = ['#10B981' if s == 'success' else '#EF4444' if s == 'failed' else '#F59E0B' for s in statuses]

                    fig = go.Figure(data=[go.Pie(
                        labels=statuses,
                        values=status_counts,
                        marker_colors=colors,
                        hole=0.4
                    )])

                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#F1F5F9',
                        height=300,
                        margin=dict(l=0, r=0, t=20, b=0),
                        showlegend=True
                    )

                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.markdown("### Category Distribution")

                    by_category = summary.get('by_category', {})
                    if by_category:
                        categories = list(by_category.keys())
                        cat_counts = list(by_category.values())

                        fig = go.Figure(data=[go.Bar(
                            y=categories,
                            x=cat_counts,
                            orientation='h',
                            marker_color='#8B5CF6',
                            text=cat_counts,
                            textposition='outside'
                        )])

                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='#F1F5F9',
                            height=300,
                            margin=dict(l=0, r=0, t=20, b=0),
                            xaxis=dict(showgrid=True, gridcolor='#334155'),
                            yaxis=dict(showgrid=False)
                        )

                        st.plotly_chart(fig, use_container_width=True)

            if not by_type and not by_status:
                st.info("No activity data available yet. Start using the AI Reporting features to see performance metrics.")

        except Exception as e:
            st.warning(f"Could not load performance data: {e}")
            st.info("Real activity data will appear here once you start using the AI Reporting features.")
    else:
        st.info("Activity log service not available. Please check your Supabase configuration.")
