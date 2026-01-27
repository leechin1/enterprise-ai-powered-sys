"""
Admin User Management Component
Allows admins to create new user invitations and manage existing users
"""

import streamlit as st
from auth.auth_service import get_auth_service, check_valid_name, check_valid_email
from services.auth_email_service import get_auth_email_service


def render_admin_user_creation(company_name: str = "Misty Jazz"):
    """
    Render the admin user creation interface.
    Admin can invite new users by generating tokens sent via email.

    Args:
        company_name: Company name for email branding
    """
    st.subheader("Create New User Profile")
    st.caption("Generate an invitation for a new user to join the system")

    auth_service = get_auth_service()
    email_service = get_auth_email_service()

    with st.form("admin_create_user_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Full Name *",
                placeholder="Enter user's full name"
            )
            email = st.text_input(
                "Email Address *",
                placeholder="Enter user's email"
            )

        with col2:
            username = st.text_input(
                "Username *",
                placeholder="Choose a username for this user"
            )

        st.markdown("---")
        submit = st.form_submit_button("Generate Invitation & Send Email", type="primary")

        if submit:
            # Validation
            name_error = check_valid_name(name)
            email_error = check_valid_email(email)

            if not name or not name.strip():
                st.error("Please enter a name")
            elif name_error:
                st.error(name_error)
            elif not email or not email.strip():
                st.error("Please enter an email address")
            elif email_error:
                st.error(email_error)
            elif not username or not username.strip():
                st.error("Please enter a username")
            elif not auth_service.check_unique_email(email.strip()):
                st.error("Email is already registered!")
            elif not auth_service.check_unique_usr(username.strip()):
                st.error("Username is already taken!")
            else:
                # Get current admin user ID
                current_username = st.session_state.get('username', '')
                admin_user = auth_service.get_user_by_username(current_username)

                if admin_user:
                    # Generate token
                    token = auth_service.generate_account_creation_token(
                        email=email.strip(),
                        name=name.strip(),
                        username=username.strip(),
                        created_by_user_id=admin_user.get('user_id')
                    )

                    # Send invitation email
                    result = email_service.send_account_invitation(
                        to_email=email.strip(),
                        to_name=name.strip(),
                        token=token,
                        username=username.strip(),
                        invited_by=admin_user.get('name', 'Admin'),
                        company_name=company_name
                    )

                    if result.get('success'):
                        st.success(f"Invitation sent to {email}!")
                        with st.expander("Token Details (for reference)"):
                            st.code(token)
                            st.caption("The user will receive this token via email")
                    else:
                        st.warning(f"Could not send email automatically.")
                        st.info(f"Please share this token manually with the user:")
                        st.code(token)
                        st.caption(f"Instruct {name} to go to Create Account page and enter their email and this token.")
                else:
                    st.error("Could not verify admin user. Please ensure you are logged in.")


def render_user_list():
    """
    Render list of all users (admin view) with management options.
    """
    st.subheader("System Users")

    auth_service = get_auth_service()
    users = auth_service.get_all_users()

    if users:
        # Summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Users", len(users))
        with col2:
            active_count = sum(1 for u in users if u.get('is_active', False))
            st.metric("Active Users", active_count)
        with col3:
            admin_count = sum(1 for u in users if u.get('is_admin', False))
            st.metric("Administrators", admin_count)

        st.markdown("---")

        # User list
        for user in users:
            status_icon = "" if user.get('is_active', False) else ""
            admin_badge = " (Admin)" if user.get('is_admin', False) else ""

            with st.expander(f"{status_icon} {user['name']} (@{user['username']}){admin_badge}", expanded=False):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Email:** {user['email']}")
                    st.write(f"**Username:** {user['username']}")
                    st.write(f"**Status:** {'Active' if user.get('is_active', False) else 'Inactive'}")
                    st.write(f"**Role:** {'Administrator' if user.get('is_admin', False) else 'User'}")

                    # Format dates
                    created_at = user.get('created_at', '')[:10] if user.get('created_at') else 'N/A'
                    last_login = user.get('last_login', '')[:10] if user.get('last_login') else 'Never'
                    st.write(f"**Created:** {created_at}")
                    st.write(f"**Last Login:** {last_login}")

                with col2:
                    # Don't allow modifying yourself
                    current_username = st.session_state.get('username', '')
                    if user['username'] != current_username:
                        # Toggle admin status
                        if not user.get('is_admin', False):
                            if st.button("Make Admin", key=f"admin_{user['user_id']}", type="secondary"):
                                if auth_service.set_user_admin_status(user['user_id'], True):
                                    st.success(f"{user['name']} is now an admin")
                                    st.rerun()
                        else:
                            if st.button("Remove Admin", key=f"remove_admin_{user['user_id']}", type="secondary"):
                                if auth_service.set_user_admin_status(user['user_id'], False):
                                    st.success(f"{user['name']} is no longer an admin")
                                    st.rerun()

                        # Deactivate user
                        if user.get('is_active', False):
                            if st.button("Deactivate", key=f"deactivate_{user['user_id']}", type="secondary"):
                                if auth_service.deactivate_user(user['user_id']):
                                    st.success(f"{user['name']} has been deactivated")
                                    st.rerun()
                    else:
                        st.caption("(Current user)")
    else:
        st.info("No users found in the system")


def render_admin_user_management(company_name: str = "Misty Jazz"):
    """
    Main function to render the complete admin user management interface.

    Args:
        company_name: Company name for email branding
    """
    auth_service = get_auth_service()

    # Check if current user is admin
    current_username = st.session_state.get('username', '')
    if not auth_service.is_user_admin(current_username):
        st.warning("You must be an administrator to access user management.")
        return

    # Tabs for different management functions
    tab1, tab2 = st.tabs(["Invite New User", "Manage Users"])

    with tab1:
        render_admin_user_creation(company_name)

    with tab2:
        render_user_list()
