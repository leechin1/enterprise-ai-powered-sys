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
from services.ai_review_response_agent import AIReviewResponseAgent

# Import email and activity log services
try:
    from services.email_service import get_email_service
    EMAIL_SERVICE_AVAILABLE = True
except Exception as e:
    EMAIL_SERVICE_AVAILABLE = False
    print(f"Email service not available: {e}")

try:
    from services.activity_log_service import get_activity_log_service
    ACTIVITY_LOG_AVAILABLE = True
except Exception as e:
    ACTIVITY_LOG_AVAILABLE = False
    print(f"Activity log service not available: {e}")


def log_activity(action_type: str, description: str, category: str = "email", **kwargs):
    """Helper function to log activities"""
    if ACTIVITY_LOG_AVAILABLE:
        try:
            activity_service = get_activity_log_service()
            activity_service.log_activity(
                action_type=action_type,
                description=description,
                category=category,
                metadata=kwargs.get('metadata'),
                status=kwargs.get('status', 'success')
            )
        except Exception as e:
            print(f"Failed to log activity: {e}")


def render_marketing_emails():
    """Render the Marketing Emails page with customer segmentation and email generation"""

    st.title("Marketing & CRM")
    st.caption("AI-powered customer segmentation, email campaigns, and review management")

    # Create tabs
    tab1, tab2 = st.tabs(["📧 Marketing Emails", "⭐ Review Responses"])

    with tab1:
        render_marketing_emails_tab()

    with tab2:
        render_review_responses_tab()


def render_marketing_emails_tab():
    """Render the Marketing Emails tab with customer segmentation and email generation"""

    st.subheader("Marketing Emails")
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

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💸 Lowest Purchasing", use_container_width=True,
                    type="primary" if st.session_state.get('segment_type') == 'low_spend' else "secondary",
                    help="Customers who have spent the least - good for re-engagement campaigns"):
            st.session_state.segment_type = 'low_spend'
            st.session_state.selected_customers = None
            st.rerun()

    with col2:
        if st.button("⭐ Best Customers", use_container_width=True,
                    type="primary" if st.session_state.get('segment_type') == 'best' else "secondary",
                    help="Top spending customers - great for VIP campaigns"):
            st.session_state.segment_type = 'best'
            st.session_state.selected_customers = None
            st.rerun()

    with col3:
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
            customers_df = marketing.get_lowest_purchasing_customers(limit=15)
            if not customers_df.empty:
                st.caption(f"📊 Found {len(customers_df)} customers with lowest spending")
                display_df = customers_df.copy()
                display_df['total_spent'] = display_df['total_spent'].apply(lambda x: f"${x:,.2f}")
                display_df = display_df[['name', 'email', 'total_spent', 'order_count']]
                display_df.columns = ['Name', 'Email', 'Total Spent', 'Orders']
            else:
                st.info("No customers found in this segment")


    elif segment_type == 'best':
        with st.spinner("Loading best customers..."):
            customers_df = marketing.get_best_customers(limit=10)
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

        st.markdown("### ✏️ Edit Email Before Sending")
        st.caption("You can edit the email content below before sending. Changes are saved automatically.")

        # Editable text area for the email
        edited_email = st.text_area(
            "Email Content",
            value=st.session_state.generated_email,
            height=300,
            key="email_editor",
            help="Edit the subject, body, and call-to-action as needed"
        )

        # Update session state with edited content
        st.session_state.generated_email = edited_email

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
                # Parse the generated email to extract subject and body
                generated_email = st.session_state.get('generated_email', '')
                customers_df = st.session_state.get('selected_customers')

                # Extract subject and body from generated email
                import re
                subject_match = re.search(r'SUBJECT:\s*(.+?)(?:\n|$)', generated_email, re.IGNORECASE)
                body_match = re.search(r'BODY:\s*(.+?)(?=CALL-TO-ACTION:|$)', generated_email, re.IGNORECASE | re.DOTALL)
                cta_match = re.search(r'CALL-TO-ACTION:\s*(.+?)$', generated_email, re.IGNORECASE | re.DOTALL)

                if not subject_match or not body_match:
                    st.error("Could not parse email content. Please regenerate the email.")
                else:
                    subject = subject_match.group(1).strip()
                    body = body_match.group(1).strip()
                    if cta_match:
                        body += f"\n\n{cta_match.group(1).strip()}"

                    # Send preview email using EmailJS (placebo mode)
                    if EMAIL_SERVICE_AVAILABLE:
                        email_service = get_email_service()

                        with st.spinner("📧 Sending preview email..."):
                            # Send a single preview email representing the campaign
                            # In placebo mode, this goes to your test email
                            first_customer = customers_df.iloc[0] if not customers_df.empty else None
                            recipient_email = first_customer['email'] if first_customer is not None else "campaign@mistyjazzrecords.com"
                            recipient_name = first_customer['name'] if first_customer is not None else "Valued Customer"

                            result = email_service.send_email(
                                to_email=recipient_email,
                                to_name=recipient_name,
                                subject=f"[CAMPAIGN PREVIEW] {subject}",
                                body=f"This is a preview of the marketing campaign that would be sent to {len(customers_df)} customers.\n\n---\n\n{body}",
                                email_type="marketing_campaign",
                                metadata={
                                    "segment_type": st.session_state.get('segment_type'),
                                    "total_recipients": len(customers_df),
                                    "campaign_id": datetime.now().strftime('%Y%m%d%H%M%S')
                                }
                            )

                            if result.get('success'):
                                # Log the activity
                                log_activity(
                                    action_type="email_sent",
                                    description=f"Marketing campaign preview sent ({len(customers_df)} recipients)",
                                    category="email",
                                    metadata={
                                        "segment_type": st.session_state.get('segment_type'),
                                        "total_recipients": len(customers_df),
                                        "subject": subject,
                                        "placebo_mode": result.get('placebo_mode', True)
                                    }
                                )

                                st.success(f"✅ Campaign preview email sent!")
                                st.balloons()

                                # Show email status
                                status = email_service.get_status()
                                if status.get('placebo_mode'):
                                    st.info(f"""
                                    📬 **Placebo Mode Active**
                                    - Preview sent to: {status.get('placebo_email')}
                                    - Original recipient would be: {recipient_email}
                                    - Campaign would reach: {len(customers_df)} customers
                                    - Campaign ID: #{datetime.now().strftime('%Y%m%d%H%M%S')}
                                    """)
                                else:
                                    st.info(f"""
                                    📊 **Campaign Stats**
                                    - Emails Sent: {len(customers_df)}
                                    - Campaign ID: #{datetime.now().strftime('%Y%m%d%H%M%S')}
                                    """)
                            else:
                                # Log failure
                                log_activity(
                                    action_type="email_failed",
                                    description=f"Marketing campaign failed: {result.get('error', 'Unknown error')}",
                                    category="email",
                                    metadata={"error": result.get('error')},
                                    status="failed"
                                )
                                st.error(f"❌ Failed to send email: {result.get('error', 'Unknown error')}")
                    else:
                        st.warning("Email service not available. Please check your EmailJS configuration in .env")


