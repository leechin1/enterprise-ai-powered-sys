"""
AI-Powered Inventory Management component for Misty AI Enterprise System
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta

def render_inventory():
    """Render the AI-powered inventory management interface"""

    st.title("Smart Inventory Management")
    st.caption("AI-powered stock optimization, demand forecasting, and automated reordering")

    # Quick actions bar
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🤖 Generate Reorder List", use_container_width=True):
            st.toast("AI analyzing inventory and generating optimal reorder suggestions...")

    with col2:
        if st.button("📊 Stock Audit", use_container_width=True):
            st.toast("Initiating AI-powered inventory audit...")

    with col3:
        if st.button("🔍 Find Overstock", use_container_width=True):
            st.toast("Identifying overstock items for promotional campaigns...")

    with col4:
        if st.button("⚡ Quick Add", use_container_width=True):
            st.session_state.show_add_modal = True

    st.markdown("---")

    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total SKUs", "1,847", "↑ 23")

    with col2:
        st.metric("Stock Value", "$284K", "↑ $12K")

    with col3:
        st.metric("Turnover Rate", "6.8x", "↑ 0.4")

    with col4:
        st.metric("Low Stock Items", "87", "↓ 12")

    with col5:
        st.metric("AI Accuracy", "94.2%", "↑ 1.8%")

    st.markdown("---")

    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📦 Inventory List",
        "🤖 AI Recommendations",
        "📈 Demand Forecast",
        "🔄 Reorder Queue",
        "⚠️ Alerts"
    ])

    with tab1:
        render_inventory_list()

    with tab2:
        render_ai_recommendations()

    with tab3:
        render_demand_forecast()

    with tab4:
        render_reorder_queue()

    with tab5:
        render_alerts()


def render_inventory_list():
    """Display the main inventory list with search and filters"""

    # Search and filters
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

    with col1:
        search_query = st.text_input("🔍 Search albums, artists, or catalog numbers", "")

    with col2:
        genre_filter = st.multiselect(
            "Genre",
            ["All", "Bebop", "Cool Jazz", "Fusion", "Vocal Jazz", "Hard Bop"],
            default=["All"]
        )

    with col3:
        stock_filter = st.selectbox(
            "Stock Status",
            ["All", "In Stock", "Low Stock", "Out of Stock", "Overstock"]
        )

    with col4:
        sort_by = st.selectbox(
            "Sort By",
            ["Name", "Stock Level", "Last Sold", "Value", "AI Priority"]
        )

    # Sample inventory data
    inventory_data = [
        {
            'SKU': 'VNL-001',
            'Album': 'Kind of Blue',
            'Artist': 'Miles Davis',
            'Genre': 'Modal Jazz',
            'Stock': 23,
            'Price': '$42.99',
            'Value': '$989.77',
            'Last Sold': '2 hours ago',
            'AI Score': 98,
            'Status': 'Optimal'
        },
        {
            'SKU': 'VNL-002',
            'Album': 'A Love Supreme',
            'Artist': 'John Coltrane',
            'Genre': 'Spiritual Jazz',
            'Stock': 4,
            'Price': '$45.99',
            'Value': '$183.96',
            'Last Sold': '5 hours ago',
            'AI Score': 95,
            'Status': 'Low Stock'
        },
        {
            'SKU': 'VNL-003',
            'Album': 'Time Out',
            'Artist': 'Dave Brubeck',
            'Genre': 'Cool Jazz',
            'Stock': 18,
            'Price': '$38.99',
            'Value': '$701.82',
            'Last Sold': '1 day ago',
            'AI Score': 92,
            'Status': 'Optimal'
        },
        {
            'SKU': 'VNL-004',
            'Album': 'Head Hunters',
            'Artist': 'Herbie Hancock',
            'Genre': 'Fusion',
            'Stock': 0,
            'Price': '$44.99',
            'Value': '$0.00',
            'Last Sold': '3 hours ago',
            'AI Score': 97,
            'Status': 'Out of Stock'
        },
        {
            'SKU': 'VNL-005',
            'Album': 'Moanin\'',
            'Artist': 'Art Blakey',
            'Genre': 'Hard Bop',
            'Stock': 31,
            'Price': '$39.99',
            'Value': '$1,239.69',
            'Last Sold': '6 hours ago',
            'AI Score': 89,
            'Status': 'Optimal'
        },
        {
            'SKU': 'VNL-006',
            'Album': 'Blue Train',
            'Artist': 'John Coltrane',
            'Genre': 'Hard Bop',
            'Stock': 2,
            'Price': '$43.99',
            'Value': '$87.98',
            'Last Sold': '4 hours ago',
            'AI Score': 96,
            'Status': 'Critical'
        },
        {
            'SKU': 'VNL-007',
            'Album': 'Waltz for Debby',
            'Artist': 'Bill Evans Trio',
            'Genre': 'Piano Jazz',
            'Stock': 45,
            'Price': '$36.99',
            'Value': '$1,664.55',
            'Last Sold': '2 days ago',
            'AI Score': 78,
            'Status': 'Overstock'
        },
    ]

    df = pd.DataFrame(inventory_data)

    # Color code rows based on status
    def highlight_status(row):
        if row['Status'] == 'Critical' or row['Status'] == 'Out of Stock':
            return ['background-color: rgba(239, 68, 68, 0.1)'] * len(row)
        elif row['Status'] == 'Low Stock':
            return ['background-color: rgba(245, 158, 11, 0.1)'] * len(row)
        elif row['Status'] == 'Overstock':
            return ['background-color: rgba(59, 130, 246, 0.1)'] * len(row)
        else:
            return [''] * len(row)

    # Display dataframe
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'AI Score': st.column_config.ProgressColumn(
                'AI Priority',
                min_value=0,
                max_value=100,
                format='%d'
            ),
            'Stock': st.column_config.NumberColumn(
                'Stock',
                format='%d units'
            )
        }
    )

    # Bulk actions
    st.markdown("**Bulk Actions:**")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.button("📤 Export to CSV", use_container_width=True)

    with col2:
        st.button("🏷️ Update Prices", use_container_width=True)

    with col3:
        st.button("📦 Generate Labels", use_container_width=True)

    with col4:
        st.button("🤖 Auto-Optimize", use_container_width=True)


def render_ai_recommendations():
    """Display AI-generated inventory recommendations"""

    st.subheader("AI-Generated Inventory Insights")
    st.caption("Machine learning recommendations based on sales patterns, seasonality, and market trends")

    # Recommendation cards
    recommendations = [
        {
            'title': '🔴 Critical Stock Alert',
            'description': 'Blue Train - John Coltrane',
            'insight': 'Only 2 units remaining. Historical data shows average daily sales of 0.8 units. Stock-out predicted in 2.5 days.',
            'action': 'Reorder 15 units immediately',
            'confidence': 96,
            'impact': 'High'
        },
        {
            'title': '📈 Trending Item',
            'description': 'Kind of Blue - Miles Davis',
            'insight': 'Sales increased 42% in the last 7 days. Social media mentions up 230%. Holiday season demand spike detected.',
            'action': 'Increase stock by 20 units',
            'confidence': 92,
            'impact': 'High'
        },
        {
            'title': '💡 Optimization Opportunity',
            'description': 'Waltz for Debby - Bill Evans Trio',
            'insight': 'Current stock (45 units) exceeds 90-day forecast. Low sales velocity detected. Turnover rate: 2.1x vs. target 6.8x.',
            'action': 'Run 15% discount promotion',
            'confidence': 88,
            'impact': 'Medium'
        },
        {
            'title': '🎯 Cross-Sell Opportunity',
            'description': 'Modal Jazz Bundle',
            'insight': 'Customers who buy "Kind of Blue" have 67% likelihood of purchasing modal jazz albums within 30 days.',
            'action': 'Create bundle with "Milestones" and "Sketches of Spain"',
            'confidence': 84,
            'impact': 'Medium'
        },
        {
            'title': '⚡ Seasonal Forecast',
            'description': 'Vocal Jazz Category',
            'insight': 'Historical patterns show 35% increase in vocal jazz sales during Q1. Valentine\'s Day effect detected.',
            'action': 'Stock up on Ella Fitzgerald and Sarah Vaughan albums',
            'confidence': 91,
            'impact': 'High'
        },
        {
            'title': '🔄 Supplier Optimization',
            'description': 'Blue Note Records Catalog',
            'insight': 'Bulk ordering from Blue Note Records could reduce per-unit cost by 18%. Minimum order: 50 units.',
            'action': 'Consolidate next 3 orders into single bulk purchase',
            'confidence': 79,
            'impact': 'Low'
        }
    ]

    for rec in recommendations:
        with st.expander(f"{rec['title']} - {rec['description']}", expanded=False):
            st.write(f"**Insight:** {rec['insight']}")
            st.write(f"**Recommended Action:** {rec['action']}")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("AI Confidence", f"{rec['confidence']}%")
            with col2:
                st.metric("Impact", rec['impact'])
            with col3:
                st.write("")  # Spacer

            col_accept, col_dismiss, col_schedule = st.columns(3)
            with col_accept:
                st.button("✓ Accept", key=f"accept_{rec['title']}", use_container_width=True)
            with col_dismiss:
                st.button("✗ Dismiss", key=f"dismiss_{rec['title']}", use_container_width=True)
            with col_schedule:
                st.button("📅 Schedule", key=f"schedule_{rec['title']}", use_container_width=True)


def render_demand_forecast():
    """Display AI demand forecasting charts"""

    st.subheader("Demand Forecasting")
    st.caption("AI-powered 30-day demand prediction with confidence intervals")

    # Album selector
    album_to_forecast = st.selectbox(
        "Select Album",
        ["Kind of Blue - Miles Davis", "A Love Supreme - John Coltrane", "Time Out - Dave Brubeck", "Head Hunters - Herbie Hancock"]
    )

    # Generate forecast data
    days = list(range(1, 31))
    historical_demand = [random.randint(15, 35) for _ in range(15)]
    forecast_demand = [random.randint(18, 40) for _ in range(30)]

    # Create forecast chart
    fig = go.Figure()

    # Historical
    fig.add_trace(go.Scatter(
        x=days[:15],
        y=historical_demand,
        mode='lines+markers',
        name='Historical Demand',
        line=dict(color='#6366F1', width=2),
        marker=dict(size=6)
    ))

    # Forecast
    fig.add_trace(go.Scatter(
        x=days,
        y=forecast_demand,
        mode='lines',
        name='Forecasted Demand',
        line=dict(color='#8B5CF6', width=2, dash='dash')
    ))

    # Confidence interval
    upper_bound = [f + random.randint(5, 12) for f in forecast_demand]
    lower_bound = [max(0, f - random.randint(5, 12)) for f in forecast_demand]

    fig.add_trace(go.Scatter(
        x=days + days[::-1],
        y=upper_bound + lower_bound[::-1],
        fill='toself',
        fillcolor='rgba(139, 92, 246, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='95% Confidence',
        showlegend=True
    ))

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#F1F5F9',
        height=400,
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis=dict(showgrid=False, title='Days'),
        yaxis=dict(showgrid=True, gridcolor='#334155', title='Units Demanded')
    )

    st.plotly_chart(fig, use_container_width=True)

    # Forecast metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("30-Day Forecast", "847 units", "↑ 12.4%")

    with col2:
        st.metric("Peak Demand Day", "Day 23", "42 units")

    with col3:
        st.metric("Model Accuracy", "93.7%", "↑ 2.1%")

    with col4:
        st.metric("Recommended Stock", "65 units", "")

    # Forecast factors
    st.subheader("Forecast Influencing Factors")

    factors = pd.DataFrame([
        {'Factor': 'Seasonal Trend', 'Impact': 'High', 'Weight': '28%', 'Direction': 'Positive'},
        {'Factor': 'Historical Sales', 'Impact': 'High', 'Weight': '25%', 'Direction': 'Positive'},
        {'Factor': 'Market Trends', 'Impact': 'Medium', 'Weight': '18%', 'Direction': 'Positive'},
        {'Factor': 'Competitor Activity', 'Impact': 'Medium', 'Weight': '15%', 'Direction': 'Neutral'},
        {'Factor': 'Social Media Sentiment', 'Impact': 'Low', 'Weight': '9%', 'Direction': 'Positive'},
        {'Factor': 'External Events', 'Impact': 'Low', 'Weight': '5%', 'Direction': 'Neutral'},
    ])

    st.dataframe(factors, use_container_width=True, hide_index=True)


def render_reorder_queue():
    """Display the AI-generated reorder queue"""

    st.subheader("Automated Reorder Queue")
    st.caption("AI-optimized purchase orders ready for approval")

    # Queue summary
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Pending Orders", "23", "")

    with col2:
        st.metric("Total Value", "$12,480", "")

    with col3:
        st.metric("Est. Delivery", "5-7 days", "")

    st.markdown("---")

    # Reorder items
    reorder_items = [
        {
            'Album': 'Blue Train',
            'Artist': 'John Coltrane',
            'Current Stock': 2,
            'Reorder Qty': 15,
            'Unit Cost': '$28.50',
            'Total': '$427.50',
            'Supplier': 'Blue Note Direct',
            'Priority': 'Critical',
            'AI Confidence': 96
        },
        {
            'Album': 'A Love Supreme',
            'Artist': 'John Coltrane',
            'Current Stock': 4,
            'Reorder Qty': 12,
            'Unit Cost': '$30.20',
            'Total': '$362.40',
            'Supplier': 'Impulse! Records',
            'Priority': 'High',
            'AI Confidence': 95
        },
        {
            'Album': 'Somethin\' Else',
            'Artist': 'Cannonball Adderley',
            'Current Stock': 2,
            'Reorder Qty': 10,
            'Unit Cost': '$27.80',
            'Total': '$278.00',
            'Supplier': 'Blue Note Direct',
            'Priority': 'High',
            'AI Confidence': 92
        },
        {
            'Album': 'Maiden Voyage',
            'Artist': 'Herbie Hancock',
            'Current Stock': 6,
            'Reorder Qty': 8,
            'Unit Cost': '$29.40',
            'Total': '$235.20',
            'Supplier': 'Blue Note Direct',
            'Priority': 'Medium',
            'AI Confidence': 88
        },
    ]

    df_reorder = pd.DataFrame(reorder_items)

    st.dataframe(
        df_reorder,
        use_container_width=True,
        hide_index=True,
        column_config={
            'AI Confidence': st.column_config.ProgressColumn(
                'AI Confidence',
                min_value=0,
                max_value=100,
                format='%d%%'
            )
        }
    )

    # Bulk actions
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.button("✓ Approve All", use_container_width=True, type="primary")

    with col2:
        st.button("📤 Export PO", use_container_width=True)

    with col3:
        st.button("📧 Email Suppliers", use_container_width=True)

    with col4:
        st.button("⚙️ Adjust Quantities", use_container_width=True)

    # Optimization insights
    st.info("💡 **AI Optimization Tip:** Consolidating Blue Note orders could save $42.30 in shipping costs. Consider combining orders #1, #3, and #4.")


def render_alerts():
    """Display inventory alerts and warnings"""

    st.subheader("Inventory Alerts & Notifications")

    # Alert severity filter
    severity_filter = st.multiselect(
        "Filter by Severity",
        ["Critical", "Warning", "Info"],
        default=["Critical", "Warning", "Info"]
    )

    # Alerts list
    alerts = [
        {
            'severity': 'Critical',
            'icon': '🔴',
            'title': 'Stock-out imminent',
            'message': 'Head Hunters - Herbie Hancock is out of stock. 3 backorders pending.',
            'time': '10 minutes ago',
            'action': 'Expedite reorder'
        },
        {
            'severity': 'Critical',
            'icon': '🔴',
            'title': 'Critical stock level',
            'message': 'Blue Train - John Coltrane has only 2 units remaining. Predicted stock-out in 2.5 days.',
            'time': '1 hour ago',
            'action': 'Auto-reorder triggered'
        },
        {
            'severity': 'Warning',
            'icon': '🟡',
            'title': 'Overstock detected',
            'message': 'Waltz for Debby - Bill Evans Trio has 45 units. Turnover rate below target.',
            'time': '3 hours ago',
            'action': 'Consider promotion'
        },
        {
            'severity': 'Warning',
            'icon': '🟡',
            'title': 'Price variance',
            'message': 'Supplier ABC increased prices by 8% for 12 SKUs. Budget impact: $240/month.',
            'time': '5 hours ago',
            'action': 'Review pricing'
        },
        {
            'severity': 'Info',
            'icon': '🔵',
            'title': 'Shipment arrived',
            'message': 'Shipment #SH-8821 received and verified. 45 units added to inventory.',
            'time': '1 day ago',
            'action': 'View details'
        },
        {
            'severity': 'Info',
            'icon': '🔵',
            'title': 'Forecast updated',
            'message': 'AI demand forecast refreshed for 147 SKUs. 3 new recommendations available.',
            'time': '1 day ago',
            'action': 'Review forecast'
        },
        {
            'severity': 'Warning',
            'icon': '🟡',
            'title': 'Seasonal trend',
            'message': 'Vocal jazz demand predicted to increase 35% in next 30 days.',
            'time': '2 days ago',
            'action': 'Stock up'
        },
    ]

    # Filter and display alerts
    filtered_alerts = [a for a in alerts if a['severity'] in severity_filter]

    for alert in filtered_alerts:
        with st.container():
            col1, col2, col3 = st.columns([1, 8, 2])

            with col1:
                st.markdown(f"<h2>{alert['icon']}</h2>", unsafe_allow_html=True)

            with col2:
                st.markdown(f"**{alert['title']}**")
                st.caption(alert['message'])
                st.caption(f"🕒 {alert['time']}")

            with col3:
                st.button(alert['action'], key=f"alert_{alert['title']}", use_container_width=True)

            st.markdown("---")
