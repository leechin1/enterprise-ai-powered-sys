"""
Knowledge component - RAG Chatbot for Misty AI Enterprise System
AI-powered chatbot with access to enterprise documents and policies
"""
import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.rag_service import RAGService


def init_session_state():
    """Initialize session state variables for chat"""
    if 'rag_messages' not in st.session_state:
        st.session_state.rag_messages = []

    if 'rag_service' not in st.session_state:
        st.session_state.rag_service = None


def render_knowledge():
    """Render the Knowledge/RAG Chatbot page"""

    init_session_state()

    st.title("Knowledge Assistant")
    st.caption("AI-powered chatbot with access to enterprise documents and policies")

    # Initialize RAG service
    try:
        if st.session_state.rag_service is None:
            st.session_state.rag_service = RAGService()
        rag = st.session_state.rag_service
    except Exception as e:
        st.error(f"Failed to initialize RAG service: {e}")
        st.info("Make sure your .env file has SUPABASE_URL, SUPABASE_SECRET_KEY, and GEMINI_API_KEY set correctly.")
        st.info("Also ensure you've run the SQL setup script: db_configure/setup_vector_embeddings.sql")
        return

    # Suggested questions - always visible at top
    suggested_questions = [
        "What is our refund policy?",
        "How do we grade vinyl records?",
        "What are our shipping procedures?",
        "Who handles customer complaints?",
        "What are the emergency procedures?",
        "How do trade-ins work?",
        "What's our privacy policy?",
    ]

    # Suggested questions section (always visible)
    with st.expander("Suggested Questions", expanded=True):
        cols = st.columns(4)
        for i, question in enumerate(suggested_questions):
            with cols[i % 4]:
                if st.button(question, key=f"suggest_{i}", use_container_width=True):
                    st.session_state.pending_question = question
                    st.rerun()

    st.markdown("---")

    # Chat container
    chat_container = st.container()

    # Display chat messages
    with chat_container:
        if not st.session_state.rag_messages:
            # Welcome message
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

    # Handle pending question from sidebar
    if 'pending_question' in st.session_state:
        user_input = st.session_state.pending_question
        del st.session_state.pending_question
        process_user_input(rag, user_input)
        st.rerun()

    # Chat input
    if user_input := st.chat_input("Ask about company policies, procedures, or guidelines..."):
        process_user_input(rag, user_input)
        st.rerun()


def process_user_input(rag: RAGService, user_input: str):
    """Process user input and get response from RAG"""

    # Add user message to history
    st.session_state.rag_messages.append({
        "role": "user",
        "content": user_input
    })

    # Prepare chat history for context
    chat_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.rag_messages[:-1]  # Exclude current message
    ]

    # Get response from RAG service
    with st.spinner("Searching knowledge base..."):
        response = rag.chat(
            query=user_input,
            chat_history=chat_history,
            include_sources=True
        )

    # Add assistant response to history
    assistant_message = {
        "role": "assistant",
        "content": response.get("answer", "I'm sorry, I couldn't process your question."),
        "sources": response.get("sources", [])
    }
    st.session_state.rag_messages.append(assistant_message)
