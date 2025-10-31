#!/bin/bash

# Demo script for Multimodal RAG System
# This script demonstrates the complete workflow of ingestion and querying

set -e

API_URL="http://localhost:8000"
SAMPLES_DIR="./samples"

echo "🚀 Multimodal RAG System - Demo Script"
echo "========================================"
echo ""

# Check if API is running
echo "📡 Checking API health..."
if ! curl -s "${API_URL}/healthz" > /dev/null; then
    echo "❌ API is not running. Please start with: docker-compose up -d"
    exit 1
fi
echo "✅ API is healthy"
echo ""

# Function to ingest a document
ingest_document() {
    local file=$1
    local source=$2
    local category=$3
    
    echo "📄 Ingesting: $(basename $file)"
    response=$(curl -s -X POST "${API_URL}/ingest" \
        -F "file=@${file}" \
        -F "source=${source}" \
        -F "metadata={\"category\":\"${category}\",\"consent\":true}")
    
    doc_id=$(echo $response | jq -r '.doc_id')
    echo "   ✅ Document ID: ${doc_id}"
    echo ""
}

# Function to query documents
query_documents() {
    local query=$1
    local strategy=$2
    
    echo "🔍 Querying: \"${query}\""
    echo "   Strategy: ${strategy}"
    
    response=$(curl -s -X POST "${API_URL}/query" \
        -H "Content-Type: application/json" \
        -d "{
            \"query\": \"${query}\",
            \"top_k\": 3,
            \"strategy\": \"${strategy}\",
            \"rerank\": true
        }")
    
    echo "   Results:"
    echo $response | jq -r '.results[] | "   - Score: \(.score) | Source: \(.source) | Page: \(.page)"'
    echo ""
}

echo "📥 Phase 1: Document Ingestion"
echo "================================"
echo ""

# Ingest text documents
if [ -d "${SAMPLES_DIR}/text" ]; then
    for file in ${SAMPLES_DIR}/text/*.txt; do
        [ -f "$file" ] && ingest_document "$file" "demo" "text"
    done
fi

# Ingest images
if [ -d "${SAMPLES_DIR}/images" ]; then
    for file in ${SAMPLES_DIR}/images/*.{png,jpg,jpeg}; do
        [ -f "$file" ] && ingest_document "$file" "demo" "image"
    done
fi

# Ingest PDFs
if [ -d "${SAMPLES_DIR}/pdfs" ]; then
    for file in ${SAMPLES_DIR}/pdfs/*.pdf; do
        [ -f "$file" ] && ingest_document "$file" "demo" "pdf"
    done
fi

echo "⏳ Waiting for ingestion to complete (10 seconds)..."
sleep 10
echo ""

echo "🔍 Phase 2: Querying"
echo "===================="
echo ""

# Dense search
query_documents "machine learning algorithms" "dense"

# Sparse search
query_documents "data visualization techniques" "sparse"

# Hybrid search
query_documents "artificial intelligence applications" "hybrid"

# Cross-modal query
query_documents "chart showing sales trends" "hybrid"

echo "📊 Phase 3: System Stats"
echo "========================"
echo ""

# Get system health
echo "🏥 System Health:"
curl -s "${API_URL}/ready" | jq '.'
echo ""

# Get vector DB info (if endpoint exists)
echo "💾 Vector Database Status:"
echo "   Active DB: Qdrant (primary)"
echo "   Fallback: Milvus (available)"
echo ""

echo "✅ Demo Complete!"
echo ""
echo "📚 Next Steps:"
echo "   - View API docs: ${API_URL}/docs"
echo "   - Check metrics: http://localhost:9090"
echo "   - View Grafana: http://localhost:3000"
echo "   - Monitor Celery: http://localhost:5555"
echo ""
