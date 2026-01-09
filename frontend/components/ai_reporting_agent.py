"""
AI Business Intelligence Reporting component (Refactored)
Uses the new LangChain-based AI Business Consultant Agent
"""
import streamlit as st
from datetime import datetime
import sys
from pathlib import Path
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.db_analytics import AnalyticsConnector
from services.ai_business_consultant_agent import AIBusinessConsultantAgent


def render_ai_reporting_agent():
    """Render AI Business Intelligence Reporting page with new agent architecture"""

    st.title("🤖 AI Business Intelligence Reporting")
    st.caption("AI-powered business consultation using Gemini 2.0-flash with LangChain agents")

    # Initialize connectors
    try:
        analytics = AnalyticsConnector()
        ai_agent = AIBusinessConsultantAgent()
    except Exception as e:
        st.error(f"Failed to initialize AI consultant: {e}")
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

    # Tabs for different analysis types
    tab1, tab2 = st.tabs(["📊 Overall Business Health", "⚠️ Issues & Problems"])

    with tab1:
        render_health_tab(ai_agent)

    with tab2:
        render_issues_tab(ai_agent)


def render_health_tab(ai_agent):
    """Render the Overall Business Health tab"""
    st.markdown("### 📊 Business Health Analysis")
    st.caption("AI-powered analysis of financial, customer, inventory, and product metrics")

    # Generate button
    if st.button("🎯 Generate Health Analysis", use_container_width=True, type="primary", key="health_generate"):
        with st.spinner("🧠 AI Agent is analyzing your business health..."):
            health_result = ai_agent.analyze_business_health()
            st.session_state.health_cache = health_result
            st.rerun()

    # Display results if available
    if st.session_state.get('health_cache'):
        health_result = st.session_state.health_cache
        display_health_results(health_result)

        st.markdown("---")

        # Recommendations button
        if st.button("💡 Generate Strategic Recommendations", use_container_width=True, type="secondary", key="health_recommendations"):
            with st.spinner("🤔 Generating strategic recommendations..."):
                recommendations = ai_agent.generate_recommendations(health_result)
                st.session_state.recommendations_cache = recommendations
                st.rerun()

        # Display recommendations if available
        if st.session_state.get('recommendations_cache'):
            display_recommendations(st.session_state.recommendations_cache)
    else:
        st.info("👆 Click 'Generate Health Analysis' to analyze your business performance")
        with st.expander("🔍 What Gets Analyzed", expanded=False):
            st.markdown("""
            - **Financial Performance**: Revenue trends, profit margins, transaction volume
            - **Customer Metrics**: Customer satisfaction, loyalty, engagement patterns
            - **Inventory Status**: Stock levels, turnover rates, optimization opportunities
            - **Product Performance**: Best sellers, underperformers, genre trends
            - **Strategic Insights**: Growth opportunities and recommendations
            """)


def render_issues_tab(ai_agent):
    """Render the Issues & Problems tab"""
    st.markdown("### ⚠️ Business Issues Detection")
    st.caption("Identify and fix critical business problems with AI-powered solutions")

    # Generate button
    if st.button("🔍 Scan for Issues", use_container_width=True, type="primary", key="issues_generate"):
        with st.spinner("🧠 AI Agent is scanning for business issues..."):
            issues_result = ai_agent.analyze_business_issues()
            st.session_state.issues_cache = issues_result
            st.rerun()

    # Display results if available
    if st.session_state.get('issues_cache'):
        issues_result = st.session_state.issues_cache
        display_issues_with_fix_buttons(issues_result, ai_agent)
    else:
        st.info("👆 Click 'Scan for Issues' to identify business problems")
        with st.expander("🔍 What Gets Scanned", expanded=False):
            st.markdown("""
            - **Payment Issues**: Failed transactions, pending payments
            - **Inventory Problems**: Low stock alerts, overstock situations
            - **Customer Concerns**: Service issues, complaint patterns
            - **Revenue Bottlenecks**: Underperforming products or categories
            - **Operational Inefficiencies**: Process improvements needed
            """)


def render_health_analysis(ai_agent):
    """Render the health analysis flow"""
    with st.spinner("🧠 AI Agent is analyzing your business health..."):

        # Generate health analysis
        if not st.session_state.get('analysis_cache'):
            health_result = ai_agent.analyze_business_health()

            st.session_state.analysis_cache = {
                "type": "health",
                "health_result": health_result,
                "timestamp": datetime.now()
            }

        # Display results
        display_health_results(st.session_state.analysis_cache["health_result"])

        # Recommendations button
        st.markdown("---")
        if st.button("💡 Business Recommendations", use_container_width=True, type="primary"):
            with st.spinner("🤔 Generating strategic recommendations..."):
                recommendations = ai_agent.generate_recommendations(
                    st.session_state.analysis_cache["health_result"]
                )
                st.session_state.analysis_cache["recommendations"] = recommendations
                st.session_state.show_recommendations = True
                st.rerun()


