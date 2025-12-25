"""
Gemini API integration for generating realistic fake data with structured output
"""

import os
import json
import time
import re
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv
from config import GEMINI_MODEL, GEMINI_TEMPERATURE, GEMINI_MAX_RETRIES
from templates import *

# Load environment variables
load_dotenv()


class SmartJSONExtractor:
    """Robust JSON extraction from LLM responses"""

    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from text with multiple fallback strategies

        Args:
            text: Raw text that may contain JSON

        Returns:
            Dict with 'success' (bool), 'data' (parsed JSON), 'error' (str)
        """
        try:
            # Strategy 1: Try direct parsing
            data = json.loads(text.strip())
            return {"success": True, "data": data, "error": None}
        except json.JSONDecodeError:
            pass

        try:
            # Strategy 2: Remove markdown code blocks
            cleaned = self._remove_code_blocks(text)
            data = json.loads(cleaned)
            return {"success": True, "data": data, "error": None}
        except json.JSONDecodeError:
            pass

        try:
            # Strategy 3: Extract first JSON array or object found
            json_match = re.search(r'(\[[\s\S]*\]|\{[\s\S]*\})', text)
            if json_match:
                data = json.loads(json_match.group(1))
                return {"success": True, "data": data, "error": None}
        except (json.JSONDecodeError, AttributeError):
            pass

        return {
            "success": False,
            "data": None,
            "error": "Failed to extract valid JSON from response"
        }

    def _remove_code_blocks(self, text: str) -> str:
        """Remove markdown code block formatting"""
        text = text.strip()
        if text.startswith('```'):
            lines = text.split('\n')
            text = '\n'.join(lines[1:-1]) if len(lines) > 2 else text
            if text.startswith('json'):
                text = text[4:].strip()
        return text


class GeminiDataGenerator:
    """Generate realistic fake data using Gemini API with structured output"""

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        self.extractor = SmartJSONExtractor()
        self.generation_config = types.GenerateContentConfig(
            temperature=GEMINI_TEMPERATURE,
            top_p=0.95,
            top_k=40,
        )
        self.TEMPLATES = TEMPLATES

    def extract_structured_form(
        self,
        instructions: str,
        form_template: Dict[str, Any],
        count: int,
        reference_ids: Optional[Dict[str, List[str]]] = None,
        model_class: Optional[BaseModel] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract data matching a form template with validation

        Args:
            instructions: Natural language instructions for data generation
            form_template: Template defining the expected structure
            count: Number of records to generate
            reference_ids: Optional dict of reference IDs for foreign keys
            model_class: Optional Pydantic model for validation

        Returns:
            List of validated dictionaries
        """
        # Build structured prompt
        prompt_parts = [
            "Extract information to fill this form template:\n",
            f"INSTRUCTIONS:\n{instructions}\n",
            f"\nForm Template:",
            json.dumps(form_template, indent=2),
        ]

        if reference_ids:
            prompt_parts.append("\n\nReference IDs (use these for foreign key fields):")
            for key, ids in reference_ids.items():
                sample_ids = ids[:10] if len(ids) > 10 else ids
                prompt_parts.append(f"- {key}: {sample_ids}")

        prompt_parts.extend([
            f"\n\nGenerate exactly {count} records.",
            "\nRules:",
            "- Use null for optional/missing information",
            "- Maintain exact field names from template",
            "- Infer appropriate realistic values from context",
            "- Ensure data types match template",
            "- Return ONLY a valid JSON array of objects",
            "- No markdown, no explanations, no code blocks",
            "\nJSON Output:"
        ])

        full_prompt = "\n".join(prompt_parts)

        # Generate with retry
        return self._generate_with_validation(full_prompt, count, model_class)

    def _generate_with_validation(
        self,
        prompt: str,
        expected_count: int,
        model_class: Optional[BaseModel] = None,
        retry: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Generate content with retry and optional Pydantic validation

        Args:
            prompt: Full prompt to send
            expected_count: Expected number of records
            model_class: Optional Pydantic model for validation
            retry: Current retry attempt

        Returns:
            List of validated dictionaries
        """
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=self.generation_config
            )

            # Extract JSON
            result = self.extractor.extract(response.text)

            if not result["success"]:
                raise ValueError(result["error"])

            data = result["data"]

            # Validate it's a list
            if not isinstance(data, list):
                raise ValueError("Response is not a JSON array")

            # Validate with Pydantic if model provided
            if model_class:
                validated_data = []
                for i, item in enumerate(data):
                    try:
                        validated_item = model_class(**item)
                        validated_data.append(validated_item.model_dump())
                    except ValidationError as e:
                        print(f"⚠ Validation warning for record {i+1}: {e}")
                        validated_data.append(item)  # Include anyway but warn
                data = validated_data

            actual_count = len(data)
            if actual_count != expected_count:
                print(f"⚠ Expected {expected_count} records, got {actual_count}")

            print(f"✓ Generated {actual_count} validated records")
            return data

        except Exception as e:
            if retry < GEMINI_MAX_RETRIES:
                print(f"✗ Error (attempt {retry + 1}/{GEMINI_MAX_RETRIES}): {e}")
                time.sleep(2 ** retry)  # Exponential backoff
                return self._generate_with_validation(prompt, expected_count, model_class, retry + 1)
            else:
                print(f"✗ Failed after {GEMINI_MAX_RETRIES} attempts: {e}")
                return []


    def generate_genres(self, count: int) -> List[Dict]:
        """Generate music genres"""
        instructions = """
Generate a diverse list of music genres for a jazz vinyl record store.
Include classic jazz genres (Bebop, Cool Jazz, Hard Bop, Modal Jazz, Free Jazz)
and contemporary sub-genres.

Field constraints:
- name: unique genre name (string)
- description: brief description, 50-150 characters (string)
- avg_margin: average profit margin percentage, range 25.0-45.0 (float)
- popularity_score: popularity rating, range 50-100 (integer)
"""
        return self.extract_structured_form(
            instructions,
            self.TEMPLATES['genre'],
            count,
            model_class=Genre
        )

    def generate_labels(self, count: int) -> List[Dict]:
        """Generate record labels"""
        instructions = """
Generate a list of record labels (both real historical labels and fictional ones).
Include famous jazz labels like Blue Note, Verve, Columbia, ECM, Impulse!,
and also create some fictional labels with realistic names.

Field constraints:
- name: label name (string)
- country: country of origin, e.g., "USA", "UK", "Germany", "Japan", "France" (string)
- founded_year: year founded, range 1940-2020 (integer)
"""
        return self.extract_structured_form(
            instructions,
            self.TEMPLATES['label'],
            count,
            model_class=Label
        )

    def generate_users(self, count: int) -> List[Dict]:
        """Generate system users"""
        instructions = """
Generate system users for a vinyl record store management system.
Create realistic employee names and emails using @mistyjazz.com domain.

Field constraints:
- email: professional email address, use @mistyjazz.com domain (string)
- first_name: first name (string)
- last_name: last name (string)
- role: one of ["admin", "manager", "staff"], mostly staff, some managers, 1 admin (string)
"""
        return self.extract_structured_form(
            instructions,
            self.TEMPLATES['user'],
            count,
            model_class=User
        )

    def generate_customers(self, count: int) -> List[Dict]:
        """Generate customers"""
        instructions = """
Generate customer profiles for a jazz vinyl record store.
Create diverse, realistic customer data.

Field constraints:
- email: unique email address (string)
- first_name: first name (string)
- last_name: last name (string)
- phone: phone number in format (XXX) XXX-XXXX (string)
- address: full street address (string)
- date_joined: join date in YYYY-MM-DD format, random dates in last 3 years (string)
- lifetime_value: total spent, range 0.00-5000.00 (float)
- total_purchases: number of purchases, range 0-50 (integer)
- preferred_genre: favorite genre or null (string or null)
- status: one of ["active", "inactive", "vip"], mostly active (string)
"""
        return self.extract_structured_form(
            instructions,
            self.TEMPLATES['customer'],
            count,
            model_class=Customer
        )

    def generate_albums(self, count: int, genre_ids: List[str], label_ids: List[str]) -> List[Dict]:
        """Generate albums with references to genres and labels"""
        instructions = """
Generate jazz vinyl album records for a record store.
Create a mix of classic and contemporary jazz albums.

Field constraints:
- sku: unique SKU code, format "VNL-XXXXX" where X is digit (string)
- title: album title, realistic jazz album names (string)
- artist: artist/band name, can be real or fictional jazz artists (string)
- genre_id: UUID from reference list (string)
- label_id: UUID from reference list (string)
- release_year: year released, range 1950-2023 (integer)
- price: retail price, range 15.99-299.99, rare albums more expensive (float)
- cost: wholesale cost, 60-70% of price (float)
- condition: one of ["M", "NM", "VG+", "VG", "G+"], mostly NM and VG+ (string)
- description: brief album description, 100-200 characters (string)
- is_rare: whether it's a collectible, 20% should be true (boolean)
- estimated_value: market value for rare items or null, higher for rare (float or null)
"""
        return self.extract_structured_form(
            instructions,
            self.TEMPLATES['album'],
            count,
            reference_ids={'genre_ids': genre_ids, 'label_ids': label_ids},
            model_class=Album
        )

    def generate_orders(self, count: int, customer_ids: List[str]) -> List[Dict]:
        """Generate orders"""
        instructions = """
Generate customer orders for a vinyl record store.
Create realistic order data with proper calculations.

Field constraints:
- order_number: unique order number, format "ORD-XXXXXX" (string)
- customer_id: UUID from reference list (string)
- subtotal: order subtotal, range 20.00-500.00 (float)
- tax: sales tax amount, 8% of subtotal (float)
- shipping_fee: shipping cost, range 0.00-25.00 (float)
- total: subtotal + tax + shipping_fee (float)
- status: one of ["pending", "processing", "shipped", "delivered", "cancelled"] (string)
- channel: one of ["in-store", "online", "phone"] (string)
- shipping_address: full address or null for in-store (string or null)
- order_date: date in YYYY-MM-DD HH:MM:SS format, last 6 months (string)
"""
        return self.extract_structured_form(
            instructions,
            self.TEMPLATES['order'],
            count,
            reference_ids={'customer_ids': customer_ids},
            model_class=Order
        )

    def generate_cases(self, count: int, customer_ids: List[str], user_ids: List[str]) -> List[Dict]:
        """Generate customer service cases"""
        instructions = """
Generate customer service tickets for a vinyl record store.
Create realistic customer service scenarios.

Field constraints:
- customer_id: UUID from reference list (string)
- subject: brief issue description, 50-100 characters (string)
- description: detailed problem description, 100-300 characters (string)
- category: one of ["order_issue", "product_question", "return", "technical", "general", "complaint", "feedback"] (string)
- priority: one of ["critical", "high", "medium", "low"], mostly medium/low (string)
- status: one of ["pending", "in_progress", "resolved", "closed"] (string)
- assigned_to: UUID from reference list or null (string or null)
- ai_sentiment: one of ["happy", "neutral", "frustrated", "angry", "confused"] (string)
- ai_score: urgency score, range 0-100 (integer)
- ai_suggestion: AI recommendation for resolution, 100-200 characters (string)
- resolution_notes: resolution summary or null if not resolved (string or null)
- created_at: timestamp in YYYY-MM-DD HH:MM:SS format, last 3 months (string)
- resolved_at: resolution timestamp or null (string or null)
"""
        return self.extract_structured_form(
            instructions,
            self.TEMPLATES['case'],
            count,
            reference_ids={'customer_ids': customer_ids, 'user_ids': user_ids},
            model_class=Case
        )

    def generate_workflows(self, count: int) -> List[Dict]:
        """Generate workflow definitions"""
        instructions = """
Generate automated workflow configurations for a business automation system.
Create workflows like inventory sync, order processing, customer notifications, etc.

Field constraints:
- name: workflow name, descriptive (string)
- description: what the workflow does, 100-200 characters (string)
- trigger_type: one of ["schedule", "event", "manual", "api"] (string)
- trigger_config: JSON object with trigger settings, use cron for schedule, event name for event (object)
  Example: {"cron": "0 * * * *"} or {"event": "order.created"}
- workflow_definition: JSON object with steps array, include step names (object)
  Example: {"steps": ["validate", "process", "notify"]}
- enabled: whether active, mostly true (boolean)
"""
        return self.extract_structured_form(
            instructions,
            self.TEMPLATES['workflow'],
            count,
            model_class=Workflow
        )

    def generate_integrations(self, count: int) -> List[Dict]:
        """Generate third-party integrations"""
        instructions = """
Generate third-party service integration configurations.
Create realistic integration services for an e-commerce business.

Field constraints:
- service_name: service name, e.g., "Stripe", "Shopify", "SendGrid" (string)
- category: one of ["payment", "ecommerce", "email", "analytics", "shipping", "accounting"] (string)
- connected: connection status (boolean)
- settings: JSON object with service settings, relevant to category (object)
- sync_frequency: how often to sync, e.g., "hourly", "daily", "realtime" (string)
- error_count: number of recent errors, range 0-10 (integer)
- last_error: error message or null (string or null)
"""
        return self.extract_structured_form(
            instructions,
            self.TEMPLATES['integration'],
            count,
            model_class=Integration
        )

    def generate_system_logs(self, count: int, user_ids: List[str]) -> List[Dict]:
        """Generate system logs"""
        instructions = """
Generate system log entries for monitoring and debugging.
Create realistic system logs with various levels and sources.

Field constraints:
- log_level: one of ["debug", "info", "warning", "error", "critical"] (string)
- source: system component, e.g., "api", "workflow_engine", "auth", "database" (string)
- message: log message, 50-200 characters (string)
- metadata: JSON object with additional context, optional (object)
- user_id: UUID from reference list or null (string or null)
- created_at: timestamp in YYYY-MM-DD HH:MM:SS format, last 7 days (string)
"""
        return self.extract_structured_form(
            instructions,
            self.TEMPLATES['system_log'],
            count,
            reference_ids={'user_ids': user_ids},
            model_class=SystemLog
        )
