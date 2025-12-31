"""
Analytics component for Misty AI Enterprise System
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

from utils.db_analytics import AnalyticsConnector

def render_analytics():
    """Render comprehensive analytics dashboards with REAL data from Supabase"""

    st.title("Analytics & Insights")
    st.caption("Real-time business intelligence from your Supabase database")

    # Initialize analytics connector
    try:
        analytics = AnalyticsConnector()
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        st.info("Make sure your .env file has SUPABASE_URL and SUPABASE_SECRET_KEY set correctly.")
        return

    # Refresh button
    col1, col2, col3 = st.columns([4, 1, 1])

    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.markdown("---")

    # Key metrics - REAL DATA
    col1, col2, col3, col4 = st.columns(4)

    total_revenue = analytics.get_total_revenue()
    total_orders = analytics.get_total_orders()
    total_customers = analytics.get_total_customers()
    avg_order_value = analytics.get_average_order_value()

    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.2f}")

    with col2:
        st.metric("Total Orders", f"{total_orders:,}")

    with col3:
        st.metric("Avg Order Value", f"${avg_order_value:,.2f}")

    with col4:
        st.metric("Total Customers", f"{total_customers:,}")

    st.markdown("---")

    # Tabs for different analytics views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Sales Trends",
        "👥 Customer Insights",
        "📦 Inventory Analysis",
        "🎵 Genre Performance",
    ])

    with tab1:
        render_sales_trends(analytics)

    with tab2:
        render_customer_insights(analytics)

    with tab3:
        render_inventory_analysis(analytics)

    with tab4:
        render_genre_performance(analytics)


def render_sales_trends(analytics: AnalyticsConnector):
    """Sales trends visualization - REAL DATA"""

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue by Order Date")

        # Get real daily revenue data
        daily_data = analytics.get_orders_by_date()

        if not daily_data.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_data['date'],
                y=daily_data['revenue'],
                mode='lines+markers',
                name='Revenue',
                line=dict(color='#6366F1', width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(99, 102, 241, 0.1)',
                text=[f"${r:,.2f}" for r in daily_data['revenue']],
                hovertemplate='<b>%{x}</b><br>Revenue: %{text}<extra></extra>'
            ))

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F1F5F9',
                height=300,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=False, title='Date'),
                yaxis=dict(showgrid=True, gridcolor='#334155', title='Revenue ($)')
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data available yet")

    with col2:
        st.subheader("Payment Methods Distribution")

        # Get real payment method data
        payment_data = analytics.get_payment_method_distribution()

        if not payment_data.empty:
            fig = go.Figure(data=[go.Pie(
                labels=payment_data['payment_method'],
                values=payment_data['count'],
                hole=0.4,
                marker=dict(colors=['#6366F1', '#8B5CF6', '#3B82F6', '#10B981']),
                text=[f"{m.title()}<br>${a:,.2f}" for m, a in zip(payment_data['payment_method'], payment_data['total_amount'])],
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br><extra></extra>'
            )])

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F1F5F9',
                height=300,
                margin=dict(l=0, r=0, t=20, b=0)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No payment data available yet")

    # Top Selling Albums
    st.subheader("🏆 Top Selling Albums")

    top_albums = analytics.get_top_selling_albums(limit=10)

    if not top_albums.empty:
        fig = go.Figure(data=[go.Bar(
            x=top_albums['units_sold'],
            y=[f"{row['title'][:30]}... - {row['artist'][:20]}" if len(row['title']) > 30
               else f"{row['title']} - {row['artist'][:20]}"
               for _, row in top_albums.iterrows()],
            orientation='h',
            marker_color='#6366F1',
            text=[f"{units} units" for units in top_albums['units_sold']],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Units Sold: %{x}<br><extra></extra>'
        )])

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#F1F5F9',
            height=400,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=True, gridcolor='#334155', title='Units Sold'),
            yaxis=dict(showgrid=False)
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sales data available yet")


def render_customer_insights(analytics: AnalyticsConnector):
    """Customer analytics and segmentation - REAL DATA"""

    st.subheader("🎖️ Top Customers by Total Spending")

    top_customers = analytics.get_top_customers(limit=15)

    if not top_customers.empty:
        # Display as a nice table
        display_df = top_customers.copy()
        display_df['total_spent'] = display_df['total_spent'].apply(lambda x: f"${x:,.2f}")
        display_df = display_df.rename(columns={
            'name': 'Customer Name',
            'email': 'Email',
            'total_spent': 'Total Spent',
            'order_count': 'Orders'
        })

        st.dataframe(
            display_df[['Customer Name', 'Email', 'Total Spent', 'Orders']],
            use_container_width=True,
            hide_index=True
        )

        # Visualize top 10 customers
        st.subheader("Top 10 Customers Visualization")

        top_10 = top_customers.head(10)

        fig = go.Figure(data=[go.Bar(
            x=top_10['total_spent'],
            y=top_10['name'],
            orientation='h',
            marker_color='#8B5CF6',
            text=[f"${spent:,.2f}" for spent in top_10['total_spent']],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Total Spent: $%{x:,.2f}<br><extra></extra>'
        )])

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#F1F5F9',
            height=400,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=True, gridcolor='#334155', title='Total Spent ($)'),
            yaxis=dict(showgrid=False, autorange="reversed")
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No customer data available yet")

    # Customer engagement metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        total_customers = analytics.get_total_customers()
        st.metric("Total Customers", f"{total_customers:,}")

    with col2:
        avg_rating = analytics.get_average_rating()
        st.metric("Avg Customer Rating", f"{avg_rating:.2f} ⭐")

    with col3:
        review_count = analytics.get_review_count()
        st.metric("Total Reviews", f"{review_count:,}")


def render_inventory_analysis(analytics: AnalyticsConnector):
    """Inventory performance and turnover analysis - REAL DATA"""

    # Inventory summary metrics
    col1, col2, col3, col4 = st.columns(4)

    inventory_summary = analytics.get_inventory_summary()
    inventory_value = analytics.get_total_inventory_value()

    with col1:
        st.metric("Total Albums", f"{inventory_summary['total_items']:,}")

    with col2:
        st.metric("Optimal Stock", f"{inventory_summary['optimal_stock']:,}", delta="Good")

    with col3:
        st.metric("Low Stock", f"{inventory_summary['low_stock']:,}",
                 delta=f"-{inventory_summary['low_stock']}", delta_color="inverse")

    with col4:
        st.metric("Inventory Value", f"${inventory_value:,.2f}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Stock Levels Distribution")

        # Real stock status
        stock_status = {
            'Optimal Stock (>20)': inventory_summary['optimal_stock'],
            'Low Stock (1-20)': inventory_summary['low_stock'],
            'Out of Stock': inventory_summary['out_of_stock']
        }

        colors = ['#10B981', '#F59E0B', '#EF4444']

        fig = go.Figure(data=[go.Pie(
            labels=list(stock_status.keys()),
            values=list(stock_status.values()),
            hole=0.4,
            marker=dict(colors=colors),
            textinfo='label+value',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#F1F5F9',
            height=300,
            margin=dict(l=0, r=0, t=20, b=0)
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Label Performance")

        label_perf = analytics.get_label_performance()

        if not label_perf.empty:
            top_labels = label_perf.head(7)

            fig = go.Figure(data=[go.Bar(
                x=top_labels['label'],
                y=top_labels['revenue'],
                marker_color='#6366F1',
                text=[f"${r:,.0f}" for r in top_labels['revenue']],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<br><extra></extra>'
            )])

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F1F5F9',
                height=300,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#334155', title='Revenue ($)')
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No label data available")

    # Low stock items - REAL DATA
    st.subheader("⚠️ Low Stock Alerts (≤20 units)")

    low_stock_albums = analytics.get_low_stock_albums(threshold=20)

    if not low_stock_albums.empty:
        display_df = low_stock_albums.copy()
        display_df['price'] = display_df['price'].apply(lambda x: f"${x:,.2f}")
        display_df = display_df.rename(columns={
            'title': 'Album',
            'artist': 'Artist',
            'quantity': 'Stock',
            'price': 'Price'
        })

        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.success("All albums have sufficient stock! 🎉")


def render_ai_predictions(analytics: AnalyticsConnector):
    """AI-powered business consultation - Using Gemini API with Langsmith tracing"""

    st.subheader("🤖 AI Business Consultant")
    st.caption("Powered by Gemini API with Langsmith tracing")

    # Initialize AI consultant
    try:
        ai_consultant = AIBusinessConsultant()
    except Exception as e:
        st.error(f"Failed to initialize AI consultant: {e}")
        st.info("Make sure GEMINI_API_KEY and Langsmith credentials are set in .env")
        return

    # Consultation options
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        consultation_type = st.selectbox(
            "Consultation Focus",
            ["Overall Business Health", "Revenue Optimization", "Customer Strategy", "Inventory Management"],
            help="Choose what aspect of your business to analyze"
        )

    with col2:
        report_format = st.selectbox(
            "Report Style",
            ["Executive Summary", "Detailed Analysis", "Quick Insights"],
            help="Choose the depth and format of analysis"
        )

    with col3:
        if st.button("🎯 Generate Report", use_container_width=True, type="primary"):
            st.session_state.generate_ai_report = True

    st.markdown("---")

    # Map selections to focus areas
    focus_map = {
        "Overall Business Health": "overall",
        "Revenue Optimization": "revenue",
        "Customer Strategy": "customer",
        "Inventory Management": "inventory"
    }

    # Generate AI consultation report
    if st.session_state.get('generate_ai_report', False) or st.session_state.get('ai_report_cache'):

        with st.spinner("🧠 AI Consultant analyzing your business data..."):

            # Check cache first
            if not st.session_state.get('ai_report_cache') or st.session_state.get('generate_ai_report'):

                focus_area = focus_map[consultation_type]

                if report_format == "Quick Insights":
                    # Generate quick insights
                    insights = ai_consultant.generate_quick_insights(limit=5)
                    st.session_state.ai_report_cache = {
                        "type": "quick_insights",
                        "data": insights,
                        "timestamp": datetime.now()
                    }
                else:
                    # Generate full consultation report
                    result = ai_consultant.generate_consultation_report(focus_area=focus_area)
                    st.session_state.ai_report_cache = {
                        "type": "full_report",
                        "data": result,
                        "timestamp": datetime.now()
                    }

                st.session_state.generate_ai_report = False

        # Display the report
        cached_report = st.session_state.ai_report_cache

        if cached_report["type"] == "quick_insights":
            st.subheader("⚡ Quick Business Insights")
            st.caption(f"Generated at {cached_report['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

            insights = cached_report["data"]

            if insights:
                for i, insight in enumerate(insights, 1):
                    priority_colors = {
                        "High": "🔴",
                        "Medium": "🟡",
                        "Low": "🟢"
                    }

                    priority = insight.get('priority', 'Medium')
                    emoji = priority_colors.get(priority, "⚪")

                    with st.expander(f"{emoji} Insight #{i}: {insight.get('insight', 'N/A')}", expanded=(i == 1)):
                        st.markdown(f"**Priority:** {priority}")
                        st.markdown(f"**Action:** {insight.get('action', 'N/A')}")
                        st.markdown(f"**Expected Impact:** {insight.get('impact', 'N/A')}")
            else:
                st.warning("No insights generated. Try generating a full report.")

        elif cached_report["type"] == "full_report":
            result = cached_report["data"]

            if result["success"]:
                st.subheader(f"📊 {consultation_type} - Business Consultation Report")
                st.caption(f"Generated at {cached_report['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} | Model: {result['model']}")

                # Display the AI-generated consultation
                st.markdown(result["report"])

                # Add download button
                st.download_button(
                    label="📥 Download Report",
                    data=result["report"],
                    file_name=f"misty_consultation_{result['focus_area']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

            else:
                st.error(f"Failed to generate report: {result.get('error', 'Unknown error')}")

        # Clear cache button
        if st.button("🔄 Generate New Report", use_container_width=True):
            st.session_state.ai_report_cache = None
            st.session_state.generate_ai_report = True
            st.rerun()

    else:
        # Show instructions when no report is generated
        st.info("👆 Select your consultation focus and click **Generate Report** to get AI-powered business insights based on your Supabase data.")

        # Show preview of data being analyzed
        with st.expander("📋 Preview: Data Being Analyzed", expanded=False):
            st.markdown("""
            The AI consultant will analyze:
            - 💰 Financial metrics (revenue, orders, avg order value)
            - 👥 Customer data (top customers, ratings, reviews)
            - 📦 Inventory status (stock levels, low stock alerts)
            - 🎵 Product performance (top albums, genres, labels)
            - 💳 Payment analytics (methods, success rates)

            **Powered by:**
            - Gemini 
            - Langsmith (full traceability and monitoring)
            - Real-time Supabase data
            """)

    st.markdown("---")

    # Quick metrics snapshot
    st.subheader("📈 Current Business Snapshot")

    col1, col2, col3, col4 = st.columns(4)

    top_albums = analytics.get_top_selling_albums(limit=1)
    low_stock = analytics.get_low_stock_albums(threshold=10)
    top_customers = analytics.get_top_customers(limit=1)
    avg_rating = analytics.get_average_rating()

    with col1:
        if not top_albums.empty:
            st.metric("Best Seller", top_albums.iloc[0]['title'][:20] + "...",
                     f"{int(top_albums.iloc[0]['units_sold'])} units")

    with col2:
        st.metric("Low Stock Items", len(low_stock),
                 delta=f"-{len(low_stock)}" if len(low_stock) > 0 else "All good",
                 delta_color="inverse")

    with col3:
        if not top_customers.empty:
            st.metric("Top Customer", top_customers.iloc[0]['name'][:15],
                     f"${top_customers.iloc[0]['total_spent']:,.0f}")

    with col4:
        st.metric("Avg Rating", f"{avg_rating:.2f} ⭐",
                 "Excellent" if avg_rating >= 4.5 else "Good" if avg_rating >= 4.0 else "Needs Improvement")


def render_genre_performance(analytics: AnalyticsConnector):
    """Genre-specific performance analytics - REAL DATA"""

    st.subheader("🎵 Genre Performance Analysis")

    genre_data = analytics.get_genre_performance()

    if not genre_data.empty:
        # Summary metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Genres", len(genre_data))

        with col2:
            best_genre = genre_data.iloc[0]
            st.metric("Top Genre", best_genre['genre'], f"${best_genre['revenue']:,.0f}")

        with col3:
            total_units = genre_data['units_sold'].sum()
            st.metric("Total Units Sold", f"{total_units:,}")

        st.markdown("---")

        # Visualize genre performance
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Revenue by Genre")

            fig = go.Figure(data=[go.Bar(
                x=genre_data['genre'],
                y=genre_data['revenue'],
                marker_color='#6366F1',
                text=[f"${r:,.0f}" for r in genre_data['revenue']],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<br><extra></extra>'
            )])

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F1F5F9',
                height=400,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=False, tickangle=-45),
                yaxis=dict(showgrid=True, gridcolor='#334155', title='Revenue ($)')
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Units Sold by Genre")

            fig = go.Figure(data=[go.Pie(
                labels=genre_data['genre'],
                values=genre_data['units_sold'],
                hole=0.4,
                hovertemplate='<b>%{label}</b><br>Units: %{value}<br>%{percent}<extra></extra>'
            )])

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F1F5F9',
                height=400,
                margin=dict(l=0, r=0, t=20, b=0)
            )

            st.plotly_chart(fig, use_container_width=True)

        # Detailed table
        st.subheader("Detailed Genre Metrics")

        display_df = genre_data.copy()
        display_df['avg_price'] = display_df['revenue'] / display_df['units_sold']
        display_df['revenue'] = display_df['revenue'].apply(lambda x: f"${x:,.2f}")
        display_df['avg_price'] = display_df['avg_price'].apply(lambda x: f"${x:,.2f}")

        display_df = display_df.rename(columns={
            'genre': 'Genre',
            'units_sold': 'Units Sold',
            'revenue': 'Total Revenue',
            'avg_price': 'Avg Price'
        })

        st.dataframe(
            display_df[['Genre', 'Total Revenue', 'Units Sold', 'Avg Price']],
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No genre sales data available yet")
