"""
Knowledge component - RAG Chatbot & Jazz Research for Misty AI Enterprise System
AI-powered chatbot with access to enterprise documents and jazz domain research
"""
import streamlit as st
from datetime import datetime
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.rag_service import RAGService
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Supabase storage configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SECRET_KEY')
BUCKET_NAME = "enterprise-documents"

# Import jazz research service
try:
    from services.jazz_research_service import JazzResearchService
    JAZZ_RESEARCH_AVAILABLE = True
except Exception as e:
    JAZZ_RESEARCH_AVAILABLE = False
    print(f"Jazz research service not available: {e}")

# Import activity log service
try:
    from services.activity_log_service import get_activity_log_service
    ACTIVITY_LOG_AVAILABLE = True
except Exception as e:
    ACTIVITY_LOG_AVAILABLE = False
    print(f"Activity log service not available: {e}")


def log_activity(action_type: str, description: str, category: str = "knowledge", **kwargs):
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


def get_supabase_storage():
    """Get Supabase storage client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_to_bucket(file_content: bytes, file_name: str) -> dict:
    """Upload a file to Supabase storage bucket"""
    try:
        supabase = get_supabase_storage()
        if not supabase:
            return {"success": False, "error": "Supabase not configured"}

        # Determine content type
        ext = Path(file_name).suffix.lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.md': 'text/markdown',
            '.txt': 'text/plain'
        }
        content_type = content_types.get(ext, 'application/octet-stream')

        # Upload to bucket (upsert to overwrite existing)
        response = supabase.storage.from_(BUCKET_NAME).upload(
            path=file_name,
            file=file_content,
            file_options={"content-type": content_type, "upsert": "true"}
        )

        # Get public URL
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)

        return {
            "success": True,
            "url": public_url,
            "file_name": file_name
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_document_url(file_name: str) -> str:
    """Get the public URL for a document in the bucket"""
    try:
        supabase = get_supabase_storage()
        if not supabase:
            return None

        # Try different file extensions
        extensions = ['.pdf', '.md', '.txt']
        base_name = Path(file_name).stem

        for ext in extensions:
            try:
                full_name = f"{base_name}{ext}"
                url = supabase.storage.from_(BUCKET_NAME).get_public_url(full_name)
                return url
            except:
                continue
        return None
    except Exception as e:
        print(f"Error getting document URL: {e}")
        return None


def list_bucket_files() -> list:
    """List all files in the bucket"""
    try:
        supabase = get_supabase_storage()
        if not supabase:
            return []
        files = supabase.storage.from_(BUCKET_NAME).list()
        return files if files else []
    except Exception as e:
        print(f"Error listing bucket files: {e}")
        return []


def init_session_state():
    """Initialize session state variables for chat"""
    if 'rag_messages' not in st.session_state:
        st.session_state.rag_messages = []

    if 'jazz_messages' not in st.session_state:
        st.session_state.jazz_messages = []

    if 'rag_service' not in st.session_state:
        st.session_state.rag_service = None

    if 'jazz_service' not in st.session_state:
        st.session_state.jazz_service = None


def render_knowledge():
    """Render the Knowledge/RAG Chatbot page with tabs"""

    init_session_state()

    st.title("Knowledge Assistant")
    st.caption("AI-powered chatbot with access to enterprise documents and jazz domain research")

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📚 Enterprise Knowledge", "🎷 Jazz Research", "📁 Document Management"])

    with tab1:
        render_enterprise_knowledge_tab()

    with tab2:
        render_jazz_research_tab()

    with tab3:
        render_document_management_tab()


def render_enterprise_knowledge_tab():
    """Render the Enterprise Knowledge RAG chatbot tab"""

    st.subheader("Enterprise Knowledge Base")
    st.caption("Ask questions about company policies, procedures, and guidelines")

    # Initialize RAG service
    try:
        if st.session_state.rag_service is None:
            st.session_state.rag_service = RAGService()
        rag = st.session_state.rag_service
    except Exception as e:
        st.error(f"Failed to initialize RAG service: {e}")
        st.info("Make sure your .env file has SUPABASE_URL, SUPABASE_SECRET_KEY, and GCP credentials set correctly.")
        return

    # Suggested questions
    suggested_questions = [
        "What is our refund policy?",
        "How do we grade vinyl records?",
        "What are our shipping procedures?",
        "Who handles customer complaints?",
        "What are the emergency procedures?",
        "How do trade-ins work?",
        "What's our privacy policy?",
    ]

    # Suggested questions section
    with st.expander("Suggested Questions", expanded=True):
        cols = st.columns(4)
        for i, question in enumerate(suggested_questions):
            with cols[i % 4]:
                if st.button(question, key=f"suggest_{i}", use_container_width=True):
                    st.session_state.pending_rag_question = question
                    st.rerun()

    st.markdown("---")

    # Chat container
    chat_container = st.container()

    # Display chat messages
    with chat_container:
        if not st.session_state.rag_messages:
            st.markdown("""
            ### Welcome!

            I'm here to help you find information from our enterprise documents including company policies,
            employee guidelines, operations manuals, and specialized guides.

            **Click a suggested question above or type your own below.**
            """)
        else:
            for message in st.session_state.rag_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

                    # Show sources if available
                    if message["role"] == "assistant" and message.get("sources"):
                        with st.expander("Sources", expanded=False):
                            for source in message["sources"]:
                                similarity = source.get("similarity", 0)
                                doc_name = source.get("document", "Unknown")
                                st.caption(f"- {doc_name} ({similarity:.0%} relevant)")

    # Handle pending question
    if 'pending_rag_question' in st.session_state:
        user_input = st.session_state.pending_rag_question
        del st.session_state.pending_rag_question
        process_rag_input(rag, user_input)
        st.rerun()

    # Chat input
    if user_input := st.chat_input("Ask about company policies, procedures, or guidelines...", key="rag_chat_input"):
        process_rag_input(rag, user_input)
        st.rerun()


def process_rag_input(rag: RAGService, user_input: str):
    """Process user input and get response from RAG"""

    # Add user message to history
    st.session_state.rag_messages.append({
        "role": "user",
        "content": user_input
    })

    # Prepare chat history for context
    chat_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.rag_messages[:-1]
    ]

    # Get response from RAG service
    with st.spinner("Searching knowledge base..."):
        response = rag.chat(
            query=user_input,
            chat_history=chat_history,
            include_sources=True
        )

    # Log the activity
    log_activity(
        action_type="rag_query",
        description=f"Knowledge base query: {user_input[:50]}...",
        category="knowledge",
        metadata={
            "query": user_input,
            "sources_found": len(response.get("sources", [])),
            "success": response.get("success", False)
        }
    )

    # Add assistant response to history
    assistant_message = {
        "role": "assistant",
        "content": response.get("answer", "I'm sorry, I couldn't process your question."),
        "sources": response.get("sources", [])
    }
    st.session_state.rag_messages.append(assistant_message)


def render_jazz_research_tab():
    """Render the Jazz Research tab with web search capabilities"""

    st.subheader("Jazz Research Assistant")
    st.caption("Ask questions about jazz history, artists, albums, genres, and music theory - powered by web search")

    if not JAZZ_RESEARCH_AVAILABLE:
        st.warning("Jazz Research service not available. Please check your configuration.")
        st.info("Make sure you have the Google GenAI SDK installed: `pip install google-genai`")
        return

    # Initialize Jazz Research service
    try:
        if st.session_state.jazz_service is None:
            st.session_state.jazz_service = JazzResearchService()
        jazz = st.session_state.jazz_service
    except Exception as e:
        st.error(f"Failed to initialize Jazz Research service: {e}")
        st.info("Make sure your .env file has GEMINI_API_KEY set correctly.")
        return

    # Jazz topic suggestions
    jazz_topics = [
        "Who is Miles Davis?",
        "What is bebop jazz?",
        "Best jazz albums of all time",
        "History of Blue Note Records",
        "What is modal jazz?",
        "Famous jazz saxophonists",
        "Origins of cool jazz",
        "John Coltrane's influence",
    ]

    # Suggested topics section
    with st.expander("Suggested Jazz Topics", expanded=True):
        cols = st.columns(4)
        for i, topic in enumerate(jazz_topics):
            with cols[i % 4]:
                if st.button(topic, key=f"jazz_suggest_{i}", use_container_width=True):
                    st.session_state.pending_jazz_question = topic
                    st.rerun()

    st.markdown("---")

    # Important notice
    st.info("🎷 **Jazz Research Mode**: This assistant answers questions about jazz music ONLY. Questions about other topics will be politely redirected.")

    # Chat container
    chat_container = st.container()

    # Display chat messages
    with chat_container:
        if not st.session_state.jazz_messages:
            st.markdown("""
            ### Welcome to Jazz Research!

            I'm your jazz music expert, powered by web search to give you the latest and most accurate information about:

            - **Jazz History** - Origins, evolution, and major movements
            - **Artists & Musicians** - Biographies, discographies, and influences
            - **Albums & Recordings** - Classic and contemporary jazz albums
            - **Genres & Styles** - Bebop, cool jazz, hard bop, fusion, and more
            - **Music Theory** - Jazz harmony, improvisation techniques, and composition
            - **Record Labels** - Blue Note, Prestige, Impulse!, and others

            **Click a suggested topic above or ask your own question below.**
            """)
        else:
            for message in st.session_state.jazz_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

                    # Show web sources if available
                    if message["role"] == "assistant" and message.get("web_sources"):
                        with st.expander("🔗 Web Sources", expanded=False):
                            for source in message["web_sources"]:
                                st.markdown(f"- [{source.get('title', 'Source')}]({source.get('url', '#')})")

    # Handle pending question
    if 'pending_jazz_question' in st.session_state:
        user_input = st.session_state.pending_jazz_question
        del st.session_state.pending_jazz_question
        process_jazz_input(jazz, user_input)
        st.rerun()

    # Chat input
    if user_input := st.chat_input("Ask about jazz history, artists, albums, or music theory...", key="jazz_chat_input"):
        process_jazz_input(jazz, user_input)
        st.rerun()

    # Clear chat button
    st.markdown("---")
    if st.button("🗑️ Clear Jazz Chat History", use_container_width=True):
        st.session_state.jazz_messages = []
        st.rerun()


def process_jazz_input(jazz, user_input: str):
    """Process user input and get response from Jazz Research service"""

    # Add user message to history
    st.session_state.jazz_messages.append({
        "role": "user",
        "content": user_input
    })

    # Prepare chat history for context
    chat_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.jazz_messages[:-1]
    ]

    # Get response from Jazz Research service
    with st.spinner("🎷 Researching jazz knowledge..."):
        response = jazz.research(
            query=user_input,
            chat_history=chat_history
        )

    # Log the activity
    log_activity(
        action_type="rag_query",
        description=f"Jazz research query: {user_input[:50]}...",
        category="knowledge",
        metadata={
            "query": user_input,
            "type": "jazz_research",
            "web_search": True,
            "success": response.get("success", False)
        }
    )

    # Add assistant response to history
    assistant_message = {
        "role": "assistant",
        "content": response.get("answer", "I'm sorry, I couldn't research that topic."),
        "web_sources": response.get("web_sources", [])
    }
    st.session_state.jazz_messages.append(assistant_message)


def render_document_management_tab():
    """Render the Document Management tab for viewing and managing knowledge base documents"""

    st.subheader("Document Management")
    st.caption("View, upload, and manage documents in the knowledge base")

    # Initialize RAG service
    try:
        if st.session_state.rag_service is None:
            st.session_state.rag_service = RAGService()
        rag = st.session_state.rag_service
    except Exception as e:
        st.error(f"Failed to initialize RAG service: {e}")
        return

    # Create two columns for layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Indexed Documents")

        # Get indexed documents
        indexed_docs = rag.get_indexed_documents()

        # Get files from bucket for URL lookup
        bucket_files = list_bucket_files()
        bucket_file_names = {f.get('name', ''): f for f in bucket_files if f.get('name')}

        if not indexed_docs:
            st.info("No documents indexed yet. Upload documents below to get started.")
        else:
            # Display documents in a table-like format
            for doc in indexed_docs:
                doc_name = doc.get('document_name', 'Unknown')
                chunk_count = doc.get('chunk_count', 0)
                display_name = doc_name.replace('_', ' ').title()

                with st.container():
                    doc_col1, doc_col2, doc_col3, doc_col4 = st.columns([3, 1, 0.5, 0.5])

                    with doc_col1:
                        st.markdown(f"**{display_name}**")

                    with doc_col2:
                        st.caption(f"{chunk_count} chunks")

                    with doc_col3:
                        # View button - opens document in new tab
                        doc_url = get_document_url(doc_name)
                        if doc_url:
                            st.link_button("📄", doc_url, help=f"View {display_name}")
                        else:
                            st.button("📄", key=f"view_{doc_name}", disabled=True, help="Document not in storage")

                    with doc_col4:
                        if st.button("🗑️", key=f"delete_{doc_name}", help=f"Delete {display_name}"):
                            result = rag.delete_document(doc_name)
                            if result.get('success'):
                                st.success(f"Deleted: {display_name}")
                                log_activity(
                                    action_type="document_delete",
                                    description=f"Deleted document: {display_name}",
                                    category="knowledge",
                                    metadata={"document_name": doc_name}
                                )
                                st.rerun()
                            else:
                                st.error(f"Failed to delete: {result.get('error')}")

                    st.markdown("---")

            # Summary stats
            total_docs = len(indexed_docs)
            total_chunks = sum(doc.get('chunk_count', 0) for doc in indexed_docs)
            st.caption(f"**Total:** {total_docs} documents, {total_chunks} chunks indexed")

    with col2:
        st.markdown("### Upload Document")

        # File uploader - now supports PDF, MD, and TXT
        uploaded_file = st.file_uploader(
            "Choose a file to upload",
            type=['pdf', 'md', 'txt'],
            help="Upload a PDF, Markdown, or text file to add to the knowledge base"
        )

        if uploaded_file is not None:
            file_ext = Path(uploaded_file.name).suffix.lower()
            st.markdown(f"**File:** {uploaded_file.name}")
            st.markdown(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
            st.markdown(f"**Type:** {file_ext.upper()[1:]}")

            if st.button("📥 Upload & Index Document", type="primary", use_container_width=True):
                with st.spinner("Uploading and indexing document..."):
                    try:
                        # Read file content
                        file_content = uploaded_file.read()

                        # Upload to Supabase bucket
                        bucket_result = upload_to_bucket(file_content, uploaded_file.name)
                        if bucket_result.get('success'):
                            st.success(f"✓ Uploaded to storage: {uploaded_file.name}")
                        else:
                            st.warning(f"Storage upload skipped: {bucket_result.get('error')}")

                        # Save file locally for indexing
                        docs_dir = Path(__file__).parent.parent.parent / "assets" / "enterprise_documents"
                        docs_dir.mkdir(parents=True, exist_ok=True)
                        file_path = docs_dir / uploaded_file.name

                        # Write file content (binary for PDF, text for others)
                        if file_ext == '.pdf':
                            with open(file_path, 'wb') as f:
                                f.write(file_content)
                        else:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(file_content.decode('utf-8'))

                        # Index the document
                        result = rag.index_document(str(file_path))

                        if result.get('success'):
                            st.success(f"✓ Indexed: {uploaded_file.name}")
                            st.info(f"Created {result.get('chunks_indexed', 0)} chunks")

                            log_activity(
                                action_type="document_upload",
                                description=f"Uploaded and indexed: {uploaded_file.name}",
                                category="knowledge",
                                metadata={
                                    "document_name": result.get('document_name'),
                                    "chunks": result.get('chunks_indexed', 0),
                                    "bucket_url": bucket_result.get('url'),
                                    "file_type": file_ext
                                }
                            )
                            st.rerun()
                        else:
                            st.error(f"Indexing failed: {result.get('error')}")

                    except Exception as e:
                        st.error(f"Upload failed: {e}")

        st.markdown("---")

        # Re-index all documents button
        st.markdown("### Re-index All")
        st.caption("Re-index all documents from the enterprise documents folder (includes PDFs)")

        if st.button("🔄 Re-index All Documents", use_container_width=True):
            with st.spinner("Re-indexing all documents..."):
                try:
                    docs_dir = Path(__file__).parent.parent.parent / "assets" / "enterprise_documents"

                    if not docs_dir.exists():
                        st.error("Enterprise documents folder not found")
                    else:
                        result = rag.index_documents_from_directory(str(docs_dir))

                        if result.get('success'):
                            st.success("Re-indexing complete!")
                            st.info(f"Processed {result.get('documents_processed', 0)} documents, {result.get('total_chunks', 0)} chunks")

                            log_activity(
                                action_type="document_reindex",
                                description="Re-indexed all enterprise documents",
                                category="knowledge",
                                metadata={
                                    "documents": result.get('documents_processed', 0),
                                    "chunks": result.get('total_chunks', 0)
                                }
                            )
                        else:
                            st.warning("Re-indexing completed with errors")
                            for err in result.get('errors', []):
                                st.error(f"{err.get('file')}: {err.get('error')}")

                        st.rerun()

                except Exception as e:
                    st.error(f"Re-indexing failed: {e}")
