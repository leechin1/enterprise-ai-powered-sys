"""
Knowledge component - RAG Chatbot for Misty AI Enterprise System
"""
import streamlit as st
from datetime import datetime

def render_knowledge():
    """Render the Knowledge/RAG chatbot interface"""

    st.title("Knowledge Assistant")
    st.caption("AI-powered assistant with access to inventory, customer data, artist information, and business insights.")

    # Knowledge source selector
    col1, col2 = st.columns([3, 1])

    with col1:
        knowledge_sources = st.multiselect(
            "Active Knowledge Sources",
            ["Inventory Database", "Customer Records", "Artist Encyclopedia", "Sales History", "Supplier Catalogs", "Product Reviews"],
            default=["Inventory Database", "Artist Encyclopedia", "Sales History"]
        )

    with col2:
        search_mode = st.selectbox(
            "Search Mode",
            ["Semantic", "Keyword", "Hybrid"]
        )

    st.markdown("---")

    # Initialize chat history
    if "knowledge_messages" not in st.session_state:
        st.session_state.knowledge_messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm your Misty Knowledge Assistant. I can help you with:\n\n- Finding specific vinyl records in inventory\n- Artist and album information\n- Customer purchase history and preferences\n- Sales trends and analytics\n- Supplier and pricing information\n- Recommendations based on our catalog\n\nWhat would you like to know?",
                "timestamp": datetime.now()
            }
        ]

    # Chat container
    chat_container = st.container()

    # Display chat messages
    with chat_container:
        for message in st.session_state.knowledge_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

                # Show sources if available
                if "sources" in message:
                    with st.expander("📚 Sources"):
                        for source in message["sources"]:
                            st.caption(f"• {source}")

    # Chat input
    if prompt := st.chat_input("Ask me anything about Misty's operations..."):
        # Add user message
        st.session_state.knowledge_messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now()
        })

        # Simulate AI response (this will be connected to your backend later)
        response = generate_knowledge_response(prompt, knowledge_sources)

        # Add assistant message
        st.session_state.knowledge_messages.append({
            "role": "assistant",
            "content": response["content"],
            "sources": response.get("sources", []),
            "timestamp": datetime.now()
        })

        st.rerun()

    # Sidebar with quick actions
    with st.sidebar:
        st.markdown("### Quick Queries")

        if st.button("📊 Weekly sales summary", use_container_width=True):
            prompt = "Give me a summary of this week's sales performance"
            st.session_state.knowledge_messages.append({
                "role": "user",
                "content": prompt,
                "timestamp": datetime.now()
            })
            response = generate_knowledge_response(prompt, knowledge_sources)
            st.session_state.knowledge_messages.append({
                "role": "assistant",
                "content": response["content"],
                "sources": response.get("sources", []),
                "timestamp": datetime.now()
            })
            st.rerun()

        if st.button("🎵 Low stock albums", use_container_width=True):
            prompt = "What albums are currently low in stock?"
            st.session_state.knowledge_messages.append({
                "role": "user",
                "content": prompt,
                "timestamp": datetime.now()
            })
            response = generate_knowledge_response(prompt, knowledge_sources)
            st.session_state.knowledge_messages.append({
                "role": "assistant",
                "content": response["content"],
                "sources": response.get("sources", []),
                "timestamp": datetime.now()
            })
            st.rerun()

        if st.button("⭐ Top customers", use_container_width=True):
            prompt = "Who are our top 5 customers this month?"
            st.session_state.knowledge_messages.append({
                "role": "user",
                "content": prompt,
                "timestamp": datetime.now()
            })
            response = generate_knowledge_response(prompt, knowledge_sources)
            st.session_state.knowledge_messages.append({
                "role": "assistant",
                "content": response["content"],
                "sources": response.get("sources", []),
                "timestamp": datetime.now()
            })
            st.rerun()

        if st.button("🔍 Rare vinyl finder", use_container_width=True):
            prompt = "What rare or valuable vinyl records do we have in stock?"
            st.session_state.knowledge_messages.append({
                "role": "user",
                "content": prompt,
                "timestamp": datetime.now()
            })
            response = generate_knowledge_response(prompt, knowledge_sources)
            st.session_state.knowledge_messages.append({
                "role": "assistant",
                "content": response["content"],
                "sources": response.get("sources", []),
                "timestamp": datetime.now()
            })
            st.rerun()

        st.markdown("---")

        if st.button("🗑️ Clear conversation", use_container_width=True):
            st.session_state.knowledge_messages = []
            st.rerun()


