"""
Configuration and Settings component for Misty AI Enterprise System
"""
import streamlit as st

def render_configuration():
    """Render the configuration and settings interface"""

    st.title("Configuration & Settings")
    st.caption("Manage system settings, AI models, and integrations")

    # Tabs for different configuration sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⚙️ General",
        "🤖 AI Models",
        "🔌 Integrations",
        "👥 Users & Permissions",
        "🔔 Notifications"
    ])

    with tab1:
        render_general_settings()

    with tab2:
        render_ai_model_settings()

    with tab3:
        render_integrations()

    with tab4:
        render_users_permissions()

    with tab5:
        render_notifications()


def render_general_settings():
    """General system settings"""

    st.subheader("General Settings")

    # Business Information
    with st.expander("🏢 Business Information", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Business Name", value="Misty Jazz Records")
            st.text_input("Email", value="contact@mistyjazz.com")
            st.text_input("Phone", value="+1 (555) 123-4567")

        with col2:
            st.text_input("Website", value="https://mistyjazz.com")
            st.text_input("Address", value="123 Jazz Street, Music City")
            st.selectbox("Timezone", ["America/New_York", "America/Los_Angeles", "Europe/London"])

    # Operational Settings
    with st.expander("⏰ Operational Settings", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Business Hours", value="9:00 AM - 9:00 PM")
            st.multiselect(
                "Operating Days",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            )

        with col2:
            st.selectbox("Currency", ["USD", "EUR", "GBP", "CAD"])
            st.number_input("Tax Rate (%)", min_value=0.0, max_value=100.0, value=8.5, step=0.1)

    # System Preferences
    with st.expander("🎨 Display & Preferences", expanded=False):
        st.selectbox("Theme", ["Dark", "Light", "Auto"])
        st.selectbox("Language", ["English", "Spanish", "French", "German"])
        st.slider("Data Retention (days)", min_value=30, max_value=365, value=90)

    if st.button("💾 Save General Settings", type="primary"):
        st.success("Settings saved successfully!")


def render_ai_model_settings():
    """AI model configuration"""

    st.subheader("AI Model Configuration")

    # Model Selection
    with st.expander("🧠 Active AI Models", expanded=True):
        models = [
            {
                'name': 'Customer Recommendation Engine',
                'model': 'GPT-4o',
                'status': 'Active',
                'accuracy': '94.2%'
            },
            {
                'name': 'Inventory Demand Forecasting',
                'model': 'Claude Sonnet 4.5',
                'status': 'Active',
                'accuracy': '92.7%'
            },
            {
                'name': 'Customer Sentiment Analysis',
                'model': 'GPT-4o-mini',
                'status': 'Active',
                'accuracy': '88.5%'
            },
            {
                'name': 'Fraud Detection',
                'model': 'Custom ML Model',
                'status': 'Active',
                'accuracy': '97.3%'
            },
        ]

        for model in models:
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

            with col1:
                st.write(f"**{model['name']}**")
            with col2:
                st.write(f"Model: {model['model']}")
            with col3:
                st.write(f"🎯 {model['accuracy']}")
            with col4:
                st.button("⚙️", key=f"config_{model['name']}")

    # Model Parameters
    with st.expander("🎛️ Model Parameters", expanded=False):
        st.markdown("### Recommendation Engine")

        col1, col2 = st.columns(2)

        with col1:
            st.slider("Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1)
            st.slider("Top P", min_value=0.0, max_value=1.0, value=0.9, step=0.05)

        with col2:
            st.number_input("Max Tokens", min_value=100, max_value=4000, value=1000)
            st.number_input("Recommendation Count", min_value=1, max_value=20, value=5)

        st.markdown("### Demand Forecasting")

        col1, col2 = st.columns(2)

        with col1:
            st.number_input("Forecast Horizon (days)", min_value=7, max_value=90, value=30)
            st.slider("Confidence Threshold", min_value=0.5, max_value=0.99, value=0.85, step=0.01)

        with col2:
            st.selectbox("Seasonality", ["Auto", "Weekly", "Monthly", "Quarterly"])
            st.checkbox("Include External Factors", value=True)

    # API Keys
    with st.expander("🔑 API Keys & Credentials", expanded=False):
        st.text_input("OpenAI API Key", value="sk-••••••••••••••••", type="password")
        st.text_input("Anthropic API Key", value="sk-ant-••••••••••••", type="password")
        st.text_input("Custom ML Endpoint", value="https://api.misty-ml.com/v1")

    if st.button("💾 Save AI Model Settings", type="primary"):
        st.success("AI model settings saved successfully!")


def render_integrations():
    """Third-party integrations"""

    st.subheader("Integrations")

    # Connected Integrations
    st.markdown("### Connected Services")

    integrations = [
        {
            'name': 'Stripe',
            'category': 'Payment Processing',
            'status': 'Connected',
            'icon': '💳'
        },
        {
            'name': 'Shopify',
            'category': 'E-commerce Platform',
            'status': 'Connected',
            'icon': '🛒'
        },
        {
            'name': 'SendGrid',
            'category': 'Email Service',
            'status': 'Connected',
            'icon': '📧'
        },
        {
            'name': 'Google Analytics',
            'category': 'Analytics',
            'status': 'Connected',
            'icon': '📊'
        },
    ]

    for integration in integrations:
        col1, col2, col3, col4 = st.columns([1, 3, 2, 2])

        with col1:
            st.markdown(f"<h2>{integration['icon']}</h2>", unsafe_allow_html=True)

        with col2:
            st.write(f"**{integration['name']}**")
            st.caption(integration['category'])

        with col3:
            st.write(f"✅ {integration['status']}")

        with col4:
            col_config, col_disconnect = st.columns(2)
            with col_config:
                st.button("⚙️", key=f"config_int_{integration['name']}")
            with col_disconnect:
                st.button("🔌", key=f"disconnect_{integration['name']}")

    st.markdown("---")

    # Available Integrations
    st.markdown("### Available Integrations")

    available = [
        {'name': 'Mailchimp', 'category': 'Email Marketing', 'icon': '📬'},
        {'name': 'Slack', 'category': 'Team Communication', 'icon': '💬'},
        {'name': 'Zapier', 'category': 'Automation', 'icon': '⚡'},
        {'name': 'QuickBooks', 'category': 'Accounting', 'icon': '💰'},
    ]

    cols = st.columns(4)

    for idx, integration in enumerate(available):
        with cols[idx]:
            st.markdown(f"<h2 style='text-align: center;'>{integration['icon']}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center;'><strong>{integration['name']}</strong></p>", unsafe_allow_html=True)
            st.caption(integration['category'])
            st.button("+ Connect", key=f"connect_{integration['name']}", use_container_width=True)


def render_users_permissions():
    """User management and permissions"""

    st.subheader("Users & Permissions")

    # Add new user button
    if st.button("➕ Add New User", type="primary"):
        st.toast("Opening user creation form...")

    st.markdown("---")

    # User list
    users = [
        {
            'name': 'Sarah Mitchell',
            'email': 'sarah@mistyjazz.com',
            'role': 'Admin',
            'status': 'Active',
            'last_login': '2 hours ago'
        },
        {
            'name': 'James Rodriguez',
            'email': 'james@mistyjazz.com',
            'role': 'Manager',
            'status': 'Active',
            'last_login': '5 hours ago'
        },
        {
            'name': 'Emily Chen',
            'email': 'emily@mistyjazz.com',
            'role': 'Staff',
            'status': 'Active',
            'last_login': '1 day ago'
        },
        {
            'name': 'AI Agent',
            'email': 'ai@mistyjazz.com',
            'role': 'System',
            'status': 'Active',
            'last_login': '1 minute ago'
        },
    ]

    for user in users:
        with st.expander(f"{user['name']} - {user['role']}", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Email:** {user['email']}")
                st.write(f"**Role:** {user['role']}")
                st.write(f"**Status:** {user['status']}")
                st.write(f"**Last Login:** {user['last_login']}")

            with col2:
                st.button("✏️ Edit", key=f"edit_user_{user['name']}", use_container_width=True)
                st.button("🔒 Reset Password", key=f"reset_{user['name']}", use_container_width=True)
                if user['role'] != 'System':
                    st.button("🗑️ Remove", key=f"remove_{user['name']}", use_container_width=True)

    st.markdown("---")

    # Role Permissions
    st.markdown("### Role Permissions")

    roles = {
        'Admin': ['All Permissions'],
        'Manager': ['View Analytics', 'Manage Inventory', 'Manage Orders', 'Configure Workflows', 'View Reports'],
        'Staff': ['View Inventory', 'Process Orders', 'Customer Service'],
        'System': ['API Access', 'Automation Execution', 'Data Processing']
    }

    selected_role = st.selectbox("View Permissions for Role", list(roles.keys()))

    st.write(f"**Permissions for {selected_role}:**")
    for permission in roles[selected_role]:
        st.write(f"✅ {permission}")


def render_notifications():
    """Notification settings"""

    st.subheader("Notification Settings")

    # Email Notifications
    with st.expander("📧 Email Notifications", expanded=True):
        st.checkbox("New Order Notifications", value=True)
        st.checkbox("Low Stock Alerts", value=True)
        st.checkbox("Customer Service Tickets", value=True)
        st.checkbox("Daily Sales Summary", value=True)
        st.checkbox("Weekly Analytics Report", value=True)
        st.checkbox("System Errors", value=True)

    # Slack Notifications
    with st.expander("💬 Slack Notifications", expanded=False):
        st.text_input("Slack Webhook URL", placeholder="https://hooks.slack.com/services/...")

        st.checkbox("Critical Alerts", value=True)
        st.checkbox("Order Updates", value=False)
        st.checkbox("Workflow Failures", value=True)

    # SMS Notifications
    with st.expander("📱 SMS Notifications", expanded=False):
        st.text_input("Phone Number", placeholder="+1 (555) 123-4567")

        st.checkbox("Critical System Alerts Only", value=True)
        st.checkbox("Fraud Detection Alerts", value=True)

    # Alert Thresholds
    with st.expander("⚠️ Alert Thresholds", expanded=False):
        st.number_input("Low Stock Threshold (units)", min_value=1, max_value=50, value=5)
        st.number_input("High Value Order Alert ($)", min_value=100, max_value=10000, value=500)
        st.slider("Failure Rate Alert (%)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)

    if st.button("💾 Save Notification Settings", type="primary"):
        st.success("Notification settings saved successfully!")
