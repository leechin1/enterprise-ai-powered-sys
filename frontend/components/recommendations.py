import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.db_analytics import AnalyticsConnector
from services.tools.recommendation_connector import RecommendationConnector



def render_recommendations(
    analytics: AnalyticsConnector,
    recommender: RecommendationConnector
):
    st.subheader("🎯 Product Recommendations")

    mode = st.radio(
        "Recommendation type",
        ["Single Item", "Basket"],
        horizontal=True
    )

    items = analytics.get_available_albums()  # or artists

    if mode == "Single Item":
        item = st.selectbox("Select an item", items)

        if st.button("Get recommendations"):
            recs = recommender.recommend_for_item(item)

            if recs:
                st.dataframe(recs)
            else:
                st.info("No recommendations found")

    else:
        basket = st.multiselect("Select items", items)

        if st.button("Get recommendations") and basket:
            recs = recommender.recommend_for_basket(basket)

            if recs:
                st.dataframe(recs)
            else:
                st.info("No recommendations found")
