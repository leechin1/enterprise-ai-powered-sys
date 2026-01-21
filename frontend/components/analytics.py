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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📈 Sales Trends",
        "👥 Customer Insights",
        "📦 Inventory Analysis",
        "🎵 Genre Performance",
        "🎤 Artist Performance",
        "⭐ Review Analytics",
        "💳 Payment Analytics",
        "🗄️ Table Viewer",
    ])

    with tab1:
        render_sales_trends(analytics)

    with tab2:
        render_customer_insights(analytics)

    with tab3:
        render_inventory_analysis(analytics)

    with tab4:
        render_genre_performance(analytics)

    with tab5:
        render_artist_performance(analytics)

    with tab6:
        render_review_analytics(analytics)

    with tab7:
        render_payment_analytics(analytics)

    with tab8:
        render_table_viewer(analytics)


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

    # Monthly trends and day-of-week analysis
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Monthly Revenue Trends")

        monthly_data = analytics.get_orders_by_month()

        if not monthly_data.empty:
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=monthly_data['month'],
                y=monthly_data['revenue'],
                marker_color='#6366F1',
                text=[f"${r:,.0f}" for r in monthly_data['revenue']],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<br><extra></extra>'
            ))

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F1F5F9',
                height=300,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=False, title='Month'),
                yaxis=dict(showgrid=True, gridcolor='#334155', title='Revenue ($)')
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No monthly data available")

    with col2:
        st.subheader("Sales by Day of Week")

        dow_data = analytics.get_orders_by_day_of_week()

        if not dow_data.empty:
            fig = go.Figure(data=[go.Bar(
                x=dow_data['day'],
                y=dow_data['order_count'],
                marker_color='#10B981',
                text=dow_data['order_count'],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Orders: %{y}<br><extra></extra>'
            )])

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F1F5F9',
                height=300,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=False, title='Day'),
                yaxis=dict(showgrid=True, gridcolor='#334155', title='Orders')
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No day-of-week data available")

    st.markdown("---")

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

    st.markdown("---")

    # Customer order frequency and growth
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer Order Frequency")

        order_freq = analytics.get_customer_order_frequency()

        if not order_freq.empty:
            fig = go.Figure(data=[go.Pie(
                labels=order_freq['frequency'],
                values=order_freq['customers'],
                hole=0.4,
                marker=dict(colors=['#6366F1', '#8B5CF6', '#3B82F6', '#10B981']),
                textinfo='label+value',
                hovertemplate='<b>%{label}</b><br>Customers: %{value}<br>%{percent}<extra></extra>'
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
            st.info("No order frequency data available")

    with col2:
        st.subheader("Customer Growth by Month")

        customer_growth = analytics.get_customers_by_registration_month()

        if not customer_growth.empty:
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=customer_growth['month'],
                y=customer_growth['new_customers'],
                marker_color='#8B5CF6',
                text=customer_growth['new_customers'],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>New Customers: %{y}<extra></extra>'
            ))

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F1F5F9',
                height=300,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=False, title='Month'),
                yaxis=dict(showgrid=True, gridcolor='#334155', title='New Customers')
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No customer growth data available")


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

    # Price distribution
    st.subheader("💰 Album Price Distribution")

    price_dist = analytics.get_price_distribution()

    if not price_dist.empty:
        fig = go.Figure(data=[go.Bar(
            x=price_dist['price_range'],
            y=price_dist['count'],
            marker_color=['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444'],
            text=price_dist['count'],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Albums: %{y}<extra></extra>'
        )])

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#F1F5F9',
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=False, title='Price Range'),
            yaxis=dict(showgrid=True, gridcolor='#334155', title='Number of Albums')
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No price data available")

    st.markdown("---")

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


