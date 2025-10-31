"""
Streamlit Frontend for Multimodal RAG System

A production-ready, user-friendly interface for document upload and querying.
Designed for easy deployment on Railway, Vercel, or Render.
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
    page_title="Multimodal RAG System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    .source-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .metric-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        text-align: center;
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
            "user_id": user_id,
            "retrieval_strategy": retrieval_strategy,
            "top_k": top_k
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        response = requests.post(
            f"{API_URL}/query/rag",
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
            st.text(source.get('content', '')[:500] + "..." if len(source.get('content', '')) > 500 else source.get('content', ''))
            
            metadata = source.get('metadata', {})
            if metadata:
                st.markdown("**Metadata:**")
                for key, value in metadata.items():
                    st.text(f"  • {key}: {value}")


def main():
    # Header
    st.markdown('<div class="main-header">🔍 Multimodal RAG System</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Check API health
    api_healthy = check_api_health()
    
    if not api_healthy:
        st.error(f"⚠️ Cannot connect to API at {API_URL}. Please ensure the API is running.")
        st.info("Start the API with: `uvicorn src.api.main:app --reload`")
        return
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/1f77b4/ffffff?text=RAG+System", use_column_width=True)
        st.markdown("### ⚙️ Settings")
        
        # User settings
        user_id = st.text_input("User ID", value=st.session_state.user_id)
        st.session_state.user_id = user_id
        
        collection_name = st.text_input("Collection Name", value=st.session_state.collection_name)
        st.session_state.collection_name = collection_name
        
        st.markdown("---")
        
        # Retrieval settings
        st.markdown("### 🔍 Retrieval Settings")
        retrieval_strategy = st.selectbox(
            "Strategy",
            ["hybrid", "dense", "sparse"],
            index=0
        )
        
        top_k = st.slider("Top K Results", min_value=1, max_value=20, value=5)
        
        st.markdown("---")
        
        # Conversation settings
        if CONVERSATION_ENABLED:
            st.markdown("### 💬 Conversation")
            
            if st.session_state.conversation_id:
                st.success(f"Active: {st.session_state.conversation_id[:8]}...")
                if st.button("End Conversation"):
                    st.session_state.conversation_id = None
                    st.session_state.chat_history = []
                    st.rerun()
            else:
                if st.button("Start Conversation"):
                    conv_id = create_conversation(user_id)
                    if conv_id:
                        st.session_state.conversation_id = conv_id
                        st.success("Conversation started!")
                        st.rerun()
        
        st.markdown("---")
        
        # System info
        st.markdown("### ℹ️ System Info")
        st.text(f"API: {API_URL}")
        st.text(f"Status: {'🟢 Online' if api_healthy else '🔴 Offline'}")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload Documents", "💬 Query & Chat", "📊 Analytics"])
    
    # Tab 1: Upload
    with tab1:
        st.markdown("## 📤 Upload Documents")
        st.markdown("Upload documents to build your knowledge base. Supported formats: Text, PDF, Images, DOCX, XLSX")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_files = st.file_uploader(
                "Choose files",
                type=["txt", "pdf", "png", "jpg", "jpeg", "gif", "docx", "xlsx", "csv"],
                accept_multiple_files=True
            )
            
            if uploaded_files:
                if st.button("🚀 Upload All", type="primary"):
                    progress_bar = st.progress(0)
                    success_count = 0
                    
                    for i, file in enumerate(uploaded_files):
                        st.info(f"Uploading: {file.name}")
                        result = upload_document(file, collection_name, user_id)
                        
                        if result:
                            success_count += 1
                            st.success(f"✅ {file.name} uploaded successfully!")
                        
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    st.balloons()
                    st.success(f"🎉 Uploaded {success_count}/{len(uploaded_files)} files successfully!")
        
        with col2:
            st.markdown("### 📋 Tips")
            st.info("""
            **Supported Files:**
            - 📄 Text (.txt)
            - 📕 PDF (.pdf)
            - 🖼️ Images (.png, .jpg)
            - 📝 Word (.docx)
            - 📊 Excel (.xlsx)
            
            **Best Practices:**
            - Use descriptive filenames
            - Organize by collection
            - Wait for upload confirmation
            """)
    
    # Tab 2: Query & Chat
    with tab2:
        st.markdown("## 💬 Query Your Knowledge Base")
        
        # Query input
        query = st.text_area(
            "Enter your question:",
            placeholder="What would you like to know?",
            height=100
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_button = st.button("🔍 Search", type="primary", use_container_width=True)
        
        with col2:
            use_conversation = st.checkbox("Use Conversation", value=bool(st.session_state.conversation_id))
        
        # Execute query
        if search_button and query:
            with st.spinner("Searching..."):
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
                    # Display answer
                    st.markdown("### 💡 Answer")
                    st.markdown(f'<div class="success-box">{result.get("answer", "No answer generated")}</div>', unsafe_allow_html=True)
                    
                    # Update chat history
                    st.session_state.chat_history.append({
                        "query": query,
                        "answer": result.get("answer", ""),
                        "timestamp": time.time()
                    })
                    
                    # Display sources
                    sources = result.get("sources", [])
                    if sources:
                        display_sources(sources)
                    
                    # Display metrics
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Sources Found", len(sources))
                    with col2:
                        st.metric("Response Time", f"{result.get('response_time', 0):.2f}s")
                    with col3:
                        st.metric("Strategy", retrieval_strategy.title())
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("---")
            st.markdown("### 📜 Recent Queries")
            
            for i, item in enumerate(reversed(st.session_state.chat_history[-5:]), 1):
                with st.expander(f"Query {len(st.session_state.chat_history) - i + 1}: {item['query'][:50]}..."):
                    st.markdown(f"**Question:** {item['query']}")
                    st.markdown(f"**Answer:** {item['answer']}")
    
    # Tab 3: Analytics
    with tab3:
        st.markdown("## 📊 System Analytics")
        
        try:
            # Get health status
            response = requests.get(f"{API_URL}/ready", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                
                st.markdown("### 🏥 System Health")
                
                col1, col2, col3, col4 = st.columns(4)
                
                deps = health_data.get("dependencies", {})
                
                with col1:
                    status = "🟢" if "healthy" in str(deps.get("vector_db", "")) else "🔴"
                    st.metric("Vector DB", status)
                
                with col2:
                    status = "🟢" if "healthy" in str(deps.get("document_store", "")) else "🔴"
                    st.metric("Document Store", status)
                
                with col3:
                    status = "🟢" if "healthy" in str(deps.get("cache", "")) else "🔴"
                    st.metric("Cache", status)
                
                with col4:
                    status = "🟢" if "healthy" in str(deps.get("llm_provider", "")) else "🔴"
                    st.metric("LLM Provider", status)
                
                st.markdown("---")
                st.markdown("### 📈 Usage Statistics")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Chat History", len(st.session_state.chat_history))
                
                with col2:
                    st.metric("Active Collection", collection_name)
                
                with col3:
                    st.metric("Current User", user_id)
        
        except Exception as e:
            st.error(f"Failed to fetch analytics: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6c757d; padding: 2rem;'>
        <p>🔍 Multimodal RAG System v1.0.0</p>
        <p>Built with FastAPI, Streamlit, and ❤️</p>
        <p>Deploy on Railway, Vercel, or Render</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
