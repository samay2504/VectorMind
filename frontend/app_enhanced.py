"""
VectorMind - Enhanced Streamlit Application

Copyright © 2025 Samay Mehar. All Rights Reserved.
PROPRIETARY SOFTWARE - PATENT PENDING

Production-ready Streamlit frontend with dark theme and enhanced features
"""

import streamlit as st
import os
from streamlit_components import (
    display_system_stats,
    display_upload_section,
    display_query_interface,
    display_results_panel
)

# Configuration
API_URL = os.getenv("PUBLIC_API_URL", "http://localhost:8000")

# Page configuration with dark theme
st.set_page_config(
    page_title="VectorMind | Multimodal RAG System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/samay2504/VectorMind',
        'Report a bug': "https://github.com/samay2504/VectorMind/issues",
        'About': "VectorMind © 2025 Samay Mehar. All Rights Reserved."
    }
)

# Custom CSS for dark, cyber-themed interface
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Inter:wght@400;600;700&display=swap');
    
    /* Global dark theme */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1a1f35 50%, #0f172a 100%);
        background-size: 200% 200%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Main title */
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #06b6d4 0%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 1rem 0;
        letter-spacing: 2px;
        animation: pulse 3s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Subtitle */
    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 1px;
    }
    
    /* Card styling */
    .stContainer {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(51, 65, 85, 0.5);
        border-radius: 12px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #e2e8f0;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(6, 182, 212, 0.3);
    }
    
    /* Primary button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        box-shadow: 0 5px 15px rgba(16, 185, 129, 0.3);
    }
    
    /* Metric styling */
    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.5);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(6, 182, 212, 0.2);
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8;
        font-size: 0.875rem;
    }
    
    [data-testid="stMetricValue"] {
        color: #06b6d4;
        font-weight: 700;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #10b981 0%, #06b6d4 100%);
    }
    
    /* Text input and textarea */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(51, 65, 85, 0.5);
        color: #e2e8f0;
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #06b6d4;
        box-shadow: 0 0 0 1px #06b6d4;
    }
    
    /* Divider */
    hr {
        border-color: rgba(51, 65, 85, 0.3);
        margin: 2rem 0;
    }
    
    /* Success/error boxes */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        color: #6ee7b7;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        color: #fca5a5;
    }
    
    .stWarning {
        background: rgba(251, 191, 36, 0.1);
        border-left: 4px solid #fbbf24;
        color: #fde68a;
    }
    
    .stInfo {
        background: rgba(6, 182, 212, 0.1);
        border-left: 4px solid #06b6d4;
        color: #67e8f9;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(30, 41, 59, 0.5);
        border: 2px dashed rgba(6, 182, 212, 0.3);
        border-radius: 12px;
        padding: 2rem;
    }
    
    /* Badge styling */
    .stBadge {
        background: rgba(6, 182, 212, 0.2);
        color: #06b6d4;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    /* Container borders */
    [data-testid="stVerticalBlock"] > div:has([data-testid="stContainer"]) {
        border: 1px solid rgba(51, 65, 85, 0.3);
        border-radius: 12px;
        background: rgba(30, 41, 59, 0.3);
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-title">
    🧠 VectorMind
</div>
<div class="subtitle">
    Multimodal RAG System | Powered by AI
</div>
""", unsafe_allow_html=True)

st.divider()

# Initialize session state
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "query_type" not in st.session_state:
    st.session_state.query_type = "Factual"

# Sidebar - Upload and Stats
with st.sidebar:
    st.markdown("## 📋 Navigation")
    
    # Display system stats
    with st.expander("📈 System Status", expanded=True):
        display_system_stats(API_URL)
    
    st.divider()
    
    # Upload section
    with st.expander("📁 Upload Documents", expanded=False):
        display_upload_section(API_URL)
    
    st.divider()
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 1rem; margin-top: 2rem;">
        <p style="color: #64748b; font-size: 0.75rem; margin: 0;">
            Copyright © 2025 Samay Mehar
        </p>
        <p style="color: #475569; font-size: 0.7rem; margin-top: 0.25rem;">
            All Rights Reserved | Patent Pending
        </p>
    </div>
    """, unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([1, 2])

# Left column - Query interface
with col1:
    with st.container(border=False):
        display_query_interface(API_URL)

# Right column - Results
with col2:
    with st.container(border=False):
        display_results_panel()

# Footer with helpful tips
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem;">
    <p style="color: #64748b; font-size: 0.9rem;">
        💡 <strong>Tips:</strong> Upload documents first, then use the query interface to search. 
        Choose query types based on your needs: Factual for direct answers, Exploratory for discovery, or Cross-Modal for image+text search.
    </p>
</div>
""", unsafe_allow_html=True)