def render_artist_performance(analytics: AnalyticsConnector):
    """Artist-specific performance analytics"""

    st.subheader("🎤 Artist Performance Analysis")

    artist_data = analytics.get_artist_performance(limit=15)

    if not artist_data.empty:
        # Summary metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Artists Sold", len(artist_data))

        with col2:
            top_artist = artist_data.iloc[0]
            st.metric("Top Artist", top_artist['artist'][:20], f"${top_artist['revenue']:,.0f}")

        with col3:
            total_units = artist_data['units_sold'].sum()
            st.metric("Total Units by Top 15", f"{total_units:,}")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Revenue by Artist")

            fig = go.Figure(data=[go.Bar(
                x=artist_data['revenue'],
                y=artist_data['artist'],
                orientation='h',
                marker_color='#8B5CF6',
                text=[f"${r:,.0f}" for r in artist_data['revenue']],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>'
            )])

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F1F5F9',
                height=500,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=True, gridcolor='#334155', title='Revenue ($)'),
                yaxis=dict(showgrid=False, autorange="reversed")
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Units Sold by Artist")

            fig = go.Figure(data=[go.Bar(
                x=artist_data['units_sold'],
                y=artist_data['artist'],
                orientation='h',
                marker_color='#10B981',
                text=[f"{u} units" for u in artist_data['units_sold']],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Units: %{x}<extra></extra>'
            )])

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F1F5F9',
                height=500,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=True, gridcolor='#334155', title='Units Sold'),
                yaxis=dict(showgrid=False, autorange="reversed")
            )

            st.plotly_chart(fig, use_container_width=True)

        # Artist performance table
        st.subheader("Detailed Artist Metrics")

        display_df = artist_data.copy()
        display_df['avg_price'] = display_df['revenue'] / display_df['units_sold']
        display_df['revenue'] = display_df['revenue'].apply(lambda x: f"${x:,.2f}")
        display_df['avg_price'] = display_df['avg_price'].apply(lambda x: f"${x:,.2f}")

        display_df = display_df.rename(columns={
            'artist': 'Artist',
            'units_sold': 'Units Sold',
            'revenue': 'Total Revenue',
            'order_count': 'Orders',
            'avg_price': 'Avg Sale Price'
        })

        st.dataframe(
            display_df[['Artist', 'Total Revenue', 'Units Sold', 'Orders', 'Avg Sale Price']],
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No artist sales data available yet")


def render_review_analytics(analytics: AnalyticsConnector):
    """Review and rating analytics"""

    st.subheader("⭐ Review & Rating Analytics")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    avg_rating = analytics.get_average_rating()
    review_count = analytics.get_review_count()
    rating_dist = analytics.get_rating_distribution()

    with col1:
        st.metric("Average Rating", f"{avg_rating:.2f} ⭐")

    with col2:
        st.metric("Total Reviews", f"{review_count:,}")

    with col3:
        if not rating_dist.empty:
            five_star = rating_dist[rating_dist['rating'] == 5]['count'].values
            five_star_count = five_star[0] if len(five_star) > 0 else 0
            st.metric("5-Star Reviews", f"{five_star_count:,}")

    with col4:
        if not rating_dist.empty:
            one_star = rating_dist[rating_dist['rating'] == 1]['count'].values
            one_star_count = one_star[0] if len(one_star) > 0 else 0
            st.metric("1-Star Reviews", f"{one_star_count:,}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Rating Distribution")

        if not rating_dist.empty:
            colors = ['#EF4444', '#F97316', '#F59E0B', '#84CC16', '#10B981']

            fig = go.Figure(data=[go.Bar(
                x=[f"{r} ⭐" for r in rating_dist['rating']],
                y=rating_dist['count'],
                marker_color=colors,
                text=rating_dist['count'],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
            )])

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F1F5F9',
                height=350,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=False, title='Rating'),
                yaxis=dict(showgrid=True, gridcolor='#334155', title='Count')
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No rating data available")

    with col2:
        st.subheader("Rating Breakdown")

        if not rating_dist.empty:
            fig = go.Figure(data=[go.Pie(
                labels=[f"{r} Stars" for r in rating_dist['rating']],
                values=rating_dist['count'],
                hole=0.4,
                marker=dict(colors=['#EF4444', '#F97316', '#F59E0B', '#84CC16', '#10B981']),
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
            )])

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F1F5F9',
                height=350,
                margin=dict(l=0, r=0, t=20, b=0)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No rating data available")

    # Top Rated Albums
    st.subheader("🏆 Top Rated Albums")

    top_rated = analytics.get_top_rated_albums(limit=10)

    if not top_rated.empty:
        fig = go.Figure(data=[go.Bar(
            x=top_rated['avg_rating'],
            y=[f"{row['title'][:25]}..." if len(row['title']) > 25 else row['title']
               for _, row in top_rated.iterrows()],
            orientation='h',
            marker_color='#F59E0B',
            text=[f"{r:.1f} ⭐ ({c} reviews)" for r, c in zip(top_rated['avg_rating'], top_rated['review_count'])],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Rating: %{x:.2f}<extra></extra>'
        )])

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#F1F5F9',
            height=400,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=True, gridcolor='#334155', title='Average Rating', range=[0, 5.5]),
            yaxis=dict(showgrid=False, autorange="reversed")
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No rated albums available (minimum 2 reviews required)")

    # Recent Reviews
    st.subheader("📝 Recent Reviews")

    recent_reviews = analytics.get_recent_reviews(limit=10)

    if not recent_reviews.empty:
        display_df = recent_reviews.copy()
        display_df['rating'] = display_df['rating'].apply(lambda x: '⭐' * x)
        display_df = display_df.rename(columns={
            'album': 'Album',
            'artist': 'Artist',
            'customer': 'Customer',
            'rating': 'Rating',
            'review': 'Review',
            'date': 'Date'
        })

        st.dataframe(
            display_df[['Album', 'Artist', 'Customer', 'Rating', 'Review']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No reviews available")


def render_payment_analytics(analytics: AnalyticsConnector):
    """Payment analytics and trends"""

    st.subheader("💳 Payment Analytics")

    # Payment method distribution (already exists in sales trends, but let's expand)
    payment_data = analytics.get_payment_method_distribution()
    payment_status = analytics.get_payment_status_distribution()

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    total_payments = payment_data['count'].sum() if not payment_data.empty else 0
    total_amount = payment_data['total_amount'].sum() if not payment_data.empty else 0

    with col1:
        st.metric("Total Payments", f"{total_payments:,}")

    with col2:
        st.metric("Total Amount", f"${total_amount:,.2f}")

    with col3:
        if not payment_status.empty:
            completed = payment_status[payment_status['status'] == 'completed']
            completed_count = completed['count'].values[0] if len(completed) > 0 else 0
            success_rate = (completed_count / total_payments * 100) if total_payments > 0 else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")

    with col4:
        avg_payment = total_amount / total_payments if total_payments > 0 else 0
        st.metric("Avg Payment", f"${avg_payment:,.2f}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Payment Methods")

        if not payment_data.empty:
            fig = go.Figure(data=[go.Bar(
                x=payment_data['payment_method'],
                y=payment_data['total_amount'],
                marker_color=['#6366F1', '#8B5CF6', '#3B82F6', '#10B981'][:len(payment_data)],
                text=[f"${a:,.0f}<br>({c} txns)" for a, c in zip(payment_data['total_amount'], payment_data['count'])],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Amount: $%{y:,.2f}<extra></extra>'
            )])

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F1F5F9',
                height=350,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis=dict(showgrid=False, title='Payment Method'),
                yaxis=dict(showgrid=True, gridcolor='#334155', title='Total Amount ($)')
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No payment data available")

    with col2:
        st.subheader("Payment Status")

        if not payment_status.empty:
            status_colors = {
                'completed': '#10B981',
                'pending': '#F59E0B',
                'failed': '#EF4444',
                'refunded': '#8B5CF6'
            }

            colors = [status_colors.get(s, '#6366F1') for s in payment_status['status']]

            fig = go.Figure(data=[go.Pie(
                labels=payment_status['status'].str.title(),
                values=payment_status['count'],
                hole=0.4,
                marker=dict(colors=colors),
                textinfo='label+value',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
            )])

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#F1F5F9',
                height=350,
                margin=dict(l=0, r=0, t=20, b=0)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No payment status data available")

    # Payment trends over time
    st.subheader("Payment Trends Over Time")

    payment_trends = analytics.get_payments_over_time()

    if not payment_trends.empty:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=payment_trends['date'],
            y=payment_trends['amount'],
            mode='lines+markers',
            name='Payment Amount',
            line=dict(color='#10B981', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(16, 185, 129, 0.1)',
            hovertemplate='<b>%{x}</b><br>Amount: $%{y:,.2f}<extra></extra>'
        ))

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#F1F5F9',
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=False, title='Date'),
            yaxis=dict(showgrid=True, gridcolor='#334155', title='Amount ($)')
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No payment trend data available")

    # Detailed payment table
    st.subheader("Payment Method Details")

    if not payment_data.empty:
        display_df = payment_data.copy()
        display_df['avg_payment'] = display_df['total_amount'] / display_df['count']
        display_df['total_amount'] = display_df['total_amount'].apply(lambda x: f"${x:,.2f}")
        display_df['avg_payment'] = display_df['avg_payment'].apply(lambda x: f"${x:,.2f}")

        display_df = display_df.rename(columns={
            'payment_method': 'Method',
            'count': 'Transactions',
            'total_amount': 'Total Amount',
            'avg_payment': 'Avg Transaction'
        })

        st.dataframe(
            display_df[['Method', 'Transactions', 'Total Amount', 'Avg Transaction']],
            use_container_width=True,
            hide_index=True
        )


