"""
Cases/Issues Management component for Misty AI Enterprise System
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

def render_cases():
    """Render the cases and issues management interface"""

    st.title("Cases & Customer Service")
    st.caption("AI-powered customer service management with automated ticket routing and sentiment analysis")

    # Quick stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Open Cases", "47", "↓ 8")

    with col2:
        st.metric("Avg Response Time", "2.3 hrs", "↓ 0.5 hrs")

    with col3:
        st.metric("Customer Satisfaction", "4.7/5.0", "↑ 0.2")

    with col4:
        st.metric("AI Auto-Resolved", "34%", "↑ 5%")

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Active Cases", "✅ Resolved Cases", "🤖 AI Insights"])

    with tab1:
        render_active_cases()

    with tab2:
        render_resolved_cases()

    with tab3:
        render_case_insights()


def render_active_cases():
    """Display active customer service cases"""

    # Filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        priority_filter = st.multiselect(
            "Priority",
            ["Critical", "High", "Medium", "Low"],
            default=["Critical", "High", "Medium", "Low"]
        )

    with col2:
        category_filter = st.selectbox(
            "Category",
            ["All", "Order Issue", "Product Question", "Return", "Technical", "General Inquiry"]
        )

    with col3:
        assignee_filter = st.selectbox(
            "Assigned To",
            ["All", "AI Agent", "Sarah M.", "James K.", "Unassigned"]
        )

    with col4:
        sort_by = st.selectbox(
            "Sort By",
            ["Date (Newest)", "Date (Oldest)", "Priority", "AI Score"]
        )

    # Sample cases data
    cases = [
        {
            'ID': '#CS-2847',
            'Customer': 'Marcus Johnson',
            'Subject': 'Wrong album shipped in order',
            'Category': 'Order Issue',
            'Priority': 'High',
            'Status': 'In Progress',
            'Assigned': 'Sarah M.',
            'Created': '2 hours ago',
            'AI Sentiment': 'Frustrated',
            'AI Score': 92,
            'AI Suggestion': 'Offer expedited replacement + 10% discount'
        },
        {
            'ID': '#CS-2846',
            'Customer': 'Emily Rodriguez',
            'Subject': 'Vinyl condition not as described',
            'Category': 'Return',
            'Priority': 'Medium',
            'Status': 'Pending',
            'Assigned': 'James K.',
            'Created': '5 hours ago',
            'AI Sentiment': 'Disappointed',
            'AI Score': 88,
            'AI Suggestion': 'Initiate return, offer store credit with 15% bonus'
        },
        {
            'ID': '#CS-2845',
            'Customer': 'David Chen',
            'Subject': 'Question about rare vinyl authenticity',
            'Category': 'Product Question',
            'Priority': 'Medium',
            'Status': 'Pending',
            'Assigned': 'AI Agent',
            'Created': '8 hours ago',
            'AI Sentiment': 'Curious',
            'AI Score': 76,
            'AI Suggestion': 'Provide certificate of authenticity, share provenance'
        },
        {
            'ID': '#CS-2844',
            'Customer': 'Sarah Williams',
            'Subject': 'Damaged package delivery',
            'Category': 'Order Issue',
            'Priority': 'Critical',
            'Status': 'In Progress',
            'Assigned': 'Sarah M.',
            'Created': '1 day ago',
            'AI Sentiment': 'Angry',
            'AI Score': 95,
            'AI Suggestion': 'Immediate replacement, refund shipping, apologize'
        },
    ]

    # Display cases as expandable cards
    for case in cases:
        with st.expander(f"{case['Priority']} - {case['ID']}: {case['Subject']}", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Customer:** {case['Customer']}")
                st.write(f"**Category:** {case['Category']}")
                st.write(f"**Status:** {case['Status']}")
                st.write(f"**Created:** {case['Created']}")

            with col2:
                st.write(f"**Assigned:** {case['Assigned']}")
                st.write(f"**Priority:** {case['Priority']}")
                st.metric("AI Score", case['AI Score'])

            st.markdown("---")

            st.write(f"**AI Sentiment Analysis:** {case['AI Sentiment']}")
            st.info(f"🤖 **AI Suggestion:** {case['AI Suggestion']}")

            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.button("💬 Reply", key=f"reply_{case['ID']}", use_container_width=True)
            with col2:
                st.button("✓ Resolve", key=f"resolve_{case['ID']}", use_container_width=True)
            with col3:
                st.button("↗️ Escalate", key=f"escalate_{case['ID']}", use_container_width=True)
            with col4:
                st.button("🤖 Auto-Handle", key=f"auto_{case['ID']}", use_container_width=True)


def render_resolved_cases():
    """Display resolved cases"""

    st.subheader("Recently Resolved Cases")

    resolved_cases = pd.DataFrame([
        {
            'ID': '#CS-2843',
            'Customer': 'John Smith',
            'Subject': 'Inquiry about jazz festival vinyl',
            'Resolution Time': '1.2 hrs',
            'Resolved By': 'AI Agent',
            'Satisfaction': '5/5',
            'Date': '12-24-2024'
        },
        {
            'ID': '#CS-2842',
            'Customer': 'Lisa Chen',
            'Subject': 'Order status question',
            'Resolution Time': '0.5 hrs',
            'Resolved By': 'AI Agent',
            'Satisfaction': '5/5',
            'Date': '12-24-2024'
        },
        {
            'ID': '#CS-2841',
            'Customer': 'Robert Taylor',
            'Subject': 'Return processed successfully',
            'Resolution Time': '24 hrs',
            'Resolved By': 'James K.',
            'Satisfaction': '4/5',
            'Date': '12-23-2024'
        },
        {
            'ID': '#CS-2840',
            'Customer': 'Maria Garcia',
            'Subject': 'Recommendation for bebop albums',
            'Resolution Time': '0.3 hrs',
            'Resolved By': 'AI Agent',
            'Satisfaction': '5/5',
            'Date': '12-23-2024'
        },
    ])

    st.dataframe(resolved_cases, use_container_width=True, hide_index=True)


def render_case_insights():
    """Display AI-powered insights about cases"""

    st.subheader("AI-Powered Case Analytics")

    # Common issues
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Top Issues This Week")

        issues_data = pd.DataFrame([
            {'Issue': 'Shipping delays', 'Count': 23, 'Trend': '↑ 15%'},
            {'Issue': 'Product questions', 'Count': 18, 'Trend': '→ 0%'},
            {'Issue': 'Return requests', 'Count': 12, 'Trend': '↓ 8%'},
            {'Issue': 'Vinyl condition', 'Count': 9, 'Trend': '↑ 12%'},
            {'Issue': 'Payment issues', 'Count': 5, 'Trend': '↓ 20%'},
        ])

        st.dataframe(issues_data, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("### Customer Sentiment Breakdown")

        sentiment_data = {
            'Happy': 145,
            'Neutral': 67,
            'Frustrated': 23,
            'Angry': 8
        }

        import plotly.graph_objects as go

        fig = go.Figure(data=[go.Pie(
            labels=list(sentiment_data.keys()),
            values=list(sentiment_data.values()),
            hole=0.4,
            marker=dict(colors=['#10B981', '#3B82F6', '#F59E0B', '#EF4444'])
        )])

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#F1F5F9',
            height=300,
            margin=dict(l=0, r=0, t=20, b=0)
        )

        st.plotly_chart(fig, use_container_width=True)

    # AI Recommendations
    st.markdown("### AI Process Recommendations")

    recommendations = [
        "📦 **Shipping Process:** 68% of shipping delay complaints occur on Mondays. Consider proactive notifications for weekend orders.",
        "📚 **Knowledge Base:** Create FAQ for top 5 product questions to enable 24/7 self-service (potential 40% ticket reduction).",
        "🎯 **Automation:** Return requests follow predictable patterns. AI can auto-approve 78% of cases with 95% confidence.",
        "⭐ **Customer Retention:** Customers with resolved issues within 4 hours show 23% higher lifetime value.",
    ]

    for rec in recommendations:
        st.info(rec)
