"""
Misty AI Enterprise System
AI-powered enterprise automation platform for Misty Jazz Records
"""

import streamlit as st
import os

# --- 1. SECRETS INJECTION (MUST BE FIRST) ---
# This allows your existing components to use os.getenv() successfully
try:
    if len(st.secrets) > 0:
        for section_name in st.secrets:
            section = st.secrets[section_name]
            if isinstance(section, (dict, st.runtime.secrets.AttrDict)):
                for key, value in section.items():
                    os.environ[key] = str(value)
            else:
                os.environ[section_name] = str(section)
except FileNotFoundError:
    st.error("⚠️ Secrets not configured. Please add secrets in Streamlit Cloud dashboard.")
    st.stop()


# --- 2. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Misty - AI Enterprise System",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "Misty AI Enterprise System - AI-powered automation for jazz vinyl retail"}
)

# --- 3. COMPONENT IMPORTS ---
from frontend.styles import CUSTOM_CSS
from frontend.components import dashboard, analytics, activity, rag, marketing_emails, ai_reporting_agent
from frontend.components.authentication import __login__
from frontend.components import admin_configure
from streamlit_option_menu import option_menu

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- 4. AUTHENTICATION SETUP ---
__login__obj = __login__(
    # Pulling from your migrated secrets.toml [emailjs] section
    auth_token=st.secrets["emailjs"]["EMAILJS_PRIVATE_KEY"], 
    company_name="Shims",
    width=200,
    height=250,
    logout_button_name='Logout',
    hide_menu_bool=True,
    hide_footer_bool=True,
    lottie_url='https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json'
)

LOGGED_IN = __login__obj.build_login_ui()

# Redirect to Login if not logged in
if not LOGGED_IN:
    st.stop()

# --- 5. MAIN APP (ONLY IF LOGGED IN) ---
st.logo("assets/logo.png", size="large")

if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'

with st.sidebar:
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

    selected = option_menu(
        menu_title="Navigation",
        options=["Dashboard", "Analytics", "Business Reporting", "CRM", "Knowledge", "Activity", "Configure"],
        icons=["graph-up", "bar-chart", "robot", "envelope", "book", "activity", "gear"],
        menu_icon="list-columns-reverse",
        default_index=0
    )
    st.session_state.page = selected.lower().replace(" ", "_")

    st.markdown("---")
    
    username = __login__obj.get_username()
    st.session_state['username'] = username
    st.markdown(f"**Logged in as:** {username}")

    if st.button("Logout"):
        __login__obj.logout()  
        st.rerun() # Use rerun instead of manual boolean set for cleaner state reset

    st.markdown("---")
    st.caption("Version 1.0.0")
    st.caption("© 2026 Misty Jazz Records")

# --- 6. ROUTING LOGIC ---
if st.session_state.page == 'dashboard':
    dashboard.render_dashboard()
elif st.session_state.page == 'analytics':
    analytics.render_analytics()
elif st.session_state.page == 'activity':
    activity.render_activity()
elif st.session_state.page == 'knowledge':
    rag.render_knowledge()
elif st.session_state.page == 'crm':
    marketing_emails.render_marketing_emails()
elif st.session_state.page == 'business_reporting':
    ai_reporting_agent.render_ai_reporting_agent()
elif st.session_state.page == 'configure':
    admin_configure.render_admin_configure(company_name="Misty Jazz")
else:
    st.session_state.page = 'dashboard'
    st.rerun()