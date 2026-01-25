"""
Misty AI Enterprise System
AI-powered enterprise automation platform for Misty Jazz Records
"""

import streamlit as st
from frontend.styles import CUSTOM_CSS
from frontend.components import dashboard, analytics, activity, rag, marketing_emails, ai_reporting_agent
from frontend.components.authentication import __login__

# Page configuration
st.set_page_config(
    page_title="Misty- AI Enterprise System",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "Misty AI Enterprise System - AI-powered automation for jazz vinyl retail"}
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Authentication Setup
__login__obj = __login__(
    auth_token="courier_auth_token",  # Replace with st.secrets
    company_name="Shims",
    width=200,
    height=250,
    logout_button_name='Logout',
    hide_menu_bool=True,
    hide_footer_bool=True,
    lottie_url='https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json'
)

LOGGED_IN = __login__obj.build_login_ui()
username = __login__obj.get_username()


# Redirect to Login if not logged in
if not LOGGED_IN:
    # Stop Streamlit from rendering the rest of the app
    st.stop()


# Main App (only if logged in)
# Logo setup
st.logo("assets/logo.png", size="large")

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'


# Sidebar
from streamlit_option_menu import option_menu

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
    selected = option_menu(
        menu_title="Navigation",
        options=["Dashboard", "Analytics", "Business Reporting", "CRM", "Knowledge"],
        icons=["graph-up", "bar-chart", "robot", "envelope", "book"],
        menu_icon="list-columns-reverse",
        default_index=0
    )
    st.session_state.page = selected.lower().replace(" ", "_")

    st.markdown("---")

    # Logged-in user
    username = __login__obj.get_username()
    st.markdown(f"**Logged in as:** {username}")

    # Logout button
    if st.button(__login__obj.logout_button_name):
        __login__obj.logout()  
        st.session_state.LOGGED_IN = False

    st.markdown("---")
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

elif st.session_state.page == 'marketing_emails':
    marketing_emails.render_marketing_emails()

elif st.session_state.page == 'ai_reporting_agent':
    ai_reporting_agent.render_ai_reporting_agent()

else:
    # Default to dashboard if unknown page
    st.session_state.page = 'dashboard'
    st.rerun()
