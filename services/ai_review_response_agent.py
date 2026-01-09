"""
AI Review Response Agent
Analyzes customer reviews using sentiment analysis and generates appropriate responses
Uses TextBlob for sentiment analysis and Gemini for response generation
"""

import os
import re
import random
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd
from textblob import TextBlob
from google import genai
from google.genai import types
from langfuse import observe
from services.schemas.review_agent_schemas import ReviewResponseOutput
from services.prompts import load_system_instructions

load_dotenv()

# Silence OpenTelemetry (Langfuse) errors
logging.getLogger("opentelemetry.sdk._shared_internal").setLevel(logging.CRITICAL)

MODEL=os.getenv("GEMINI_MODEL")
class AIReviewResponseAgent:
    """AI agent for analyzing reviews and generating appropriate responses"""

    # Sentiment thresholds
    SENTIMENT_POSITIVE_THRESHOLD = 0.1
    SENTIMENT_NEGATIVE_THRESHOLD = -0.1
    STAR_HIGH_THRESHOLD = 4  # 4-5 stars
    STAR_MEDIUM_THRESHOLD = 3  # 3-4 stars
    STAR_LOW_THRESHOLD = 2  # 1-2 stars

    def __init__(self):
        self.client: Optional[Client] = None
        self.gemini_client = None
        self._connect()

    def _connect(self):
        """Connect to Supabase and Gemini"""
        try:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SECRET_KEY')

            if not supabase_url or not supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_SECRET_KEY must be set in .env file")

            self.client = create_client(supabase_url, supabase_key)

            # Initialize Gemini with Flash-Lite model
            gemini_api_key = os.getenv('GEMINI_API_KEY')
            if gemini_api_key:
                self.gemini_client = genai.Client(api_key=gemini_api_key)

        except Exception as e:
            print(f"Failed to connect to services: {e}")
            raise

    @observe()
    def _analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of review text using TextBlob

        Args:
            text: Review text to analyze

        Returns:
            Sentiment polarity score (-1.0 to 1.0)
        """
        blob = TextBlob(text)
        return blob.sentiment.polarity

    def _classify_review(self, star_rating: int, sentiment_score: float) -> str:
        """
        Classify review into one of 5 categories based on star rating and sentiment

        Categories:
        - low_sentiment_low_stars: Reply comprehensively, ask to email support
        - low_sentiment_high_stars: Encourage + apologize for experience
        - high_sentiment_high_stars: Thank generously, encourage repeat purchase
        - high_sentiment_low_stars: Apologize, ask to contact support
        - medium_reviews: 3-4 stars, generic positive responses

        Args:
            star_rating: Star rating (1-5)
            sentiment_score: TextBlob sentiment score (-1.0 to 1.0)

        Returns:
            Category string
        """
        is_high_sentiment = sentiment_score >= self.SENTIMENT_POSITIVE_THRESHOLD
        is_low_sentiment = sentiment_score <= self.SENTIMENT_NEGATIVE_THRESHOLD
        is_high_stars = star_rating >= self.STAR_HIGH_THRESHOLD
        is_low_stars = star_rating <= self.STAR_LOW_THRESHOLD
        is_medium_stars = self.STAR_MEDIUM_THRESHOLD <= star_rating <= self.STAR_HIGH_THRESHOLD

        # Check for medium reviews first (3-4 stars)
        if is_medium_stars:
            return "medium_reviews"

        # Classify based on sentiment and stars
        if is_low_sentiment and is_low_stars:
            return "low_sentiment_low_stars"
        elif is_low_sentiment and is_high_stars:
            return "low_sentiment_high_stars"
        elif is_high_sentiment and is_high_stars:
            return "high_sentiment_high_stars"
        elif is_high_sentiment and is_low_stars:
            return "high_sentiment_low_stars"
        else:
            # Default to medium for edge cases
            return "medium_reviews"

    def _extract_and_validate_response(
        self,
        response_text: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Extract and validate review response from LLM output

        Args:
            response_text: Raw LLM response
            max_retries: Maximum retry attempts (unused here, kept for consistency)

        Returns:
            Validated response dictionary
        """
        # Try to extract from text code block first
        text_block_pattern = r'```(?:text)?\s*\n?(.*?)\n?```'
        code_block_match = re.search(text_block_pattern, response_text, re.DOTALL)

        if code_block_match:
            content = code_block_match.group(1).strip()
        else:
            content = response_text.strip()

        # Parse structured format
        response_match = re.search(r'RESPONSE:\s*(.+?)(?=TONE:|$)', content, re.IGNORECASE | re.DOTALL)
        tone_match = re.search(r'TONE:\s*(.+?)(?=INCLUDES_SUPPORT:|$)', content, re.IGNORECASE)
        support_match = re.search(r'INCLUDES_SUPPORT:\s*(.+?)$', content, re.IGNORECASE)

        if not response_match:
            # If structured format not found, use entire content as response
            response_data = {
                'response_text': content,
                'tone': 'supportive',
                'includes_support_contact': 'support' in content.lower() or 'contact' in content.lower()
            }
        else:
            response_data = {
                'response_text': response_match.group(1).strip(),
                'tone': tone_match.group(1).strip().lower() if tone_match else 'supportive',
                'includes_support_contact': support_match.group(1).strip().lower() in ['true', 'yes'] if support_match else False
            }

        # Validate using Pydantic model
        validated_response = ReviewResponseOutput(**response_data)
        return validated_response.model_dump()

    @observe()
    def generate_review_response(
        self,
        review_text: str,
        star_rating: int,
        customer_name: str,
        category: str,
        sentiment_score: float
    ) -> Optional[Dict[str, Any]]:
        """
        Generate AI response to a customer review based on category

        Args:
            review_text: The customer's review text
            star_rating: Star rating (1-5)
            customer_name: Customer's name
            category: Review category classification
            sentiment_score: TextBlob sentiment score

        Returns:
            Dictionary with response text and metadata, or None if failed
        """
        if not self.gemini_client:
            raise ValueError("Gemini API key not configured")

        # Define response guidelines based on category
        category_guidelines = {
            "low_sentiment_low_stars": {
                "tone": "apologetic and supportive",
                "goal": "Reply comprehensively to address concerns and ask customer to email support for resolution",
                "include_support": True,
                "key_points": [
                    "Sincerely apologize for the poor experience",
                    "Acknowledge specific issues mentioned in the review",
                    "Express commitment to quality and customer satisfaction",
                    "Provide support email contact (support@mistyjazzrecords.com)",
                    "Encourage them to reach out so we can make it right"
                ]
            },
            "low_sentiment_high_stars": {
                "tone": "encouraging and apologetic",
                "goal": "Encourage continued purchases while apologizing for any negative aspects of their experience",
                "include_support": False,
                "key_points": [
                    "Thank them for the positive rating despite concerns",
                    "Apologize for any issues mentioned in their review",
                    "Highlight our commitment to improvement",
                    "Encourage them to continue shopping with us",
                    "Mention upcoming releases or recommendations"
                ]
            },
            "high_sentiment_high_stars": {
                "tone": "grateful and enthusiastic",
                "goal": "Thank them generously and encourage repeat purchases",
                "include_support": False,
                "key_points": [
                    "Express genuine gratitude for their positive review",
                    "Highlight specific positive aspects they mentioned",
                    "Share enthusiasm about their jazz collection",
                    "Suggest they'll love our upcoming releases",
                    "Invite them to explore more albums in our catalog"
                ]
            },
            "high_sentiment_low_stars": {
                "tone": "apologetic and supportive",
                "goal": "Apologize for the experience despite positive sentiment, and ask them to contact support",
                "include_support": True,
                "key_points": [
                    "Acknowledge the discrepancy (positive words but low rating)",
                    "Apologize for not meeting their expectations",
                    "Express desire to understand what went wrong",
                    "Provide support contact (support@mistyjazzrecords.com)",
                    "Assure them we want to make it right"
                ]
            },
            "medium_reviews": {
                "tone": "positive and encouraging",
                "goal": "Generic positive response encouraging future purchases",
                "include_support": False,
                "key_points": [
                    "Thank them for their feedback",
                    "Appreciate their business",
                    "Express hope they enjoy their purchase",
                    "Mention we're always improving",
                    "Encourage them to explore more of our catalog"
                ]
            }
        }

        guidelines = category_guidelines.get(category, category_guidelines["medium_reviews"])

        # Build prompt for AI response generation
        response_prompt = f"""You are writing a customer service response for Misty Jazz Records, a premium vinyl record store.

**Customer Review Details:**
- Customer Name: {customer_name}
- Star Rating: {star_rating}/5
- Review Text: "{review_text}"
- Sentiment Score: {sentiment_score:.2f} (TextBlob analysis)
- Category: {category}

**Response Guidelines:**
- Tone: {guidelines['tone']}
- Goal: {guidelines['goal']}
- Include Support Contact: {'Yes' if guidelines['include_support'] else 'No'}

**Key Points to Address:**
{chr(10).join([f"- {point}" for point in guidelines['key_points']])}

**Requirements:**
1. Address the customer by their first name
2. Keep response between 15-40 words
3. Be genuine, personal, and specific to their review
4. Match the specified tone perfectly
5. If support contact is required, include: support@mistyjazzrecords.com
6. Maintain Misty Jazz Records' premium brand voice

RESPONSE FORMAT:
You MUST return your response in a text code block using this EXACT format:

```text
RESPONSE: [Your personalized response here]

TONE: {guidelines['tone'].split(' and ')[0]}

INCLUDES_SUPPORT: {'true' if guidelines['include_support'] else 'false'}
```

CRITICAL FORMATTING RULES:
- Wrap entire response in a text code block (```text ... ```)
- Use EXACTLY the labels: RESPONSE:, TONE:, INCLUDES_SUPPORT:
- Response must be 15-40 words
- Be specific to THIS review, not generic
- Do NOT include extra commentary outside the code block
"""

        # Retry logic with validation
        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                generation_config = types.GenerateContentConfig(
                    system_instruction=load_system_instructions('review_response_system_instructions.txt'),
                    temperature=0.7,
                    top_p=0.9,
                    top_k=40,
                )

                response = self.gemini_client.models.generate_content(
                    model=MODEL,  
                    contents=response_prompt,
                    config=generation_config
                )

                # Extract and validate the response
                validated_response = self._extract_and_validate_response(response.text, max_retries=max_retries)

                return validated_response

            except Exception as e:
                last_error = e
                error_msg = str(e)
                print(f"Attempt {attempt + 1}/{max_retries} failed for review response: {error_msg}")

                # Print more detailed error information
                import traceback
                print(f"Detailed error: {traceback.format_exc()}")

                if attempt < max_retries - 1:
                    print(f"Retrying response generation...")
                    continue
                else:
                    print(f"All {max_retries} attempts failed. Last error: {error_msg}")
                    return None

        return None

    @observe()
    def analyze_all_reviews(self) -> pd.DataFrame:
        """
        Analyze all reviews with TextBlob sentiment analysis and classify them

        Returns:
            DataFrame with reviews, sentiment scores, categories, and customer info
        """
        try:
            # Get all reviews
            reviews_result = self.client.table('reviews').select(
                'review_id, customer_id, album_id, rating, review_text, created_at'
            ).execute()

            if not reviews_result.data:
                return pd.DataFrame()

            # Get all customers for name lookup
            customers_result = self.client.table('customers').select(
                'customer_id, first_name, last_name'
            ).execute()

            # Create customer lookup dictionary
            customer_lookup = {}
            if customers_result.data:
                for customer in customers_result.data:
                    customer_lookup[customer['customer_id']] = {
                        'first_name': customer['first_name'],
                        'last_name': customer['last_name']
                    }

            # Process reviews
            reviews_data = []
            for review in reviews_result.data:
                review_text = review.get('review_text', '')
                star_rating = review.get('rating', 3)
                customer_id = review.get('customer_id')

                # Get customer name
                customer_info = customer_lookup.get(customer_id, {'first_name': 'Valued', 'last_name': 'Customer'})
                customer_name = f"{customer_info['first_name']} {customer_info['last_name']}"

                # Analyze sentiment
                sentiment_score = self._analyze_sentiment(review_text) if review_text else 0.0

                # Classify review
                category = self._classify_review(star_rating, sentiment_score)

                reviews_data.append({
                    'review_id': review['review_id'],
                    'customer_id': customer_id,
                    'customer_name': customer_name,
                    'first_name': customer_info['first_name'],
                    'album_id': review.get('album_id'),
                    'star_rating': star_rating,
                    'review_text': review_text,
                    'sentiment_score': round(sentiment_score, 3),
                    'category': category,
                    'created_at': review.get('created_at')
                })

            return pd.DataFrame(reviews_data)

        except Exception as e:
            print(f"Error analyzing reviews: {e}")
            return pd.DataFrame()

    def generate_medium_review_responses(self) -> List[str]:
        """
        Generate generic positive response templates for medium reviews (3-4 stars)

        Returns:
            List of response template strings
        """
        responses = [
            "Thank you for taking the time to share your thoughts! We're glad you enjoyed your purchase and hope it brings many hours of listening pleasure. Feel free to explore more gems in our collection!",
            "We appreciate your feedback and are thrilled to have you as part of the Misty Jazz Records family. If you ever need recommendations, we're here to help you discover your next favorite album!",
            "Thanks for your review! We're always working to improve and provide the best vinyl experience. We hope you'll continue to explore our curated jazz collection.",
            "We value your feedback and are happy you're enjoying your new vinyl. Our catalog is constantly growing with rare finds and timeless classics - happy listening!",
            "Thank you for your support! We're committed to bringing you the finest jazz vinyl selections. Don't hesitate to reach out if you need any recommendations for your next purchase.",
            "We appreciate you sharing your experience with us! Your feedback helps us continue to provide quality vinyl records. We hope you enjoy your new albums!",
            "Thanks for your review! We're glad you're part of our jazz-loving community. Feel free to reach out if you need any recommendations for your next purchase.",
            "Thank you for your feedback! We value every customer's opinion and are always striving to improve. Happy listening!"
        ]

        return responses

    @observe()
    def generate_batch_responses(
        self,
        reviews_df: pd.DataFrame,
        category: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate responses for a batch of reviews in a specific category

        Args:
            reviews_df: DataFrame containing reviews to process
            category: Review category to generate responses for
            limit: Maximum number of reviews to process (default 10)

        Returns:
            List of dictionaries containing review info and generated responses
        """
        results = []

        # Filter reviews by category and limit
        category_reviews = reviews_df[reviews_df['category'] == category].head(limit)

        print(f"Generating responses for {len(category_reviews)} reviews in category '{category}'...")

        for _, review in category_reviews.iterrows():
            try:
                # For medium reviews, use pre-generated templates
                if category == "medium_reviews":
                    medium_responses = self.generate_medium_review_responses()
                    selected_response_text = random.choice(medium_responses)

                    result = {
                        'review_id': review['review_id'],
                        'customer_name': review['customer_name'],
                        'first_name': review['first_name'],
                        'last_name': review['customer_name'].split()[-1] if ' ' in review['customer_name'] else review['customer_name'],
                        'star_rating': review['star_rating'],
                        'sentiment_score': review['sentiment_score'],
                        'review_text': review['review_text'],
                        'response_text': selected_response_text,
                        'attributed_to': 'Template',
                        'tone': 'positive',
                        'includes_support_contact': False,
                        'status': 'success'
                    }
                else:
                    # Generate custom AI response
                    response = self.generate_review_response(
                        review_text=review['review_text'],
                        star_rating=review['star_rating'],
                        customer_name=review['first_name'],
                        category=category,
                        sentiment_score=review['sentiment_score']
                    )

                    if response:
                        result = {
                            'review_id': review['review_id'],
                            'customer_name': review['customer_name'],
                            'first_name': review['first_name'],
                            'last_name': review['customer_name'].split()[-1] if ' ' in review['customer_name'] else review['customer_name'],
                            'star_rating': review['star_rating'],
                            'sentiment_score': review['sentiment_score'],
                            'review_text': review['review_text'],
                            'response_text': response['response_text'],
                            'attributed_to': 'AI Generated',
                            'tone': response['tone'],
                            'includes_support_contact': response['includes_support_contact'],
                            'status': 'success'
                        }
                    else:
                        result = {
                            'review_id': review['review_id'],
                            'customer_name': review['customer_name'],
                            'first_name': review['first_name'],
                            'last_name': review['customer_name'].split()[-1] if ' ' in review['customer_name'] else review['customer_name'],
                            'star_rating': review['star_rating'],
                            'sentiment_score': review['sentiment_score'],
                            'review_text': review['review_text'],
                            'response_text': 'Failed to generate response',
                            'attributed_to': 'Error',
                            'tone': 'error',
                            'includes_support_contact': False,
                            'status': 'failed'
                        }

                results.append(result)
                print(f"Processed review {len(results)}/{len(category_reviews)}")

            except Exception as e:
                print(f"Error processing review {review['review_id']}: {e}")
                result = {
                    'review_id': review['review_id'],
                    'customer_name': review['customer_name'],
                    'first_name': review['first_name'],
                    'last_name': review['customer_name'].split()[-1] if ' ' in review['customer_name'] else review['customer_name'],
                    'star_rating': review['star_rating'],
                    'sentiment_score': review['sentiment_score'],
                    'review_text': review['review_text'],
                    'response_text': f'Error: {str(e)}',
                    'attributed_to': 'Error',
                    'tone': 'error',
                    'includes_support_contact': False,
                    'status': 'failed'
                }
                results.append(result)

        return results
