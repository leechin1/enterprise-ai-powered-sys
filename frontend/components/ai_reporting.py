"""
AI Business Intelligence Reporting component for Misty AI Enterprise System
"""
import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.db_analytics import AnalyticsConnector
from services.ai_business_consultant import AIBusinessConsultant


def render_ai_reporting():
    """Render AI Business Intelligence Reporting page"""

    st.title("🤖 AI Business Intelligence Reporting")
    st.caption("AI-powered business consultation using Gemini API with Langsmith tracing")

    # Initialize connectors
    try:
        analytics = AnalyticsConnector()
        ai_consultant = AIBusinessConsultant()
    except Exception as e:
        st.error(f"Failed to initialize AI consultant: {e}")
        st.info("Make sure GEMINI_API_KEY, LANGSMITH_API_KEY, and Supabase credentials are set in .env")

        with st.expander("🔧 Troubleshooting", expanded=True):
            st.markdown("""
            **Required environment variables:**
            ```
            GEMINI_API_KEY=your_gemini_key
            LANGSMITH_API_KEY=your_langsmith_key
            LANGSMITH_TRACING=true
            LANGSMITH_PROJECT=misty-ai-enterprise
            SUPABASE_URL=your_supabase_url
            SUPABASE_SECRET_KEY=your_supabase_key
            ```

            **Setup steps:**
            1. Get Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
            2. Get Langsmith API key from [Langsmith](https://smith.langchain.com/)
            3. Add all keys to your `.env` file
            4. Restart the application
            """)
        return

    # Header with business metrics snapshot
    st.markdown("---")
    st.subheader("📊 Current Business Overview")

    col1, col2, col3, col4 = st.columns(4)

    # Get key metrics
    total_revenue = analytics.get_total_revenue()
    total_orders = analytics.get_total_orders()
    total_customers = analytics.get_total_customers()
    avg_rating = analytics.get_average_rating()

    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.2f}", help="Total revenue from all orders")

    with col2:
        st.metric("Total Orders", f"{total_orders:,}", help="Total number of orders placed")

    with col3:
        st.metric("Total Customers", f"{total_customers:,}", help="Total registered customers")

    with col4:
        st.metric("Avg Rating", f"{avg_rating:.2f} ⭐", help="Average customer rating across all reviews")

    st.markdown("---")

    # Consultation configuration
    st.subheader("⚙️ Configure Your Consultation")

    col1, col2 = st.columns(2)

    with col1:
        consultation_type = st.selectbox(
            "📋 Consultation Focus",
            [
                "Overall Business Health",
                "Revenue Optimization",
                "Customer Strategy",
                "Inventory Management"
            ],
            help="Choose what aspect of your business to analyze in depth"
        )

        # Description for each type
        focus_descriptions = {
            "Overall Business Health": "Comprehensive analysis covering revenue, customers, inventory, and strategic recommendations",
            "Revenue Optimization": "Deep dive into pricing strategies, upselling opportunities, and revenue growth tactics",
            "Customer Strategy": "Customer retention, acquisition, VIP programs, and lifetime value optimization",
            "Inventory Management": "Stock optimization, reordering strategies, and supplier relationship management"
        }

        st.info(f"**About:** {focus_descriptions[consultation_type]}")

    with col2:
        report_format = st.selectbox(
            "📝 Report Style",
            [
                "Executive Summary",
                "Detailed Analysis",
                "Quick Insights"
            ],
            help="Choose the depth and format of the analysis"
        )

        # Description for each format
        format_descriptions = {
            "Executive Summary": "High-level overview with key findings and top recommendations (1-2 pages)",
            "Detailed Analysis": "Comprehensive report with in-depth analysis and actionable strategies (3-5 pages)",
            "Quick Insights": "5 rapid-fire insights with priorities and actions (bullet points)"
        }

        st.info(f"**About:** {format_descriptions[report_format]}")

    # Generate button
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("🎯 Generate AI Report", use_container_width=True, type="primary"):
            st.session_state.generate_ai_report = True

    st.markdown("---")

    # Map selections to focus areas
    focus_map = {
        "Overall Business Health": "overall",
        "Revenue Optimization": "revenue",
        "Customer Strategy": "customer",
        "Inventory Management": "inventory"
    }

    # Generate and display AI consultation report
    if st.session_state.get('generate_ai_report', False) or st.session_state.get('ai_report_cache'):

        with st.spinner("🧠 AI Consultant is analyzing your business data from Supabase..."):

            # Check cache first to avoid regenerating
            if not st.session_state.get('ai_report_cache') or st.session_state.get('generate_ai_report'):

                focus_area = focus_map[consultation_type]

                if report_format == "Quick Insights":
                    # Generate quick insights
                    insights = ai_consultant.generate_quick_insights(limit=5)
                    st.session_state.ai_report_cache = {
                        "type": "quick_insights",
                        "data": insights,
                        "consultation_type": consultation_type,
                        "timestamp": datetime.now()
                    }
                else:
                    # Generate full consultation report
                    result = ai_consultant.generate_consultation_report(focus_area=focus_area)
                    st.session_state.ai_report_cache = {
                        "type": "full_report",
                        "data": result,
                        "consultation_type": consultation_type,
                        "timestamp": datetime.now()
                    }

                st.session_state.generate_ai_report = False

        # Display the report
        cached_report = st.session_state.ai_report_cache

        st.success("✅ Report generated successfully!")

        # Report header
        st.markdown("---")

        if cached_report["type"] == "quick_insights":
            # Quick Insights Display
            st.subheader("⚡ Quick Business Insights")
            st.caption(f"Generated: {cached_report['timestamp'].strftime('%B %d, %Y at %I:%M %p')}")
            st.caption(f"Focus: {cached_report['consultation_type']}")

            st.markdown("---")

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
                        col1, col2 = st.columns([1, 2])

                        with col1:
                            st.markdown(f"**Priority Level**")
                            st.markdown(f"### {priority}")

                        with col2:
                            st.markdown(f"**Recommended Action**")
                            st.markdown(insight.get('action', 'N/A'))

                        st.markdown("---")
                        st.markdown(f"**Expected Business Impact**")
                        st.markdown(insight.get('impact', 'N/A'))

                # Download insights
                insights_text = f"AI Business Insights - {cached_report['consultation_type']}\n"
                insights_text += f"Generated: {cached_report['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"

                for i, insight in enumerate(insights, 1):
                    insights_text += f"\nInsight #{i}\n"
                    insights_text += f"Priority: {insight.get('priority', 'N/A')}\n"
                    insights_text += f"Insight: {insight.get('insight', 'N/A')}\n"
                    insights_text += f"Action: {insight.get('action', 'N/A')}\n"
                    insights_text += f"Impact: {insight.get('impact', 'N/A')}\n"
                    insights_text += "-" * 60 + "\n"

                st.download_button(
                    label="📥 Download Insights",
                    data=insights_text,
                    file_name=f"misty_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            else:
                st.warning("No insights generated. Try generating a full report instead.")

        elif cached_report["type"] == "full_report":
            # Full Report Display
            result = cached_report["data"]

            if result["success"]:
                st.subheader(f"📊 {cached_report['consultation_type']} - Business Consultation Report")
                st.caption(f"Generated: {cached_report['timestamp'].strftime('%B %d, %Y at %I:%M %p')}")
                st.caption(f"AI Model: {result['model']}")

                st.markdown("---")

                # Display the AI-generated consultation in a nice container
                with st.container():
                    st.markdown(result["report"])

                st.markdown("---")

                # Action buttons
                col1, col2 = st.columns(2)

                with col1:
                    st.download_button(
                        label="📥 Download Full Report",
                        data=result["report"],
                        file_name=f"misty_consultation_{result['focus_area']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

                with col2:
                    if st.button("🔄 Generate New Report", use_container_width=True):
                        st.session_state.ai_report_cache = None
                        st.session_state.generate_ai_report = True
                        st.rerun()

            else:
                st.error(f"❌ Failed to generate report: {result.get('error', 'Unknown error')}")
                st.info("Please check your API keys and try again.")

    else:
        # Instructions when no report is generated
        st.info("👆 **Get Started:** Select your consultation focus and report style above, then click 'Generate AI Report'")

        # What gets analyzed
        with st.expander("🔍 What Data Gets Analyzed", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                **Financial Metrics**
                - Total revenue across all orders
                - Average order value
                - Revenue trends and patterns

                **Customer Analytics**
                - Top customers by spending
                - Customer ratings and satisfaction
                - Review sentiment analysis

                **Product Performance**
                - Best-selling albums
                - Top-rated products
                - Genre performance
                """)

            with col2:
                st.markdown("""
                **Inventory Status**
                - Stock level distribution
                - Low stock alerts
                - Inventory value analysis

                **Sales Insights**
                - Record label performance
                - Payment method preferences
                - Sales trends over time

                **Strategic Recommendations**
                - Growth opportunities
                - Risk mitigation
                - Action plans with ROI
                """)



