"""
Marketing Emails component for Misty AI Enterprise System
Customer segmentation and AI-powered email generation
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.marketing_service import MarketingService


def render_marketing_emails():
    """Render the Marketing Emails page with customer segmentation and email generation"""

    st.title("Marketing Emails")
    st.caption("AI-powered customer segmentation and personalized email campaigns")

    # Initialize service
    try:
        marketing = MarketingService()
    except Exception as e:
        st.error(f"Failed to connect to services: {e}")
        st.info("Make sure your .env file has SUPABASE_URL, SUPABASE_SECRET_KEY, and GEMINI_API_KEY set correctly.")
        return

    st.markdown("---")

    # Section 1: Customer Segmentation Hints
    st.subheader("1. Customer Segmentation")
    st.caption("Select a customer segment to target with your marketing campaign")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("💸 Lowest Purchasing", use_container_width=True,
                    type="primary" if st.session_state.get('segment_type') == 'low_spend' else "secondary",
                    help="Customers who have spent the least - good for re-engagement campaigns"):
            st.session_state.segment_type = 'low_spend'
            st.session_state.selected_customers = None
            st.rerun()

    with col2:
        if st.button("💤 Inactive Customers", use_container_width=True,
                    type="primary" if st.session_state.get('segment_type') == 'inactive' else "secondary",
                    help="Customers who haven't purchased in a long time"):
            st.session_state.segment_type = 'inactive'
            st.session_state.selected_customers = None
            st.rerun()

    with col3:
        if st.button("⭐ Best Customers", use_container_width=True,
                    type="primary" if st.session_state.get('segment_type') == 'best' else "secondary",
                    help="Top spending customers - great for VIP campaigns"):
            st.session_state.segment_type = 'best'
            st.session_state.selected_customers = None
            st.rerun()

    with col4:
        if st.button("🎵 Genre Specific", use_container_width=True,
                    type="primary" if st.session_state.get('segment_type') == 'genre' else "secondary",
                    help="Customers who prefer specific genres"):
            st.session_state.segment_type = 'genre'
            st.session_state.selected_customers = None
            st.rerun()

    st.markdown("---")

    # Section 2: Customer Results Table
    st.subheader("2. Customer Results")

    # Load customer data based on segment type
    segment_type = st.session_state.get('segment_type', None)
    customers_df = pd.DataFrame()

    if segment_type == 'low_spend':
        with st.spinner("Loading lowest purchasing customers..."):
            customers_df = marketing.get_lowest_purchasing_customers(limit=100)
            if not customers_df.empty:
                st.caption(f"📊 Found {len(customers_df)} customers with lowest spending")
                display_df = customers_df.copy()
                display_df['total_spent'] = display_df['total_spent'].apply(lambda x: f"${x:,.2f}")
                display_df = display_df[['name', 'email', 'total_spent', 'order_count']]
                display_df.columns = ['Name', 'Email', 'Total Spent', 'Orders']
            else:
                st.info("No customers found in this segment")

    elif segment_type == 'inactive':
        # Add slider for days inactive
        days_inactive = st.slider("Days since last purchase", 30, 365, 90, 30)

        with st.spinner(f"Loading customers inactive for {days_inactive}+ days..."):
            customers_df = marketing.get_inactive_customers(days_inactive=days_inactive, limit=100)
            if not customers_df.empty:
                st.caption(f"📊 Found {len(customers_df)} inactive customers")
                display_df = customers_df.copy()
                display_df['total_spent'] = display_df['total_spent'].apply(lambda x: f"${x:,.2f}")
                display_df = display_df[['name', 'email', 'days_inactive', 'last_order_date_str', 'total_spent', 'order_count']]
                display_df.columns = ['Name', 'Email', 'Days Inactive', 'Last Order', 'Total Spent', 'Orders']
            else:
                st.info("No inactive customers found with the current criteria")

    elif segment_type == 'best':
        with st.spinner("Loading best customers..."):
            customers_df = marketing.get_best_customers(limit=100)
            if not customers_df.empty:
                st.caption(f"📊 Found {len(customers_df)} top customers")
                display_df = customers_df.copy()
                display_df['total_spent'] = display_df['total_spent'].apply(lambda x: f"${x:,.2f}")
                display_df = display_df[['name', 'email', 'total_spent', 'order_count']]
                display_df.columns = ['Name', 'Email', 'Total Spent', 'Orders']
            else:
                st.info("No customers found in this segment")

    elif segment_type == 'genre':
        # Get available genres
        genres = marketing.get_available_genres()
        if genres:
            selected_genre = st.selectbox("Select Genre", genres)

            with st.spinner(f"Loading customers who purchased {selected_genre}..."):
                customers_df = marketing.get_genre_specific_customers(genre_name=selected_genre, limit=100)
                if not customers_df.empty:
                    st.caption(f"📊 Found {len(customers_df)} customers who purchased {selected_genre}")
                    display_df = customers_df.copy()
                    display_df['genre_spent'] = display_df['genre_spent'].apply(lambda x: f"${x:,.2f}")
                    display_df = display_df[['name', 'email', 'genre', 'genre_spent', 'genre_units']]
                    display_df.columns = ['Name', 'Email', 'Genre', 'Spent on Genre', 'Units Purchased']
                else:
                    st.info(f"No customers found who purchased {selected_genre}")
        else:
            st.info("No genre data available")

    else:
        st.info("👆 Select a customer segment above to view results")

    # Display the table
    if not customers_df.empty:
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Store selected customers in session state
        st.session_state.selected_customers = customers_df

    st.markdown("---")

    # Section 3: Email Tone Configuration
    st.subheader("3. Email Configuration")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("**Tone Settings**")
        tone = st.selectbox(
            "Email Tone",
            ["Professional", "Friendly", "Casual", "Enthusiastic", "Luxurious", "Urgent"],
            help="Select the tone for the email"
        )

        email_goal = st.selectbox(
            "Campaign Goal",
            ["Re-engagement", "Product Launch", "Special Discount", "VIP Appreciation", "New Arrival Alert", "Personalized Recommendation"],
            help="What is the goal of this email campaign?"
        )

    with col2:
        st.markdown("**Email Settings**")
        include_discount = st.checkbox("Include Discount Offer", value=False)
        if include_discount:
            discount_percentage = st.number_input("Discount %", min_value=5, max_value=50, value=10)
        else:
            discount_percentage = 0

        email_length = st.select_slider(
            "Email Length",
            options=["Short", "Medium", "Long"],
            value="Medium"
        )

    # Additional custom instructions
    custom_instructions = st.text_area(
        "Additional Instructions (Optional)",
        placeholder="E.g., Mention our new vinyl cleaning service, highlight limited edition albums, etc.",
        height=80
    )

    st.markdown("---")

    # Section 4: Email Generation
    st.subheader("4. Generate & Send Email")

    col1, col2 = st.columns([3, 1])

    with col1:
        generate_button = st.button("🤖 Generate Email with AI", use_container_width=True, type="primary")

    with col2:
        # Preview customer count
        customer_count = len(st.session_state.get('selected_customers', []))
        st.metric("Recipients", customer_count)

    # Generate email when button is clicked
    if generate_button:
        if st.session_state.get('selected_customers') is None or len(st.session_state.get('selected_customers', [])) == 0:
            st.error("Please select a customer segment first!")
        else:
            with st.spinner("🧠 AI is crafting your personalized email..."):
                segment_type = st.session_state.get('segment_type', 'general')
                customers_df = st.session_state.get('selected_customers')

                try:
                    # Generate email using the service
                    generated_email = marketing.generate_marketing_email(
                        segment_type=segment_type,
                        segment_data=customers_df,
                        tone=tone,
                        campaign_goal=email_goal,
                        include_discount=include_discount,
                        discount_percentage=discount_percentage,
                        email_length=email_length,
                        custom_instructions=custom_instructions
                    )

                    if generated_email:
                        st.session_state.generated_email = generated_email
                    else:
                        st.error("Failed to generate email. Please try again.")

                except Exception as e:
                    st.error(f"Failed to generate email: {e}")

    # Display generated email
    if st.session_state.get('generated_email'):
        st.success("✅ Email generated successfully!")

        st.markdown("### Generated Email Preview")

        # Display in a nice card
        with st.container():
            st.markdown(
                f"""
                <div style="background-color: #1E293B; padding: 2rem; border-radius: 0.5rem; border-left: 4px solid #6366F1;">
                    <pre style="white-space: pre-wrap; font-family: inherit; color: #F1F5F9;">{st.session_state.generated_email}</pre>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")

        # Send section
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.markdown("**Ready to send?**")
            st.caption(f"This email will be sent to {len(st.session_state.get('selected_customers', []))} customers")

        with col2:
            st.download_button(
                label="📥 Download Email",
                data=st.session_state.generated_email,
                file_name=f"misty_email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col3:
            if st.button("📧 Send Email", use_container_width=True, type="primary"):
                # Placebo send button
                with st.spinner("Sending emails..."):
                    import time
                    time.sleep(2)  # Simulate sending
                    st.success(f"✅ Email sent to {len(st.session_state.get('selected_customers', []))} customers!")
                    st.balloons()

                    # Show some fake stats
                    st.info(f"""
                    📊 **Campaign Stats (Simulated)**
                    - Emails Sent: {len(st.session_state.get('selected_customers', []))}
                    - Estimated Open Rate: 24-32%
                    - Estimated Click Rate: 8-12%
                    - Campaign ID: #{datetime.now().strftime('%Y%m%d%H%M%S')}
                    """)
