"""
RAG Service - Retrieval-Augmented Generation for Enterprise Documents
Handles document embedding, storage, retrieval, and chat with knowledge base
Uses new Google GenAI SDK for Vertex AI
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai
from google.genai import types
from langfuse import observe
import fitz

# PDF extraction support
try:
      
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("PyMuPDF not installed. PDF support disabled. Install with: pip install pymupdf")

# Import centralized config
from services.config import GCPConfig, ModelConfig, RAGConfig

load_dotenv()

# Silence unnecessary logging
logging.getLogger("opentelemetry.sdk._shared_internal").setLevel(logging.CRITICAL)


class RAGService:
    """
    RAG Service for enterprise document knowledge base
    Handles embedding generation, document indexing, and retrieval-augmented chat
    Uses new Google GenAI SDK
    """

    def __init__(self):
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SECRET_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SECRET_KEY must be set")

        self.supabase: Client = create_client(supabase_url, supabase_key)

        # Initialize GenAI client with Vertex AI using centralized config
        self.client = genai.Client(
            vertexai=True,
            project=GCPConfig.PROJECT_ID,
            location=GCPConfig.LOCATION
        )

        # Model names from centralized config
        self.model_name = GCPConfig.VERTEX_MODEL
        self.embedding_model_name = RAGConfig.EMBEDDING_MODEL

        # Load system prompt from file
        from services.prompts import load_prompt
        self.system_prompt = load_prompt('rag_chatbot_system_prompt.txt')

    def _extract_pdf_text(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file using PyMuPDF

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text content
        """
        if not PDF_SUPPORT:
            raise ImportError("PyMuPDF is required for PDF support. Install with: pip install pymupdf")

        text_parts = []
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text_parts.append(page.get_text())

        return "\n\n".join(text_parts)

    def _chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Split text into overlapping chunks

        Args:
            text: Text to split
            chunk_size: Maximum characters per chunk (defaults to RAGConfig.CHUNK_SIZE)
            overlap: Number of overlapping characters between chunks (defaults to RAGConfig.CHUNK_OVERLAP)

        Returns:
            List of text chunks
        """
        # Use centralized config defaults
        chunk_size = chunk_size or RAGConfig.CHUNK_SIZE
        overlap = overlap or RAGConfig.CHUNK_OVERLAP

        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence or paragraph boundary
            if end < len(text):
                # Look for paragraph break
                para_break = text.rfind('\n\n', start, end)
                if para_break > start + chunk_size // 2:
                    end = para_break + 2
                else:
                    # Look for sentence break
                    sentence_break = max(
                        text.rfind('. ', start, end),
                        text.rfind('.\n', start, end),
                        text.rfind('? ', start, end),
                        text.rfind('! ', start, end)
                    )
                    if sentence_break > start + chunk_size // 2:
                        end = sentence_break + 2

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap

        return chunks

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using GenAI embedding model

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        result = self.client.models.embed_content(
            model=self.embedding_model_name,
            contents=text
        )
        return result.embeddings[0].values

    def _generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query

        Args:
            query: Search query text

        Returns:
            Embedding vector as list of floats
        """
        return self._generate_embedding(query)

    def index_document(self, document_path: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Index a document by chunking it and storing embeddings

        Args:
            document_path: Path to the document file (markdown, text, or PDF)
            metadata: Optional metadata to store with chunks

        Returns:
            Result dict with success status and chunk count
        """
        try:
            path = Path(document_path)
            document_name = path.stem
            file_extension = path.suffix.lower()

            # Read document content based on file type
            if file_extension == '.pdf':
                if not PDF_SUPPORT:
                    return {
                        "success": False,
                        "error": "PDF support not available. Install pymupdf: pip install pymupdf"
                    }
                content = self._extract_pdf_text(document_path)
            else:
                with open(document_path, 'r', encoding='utf-8') as f:
                    content = f.read()

            # Chunk the document
            chunks = self._chunk_text(content)

            # Store each chunk with its embedding
            indexed_count = 0
            for i, chunk in enumerate(chunks):
                # Generate embedding
                embedding = self._generate_embedding(chunk)

                # Prepare metadata
                chunk_metadata = {
                    "source_file": str(path.name),
                    "chunk_size": len(chunk),
                    **(metadata or {})
                }

                # Upsert to Supabase
                self.supabase.table('document_embeddings').upsert({
                    'document_name': document_name,
                    'chunk_index': i,
                    'content': chunk,
                    'embedding': embedding,
                    'metadata': chunk_metadata
                }, on_conflict='document_name,chunk_index').execute()

                indexed_count += 1

            return {
                "success": True,
                "document_name": document_name,
                "chunks_indexed": indexed_count
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def index_documents_from_directory(self, directory_path: str, extensions: List[str] = ['.md', '.txt', '.pdf']) -> Dict[str, Any]:
        """
        Index all documents from a directory

        Args:
            directory_path: Path to directory containing documents
            extensions: List of file extensions to process

        Returns:
            Result dict with success status and statistics
        """
        results = {
            "success": True,
            "documents_processed": 0,
            "total_chunks": 0,
            "errors": []
        }

        directory = Path(directory_path)

        for ext in extensions:
            for file_path in directory.glob(f"*{ext}"):
                result = self.index_document(str(file_path))

                if result["success"]:
                    results["documents_processed"] += 1
                    results["total_chunks"] += result.get("chunks_indexed", 0)
                else:
                    results["errors"].append({
                        "file": file_path.name,
                        "error": result.get("error")
                    })

        if results["errors"]:
            results["success"] = False

        return results

    def search_documents(
        self,
        query: str,
        match_count: int = 5,
        match_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant document chunks using semantic similarity

        Args:
            query: Search query
            match_count: Maximum number of results to return
            match_threshold: Minimum similarity threshold (0-1)

        Returns:
            List of matching document chunks with similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = self._generate_query_embedding(query)

            # Search using Supabase RPC function
            result = self.supabase.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': match_threshold,
                    'match_count': match_count
                }
            ).execute()

            if result.data:
                print(f"[RAG Search] RPC returned {len(result.data)} results")
                return result.data
            else:
                print("[RAG Search] RPC returned no results, trying fallback...")
                return self._fallback_search(query, match_count)

        except Exception as e:
            print(f"[RAG Search] RPC error: {e}, using fallback...")
            # Fallback: manual search if RPC not available
            return self._fallback_search(query, match_count)

    def _fallback_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fallback search method using direct query
        Less efficient but works without pgvector RPC functions
        """
        try:
            # Get all documents and compute similarity in Python
            result = self.supabase.table('document_embeddings').select('id, document_name, chunk_index, content, metadata, embedding').limit(200).execute()

            print(f"[RAG Fallback] Fetched {len(result.data) if result.data else 0} chunks from database")

            if not result.data:
                print("[RAG Fallback] No documents in database! Have you run the indexing script?")
                return []

            query_embedding = self._generate_query_embedding(query)

            # Compute cosine similarity
            def cosine_similarity(a, b):
                import numpy as np
                a = np.array(a)
                b = np.array(b)
                return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

            results_with_scores = []
            for doc in result.data:
                if doc.get('embedding'):
                    # Parse embedding if it's stored as JSON string
                    doc_embedding = doc['embedding']
                    if isinstance(doc_embedding, str):
                        doc_embedding = json.loads(doc_embedding)

                    similarity = cosine_similarity(query_embedding, doc_embedding)
                    results_with_scores.append({
                        'id': doc.get('id'),
                        'document_name': doc.get('document_name'),
                        'chunk_index': doc.get('chunk_index'),
                        'content': doc.get('content'),
                        'metadata': doc.get('metadata'),
                        'similarity': float(similarity)
                    })

            # Sort by similarity and return top results
            results_with_scores.sort(key=lambda x: x['similarity'], reverse=True)

            top_results = results_with_scores[:limit]
            if top_results:
                print(f"[RAG Fallback] Top result: {top_results[0]['document_name']} (similarity: {top_results[0]['similarity']:.2f})")

            return top_results

        except Exception as e:
            print(f"[RAG Fallback] Error: {e}")
            return []

    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into context string for LLM

        Args:
            documents: List of retrieved document chunks

        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant documents found."

        context_parts = []
        for i, doc in enumerate(documents, 1):
            doc_name = doc.get('document_name', 'Unknown').replace('_', ' ').title()
            content = doc.get('content', '')
            similarity = doc.get('similarity', 0)

            context_parts.append(
                f"[Source {i}: {doc_name} (relevance: {similarity:.0%})]\n{content}"
            )

        return "\n\n---\n\n".join(context_parts)

    @observe()
    def chat(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Chat with the knowledge base using RAG

        Args:
            query: User's question
            chat_history: Optional list of previous messages
            include_sources: Whether to include source documents in response

        Returns:
            Response dict with answer and sources
        """
        try:
            # Search for relevant documents using centralized config
            relevant_docs = self.search_documents(
                query,
                match_count=RAGConfig.MATCH_COUNT,
                match_threshold=RAGConfig.MATCH_THRESHOLD
            )

            # Debug logging
            print(f"[RAG] Query: {query}")
            print(f"[RAG] Found {len(relevant_docs)} relevant documents")

            # Format context
            context = self._format_context(relevant_docs)

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

            # Add current query with context
            user_message = f"""Based on the following context from the knowledge base, please answer the question.

CONTEXT:
{context}

QUESTION: {query}

Please provide a helpful, accurate answer based on the context provided. If the context doesn't contain relevant information, say so clearly."""

            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)]
            ))

            # Generate response using GenAI SDK with centralized config
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=ModelConfig.get_temperature('rag'),
                    top_p=ModelConfig.DEFAULT_TOP_P,
                    top_k=ModelConfig.DEFAULT_TOP_K,
                )
            )

            answer = response.text

            # Extract unique sources
            sources = []
            seen_docs = set()
            for doc in relevant_docs:
                doc_name = doc.get('document_name', '')
                if doc_name and doc_name not in seen_docs:
                    seen_docs.add(doc_name)
                    sources.append({
                        "document": doc_name.replace('_', ' ').title(),
                        "similarity": doc.get('similarity', 0)
                    })

            result = {
                "success": True,
                "answer": answer,
                "model": self.model_name
            }

            if include_sources:
                result["sources"] = sources
                result["context_used"] = len(relevant_docs) > 0

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": "I'm sorry, I encountered an error while processing your question. Please try again."
            }

    def get_indexed_documents(self) -> List[Dict[str, Any]]:
        """
        Get list of all indexed documents with statistics

        Returns:
            List of document stats
        """
        try:
            # Query document stats
            result = self.supabase.table('document_embeddings') \
                .select('document_name') \
                .execute()

            if not result.data:
                return []

            # Count chunks per document
            doc_counts = {}
            for item in result.data:
                name = item['document_name']
                doc_counts[name] = doc_counts.get(name, 0) + 1

            return [
                {"document_name": name, "chunk_count": count}
                for name, count in sorted(doc_counts.items())
            ]

        except Exception as e:
            print(f"Error getting indexed documents: {e}")
            return []

    def delete_document(self, document_name: str) -> Dict[str, Any]:
        """
        Delete a document and all its chunks from the index

        Args:
            document_name: Name of document to delete

        Returns:
            Result dict with success status
        """
        try:
            self.supabase.table('document_embeddings') \
                .delete() \
                .eq('document_name', document_name) \
                .execute()

            return {"success": True, "deleted": document_name}

        except Exception as e:
            return {"success": False, "error": str(e)}