def render_issues_analysis(ai_agent):
    """Render the issues analysis flow"""
    with st.spinner("🧠 AI Agent is scanning for business issues..."):

        # Generate issues analysis
        if not st.session_state.get('analysis_cache'):
            issues_result = ai_agent.analyze_business_issues()

            st.session_state.analysis_cache = {
                "type": "issues",
                "issues_result": issues_result,
                "timestamp": datetime.now()
            }

        # Display results
        display_issues_results(st.session_state.analysis_cache["issues_result"])

        # Fixes button
        st.markdown("---")
        if st.button("🔧 Suggested Fixes", use_container_width=True, type="primary"):
            with st.spinner("🛠️ Generating fix recommendations..."):
                fixes = ai_agent.generate_fixes(
                    st.session_state.analysis_cache["issues_result"]
                )
                st.session_state.analysis_cache["fixes"] = fixes
                st.session_state.show_fixes = True
                st.rerun()


def display_health_results(result):
    """Display health analysis results in boxes"""
    if not result["success"]:
        st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
        return

    st.success("✅ Business Health Analysis Complete!")
    st.markdown("---")

    st.subheader("📊 Key Business Insights")
    st.caption(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    st.caption(f"Model: {result['model']}")

    insights = result.get("data", {}).get("insights", [])

    if not insights:
        st.warning("No insights generated. Please try again.")
        return

    # Display insights in grid (2 columns)
    col1, col2 = st.columns(2)

    for i, insight in enumerate(insights[:6]):  # Limit to 6
        priority = insight.get("priority", "medium")
        metric_type = insight.get("metric_type", "general")

        # Color coding
        priority_colors = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }

        metric_icons = {
            "financial": "💰",
            "customer": "👥",
            "inventory": "📦",
            "product": "🎵",
            "overall": "📊"
        }

        emoji = priority_colors.get(priority, "⚪")
        icon = metric_icons.get(metric_type, "📊")

        with col1 if i % 2 == 0 else col2:
            with st.container(border=True):
                st.markdown(f"### {icon} {insight.get('title', 'Insight')}")
                st.markdown(f"**Priority:** {emoji} {priority.title()}")
                st.markdown(insight.get('content', 'N/A'))


def display_recommendations(recommendations_result):
    """Display strategic recommendations"""
    st.markdown("---")
    st.subheader("💡 Strategic Recommendations")

    if not recommendations_result or not isinstance(recommendations_result, dict):
        st.error("No recommendations data available. Please try generating the analysis again.")
        return

    if not recommendations_result.get("success", False):
        st.error(f"Failed to generate recommendations: {recommendations_result.get('error', 'Unknown error')}")
        return

    recommendations = recommendations_result.get("data", {}).get("recommendations", [])

    for i, rec in enumerate(recommendations, 1):
        priority = rec.get("priority", "medium")
        difficulty = rec.get("difficulty", "medium")

        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
        difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(difficulty, "⚪")

        with st.expander(f"{i}. {rec.get('title', 'Recommendation')}", expanded=(i == 1)):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Priority:** {priority_emoji} {priority.title()}")
                st.markdown(f"**Difficulty:** {difficulty_emoji} {difficulty.title()}")

            with col2:
                st.markdown(f"**Expected Impact:**")
                st.markdown(rec.get('expected_impact', 'N/A'))

            st.markdown("---")
            st.markdown("**Recommendation:**")
            st.markdown(rec.get('description', 'N/A'))


def display_issues_results(result):
    """Display issues analysis results in boxes"""
    if not result["success"]:
        st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
        return

    st.success("✅ Business Issues Analysis Complete!")
    st.markdown("---")

    st.subheader("⚠️ Critical Business Issues")
    st.caption(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    st.caption(f"Model: {result['model']}")

    issues = result.get("data", {}).get("issues", [])

    if not issues:
        st.info("🎉 No critical issues found! Business is running smoothly.")
        return

    # Display issues in grid
    for i, issue in enumerate(issues[:7], 1):  # Limit to 7
        impact = issue.get("impact", "medium")
        category = issue.get("category", "general")

        impact_colors = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }

        category_icons = {
            "payment": "💳",
            "inventory": "📦",
            "customer": "👥",
            "financial": "💰",
            "general": "⚠️"
        }

        emoji = impact_colors.get(impact, "⚪")
        icon = category_icons.get(category, "⚠️")

        with st.container(border=True):
            st.markdown(f"### {icon} Issue #{i}: {issue.get('title', 'Unknown Issue')}")
            st.markdown(f"**Impact:** {emoji} {impact.title()} | **Category:** {category.title()}")
            st.markdown(f"**Affected:** {issue.get('affected_count', 'N/A')}")
            st.markdown("---")
            st.markdown(issue.get('description', 'N/A'))


