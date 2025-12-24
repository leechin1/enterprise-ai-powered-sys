"""
Styling and theming for the Misty AI Enterprise System
"""

# Color scheme inspired by jazz/vinyl aesthetic
COLORS = {
    'primary': '#6366F1',  # Indigo
    'secondary': '#8B5CF6',  # Purple
    'success': '#10B981',  # Green
    'warning': '#F59E0B',  # Amber
    'error': '#EF4444',  # Red
    'info': '#3B82F6',  # Blue
    'background': '#0F172A',  # Dark slate
    'surface': '#1E293B',  # Slate
    'text': '#F1F5F9',  # Light slate
    'text_secondary': '#94A3B8',  # Slate gray
}

# Custom CSS for the app
CUSTOM_CSS = """
<style>
    /* Main app styling */
    .stApp {
        background-color: #0F172A;
        color: #F1F5F9;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1E293B;
    }

    /* Metrics cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
        color: #F1F5F9;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.875rem;
    }

    /* Custom card styling */
    .custom-card {
        background-color: #1E293B;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #334155;
    }

    .custom-card h3 {
        color: #F1F5F9;
        margin-bottom: 1rem;
        font-size: 1.25rem;
    }

    /* Status badges */
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-block;
    }

    .status-running {
        background-color: rgba(99, 102, 241, 0.2);
        color: #A5B4FC;
    }

    .status-complete {
        background-color: rgba(16, 185, 129, 0.2);
        color: #6EE7B7;
    }

    .status-error {
        background-color: rgba(239, 68, 68, 0.2);
        color: #FCA5A5;
    }

    .status-blocked {
        background-color: rgba(245, 158, 11, 0.2);
        color: #FCD34D;
    }

    /* Activity table */
    .activity-table {
        width: 100%;
        margin-top: 1rem;
    }

    .activity-row {
        border-bottom: 1px solid #334155;
        padding: 1rem 0;
    }

    /* Chart container */
    .chart-container {
        background-color: #1E293B;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }

    /* Buttons */
    .stButton>button {
        background-color: #6366F1;
        color: white;
        border-radius: 0.375rem;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }

    .stButton>button:hover {
        background-color: #4F46E5;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }

    .stTabs [data-baseweb="tab"] {
        color: #94A3B8;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        color: #6366F1;
    }

    /* Input fields */
    .stTextInput>div>div>input {
        background-color: #1E293B;
        color: #F1F5F9;
        border: 1px solid #334155;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1E293B;
        color: #F1F5F9;
    }
</style>
"""

def get_status_badge(status):
    """Generate HTML for status badge"""
    status_map = {
        'running': 'status-running',
        'complete': 'status-complete',
        'error': 'status-error',
        'blocked': 'status-blocked',
        'pending': 'status-running',
        'completed': 'status-complete',
    }

    status_lower = status.lower()
    badge_class = status_map.get(status_lower, 'status-running')

    return f'<span class="status-badge {badge_class}">{status}</span>'
