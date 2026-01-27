import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from streamlit_cookies_manager import EncryptedCookieManager

from auth.auth_service import (
    check_usr_pass,
    load_lottie,
    check_valid_email,
    check_email_exists,
    generate_random_passwd,
    change_passwd,
    check_current_passwd,
    get_auth_service
)
from services.auth_email_service import get_auth_email_service


class __login__:
    """
    Builds the UI for the Login/ Sign Up page.
    """

    def __init__(
        self,
        auth_token: str,
        company_name: str,
        width,
        height,
        logout_button_name: str = 'Logout',
        hide_menu_bool: bool = False,
        hide_footer_bool: bool = False,
        lottie_url: str = "https://assets8.lottiefiles.com/packages/lf20_ktwnwv5m.json"
    ):
        """
        Arguments:
        -----------
        1. self
        2. auth_token : The unique authorization token (kept for backward compatibility)
        3. company_name : This is the name of the person/ organization which will send emails.
        4. width : Width of the animation on the login page.
        5. height : Height of the animation on the login page.
        6. logout_button_name : The logout button name.
        7. hide_menu_bool : Pass True if the streamlit menu should be hidden.
        8. hide_footer_bool : Pass True if the 'made with streamlit' footer should be hidden.
        9. lottie_url : The lottie animation to use on the login page.
        """
        self.auth_token = auth_token
        self.company_name = company_name
        self.width = width
        self.height = height
        self.logout_button_name = logout_button_name
        self.hide_menu_bool = hide_menu_bool
        self.hide_footer_bool = hide_footer_bool
        self.lottie_url = lottie_url

        # Initialize auth service
        self.auth_service = get_auth_service()
        self.auth_email_service = get_auth_email_service()

        self.cookies = EncryptedCookieManager(
            prefix="streamlit_login_ui_cookies",
            password='9d68d6f2-4258-45c9-96eb-2d6bc74ddbb5-d8f49cab-edbb-404a-94d0-b25b1d4a564b'
        )

        if not self.cookies.ready():
            st.stop()

    def get_username(self):
        if st.session_state['LOGOUT_BUTTON_HIT'] == False:
            fetched_cookies = self.cookies
            if '__streamlit_login_signup_ui_username__' in fetched_cookies.keys():
                username = fetched_cookies['__streamlit_login_signup_ui_username__']
                return username

    def login_widget(self) -> None:
        """
        Creates the login widget and authenticates the user, redirecting to the application
        """
        # Attempt automatic login using stored authentication cookie
        if not st.session_state.get("LOGGED_IN", False):
            if not st.session_state.get("LOGOUT_BUTTON_HIT", False):
                if "__streamlit_login_signup_ui_username__" in self.cookies:
                    if self.cookies["__streamlit_login_signup_ui_username__"] != "1c9a923f-fb21-4a91-b3f3-5f18e3f01182":
                        st.session_state["LOGGED_IN"] = True

        # Render login form only if the user is not authenticated
        if not st.session_state["LOGGED_IN"]:
            st.session_state["LOGOUT_BUTTON_HIT"] = False

            # Centered layout
            left, center, right = st.columns([1, 2, 1])

            with center:
                st.subheader("Login")

                with st.form("Login Form"):
                    # Username
                    username = st.text_input(
                        "Username",
                        placeholder="Enter your username"
                    )

                    # Password
                    password = st.text_input(
                        "Password",
                        placeholder="Enter your password",
                        type="password"
                    )

                    st.markdown("###")
                    login_submit_button = st.form_submit_button("Login")

                    if login_submit_button:
                        authenticate_user_check = check_usr_pass(username, password)

                        if not authenticate_user_check:
                            st.error("Invalid username or password")
                        else:
                            # Update last login timestamp
                            self.auth_service.update_last_login(username)

                            st.session_state["LOGGED_IN"] = True
                            self.cookies["__streamlit_login_signup_ui_username__"] = username
                            self.cookies.save()

                            st.session_state["rerun_trigger"] = not st.session_state.get("rerun_trigger", False)
                            st.stop()

    def animation(self) -> None:
        """
        Renders the lottie animation.
        """
        lottie_json = load_lottie(self.lottie_url)
        if lottie_json:
            st_lottie(lottie_json, width=self.width, height=self.height)

    def create_account_widget(self) -> None:
        """
        Token-based account creation for invited users.
        Users enter the token they received via email to complete registration.
        """
        st.subheader("Create Account")
        st.caption("Enter the verification token you received via email to complete your registration.")

        with st.form("Create Account Form"):
            email = st.text_input(
                "Email *",
                placeholder="Enter the email where you received the invitation"
            )

            token = st.text_input(
                "Verification Token *",
                placeholder="Enter the token from your invitation email"
            )

            password = st.text_input(
                "Choose Password *",
                type="password",
                placeholder="Create a strong password (min 8 characters)"
            )

            password_confirm = st.text_input(
                "Confirm Password *",
                type="password",
                placeholder="Re-enter your password"
            )

            st.markdown("###")
            submit = st.form_submit_button("Create Account")

            if submit:
                # Validation
                email_error = check_valid_email(email)
                if email_error:
                    st.error(email_error)
                elif not token or not token.strip():
                    st.error("Please enter the verification token")
                elif not password:
                    st.error("Please enter a password")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters")
                elif password != password_confirm:
                    st.error("Passwords do not match!")
                else:
                    # Attempt to create account with token
                    success, message = self.auth_service.create_user_from_token(
                        email.strip(),
                        token.strip(),
                        password
                    )

                    if success:
                        st.success(message)
                        st.info("You can now log in with your username and password.")

                        # Send confirmation email
                        is_valid, token_data = self.auth_service.validate_token(
                            email.strip(), token.strip(), 'account_creation'
                        )
                        if token_data:
                            self.auth_email_service.send_account_created_confirmation(
                                to_email=email.strip(),
                                to_name=token_data.get('name', 'User'),
                                username=token_data.get('username', ''),
                                company_name=self.company_name
                            )
                    else:
                        st.error(message)

    def forgot_password(self) -> None:
        """
        Creates the forgot password widget.
        Sends a password reset token via EmailJS.
        """
        st.subheader("Forgot Password")
        st.caption("Enter your email to receive a password reset token.")

        with st.form("Forgot Password Form"):
            email_forgot_passwd = st.text_input(
                "Email",
                placeholder='Please enter your email'
            )

            st.markdown("###")
            forgot_passwd_submit_button = st.form_submit_button(label='Send Reset Token')

            if forgot_passwd_submit_button:
                email_exists_check, username_forgot_passwd = check_email_exists(email_forgot_passwd)

                if email_exists_check == False:
                    st.error("Email ID not registered with us!")
                else:
                    # Generate reset token and send via EmailJS
                    token = self.auth_service.generate_password_reset_token(email_forgot_passwd)

                    # Get user's name for the email
                    user = self.auth_service.get_user_by_email(email_forgot_passwd)
                    user_name = user.get('name', 'User') if user else 'User'

                    result = self.auth_email_service.send_password_reset_token(
                        to_email=email_forgot_passwd,
                        to_name=user_name,
                        token=token,
                        company_name=self.company_name
                    )

                    if result.get('success'):
                        st.success("Password reset token sent to your email!")
                        st.info("Check your inbox and use the token on the Reset Password page.")
                    else:
                        st.warning(f"Could not send email. Your reset token is: `{token}`")
                        st.info("Please save this token and use it on the Reset Password page.")

    def reset_password(self) -> None:
        """
        Creates the reset password widget.
        User enters email, reset token, and new password.
        """
        st.subheader("Reset Password")
        st.caption("Enter the reset token you received via email along with your new password.")

        with st.form("Reset Password Form"):
            email_reset_passwd = st.text_input(
                "Email",
                placeholder='Please enter your email'
            )

            reset_token = st.text_input(
                "Reset Token",
                placeholder='Please enter the token you received in the email'
            )

            new_passwd = st.text_input(
                "New Password",
                placeholder='Please enter a new, strong password',
                type='password'
            )

            new_passwd_confirm = st.text_input(
                "Confirm New Password",
                placeholder='Please re-enter the new password',
                type='password'
            )

            st.markdown("###")
            reset_passwd_submit_button = st.form_submit_button(label='Reset Password')

            if reset_passwd_submit_button:
                email_exists_check, _ = check_email_exists(email_reset_passwd)

                if not email_exists_check:
                    st.error("Email does not exist!")
                elif not reset_token or not reset_token.strip():
                    st.error("Please enter the reset token")
                elif not new_passwd:
                    st.error("Please enter a new password")
                elif len(new_passwd) < 8:
                    st.error("Password must be at least 8 characters")
                elif new_passwd != new_passwd_confirm:
                    st.error("Passwords don't match!")
                else:
                    # Validate the token
                    is_valid, token_data = self.auth_service.validate_token(
                        email_reset_passwd.strip(),
                        reset_token.strip(),
                        'password_reset'
                    )

                    if is_valid:
                        # Change the password
                        change_passwd(email_reset_passwd, new_passwd)
                        # Mark token as used
                        self.auth_service.mark_token_used(reset_token.strip())
                        st.success("Password Reset Successfully!")
                        st.info("You can now log in with your new password.")
                    else:
                        st.error("Invalid or expired reset token!")

    def logout(self):
        """
        Logs out the user: clears session and cookies, then reruns Streamlit.
        """
        st.session_state["LOGGED_IN"] = False
        st.session_state["LOGOUT_BUTTON_HIT"] = True
        self.cookies["__streamlit_login_signup_ui_username__"] = "1c9a923f-fb21-4a91-b3f3-5f18e3f01182"
        self.cookies.save()
        st.session_state["rerun_trigger"] = not st.session_state.get("rerun_trigger", False)
        st.stop()

    def logout_widget(self) -> None:
        """
        Creates the logout widget in the sidebar only if the user is logged in.
        Fully rerun-safe and avoids duplicate key errors.
        """
        # Ensure session_state keys exist
        st.session_state.setdefault("LOGGED_IN", False)
        st.session_state.setdefault("LOGOUT_BUTTON_HIT", False)
        st.session_state.setdefault("rerun_trigger", False)
        st.session_state.setdefault("LOGOUT_BUTTON_CREATED", False)

        if st.session_state["LOGGED_IN"] and not st.session_state["LOGOUT_BUTTON_CREATED"]:
            logout_container = st.sidebar.container()
            logout_container.markdown("#")  # spacing

            # Use id(self) + random to guarantee a unique key
            import random
            unique_key = f"logout_button_{id(self)}_{random.randint(0, 999999)}"

            logout_click = logout_container.button(
                label=self.logout_button_name,
                key=unique_key
            )

            if logout_click:
                # Update session state and cookies
                st.session_state["LOGOUT_BUTTON_HIT"] = True
                st.session_state["LOGGED_IN"] = False
                self.cookies["__streamlit_login_signup_ui_username__"] = "1c9a923f-fb21-4a91-b3f3-5f18e3f01182"
                self.cookies.save()

                # Remove the button from sidebar
                logout_container.empty()

                # Trigger a rerun safely
                st.session_state["rerun_trigger"] = not st.session_state["rerun_trigger"]

                # Reset button created flag
                st.session_state["LOGOUT_BUTTON_CREATED"] = False

            else:
                # Mark button as created for this session
                st.session_state["LOGOUT_BUTTON_CREATED"] = True

    def nav_sidebar(self):
        """
        Creates the side navigation bar
        """
        main_page_sidebar = st.sidebar.empty()
        with main_page_sidebar:
            selected_option = option_menu(
                menu_title='Navigation',
                menu_icon='list-columns-reverse',
                icons=['box-arrow-in-right', 'person-plus', 'x-circle', 'arrow-counterclockwise'],
                options=['Login', 'Create Account', 'Forgot Password?', 'Reset Password'],
                styles={
                    "container": {"padding": "5px"},
                    "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px"}
                }
            )
        return main_page_sidebar, selected_option

    def hide_menu(self) -> None:
        """
        Hides the streamlit menu situated in the top right.
        """
        st.markdown(""" <style>
        #MainMenu {visibility: hidden;}
        </style> """, unsafe_allow_html=True)

    def hide_footer(self) -> None:
        """
        Hides the 'made with streamlit' footer.
        """
        st.markdown(""" <style>
        footer {visibility: hidden;}
        </style> """, unsafe_allow_html=True)

    def build_login_ui(self):
        """
        Brings everything together, calls important functions.
        """
        if 'LOGGED_IN' not in st.session_state:
            st.session_state['LOGGED_IN'] = False

        if 'LOGOUT_BUTTON_HIT' not in st.session_state:
            st.session_state['LOGOUT_BUTTON_HIT'] = False

        main_page_sidebar, selected_option = self.nav_sidebar()

        if selected_option == 'Login':
            c1, c2 = st.columns([7, 3])
            with c1:
                self.login_widget()
            with c2:
                if st.session_state['LOGGED_IN'] == False:
                    self.animation()

        if selected_option == 'Create Account':
            self.create_account_widget()

        if selected_option == 'Forgot Password?':
            self.forgot_password()

        if selected_option == 'Reset Password':
            self.reset_password()

        self.logout_widget()

        if st.session_state['LOGGED_IN'] == True:
            main_page_sidebar.empty()

        if self.hide_menu_bool == True:
            self.hide_menu()

        if self.hide_footer_bool == True:
            self.hide_footer()

        return st.session_state['LOGGED_IN']
