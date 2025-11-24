# VectorMind - Enhanced Frontends

**Copyright © 2025 Samay Mehar. All Rights Reserved.**

This branch contains production-ready frontend implementations for VectorMind:

## 🎨 Frontends Included

### 1. **Next.js Frontend** (Vercel-Optimized)
- **Location:** `nextjs-frontend/`
- **Tech:** Next.js 14, TypeScript, Tailwind CSS
- **Deploy:** Vercel (one-click)
- **Features:**
  - Dark cyber-themed UI
  - Drag-and-drop upload
  - Real-time query interface
  - Relevance score visualization
  - Full TypeScript support

### 2. **Enhanced Streamlit Frontend**
- **Location:** `frontend/`
- **Tech:** Streamlit, Python
- **Deploy:** Railway, Render, or any Python host
- **Features:**
  - Segmented query types (Factual, Exploratory, Cross-Modal)
  - System statistics dashboard
  - Enhanced results display with metrics
  - Improved upload interface

## 🚀 Quick Start

### Next.js Frontend

```bash
cd nextjs-frontend
npm install
npm run dev
# Open http://localhost:3000
```

### Streamlit Frontend

```bash
cd frontend
streamlit run app_enhanced.py
# Open http://localhost:8501
```

## 📦 Backend Compatibility

Both frontends are fully compatible with the existing FastAPI backend:

- **No backend changes required**
- **All API endpoints work out-of-the-box**
- **Same collection names and parameters**

### Backend Endpoints Used

- `POST /api/ingest/upload` - File upload
- `POST /api/query/` - RAG queries
- `GET /api/health` - Health check
- `GET /api/stats` - Statistics

## 🎯 Production Deployment

### Next.js to Vercel

1. Push code to GitHub
2. Import project in Vercel
3. Set environment variable:
   - `NEXT_PUBLIC_API_URL`: Your backend API URL
4. Deploy automatically

### Streamlit to Railway

1. Create new project from GitHub
2. Select `frontend` directory
3. Add start command: `streamlit run app_enhanced.py`
4. Set environment variable:
   - `PUBLIC_API_URL`: Your backend API URL
5. Deploy

## 📊 Features Comparison

| Feature | Next.js | Streamlit |
|---------|---------|-----------|
| Dark Theme | ✅ | ✅ |
| Drag-Drop Upload | ✅ | ✅ |
| Query Types | ✅ | ✅ |
| Real-Time Stats | ✅ | ✅ |
| Relevance Scores | ✅ | ✅ |
| TypeScript | ✅ | ❌ |
| Python Native | ❌ | ✅ |
| Vercel Optimized | ✅ | ❌ |
| Server-Side Rendering | ✅ | ❌ |

## 🔧 Configuration

### Next.js Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_COLLECTION_NAME=multimodal_docs
```

### Streamlit Environment Variables

```env
PUBLIC_API_URL=http://localhost:8000
```

## 📝 Notes

- Both frontends use the same backend API
- No database or backend modifications needed
- Choose based on your deployment preference
- Next.js offers better performance and SEO
- Streamlit offers faster Python-native development

## 🛡️ Legal

Copyright © 2025 Samay Mehar. All Rights Reserved.

This software is proprietary and protected by copyright and patent law.

See [LICENSE](../LICENSE) for details.

---

**Created:** November 1, 2025  
**Author:** Samay Mehar  
**Repository:** https://github.com/samay2504/VectorMind
