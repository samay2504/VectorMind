# Multimodal RAG System

> Production-grade Retrieval-Augmented Generation system with multimodal support (text, images, PDFs), GDPR/CCPA/DPDP compliance, and automatic LLM/vector DB failover.

[![CI](https://github.com/yourusername/multimodal-rag/workflows/CI/badge.svg)](https://github.com/yourusername/multimodal-rag/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 🚀 Features

### Core Capabilities
- **Multimodal Ingestion**: Process text documents, images (PNG/JPG), and PDFs (text/image/mixed)
- **Advanced Retrieval**: Dense, sparse (BM25), and hybrid search with reranking
- **Dual Vector DB**: Qdrant (primary) + Milvus (fallback) with automatic failover
- **LLM Fallback Chain**: Google Gemini → Groq → OpenAI → HuggingFace → Fallback
- **OCR & Vision**: Tesseract OCR + CLIP/BLIP for image understanding
- **Async Processing**: Celery workers for background ingestion and indexing

### Compliance & Security
- **GDPR, CCPA, DPDP**: Full compliance with consent management, DSAR endpoints, audit logs
- **Data Protection**: Field-level encryption, TLS, PII redaction, retention policies
- **RBAC**: JWT-based authentication with role-based access control
- **Privacy by Default**: Consent requirements, data minimization, secure deletion

### Observability
- **Structured Logging**: JSON logs with request tracing and PII redaction
- **Metrics**: Prometheus metrics for latency, errors, and resource usage
- **Monitoring**: Grafana dashboards for real-time observability
- **Tracing**: LLM provider tracking with trace IDs and metadata

## 📋 Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Compliance](#compliance)
- [Contributing](#contributing)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Applications                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                   ┌────────▼────────┐
                   │   FastAPI App   │
                   │  (Gunicorn +    │
                   │   Uvicorn)      │
                   └────┬──────┬─────┘
                        │      │
        ┌───────────────┘      └──────────────┐
        │                                      │
┌───────▼──────────┐                 ┌────────▼─────────┐
│  Vector DB Layer │                 │  Document Store  │
│  ┌─────────────┐ │                 │   (MongoDB)      │
│  │  Qdrant     │◄┼─Failover────┐   └──────────────────┘
│  │  (Primary)  │ │              │
│  └─────────────┘ │          ┌───▼──────────┐
│  ┌─────────────┐ │          │   Milvus     │
│  │   Cache     │ │          │  (Fallback)  │
│  │   (Redis)   │ │          └──────────────┘
│  └─────────────┘ │
└──────────────────┘
        │
┌───────▼────────────────────────────────────────┐
│           Processing Pipeline                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │   OCR    │  │  Vision  │  │  Embeddings  │ │
│  │(Tesseract│  │  (CLIP)  │  │(Transformers)│ │
│  └──────────┘  └──────────┘  └──────────────┘ │
└────────────────────────────────────────────────┘
        │
┌───────▼────────────────────────────────────────┐
│         LLM Provider Chain                      │
│  Gemini → Groq → OpenAI → HuggingFace → Static │
└────────────────────────────────────────────────┘
```

### Component Overview

| Component | Technology | Purpose |
|-----------|------------|---------|
| API | FastAPI + Uvicorn | Async REST endpoints |
| Vector DB (Primary) | Qdrant | Fast similarity search |
| Vector DB (Fallback) | Milvus | Automatic failover |
| Document Store | MongoDB | Original documents + metadata |
| Cache | Redis | Embedding cache, query results |
| Embeddings | Sentence Transformers | Text → vector conversion |
| OCR | Tesseract | Image → text extraction |
| Vision | CLIP/BLIP | Image → embeddings |
| LLM | Multi-provider | Query augmentation |
| Queue | Celery + Redis | Async processing |
| Metrics | Prometheus + Grafana | Observability |

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose** (recommended)
- **Python 3.10+** (for local development)
- **Tesseract OCR** (for OCR functionality)
- At least one LLM API key (Google/Groq/OpenAI/HuggingFace)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/multimodal-rag.git
cd multimodal-rag

# Copy environment file and configure
cp .env.example .env
# Edit .env and add your API keys

# Start all services
docker-compose up -d

# Check health
curl http://localhost:8000/healthz

# View logs
docker-compose logs -f api
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract
# Ubuntu/Debian: sudo apt-get install tesseract-ocr poppler-utils
# macOS: brew install tesseract poppler
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

# Set up services (using Docker)
docker-compose up -d qdrant mongo redis

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run development server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Quick Test

```bash
# Ingest a document
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.pdf" \
  -F "source=test" \
  -F 'metadata={"consent":true}'

# Query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "top_k": 5,
    "strategy": "hybrid"
  }'
```

## ⚙️ Configuration

### Environment Variables

Key configuration options (see `.env.example` for all options):

```env
# Vector Database
QDRANT_URL=http://qdrant:6333
MILVUS_URL=localhost:19530  # Optional fallback

# LLM Providers (at least one required)
GOOGLE_API_KEY=your_google_key
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
HUGGINGFACEHUB_API_TOKEN=your_hf_token

# Provider preference order
LLM_PROVIDER_PREFERENCE=google_genai,groq,openai,huggingface,fallback

# Embeddings
EMBEDDER_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDER_DEVICE=cpu  # or 'cuda' for GPU

# Security
JWT_SECRET=your-secret-key-here
ENCRYPTION_KEY=your-32-byte-encryption-key
ENABLE_CONSENT_REQUIREMENT=true
ENABLE_PII_REDACTION=true

# Compliance
RETENTION_DAYS=90
AUDIT_LOG_ENABLED=true
```

### Vector Database Configuration

#### Qdrant (Primary)
- **Type**: In-memory + persistent storage
- **Index**: HNSW for fast similarity search
- **Distance**: Cosine similarity
- **Automatic** failover to Milvus after 3 failures

#### Milvus (Fallback)
- **Type**: Optional distributed vector DB
- **Index**: HNSW with IVF_FLAT fallback
- **Requires**: etcd + MinIO (included in docker-compose, commented out)

To enable Milvus fallback, uncomment the Milvus section in `docker-compose.yml`.

## 📚 API Documentation

### Core Endpoints

#### Ingestion

**POST /ingest**

Upload and process documents.

```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "source=user_upload" \
  -F 'metadata={"category":"research","consent":true}'
```

Response:
```json
{
  "doc_id": "uuid-here",
  "ingestion_job_id": "job-uuid",
  "status": "processing",
  "message": "Document queued for processing"
}
```

**GET /ingest/status/{job_id}**

Check ingestion job status.

#### Query

**POST /query**

Search for relevant documents.

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning algorithms",
    "top_k": 5,
    "strategy": "hybrid",
    "rerank": true,
    "filters": {"category": "research"}
  }'
```

Response:
```json
{
  "results": [
    {
      "doc_id": "uuid",
      "chunk_id": "chunk-0",
      "page": 1,
      "text": "Machine learning algorithms...",
      "score": 0.92,
      "source": "document.pdf",
      "highlight": "...machine learning algorithms..."
    }
  ],
  "query": "machine learning algorithms",
  "strategy": "hybrid",
  "latency_ms": 245,
  "trace_id": "trace-uuid"
}
```

**Retrieval Strategies:**
- `dense`: Pure vector similarity search
- `sparse`: BM25 keyword search
- `hybrid`: Combined dense + sparse with score fusion

#### DSAR (Data Subject Access Rights)

**POST /dsar/export**

Export all data for a subject.

```bash
curl -X POST "http://localhost:8000/dsar/export" \
  -H "Content-Type: application/json" \
  -d '{"subject_identifier": "user@example.com"}'
```

**POST /dsar/delete**

Delete or anonymize subject data.

```bash
curl -X POST "http://localhost:8000/dsar/delete" \
  -H "Content-Type: application/json" \
  -d '{"subject_identifier": "user@example.com", "reason": "User request"}'
```

#### Health & Monitoring

**GET /healthz** - Basic health check  
**GET /ready** - Readiness probe  
**GET /metrics** - Prometheus metrics

### Interactive API Docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛠️ Development

### Project Structure

```
multimodal-rag/
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── main.py            # App factory
│   │   ├── dependencies.py    # Dependency injection
│   │   ├── routes/
│   │   │   ├── ingest.py      # Document ingestion
│   │   │   ├── query.py       # Search/retrieval
│   │   │   ├── dsar.py        # GDPR/CCPA endpoints
│   │   │   └── health.py      # Health checks
│   │   └── middleware/
│   │       ├── request_id.py  # Request tracing
│   │       ├── logging.py     # Log redaction
│   │       └── rate_limit.py  # Rate limiting
│   ├── core/
│   │   ├── vector_adapter.py  # Qdrant/Milvus adapter
│   │   ├── ingestion/
│   │   │   ├── pdf_processor.py
│   │   │   ├── image_processor.py
│   │   │   ├── text_chunker.py
│   │   │   └── embedder.py
│   │   ├── retrieval/
│   │   │   ├── dense_retriever.py
│   │   │   ├── sparse_retriever.py
│   │   │   └── hybrid.py
│   │   ├── llm/
│   │   │   └── provider.py    # Multi-provider LLM
│   │   └── security/
│   │       ├── pii_detector.py
│   │       ├── consent_manager.py
│   │       ├── audit_log.py
│   │       └── encryption.py
│   ├── workers/
│   │   ├── celery_app.py      # Celery configuration
│   │   └── tasks.py           # Background tasks
│   ├── config.py              # Settings management
│   └── utils.py               # Utilities
├── tests/
│   ├── unit/
│   └── integration/
├── samples/                    # Sample documents
├── scripts/
│   ├── demo_run.sh            # Demo script
│   └── seed_data.py           # Data seeding
├── infra/
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── grafana/
│       ├── dashboards/
│       └── datasources/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── Makefile
└── README.md
```

### Common Tasks

```bash
# Run tests
make test

# Run specific test file
pytest tests/unit/test_embedder.py -v

# Lint code
make lint

# Format code
make format

# Build Docker image
make docker-build

# View logs
make docker-logs

# Restart services
make docker-restart
```

### Adding New Document Types

1. Create processor in `src/core/ingestion/`
2. Register in ingestion pipeline
3. Add tests in `tests/unit/ingestion/`
4. Update API documentation

Example:
```python
# src/core/ingestion/docx_processor.py
class DOCXProcessor:
    def process(self, file_path: str) -> Dict[str, Any]:
        # Extract text and images from DOCX
        pass
```

## 🧪 Testing

### Run All Tests

```bash
# Unit + integration tests
pytest tests/ -v --cov=src --cov-report=html

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Specific test file
pytest tests/unit/test_vector_adapter.py -v -k "test_qdrant_search"
```

### Test Coverage

Current coverage target: **>80%**

View coverage report: `open htmlcov/index.html`

### Test Checklist

- [x] Ingest plain text documents
- [x] Ingest images with OCR
- [x] Ingest mixed PDFs
- [x] Dense retrieval
- [x] Sparse retrieval (BM25)
- [x] Hybrid retrieval with reranking
- [x] Cross-modal queries
- [x] DSAR export
- [x] DSAR deletion with audit
- [x] Qdrant → Milvus failover
- [x] LLM provider failover chain
- [x] PII redaction in logs
- [x] Rate limiting

### Integration Tests

Integration tests use `testcontainers` to spin up real services:

```python
# tests/integration/test_ingestion_e2e.py
def test_ingest_and_query_pdf(test_client, qdrant_container):
    # Upload PDF
    response = test_client.post("/ingest", files={"file": pdf_file})
    doc_id = response.json()["doc_id"]
    
    # Query
    response = test_client.post("/query", json={"query": "test"})
    assert len(response.json()["results"]) > 0
```

## 🚀 Deployment

### Docker Compose (Single Host)

```bash
# Production mode
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Kubernetes

```bash
# Apply manifests
kubectl apply -f infra/k8s/

# Check status
kubectl get pods -n multimodal-rag

# Scale workers
kubectl scale deployment celery-worker --replicas=5 -n multimodal-rag
```

### Environment-Specific Configuration

- **Development**: `.env` with debug enabled
- **Staging**: Separate `.env.staging` with test API keys
- **Production**: Use secrets management (HashiCorp Vault, AWS Secrets Manager)

### Performance Tuning

#### Qdrant HNSW Parameters
```python
# In vector_adapter.py
hnsw_config = {
    "m": 16,  # Number of connections per layer
    "ef_construct": 200,  # Build time accuracy
}
```

#### Redis Caching
```env
REDIS_TTL=3600  # Cache TTL in seconds
REDIS_MAX_CONNECTIONS=50
```

#### Worker Scaling
```bash
# Scale celery workers
docker-compose up --scale celery-worker=5 -d
```

### Monitoring

**Prometheus**: `http://localhost:9090`  
**Grafana**: `http://localhost:3000` (admin/admin)  
**Flower (Celery)**: `http://localhost:5555`

Key metrics:
- `api_request_duration_seconds` - Request latency
- `qdrant_search_duration_seconds` - Vector search time
- `llm_invocation_duration_seconds` - LLM latency
- `celery_task_duration_seconds` - Background task time

## 🔒 Compliance

### GDPR Compliance Checklist

- [x] **Lawful basis**: Consent capture and storage
- [x] **Data minimization**: Only necessary data collected
- [x] **Purpose limitation**: Data used only for stated purpose
- [x] **Storage limitation**: Automatic data deletion after retention period
- [x] **Right to access**: DSAR export endpoint
- [x] **Right to erasure**: DSAR deletion endpoint
- [x] **Data portability**: Export in JSON format
- [x] **Security**: Encryption at rest and in transit
- [x] **Accountability**: Comprehensive audit logs
- [x] **Privacy by design**: Default privacy settings

### CCPA Compliance

- [x] **Right to know**: Data export functionality
- [x] **Right to delete**: Deletion with audit trail
- [x] **Right to opt-out**: Consent management
- [x] **Non-discrimination**: No service degradation for opt-out
- [x] **Notice at collection**: Consent metadata
- [x] **Disclosure of data practices**: API documentation

### India DPDP Act 2023

- [x] **Consent**: Explicit consent before processing
- [x] **Purpose limitation**: Clear purpose declaration
- [x] **Data minimization**: Only necessary data
- [x] **Storage limitation**: Retention policy
- [x] **Data security**: Encryption and access control
- [x] **Right to correction**: Update endpoints
- [x] **Right to erasure**: Deletion functionality
- [x] **Breach notification**: Logging and alerting

### Security Best Practices

1. **TLS/SSL**: Enable TLS in production (`TLS_ENABLED=true`)
2. **API Keys**: Never commit to git, use `.env`
3. **JWT Secrets**: Use strong random strings
4. **Field Encryption**: Enable for PII fields
5. **Regular Updates**: Keep dependencies updated
6. **Audit Logs**: Review regularly for suspicious activity
7. **Rate Limiting**: Prevent abuse
8. **Input Validation**: All endpoints validate input

### Data Retention Policy

```env
RETENTION_DAYS=90  # Configurable retention period
```

Automatic purge job runs daily to delete expired data.

### PII Handling

PII is automatically detected and handled:
- **Logs**: PII redacted before logging
- **Storage**: PII fields encrypted at rest
- **Deletion**: Secure deletion or anonymization
- **Access**: Logged in audit trail

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Run linters (`make lint`)
6. Commit (`git commit -m 'Add amazing feature'`)
7. Push (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style

- **Black** for formatting (line length: 100)
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking
- **Pre-commit hooks** enforced

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📖 API Examples

### Example 1: Ingest and Query PDF

```python
import requests

# Upload PDF
files = {"file": open("research_paper.pdf", "rb")}
data = {"source": "research", "metadata": '{"consent": true, "category": "AI"}'}
response = requests.post("http://localhost:8000/ingest", files=files, data=data)
doc_id = response.json()["doc_id"]

# Query
payload = {
    "query": "What are the main findings?",
    "top_k": 5,
    "strategy": "hybrid",
    "rerank": true
}
response = requests.post("http://localhost:8000/query", json=payload)
print(response.json())
```

### Example 2: Cross-Modal Search

```python
# Upload image
files = {"file": open("chart.png", "rb")}
requests.post("http://localhost:8000/ingest", files=files)

# Search for related content
payload = {"query": "sales data visualization"}
response = requests.post("http://localhost:8000/query", json=payload)
```

### Example 3: DSAR Request

```python
# Export user data
payload = {"subject_identifier": "user@example.com"}
response = requests.post("http://localhost:8000/dsar/export", json=payload)
download_url = response.json()["download_url"]

# Delete user data
payload = {"subject_identifier": "user@example.com", "reason": "User request"}
requests.post("http://localhost:8000/dsar/delete", json=payload)
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: Qdrant connection refused  
**Solution**: Ensure Qdrant is running: `docker-compose up -d qdrant`

**Issue**: OCR fails  
**Solution**: Install Tesseract: `sudo apt-get install tesseract-ocr`

**Issue**: CUDA out of memory  
**Solution**: Set `EMBEDDER_DEVICE=cpu` in `.env`

**Issue**: LLM quota exceeded  
**Solution**: System automatically fails over to next provider

**Issue**: Slow query performance  
**Solution**: Enable Redis caching, tune HNSW parameters

### Debugging

```bash
# Check service health
curl http://localhost:8000/healthz

# Check vector DB health
curl http://localhost:6333/health

# View API logs
docker-compose logs -f api

# View worker logs
docker-compose logs -f celery-worker

# Check Redis
docker-compose exec redis redis-cli ping

# Check MongoDB
docker-compose exec mongo mongosh --eval "db.stats()"
```

## 📊 Performance

### Benchmarks (on modest hardware)

| Operation | Median Latency | P95 Latency |
|-----------|----------------|-------------|
| PDF Ingestion (10 pages) | 3.2s | 5.1s |
| Image OCR | 1.8s | 2.9s |
| Dense Search (cached) | 120ms | 180ms |
| Dense Search (uncached) | 450ms | 720ms |
| Hybrid Search | 680ms | 1.2s |
| DSAR Export | 2.1s | 3.5s |

### Optimization Tips

1. **Enable caching**: Set appropriate `REDIS_TTL`
2. **Batch processing**: Use bulk_upsert for multiple documents
3. **GPU acceleration**: Set `EMBEDDER_DEVICE=cuda`
4. **Async workers**: Scale celery workers horizontally
5. **HNSW tuning**: Adjust `ef_construct` and `m` parameters

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Qdrant** for high-performance vector search
- **LangChain** for LLM abstractions
- **Sentence Transformers** for embeddings
- **FastAPI** for the web framework
- **Tesseract** for OCR capabilities

## 📧 Support

- **Documentation**: [Full API docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/yourusername/multimodal-rag/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/multimodal-rag/discussions)

---

**Built with ❤️ by Samay Mehar**
