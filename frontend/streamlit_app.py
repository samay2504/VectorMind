"""
Streamlit Frontend for Multimodal RAG System

A production-ready, user-friendly interface for document upload and querying.
Designed for easy deployment on Railway, Vercel, or Render.

═══════════════════════════════════════════════════════════════════════════
Copyright © 2025 Samay Mehar. All Rights Reserved.

PROPRIETARY SOFTWARE - PATENT PENDING

Author: Samay Mehar
Created: October 31 - November 1, 2025
Project: VectorMind (Modality RAG System)

This file is part of a proprietary software system created entirely from
scratch (0 to 100) by Samay Mehar. All rights reserved. No portion of this
code may be reproduced, distributed, or transmitted in any form without
express written permission from the copyright holder.

Unauthorized use is strictly prohibited and may result in legal action.
═══════════════════════════════════════════════════════════════════════════
"""

import streamlit as st
import requests
import os
from typing import Optional, Dict, List
import time
from pathlib import Path
import json

# Configuration
API_URL = os.getenv("PUBLIC_API_URL", "http://localhost:8000")
CONVERSATION_ENABLED = os.getenv("CONVERSATION_MEMORY_ENABLED", "true").lower() == "true"

# Page configuration
st.set_page_config(
    page_title="ModalityRAG | AI-Powered Knowledge System",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Futuristic Custom CSS with animations and gradients
st.markdown("""
<style>
    /* Import futuristic font */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    /* Global styling */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1428 100%);
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* Animated gradient background */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Main header with glow effect */
    .main-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00d4ff 0%, #0099ff 50%, #00ffff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 2rem 0;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
        animation: pulse 3s ease-in-out infinite;
        letter-spacing: 3px;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.9; transform: scale(1.02); }
    }
    
    /* Subtitle */
    .subtitle {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.2rem;
        color: #00d4ff;
        text-align: center;
        margin-top: -1rem;
        margin-bottom: 2rem;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    /* Neon success box */
    .success-box {
        padding: 1.5rem;
        border-radius: 15px;
        background: linear-gradient(135deg, rgba(0, 255, 157, 0.1) 0%, rgba(0, 212, 255, 0.1) 100%);
        border: 2px solid #00ff9d;
        color: #00ff9d;
        margin: 1rem 0;
        box-shadow: 0 0 20px rgba(0, 255, 157, 0.3), inset 0 0 20px rgba(0, 255, 157, 0.1);
        font-size: 1.1rem;
        line-height: 1.6;
        animation: glowPulse 2s ease-in-out infinite;
    }
    
    @keyframes glowPulse {
        0%, 100% { box-shadow: 0 0 20px rgba(0, 255, 157, 0.3), inset 0 0 20px rgba(0, 255, 157, 0.1); }
        50% { box-shadow: 0 0 30px rgba(0, 255, 157, 0.5), inset 0 0 30px rgba(0, 255, 157, 0.2); }
    }
    
    /* Cyber error box */
    .error-box {
        padding: 1.5rem;
        border-radius: 15px;
        background: linear-gradient(135deg, rgba(255, 0, 85, 0.1) 0%, rgba(255, 0, 170, 0.1) 100%);
        border: 2px solid #ff0055;
        color: #ff0055;
        margin: 1rem 0;
        box-shadow: 0 0 20px rgba(255, 0, 85, 0.3);
        font-size: 1.1rem;
    }
    
    /* Futuristic info box */
    .info-box {
        padding: 1.5rem;
        border-radius: 15px;
        background: linear-gradient(135deg, rgba(0, 153, 255, 0.1) 0%, rgba(0, 212, 255, 0.1) 100%);
        border: 2px solid #0099ff;
        color: #00d4ff;
        margin: 1rem 0;
        box-shadow: 0 0 20px rgba(0, 153, 255, 0.3);
        font-size: 1.05rem;
    }
    
    /* Holographic source cards */
    .source-card {
        padding: 1.5rem;
        border-radius: 15px;
        background: linear-gradient(135deg, rgba(15, 20, 40, 0.9) 0%, rgba(26, 31, 58, 0.9) 100%);
        border-left: 4px solid #00d4ff;
        border-right: 1px solid rgba(0, 212, 255, 0.3);
        border-top: 1px solid rgba(0, 212, 255, 0.2);
        border-bottom: 1px solid rgba(0, 212, 255, 0.2);
        margin: 0.5rem 0;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 212, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .source-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7), 0 0 40px rgba(0, 212, 255, 0.4);
        border-left: 4px solid #00ff9d;
    }
    
    /* Metric cards with holographic effect */
    .metric-card {
        padding: 1.5rem;
        border-radius: 15px;
        background: linear-gradient(135deg, rgba(0, 153, 255, 0.05) 0%, rgba(0, 212, 255, 0.05) 100%);
        border: 2px solid rgba(0, 212, 255, 0.3);
        text-align: center;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(0, 212, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #00d4ff;
        box-shadow: 0 5px 20px rgba(0, 212, 255, 0.4), inset 0 0 30px rgba(0, 212, 255, 0.1);
        transform: scale(1.05);
    }
    
    /* Glowing buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0099ff 0%, #00d4ff 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        box-shadow: 0 5px 15px rgba(0, 153, 255, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00d4ff 0%, #00ff9d 100%) !important;
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.6), 0 0 30px rgba(0, 255, 157, 0.4) !important;
        transform: translateY(-3px) !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 14, 39, 0.95) 0%, rgba(15, 20, 40, 0.95) 100%);
        border-right: 2px solid rgba(0, 212, 255, 0.3);
        box-shadow: 5px 0 20px rgba(0, 0, 0, 0.5);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, rgba(0, 153, 255, 0.1) 0%, rgba(0, 212, 255, 0.1) 100%);
        border: 2px solid rgba(0, 212, 255, 0.3);
        border-radius: 10px;
        color: #00d4ff;
        font-family: 'Orbitron', sans-serif;
        font-weight: 600;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, rgba(0, 153, 255, 0.3) 0%, rgba(0, 212, 255, 0.3) 100%);
        border-color: #00d4ff;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0099ff 0%, #00d4ff 100%) !important;
        border-color: #00ff9d !important;
        color: #ffffff !important;
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.6) !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(15, 20, 40, 0.8) !important;
        border: 2px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 10px !important;
        color: #00d4ff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.5) !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #0099ff 0%, #00d4ff 50%, #00ff9d 100%) !important;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.6) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(0, 153, 255, 0.1) 0%, rgba(0, 212, 255, 0.1) 100%);
        border: 2px solid rgba(0, 212, 255, 0.3);
        border-radius: 10px;
        color: #00d4ff !important;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(0, 153, 255, 0.2) 0%, rgba(0, 212, 255, 0.2) 100%);
        border-color: #00d4ff;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif;
        font-size: 2rem;
        font-weight: 900;
        color: #00d4ff;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(10, 14, 39, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #0099ff 0%, #00d4ff 100%);
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #00d4ff 0%, #00ff9d 100%);
    }
    
    /* Loading animation */
    @keyframes scan {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .scanning-line {
        position: relative;
        overflow: hidden;
    }
    
    .scanning-line::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.3), transparent);
        animation: scan 2s linear infinite;
    }
    
    /* Status indicators */
    .status-online {
        color: #00ff9d;
        text-shadow: 0 0 10px rgba(0, 255, 157, 0.8);
        font-weight: 700;
        animation: pulse 2s ease-in-out infinite;
    }
    
    .status-offline {
        color: #ff0055;
        text-shadow: 0 0 10px rgba(255, 0, 85, 0.8);
        font-weight: 700;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.5), transparent);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "user_id" not in st.session_state:
    st.session_state.user_id = "demo_user"
if "collection_name" not in st.session_state:
    st.session_state.collection_name = "default"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def check_api_health() -> bool:
    """Check if API is available"""
    try:
        response = requests.get(f"{API_URL}/healthz", timeout=5)
        return response.status_code == 200
    except:
        return False


def upload_document(file, collection_name: str, user_id: str) -> Optional[Dict]:
    """Upload a document to the API"""
    try:
        files = {"file": (file.name, file, file.type)}
        data = {
            "collection_name": collection_name,
            "user_id": user_id
        }
        
        response = requests.post(
            f"{API_URL}/ingest/document",
            files=files,
            data=data,
            timeout=300
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error uploading document: {str(e)}")
        return None


def query_rag(
    query: str,
    collection_name: str,
    user_id: str,
    conversation_id: Optional[str] = None,
    retrieval_strategy: str = "hybrid",
    top_k: int = 5
) -> Optional[Dict]:
    """Query the RAG system"""
    try:
        payload = {
            "query": query,
            "collection_name": collection_name,
            "top_k": top_k,
            "use_rag": True
        }
        
        response = requests.post(
            f"{API_URL}/query/",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Query failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error querying: {str(e)}")
        return None


def create_conversation(user_id: str) -> Optional[str]:
    """Create a new conversation"""
    try:
        response = requests.post(
            f"{API_URL}/conversation/create",
            json={"user_id": user_id},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("conversation_id")
        return None
    except:
        return None


def display_sources(sources: List[Dict]):
    """Display source documents"""
    st.markdown("#### 📚 Sources")
    
    for i, source in enumerate(sources, 1):
        with st.expander(f"Source {i} - Score: {source.get('score', 0):.3f}"):
            st.markdown(f"**Content:**")
            # Get text from either 'text' or 'content' field (backend uses 'text')
            text_content = source.get('text', '') or source.get('content', '')
            if text_content:
                display_text = text_content[:500] + "..." if len(text_content) > 500 else text_content
                st.text(display_text)
            else:
                st.warning("No content available")
            
            # Display metadata
            metadata = source.get('metadata', {})
            if metadata:
                st.markdown("**Metadata:**")
                for key, value in metadata.items():
                    st.text(f"  • {key}: {value}")
            
            # Display source document info
            if source.get('filename'):
                st.markdown(f"**Source File:** `{source.get('filename')}`")
            if source.get('document_id'):
                st.markdown(f"**Document ID:** `{source.get('document_id')[:8]}...`")


def main():
    # Futuristic Header with animation
    st.markdown('''
    <div class="main-header">
        🌌 MODALITY<span style="color: #00ff9d;">RAG</span> 🌌
    </div>
    <div class="subtitle">
        ⚡ AI-Powered Multimodal Knowledge System ⚡
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Check API health
    api_healthy = check_api_health()
    
    if not api_healthy:
        st.markdown(f'''
        <div class="error-box">
            <h3>⚠️ SYSTEM OFFLINE</h3>
            <p>Cannot establish connection to API endpoint: <code>{API_URL}</code></p>
            <p>Please ensure the backend service is running.</p>
            <p style="margin-top: 1rem;">🚀 <strong>Start Command:</strong> <code>uvicorn src.api.main:app --reload</code></p>
        </div>
        ''', unsafe_allow_html=True)
        return
    
    # Sidebar with futuristic design
    with st.sidebar:
        # Logo area with glow effect
        st.markdown('''
        <div style="text-align: center; padding: 1rem 0 2rem 0;">
            <div style="
                font-family: 'Orbitron', sans-serif;
                font-size: 2rem;
                font-weight: 900;
                background: linear-gradient(135deg, #00d4ff 0%, #00ff9d 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
            ">
                🌌 MODALITY
            </div>
            <div style="color: #00d4ff; font-size: 0.9rem; letter-spacing: 3px; margin-top: 0.5rem;">
                NEURAL INTERFACE
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('<div style="height: 2px; background: linear-gradient(90deg, transparent, #00d4ff, transparent); margin: 1rem 0;"></div>', unsafe_allow_html=True)
        
        st.markdown("### ⚙️ SYSTEM CONFIGURATION")
        
        # User settings
        user_id = st.text_input("🔐 User ID", value=st.session_state.user_id)
        st.session_state.user_id = user_id
        
        collection_name = st.text_input("📁 Collection", value=st.session_state.collection_name)
        st.session_state.collection_name = collection_name
        
        st.markdown('<div style="height: 2px; background: linear-gradient(90deg, transparent, #00d4ff, transparent); margin: 1.5rem 0;"></div>', unsafe_allow_html=True)
        
        # Retrieval settings
        st.markdown("### 🔍 RETRIEVAL PARAMETERS")
        retrieval_strategy = st.selectbox(
            "Strategy Mode",
            ["hybrid", "dense", "sparse"],
            index=0
        )
        
        top_k = st.slider("📊 Top K Results", min_value=1, max_value=20, value=5)
        
        st.markdown('<div style="height: 2px; background: linear-gradient(90deg, transparent, #00d4ff, transparent); margin: 1.5rem 0;"></div>', unsafe_allow_html=True)
        
        # Conversation settings
        if CONVERSATION_ENABLED:
            st.markdown("### 💬 CONVERSATION MODE")
            
            if st.session_state.conversation_id:
                st.markdown(f'''
                <div style="
                    padding: 1rem;
                    background: linear-gradient(135deg, rgba(0, 255, 157, 0.1), rgba(0, 212, 255, 0.1));
                    border: 2px solid #00ff9d;
                    border-radius: 10px;
                    text-align: center;
                    box-shadow: 0 0 15px rgba(0, 255, 157, 0.3);
                ">
                    <div style="color: #00ff9d; font-weight: 700; font-size: 1.1rem;">
                        ✓ SESSION ACTIVE
                    </div>
                    <div style="color: #00d4ff; font-size: 0.8rem; margin-top: 0.5rem;">
                        {st.session_state.conversation_id[:16]}...
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                if st.button("🔴 END SESSION"):
                    st.session_state.conversation_id = None
                    st.session_state.chat_history = []
                    st.rerun()
            else:
                if st.button("🟢 START SESSION"):
                    conv_id = create_conversation(user_id)
                    if conv_id:
                        st.session_state.conversation_id = conv_id
                        st.success("🚀 Session Initiated!")
                        st.rerun()
        
        st.markdown('<div style="height: 2px; background: linear-gradient(90deg, transparent, #00d4ff, transparent); margin: 1.5rem 0;"></div>', unsafe_allow_html=True)
        
        # System info with status indicators
        st.markdown("### 📡 SYSTEM STATUS")
        status_color = "#00ff9d" if api_healthy else "#ff0055"
        status_text = "ONLINE" if api_healthy else "OFFLINE"
        st.markdown(f'''
        <div style="
            padding: 1rem;
            background: linear-gradient(135deg, rgba(15, 20, 40, 0.8), rgba(26, 31, 58, 0.8));
            border: 2px solid {status_color};
            border-radius: 10px;
            box-shadow: 0 0 15px {status_color}66;
        ">
            <div style="color: #00d4ff; font-size: 0.9rem; margin-bottom: 0.5rem;">🌐 API Endpoint</div>
            <div style="color: white; font-size: 0.8rem; word-break: break-all;">{API_URL}</div>
            <div style="margin-top: 1rem; color: {status_color}; font-weight: 700; font-size: 1.2rem; text-shadow: 0 0 10px {status_color};">
                {'🟢' if api_healthy else '🔴'} {status_text}
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Main content tabs with futuristic icons
    tab1, tab2, tab3 = st.tabs(["📤 DATA INGESTION", "💬 NEURAL QUERY", "📊 ANALYTICS"])
    
    # Tab 1: Upload with cyber aesthetics
    with tab1:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="
                font-family: 'Orbitron', sans-serif;
                color: #00d4ff;
                font-size: 2rem;
                text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
            ">📤 DOCUMENT INGESTION PROTOCOL</h2>
            <p style="color: #00d4ff; opacity: 0.8;">
                Upload documents to expand the neural knowledge matrix
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_files = st.file_uploader(
                "🔌 CONNECT DATA SOURCES",
                type=["txt", "pdf", "png", "jpg", "jpeg", "gif", "docx", "xlsx", "csv"],
                accept_multiple_files=True
            )
            
            if uploaded_files:
                st.markdown(f'''
                <div class="info-box">
                    <strong>📁 {len(uploaded_files)} FILE(S) DETECTED</strong>
                    <div style="margin-top: 0.5rem; font-size: 0.9rem;">
                        Ready for neural processing and embedding generation
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                if st.button("🚀 INITIATE UPLOAD SEQUENCE", type="primary", use_container_width=True):
                    progress_bar = st.progress(0)
                    status_container = st.empty()
                    success_count = 0
                    
                    for i, file in enumerate(uploaded_files):
                        status_container.markdown(f'''
                        <div class="scanning-line" style="
                            padding: 1rem;
                            background: linear-gradient(135deg, rgba(0, 153, 255, 0.1), rgba(0, 212, 255, 0.1));
                            border: 2px solid rgba(0, 212, 255, 0.5);
                            border-radius: 10px;
                            margin: 0.5rem 0;
                        ">
                            ⚡ Processing: <strong>{file.name}</strong>
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        result = upload_document(file, collection_name, user_id)
                        
                        if result:
                            success_count += 1
                            st.markdown(f'''
                            <div style="
                                padding: 0.75rem;
                                background: linear-gradient(135deg, rgba(0, 255, 157, 0.1), rgba(0, 212, 255, 0.1));
                                border-left: 4px solid #00ff9d;
                                border-radius: 5px;
                                margin: 0.3rem 0;
                                color: #00ff9d;
                                box-shadow: 0 0 10px rgba(0, 255, 157, 0.2);
                            ">
                                ✅ <strong>{file.name}</strong> - Neural embedding complete
                            </div>
                            ''', unsafe_allow_html=True)
                        
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    status_container.empty()
                    st.balloons()
                    st.markdown(f'''
                    <div class="success-box" style="text-align: center; font-size: 1.2rem;">
                        <h3>🎉 UPLOAD SEQUENCE COMPLETE</h3>
                        <div style="margin-top: 1rem;">
                            <strong style="font-size: 2rem;">{success_count}/{len(uploaded_files)}</strong>
                            <div>Files successfully integrated into knowledge matrix</div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                padding: 1.5rem;
                background: linear-gradient(135deg, rgba(0, 153, 255, 0.05), rgba(0, 212, 255, 0.05));
                border: 2px solid rgba(0, 212, 255, 0.3);
                border-radius: 15px;
                box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
            ">
                <h3 style="color: #00d4ff; font-family: 'Orbitron', sans-serif; margin-bottom: 1rem;">
                    📋 SUPPORTED FORMATS
                </h3>
                <div style="color: #00d4ff; line-height: 2;">
                    📄 Text Documents (.txt)<br>
                    📕 PDF Files (.pdf)<br>
                    🖼️ Images (.png, .jpg)<br>
                    📝 Word Documents (.docx)<br>
                    📊 Spreadsheets (.xlsx)<br>
                    📈 CSV Data (.csv)
                </div>
                <div style="
                    margin-top: 1.5rem;
                    padding-top: 1.5rem;
                    border-top: 2px solid rgba(0, 212, 255, 0.3);
                ">
                    <h4 style="color: #00ff9d; margin-bottom: 0.75rem;">⚡ OPTIMIZATION TIPS</h4>
                    <div style="color: #00d4ff; font-size: 0.9rem; line-height: 1.8;">
                        • Use descriptive filenames<br>
                        • Organize by collection<br>
                        • Monitor upload status<br>
                        • Verify embedding generation
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Tab 2: Query & Chat with neural aesthetics
    with tab2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="
                font-family: 'Orbitron', sans-serif;
                color: #00d4ff;
                font-size: 2rem;
                text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
            ">💬 NEURAL QUERY INTERFACE</h2>
            <p style="color: #00d4ff; opacity: 0.8;">
                Access the knowledge matrix through natural language processing
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Query input with futuristic styling
        query = st.text_area(
            "🎯 ENTER QUERY SEQUENCE:",
            placeholder="What insights do you seek from the knowledge matrix?",
            height=120
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_button = st.button("🔍 EXECUTE QUERY", type="primary", use_container_width=True)
        
        with col2:
            use_conversation = st.checkbox("🔗 Memory Mode", value=bool(st.session_state.conversation_id))
        
        # Execute query
        if search_button and query:
            with st.spinner("🔄 Processing neural query..."):
                conv_id = st.session_state.conversation_id if use_conversation else None
                
                result = query_rag(
                    query,
                    collection_name,
                    user_id,
                    conv_id,
                    retrieval_strategy,
                    top_k
                )
                
                if result:
                    # Display answer with holographic effect
                    st.markdown("""
                    <div style="margin: 2rem 0;">
                        <h3 style="
                            color: #00ff9d;
                            font-family: 'Orbitron', sans-serif;
                            text-shadow: 0 0 15px rgba(0, 255, 157, 0.5);
                        ">💡 NEURAL RESPONSE</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f'''
                    <div class="success-box">
                        {result.get("answer", "Unable to generate response")}
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Update chat history
                    st.session_state.chat_history.append({
                        "query": query,
                        "answer": result.get("answer", ""),
                        "timestamp": time.time()
                    })
                    
                    # Display sources with holographic cards
                    sources = result.get("sources", [])
                    if sources:
                        st.markdown("""
                        <div style="margin: 2rem 0;">
                            <h3 style="
                                color: #00d4ff;
                                font-family: 'Orbitron', sans-serif;
                                text-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
                            ">📚 SOURCE VECTORS</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for i, source in enumerate(sources, 1):
                            score = source.get('score', 0)
                            score_color = "#00ff9d" if score > 0.7 else "#00d4ff" if score > 0.4 else "#0099ff"
                            
                            with st.expander(f"🔹 Source Vector {i} | Similarity: {score:.3f}", expanded=(i==1)):
                                # Get content from 'text' field (backend uses 'text', not 'content')
                                content = source.get('text', '') or source.get('content', '')
                                
                                if not content:
                                    st.warning("⚠️ No content available for this source")
                                    continue
                                    
                                preview = content[:500] + "..." if len(content) > 500 else content
                                
                                st.markdown(f'''
                                <div class="source-card">
                                    <div style="
                                        color: {score_color};
                                        font-weight: 700;
                                        margin-bottom: 1rem;
                                        font-size: 1.1rem;
                                    ">
                                        📊 Relevance Score: <span style="font-size: 1.3rem;">{score:.3f}</span>
                                    </div>
                                    <div style="color: #00d4ff; margin-top: 1rem;">
                                        <strong>Content:</strong>
                                    </div>
                                    <div style="
                                        color: white;
                                        margin-top: 0.5rem;
                                        padding: 1rem;
                                        background: rgba(0, 0, 0, 0.3);
                                        border-radius: 8px;
                                        line-height: 1.6;
                                        white-space: pre-wrap;
                                        word-wrap: break-word;
                                    ">
                                        {preview}
                                    </div>
                                </div>
                                ''', unsafe_allow_html=True)
                                
                                # Display filename and document info
                                if source.get('filename'):
                                    st.markdown(f"**📄 Source File:** `{source.get('filename')}`")
                                if source.get('document_id'):
                                    st.markdown(f"**🔗 Document ID:** `{source.get('document_id')[:16]}...`")
                                
                                metadata = source.get('metadata', {})
                                if metadata:
                                    st.markdown("**🔖 Metadata:**")
                                    for key, value in metadata.items():
                                        st.markdown(f"  • `{key}`: {value}")
                    
                    # Display metrics with cyber cards
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f'''
                        <div class="metric-card">
                            <div style="color: #00d4ff; font-size: 0.9rem; margin-bottom: 0.5rem;">
                                VECTORS FOUND
                            </div>
                            <div style="
                                font-family: 'Orbitron', sans-serif;
                                font-size: 2.5rem;
                                font-weight: 900;
                                color: #00ff9d;
                                text-shadow: 0 0 15px rgba(0, 255, 157, 0.5);
                            ">
                                {len(sources)}
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    with col2:
                        response_time = result.get('response_time', 0)
                        st.markdown(f'''
                        <div class="metric-card">
                            <div style="color: #00d4ff; font-size: 0.9rem; margin-bottom: 0.5rem;">
                                RESPONSE TIME
                            </div>
                            <div style="
                                font-family: 'Orbitron', sans-serif;
                                font-size: 2.5rem;
                                font-weight: 900;
                                color: #00d4ff;
                                text-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
                            ">
                                {response_time:.2f}s
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f'''
                        <div class="metric-card">
                            <div style="color: #00d4ff; font-size: 0.9rem; margin-bottom: 0.5rem;">
                                STRATEGY
                            </div>
                            <div style="
                                font-family: 'Orbitron', sans-serif;
                                font-size: 1.5rem;
                                font-weight: 700;
                                color: #0099ff;
                                text-shadow: 0 0 15px rgba(0, 153, 255, 0.5);
                                text-transform: uppercase;
                            ">
                                {retrieval_strategy}
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
        
        # Display chat history with timeline effect
        if st.session_state.chat_history:
            st.markdown("---")
            st.markdown("""
            <div style="margin: 2rem 0;">
                <h3 style="
                    color: #00d4ff;
                    font-family: 'Orbitron', sans-serif;
                    text-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
                ">📜 QUERY HISTORY</h3>
            </div>
            """, unsafe_allow_html=True)
            
            for i, item in enumerate(reversed(st.session_state.chat_history[-5:]), 1):
                query_preview = item['query'][:60] + "..." if len(item['query']) > 60 else item['query']
                
                with st.expander(f"🕐 Query {len(st.session_state.chat_history) - i + 1}: {query_preview}"):
                    st.markdown(f'''
                    <div style="
                        padding: 1rem;
                        background: linear-gradient(135deg, rgba(0, 153, 255, 0.05), rgba(0, 212, 255, 0.05));
                        border-left: 4px solid #00d4ff;
                        border-radius: 10px;
                    ">
                        <div style="color: #00d4ff; font-weight: 700; margin-bottom: 0.5rem;">
                            ❓ QUESTION:
                        </div>
                        <div style="color: white; margin-bottom: 1rem;">
                            {item['query']}
                        </div>
                        <div style="color: #00ff9d; font-weight: 700; margin-bottom: 0.5rem;">
                            ✓ RESPONSE:
                        </div>
                        <div style="color: white;">
                            {item['answer']}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
    
    # Tab 3: Analytics with holographic design
    with tab3:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="
                font-family: 'Orbitron', sans-serif;
                color: #00d4ff;
                font-size: 2rem;
                text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
            ">📊 SYSTEM DIAGNOSTICS</h2>
            <p style="color: #00d4ff; opacity: 0.8;">
                Real-time monitoring of neural network components
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            # Get health status
            response = requests.get(f"{API_URL}/ready", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                
                st.markdown("### 🏥 COMPONENT STATUS")
                
                col1, col2, col3, col4 = st.columns(4)
                
                deps = health_data.get("dependencies", {})
                
                def create_status_card(title, emoji, status_key):
                    is_healthy = "healthy" in str(deps.get(status_key, "")).lower()
                    status_color = "#00ff9d" if is_healthy else "#ff0055"
                    status_text = "ONLINE" if is_healthy else "OFFLINE"
                    status_icon = "🟢" if is_healthy else "🔴"
                    
                    return f'''
                    <div style="
                        padding: 1.5rem;
                        background: linear-gradient(135deg, rgba(15, 20, 40, 0.8), rgba(26, 31, 58, 0.8));
                        border: 2px solid {status_color};
                        border-radius: 15px;
                        text-align: center;
                        box-shadow: 0 0 20px {status_color}66;
                        transition: all 0.3s ease;
                    ">
                        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">
                            {emoji}
                        </div>
                        <div style="
                            color: #00d4ff;
                            font-size: 0.9rem;
                            margin-bottom: 0.75rem;
                            font-weight: 600;
                        ">
                            {title}
                        </div>
                        <div style="
                            color: {status_color};
                            font-family: 'Orbitron', sans-serif;
                            font-weight: 900;
                            font-size: 1.2rem;
                            text-shadow: 0 0 10px {status_color};
                        ">
                            {status_icon} {status_text}
                        </div>
                    </div>
                    '''
                
                with col1:
                    st.markdown(create_status_card("VECTOR DB", "🗄️", "vector_db"), unsafe_allow_html=True)
                
                with col2:
                    st.markdown(create_status_card("DOCUMENT STORE", "📦", "document_store"), unsafe_allow_html=True)
                
                with col3:
                    st.markdown(create_status_card("CACHE LAYER", "⚡", "cache"), unsafe_allow_html=True)
                
                with col4:
                    st.markdown(create_status_card("LLM ENGINE", "🧠", "llm_provider"), unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("### 📈 USAGE METRICS")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">💬</div>
                        <div style="color: #00d4ff; font-size: 0.9rem; margin-bottom: 0.5rem;">
                            QUERY HISTORY
                        </div>
                        <div style="
                            font-family: 'Orbitron', sans-serif;
                            font-size: 3rem;
                            font-weight: 900;
                            color: #00ff9d;
                            text-shadow: 0 0 15px rgba(0, 255, 157, 0.5);
                        ">
                            {len(st.session_state.chat_history)}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">📁</div>
                        <div style="color: #00d4ff; font-size: 0.9rem; margin-bottom: 0.5rem;">
                            ACTIVE COLLECTION
                        </div>
                        <div style="
                            font-family: 'Orbitron', sans-serif;
                            font-size: 1.5rem;
                            font-weight: 700;
                            color: #00d4ff;
                            text-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
                            word-break: break-word;
                        ">
                            {collection_name}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">👤</div>
                        <div style="color: #00d4ff; font-size: 0.9rem; margin-bottom: 0.5rem;">
                            CURRENT USER
                        </div>
                        <div style="
                            font-family: 'Orbitron', sans-serif;
                            font-size: 1.5rem;
                            font-weight: 700;
                            color: #0099ff;
                            text-shadow: 0 0 15px rgba(0, 153, 255, 0.5);
                            word-break: break-word;
                        ">
                            {user_id}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                # Additional system information
                st.markdown("---")
                st.markdown("### 🔧 CONFIGURATION")
                
                config_data = {
                    "Retrieval Strategy": retrieval_strategy.upper(),
                    "Top K Results": str(top_k),
                    "Conversation Mode": "ENABLED" if CONVERSATION_ENABLED else "DISABLED",
                    "Active Session": "YES" if st.session_state.conversation_id else "NO"
                }
                
                cols = st.columns(2)
                for idx, (key, value) in enumerate(config_data.items()):
                    with cols[idx % 2]:
                        st.markdown(f'''
                        <div style="
                            padding: 1rem;
                            background: linear-gradient(135deg, rgba(0, 153, 255, 0.05), rgba(0, 212, 255, 0.05));
                            border-left: 4px solid #00d4ff;
                            border-radius: 10px;
                            margin-bottom: 1rem;
                        ">
                            <div style="color: #00d4ff; font-size: 0.85rem; margin-bottom: 0.3rem;">
                                {key}
                            </div>
                            <div style="
                                color: #00ff9d;
                                font-family: 'Orbitron', sans-serif;
                                font-weight: 700;
                                font-size: 1.1rem;
                            ">
                                {value}
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
        
        except Exception as e:
            st.markdown(f'''
            <div class="error-box">
                <h3>⚠️ DIAGNOSTICS UNAVAILABLE</h3>
                <p>Unable to retrieve system analytics</p>
                <p style="margin-top: 0.5rem; font-size: 0.9rem;">Error: {str(e)}</p>
            </div>
            ''', unsafe_allow_html=True)
    
    # Futuristic Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 3rem 0 2rem 0;'>
        <div style='
            font-family: "Orbitron", sans-serif;
            font-size: 2rem;
            font-weight: 900;
            background: linear-gradient(135deg, #00d4ff 0%, #00ff9d 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        '>
            🌌 MODALITY<span style="font-size: 1rem;">RAG</span>
        </div>
        <div style='
            color: #00d4ff;
            font-size: 1rem;
            letter-spacing: 2px;
            margin-bottom: 1.5rem;
        '>
            NEURAL KNOWLEDGE SYSTEM v1.0.0
        </div>
        <div style='
            color: rgba(0, 212, 255, 0.6);
            font-size: 0.9rem;
            line-height: 1.8;
        '>
            Built with FastAPI • Streamlit • AI ❤️<br>
            <span style="color: rgba(0, 255, 157, 0.6);">
                Deploy on Railway • Vercel • Render
            </span>
        </div>
        <div style='
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            border-top: 2px solid rgba(0, 212, 255, 0.2);
            color: rgba(0, 212, 255, 0.5);
            font-size: 0.8rem;
        '>
            🔒 Secure • ⚡ Fast • 🌐 Multilingual • 🚀 Production-Ready
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
