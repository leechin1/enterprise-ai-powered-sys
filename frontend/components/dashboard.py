"""
Dashboard component for Misty AI Enterprise System
Real-time overview with database insights and recent activity
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import services
try:
    from utils.db_analytics import AnalyticsConnector
    ANALYTICS_AVAILABLE = True
except Exception as e:
    ANALYTICS_AVAILABLE = False
    print(f"Analytics connector not available: {e}")

try:
    from services.activity_log_service import get_activity_log_service
    ACTIVITY_LOG_AVAILABLE = True
except Exception as e:
    ACTIVITY_LOG_AVAILABLE = False
    print(f"Activity log service not available: {e}")


def render_dashboard():
    """Render the main dashboard with real data from the database"""

    st.title("Dashboard")
    st.caption("Real-time overview of Misty Jazz Records enterprise system")

    # Initialize analytics connector
    analytics = None
    if ANALYTICS_AVAILABLE:
        try:
            analytics = AnalyticsConnector()
        except Exception as e:
            st.warning(f"Could not connect to database: {e}")

    # Top metrics row - Real data
    render_top_metrics(analytics)

    st.markdown("---")

    # Create two columns for main content
    left_col, right_col = st.columns([3, 2])

    with left_col:
        render_recent_activity()

    with right_col:
        render_analytics_charts(analytics)

    st.markdown("---")

    # Database overview section
    render_database_overview(analytics)


def render_top_metrics(analytics):
    """Render top metrics row with real database data"""

    col1, col2, col3, col4, col5 = st.columns(5)

    if analytics:
        try:
            # Get real metrics
            total_revenue = analytics.get_total_revenue()
            total_orders = analytics.get_total_orders()
            total_customers = analytics.get_total_customers()
            avg_order_value = analytics.get_average_order_value()
            avg_rating = analytics.get_average_rating()

            with col1:
                st.metric(
                    label="Total Revenue",
                    value=f"${total_revenue:,.2f}",
                    delta="All time"
                )

            with col2:
                st.metric(
                    label="Total Orders",
                    value=f"{total_orders:,}",
                    delta="All time"
                )

            with col3:
                st.metric(
                    label="Customers",
                    value=f"{total_customers:,}",
                    delta="Registered"
                )

            with col4:
                st.metric(
                    label="Avg Order Value",
                    value=f"${avg_order_value:.2f}",
                    delta="Per order"
                )

            with col5:
                st.metric(
                    label="Avg Rating",
                    value=f"{avg_rating:.1f} ⭐",
                    delta="All reviews"
                )

        except Exception as e:
            st.error(f"Error loading metrics: {e}")
    else:
        # Fallback display
        with col1:
            st.metric("Total Revenue", "—", "No data")
        with col2:
            st.metric("Total Orders", "—", "No data")
        with col3:
            st.metric("Customers", "—", "No data")
        with col4:
            st.metric("Avg Order Value", "—", "No data")
        with col5:
            st.metric("Avg Rating", "—", "No data")


def render_recent_activity():
    """Render recent activity from the activity logs table"""

    st.subheader("Recent Activity")
    st.caption("Latest actions from AI reporting, email campaigns, and system events")

    if ACTIVITY_LOG_AVAILABLE:
        try:
            activity_service = get_activity_log_service()
            activities = activity_service.get_recent_activities(limit=10)

            if activities:
                for activity in activities:
                    render_activity_row(activity)
            else:
                st.info("No recent activity. Actions will appear here as you use the system features.")

                # Show what gets logged
                with st.expander("What gets logged?", expanded=False):
                    st.markdown("""
                    - **Health Analysis**: When AI generates business health reports
                    - **SQL Queries**: When analysis queries are generated and executed
                    - **Issues Identified**: When business issues are detected
                    - **Fixes Proposed/Approved/Declined**: When AI generates fix proposals
                    - **Emails Sent**: Marketing campaigns and review responses
                    - **Knowledge Queries**: When RAG system is queried
                    """)

        except Exception as e:
            st.warning(f"Could not load activity data: {e}")
            st.info("Activity logs will appear here once the activity_logs table is created.")
    else:
        st.info("Activity logging not available. Please check your Supabase configuration.")


def render_activity_row(activity: dict):
    """Render a single activity row"""

    action_type = activity.get('action_type', 'unknown')
    status = activity.get('status', 'unknown')
    description = activity.get('description', 'No description')
    created_at = activity.get('created_at', '')
    category = activity.get('category', 'system')

    # Format timestamp
    try:
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        time_str = dt.strftime('%m-%d %H:%M')
    except:
        time_str = 'Unknown'

    # Icons based on type
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

    status_icons = {
        'success': '🟢',
        'failed': '🔴',
        'pending': '🟡',
        'declined': '🟠'
    }

    icon = type_icons.get(action_type, '📋')
    status_icon = status_icons.get(status, '⚪')

    # Create columns for the row
    col_time, col_icon, col_desc, col_status = st.columns([1, 0.5, 4, 1])

    with col_time:
        st.caption(time_str)

    with col_icon:
        st.write(icon)

    with col_desc:
        st.caption(description[:80] + '...' if len(description) > 80 else description)

    with col_status:
        st.caption(f"{status_icon} {status.title()}")


def render_analytics_charts(analytics):
    """Render analytics charts with real data"""

    st.subheader("Analytics")

    # Tabs for different analytics views
    tab1, tab2 = st.tabs(["📊 Revenue by Genre", "⭐ Rating Distribution"])

    with tab1:
        if analytics:
            try:
                genre_df = analytics.get_genre_performance()

                if not genre_df.empty:
                    st.caption("Sales performance by genre")

                    fig = go.Figure(data=[
                        go.Bar(
                            x=genre_df['genre'].head(8),
                            y=genre_df['revenue'].head(8),
                            marker_color='#6366F1',
                            text=[f"${v:,.0f}" for v in genre_df['revenue'].head(8)],
                            textposition='outside'
                        )
                    ])

                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#F1F5F9',
                        height=250,
                        margin=dict(l=0, r=0, t=20, b=0),
                        xaxis=dict(showgrid=False, tickangle=45),
                        yaxis=dict(showgrid=True, gridcolor='#334155')
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No genre sales data available yet.")

            except Exception as e:
                st.warning(f"Could not load genre data: {e}")
        else:
            st.info("Connect to database to see analytics.")

    with tab2:
        if analytics:
            try:
                rating_df = analytics.get_rating_distribution()

                if not rating_df.empty:
                    st.caption("Customer review distribution")

                    colors = ['#EF4444', '#F97316', '#F59E0B', '#84CC16', '#10B981']

                    fig = go.Figure(data=[
                        go.Bar(
                            x=[f"{r} ⭐" for r in rating_df['rating']],
                            y=rating_df['count'],
                            marker_color=colors,
                            text=rating_df['count'],
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
                else:
                    st.info("No review data available yet.")

            except Exception as e:
                st.warning(f"Could not load rating data: {e}")
        else:
            st.info("Connect to database to see analytics.")


def render_database_overview(analytics):
    """Render database overview with table counts and inventory insights"""

    st.subheader("Database Overview")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Table Statistics**")

        if analytics:
            try:
                tables = analytics.get_available_tables()
                table_data = []

                for table in tables:
                    count = analytics.get_table_count(table)
                    table_data.append({
                        'Table': table.replace('_', ' ').title(),
                        'Records': f"{count:,}"
                    })

                table_df = pd.DataFrame(table_data)
                st.dataframe(
                    table_df,
                    use_container_width=True,
                    hide_index=True,
                    height=300
                )

            except Exception as e:
                st.warning(f"Could not load table stats: {e}")
        else:
            st.info("Connect to database to see table statistics.")

    with col_right:
        st.markdown("**Inventory Status**")

        if analytics:
            try:
                inventory = analytics.get_inventory_summary()

                if inventory:
                    # Create inventory status cards
                    inv_col1, inv_col2 = st.columns(2)

                    with inv_col1:
                        st.metric("Total Items", f"{inventory.get('total_items', 0):,}")
                        st.metric("Optimal Stock", f"{inventory.get('optimal_stock', 0):,}", delta="20+ units")

                    with inv_col2:
                        st.metric("Low Stock", f"{inventory.get('low_stock', 0):,}", delta="1-20 units", delta_color="inverse")
                        st.metric("Out of Stock", f"{inventory.get('out_of_stock', 0):,}", delta="0 units", delta_color="inverse")

                    # Show low stock items if any
                    if inventory.get('low_stock', 0) > 0 or inventory.get('out_of_stock', 0) > 0:
                        with st.expander("View Low Stock Items"):
                            low_stock_df = analytics.get_low_stock_albums(threshold=20)
                            if not low_stock_df.empty:
                                st.dataframe(
                                    low_stock_df[['title', 'artist', 'quantity']].head(10),
                                    use_container_width=True,
                                    hide_index=True
                                )
                else:
                    st.info("No inventory data available.")

            except Exception as e:
                st.warning(f"Could not load inventory data: {e}")
        else:
            st.info("Connect to database to see inventory status.")

    # Top selling albums section
    st.markdown("---")

    col_albums, col_customers = st.columns(2)

    with col_albums:
        st.markdown("**Top Selling Albums**")

        if analytics:
            try:
                top_albums = analytics.get_top_selling_albums(limit=5)

                if not top_albums.empty:
                    display_df = top_albums[['title', 'artist', 'units_sold', 'revenue']].copy()
                    display_df['revenue'] = display_df['revenue'].apply(lambda x: f"${x:,.2f}")
                    display_df.columns = ['Title', 'Artist', 'Units', 'Revenue']

                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No sales data available yet.")

            except Exception as e:
                st.warning(f"Could not load album data: {e}")
        else:
            st.info("Connect to database to see top albums.")

    with col_customers:
        st.markdown("**Top Customers**")

        if analytics:
            try:
                top_customers = analytics.get_top_customers(limit=5)

                if not top_customers.empty:
                    display_df = top_customers[['name', 'total_spent', 'order_count']].copy()
                    display_df['total_spent'] = display_df['total_spent'].apply(lambda x: f"${x:,.2f}")
                    display_df.columns = ['Customer', 'Total Spent', 'Orders']

                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No customer data available yet.")

            except Exception as e:
                st.warning(f"Could not load customer data: {e}")
        else:
            st.info("Connect to database to see top customers.")
