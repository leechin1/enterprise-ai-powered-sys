"""
Analytics component for Misty AI Enterprise System
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

def render_analytics():
    """Render comprehensive analytics dashboards"""

    st.title("Analytics & Insights")
    st.caption("AI-powered business intelligence and predictive analytics")

    # Time range selector
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        date_range = st.selectbox(
            "Time Period",
            ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year", "All Time"]
        )

    with col2:
        metric_type = st.selectbox(
            "Metric Type",
            ["Revenue", "Units Sold", "Customer Activity", "Inventory Turnover"]
        )

    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    st.markdown("---")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Revenue", "$124,580", "+12.5%")

    with col2:
        st.metric("Units Sold", "2,847", "+8.3%")

    with col3:
        st.metric("Avg Order Value", "$43.75", "+3.2%")

    with col4:
        st.metric("Customer LTV", "$287", "+15.8%")

    st.markdown("---")

    # Tabs for different analytics views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Sales Trends",
        "👥 Customer Insights",
        "📦 Inventory Analysis",
        "🎯 AI Predictions",
        "🎵 Genre Performance"
    ])

    with tab1:
        render_sales_trends()

    with tab2:
        render_customer_insights()

    with tab3:
        render_inventory_analysis()

    with tab4:
        render_ai_predictions()

    with tab5:
        render_genre_performance()


def render_sales_trends():
    """Sales trends visualization"""

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Daily Revenue Trend")

        # Generate sample data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        revenue = [random.randint(3000, 8000) for _ in range(30)]

        df = pd.DataFrame({'Date': dates, 'Revenue': revenue})

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Revenue'],
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#6366F1', width=3),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(99, 102, 241, 0.1)'
        ))

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

    with col2:
        st.subheader("Sales by Channel")

        channels = ['In-Store', 'Online', 'Phone Orders', 'Corporate']
        values = [45, 35, 12, 8]

        fig = go.Figure(data=[go.Pie(
            labels=channels,
            values=values,
            hole=0.4,
            marker=dict(colors=['#6366F1', '#8B5CF6', '#3B82F6', '#10B981'])
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

    # Sales by hour heatmap
    st.subheader("Sales Heatmap by Day & Hour")

    # Generate sample heatmap data
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    hours = list(range(9, 21))  # 9 AM to 9 PM

    data = [[random.randint(10, 100) for _ in hours] for _ in days]

    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=hours,
        y=days,
        colorscale='Purples',
        text=data,
        texttemplate='%{text}',
        textfont={"size": 10}
    ))

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#F1F5F9',
        height=300,
        xaxis=dict(title='Hour of Day'),
        yaxis=dict(title='Day of Week')
    )

    st.plotly_chart(fig, use_container_width=True)


def render_customer_insights():
    """Customer analytics and segmentation"""

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer Segmentation")

        segments = {
            'VIP Collectors': 145,
            'Regular Enthusiasts': 423,
            'Casual Buyers': 892,
            'New Customers': 234
        }

        fig = go.Figure(data=[go.Bar(
            x=list(segments.keys()),
            y=list(segments.values()),
            marker_color=['#6366F1', '#8B5CF6', '#3B82F6', '#10B981'],
            text=list(segments.values()),
            textposition='outside'
        )])

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#F1F5F9',
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#334155', title='Customers')
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Customer Lifetime Value Distribution")

        # Generate sample CLV data
        clv_ranges = ['$0-50', '$51-100', '$101-250', '$251-500', '$500+']
        clv_counts = [320, 485, 612, 245, 132]

        fig = go.Figure(data=[go.Bar(
            x=clv_ranges,
            y=clv_counts,
            marker_color='#8B5CF6',
            text=clv_counts,
            textposition='outside'
        )])

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#F1F5F9',
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=False, title='CLV Range'),
            yaxis=dict(showgrid=True, gridcolor='#334155', title='Count')
        )

        st.plotly_chart(fig, use_container_width=True)

    # Cohort analysis
    st.subheader("Customer Retention Cohort Analysis")

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    cohort_data = [
        [100, 85, 72, 68, 65, 62],
        [100, 88, 75, 70, 67, None],
        [100, 90, 78, 73, None, None],
        [100, 87, 76, None, None, None],
        [100, 89, None, None, None, None],
        [100, None, None, None, None, None]
    ]

    df_cohort = pd.DataFrame(cohort_data, columns=months, index=months)

    fig = go.Figure(data=go.Heatmap(
        z=df_cohort.values,
        x=df_cohort.columns,
        y=df_cohort.index,
        colorscale='Blues',
        text=df_cohort.values,
        texttemplate='%{text}%',
        textfont={"size": 10}
    ))

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#F1F5F9',
        height=300,
        xaxis=dict(title='Months Since First Purchase'),
        yaxis=dict(title='Cohort (First Purchase Month)')
    )

    st.plotly_chart(fig, use_container_width=True)


def render_inventory_analysis():
    """Inventory performance and turnover analysis"""

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Inventory Turnover by Category")

        categories = ['Jazz Classics', 'Bebop', 'Fusion', 'Vocal', 'Contemporary']
        turnover = [8.5, 7.2, 6.8, 9.1, 5.4]

        fig = go.Figure(data=[go.Bar(
            y=categories,
            x=turnover,
            orientation='h',
            marker_color='#6366F1',
            text=[f"{t}x" for t in turnover],
            textposition='outside'
        )])

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#F1F5F9',
            height=300,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=True, gridcolor='#334155', title='Turnover Rate'),
            yaxis=dict(showgrid=False)
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Stock Levels Overview")

        stock_status = {
            'Optimal Stock': 1245,
            'Low Stock': 87,
            'Out of Stock': 23,
            'Overstock': 45
        }

        colors = ['#10B981', '#F59E0B', '#EF4444', '#6366F1']

        fig = go.Figure(data=[go.Pie(
            labels=list(stock_status.keys()),
            values=list(stock_status.values()),
            hole=0.4,
            marker=dict(colors=colors)
        )])

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#F1F5F9',
            height=300,
            margin=dict(l=0, r=0, t=20, b=0)
        )

        st.plotly_chart(fig, use_container_width=True)

    # Slow-moving items table
    st.subheader("Slow-Moving Inventory (AI Identified)")

    slow_items = pd.DataFrame([
        {'Album': 'Experimental Jazz Vol. 3', 'Artist': 'Various Artists', 'Days in Stock': 287, 'Units': 12, 'AI Recommendation': 'Discount 15%'},
        {'Album': 'Nordic Jazz Sessions', 'Artist': 'Lars Hansen', 'Days in Stock': 245, 'Units': 8, 'AI Recommendation': 'Bundle offer'},
        {'Album': 'Smooth Grooves Collection', 'Artist': 'Various Artists', 'Days in Stock': 198, 'Units': 15, 'AI Recommendation': 'Feature in newsletter'},
        {'Album': 'Late Night Lounge', 'Artist': 'The Trio', 'Days in Stock': 176, 'Units': 6, 'AI Recommendation': 'Clearance sale'},
    ])

    st.dataframe(slow_items, use_container_width=True, hide_index=True)


def render_ai_predictions():
    """AI-powered predictive analytics"""

    st.subheader("AI Sales Forecast (Next 30 Days)")

    # Generate forecast data
    dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
    historical = [random.randint(4000, 6000) for _ in range(15)]
    forecast = [random.randint(4500, 7000) for _ in range(30)]

    fig = go.Figure()

    # Historical
    fig.add_trace(go.Scatter(
        x=dates[:15],
        y=historical,
        mode='lines+markers',
        name='Historical',
        line=dict(color='#6366F1', width=2),
        marker=dict(size=6)
    ))

    # Forecast
    fig.add_trace(go.Scatter(
        x=dates,
        y=forecast,
        mode='lines',
        name='Forecast',
        line=dict(color='#8B5CF6', width=2, dash='dash')
    ))

    # Confidence interval
    upper_bound = [f + random.randint(500, 1000) for f in forecast]
    lower_bound = [f - random.randint(500, 1000) for f in forecast]

    fig.add_trace(go.Scatter(
        x=dates.tolist() + dates[::-1].tolist(),
        y=upper_bound + lower_bound[::-1],
        fill='toself',
        fillcolor='rgba(139, 92, 246, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Confidence Interval',
        showlegend=True
    ))

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#F1F5F9',
        height=400,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#334155', title='Revenue ($)')
    )

    st.plotly_chart(fig, use_container_width=True)

    # Prediction insights
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Predicted Revenue (30d)", "$186,500", "+14.2%")

    with col2:
        st.metric("Confidence Score", "87.5%", "High")

    with col3:
        st.metric("Model Accuracy", "92.3%", "+2.1pp")

    # AI recommendations
    st.subheader("AI-Generated Recommendations")

    recommendations = [
        {"priority": "🔴 High", "recommendation": "Stock up on Jazz Fusion albums - 34% demand increase predicted", "impact": "$12,400 revenue"},
        {"priority": "🟡 Medium", "recommendation": "Launch customer re-engagement campaign - 245 inactive customers identified", "impact": "$8,700 revenue"},
        {"priority": "🟡 Medium", "recommendation": "Optimize pricing for premium vinyl - price elasticity analysis complete", "impact": "$5,200 revenue"},
        {"priority": "🟢 Low", "recommendation": "Adjust store hours on Thursdays - low foot traffic detected", "impact": "$1,800 savings"},
    ]

    for rec in recommendations:
        with st.expander(f"{rec['priority']} - {rec['recommendation']}"):
            st.write(f"**Estimated Impact:** {rec['impact']}")
            st.write(f"**AI Confidence:** {random.randint(75, 95)}%")
            col1, col2 = st.columns(2)
            with col1:
                st.button("✓ Accept", key=f"accept_{rec['recommendation'][:20]}")
            with col2:
                st.button("✗ Dismiss", key=f"dismiss_{rec['recommendation'][:20]}")


def render_genre_performance():
    """Genre-specific performance analytics"""

    st.subheader("Genre Performance Comparison")

    # Genre data
    genres = ['Bebop', 'Cool Jazz', 'Fusion', 'Vocal Jazz', 'Hard Bop', 'Modal Jazz', 'Contemporary']
    revenue = [28500, 24300, 31200, 19800, 22400, 18900, 15600]
    units = [542, 489, 623, 387, 445, 371, 298]
    margin = [35, 32, 38, 28, 34, 31, 29]

    df = pd.DataFrame({
        'Genre': genres,
        'Revenue': revenue,
        'Units': units,
        'Margin %': margin
    })

    # Multi-metric chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Revenue',
        x=df['Genre'],
        y=df['Revenue'],
        marker_color='#6366F1',
        yaxis='y',
        offsetgroup=1
    ))

    fig.add_trace(go.Scatter(
        name='Margin %',
        x=df['Genre'],
        y=df['Margin %'],
        marker_color='#10B981',
        yaxis='y2',
        mode='lines+markers',
        line=dict(width=3)
    ))

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#F1F5F9',
        height=400,
        xaxis=dict(showgrid=False),
        yaxis=dict(
            title='Revenue ($)',
            showgrid=True,
            gridcolor='#334155'
        ),
        yaxis2=dict(
            title='Margin (%)',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Genre details table
    st.subheader("Detailed Genre Metrics")

    genre_details = pd.DataFrame([
        {'Genre': 'Bebop', 'Revenue': '$28,500', 'Units': 542, 'Avg Price': '$52.58', 'Margin': '35%', 'Trend': '↑ 8.2%'},
        {'Genre': 'Cool Jazz', 'Revenue': '$24,300', 'Units': 489, 'Avg Price': '$49.69', 'Margin': '32%', 'Trend': '↑ 5.1%'},
        {'Genre': 'Fusion', 'Revenue': '$31,200', 'Units': 623, 'Avg Price': '$50.08', 'Margin': '38%', 'Trend': '↑ 12.4%'},
        {'Genre': 'Vocal Jazz', 'Revenue': '$19,800', 'Units': 387, 'Avg Price': '$51.16', 'Margin': '28%', 'Trend': '↓ 2.3%'},
        {'Genre': 'Hard Bop', 'Revenue': '$22,400', 'Units': 445, 'Avg Price': '$50.34', 'Margin': '34%', 'Trend': '↑ 6.7%'},
    ])

    st.dataframe(genre_details, use_container_width=True, hide_index=True)
