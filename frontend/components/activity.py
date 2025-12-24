"""
Activity/Workflow Automation component for Misty AI Enterprise System
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

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
            st.toast("Loading execution logs...")

    with col4:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    st.markdown("---")

    # Metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Active Workflows", "12", "")

    with col2:
        st.metric("Executions (24h)", "6,412", "↑ 4.3%")

    with col3:
        st.metric("Success Rate", "99.82%", "↑ 0.06%")

    with col4:
        st.metric("Avg Duration", "412 ms", "")

    with col5:
        st.metric("Tasks Automated", "847", "")

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "⚡ Recent Activity",
        "🔄 Active Workflows",
        "📈 Performance",
        "⚙️ Workflow Builder"
    ])

    with tab1:
        render_recent_activity()

    with tab2:
        render_active_workflows()

    with tab3:
        render_workflow_performance()

    with tab4:
        render_workflow_builder()


def render_recent_activity():
    """Display recent automation executions"""

    st.subheader("Recent Automation Executions")
    st.caption("Real-time activity across all automated workflows")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        workflow_filter = st.selectbox(
            "Filter by Workflow",
            ["All Workflows", "Inventory Sync", "Customer Recommendations", "Order Processing", "Fraud Detection", "Report Generation"]
        )

    with col2:
        status_filter = st.multiselect(
            "Status",
            ["Running", "Complete", "Error", "Blocked"],
            default=["Running", "Complete", "Error", "Blocked"]
        )

    with col3:
        time_range = st.selectbox(
            "Time Range",
            ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days"]
        )

    # Activity feed
    activities = [
        {
            'timestamp': '2 min ago',
            'workflow': 'Inventory Sync',
            'execution_id': '#8724',
            'description': 'Processing new vinyl shipment inventory sync with 245 records.',
            'status': 'Running',
            'duration': '45s',
            'progress': 67
        },
        {
            'timestamp': '5 min ago',
            'workflow': 'Customer Recommendations',
            'execution_id': '#8723',
            'description': 'Generated personalized recommendations for 1,840 customers.',
            'status': 'Complete',
            'duration': '3m 12s',
            'progress': 100
        },
        {
            'timestamp': '12 min ago',
            'workflow': 'Order Processing',
            'execution_id': '#8722',
            'description': 'Automated order fulfillment for 23 online purchases.',
            'status': 'Complete',
            'duration': '1m 34s',
            'progress': 100
        },
        {
            'timestamp': '18 min ago',
            'workflow': 'Fraud Detection',
            'execution_id': '#8721',
            'description': 'Completed fraud detection scan on 1,200 transaction records.',
            'status': 'Complete',
            'duration': '2m 45s',
            'progress': 100
        },
        {
            'timestamp': '25 min ago',
            'workflow': 'Supplier Integration',
            'execution_id': '#8720',
            'description': 'System awaiting supplier API response for rare vinyl acquisition.',
            'status': 'Blocked',
            'duration': '25m 12s',
            'progress': 45
        },
        {
            'timestamp': '1 hour ago',
            'workflow': 'Customer Sentiment',
            'execution_id': '#8719',
            'description': 'Failed customer sentiment analysis during peak hours.',
            'status': 'Error',
            'duration': '12s',
            'progress': 15
        },
        {
            'timestamp': '2 hours ago',
            'workflow': 'Data Archive',
            'execution_id': '#8718',
            'description': 'Archived 340 customer interactions after quality review.',
            'status': 'Complete',
            'duration': '8m 23s',
            'progress': 100
        },
        {
            'timestamp': '3 hours ago',
            'workflow': 'Reorder Suggestions',
            'execution_id': '#8717',
            'description': 'AI-powered reorder suggestions generated for 87 low stock items.',
            'status': 'Complete',
            'duration': '4m 56s',
            'progress': 100
        },
    ]

    # Display activity cards
    for activity in activities:
        if activity['status'] in status_filter:
            status_colors = {
                'Running': ('🔵', 'background-color: rgba(59, 130, 246, 0.1)'),
                'Complete': ('🟢', 'background-color: rgba(16, 185, 129, 0.1)'),
                'Error': ('🔴', 'background-color: rgba(239, 68, 68, 0.1)'),
                'Blocked': ('🟠', 'background-color: rgba(245, 158, 11, 0.1)')
            }

            icon, bg_color = status_colors[activity['status']]

            st.markdown(
                f"""
                <div style="{bg_color}; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{icon} {activity['workflow']}</strong> - {activity['execution_id']}<br/>
                            <span style="color: #94A3B8;">{activity['description']}</span><br/>
                            <small style="color: #64748B;">⏱️ {activity['duration']} • 🕒 {activity['timestamp']}</small>
                        </div>
                        <div style="text-align: right;">
                            <strong>{activity['status']}</strong>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if activity['status'] == 'Running':
                st.progress(activity['progress'] / 100)


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

    # Execution trend
    import plotly.graph_objects as go
    from datetime import datetime, timedelta

    days = [(datetime.now() - timedelta(days=i)).strftime('%m/%d') for i in range(30, 0, -1)]
    import random
    executions = [random.randint(5000, 8000) for _ in range(30)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=days,
        y=executions,
        mode='lines+markers',
        name='Daily Executions',
        line=dict(color='#6366F1', width=2),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.1)'
    ))

    fig.update_layout(
        title="Daily Workflow Executions (Last 30 Days)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#F1F5F9',
        height=300,
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#334155', title='Executions')
    )

    st.plotly_chart(fig, use_container_width=True)

    # Performance by workflow
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Success Rate by Workflow")

        workflows = ['Inventory Sync', 'Recommendations', 'Order Processing', 'Fraud Detection', 'Sentiment']
        success_rates = [99.8, 98.6, 99.9, 100, 96.2]

        fig = go.Figure(data=[go.Bar(
            y=workflows,
            x=success_rates,
            orientation='h',
            marker_color='#10B981',
            text=[f"{rate}%" for rate in success_rates],
            textposition='outside'
        )])

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#F1F5F9',
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=True, gridcolor='#334155', range=[95, 100.5]),
            yaxis=dict(showgrid=False)
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Average Execution Time")

        durations = [135, 754, 83, 0.45, 312]  # in seconds

        fig = go.Figure(data=[go.Bar(
            y=workflows,
            x=durations,
            orientation='h',
            marker_color='#6366F1',
            text=[f"{d}s" if d >= 1 else f"{int(d*1000)}ms" for d in durations],
            textposition='outside'
        )])

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#F1F5F9',
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=True, gridcolor='#334155', title='Seconds'),
            yaxis=dict(showgrid=False)
        )

        st.plotly_chart(fig, use_container_width=True)


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
        if st.button("💾 Save Workflow", use_container_width=True, type="primary"):
            st.success("Workflow saved successfully!")

    with col2:
        if st.button("▶️ Test Run", use_container_width=True):
            st.info("Running test execution...")

    with col3:
        if st.button("❌ Cancel", use_container_width=True):
            st.warning("Cancelled")