def display_fixes(fixes_result):
    """Display suggested fixes"""
    st.markdown("---")
    st.subheader("🔧 Suggested Fixes & Actions")

    if not fixes_result or not isinstance(fixes_result, dict):
        st.error("No fixes data available. Please try generating the analysis again.")
        return

    if not fixes_result.get("success", False):
        st.error(f"Failed to generate fixes: {fixes_result.get('error', 'Unknown error')}")
        return

    fixes = fixes_result.get("data", {}).get("fixes", [])

    for i, fix in enumerate(fixes, 1):
        tool = fix.get("tool_to_use", "manual")
        automation = fix.get("automation_level", "manual")

        automation_emoji = {
            "full": "🤖",
            "partial": "⚙️",
            "manual": "👤"
        }.get(automation, "⚙️")

        with st.expander(f"{i}. {fix.get('fix_title', 'Fix Action')}", expanded=(i == 1)):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Related Issue:**")
                st.markdown(fix.get('issue_title', 'N/A'))
                st.markdown(f"**Tool:** {tool}")

            with col2:
                st.markdown(f"**Automation:** {automation_emoji} {automation.title()}")
                st.markdown(f"**Impact:**")
                st.markdown(fix.get('estimated_impact', 'N/A'))

            st.markdown("---")
            st.markdown("**Fix Description:**")
            st.markdown(fix.get('description', 'N/A'))


def display_action_preview_dialog(issue_num, issue, fix_result, ai_agent):
    """Display a preview dialog showing the template that will be sent"""
    st.markdown("---")
    st.markdown(f"### 📧 Preview Action for Issue #{issue_num}")

    if not fix_result or not fix_result.get('success'):
        st.error("No fix data available for preview.")
        return

    fixes = fix_result.get("data", {}).get("fixes", [])
    if not fixes:
        st.error("No fix information found.")
        return

    fix = fixes[0]
    tool_to_use = fix.get('tool_to_use', 'manual')

    # Generate preview based on the tool being used
    preview_content = None
    preview_title = "Action Preview"

    if 'email' in tool_to_use.lower():
        preview_title = "📧 Email Template Preview"
        # This is a placeholder - in real implementation, you'd call the actual tool
        preview_content = f"""
**Subject:** Action Required - {issue.get('title', 'Issue')}

Dear Team,

{fix.get('description', 'No description available.')}

This action will be performed automatically.

Best regards,
Misty Jazz Records AI System
"""
    elif 'cancel' in tool_to_use.lower():
        preview_title = "🚫 Transaction Cancellation Preview"
        preview_content = f"""
**Transaction Cancellation Notice**

Issue: {issue.get('title', 'N/A')}
Action: Cancel transaction
Reason: {issue.get('description', 'Business issue resolution')}

Affected transactions will be marked as cancelled in the system.
"""
    elif 'inventory' in tool_to_use.lower():
        preview_title = "📦 Inventory Alert Preview"
        preview_content = f"""
**Inventory Alert Email**

To: inventory@mistyjazzrecords.com
Subject: {issue.get('title', 'Inventory Alert')}

{fix.get('description', 'No description available.')}

This alert will be sent to the inventory management team.
"""
    else:
        preview_title = "⚙️ Manual Action Preview"
        preview_content = f"""
**Manual Action Required**

{fix.get('description', 'No description available.')}

Please follow the steps outlined above.
"""

    # Display the preview in a container
    with st.container(border=True):
        st.markdown(f"#### {preview_title}")
        st.markdown("---")

        if preview_content:
            st.text_area(
                "Preview:",
                preview_content,
                height=300,
                disabled=True,
                key=f"preview_content_{issue_num}"
            )

        st.markdown("")
        st.info("ℹ️ This is a preview. Click 'Send' to execute the action (demonstration only).")

        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("❌ Cancel", use_container_width=True, key=f"cancel_preview_{issue_num}"):
                st.session_state[f'show_preview_{issue_num}'] = False
                st.rerun()

        with col3:
            if st.button("📤 Send", use_container_width=True, type="primary", key=f"send_action_{issue_num}"):
                # Placebo action - just show success and close
                st.session_state[f'show_preview_{issue_num}'] = False
                st.session_state[f'fix_applied_{issue_num}'] = True
                st.rerun()

    # Show success message after sending
    if st.session_state.get(f'fix_applied_{issue_num}'):
        st.success(f"✅ Action executed successfully for Issue #{issue_num}!")
        st.balloons()
        # Clear the applied flag after showing success
        if st.button("👍 Acknowledge", key=f"ack_{issue_num}"):
            st.session_state[f'fix_applied_{issue_num}'] = False
            st.rerun()


