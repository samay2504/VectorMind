# Sample Data for Multimodal RAG System

This directory contains sample data for testing the Multimodal RAG System.

## Directory Structure

```
sample_data/
├── texts/          # 6 text documents (.txt)
├── images/         # Image files (.png, .jpg, .jpeg)
└── pdfs/           # PDF documents (text, image, mixed)
```

## Text Documents (6 files)

1. **company_overview.txt** - TechCorp company information
2. **product_specifications.txt** - CloudSync platform technical specs
3. **customer_success_story.txt** - GlobalRetail case study
4. **api_documentation.txt** - CloudSync API reference
5. **security_whitepaper.txt** - Security architecture document
6. **training_materials.txt** - CloudSync training course outline

## Images (Placeholder)

To complete the sample dataset, add 5+ images to `sample_data/images/`:

Suggested images:
- Product screenshots
- Architecture diagrams
- Charts and graphs (sales data, performance metrics)
- Company logos
- Infographics

Image formats: PNG, JPG, JPEG

## PDFs (Placeholder)

To complete the sample dataset, add 3+ PDFs to `sample_data/pdfs/`:

Required PDF types:
1. **Text-only PDF** - Pure text content (e.g., contract, report)
2. **Image-only PDF** - Scanned document or image-based PDF
3. **Mixed PDF** - Contains both text and embedded images

You can create these PDFs from:
- Converting text documents to PDF
- Scanning documents or creating image-based PDFs
- Creating presentations with text and images, export to PDF

## Using Sample Data

### Upload via API

```bash
# Upload text document
curl -X POST "http://localhost:8000/ingest/document" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_data/texts/company_overview.txt" \
  -F "collection_name=techcorp_docs" \
  -F "user_id=demo_user"

# Upload image
curl -X POST "http://localhost:8000/ingest/document" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_data/images/architecture_diagram.png" \
  -F "collection_name=techcorp_docs" \
  -F "user_id=demo_user"

# Upload PDF
curl -X POST "http://localhost:8000/ingest/document" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_data/pdfs/security_report.pdf" \
  -F "collection_name=techcorp_docs" \
  -F "user_id=demo_user"
```

### Batch Upload

```bash
curl -X POST "http://localhost:8000/ingest/batch" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@sample_data/texts/company_overview.txt" \
  -F "files=@sample_data/texts/product_specifications.txt" \
  -F "files=@sample_data/texts/api_documentation.txt" \
  -F "collection_name=techcorp_docs" \
  -F "user_id=demo_user"
```

### Query Examples

After uploading sample data, try these queries:

```bash
# Factual question
curl -X POST "http://localhost:8000/query/rag" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is TechCorps annual revenue?",
    "collection_name": "techcorp_docs",
    "user_id": "demo_user"
  }'

# Technical query
curl -X POST "http://localhost:8000/query/rag" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the system requirements for CloudSync Platform?",
    "collection_name": "techcorp_docs",
    "user_id": "demo_user"
  }'

# Cross-modal query (if images uploaded)
curl -X POST "http://localhost:8000/query/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find architecture diagrams showing cloud infrastructure",
    "collection_name": "techcorp_docs",
    "user_id": "demo_user",
    "top_k": 5
  }'

# Vague/exploratory query
curl -X POST "http://localhost:8000/query/rag" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me about security features",
    "collection_name": "techcorp_docs",
    "user_id": "demo_user",
    "retrieval_strategy": "hybrid"
  }'
```

## Data Characteristics

### Text Documents
- **Total words:** ~8,000
- **Average document length:** 1,300 words
- **Topics:** Enterprise software, cloud computing, security, API documentation
- **Technical level:** Mixed (business overview to technical specifications)

### Content Coverage
The sample dataset covers:
- Company information and background
- Product technical specifications
- Customer success stories and case studies
- API reference and integration guides
- Security architecture and compliance
- Training and educational content

This diverse content allows testing of:
- Factual retrieval
- Technical documentation search
- Multi-document reasoning
- Domain-specific terminology understanding
- Cross-referencing between documents

## Adding Your Own Data

1. **Text files:** Simply add .txt files to `texts/` directory
2. **Images:** Add PNG/JPG/JPEG files to `images/` directory
3. **PDFs:** Add PDF files to `pdfs/` directory

Supported formats:
- Text: .txt, .md
- Images: .png, .jpg, .jpeg
- PDFs: .pdf (text, image, or mixed)

## Testing Recommendations

### Ingestion Testing
1. Upload each document individually to verify processing
2. Test batch upload with multiple files
3. Verify metadata is correctly stored
4. Check vector embeddings are generated

### Retrieval Testing
1. Test specific factual queries
2. Test vague/exploratory queries
3. Test queries across multiple documents
4. Test with different retrieval strategies (dense, sparse, hybrid)
5. Verify relevance scores and source attribution

### Edge Cases
1. Empty queries
2. Very long queries (> 1000 words)
3. Queries with special characters
4. Queries in different languages (if supported)
5. Queries for non-existent information

## Notes

- Text documents are in plain text format for easy ingestion
- All content is fictional and created for demonstration purposes
- Documents are interconnected (e.g., API docs reference the platform)
- Sample data size: ~50KB total (text files only)
- Estimated processing time: < 30 seconds for all text files

## License

Sample data is provided for testing purposes only. Use for demonstration and development of the Multimodal RAG System.
