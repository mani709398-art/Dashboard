"""
Consumables & Toners Tracking Dashboard
Main Streamlit Application - MDF Style Dark Theme
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from io import BytesIO
import database as db

# Page configuration
st.set_page_config(
    page_title="🖥️ IT Inventory Tracking Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Admin users who can add new users
ADMIN_USERS = ['gmanisel', 'ddink', 'saswith']

# MDF Style CSS - Dark Navy Theme with White Cards and Orange Accents
st.markdown("""
<style>
    /* Main app background - Light Gray */
    .stApp {
        background: #f0f2f5;
    }
    
    /* Main content area */
    .main .block-container {
        background: #f0f2f5;
        padding: 1rem 2rem;
    }
    
    /* Header styling */
    .main-header {
        color: #1a2744;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .sub-header {
        color: #0984e3;
        font-size: 1rem;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
    
    /* Sidebar styling - Dark Navy */
    [data-testid="stSidebar"] {
        background: #1a2744;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #f39c12 !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox label {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #ffffff !important;
        background: rgba(255,255,255,0.1);
        padding: 8px 12px;
        border-radius: 8px;
        margin: 4px 0;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] {
        background: #f39c12;
        color: white !important;
    }
    
    [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] p {
        color: #ffffff !important;
    }
    
    /* Sidebar selectbox - white text and dropdown */
    [data-testid="stSidebar"] [data-baseweb="select"] {
        background: rgba(255,255,255,0.1) !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: rgba(255,255,255,0.1) !important;
        border-radius: 8px;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] span {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] svg {
        fill: #ffffff !important;
    }
    
    /* Custom metric cards - Dark Navy with shadow */
    .metric-card {
        background: linear-gradient(135deg, #1a2744 0%, #2d3a4a 100%);
        border-radius: 12px;
        padding: 20px 25px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.2);
        margin-bottom: 15px;
    }
    
    .metric-label {
        color: #ffffff;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0;
    }
    
    .metric-value-green {
        color: #00b894;
    }
    
    .metric-value-blue {
        color: #0984e3;
    }
    
    .metric-value-orange {
        color: #f39c12;
    }
    
    .metric-value-red {
        color: #e74c3c;
    }
    
    .metric-value-purple {
        color: #9b59b6;
    }
    
    .metric-value-dark {
        color: #ffffff;
    }
    
    .metric-sub {
        color: #f39c12;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    /* Live monitoring badge */
    .live-badge {
        background: #00b894;
        color: white;
        padding: 8px 20px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    
    .live-dot {
        width: 10px;
        height: 10px;
        background: white;
        border-radius: 50%;
        animation: pulse-dot 1.5s infinite;
    }
    
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* White content cards */
    .content-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        color: #2d3436;
    }
    
    .card-header {
        color: #1a2744 !important;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 2px solid #f0f2f5;
        background: transparent;
    }
    
    /* Ensure all text in tabs is visible */
    .stTabs [data-baseweb="tab-panel"] {
        color: #ffffff;
    }
    
    /* Headers inside tabs */
    h4, h3, h2, h1 {
        color: #1a2744 !important;
    }
    
    /* Plotly chart titles - white */
    .js-plotly-plot .plotly .gtitle {
        fill: #ffffff !important;
    }
    
    /* Force all content inside cards to be white */
    .content-card * {
        color: #ffffff;
    }
    
    .content-card h1, .content-card h2, .content-card h3, .content-card h4, .content-card h5, .content-card h6 {
        color: #ffffff !important;
    }
    
    /* Markdown text in main area */
    .main .stMarkdown p, .main .stMarkdown span, .main .stMarkdown div {
        color: inherit;
    }
    
    /* Alert styling */
    .low-stock-alert {
        background: #3d2a2a;
        border-left: 4px solid #e74c3c;
        padding: 12px 18px;
        margin: 8px 0;
        border-radius: 0 8px 8px 0;
        color: #ffffff;
    }
    
    /* Orange buttons */
    .stButton > button {
        background: #f39c12;
        color: white;
        border: none;
        padding: 10px 25px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: #e67e22;
        transform: translateY(-2px);
    }
    
    /* Red download/export button */
    .stDownloadButton > button {
        background: #e74c3c !important;
        color: white !important;
        border: none !important;
        padding: 10px 25px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: #c0392b !important;
        transform: translateY(-2px);
    }
    
    /* Refresh button style */
    .refresh-btn {
        background: #f39c12;
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        cursor: pointer;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #2d3a4a;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        color: #ffffff;
        border: 2px solid #3d4a5a;
    }
    
    .stTabs [aria-selected="true"] {
        background: #0984e3;
        color: white;
        border-color: #0984e3;
    }
    
    /* Table styling */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        background: #2d3a4a;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .styled-table thead tr {
        background: #1a2744;
        color: white;
    }
    
    .styled-table th {
        padding: 15px;
        font-weight: 600;
        text-align: center;
        font-size: 0.85rem;
        text-transform: uppercase;
    }
    
    .styled-table td {
        padding: 12px 15px;
        text-align: center;
        border-bottom: 1px solid #3d4a5a;
        color: #ffffff;
    }
    
    .styled-table tbody tr:hover {
        background-color: #3d4a5a;
    }
    
    /* User card - Green style */
    .user-card {
        background: linear-gradient(135deg, #00b894 0%, #00a884 100%);
        border-radius: 12px;
        padding: 18px;
        color: white;
        margin: 15px 0;
    }
    
    /* Quick select buttons */
    .quick-btn {
        background: white;
        color: #2d3436;
        border: 2px solid #e0e0e0;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 500;
        margin-right: 8px;
    }
    
    .quick-btn-active {
        background: #0984e3;
        color: white;
        border-color: #0984e3;
    }
    
    /* Date filter section */
    .filter-section {
        background: #2d3a4a;
        border-radius: 10px;
        padding: 15px 20px;
        margin-bottom: 20px;
    }
    
    /* Section headers */
    .section-title {
        color: #1a2744;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 20px 0 15px 0;
    }
    
    /* Low stock alert title - red */
    .section-title-alert {
        color: #e74c3c;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 20px 0 15px 0;
    }
    
    /* Input fields - all white backgrounds */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        background: white !important;
        color: #2d3436 !important;
    }
    
    .stSelectbox > div > div {
        border-radius: 8px;
        background: white !important;
    }
    
    /* Selectbox dropdown - white background */
    .main [data-baseweb="select"] > div {
        background: white !important;
        border-radius: 8px;
    }
    
    .main [data-baseweb="select"] > div > div {
        background: white !important;
    }
    
    /* Input labels in main content - dark for light background */
    .main .stTextInput label, .main .stNumberInput label, .main .stSelectbox label {
        color: #1a2744 !important;
    }
    
    /* Force ALL labels in main area to be dark */
    .main label {
        color: #1a2744 !important;
    }
    
    .main .stSelectbox label p {
        color: #1a2744 !important;
    }
    
    .main [data-testid="stWidgetLabel"] {
        color: #1a2744 !important;
    }
    
    .main [data-testid="stWidgetLabel"] p {
        color: #1a2744 !important;
    }
    
    /* Labels inside tabs */
    .stTabs [data-baseweb="tab-panel"] label {
        color: #1a2744 !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] [data-testid="stWidgetLabel"] p {
        color: #1a2744 !important;
    }
    
    /* Selectbox text - WHITE for dark bg - MOBILE COMPATIBLE */
    .main [data-baseweb="select"] span,
    .main [data-baseweb="select"] div[class*="valueContainer"] span,
    .main [data-baseweb="select"] [data-testid] span,
    [data-baseweb="select"] span[class*="single"],
    .stSelectbox span {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    /* All selectbox values bold and visible */
    [data-baseweb="select"] span {
        font-weight: 700 !important;
        -webkit-text-fill-color: inherit !important;
    }
    
    /* MAIN AREA selectboxes - dark bg matching sidebar style - MOBILE COMPATIBLE */
    .main [data-baseweb="select"] > div,
    .main [data-baseweb="select"] [class*="control"],
    .main .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox > div > div[data-baseweb="select"] > div {
        background: #2d3a4a !important;
        background-color: #2d3a4a !important;
        border: 2px solid #f39c12 !important;
        -webkit-appearance: none !important;
    }
    
    .main [data-baseweb="select"] > div > div,
    .main [data-baseweb="select"] [class*="valueContainer"],
    .stSelectbox [data-baseweb="select"] > div > div {
        background: #2d3a4a !important;
        background-color: #2d3a4a !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    
    /* Selectbox value container in main - dark bg with orange border - MOBILE */
    .main .stSelectbox > div > div,
    .stSelectbox > div > div {
        background: #2d3a4a !important;
        background-color: #2d3a4a !important;
        border: 2px solid #f39c12 !important;
        border-radius: 8px !important;
    }
    
    .main .stSelectbox [data-baseweb="select"] > div {
        background: #2d3a4a !important;
        background-color: #2d3a4a !important;
    }
    
    /* Mobile-specific overrides for iOS/Android */
    @media screen and (max-width: 768px) {
        .main [data-baseweb="select"] span,
        .stSelectbox span,
        [data-baseweb="select"] span {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-weight: 700 !important;
        }
        
        .main [data-baseweb="select"] > div,
        .stSelectbox > div > div,
        [data-baseweb="select"] > div {
            background: #2d3a4a !important;
            background-color: #2d3a4a !important;
            border: 2px solid #f39c12 !important;
        }
        
        /* Force input styling on mobile */
        .stSelectbox input,
        [data-baseweb="select"] input {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            background: transparent !important;
        }
    }
    
    /* SIDEBAR selectboxes - dark bg with WHITE text */
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: #2d3a4a !important;
        border: 2px solid #f39c12 !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #2d3a4a !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] > div > div {
        background: #2d3a4a !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] span {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    /* Dropdown menu - white background with dark text */
    [data-baseweb="popover"] {
        background: white !important;
    }
    
    [data-baseweb="popover"] ul {
        background: white !important;
    }
    
    [data-baseweb="popover"] li {
        background: white !important;
        color: #1a2744 !important;
    }
    
    [data-baseweb="popover"] li:hover {
        background: #f0f2f5 !important;
        color: #1a2744 !important;
    }
    
    /* Selected item in dropdown - highlighted */
    [data-baseweb="popover"] li[aria-selected="true"] {
        background: #0984e3 !important;
        color: white !important;
    }
    
    /* Dropdown option text */
    [data-baseweb="menu"] [role="option"] {
        background: white !important;
        color: #1a2744 !important;
    }
    
    [data-baseweb="menu"] [role="option"]:hover {
        background: #e8f4fd !important;
    }
    
    [data-baseweb="menu"] [role="option"][aria-selected="true"] {
        background: #0984e3 !important;
        color: white !important;
    }
    
    /* Number input styling - DARK background matching selectbox - ALL AREAS */
    .stNumberInput > div > div > input,
    .main .stNumberInput > div > div > input,
    [data-testid="stSidebar"] .stNumberInput > div > div > input,
    .stNumberInput input[type="number"] {
        background: #2d3a4a !important;
        background-color: #2d3a4a !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 2px solid #f39c12 !important;
        border-radius: 8px;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    
    /* Number input container - dark background - ALL AREAS */
    .stNumberInput > div > div,
    .main .stNumberInput > div > div,
    [data-testid="stSidebar"] .stNumberInput > div > div {
        background: #2d3a4a !important;
        background-color: #2d3a4a !important;
        border: 2px solid #f39c12 !important;
        border-radius: 8px !important;
    }
    
    /* Number input +/- buttons - ALL AREAS */
    .stNumberInput button,
    [data-testid="stSidebar"] .stNumberInput button {
        background: #2d3a4a !important;
        color: #ffffff !important;
        border-color: #f39c12 !important;
    }
    
    /* Sidebar number input label */
    [data-testid="stSidebar"] .stNumberInput label {
        color: #ffffff !important;
    }
    
    /* Mobile number input */
    @media screen and (max-width: 768px) {
        .stNumberInput input,
        .stNumberInput > div > div > input,
        [data-testid="stSidebar"] .stNumberInput input {
            background: #2d3a4a !important;
            background-color: #2d3a4a !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            border: 2px solid #f39c12 !important;
        }
    }
    
    /* All input containers white */
    [data-baseweb="input"] {
        background: white !important;
    }
    
    [data-baseweb="input"] > div {
        background: white !important;
    }
    
    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        background: #2d3a4a;
        border-radius: 8px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 15px;
        color: #888;
        font-size: 0.85rem;
    }
    
    /* Status badges */
    .status-ok {
        background: #00b894;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-low {
        background: #e74c3c;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Last updated text */
    .last-updated {
        color: #888;
        font-size: 0.85rem;
    }
    
    /* Hide Streamlit Deploy button */
    .stDeployButton {
        display: none !important;
    }
    
    /* Hide main hamburger menu - but keep settings */
    #MainMenu {
        display: none !important;
    }
    
    /* Style header - show sidebar toggle */
    header[data-testid="stHeader"] {
        background: #f0f2f5 !important;
        height: 40px !important;
    }
    
    /* Sidebar toggle button - RED for visibility */
    [data-testid="stSidebarCollapsedControl"] {
        background: #e74c3c !important;
        color: white !important;
        border-radius: 4px !important;
    }
    
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: white !important;
        stroke: white !important;
    }
    
    [data-testid="stSidebarCollapsedControl"]:hover {
        background: #c0392b !important;
    }
    
    /* Sidebar expand button on dark sidebar */
    [data-testid="stSidebarNavCollapseIcon"] {
        background: #e74c3c !important;
        border-radius: 4px !important;
    }
    
    [data-testid="stSidebarNavCollapseIcon"] svg {
        fill: white !important;
        stroke: white !important;
    }
    
    /* Collapse button in sidebar */
    button[kind="header"] {
        background: #e74c3c !important;
        color: white !important;
    }
    
    button[kind="header"] svg {
        fill: white !important;
    }
    
    /* Reduce top padding */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 1200px;
    }
    
    /* Compact metric cards */
    .metric-card {
        padding: 15px 20px;
        margin-bottom: 10px;
    }
    
    .metric-value {
        font-size: 2.2rem;
    }
    
    .metric-label {
        font-size: 0.75rem;
    }
    
    /* Compact content cards */
    .content-card {
        padding: 18px;
        margin-bottom: 12px;
    }
    
    /* Reduce spacing between elements */
    .stTabs {
        margin-top: 0.5rem !important;
    }
    
    /* Compact sidebar */
    [data-testid="stSidebar"] {
        padding-top: 1rem;
    }
    
    /* Smaller headers */
    .main-header {
        font-size: 2rem;
        margin-bottom: 0.2rem;
    }
    
    .sub-header {
        margin-bottom: 0.8rem;
    }
    
    /* Compact section title */
    .section-title {
        margin: 12px 0 10px 0;
    }
    
    /* Remove extra spacing from dataframes */
    [data-testid="stDataFrame"] {
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
db.init_database()
db.insert_sample_data()

# Session state
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None
if 'success_msg' not in st.session_state:
    st.session_state.success_msg = None
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Show success message as toast notification
if st.session_state.success_msg:
    st.toast(st.session_state.success_msg, icon="✅")
    st.session_state.success_msg = None

# Theme toggle at top of page
theme_col1, theme_col2 = st.columns([8, 1])
with theme_col2:
    theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
    if st.button(theme_icon, key="theme_toggle", help="Toggle Dark/Light Mode"):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
        st.rerun()

# Apply dark theme CSS if enabled
if st.session_state.theme == 'dark':
    st.markdown("""
    <style>
        .stApp { background: #1a1a2e !important; }
        .main .block-container { background: #1a1a2e !important; }
        .main-header { color: #ffffff !important; }
        .sub-header { color: #00b894 !important; }
        .content-card { background: #16213e !important; }
        .card-header { color: #ffffff !important; }
        h4, h3, h2, h1 { color: #ffffff !important; }
        .section-title { color: #ffffff !important; }
        .section-title-alert { color: #ff6b6b !important; }
        .last-updated { color: #aaa !important; }
        header[data-testid="stHeader"] { background: #1a1a2e !important; }
        
        /* ALL form labels WHITE in dark mode */
        .main label { color: #ffffff !important; }
        .main [data-testid="stWidgetLabel"] { color: #ffffff !important; }
        .main [data-testid="stWidgetLabel"] p { color: #ffffff !important; }
        .main [data-testid="stWidgetLabel"] span { color: #ffffff !important; }
        .main .stSelectbox label { color: #ffffff !important; }
        .main .stSelectbox label p { color: #ffffff !important; }
        .main .stTextInput label { color: #ffffff !important; }
        .main .stTextInput label p { color: #ffffff !important; }
        .main .stNumberInput label { color: #ffffff !important; }
        .main .stNumberInput label p { color: #ffffff !important; }
        .stTabs [data-baseweb="tab-panel"] label { color: #ffffff !important; }
        .stTabs [data-baseweb="tab-panel"] [data-testid="stWidgetLabel"] p { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)


def create_metric_card(label, value, color_class="metric-value-dark", sub_text=""):
    """Create a white metric card with colored value"""
    sub_html = f'<div class="metric-sub">{sub_text}</div>' if sub_text else ''
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {color_class}">{value}</div>
        {sub_html}
    </div>
    """


def login_section():
    """User login section with password for admins"""
    users = db.get_all_users()
    
    if st.session_state.logged_in_user:
        current_user = db.get_user_by_id(st.session_state.logged_in_user)
        is_admin = current_user['username'] in ADMIN_USERS
        badge_color = "#f39c12" if is_admin else "#00b894"
        role_text = "Admin" if is_admin else "User"
        st.sidebar.markdown(f"""
        <div style="background: linear-gradient(135deg, {badge_color} 0%, {badge_color}cc 100%); border-radius: 10px; padding: 12px; color: white; margin-bottom: 10px;">
            <div style="font-weight: 700;">👤 {current_user['full_name']}</div>
            <div style="font-size: 0.85rem; opacity: 0.9;">@{current_user['username']} | {role_text}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in_user = None
            st.rerun()
        
        # Admin panel
        if is_admin:
            with st.sidebar.expander("🔧 Admin Panel"):
                admin_action = st.radio("Action", ["Add User", "Edit User", "Remove User", "Set Password", "Edit Stock"], label_visibility="collapsed")
                
                if admin_action == "Add User":
                    st.markdown("**➕ Add New User**")
                    new_username = st.text_input("Username", key="new_user")
                    new_fullname = st.text_input("Full Name", key="new_name")
                    if st.button("Add User", use_container_width=True):
                        if new_username and new_fullname:
                            try:
                                db.add_user(new_username, new_fullname, 'IT')
                                st.success("✅ User added!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                
                elif admin_action == "Edit User":
                    st.markdown("**✏️ Edit User Details**")
                    user_list = [u for u in users if u['username'] not in ADMIN_USERS]
                    if user_list:
                        sel_user = st.selectbox("Select User", [f"{u['full_name']} (@{u['username']})" for u in user_list], key="edit_user_sel")
                        user_idx = [f"{u['full_name']} (@{u['username']})" for u in user_list].index(sel_user)
                        selected_user = user_list[user_idx]
                        
                        edit_fullname = st.text_input("Full Name", value=selected_user['full_name'], key="edit_fullname")
                        edit_username = st.text_input("Username", value=selected_user['username'], key="edit_username")
                        
                        if st.button("Update User", use_container_width=True):
                            if edit_fullname and edit_username:
                                try:
                                    db.update_user_details(selected_user['id'], edit_fullname, edit_username, selected_user['department'])
                                    st.success(f"✅ User updated successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                            else:
                                st.error("Full Name and Username are required!")
                    else:
                        st.info("No regular users to edit")
                
                elif admin_action == "Remove User":
                    st.markdown("**🗑️ Remove User**")
                    user_list = [u for u in users if u['username'] not in ADMIN_USERS]
                    if user_list:
                        sel_user = st.selectbox("Select User", [f"{u['full_name']} (@{u['username']})" for u in user_list], key="remove_user_sel")
                        user_idx = [f"{u['full_name']} (@{u['username']})" for u in user_list].index(sel_user)
                        selected_user = user_list[user_idx]
                        
                        st.warning(f"⚠️ This will permanently delete the user: **{selected_user['full_name']}**")
                        
                        confirm_delete = st.checkbox("I confirm I want to delete this user", key="confirm_delete")
                        
                        if st.button("🗑️ Delete User", use_container_width=True, type="primary"):
                            if confirm_delete:
                                try:
                                    db.delete_user(selected_user['id'])
                                    st.success(f"✅ User '{selected_user['full_name']}' deleted successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                            else:
                                st.error("Please confirm the deletion by checking the checkbox!")
                    else:
                        st.info("No regular users to remove")
                
                elif admin_action == "Set Password":
                    st.markdown("**🔑 Set User Password**")
                    # Allow password change for ALL users including admins
                    sel_user = st.selectbox("Select User", [f"{u['full_name']} (@{u['username']})" for u in users], key="pwd_user")
                    new_pwd = st.text_input("New Password", type="password", key="new_pwd")
                    if st.button("Set Password", use_container_width=True):
                        if new_pwd:
                            user_idx = [f"{u['full_name']} (@{u['username']})" for u in users].index(sel_user)
                            db.update_user_password(users[user_idx]['id'], new_pwd)
                            st.success(f"✅ Password set for {sel_user}")
                        else:
                            st.error("Please enter a password!")
                
                elif admin_action == "Edit Stock":
                    st.markdown("**📦 Edit Inventory**")
                    item_type = st.radio("Type", ["Consumable", "Toner"], key="edit_type", horizontal=True)
                    if item_type == "Consumable":
                        consumables = db.get_all_consumables()
                        sel_item = st.selectbox("Item", [c['item_name'] for c in consumables], key="edit_cons")
                        sel_loc = st.selectbox("Location", ["P1 IT Cage", "HRV Backside", "RF Cage"], key="edit_cons_loc")
                        item = next((c for c in consumables if c['item_name'] == sel_item), None)
                        if item:
                            loc_map = {"P1 IT Cage": item['p1_it_cage'], "HRV Backside": item['hrv_backside'], "RF Cage": item['rf_cage']}
                            new_qty = st.number_input(f"New Qty (Current: {loc_map[sel_loc]})", min_value=0, value=loc_map[sel_loc], key="edit_cons_qty")
                            if st.button("Update Stock", use_container_width=True, key="upd_cons"):
                                db.set_consumable_stock(item['id'], sel_loc, new_qty)
                                st.success(f"✅ Updated {sel_item} at {sel_loc} to {new_qty}")
                                st.rerun()
                    else:
                        toners = db.get_all_toners()
                        sel_item = st.selectbox("Toner", [f"{t['toner_model']} - {t['printer_model']}" for t in toners], key="edit_ton")
                        sel_loc = st.selectbox("Location", ["P1 IT Cage", "HRV Backside", "RF Cage"], key="edit_ton_loc")
                        toner_model = sel_item.split(" - ")[0]
                        item = next((t for t in toners if t['toner_model'] == toner_model), None)
                        if item:
                            loc_map = {"P1 IT Cage": item['p1_it_cage'], "HRV Backside": item['hrv_backside'], "RF Cage": item['rf_cage']}
                            new_qty = st.number_input(f"New Qty (Current: {loc_map[sel_loc]})", min_value=0, value=loc_map[sel_loc], key="edit_ton_qty")
                            if st.button("Update Stock", use_container_width=True, key="upd_ton"):
                                db.set_toner_stock(item['id'], sel_loc, new_qty)
                                st.success(f"✅ Updated {toner_model} at {sel_loc} to {new_qty}")
                                st.rerun()
    else:
        st.sidebar.markdown("### 👤 Login")
        
        # Separate admin and regular users
        admin_users_list = [u for u in users if u['username'] in ADMIN_USERS]
        regular_users_list = [u for u in users if u['username'] not in ADMIN_USERS]
        
        login_type = st.sidebar.radio("Login As", ["Admin", "User"], horizontal=True, label_visibility="collapsed")
        
        if login_type == "Admin":
            st.sidebar.markdown("**🔐 Admin Login**")
            admin_select = st.sidebar.selectbox("Admin User", [f"{u['full_name']} (@{u['username']})" for u in admin_users_list], label_visibility="collapsed")
            admin_pwd = st.sidebar.text_input("Password", type="password", key="admin_pwd")
            if st.sidebar.button("🔐 Login", type="primary", use_container_width=True):
                admin_idx = [f"{u['full_name']} (@{u['username']})" for u in admin_users_list].index(admin_select)
                user = admin_users_list[admin_idx]
                if user['password'] == admin_pwd:
                    st.session_state.logged_in_user = user['id']
                    st.rerun()
                else:
                    st.sidebar.error("❌ Invalid password!")
        else:
            st.sidebar.markdown("**👤 User Login**")
            if regular_users_list:
                user_select = st.sidebar.selectbox("Select User", [f"{u['full_name']} (@{u['username']})" for u in regular_users_list], label_visibility="collapsed")
                user_idx = [f"{u['full_name']} (@{u['username']})" for u in regular_users_list].index(user_select)
                user = regular_users_list[user_idx]
                
                # Check if user has password set
                if user['password']:
                    user_pwd = st.sidebar.text_input("Password", type="password", key="user_pwd")
                    if st.sidebar.button("🔐 Login", type="primary", use_container_width=True):
                        if user['password'] == user_pwd:
                            st.session_state.logged_in_user = user['id']
                            st.rerun()
                        else:
                            st.sidebar.error("❌ Invalid password!")
                else:
                    if st.sidebar.button("🔐 Login", type="primary", use_container_width=True):
                        st.session_state.logged_in_user = user['id']
                        st.rerun()
            else:
                st.sidebar.info("No regular users available")


def consumables_dashboard():
    """Consumables Dashboard"""
    # Header with live badge
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown('<div class="main-header">🏭 Consumables Inventory</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">IT Equipment & Accessories</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="text-align: right;">
            <span class="live-badge"><span class="live-dot"></span> LIVE</span>
            <div class="last-updated">Last Updated: {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    stats = db.get_consumable_stats()
    consumables = db.get_all_consumables()
    low_stock = db.get_low_stock_consumables()
    
    # Metric cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_card("TOTAL ITEMS", stats['total_items'], "metric-value-blue"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("TOTAL STOCK", stats['total_stock'], "metric-value-dark"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("LOW STOCK ALERTS", stats['low_stock_count'], "metric-value-red"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("CATEGORIES", stats['categories'], "metric-value-purple"), unsafe_allow_html=True)
    
    # Low stock alerts - only show if there are items
    if low_stock and len(low_stock) > 0:
        st.markdown('<div class="section-title-alert">⚠️ Low Stock Alerts</div>', unsafe_allow_html=True)
        for item in low_stock:
            st.markdown(f"""
            <div class="low-stock-alert">
                <strong>🔴 {item['item_name']}</strong> — Total Stock: <strong>{item['total_stock']}</strong> 
                (Min: {item['min_stock_level']}) | P1: {item['p1_it_cage']} | HRV: {item['hrv_backside']} | RF: {item['rf_cage']}
            </div>
            """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Inventory", "🔄 Pick/Stow", "📜 History"])
    
    with tab1:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📦 Current Inventory</div>', unsafe_allow_html=True)
        df = pd.DataFrame(consumables)
        if not df.empty:
            df['S.No'] = range(1, len(df) + 1)
            df_display = df[['S.No', 'item_name', 'category', 'p1_it_cage', 'hrv_backside', 'rf_cage', 'total_stock']].copy()
            df_display.columns = ['S.No', 'Item Name', 'Category', 'P1 IT Cage', 'HRV Backside', 'RF Cage', 'Total']
            
            # Export to Excel button
            df_export = df[['item_name', 'category', 'p1_it_cage', 'hrv_backside', 'rf_cage', 'total_stock']].copy()
            df_export.columns = ['Item Name', 'Category', 'P1 IT Cage', 'HRV Backside', 'RF Cage', 'Total']
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Consumables Inventory')
            excel_data = output.getvalue()
            st.download_button(
                label="📥 Export to Excel",
                data=excel_data,
                file_name=f"Consumables_Inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="export_consumables"
            )
            
            for col in ['P1 IT Cage', 'HRV Backside', 'RF Cage']:
                df_display[col] = df_display[col].apply(lambda x: '-' if x == 0 else x)
            html_table = df_display.to_html(index=False, classes='styled-table')
            st.markdown(html_table, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            category_stock = df.groupby('category')['total_stock'].sum().reset_index()
            fig = px.pie(category_stock, values='total_stock', names='category', 
                        title='Stock Distribution by Category',
                        color_discrete_sequence=['#0984e3', '#00b894', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            loc_data = pd.DataFrame({'Location': ['P1 IT Cage', 'HRV Backside', 'RF Cage'], 
                                     'Stock': [stats['p1_it_cage'], stats['hrv_backside'], stats['rf_cage']]})
            fig = px.pie(loc_data, values='Stock', names='Location', title='Stock by Location',
                        color_discrete_sequence=['#0984e3', '#f39c12', '#00b894'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        if not st.session_state.logged_in_user:
            st.warning("⚠️ Please login to perform pick/stow operations")
        else:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">🔄 Pick / Stow Operations</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 📤 Pick Item")
                pick_item = st.selectbox("Select Item", [c['item_name'] for c in consumables], key="pick_c")
                pick_loc = st.selectbox("Location", ["P1 IT Cage", "HRV Backside", "RF Cage"], key="pick_loc_c")
                pick_qty = st.number_input("Quantity", min_value=1, value=1, key="pick_qty_c")
                pick_notes = st.text_input("Notes (optional)", key="pick_notes_c")
                if st.button("📤 Pick Item", key="pick_btn_c", use_container_width=True):
                    item = next((c for c in consumables if c['item_name'] == pick_item), None)
                    if item:
                        loc_stock = {"P1 IT Cage": item['p1_it_cage'], "HRV Backside": item['hrv_backside'], "RF Cage": item['rf_cage']}
                        if loc_stock[pick_loc] >= pick_qty:
                            db.update_consumable_stock(item['id'], pick_loc, -pick_qty)
                            db.log_activity(st.session_state.logged_in_user, "Consumable", item['id'], f"{item['item_name']} ({pick_loc})", "Pick", pick_qty, pick_notes)
                            st.session_state.success_msg = f"✅ Successfully Picked {pick_qty} x {pick_item} from {pick_loc}"
                            st.rerun()
                        else:
                            st.error(f"❌ Insufficient stock at {pick_loc}!")
            
            with col2:
                st.markdown("#### 📥 Stow Item")
                stow_item = st.selectbox("Select Item", [c['item_name'] for c in consumables], key="stow_c")
                stow_loc = st.selectbox("Location", ["P1 IT Cage", "HRV Backside", "RF Cage"], key="stow_loc_c")
                stow_qty = st.number_input("Quantity", min_value=1, value=1, key="stow_qty_c")
                stow_notes = st.text_input("Notes (optional)", key="stow_notes_c")
                if st.button("📥 Stow Item", key="stow_btn_c", use_container_width=True):
                    item = next((c for c in consumables if c['item_name'] == stow_item), None)
                    if item:
                        db.update_consumable_stock(item['id'], stow_loc, stow_qty)
                        db.log_activity(st.session_state.logged_in_user, "Consumable", item['id'], f"{item['item_name']} ({stow_loc})", "Stow", stow_qty, stow_notes)
                        st.session_state.success_msg = f"✅ Successfully Stowed {stow_qty} x {stow_item} to {stow_loc}"
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📜 All Consumable Activity History</div>', unsafe_allow_html=True)
        activities = db.get_recent_activities(100)
        consumable_activities = [a for a in activities if a['item_type'] == 'Consumable']
        if consumable_activities:
            df_act = pd.DataFrame(consumable_activities)
            df_act['timestamp'] = pd.to_datetime(df_act['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(df_act[['timestamp', 'user_name', 'item_name', 'action_type', 'quantity', 'notes']], use_container_width=True, hide_index=True)
        else:
            st.info("No consumable activity history yet. Activities will appear here after pick/stow operations.")
        st.markdown('</div>', unsafe_allow_html=True)


def toner_dashboard():
    """Toner Dashboard"""
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown('<div class="main-header">🖨️ Toner Inventory</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Printer Toners & Cartridges</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="text-align: right;">
            <span class="live-badge"><span class="live-dot"></span> LIVE</span>
            <div class="last-updated">Last Updated: {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    stats = db.get_toner_stats()
    toners = db.get_all_toners()
    low_stock = db.get_low_stock_toners()
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(create_metric_card("TOTAL TONER TYPES", stats['total_items'], "metric-value-blue"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("TOTAL STOCK", stats['total_stock'], "metric-value-dark"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("LOW STOCK", stats['low_stock_count'], "metric-value-red"), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(create_metric_card("P1 IT CAGE", stats['p1_it_cage'], "metric-value-purple"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("HRV BACKSIDE", stats['hrv_backside'], "metric-value-orange"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("RF CAGE", stats['rf_cage'], "metric-value-green"), unsafe_allow_html=True)
    
    # Low stock alerts - only show if there are items
    if low_stock and len(low_stock) > 0:
        st.markdown('<div class="section-title-alert">⚠️ Low Stock Alerts</div>', unsafe_allow_html=True)
        for item in low_stock:
            st.markdown(f"""
            <div class="low-stock-alert">
                <strong>🔴 {item['toner_model']}</strong> ({item['color']}) — 
                🖨️ {item['printer_model']} | Stock: <strong>{item['total_stock']}</strong> (Min: {item['min_stock_level']})
            </div>
            """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Inventory", "🔄 Pick/Stow", "📜 History"])
    
    with tab1:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🖨️ Current Toner Inventory</div>', unsafe_allow_html=True)
        df = pd.DataFrame(toners)
        if not df.empty:
            df['S.No'] = range(1, len(df) + 1)
            df_display = df[['S.No', 'printer_model', 'printer_count', 'toner_model', 'p1_it_cage', 'hrv_backside', 'rf_cage', 'total_stock']].copy()
            df_display.columns = ['S.No', 'Printer Name', 'Printer Count', 'Toner', 'P1 IT Cage', 'HRV Backside', 'RF Cage', 'Total']
            
            # Export to Excel button
            df_export = df[['printer_model', 'printer_count', 'toner_model', 'color', 'p1_it_cage', 'hrv_backside', 'rf_cage', 'total_stock']].copy()
            df_export.columns = ['Printer Name', 'Printer Count', 'Toner Model', 'Color', 'P1 IT Cage', 'HRV Backside', 'RF Cage', 'Total']
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Toner Inventory')
            excel_data = output.getvalue()
            st.download_button(
                label="📥 Export to Excel",
                data=excel_data,
                file_name=f"Toner_Inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="export_toners"
            )
            
            for col in ['P1 IT Cage', 'HRV Backside', 'RF Cage']:
                df_display[col] = df_display[col].apply(lambda x: '-' if x == 0 else x)
            html_table = df_display.to_html(index=False, classes='styled-table')
            st.markdown(html_table, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            loc_data = pd.DataFrame({'Location': ['P1 IT Cage', 'HRV Backside', 'RF Cage'], 'Stock': [stats['p1_it_cage'], stats['hrv_backside'], stats['rf_cage']]})
            fig = px.pie(loc_data, values='Stock', names='Location', title='Stock by Location',
                        color_discrete_sequence=['#0984e3', '#f39c12', '#00b894'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            color_stock = df.groupby('color')['total_stock'].sum().reset_index()
            fig = px.bar(color_stock, x='color', y='total_stock', title='Stock by Toner Color',
                        color='color', color_discrete_map={'Black': '#2d3436', 'Cyan': '#00bcd4', 'Magenta': '#e91e63', 'Yellow': '#ffc107'})
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        if not st.session_state.logged_in_user:
            st.warning("⚠️ Please login to perform pick/stow operations")
        else:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">🔄 Pick / Stow Operations</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 📤 Pick Toner")
                pick_item = st.selectbox("Toner", [f"{t['toner_model']} - {t['printer_model']}" for t in toners], key="pick_t")
                pick_loc = st.selectbox("Location", ["P1 IT Cage", "HRV Backside", "RF Cage"], key="pick_loc_t")
                pick_qty = st.number_input("Quantity", min_value=1, value=1, key="pick_qty_t")
                pick_notes = st.text_input("Notes (optional)", key="pick_notes_t")
                if st.button("📤 Pick Toner", key="pick_btn_t", use_container_width=True):
                    toner_model = pick_item.split(" - ")[0]
                    item = next((t for t in toners if t['toner_model'] == toner_model), None)
                    if item:
                        loc_stock = {"P1 IT Cage": item['p1_it_cage'], "HRV Backside": item['hrv_backside'], "RF Cage": item['rf_cage']}
                        if loc_stock[pick_loc] >= pick_qty:
                            db.update_toner_stock(item['id'], pick_loc, -pick_qty)
                            db.log_activity(st.session_state.logged_in_user, "Toner", item['id'], f"{item['toner_model']} ({pick_loc})", "Pick", pick_qty, pick_notes)
                            st.session_state.success_msg = f"✅ Successfully Picked {pick_qty} x {item['toner_model']} from {pick_loc}"
                            st.rerun()
                        else:
                            st.error(f"❌ Insufficient stock at {pick_loc}!")
            with col2:
                st.markdown("#### 📥 Stow Toner")
                stow_item = st.selectbox("Toner", [f"{t['toner_model']} - {t['printer_model']}" for t in toners], key="stow_t")
                stow_loc = st.selectbox("Location", ["P1 IT Cage", "HRV Backside", "RF Cage"], key="stow_loc_t")
                stow_qty = st.number_input("Quantity", min_value=1, value=1, key="stow_qty_t")
                stow_notes = st.text_input("Notes (optional)", key="stow_notes_t")
                if st.button("📥 Stow Toner", key="stow_btn_t", use_container_width=True):
                    toner_model = stow_item.split(" - ")[0]
                    item = next((t for t in toners if t['toner_model'] == toner_model), None)
                    if item:
                        db.update_toner_stock(item['id'], stow_loc, stow_qty)
                        db.log_activity(st.session_state.logged_in_user, "Toner", item['id'], f"{item['toner_model']} ({stow_loc})", "Stow", stow_qty, stow_notes)
                        st.session_state.success_msg = f"✅ Successfully Stowed {stow_qty} x {item['toner_model']} to {stow_loc}"
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📜 All Toner Activity History</div>', unsafe_allow_html=True)
        activities = db.get_recent_activities(100)
        toner_activities = [a for a in activities if a['item_type'] == 'Toner']
        if toner_activities:
            df_act = pd.DataFrame(toner_activities)
            df_act['timestamp'] = pd.to_datetime(df_act['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(df_act[['timestamp', 'user_name', 'item_name', 'action_type', 'quantity', 'notes']], use_container_width=True, hide_index=True)
        else:
            st.info("No toner activity history yet. Activities will appear here after pick/stow operations.")
        st.markdown('</div>', unsafe_allow_html=True)


def activity_dashboard():
    """Activity Dashboard"""
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown('<div class="main-header">📋 Activity Log</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">User Activity & Transaction History</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="text-align: right;">
            <span class="live-badge"><span class="live-dot"></span> LIVE</span>
            <div class="last-updated">Last Updated: {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    activities = db.get_recent_activities(100)
    users = db.get_all_users()
    
    total = len(activities)
    picks = sum(1 for a in activities if a['action_type'] == 'Pick')
    stows = sum(1 for a in activities if a['action_type'] == 'Stow')
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_card("TOTAL ACTIVITIES", total, "metric-value-blue"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("TOTAL PICKS", picks, "metric-value-red"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("TOTAL STOWS", stows, "metric-value-green"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("ACTIVE USERS", len(users), "metric-value-purple"), unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📜 Recent Activity", "👥 User Summary"])
    
    with tab1:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📜 Recent Activity Log</div>', unsafe_allow_html=True)
        
        filter_type = st.selectbox("Filter by Type", ["All", "Consumable", "Toner"])
        
        filtered = activities.copy()
        if filter_type != "All":
            filtered = [a for a in filtered if a['item_type'] == filter_type]
        
        if filtered:
            df_act = pd.DataFrame(filtered)
            df_act['timestamp'] = pd.to_datetime(df_act['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            df_display = df_act[['timestamp', 'user_name', 'item_type', 'item_name', 'action_type', 'quantity']]
            df_display.columns = ['Time', 'User', 'Type', 'Item', 'Action', 'Qty']
            
            # Export to Excel button
            df_export = df_display.copy()
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Activity Log')
            excel_data = output.getvalue()
            st.download_button(
                label="📥 Export to Excel",
                data=excel_data,
                file_name=f"Activity_Log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="export_activity"
            )
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("No activities match filters")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">👥 User Activity Summary</div>', unsafe_allow_html=True)
        user_summary = db.get_user_activity_summary()
        if user_summary:
            df_sum = pd.DataFrame(user_summary)
            df_sum = df_sum[['full_name', 'department', 'total_activities', 'total_picks', 'total_stows']]
            df_sum.columns = ['User', 'Dept', 'Total', 'Picks', 'Stows']
            st.dataframe(df_sum, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)


def main():
    """Main application"""
    login_section()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📑 Navigation")
    page = st.sidebar.radio("Dashboard", ["📦 Consumables", "🖨️ Toners", "📋 Activity Log"], label_visibility="collapsed")
    
    if page == "📦 Consumables":
        consumables_dashboard()
    elif page == "🖨️ Toners":
        toner_dashboard()
    else:
        activity_dashboard()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown('<div class="footer">IT Inventory Dashboard v2.0</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
