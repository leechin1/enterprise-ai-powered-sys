"""
Admin Configure Component
User settings, password change with email verification, and user management
"""

import streamlit as st
from auth.auth_service import get_auth_service, check_valid_name, check_valid_email
from services.auth_email_service import get_auth_email_service


def render_user_profile(current_user: dict):
    """Render the user profile information card"""

    # Profile card
    st.markdown("""
        <style>
        .profile-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 24px;
            color: white;
            margin-bottom: 20px;
        }
        .profile-name {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 4px;
        }
        .profile-role {
            font-size: 14px;
            opacity: 0.9;
            background: rgba(255,255,255,0.2);
            padding: 4px 12px;
            border-radius: 20px;
            display: inline-block;
        }
        </style>
    """, unsafe_allow_html=True)

    role = "Administrator" if current_user.get('is_admin', False) else "User"
    role_icon = "" if current_user.get('is_admin', False) else ""

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"### {current_user.get('name', 'N/A')}")
        st.caption(f"{role_icon} {role}")

    with col2:
        status = "Active" if current_user.get('is_active', True) else "Inactive"
        st.metric("Status", status)

    # Details in expandable section
    with st.expander("Profile Details", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Username:** `{current_user.get('username', 'N/A')}`")
            st.write(f"**Email:** {current_user.get('email', 'N/A')}")

        with col2:
            created = current_user.get('created_at', '')[:10] if current_user.get('created_at') else 'N/A'
            st.write(f"**Member since:** {created}")

            last_login = current_user.get('last_login')
            if last_login:
                st.write(f"**Last login:** {last_login[:16].replace('T', ' ')}")


def render_password_change(current_user: dict, company_name: str = "Misty Jazz"):
    """Render password change section with email verification"""

    auth_service = get_auth_service()
    email_service = get_auth_email_service()

    # Initialize session state
    if 'password_reset_requested' not in st.session_state:
        st.session_state.password_reset_requested = False
    if 'password_reset_token_sent' not in st.session_state:
        st.session_state.password_reset_token_sent = False

    st.markdown("#### Change Password")
    st.caption("For security, a verification token will be sent to your email")

    if not st.session_state.password_reset_requested:
        # Step 1: Request token
        st.info(f"A verification token will be sent to: **{current_user['email']}**")

        if st.button("Request Password Change", type="primary", use_container_width=True):
            token = auth_service.generate_password_reset_token(current_user['email'])

            result = email_service.send_password_reset_token(
                to_email=current_user['email'],
                to_name=current_user.get('name', 'User'),
                token=token,
                company_name=company_name
            )

            st.session_state.password_reset_requested = True

            if result.get('success'):
                st.session_state.password_reset_token_sent = True
            else:
                st.session_state.password_reset_token_sent = False
                st.session_state.manual_token = token

            st.rerun()
    else:
        # Step 2: Enter token and new password
        if st.session_state.get('password_reset_token_sent'):
            st.success("Verification token sent! Check your email.")
        else:
            st.warning("Could not send email automatically.")
            if 'manual_token' in st.session_state:
                st.info("Your verification token:")
                st.code(st.session_state.manual_token, language=None)

        with st.form("password_change_form"):
            verification_token = st.text_input(
                "Verification Token *",
                placeholder="Paste the token from your email"
            )

            new_password = st.text_input(
                "New Password *",
                type="password",
                placeholder="Min 8 characters"
            )

            confirm_password = st.text_input(
                "Confirm Password *",
                type="password",
                placeholder="Re-enter password"
            )

            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Update Password", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("Cancel", use_container_width=True)

            if cancel:
                st.session_state.password_reset_requested = False
                st.session_state.password_reset_token_sent = False
                if 'manual_token' in st.session_state:
                    del st.session_state.manual_token
                st.rerun()

            if submit:
                if not verification_token or not verification_token.strip():
                    st.error("Please enter the verification token")
                elif not new_password:
                    st.error("Please enter a new password")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters")
                elif new_password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    is_valid, _ = auth_service.validate_token(
                        current_user['email'],
                        verification_token.strip(),
                        'password_reset'
                    )

                    if is_valid:
                        if auth_service.change_password(current_user['email'], new_password):
                            auth_service.mark_token_used(verification_token.strip())

                            email_service.send_password_change_confirmation(
                                to_email=current_user['email'],
                                to_name=current_user.get('name', 'User'),
                                company_name=company_name
                            )

                            st.success("Password updated successfully!")
                            st.session_state.password_reset_requested = False
                            st.session_state.password_reset_token_sent = False
                            if 'manual_token' in st.session_state:
                                del st.session_state.manual_token
                        else:
                            st.error("Failed to update password")
                    else:
                        st.error("Invalid or expired token")


def render_invite_user(current_user: dict, company_name: str = "Misty Jazz"):
    """Render the invite new user form"""

    auth_service = get_auth_service()
    email_service = get_auth_email_service()

    st.markdown("#### Invite New User")
    st.caption("Send an invitation to create an account")

    with st.form("invite_user_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Full Name *", placeholder="John Doe")
            email = st.text_input("Email *", placeholder="john@example.com")

        with col2:
            username = st.text_input("Username *", placeholder="johndoe")
            make_admin = st.checkbox("Make Admin", help="Grant administrator privileges to this user")

        submit = st.form_submit_button("Send Invitation", type="primary", use_container_width=True)

        if submit:
            # Validation
            name_error = check_valid_name(name) if name else "Name is required"
            email_error = check_valid_email(email) if email else "Email is required"

            if not name or not name.strip():
                st.error("Please enter a name")
            elif name_error:
                st.error(name_error)
            elif not email or not email.strip():
                st.error("Please enter an email")
            elif email_error:
                st.error(email_error)
            elif not username or not username.strip():
                st.error("Please enter a username")
            elif not auth_service.check_unique_email(email.strip()):
                st.error("This email is already registered")
            elif not auth_service.check_unique_usr(username.strip()):
                st.error("This username is already taken")
            else:
                # Generate token and send invitation
                token = auth_service.generate_account_creation_token(
                    email=email.strip(),
                    name=name.strip(),
                    username=username.strip(),
                    created_by_user_id=current_user.get('user_id')
                )

                result = email_service.send_account_invitation(
                    to_email=email.strip(),
                    to_name=name.strip(),
                    token=token,
                    username=username.strip(),
                    invited_by=current_user.get('name', 'Admin'),
                    company_name=company_name
                )

                if result.get('success'):
                    st.success(f"Invitation sent to {email}!")
                    st.balloons()
                else:
                    st.warning("Could not send email automatically")

                # Always show the token for reference
                with st.expander("Invitation Token (for reference)", expanded=not result.get('success')):
                    st.code(token, language=None)
                    st.caption(f"Share this token with {name}. They'll need it to create their account.")


def render_manage_users():
    """Render the user management list"""

    auth_service = get_auth_service()
    users = auth_service.get_all_users()

    st.markdown("#### Manage Users")

    if not users:
        st.info("No users found")
        return

    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Users", len(users))
    with col2:
        active = sum(1 for u in users if u.get('is_active', False))
        st.metric("Active", active)
    with col3:
        admins = sum(1 for u in users if u.get('is_admin', False))
        st.metric("Admins", admins)

    st.markdown("---")

    # User list
    current_username = st.session_state.get('username', '')

    for user in users:
        is_current = user['username'] == current_username
        admin_badge = " (Admin)" if user.get('is_admin') else ""
        status_icon = "" if user.get('is_active') else ""
        you_badge = " - You" if is_current else ""

        with st.expander(f"{status_icon} {user['name']} @{user['username']}{admin_badge}{you_badge}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**Email:** {user['email']}")
                created = user.get('created_at', '')[:10] if user.get('created_at') else 'N/A'
                st.write(f"**Created:** {created}")

            with col2:
                if not is_current:
                    # Toggle admin
                    if user.get('is_admin'):
                        if st.button("Remove Admin", key=f"rm_admin_{user['user_id']}"):
                            auth_service.set_user_admin_status(user['user_id'], False)
                            st.rerun()
                    else:
                        if st.button("Make Admin", key=f"mk_admin_{user['user_id']}"):
                            auth_service.set_user_admin_status(user['user_id'], True)
                            st.rerun()

                    # Deactivate
                    if user.get('is_active'):
                        if st.button("Deactivate", key=f"deact_{user['user_id']}"):
                            auth_service.deactivate_user(user['user_id'])
                            st.rerun()


def render_admin_configure(company_name: str = "Misty Jazz"):
    """Main configure page with tabs"""

    auth_service = get_auth_service()
    current_username = st.session_state.get('username', '')
    current_user = auth_service.get_user_by_username(current_username)

    if not current_user:
        st.error("Could not load user information. Please try logging in again.")
        st.info(f"Looking for username: {current_username}")
        return

    # Page header
    st.title("Settings")

    # Profile section at top
    render_user_profile(current_user)

    st.markdown("---")

    # Check if admin
    is_admin = current_user.get('is_admin', False)

    if is_admin:
        # Admin gets tabs
        tab1, tab2, tab3 = st.tabs(["Security", "Invite Users", "Manage Users"])

        with tab1:
            render_password_change(current_user, company_name)

        with tab2:
            render_invite_user(current_user, company_name)

        with tab3:
            render_manage_users()
    else:
        # Regular users only see security
        st.markdown("### Security")
        render_password_change(current_user, company_name)

        st.markdown("---")
        st.caption("Contact an administrator if you need additional permissions.")
