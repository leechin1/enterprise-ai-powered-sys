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
from services.ai_health_agent import AIHealthAgent
from services.ai_issues_agent import AIIssuesAgent


def render_ai_reporting_agent():
    """Render AI Business Intelligence Reporting page with new agent architecture"""

    st.title("🤖 AI Business Intelligence Reporting")
    st.caption("AI-powered business consultation using Gemini 2.0-flash with LangChain agents")

    # Initialize connectors
    try:
        analytics = AnalyticsConnector()
        health_agent = AIHealthAgent()
        issues_agent = AIIssuesAgent()
    except Exception as e:
        st.error(f"Failed to initialize AI agents: {e}")
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
        render_health_tab(health_agent)

    with tab2:
        render_issues_tab(issues_agent)


def render_health_tab(health_agent):
    """Render the Overall Business Health tab"""
    st.markdown("### 📊 Business Health Analysis")
    st.caption("AI-powered analysis of financial, customer, inventory, and product metrics")

    # Generate button
    if st.button("🎯 Generate Health Analysis", use_container_width=True, type="primary", key="health_generate"):
        with st.spinner("🧠 AI Agent is analyzing your business health..."):
            health_result = health_agent.analyze_business_health()
            st.session_state.health_cache = health_result
            st.rerun()

    # Display results if available
    if st.session_state.get('health_cache'):
        health_result = st.session_state.health_cache
        display_health_results(health_result)
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