def generate_knowledge_response(prompt, sources):
    """
    Generate a simulated knowledge response
    This will be replaced with actual RAG backend later
    """

    # Simulated responses based on keywords
    prompt_lower = prompt.lower()

    if "sales" in prompt_lower or "performance" in prompt_lower:
        return {
            "content": """Based on the latest data, here's this week's sales summary:

**Sales Overview (Dec 18-24, 2024)**
- Total Revenue: $18,450
- Units Sold: 342 vinyl records
- Average Order Value: $53.95
- Top Genre: Jazz Fusion (28% of sales)

**Top Selling Albums:**
1. Kind of Blue - Miles Davis (23 copies)
2. A Love Supreme - John Coltrane (18 copies)
3. Time Out - Dave Brubeck (15 copies)

**Trends:**
- 12% increase compared to last week
- Online orders up 18%
- Store traffic steady at 145 daily visitors
- Customer retention rate: 67%

This represents strong performance, especially in the Jazz Fusion category.""",
            "sources": [
                "Sales Database - Weekly Report (Dec 18-24, 2024)",
                "Inventory Management System - Transaction Log",
                "Customer Analytics Dashboard - Active Period"
            ]
        }

    elif "low stock" in prompt_lower or "inventory" in prompt_lower:
        return {
            "content": """Here are the albums currently low in stock (≤5 units):

**Critical Stock Levels:**
1. **The Black Saint and the Sinner Lady** - Charles Mingus (2 units)
2. **Blue Train** - John Coltrane (3 units)
3. **Moanin'** - Art Blakey & The Jazz Messengers (4 units)
4. **Somethin' Else** - Cannonball Adderley (2 units)
5. **Waltz for Debby** - Bill Evans Trio (5 units)

**Recommended Actions:**
- Reorder suggested for all items (high demand, reliable suppliers)
- Estimated delivery: 5-7 business days
- Total reorder cost estimate: $380

Would you like me to generate purchase orders for these items?""",
            "sources": [
                "Inventory Database - Current Stock Levels",
                "Sales Trend Analysis - 30 Day Moving Average",
                "Supplier Catalog - Availability Check"
            ]
        }

    elif "customer" in prompt_lower or "top" in prompt_lower:
        return {
            "content": """Here are our top 5 customers for December 2024:

**Top Customers by Revenue:**
1. **Marcus Johnson** - $1,245 (8 purchases)
   - Favorite Genre: Bebop & Hard Bop
   - Last Purchase: Blue Note Records Collection

2. **Sarah Williams** - $980 (12 purchases)
   - Favorite Genre: Smooth Jazz
   - Last Purchase: Herbie Hancock - Head Hunters

3. **David Chen** - $875 (6 purchases)
   - Favorite Genre: Jazz Fusion
   - Last Purchase: Weather Report - Heavy Weather

4. **Emily Rodriguez** - $790 (10 purchases)
   - Favorite Genre: Vocal Jazz
   - Last Purchase: Ella Fitzgerald Collection

5. **James Mitchell** - $685 (7 purchases)
   - Favorite Genre: Modal Jazz
   - Last Purchase: Miles Davis Complete Collection

**Insights:**
- Average purchase frequency: 8.6 purchases/month
- High-value segment shows 85% retention
- Recommendation engine accuracy: 73%""",
            "sources": [
                "Customer Database - Purchase History",
                "CRM System - Customer Profiles",
                "Analytics Engine - Customer Segmentation"
            ]
        }

    elif "rare" in prompt_lower or "valuable" in prompt_lower:
        return {
            "content": """Here are the rare and valuable vinyl records currently in our inventory:

**Premium Collection:**
1. **Thelonious Monk - Brilliant Corners** (1957 Blue Note Original)
   - Condition: VG+/NM
   - Value: $850
   - Stock: 1 unit

2. **Art Pepper - Surf Ride** (1952 First Pressing)
   - Condition: VG/VG+
   - Value: $620
   - Stock: 1 unit

3. **Grant Green - Matador** (1964 Blue Note)
   - Condition: NM/NM
   - Value: $485
   - Stock: 2 units

4. **Freddie Hubbard - Red Clay** (1970 CTI Original)
   - Condition: VG+/VG+
   - Value: $395
   - Stock: 1 unit

**Recommendations:**
- Consider featuring these in premium display
- Potential auction interest for items >$500
- Insurance review recommended
- High collector demand in current market""",
            "sources": [
                "Inventory Database - Premium Catalog",
                "Vinyl Valuation API - Current Market Prices",
                "Discogs Integration - Rarity Assessment"
            ]
        }

    else:
        # Generic response
        return {
            "content": f"""I understand you're asking about: "{prompt}"

I have access to the following information sources:
{', '.join(sources)}

To provide you with the most accurate information, could you please specify:
- What specific data you're looking for?
- Any particular time frame?
- Would you like detailed analytics or a summary?

Some examples of what I can help with:
- Inventory searches and stock levels
- Sales performance and trends
- Customer insights and preferences
- Artist and album information
- Supplier and pricing data
- Recommendations and predictions""",
            "sources": knowledge_sources
        }
