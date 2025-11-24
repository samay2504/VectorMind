"""
Enhanced Streamlit Components for VectorMind

Copyright © 2025 Samay Mehar. All Rights Reserved.
PROPRIETARY SOFTWARE - PATENT PENDING
"""

import streamlit as st
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
import time


def display_query_types() -> str:
    """Display segmented control for query types"""
    st.markdown("#### 🔍 Query Type")
    
    query_types = {
        "Factual": {
            "emoji": "📊",
            "description": "Direct answers from documents"
        },
        "Exploratory": {
            "emoji": "🔬",
            "description": "Discover related information"
        },
        "Cross-Modal": {
            "emoji": "🎨",
            "description": "Search across text and images"
        }
    }
    
    cols = st.columns(3)
    selected_type = st.session_state.get("query_type", "Factual")
    
    for idx, (type_name, type_info) in enumerate(query_types.items()):
        with cols[idx]:
            if st.button(
                f"{type_info['emoji']} {type_name}",
                key=f"query_type_{type_name}",
                use_container_width=True,
                type="primary" if selected_type == type_name else "secondary"
            ):
                st.session_state.query_type = type_name
                selected_type = type_name
    
    st.caption(f"*{query_types[selected_type]['description']}*")
    return selected_type


def display_system_stats(api_url: str):
    """Display system statistics in sidebar"""
    st.markdown("### 📈 System Stats")
    
    try:
        # Fetch health status
        health_response = requests.get(f"{api_url}/api/health", timeout=5)
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            components = health_data.get("components", {})
            
            # Status indicators
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Vector DB",
                    "🟢 Online" if components.get("vector_db") == "healthy" else "🔴 Offline"
                )
                st.metric(
                    "MongoDB",
                    "🟢 Online" if components.get("mongodb") == "healthy" else "🔴 Offline"
                )
            
            with col2:
                st.metric(
                    "LLM Provider",
                    "🟢 Active" if components.get("llm_provider") == "healthy" else "🔴 Inactive"
                )
                st.metric(
                    "Redis",
                    "🟢 Connected" if components.get("redis") == "healthy" else "🔴 Disconnected"
                )
        
        # Try to fetch collection stats
        try:
            stats_response = requests.get(f"{api_url}/api/stats", timeout=5)
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                
                st.divider()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Documents", stats_data.get("total_documents", 0))
                with col2:
                    st.metric("Total Chunks", stats_data.get("total_chunks", 0))
                
                st.caption(f"Collection: `{stats_data.get('collection_name', 'N/A')}`")
                st.caption(f"Vector DB: `{stats_data.get('vector_db_type', 'N/A')}`")
        except:
            pass
            
    except Exception as e:
        st.warning("Unable to fetch system stats")
        st.caption(f"Error: {str(e)[:50]}...")


