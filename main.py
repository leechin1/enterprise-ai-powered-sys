"""
Misty AI Enterprise System
AI-powered enterprise automation platform for Misty Jazz Records

A comprehensive AI ecosystem demonstrating how a small enterprise can leverage
LLM technology to automate processes, gain insights, and optimize operations.
"""

import streamlit as st
from frontend.styles import CUSTOM_CSS
from frontend.components import dashboard, analytics, activity, configuration, ai_reporting, rag


# Logo setup

st.logo(
    "assets/logo.png",
    size="large"
)

# Page configuration
st.set_page_config(
    page_title="Misty- AI Enterprise System",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Misty AI Enterprise System - AI-powered automation for jazz vinyl retail"
    }
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'

# Sidebar navigation
with st.sidebar:
    # Logo and title
    st.markdown(
        """
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="color: #6366F1; margin: 0;">🎵 Misty</h1>
            <p style="color: #94A3B8; font-size: 0.875rem; margin: 0;">AI Enterprise System</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # Navigation menu
    st.markdown("### Navigation")

    # Dashboard
    if st.button("📊 Dashboard", use_container_width=True, type="primary" if st.session_state.page == 'dashboard' else "secondary"):
        st.session_state.page = 'dashboard'
        st.rerun()

    # Analytics
    if st.button("📈 Analytics", use_container_width=True, type="primary" if st.session_state.page == 'analytics' else "secondary"):
        st.session_state.page = 'analytics'
        st.rerun()

    # AI BI Reporting
    if st.button("🤖 AI BI Reporting", use_container_width=True, type="primary" if st.session_state.page == 'ai_reporting' else "secondary"):
        st.session_state.page = 'ai_reporting'
        st.rerun()


    # Knowledge
    if st.button("🧠 Knowledge", use_container_width=True, type="primary" if st.session_state.page == 'knowledge' else "secondary"):
        st.session_state.page = 'knowledge'
        st.rerun()

    st.markdown("---")

    # Admin section
    st.markdown("### Admin")

    if st.button("⚙️ Configuration", use_container_width=True, type="primary" if st.session_state.page == 'configuration' else "secondary"):
        st.session_state.page = 'configuration'
        st.rerun()

    if st.button("🚪 Sign Out", use_container_width=True):
        st.toast("Signing out...")

    st.markdown("---")

    # Version info
    st.caption("Version 1.0.0")
    st.caption("© 2025 Misty Jazz Records")

# Main content area
if st.session_state.page == 'dashboard':
    dashboard.render_dashboard()

elif st.session_state.page == 'analytics':
    analytics.render_analytics()

elif st.session_state.page == 'activity':
    activity.render_activity()


elif st.session_state.page == 'knowledge':
    rag.render_knowledge()

elif st.session_state.page == 'configuration':
    configuration.render_configuration()

elif st.session_state.page == 'ai_reporting':
    ai_reporting.render_ai_reporting()

else:
    # Default to dashboard if unknown page
    st.session_state.page = 'dashboard'
    st.rerun()