def render_review_responses_tab():
    """Render the Review Responses tab with 5 category boxes for classified reviews"""

    st.subheader("Review Response Management")
    st.caption("AI-powered sentiment analysis and automated review response generation")

    # Initialize service
    try:
        review_agent = AIReviewResponseAgent()
    except Exception as e:
        st.error(f"Failed to connect to services: {e}")
        st.info("Make sure your .env file has SUPABASE_URL, SUPABASE_SECRET_KEY, and GEMINI_API_KEY set correctly.")
        return

    st.markdown("---")

    # Load and analyze reviews
    if st.button("🔄 Analyze All Reviews", type="primary"):
        with st.spinner("Analyzing reviews with sentiment analysis..."):
            st.session_state.reviews_df = review_agent.analyze_all_reviews()
            if not st.session_state.reviews_df.empty:
                st.success(f"✅ Analyzed {len(st.session_state.reviews_df)} reviews!")
            else:
                st.warning("No reviews found in the database.")

    st.markdown("---")

    # Display 5 category boxes
    if 'reviews_df' in st.session_state and not st.session_state.reviews_df.empty:
        reviews_df = st.session_state.reviews_df

        st.subheader("Review Categories")
        st.caption("Reviews classified by sentiment and star rating")

        # Define category information
        categories = {
            "low_sentiment_low_stars": {
                "title": "🔴 Low Sentiment + Low Stars",
                "description": "Critical reviews that need comprehensive response",
                "color": "#DC2626"
            },
            "low_sentiment_high_stars": {
                "title": "🟡 Low Sentiment + High Stars",
                "description": "Good ratings with concerning feedback",
                "color": "#F59E0B"
            },
            "high_sentiment_high_stars": {
                "title": "🟢 High Sentiment + High Stars",
                "description": "Excellent reviews to celebrate",
                "color": "#10B981"
            },
            "high_sentiment_low_stars": {
                "title": "🟠 High Sentiment + Low Stars",
                "description": "Positive feedback but low rating",
                "color": "#F97316"
            },
            "medium_reviews": {
                "title": "🔵 Medium Reviews (3-4 Stars)",
                "description": "Standard reviews with generic responses",
                "color": "#3B82F6"
            }
        }

        # Display category boxes in rows
        for idx, (category_key, category_info) in enumerate(categories.items()):
            category_reviews = reviews_df[reviews_df['category'] == category_key]
            count = len(category_reviews)

            # Create expandable section for each category
            with st.expander(f"{category_info['title']} ({count} reviews)", expanded=(count > 0 and idx == 0)):
                if count > 0:
                    # Display category stats
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
                    with col1:
                        avg_rating = category_reviews['star_rating'].mean()
                        st.metric("Avg Rating", f"{avg_rating:.1f} ⭐")
                    with col2:
                        avg_sentiment = category_reviews['sentiment_score'].mean()
                        st.metric("Avg Sentiment", f"{avg_sentiment:.2f}")
                    with col3:
                        st.metric("Total Reviews", count)
                    with col4:
                        # Generate Responses button for this category (limited to 5 for preview)
                        if st.button(f"🤖 Generate Responses (preview 5)", key=f"batch_gen_{category_key}", type="primary", use_container_width=True):
                            with st.spinner(f"Generating responses for {category_info['title']}..."):
                                batch_results = review_agent.generate_batch_responses(
                                    reviews_df=reviews_df,
                                    category=category_key,
                                    limit=5  # Changed from 20 to 5 for preview
                                )
                                st.session_state[f'batch_results_{category_key}'] = batch_results
                                st.session_state[f'show_popup_{category_key}'] = True
                                st.rerun()

                    st.markdown("---")

                    # Show sample reviews (first 5)
                    st.caption(f"**Sample Reviews (showing first 5 of {count}):**")
                    for idx, (_, review) in enumerate(category_reviews.head(5).iterrows()):
                        st.markdown(f"**{review['customer_name']}** - {review['star_rating']} ⭐ (Sentiment: {review['sentiment_score']:.2f})")
                        st.markdown(f"_{review['review_text']}_")
                        st.markdown("---")

                else:
                    st.info(f"No reviews in this category.")

        # Display popup modal for batch results
        for category_key, category_info in categories.items():
            if st.session_state.get(f'show_popup_{category_key}', False):
                render_batch_results_popup(category_key, category_info)

    else:
        st.info("👆 Click 'Analyze All Reviews' to load and classify reviews by sentiment.")