def render_issues_tab(issues_agent):
    """Render the Issues & Problems tab with three-stage reasoning"""
    st.markdown("### ⚠️ Business Issues & Problems")
    st.caption("Three-stage AI analysis: SQL Generation → Query Approval → Issue Identification → Fix Proposals")

    # Initialize analytics connector for saved queries
    try:
        from utils.db_analytics import AnalyticsConnector
        analytics = AnalyticsConnector()
        saved_queries_available = True
    except Exception:
        saved_queries_available = False
        analytics = None

    # Check for saved queries
    saved_info = None
    if saved_queries_available and analytics:
        saved_info = analytics.get_saved_queries_info('last_generated')

    # Stage 0 Options: Generate new OR Load saved
    st.markdown("#### Stage 0: SQL Query Generation")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔍 Generate New Queries", use_container_width=True, type="primary", key="sql_generate"):
            with st.spinner("🧠 Stage 0: AI Agent analyzing database schema and generating SQL queries..."):
                sql_result = issues_agent.generate_sql_queries()
                st.session_state.sql_queries_cache = sql_result
                st.session_state.issues_cache = None  # Clear previous results
                st.session_state.fixes_cache = None
                st.session_state.loaded_from_saved = False
                st.rerun()

    with col2:
        if saved_info:
            # Format the saved date nicely
            saved_at = saved_info.get('updated_at', saved_info.get('created_at', 'Unknown'))
            if saved_at and saved_at != 'Unknown':
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(saved_at.replace('Z', '+00:00'))
                    saved_at_formatted = dt.strftime('%b %d, %Y %I:%M %p')
                except:
                    saved_at_formatted = saved_at
            else:
                saved_at_formatted = 'Unknown'

            if st.button(
                f"📂 Load Last Saved ({saved_info['query_count']} queries)",
                use_container_width=True,
                type="secondary",
                key="sql_load_saved",
                help=f"Saved on {saved_at_formatted} using {saved_info.get('model', 'unknown')}"
            ):
                # Load saved queries
                saved_data = analytics.load_saved_queries('last_generated')
                if saved_data and saved_data.get('queries'):
                    # Convert to the format expected by display_sql_queries
                    st.session_state.sql_queries_cache = {
                        "success": True,
                        "type": "sql_queries",
                        "stage": 0,
                        "data": {"queries": saved_data['queries']},
                        "model": saved_data.get('model', 'unknown'),
                        "loaded_from_saved": True,
                        "saved_at": saved_at_formatted
                    }
                    st.session_state.issues_cache = None
                    st.session_state.fixes_cache = None
                    st.session_state.loaded_from_saved = True
                    st.rerun()
                else:
                    st.error("Failed to load saved queries")
        else:
            st.button(
                "📂 No Saved Queries",
                use_container_width=True,
                type="secondary",
                key="sql_no_saved",
                disabled=True,
                help="Generate queries first, then save them for later use"
            )

    # Display Stage 0: SQL Queries for approval
    if st.session_state.get('sql_queries_cache'):
        sql_result = st.session_state.sql_queries_cache

        # Show if loaded from saved
        if sql_result.get('loaded_from_saved') or st.session_state.get('loaded_from_saved'):
            st.info(f"📂 Loaded from saved queries (saved: {sql_result.get('saved_at', 'Unknown')})")

        display_sql_queries(sql_result, issues_agent, analytics)

        st.markdown("---")

    # Display Stage 1: Issues if available
    if st.session_state.get('issues_cache'):
        issues_result = st.session_state.issues_cache
        display_issues_results(issues_result)

        st.markdown("---")

        # Stage 2: Generate Fixes button
        if st.button("🔧 Stage 2: Propose Fixes", use_container_width=True, type="secondary", key="fixes_generate"):
            with st.spinner("🛠️ Stage 2: AI Agent proposing fixes using available business tools..."):
                issues = issues_result.get('data', {}).get('issues', [])
                fixes_result = issues_agent.propose_fixes(issues)
                st.session_state.fixes_cache = fixes_result
                st.rerun()

        # Display Stage 2 results if available
        if st.session_state.get('fixes_cache'):
            fixes_result = st.session_state.fixes_cache
            display_fixes_results(fixes_result)

    elif not st.session_state.get('sql_queries_cache'):
        st.info("👆 Click 'Stage 0: Generate SQL Queries' to start the three-stage analysis")
        with st.expander("🔍 How It Works", expanded=False):
            st.markdown("""
            **Stage 0: SQL Query Generation**
            - AI analyzes the database schema
            - Generates 5-10 SQL queries to investigate potential issues
            - You review and approve queries before execution

            **Stage 1: Issue Identification**
            - Executes approved SQL queries
            - AI analyzes results to identify 7 critical issues
            - Provides detailed descriptions with specific data

            **Stage 2: Fix Proposals**
            - AI proposes concrete fixes for each issue
            - Suggests which business tools to use
            - Provides step-by-step action plans
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


def display_sql_queries(sql_result, issues_agent, analytics=None):
    """Display generated SQL queries for user approval"""
    if not sql_result["success"]:
        st.error(f"❌ SQL Generation failed: {sql_result.get('error', 'Unknown error')}")
        return

    st.success("✅ SQL Queries Generated!")
    st.markdown("---")

    st.subheader("📝 Generated SQL Queries")
    st.caption(f"Review and approve these queries before execution | Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    st.caption(f"Model: {sql_result['model']}")

    queries = sql_result.get("data", {}).get("queries", [])

    if not queries:
        st.warning("No queries generated. Please try again.")
        return

    # Display queries in expandable sections
    for i, query in enumerate(queries, 1):
        priority = query.get("priority", "medium")
        priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(priority, "⚪")

        with st.expander(f"{priority_emoji} Query {query.get('query_id', i)}: {query.get('purpose', 'Unknown')}", expanded=(i == 1)):
            # Non-technical explanation
            st.markdown("**What this query does (for business users):**")
            st.info(query.get('explanation', 'No explanation provided'))

            # SQL Query
            st.markdown("**SQL Query:**")
            st.code(query.get('sql_query', ''), language='sql')

            # Priority
            st.markdown(f"**Priority:** {priority_emoji} {priority.upper()}")

    st.markdown("---")

    # Action buttons row
    col1, col2 = st.columns([3, 1])

    with col2:
        # Save queries button (only if analytics is available and queries weren't loaded from saved)
        if analytics and not sql_result.get('loaded_from_saved'):
            if st.button("💾 Save Queries", use_container_width=True, key="save_queries"):
                with st.spinner("Saving queries..."):
                    success = analytics.save_generated_queries(
                        queries=queries,
                        model=sql_result.get('model', 'unknown')
                    )
                    if success:
                        st.success("✅ Queries saved!")
                        st.session_state.queries_saved = True
                    else:
                        st.error("Failed to save queries")

            # Show saved indicator
            if st.session_state.get('queries_saved'):
                st.caption("✅ Saved to database")

    with col1:
        # Accept all queries button
        execute_clicked = st.button("✅ Accept All Queries & Execute (Stage 1)", use_container_width=True, type="primary", key="execute_queries")

    if execute_clicked:
        with st.spinner("⚙️ Executing SQL queries and analyzing results..."):
            # Execute queries
            execution_result = issues_agent.execute_sql_queries(queries)

            if not execution_result['success']:
                st.error(f"❌ Query execution failed: {execution_result.get('error', 'Unknown error')}")
                return

            # Show execution summary
            st.success(f"✅ Executed {execution_result['successful_queries']}/{execution_result['total_queries']} queries successfully!")

            # Analyze results with Stage 1 agent
            query_results = execution_result['results']
            issues_result = issues_agent.identify_business_issues(query_results)

            st.session_state.issues_cache = issues_result
            st.session_state.query_results_cache = query_results  # Store for reference
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
        severity = issue.get("severity", "medium")
        category = issue.get("category", "operations")

        severity_colors = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡"
        }

        category_icons = {
            "inventory": "📦",
            "payments": "💳",
            "customers": "👥",
            "revenue": "💰",
            "operations": "⚙️",
            "data_quality": "📊",
            "financial": "💵"
        }

        emoji = severity_colors.get(severity, "⚪")
        icon = category_icons.get(category, "⚠️")

        with st.container(border=True):
            st.markdown(f"### {icon} Issue #{i}: {issue.get('title', 'Unknown Issue')}")
            st.markdown(f"**Severity:** {emoji} {severity.title()} | **Category:** {category.title()}")
            if issue.get('affected_metrics'):
                st.markdown(f"**Affected Metrics:** {', '.join(issue['affected_metrics'])}")
            st.markdown("---")
            st.markdown(issue.get('description', 'N/A'))


def display_fixes_results(result):
    """Display proposed fixes for identified issues"""
    if not result["success"]:
        st.error(f"❌ Fix generation failed: {result.get('error', 'Unknown error')}")
        return

    st.success("✅ Fix Proposals Generated!")
    st.markdown("---")

    st.subheader("🔧 Proposed Fixes")
    st.caption(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    st.caption(f"Model: {result['model']}")

    fixes = result.get("data", {}).get("fixes", [])

    if not fixes:
        st.warning("No fixes could be generated at this time.")
        return

    # Display fixes in expandable cards
    for i, fix in enumerate(fixes, 1):
        priority = fix.get("priority", "scheduled")

        priority_colors = {
            "immediate": "🔴",
            "urgent": "🟠",
            "scheduled": "🟢"
        }

        emoji = priority_colors.get(priority, "⚪")

        with st.expander(f"{emoji} Fix #{i}: {fix.get('fix_title', 'Unknown Fix')}", expanded=(i == 1)):
            st.markdown(f"**Addressing Issue:** {fix.get('issue_id', 'N/A')}")
            st.markdown(f"**Priority:** {emoji} {priority.title()}")

            if fix.get('tools_to_use'):
                tools_list = ", ".join([f"`{tool}`" for tool in fix['tools_to_use']])
                st.markdown(f"**Tools to Use:** {tools_list}")

            st.markdown("---")
            st.markdown("**📋 What Needs to Be Done:**")
            st.markdown(fix.get('fix_description', 'N/A'))

            st.markdown("---")
            st.markdown("**🔢 Action Steps:**")
            for step_idx, step in enumerate(fix.get('action_steps', []), 1):
                st.markdown(f"{step_idx}. {step}")

            st.markdown("---")
            st.markdown(f"**📈 Expected Outcome:** {fix.get('expected_outcome', 'N/A')}")

            # Action button (placebo)
            if st.button(f"✅ Execute Fix #{i}", key=f"execute_fix_{i}", type="primary"):
                with st.spinner(f"Executing fix #{i}..."):
                    import time
                    time.sleep(2)
                st.success(f"✅ Fix #{i} executed successfully!")
                st.balloons()


def display_fixes(fixes_result):
    """Display suggested fixes (DEPRECATED - use display_fixes_results instead)"""
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
