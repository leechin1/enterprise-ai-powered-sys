"""
Knowledge component - RAG Chatbot & Jazz Research for Misty AI Enterprise System
AI-powered chatbot with access to enterprise documents and jazz domain research
"""
import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.rag_service import RAGService

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
    tab1, tab2 = st.tabs(["📚 Enterprise Knowledge", "🎷 Jazz Research"])

    with tab1:
        render_enterprise_knowledge_tab()

    with tab2:
        render_jazz_research_tab()


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
