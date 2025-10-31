# Quick Reference Guide

## 🚀 5-Minute Quick Start

```powershell
# 1. Navigate to project
cd d:\Projects2.0\RAGs\Modality

# 2. Run setup (checks prerequisites, creates config)
.\setup.ps1

# 3. Add at least ONE API key to .env
notepad .env
# Add: GOOGLE_API_KEY=your_key_here (or GROQ_API_KEY, etc.)

# 4. Start all services
docker-compose up -d

# 5. Verify it's working
curl http://localhost:8000/healthz
```

## 📁 Key Files You Need to Know

| File | Purpose | Status |
|------|---------|--------|
| `.env` | Configuration & API keys | ⚠️ ADD YOUR KEYS |
| `README.md` | Complete documentation | ✅ Read this first |
| `IMPLEMENTATION_GUIDE.md` | Copy-paste code templates | ✅ Use for coding |
| `PROJECT_STATUS.md` | Current status & roadmap | ✅ Track progress |
| `DELIVERY_SUMMARY.md` | What you got & how to use it | ✅ Overview |

## 🔧 Common Commands

```powershell
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f api

# Rebuild after code changes
docker-compose build api
docker-compose restart api

# Run tests (after implementing)
docker-compose exec api pytest tests/ -v

# Generate sample data
python scripts\seed_data.py

# Check health
curl http://localhost:8000/healthz
curl http://localhost:8000/ready
```

## 🌐 Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Qdrant** | http://localhost:6333/dashboard | - |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin/admin |
| **Flower** | http://localhost:5555 | - |
| **MongoDB** | mongodb://localhost:27017 | - |
| **Redis** | redis://localhost:6379 | - |

## 📝 Implementation Order

### Step 1: Core Processing (4-6 hours)
Copy from `IMPLEMENTATION_GUIDE.md`:
1. `text_chunker.py` → Token-aware text splitting
2. `pdf_processor.py` → PDF extraction
3. `image_processor.py` → OCR + vision
4. Test each component

### Step 2: Retrieval (3-4 hours)
Copy from `IMPLEMENTATION_GUIDE.md`:
1. `dense_retriever.py` → Vector search
2. `sparse_retriever.py` → BM25 search
3. `hybrid.py` → Combined retrieval
4. `ingest.py` route → Upload endpoint
5. `query.py` route → Search endpoint

### Step 3: Compliance (3-4 hours)
Copy from `IMPLEMENTATION_GUIDE.md`:
1. `pii_detector.py` → PII detection
2. `consent_manager.py` → Consent tracking
3. `audit_log.py` → Audit trail
4. `encryption.py` → Data encryption
5. `dsar.py` route → GDPR/CCPA endpoints

### Step 4: Polish (2-3 hours)
1. Middleware (RequestID, logging, rate-limit)
2. Celery workers
3. Tests
4. Documentation updates

## 🐛 Troubleshooting Quick Fixes

**Problem**: Docker not starting  
**Fix**: Open Docker Desktop and wait for it to fully start

**Problem**: Port already in use  
**Fix**: `docker-compose down` then `docker-compose up -d`

**Problem**: API returning errors  
**Fix**: Check logs with `docker-compose logs -f api`

**Problem**: LLM provider fails  
**Fix**: Check `.env` for API keys, system will auto-fallback

**Problem**: Qdrant connection error  
**Fix**: Wait 30s after starting, check `http://localhost:6333/health`

## 📊 Testing Checklist

```powershell
# 1. Test health
curl http://localhost:8000/healthz

# 2. Test ingestion (after implementing)
curl -X POST http://localhost:8000/ingest `
  -F "file=@samples\text\machine_learning.txt"

# 3. Test query (after implementing)
curl -X POST http://localhost:8000/query `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"machine learning\", \"top_k\": 5}'

# 4. Run unit tests
pytest tests/unit/ -v

# 5. Run integration tests
pytest tests/integration/ -v

# 6. Check coverage
pytest tests/ --cov=src --cov-report=html
```

## 🔑 Environment Variables

**Required** (add at least ONE):
```env
GOOGLE_API_KEY=your_key
GROQ_API_KEY=your_key
OPENAI_API_KEY=your_key
HUGGINGFACEHUB_API_TOKEN=your_token
```

**Optional** (have defaults):
```env
QDRANT_URL=http://qdrant:6333
MONGO_URI=mongodb://mongo:27017
REDIS_URL=redis://redis:6379/0
EMBEDDER_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 📚 File Templates Location

All copy-paste ready code is in:
- **`IMPLEMENTATION_GUIDE.md`** (30+ complete implementations)

Example structure:
```markdown
## 1. Text Chunker (src/core/ingestion/text_chunker.py)
```python
# Complete, working code here
# Just copy and paste!
```

## 🎯 Success Metrics

- [ ] Services start without errors
- [ ] Health endpoint returns 200
- [ ] Can ingest a document
- [ ] Can query and get results
- [ ] Tests pass (>80% coverage)
- [ ] Documentation is up-to-date

## 💡 Pro Tips

1. **Start with text_chunker** - It's the simplest and tests the pipeline
2. **Use API docs** - http://localhost:8000/docs for interactive testing
3. **Check logs frequently** - `docker-compose logs -f api` is your friend
4. **Test incrementally** - Don't implement everything before testing
5. **Read the templates** - They include comments and best practices

## 📞 Where to Get Help

1. **Documentation**: Start with README.md
2. **Implementation**: Check IMPLEMENTATION_GUIDE.md
3. **Status**: See PROJECT_STATUS.md
4. **Errors**: Check logs with docker-compose logs

## 🎉 You're Ready!

Everything you need is in:
1. **Infrastructure**: ✅ Complete (Docker, CI/CD, config)
2. **Core Code**: ✅ Foundation ready (vector DB, LLM, embeddings)
3. **Templates**: ✅ 30+ implementations ready to copy
4. **Documentation**: ✅ 15,000+ words of guides

**Estimated time**: 18-26 hours using the templates

**Start here**: Run `.\setup.ps1` then read `IMPLEMENTATION_GUIDE.md`

---

*Quick Reference v1.0 - For full details see README.md*
