# Multimodal RAG System - Frontend

Production-ready Streamlit frontend for the Multimodal RAG System.

## Features

- 📤 **Document Upload**: Support for multiple file formats (TXT, PDF, Images, DOCX, XLSX)
- 💬 **Interactive Querying**: Real-time RAG queries with conversation memory
- 📊 **Analytics Dashboard**: System health and usage statistics
- 🎨 **Modern UI**: Clean, responsive interface with custom styling
- 🚀 **Easy Deployment**: Ready for Railway, Vercel, or Render

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API (in separate terminal)
uvicorn src.api.main:app --reload

# Start Streamlit frontend
streamlit run frontend/streamlit_app.py
```

Access at: `http://localhost:8501`

### Environment Variables

Create `.env` file or set in your deployment platform:

```bash
PUBLIC_API_URL=http://localhost:8000
CONVERSATION_MEMORY_ENABLED=true
STREAMLIT_SERVER_PORT=8501
```

## Deployment

### Railway

1. Connect your GitHub repository
2. Create new project from repo
3. Add service: `frontend`
4. Set start command: `streamlit run frontend/streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
5. Add environment variables
6. Deploy!

### Render

1. Connect repository
2. Create new Web Service
3. Set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run frontend/streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
4. Add environment variables
5. Deploy!

### Vercel (Serverless)

Vercel is better suited for the FastAPI backend. For frontend, use Railway or Render.

## Usage

### 1. Upload Documents

- Click "Upload Documents" tab
- Choose files (TXT, PDF, Images, DOCX, XLSX)
- Click "Upload All"
- Wait for confirmation

### 2. Query Knowledge Base

- Click "Query & Chat" tab
- Enter your question
- Select retrieval strategy (hybrid recommended)
- Click "Search"
- View answer and sources

### 3. Conversation Mode

- Enable "Use Conversation" checkbox
- Start conversation in sidebar
- Ask follow-up questions
- Context is maintained automatically

### 4. Monitor System

- Click "Analytics" tab
- View system health
- Check component status
- Monitor usage statistics

## Configuration

### Streamlit Config

Edit `frontend/.streamlit/config.toml`:

```toml
[server]
port = 8501
headless = true

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
```

### API Connection

Set `PUBLIC_API_URL` to your API endpoint:

- Local: `http://localhost:8000`
- Railway: `https://your-app.railway.app`
- Render: `https://your-app.onrender.com`

## Features

### Document Upload
- Multi-file upload
- Progress tracking
- Success/error notifications
- Support for all file types

### Query Interface
- Text area for questions
- Retrieval strategy selection
- Top-K results configuration
- Real-time search

### Conversation Memory
- Start/end conversations
- Conversation ID tracking
- Chat history display
- Context preservation

### Analytics
- System health monitoring
- Component status
- Usage statistics
- Real-time updates

## Customization

### Styling

Edit CSS in `streamlit_app.py`:

```python
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)
```

### Layout

Modify tabs and columns:

```python
tab1, tab2, tab3 = st.tabs(["Upload", "Query", "Analytics"])
col1, col2 = st.columns([2, 1])
```

## Troubleshooting

### Cannot Connect to API

**Error**: "Cannot connect to API at http://localhost:8000"

**Solution**:
1. Ensure API is running: `uvicorn src.api.main:app --reload`
2. Check `PUBLIC_API_URL` in environment
3. Verify firewall/network settings

### Upload Fails

**Error**: "Upload failed: 500"

**Solution**:
1. Check file size (max 100MB default)
2. Verify supported file type
3. Check API logs for errors
4. Ensure all services (vector DB, MongoDB, Redis) are running

### Conversation Not Working

**Error**: "Conversation features disabled"

**Solution**:
1. Set `CONVERSATION_MEMORY_ENABLED=true`
2. Ensure Redis is running
3. Restart frontend

## Production Considerations

### Performance

- Use Gunicorn for API (4+ workers)
- Enable Redis caching
- Set appropriate rate limits
- Monitor memory usage

### Security

- Enable HTTPS
- Set proper CORS origins
- Use environment variables for secrets
- Implement authentication (add to API)

### Monitoring

- Check `/ready` endpoint regularly
- Monitor system health dashboard
- Set up alerts for failures
- Track usage metrics

## Advanced Usage

### Custom Retrieval Strategies

```python
# In your code or via API
retrieval_strategy = "hybrid"  # or "dense" or "sparse"
top_k = 5  # number of results
```

### Conversation Export

Implement conversation export/import:

```python
# Get conversation
GET /conversation/{conversation_id}

# Export as JSON
{
  "conversation_id": "...",
  "messages": [...]
}
```

## Support

- **Documentation**: See main `README.md`
- **API Docs**: `http://localhost:8000/docs`
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## License

Same as main project.

---

**Built with Streamlit 🎈**