def render_table_viewer(analytics: AnalyticsConnector):
    """Database table viewer - RAW DATA"""

    st.subheader("🗄️ Database Table Viewer")
    st.caption("View raw data from any database table")

    # Get available tables
    available_tables = analytics.get_available_tables()

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        selected_table = st.selectbox(
            "Select Table",
            available_tables,
            help="Choose a table to view its data"
        )

    with col2:
        row_limit = st.number_input(
            "Rows to Display",
            min_value=10,
            max_value=1000,
            value=100,
            step=10,
            help="Number of rows to fetch (max 1000)"
        )

    with col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.markdown("---")

    # Get table info
    total_rows = analytics.get_table_count(selected_table)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Table:** `{selected_table}`")
    with col2:
        st.metric("Total Rows", f"{total_rows:,}")

    # Fetch and display table data
    with st.spinner(f"Loading data from {selected_table}..."):
        table_df = analytics.get_table_data(selected_table, limit=row_limit)

        if not table_df.empty:
            # Show table info
            st.caption(f"Showing {len(table_df)} of {total_rows} rows")

            # Display the raw data
            st.dataframe(
                table_df,
                use_container_width=True,
                hide_index=True,
                height=500
            )

        

            # Download button
            csv_data = table_df.to_csv(index=False)
            st.download_button(
                label=f"📥 Download {selected_table}.csv",
                data=csv_data,
                file_name=f"{selected_table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        else:
            st.info(f"No data found in {selected_table} table")