@st.dialog(title="Review Responses", width="large")
def render_batch_results_popup(category_key, category_info):
    """Render a popup with editable table for batch-generated responses"""

    st.markdown(f"### {category_info['title']}")
    st.caption("Review and edit the AI-generated responses before sending")

    batch_results = st.session_state.get(f'batch_results_{category_key}', [])

    if not batch_results:
        st.warning("No results to display.")
        if st.button("Close"):
            st.session_state[f'show_popup_{category_key}'] = False
            st.rerun()
        return

    # Create editable dataframe
    st.markdown("**Generated Responses:**")
    st.caption(f"✏️ Click on any cell to edit the response text. Changes are saved automatically.")

    # Prepare data for editable table
    table_data = []
    for result in batch_results:
        table_data.append({
            'Review ID': result['review_id'],
            'First Name': result['first_name'],
            'Last Name': result['last_name'],
            'Rating': f"{result['star_rating']} ⭐",
            'Sentiment': f"{result['sentiment_score']:.2f}",
            'Review': result['review_text'][:100] + '...' if len(result['review_text']) > 100 else result['review_text'],
            'Proposed Response': result['response_text']
        })

    # Create DataFrame
    responses_df = pd.DataFrame(table_data)

    # Display editable data editor
    edited_df = st.data_editor(
        responses_df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "Review ID": st.column_config.TextColumn("Review ID", disabled=True, width="small"),
            "First Name": st.column_config.TextColumn("First Name", disabled=True, width="small"),
            "Last Name": st.column_config.TextColumn("Last Name", disabled=True, width="small"),
            "Rating": st.column_config.TextColumn("Rating", disabled=True, width="small"),
            "Sentiment": st.column_config.TextColumn("Sentiment", disabled=True, width="small"),
            "Review": st.column_config.TextColumn("Review", disabled=True, width="medium"),
            "Proposed Response": st.column_config.TextColumn("Proposed Response", width="large")
        },
        height=400
    )

    st.markdown("---")

    # Action buttons
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        st.caption(f"**{len(batch_results)} responses generated**")
        success_count = sum(1 for r in batch_results if r['status'] == 'success')
        failed_count = sum(1 for r in batch_results if r['status'] == 'failed')
        if failed_count > 0:
            st.warning(f"⚠️ {failed_count} responses failed to generate")

    with col2:
        if st.button("📥 Download CSV", use_container_width=True):
            csv = edited_df.to_csv(index=False)
            st.download_button(
                label="Download",
                data=csv,
                file_name=f"review_responses_{category_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    with col3:
        if st.button("📤 Send All", type="primary", use_container_width=True):
            # Update batch results with edited responses
            for idx, result in enumerate(batch_results):
                result['response_text'] = edited_df.iloc[idx]['Proposed Response']

            # Send review responses via EmailJS (placebo mode)
            if EMAIL_SERVICE_AVAILABLE:
                email_service = get_email_service()
                emails_sent = 0
                emails_failed = 0

                with st.spinner("📧 Sending review responses..."):
                    for result in batch_results:
                        if result['status'] == 'success':
                            # Create email for this review response
                            # In a real system, this would go to the customer
                            # In placebo mode, it goes to your test email
                            customer_email = f"{result['first_name'].lower()}.{result['last_name'].lower()}@customer.example.com"

                            email_result = email_service.send_email(
                                to_email=customer_email,
                                to_name=f"{result['first_name']} {result['last_name']}",
                                subject=f"Thank you for your review - Misty Jazz Records",
                                body=result['response_text'],
                                email_type="review_response",
                                metadata={
                                    "review_id": result['review_id'],
                                    "star_rating": result['star_rating'],
                                    "sentiment_score": result['sentiment_score'],
                                    "category": category_key
                                }
                            )

                            if email_result.get('success'):
                                emails_sent += 1
                                log_activity(
                                    action_type="email_sent",
                                    description=f"Review response sent to {result['first_name']} {result['last_name']}",
                                    category="email",
                                    metadata={
                                        "review_id": result['review_id'],
                                        "to_email": customer_email,
                                        "placebo_mode": email_result.get('placebo_mode', True)
                                    }
                                )
                            else:
                                emails_failed += 1
                                log_activity(
                                    action_type="email_failed",
                                    description=f"Review response failed to {result['first_name']} {result['last_name']}: {email_result.get('error')}",
                                    category="email",
                                    metadata={
                                        "review_id": result['review_id'],
                                        "error": email_result.get('error')
                                    },
                                    status="failed"
                                )

                if emails_sent > 0:
                    st.success(f"✅ Sent {emails_sent} review response(s)!")
                    st.balloons()

                if emails_failed > 0:
                    st.warning(f"⚠️ {emails_failed} email(s) failed to send")

                # Show placebo mode indicator
                status = email_service.get_status()
                if status.get('placebo_mode'):
                    st.info(f"""
                    📬 **Placebo Mode Active**
                    - All {emails_sent} emails sent to: {status.get('placebo_email')}
                    - Category: {category_info['title']}
                    - Each email shows the intended recipient in the subject line
                    """)
                else:
                    st.info(f"""
                    📊 **Send Summary**
                    - Responses Sent: {emails_sent}
                    - Failed: {emails_failed}
                    - Category: {category_info['title']}
                    - Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """)
            else:
                # Fallback if email service not available
                st.warning("Email service not available. Simulating send...")
                import time
                time.sleep(2)
                st.success(f"✅ Simulated sending {success_count} responses!")
                st.info(f"""
                📊 **Send Summary (Simulated)**
                - Responses Sent: {success_count}
                - Failed: {failed_count}
                - Category: {category_info['title']}
                - Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """)

            # Clear the popup state
            st.session_state[f'show_popup_{category_key}'] = False
            st.session_state[f'batch_results_{category_key}'] = []

            import time
            time.sleep(2)
            st.rerun()

    with col4:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state[f'show_popup_{category_key}'] = False
            st.session_state[f'batch_results_{category_key}'] = []
            st.rerun()
