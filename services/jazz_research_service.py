"""
Jazz Research Service - Web Search powered Jazz Domain Expert
Uses Google GenAI SDK with Google Search tool for jazz-specific research
"""

import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from langfuse import observe

# Import centralized config
from services.config import GCPConfig, ModelConfig
from services.prompts import load_prompt

load_dotenv()

# Silence unnecessary logging
logging.getLogger("opentelemetry.sdk._shared_internal").setLevel(logging.CRITICAL)


class JazzResearchService:
    """
    Jazz Research Service for web-powered jazz domain expertise
    Uses Google Search tool to find information about jazz music
    """

    def __init__(self):
        # Initialize GenAI client with Vertex AI using centralized config
        self.client = genai.Client(
            vertexai=True,
            project=GCPConfig.PROJECT_ID,
            location=GCPConfig.LOCATION
        )

        self.model_name = GCPConfig.VERTEX_MODEL

        # Load system prompt from file
        self.system_prompt = load_prompt('jazz_research_prompt.txt')

    @observe()
    def research(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Research jazz topics using web search

        Args:
            query: User's question about jazz
            chat_history: Optional list of previous messages

        Returns:
            Response dict with answer and web sources
        """
        try:
            # Build conversation contents
            contents = []

            # Add chat history if provided
            if chat_history:
                for msg in chat_history[-6:]:  # Last 6 messages for context
                    role = "user" if msg.get("role") == "user" else "model"
                    contents.append(types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg.get("content", ""))]
                    ))

            # Add current query
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=query)]
            ))

            # Configure Google Search tool
            google_search_tool = types.Tool(
                google_search=types.GoogleSearch()
            )

            # Generate response with Google Search using centralized config
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=ModelConfig.get_temperature('jazz_research'),
                    top_p=ModelConfig.DEFAULT_TOP_P,
                    top_k=ModelConfig.DEFAULT_TOP_K,
                    tools=[google_search_tool],
                )
            )

            answer = response.text

            # Extract web sources from grounding metadata if available
            web_sources = self._extract_web_sources(response)

            return {
                "success": True,
                "answer": answer,
                "web_sources": web_sources,
                "model": self.model_name
            }

        except Exception as e:
            print(f"[Jazz Research] Error: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": "I'm sorry, I encountered an error while researching that topic. Please try again.",
                "web_sources": []
            }

    def _extract_web_sources(self, response) -> List[Dict[str, str]]:
        """
        Extract web sources from the response's grounding metadata

        Args:
            response: GenAI response object

        Returns:
            List of source dicts with title and url
        """
        sources = []

        try:
            # Try to extract grounding metadata from the response
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]

                # Check for grounding metadata
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    grounding = candidate.grounding_metadata

                    # Extract search entry point if available
                    if hasattr(grounding, 'search_entry_point') and grounding.search_entry_point:
                        if hasattr(grounding.search_entry_point, 'rendered_content'):
                            # This contains the search results
                            pass

                    # Extract grounding chunks/sources
                    if hasattr(grounding, 'grounding_chunks') and grounding.grounding_chunks:
                        for chunk in grounding.grounding_chunks:
                            if hasattr(chunk, 'web') and chunk.web:
                                web = chunk.web
                                source = {}
                                if hasattr(web, 'title'):
                                    source['title'] = web.title
                                if hasattr(web, 'uri'):
                                    source['url'] = web.uri
                                if source:
                                    sources.append(source)

                    # Also check grounding_supports for additional sources
                    if hasattr(grounding, 'grounding_supports') and grounding.grounding_supports:
                        for support in grounding.grounding_supports:
                            if hasattr(support, 'grounding_chunk_indices'):
                                # These reference the grounding_chunks
                                pass

        except Exception as e:
            print(f"[Jazz Research] Error extracting sources: {e}")

        # Remove duplicates while preserving order
        seen = set()
        unique_sources = []
        for source in sources:
            url = source.get('url', '')
            if url and url not in seen:
                seen.add(url)
                unique_sources.append(source)

        return unique_sources[:5]  # Return top 5 sources

    def is_jazz_related(self, query: str) -> bool:
        """
        Quick check if query is likely jazz-related

        Args:
            query: User's question

        Returns:
            True if likely jazz-related
        """
        jazz_keywords = [
            'jazz', 'bebop', 'swing', 'improvisation', 'saxophone', 'trumpet',
            'miles davis', 'john coltrane', 'charlie parker', 'thelonious monk',
            'duke ellington', 'louis armstrong', 'dizzy gillespie', 'blue note',
            'prestige', 'impulse', 'modal', 'hard bop', 'cool jazz', 'fusion',
            'latin jazz', 'free jazz', 'big band', 'combo', 'quartet', 'quintet',
            'vinyl', 'record', 'album', 'recording session', 'standards'
        ]

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in jazz_keywords)
