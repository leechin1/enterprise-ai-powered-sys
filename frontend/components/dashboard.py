"""
Dashboard component for Misty AI Enterprise System
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

def render_dashboard():
    """Render the main dashboard with activity, analytics, and metrics"""

    st.title("Dashboard")

    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Processed (24h)",
            value="6,412",
            delta="↑ 4.3% vs. prior 24h"
        )

    with col2:
        st.metric(
            label="Failure Rate",
            value="0.18%",
            delta="↓ 0.06pp",
            delta_color="inverse"
        )

    with col3:
        st.metric(
            label="Avg. Latency",
            value="412 ms",
            delta="P95: 1.8s"
        )

    with col4:
        st.metric(
            label="Open Issues",
            value="12",
            delta="↓ 3 from yesterday",
            delta_color="inverse"
        )

    st.markdown("---")

    # Create two columns for main content
    left_col, right_col = st.columns([3, 2])

    with left_col:
        # Activity section
        st.subheader("Activity")
        st.caption("Latest automation executions across inventory, customer service, and analytics pipelines.")

        # Activity data
        activities = [
            {
                'date': '12-24-2024',
                'id': '#8721',
                'details': 'Processed new vinyl shipment inventory sync with 245 records.',
                'status': 'Complete'
            },
            {
                'date': '12-24-2024',
                'id': '#8722',
                'details': 'Generated personalized recommendations for 1,840 customers.',
                'status': 'Complete'
            },
            {
                'date': '12-24-2024',
                'id': '#8720',
                'details': 'System awaiting supplier API response for rare vinyl acquisition.',
                'status': 'Blocked'
            },
            {
                'date': '12-24-2024',
                'id': '#8719',
                'details': 'Failed customer sentiment analysis during peak hours.',
                'status': 'Error'
            },
            {
                'date': '12-23-2024',
                'id': '#8718',
                'details': 'Archived 340 customer interactions after quality review.',
                'status': 'Complete'
            },
            {
                'date': '12-23-2024',
                'id': '#8717',
                'details': 'AI-powered reorder suggestions generated for low stock items.',
                'status': 'Running'
            }
        ]

        # Render activity table
        for activity in activities:
            col_date, col_id, col_details, col_status = st.columns([1, 1, 3, 1])

            with col_date:
                st.text(activity['date'])

            with col_id:
                st.text(activity['id'])

            with col_details:
                st.text(activity['details'])

            with col_status:
                status_colors = {
                    'Complete': '🟢',
                    'Running': '🔵',
                    'Error': '🔴',
                    'Blocked': '🟠'
                }
                st.text(f"{status_colors.get(activity['status'], '⚪')} {activity['status']}")

    with right_col:
        # Analytics section
        st.subheader("Analytics")

        # Tabs for different analytics views
        tab1, tab2 = st.tabs(["Workforce Insights", "Customer Trends"])

        with tab1:
            st.caption("Last 60 days")

            # Generate sample data for bar chart
            weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6']
            values = [4200, 6100, 5400, 7200, 7600, 7900]

            fig = go.Figure(data=[
                go.Bar(
                    x=weeks,
                    y=values,
                    marker_color='#6366F1',
                    text=values,
                    textposition='outside'
                )
            ])

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F1F5F9',
                height=250,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#334155')
            )

            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.caption("Last 30 days")

            # Generate sample data for customer trends
            days = list(range(1, 31))
            customer_activity = [random.randint(150, 350) for _ in range(30)]

            fig = go.Figure(data=[
                go.Scatter(
                    x=days,
                    y=customer_activity,
                    mode='lines',
                    fill='tozeroy',
                    line=dict(color='#8B5CF6', width=2),
                    fillcolor='rgba(139, 92, 246, 0.2)'
                )
            ])

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F1F5F9',
                height=250,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=False, title='Day'),
                yaxis=dict(showgrid=True, gridcolor='#334155', title='Active Customers')
            )

            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Improve section (Issues)
    st.subheader("Improve")

    col_issues, col_button = st.columns([4, 1])
    with col_issues:
        st.caption("Closed Issues")
    with col_button:
        if st.button("Open Issues", use_container_width=True):
            st.session_state.page = 'cases'
            st.rerun()

    # Issues table
    issues_df = pd.DataFrame([
        {'ID': '#445', 'Title': 'Webhook retries failing', 'Owner': 'System', 'Closed': '12-23-2024', 'Tags': 'integration'},
        {'ID': '#442', 'Title': 'Vinyl condition AI classifier accuracy', 'Owner': 'ML Team', 'Closed': '12-22-2024', 'Tags': 'ml-model'},
        {'ID': '#438', 'Title': 'Customer recommendation latency', 'Owner': 'Backend', 'Closed': '12-20-2024', 'Tags': 'performance'},
        {'ID': '#435', 'Title': 'Stock prediction model drift', 'Owner': 'Data Ops', 'Closed': '12-18-2024', 'Tags': 'monitoring'},
    ])

    st.dataframe(
        issues_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'ID': st.column_config.TextColumn('ID', width='small'),
            'Title': st.column_config.TextColumn('Title', width='large'),
            'Owner': st.column_config.TextColumn('Owner', width='medium'),
            'Closed': st.column_config.TextColumn('Closed', width='medium'),
            'Tags': st.column_config.TextColumn('Tags', width='medium')
        }
    )
