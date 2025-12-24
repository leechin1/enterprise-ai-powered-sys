# Quick Start Guide

## Installation & Setup

### Using uv (Recommended)

```bash
# Create virtual environment
uv venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install streamlit pandas plotly
```

### Using pip

```bash
# Create virtual environment
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
streamlit run main.py
```

The application will automatically open in your browser at `http://localhost:8501`

## First Steps

1. **Explore the Dashboard**: View key metrics, recent activity, and analytics
2. **Try the Knowledge Assistant**: Ask questions about inventory, customers, or sales
3. **Check Smart Inventory**: Review AI recommendations and demand forecasts
4. **Browse Analytics**: Explore sales trends, customer insights, and predictions
5. **View Activity**: Monitor automated workflows and executions
6. **Manage Cases**: See customer service tickets and AI suggestions
7. **Configure Settings**: Adjust AI models, integrations, and preferences

## Demo Features

All data in the demo is simulated to showcase capabilities:

- **Real-time Metrics**: 6,412 processes per 24h, 0.18% failure rate
- **AI Recommendations**: Inventory reorder suggestions with 90%+ confidence
- **Predictive Analytics**: 30-day demand forecasting
- **Sentiment Analysis**: Customer feedback analysis
- **Workflow Automation**: 12+ active automated processes

## Navigation

Use the sidebar to navigate between:
- 📊 Dashboard
- 📈 Analytics
- ⚡ Activity
- 📋 Cases
- 📦 Smart Inventory
- 🧠 Knowledge
- ⚙️ Configuration

## Tips

- Click on expandable sections to see more details
- Use filters to customize views
- Try the Knowledge Assistant's quick query buttons
- Explore different time ranges in Analytics
- Check AI recommendations in Smart Inventory

## Next Steps

This is a UI demo. To make it functional:

1. Connect to your database
2. Integrate AI models (OpenAI, Anthropic, etc.)
3. Implement backend APIs
4. Add authentication
5. Connect real data sources

See [README.md](README.md) for full documentation.
