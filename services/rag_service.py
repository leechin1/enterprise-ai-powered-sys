"""
RAG Service - Retrieval-Augmented Generation for Enterprise Documents
Handles document embedding, storage, retrieval, and chat with knowledge base
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
import vertexai
from vertexai.language_models import TextEmbeddingModel
from langchain_google_vertexai import ChatVertexAI
from langfuse import observe

load_dotenv()

# Configuration
MODEL = os.getenv('VERTEX_MODEL')
PROJECT_ID = os.getenv('GCP_PROJECT_ID')
LOCATION = os.getenv('GCP_LOCATION', 'us-central1')
EMBEDDING_MODEL = "text-embedding-004"
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks
EMBEDDING_DIMENSION = 768  # Google text-embedding-004 dimension

# Silence unnecessary logging
logging.getLogger("opentelemetry.sdk._shared_internal").setLevel(logging.CRITICAL)


class RAGService:
    """
    RAG Service for enterprise document knowledge base
    Handles embedding generation, document indexing, and retrieval-augmented chat
    """

    def __init__(self):
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SECRET_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SECRET_KEY must be set")

        self.supabase: Client = create_client(supabase_url, supabase_key)

        # Initialize Vertex AI
        if PROJECT_ID:
            vertexai.init(project=PROJECT_ID, location=LOCATION)

        # Initialize embedding model via Vertex AI
        self.embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

        # Initialize LLM for chat via Vertex AI (uses GCP credits)
        self.llm = ChatVertexAI(
            model=MODEL,
            project=PROJECT_ID,
            location=LOCATION,
            temperature=0.7,
        )

        # System prompt for RAG chatbot
        self.system_prompt = """You are a helpful AI assistant for Misty Jazz Records, a vinyl record store.
You answer questions based ONLY on the provided context from the company's knowledge base.

STRICT RULES:
1. ONLY use information from the CONTEXT provided - never make up information
2. If the context contains relevant information, provide a detailed answer based on it
3. If the context does NOT contain relevant information, say exactly: "I don't have information about that in my knowledge base."
4. NEVER invent names, roles, or details not in the context
5. NEVER suggest contacting specific people unless they are explicitly mentioned in the context
6. Quote specific policies or procedures from the context when relevant

Be concise but thorough. Maintain a professional, helpful tone."""

    def _chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """
        Split text into overlapping chunks

        Args:
            text: Text to split
            chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters between chunks

        Returns:
            List of text chunks
        """
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
        Generate embedding for text using Vertex AI's embedding model

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        embeddings = self.embedding_model.get_embeddings([text])
        return embeddings[0].values

    def _generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query using Vertex AI

        Args:
            query: Search query text

        Returns:
            Embedding vector as list of floats
        """
        embeddings = self.embedding_model.get_embeddings([query])
        return embeddings[0].values

    def index_document(self, document_path: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Index a document by chunking it and storing embeddings

        Args:
            document_path: Path to the document file (markdown or text)
            metadata: Optional metadata to store with chunks

        Returns:
            Result dict with success status and chunk count
        """
        try:
            path = Path(document_path)
            document_name = path.stem

            # Read document content
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

    def index_documents_from_directory(self, directory_path: str, extensions: List[str] = ['.md', '.txt']) -> Dict[str, Any]:
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
            # Search for relevant documents (lower threshold to catch more results)
            relevant_docs = self.search_documents(query, match_count=5, match_threshold=0.3)

            # Debug logging
            print(f"[RAG] Query: {query}")
            print(f"[RAG] Found {len(relevant_docs)} relevant documents")

            # Format context
            context = self._format_context(relevant_docs)

            # Build messages
            messages = [
                ("system", self.system_prompt),
            ]

            # Add chat history if provided
            if chat_history:
                for msg in chat_history[-6:]:  # Last 6 messages for context
                    role = "human" if msg.get("role") == "user" else "assistant"
                    messages.append((role, msg.get("content", "")))

            # Add current query with context
            user_message = f"""Based on the following context from the knowledge base, please answer the question.

CONTEXT:
{context}

QUESTION: {query}

Please provide a helpful, accurate answer based on the context provided. If the context doesn't contain relevant information, say so clearly."""

            messages.append(("human", user_message))

            # Get response from LLM
            response = self.llm.invoke(messages)
            answer = response.content

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
                "model": MODEL
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
