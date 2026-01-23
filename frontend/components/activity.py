"""
Activity/Workflow Automation component for Misty AI Enterprise System
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
    """Render the activity and workflow automation interface"""

    st.title("Activity & Workflow Automation")
    st.caption("Monitor and manage automated business processes and AI agent activities")

    # Quick actions
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("▶️ New Workflow", use_container_width=True):
            st.toast("Opening workflow builder...")

    with col2:
        if st.button("⏸️ Pause All", use_container_width=True):
            st.toast("Pausing all active workflows...")

    with col3:
        if st.button("📊 View Logs", use_container_width=True):
            st.session_state['show_activity_logs'] = True
            st.rerun()

    with col4:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

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
    tab1, tab2, tab3, tab4 = st.tabs([
        "⚡ Activity Log",
        "🔄 Active Workflows",
        "📈 Performance",
        "⚙️ Workflow Builder"
    ])

    with tab1:
        render_activity_log(recent_activities if ACTIVITY_LOG_AVAILABLE else None)

    with tab2:
        render_active_workflows()

    with tab3:
        render_workflow_performance()

    with tab4:
        render_workflow_builder()


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


def render_active_workflows():
    """Display currently active workflows"""

    st.subheader("Active Workflow Configurations")

    workflows = [
        {
            'name': 'Inventory Sync',
            'description': 'Automatically sync inventory across all channels',
            'trigger': 'Every 15 minutes',
            'status': 'Active',
            'executions': 2847,
            'success_rate': '99.8%',
            'avg_duration': '2m 15s',
            'enabled': True
        },
        {
            'name': 'Customer Recommendations',
            'description': 'Generate personalized product recommendations',
            'trigger': 'Daily at 2:00 AM',
            'status': 'Active',
            'executions': 145,
            'success_rate': '98.6%',
            'avg_duration': '12m 34s',
            'enabled': True
        },
        {
            'name': 'Order Processing',
            'description': 'Automated order fulfillment and shipping',
            'trigger': 'On new order',
            'status': 'Active',
            'executions': 1245,
            'success_rate': '99.9%',
            'avg_duration': '1m 23s',
            'enabled': True
        },
        {
            'name': 'Fraud Detection',
            'description': 'Real-time transaction fraud analysis',
            'trigger': 'On payment',
            'status': 'Active',
            'executions': 1389,
            'success_rate': '100%',
            'avg_duration': '450ms',
            'enabled': True
        },
        {
            'name': 'Customer Sentiment',
            'description': 'Analyze customer feedback and reviews',
            'trigger': 'Every 6 hours',
            'status': 'Error',
            'executions': 67,
            'success_rate': '96.2%',
            'avg_duration': '5m 12s',
            'enabled': True
        },
        {
            'name': 'Supplier Price Monitor',
            'description': 'Track supplier price changes',
            'trigger': 'Daily at 8:00 AM',
            'status': 'Paused',
            'executions': 89,
            'success_rate': '99.1%',
            'avg_duration': '3m 45s',
            'enabled': False
        },
    ]

    for workflow in workflows:
        with st.expander(f"{'✅' if workflow['enabled'] else '⏸️'} {workflow['name']}", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**Description:** {workflow['description']}")
                st.write(f"**Trigger:** {workflow['trigger']}")
                st.write(f"**Status:** {workflow['status']}")

                col_metric1, col_metric2, col_metric3 = st.columns(3)
                with col_metric1:
                    st.metric("Executions", workflow['executions'])
                with col_metric2:
                    st.metric("Success Rate", workflow['success_rate'])
                with col_metric3:
                    st.metric("Avg Duration", workflow['avg_duration'])

            with col2:
                st.write("")  # Spacer
                if workflow['enabled']:
                    st.button("⏸️ Pause", key=f"pause_{workflow['name']}", use_container_width=True)
                else:
                    st.button("▶️ Resume", key=f"resume_{workflow['name']}", use_container_width=True)

                st.button("⚙️ Configure", key=f"config_{workflow['name']}", use_container_width=True)
                st.button("📊 View Logs", key=f"logs_{workflow['name']}", use_container_width=True)


def render_workflow_performance():
    """Display workflow performance metrics"""

    st.subheader("Workflow Performance Analytics")

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

        except Exception as e:
            st.warning(f"Could not load performance data: {e}")
            render_mock_performance()
    else:
        render_mock_performance()


def render_mock_performance():
    """Display mock performance data when real data is not available"""

    # Execution trend with mock data
    import random

    days = [(datetime.now() - timedelta(days=i)).strftime('%m/%d') for i in range(30, 0, -1)]
    executions = [random.randint(50, 200) for _ in range(30)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=days,
        y=executions,
        mode='lines+markers',
        name='Daily Activities',
        line=dict(color='#6366F1', width=2),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.1)'
    ))

    fig.update_layout(
        title="Daily Activity Trend (Mock Data)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#F1F5F9',
        height=300,
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#334155', title='Activities')
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info("Real activity data will appear here once you start using the AI Reporting features.")


def render_workflow_builder():
    """Simple workflow builder interface"""

    st.subheader("Workflow Builder")
    st.caption("Create and configure automated workflows")

    workflow_name = st.text_input("Workflow Name", placeholder="e.g., Customer Birthday Email Campaign")

    workflow_description = st.text_area("Description", placeholder="Describe what this workflow does...")

    st.markdown("### Trigger Configuration")

    trigger_type = st.selectbox(
        "Trigger Type",
        ["Schedule", "Event", "Manual", "API Call"]
    )

    if trigger_type == "Schedule":
        col1, col2 = st.columns(2)
        with col1:
            schedule_type = st.selectbox("Schedule", ["Daily", "Weekly", "Monthly", "Custom Cron"])
        with col2:
            schedule_time = st.time_input("Time")

    elif trigger_type == "Event":
        event_type = st.selectbox(
            "Event",
            ["New Order", "Customer Signup", "Low Stock Alert", "Payment Received", "Review Posted"]
        )

    st.markdown("### Actions")

    num_actions = st.number_input("Number of Actions", min_value=1, max_value=10, value=1)

    for i in range(int(num_actions)):
        with st.expander(f"Action {i+1}", expanded=True):
            action_type = st.selectbox(
                "Action Type",
                ["Send Email", "Update Database", "Call API", "Run AI Model", "Send Notification", "Create Task"],
                key=f"action_type_{i}"
            )

            action_config = st.text_area(
                "Configuration (JSON)",
                placeholder='{"to": "customer@email.com", "template": "birthday_offer"}',
                key=f"action_config_{i}"
            )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Save Workflow", use_container_width=True, type="primary"):
            st.success("Workflow saved successfully!")

    with col2:
        if st.button("Test Run", use_container_width=True):
            st.info("Running test execution...")

    with col3:
        if st.button("Cancel", use_container_width=True):
            st.warning("Cancelled")