def display_upload_section(api_url: str):
    """Enhanced upload section with file validation"""
    st.markdown("### 📁 Upload Documents")
    
    # Supported file types
    supported_types = ["txt", "pdf", "png", "jpg", "jpeg", "docx", "xlsx", "csv", "md"]
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 255, 255, 0.1) 100%);
        border: 2px dashed #00d4ff;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    ">
        <p style="color: #00d4ff; font-size: 1.1rem; margin: 0;">
            📤 Drag and drop files here
        </p>
        <p style="color: #888; font-size: 0.9rem; margin-top: 5px;">
            Supports: {", ".join(supported_types).upper()}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=supported_types,
        accept_multiple_files=True,
        key="file_uploader",
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) selected**")
        
        # Display file details
        for file in uploaded_files:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                file_icon = {
                    'pdf': '📄', 'txt': '📝', 'docx': '📘',
                    'xlsx': '📊', 'csv': '📈',
                    'png': '🖼️', 'jpg': '🖼️', 'jpeg': '🖼️'
                }.get(file.name.split('.')[-1].lower(), '📎')
                st.write(f"{file_icon} `{file.name}`")
            with col2:
                st.caption(f"{file.size / 1024:.1f} KB")
            with col3:
                st.badge(file.name.split('.')[-1].upper(), text_color="text")
        
        # Upload button
        if st.button("🚀 Process Files", use_container_width=True, type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, file in enumerate(uploaded_files):
                try:
                    status_text.text(f"Uploading {file.name}...")
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                    
                    # Upload file
                    files = {"file": (file.name, file, file.type)}
                    response = requests.post(
                        f"{api_url}/api/ingest/upload",
                        files=files,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {file.name}: {result.get('num_chunks', 0)} chunks created")
                    else:
                        st.error(f"❌ {file.name}: Upload failed")
                
                except Exception as e:
                    st.error(f"❌ {file.name}: {str(e)}")
                
                time.sleep(0.5)  # Small delay for UX
            
            status_text.text("Upload complete!")
            progress_bar.empty()
            time.sleep(2)
            status_text.empty()


def display_query_interface(api_url: str):
    """Enhanced query interface"""
    st.markdown("### 🔍 Query Documents")
    
    # Query type selector
    query_type = display_query_types()
    
    # Query input
    query_text = st.text_area(
        "Enter your question or search query",
        placeholder="e.g., What are the key metrics from Q4 reports?",
        height=120,
        key="query_input",
        help="Press Ctrl+Enter to submit"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        search_button = st.button(
            "🔎 Search",
            use_container_width=True,
            type="primary",
            disabled=not query_text.strip()
        )
    
    with col2:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.search_results = None
            st.session_state.query_input = ""
            st.rerun()
    
    if search_button and query_text.strip():
        with st.spinner("🔍 Searching documents..."):
            try:
                response = requests.post(
                    f"{api_url}/api/query/",
                    json={
                        "query": query_text,
                        "collection_name": "multimodal_docs",
                        "top_k": 5,
                        "use_rag": True
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    st.session_state.search_results = response.json()
                    st.session_state.query_text = query_text
                else:
                    st.error(f"Query failed: {response.status_code}")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")


def display_results_panel():
    """Enhanced results display with metrics"""
    st.markdown("### 📊 Results")
    
    if "search_results" not in st.session_state:
        st.info("💡 Run a query to see results")
        return
    
    results = st.session_state.search_results
    
    if not results:
        st.warning("No results found. Try a different query.")
        return
    
    # Display metrics
    sources = results.get("sources", [])
    metadata = results.get("metadata", {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Results", len(sources))
    
    with col2:
        if sources:
            avg_relevance = sum(
                (s.get("score", 0) * 100) for s in sources
            ) / len(sources)
            st.metric("Avg Relevance", f"{avg_relevance:.0f}%")
        else:
            st.metric("Avg Relevance", "N/A")
    
    with col3:
        processing_time = metadata.get("processing_time", 0)
        st.metric("Search Time", f"{processing_time}ms")
    
    st.divider()
    
    # Display answer
    answer = results.get("answer", "")
    if answer:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 255, 0, 0.1) 100%);
            border-left: 4px solid #00d4ff;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="width: 8px; height: 8px; background: #00ff00; border-radius: 50%; margin-right: 10px; animation: pulse 2s infinite;"></div>
                <strong style="color: #00d4ff;">Answer</strong>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(answer)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Metadata
        if metadata:
            meta_cols = st.columns(3)
            with meta_cols[0]:
                st.caption(f"Provider: `{metadata.get('provider', 'N/A')}`")
            with meta_cols[1]:
                st.caption(f"Intent: `{metadata.get('intent', 'N/A')}`")
            with meta_cols[2]:
                st.caption(f"Type: `{metadata.get('query_type', 'N/A')}`")
    
    st.divider()
    
    # Display sources
    if sources:
        st.markdown("#### 📚 Sources")
        
        for idx, source in enumerate(sources, 1):
            relevance = min(max(int((source.get("score", 0) * 100)), 0), 100)
            
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    filename = source.get("filename", f"Source {idx}")
                    file_icon = "📄" if "pdf" in filename.lower() else "📝" if "txt" in filename.lower() else "🖼️" if any(ext in filename.lower() for ext in ['.png', '.jpg', '.jpeg']) else "📎"
                    st.markdown(f"**{file_icon} {filename}**")
                
                with col2:
                    file_ext = filename.split('.')[-1].upper() if '.' in filename else "FILE"
                    st.badge(file_ext)
                
                with col3:
                    st.markdown(f"**🎯 {relevance}%**")
                
                # Relevance bar
                st.progress(relevance / 100, text=f"Relevance Score: {relevance}%")
                
                # Content preview
                text = source.get("text", "No preview available")
                st.caption(text[:300] + "..." if len(text) > 300 else text)
                
                # Metadata footer
                meta_cols = st.columns(3)
                with meta_cols[0]:
                    doc_id = source.get("document_id", "N/A")
                    st.caption(f"📑 ID: `{doc_id[:12]}...`")
                with meta_cols[1]:
                    chunk_idx = source.get("metadata", {}).get("chunk_index", "N/A")
                    st.caption(f"📦 Chunk: `{chunk_idx}`")
                with meta_cols[2]:
                    st.caption(f"📅 Retrieved: `{datetime.now().strftime('%H:%M:%S')}`")