def display_issues_with_fix_buttons(result, ai_agent):
    """Display issues with individual fix problem buttons"""
    if not result["success"]:
        st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
        return

    st.success("✅ Business Issues Analysis Complete!")
    st.markdown("---")

    st.subheader("⚠️ Critical Business Issues")
    st.caption(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    st.caption(f"Model: {result['model']}")

    issues = result.get("data", {}).get("issues", [])

    if not issues:
        st.info("🎉 No critical issues found! Business is running smoothly.")
        return

    # Display issues with individual fix buttons
    for i, issue in enumerate(issues[:7], 1):  # Limit to 7
        impact = issue.get("impact", "medium")
        category = issue.get("category", "general")

        impact_colors = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }

        category_icons = {
            "payment": "💳",
            "inventory": "📦",
            "customer": "👥",
            "financial": "💰",
            "general": "⚠️"
        }

        emoji = impact_colors.get(impact, "⚪")
        icon = category_icons.get(category, "⚠️")

        with st.container(border=True):
            st.markdown(f"### {icon} Issue #{i}: {issue.get('title', 'Unknown Issue')}")
            st.markdown(f"**Impact:** {emoji} {impact.title()} | **Category:** {category.title()}")
            st.markdown(f"**Affected:** {issue.get('affected_count', 'N/A')}")
            st.markdown("---")
            st.markdown(issue.get('description', 'N/A'))

            st.markdown("")  # Spacing

            # Individual fix button for each issue
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                fix_key = f"fix_issue_{i}"

                # Check if we need to generate fix
                if st.button(f"🔧 Fix Problem", use_container_width=True, type="secondary", key=fix_key):
                    # Mark that we want to show fix for this issue
                    st.session_state[f'show_fix_{i}'] = True
                    st.rerun()

        # Display fix dialog/popup outside the container (after all issues are rendered)
        if st.session_state.get(f'show_fix_{i}'):
            # Generate fix if not already generated
            if not st.session_state.get(f'fix_result_{i}'):
                with st.spinner(f"🛠️ Generating fix for Issue #{i}..."):
                    # Create a temporary issues result with only this issue
                    single_issue_result = {
                        "success": True,
                        "data": {"issues": [issue]},
                        "model": result['model']
                    }
                    fix_result = ai_agent.generate_fixes(single_issue_result)
                    st.session_state[f'fix_result_{i}'] = fix_result

            # Show the fix in a dialog/modal style
            fix_result = st.session_state.get(f'fix_result_{i}')
            if fix_result and fix_result.get('success'):
                fixes = fix_result.get("data", {}).get("fixes", [])
                if fixes:
                    fix = fixes[0]  # Get the first (and only) fix

                    st.markdown("---")
                    st.markdown(f"### 💡 Suggested Fix for Issue #{i}")

                    with st.container(border=True):
                        col_a, col_b = st.columns(2)

                        with col_a:
                            st.markdown(f"**Fix:** {fix.get('fix_title', 'N/A')}")
                            st.markdown(f"**Tool:** {fix.get('tool_to_use', 'manual')}")

                        with col_b:
                            automation_emoji = {
                                "full": "🤖",
                                "partial": "⚙️",
                                "manual": "👤"
                            }.get(fix.get('automation_level', 'manual'), "⚙️")
                            st.markdown(f"**Automation:** {automation_emoji} {fix.get('automation_level', 'manual').title()}")
                            st.markdown(f"**Impact:** {fix.get('estimated_impact', 'N/A')}")

                        st.markdown("---")
                        st.markdown(f"**Description:** {fix.get('description', 'N/A')}")

                        st.markdown("")

                        # Action buttons
                        col_x, col_y, col_z = st.columns([1, 1, 1])

                        with col_x:
                            if st.button("❌ Cancel", use_container_width=True, key=f"cancel_fix_{i}"):
                                st.session_state[f'show_fix_{i}'] = False
                                st.session_state[f'fix_result_{i}'] = None
                                st.rerun()

                        with col_z:
                            if st.button("✅ Accept and Take Action", use_container_width=True, type="primary", key=f"apply_fix_{i}"):
                                # Show preview template dialog
                                st.session_state[f'show_preview_{i}'] = True
                                st.session_state[f'show_fix_{i}'] = False
                                st.rerun()

            # Show preview template dialog if needed
            if st.session_state.get(f'show_preview_{i}'):
                display_action_preview_dialog(i, issue, fix_result, ai_agent)
