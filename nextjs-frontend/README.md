# VectorMind - Next.js Frontend

**Copyright © 2025 Samay Mehar. All Rights Reserved.**  
**PROPRIETARY SOFTWARE - PATENT PENDING**

## Overview

Modern, production-ready Next.js frontend for the VectorMind (Modality RAG System). Optimized for Vercel deployment with a beautiful dark-themed UI.

## Features

- ✅ **Dark, Cyber-Themed UI** - Professional gradient design with slate/cyan/emerald colors
- ✅ **Drag-and-Drop Upload** - Support for 8+ file types (PDF, DOCX, XLSX, CSV, TXT, images)
- ✅ **Real-Time Query Interface** - Three query types (Factual, Exploratory, Cross-Modal)
- ✅ **Smart Results Display** - Relevance scores, source attribution, metadata
- ✅ **Responsive Design** - Mobile-first, works on all screen sizes
- ✅ **Type-Safe** - Full TypeScript support
- ✅ **SWR Data Fetching** - Optimistic UI updates and caching
- ✅ **Production-Ready** - Optimized for Vercel deployment

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **Data Fetching:** SWR + Axios
- **Deployment:** Vercel (one-click deploy)

## Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Backend API running (FastAPI on port 8000)

## Installation

```bash
# Install dependencies
npm install

# Or with yarn
yarn install

# Or with pnpm
pnpm install
```

## Configuration

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_COLLECTION_NAME=multimodal_docs
```

For production (Vercel):
- Set `NEXT_PUBLIC_API_URL` to your deployed backend URL
- Example: `https://your-api.railway.app`

## Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

## Build & Deploy

### Local Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

### Deploy to Vercel

#### Option 1: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Deploy to production
vercel --prod
```

#### Option 2: GitHub Integration

1. Push code to GitHub
2. Import project in Vercel dashboard
3. Set environment variables:
   - `NEXT_PUBLIC_API_URL`: Your backend API URL
4. Deploy automatically

## Project Structure

```
nextjs-frontend/
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx             # Main RAG interface
│   ├── globals.css          # Global styles & Tailwind
│   └── api/                 # (Future: API routes)
├── components/
│   ├── upload-section.tsx   # File upload with drag-drop
│   ├── query-input.tsx      # Query interface with types
│   └── results-panel.tsx    # Results display with scores
├── lib/
│   ├── api.ts               # Backend API integration
│   └── utils.ts             # Utility functions
├── public/                  # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.mjs
└── next.config.mjs
```

## API Integration

The frontend connects to the FastAPI backend at these endpoints:

- `POST /api/ingest/upload` - Upload documents
- `POST /api/query/` - Query RAG system
- `GET /api/health` - Health check
- `GET /api/stats` - Collection statistics

## Components

### UploadSection

Drag-and-drop file upload with:
- Multi-file selection
- File type validation
- Upload progress tracking
- Success/error states

### QueryInput

Advanced query interface with:
- Three query types (Factual, Exploratory, Cross-Modal)
- Real-time input validation
- Keyboard shortcuts (Enter to submit)

### ResultsPanel

Results display featuring:
- Relevance score visualization
- Source attribution
- Document metadata
- Loading and empty states

## Customization

### Colors

Edit `tailwind.config.ts` to change the color scheme:

```typescript
theme: {
  extend: {
    colors: {
      // Change primary accent color
      primary: colors.cyan,
      // Change secondary accent color
      secondary: colors.emerald,
    }
  }
}
```

### API URL

Change the backend URL in `.env.local` or `lib/api.ts`:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

## Performance

- ⚡ **Fast:** Next.js 14 with Turbopack
- 🎨 **Optimized:** Tailwind CSS with PurgeCSS
- 📦 **Small Bundle:** Tree-shaking and code splitting
- 🚀 **CDN:** Static assets served from Vercel Edge Network

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### API Connection Issues

```bash
# Check if backend is running
curl http://localhost:8000/api/health

# Verify environment variable
echo $NEXT_PUBLIC_API_URL
```

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Type Errors

```bash
# Check TypeScript configuration
npx tsc --noEmit
```

## License

**Proprietary Software**

Copyright © 2025 Samay Mehar. All Rights Reserved.

This software is protected by copyright and patent law. Unauthorized use, reproduction, or distribution is strictly prohibited.

See [LICENSE](../LICENSE) and [COPYRIGHT_NOTICE.md](../COPYRIGHT_NOTICE.md) for complete legal information.

## Author

**Samay Mehar**  
GitHub: [@samay2504](https://github.com/samay2504)  
Repository: https://github.com/samay2504/VectorMind

## Support

For issues or questions:
1. Check the [main README](../README.md)
2. Review backend API documentation
3. Contact via GitHub issues

---

**Created:** November 1, 2025  
**Version:** 1.0.0  
**Status:** Production-Ready
