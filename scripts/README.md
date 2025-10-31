# MongoDB Setup & Management Scripts

This directory contains utility scripts for setting up and managing the MongoDB database for the Multimodal RAG System.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Scripts Overview](#scripts-overview)
- [Database Structure](#database-structure)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Prerequisites

1. **MongoDB Installed and Running**
   ```powershell
   # Windows - Start MongoDB service
   net start MongoDB
   
   # Check if MongoDB is running
   mongosh --eval "db.version()"
   ```

2. **Python Environment**
   ```powershell
   # Install required packages
   pip install pymongo python-dotenv
   ```

3. **Environment Variables**
   - Ensure `.env` file is configured with MongoDB connection details

---

## ⚡ Quick Start

### Step 1: Create MongoDB User and Database

```powershell
python scripts/setup_mongodb_user.py
```

**What it does:**
- Creates the `modality_rag` database
- Creates user `samay2504` with proper permissions
- Tests authentication
- Provides connection URI

**Output:**
```
✅ MongoDB Setup Complete!
📊 Database: modality_rag
👤 User: samay2504
🔗 Connection URI: mongodb://samay2504:250403@localhost:27017/modality_rag?authSource=modality_rag
```

### Step 2: Initialize Database Structure

```powershell
python scripts/init_mongodb.py
```

**What it does:**
- Creates 6 collections (documents, images, pdfs, conversations, consents, audit_logs)
- Creates optimized indexes
- Inserts sample documents
- Provides detailed summary

**Output:**
```
✅ MongoDB Database Initialization Complete!
📊 Database: modality_rag
📍 Collections created:
   1. documents     - 1 documents, 7 indexes
   2. images        - 1 documents, 6 indexes
   3. pdfs          - 1 documents, 7 indexes
   4. conversations - 0 documents, 5 indexes
   5. consents      - 0 documents, 4 indexes
   6. audit_logs    - 0 documents, 5 indexes
```

### Step 3: View Database (Optional)

```powershell
python scripts/view_mongodb.py
```

**What it does:**
- Shows all collections with statistics
- Displays sample documents
- Shows index details
- Provides collection statistics

---

## 📚 Scripts Overview

### 1. `setup_mongodb_user.py`

**Purpose:** First-time setup of MongoDB user and database

**When to use:**
- Initial setup
- Creating a new database
- Resetting user credentials

**Features:**
- ✅ Creates database and user
- ✅ Sets up proper permissions (readWrite, dbAdmin)
- ✅ Tests authentication
- ✅ Handles existing users gracefully

**Usage:**
```powershell
python scripts/setup_mongodb_user.py
```

---

### 2. `init_mongodb.py`

**Purpose:** Initialize database structure with collections and indexes

**When to use:**
- After creating user (first time)
- When adding new collections
- Resetting database structure

**Features:**
- ✅ Creates 6 specialized collections
- ✅ 34+ optimized indexes
- ✅ Sample data insertion
- ✅ Full-text search setup
- ✅ TTL indexes for conversations
- ✅ Comprehensive error handling

**Collections Created:**

| Collection | Purpose | Sample Count | Indexes |
|------------|---------|--------------|---------|
| `documents` | Text documents | 1 | 7 |
| `images` | Image files | 1 | 6 |
| `pdfs` | PDF documents | 1 | 7 |
| `conversations` | Chat history | 0 | 5 (with TTL) |
| `consents` | GDPR compliance | 0 | 4 |
| `audit_logs` | Security logs | 0 | 5 |

**Usage:**
```powershell
python scripts/init_mongodb.py
```

---

### 3. `view_mongodb.py`

**Purpose:** Interactive database viewer and inspector

**When to use:**
- Checking database state
- Viewing sample documents
- Debugging data issues
- Inspecting indexes

**Features:**
- ✅ Collection statistics
- ✅ Document count per collection
- ✅ Index details with types
- ✅ Sample document display
- ✅ Pretty-printed JSON output

**Usage:**
```powershell
python scripts/view_mongodb.py
```

**Output Example:**
```
📊 MODALITY RAG - MONGODB DATABASE VIEWER
════════════════════════════════════════

📂 Total Collections: 6

1. 📁 DOCUMENTS
   Documents: 1
   Indexes: 7
   Index Details:
      • document_id_1: (document_id: 1) [UNIQUE]
      • user_id_1: (user_id: 1)
      • file_type_1: (file_type: 1)
      • $**_text: Full-text search

   📄 Sample Document:
      {
         "document_id": "sample_text_001",
         "user_id": "user_demo",
         "file_type": "text",
         ...
      }
```

---

## 🗄️ Database Structure

### Documents Collection
```json
{
  "document_id": "unique_doc_id",
  "user_id": "user_identifier",
  "file_name": "document.txt",
  "file_type": "text",
  "content": {
    "raw_text": "...",
    "chunks": [...],
    "summary": "..."
  },
  "metadata": {
    "tags": ["tag1", "tag2"],
    "language": "en"
  },
  "vector_ids": ["vector_id_1"],
  "status": "processed",
  "created_at": "2025-10-31T12:00:00Z"
}
```

### Images Collection
```json
{
  "image_id": "unique_img_id",
  "document_id": "parent_doc_id",
  "image_data": {
    "width": 1920,
    "height": 1080,
    "format": "JPEG"
  },
  "extracted_content": {
    "ocr_text": "...",
    "caption": "...",
    "objects_detected": [...]
  },
  "embeddings": {
    "visual_embedding_id": "...",
    "text_embedding_id": "..."
  }
}
```

### PDFs Collection
```json
{
  "pdf_id": "unique_pdf_id",
  "pdf_metadata": {
    "num_pages": 10,
    "author": "...",
    "title": "..."
  },
  "pages": [
    {
      "page_number": 1,
      "text_content": "...",
      "has_images": true,
      "images": [...]
    }
  ],
  "extracted_content": {
    "full_text": "...",
    "chunks": [...],
    "summary": "..."
  }
}
```

---

## 💡 Usage Examples

### Example 1: Fresh Installation

```powershell
# Step 1: Setup user and database
python scripts/setup_mongodb_user.py

# Step 2: Initialize collections and indexes
python scripts/init_mongodb.py

# Step 3: Verify everything
python scripts/view_mongodb.py
```

### Example 2: Reset Database

```powershell
# In MongoDB shell or compass, drop the database
mongosh
> use modality_rag
> db.dropDatabase()

# Then re-run initialization
python scripts/setup_mongodb_user.py
python scripts/init_mongodb.py
```

### Example 3: Check Database Health

```powershell
# View current state
python scripts/view_mongodb.py

# Check specific collection
mongosh modality_rag --eval "db.documents.countDocuments()"
```

---

## 🔧 Troubleshooting

### Issue 1: Authentication Failed

**Error:**
```
Authentication failed.
```

**Solution:**
1. Run user setup again:
   ```powershell
   python scripts/setup_mongodb_user.py
   ```
2. Check if MongoDB is running:
   ```powershell
   net start MongoDB
   ```

### Issue 2: Connection Refused

**Error:**
```
Connection refused to localhost:27017
```

**Solution:**
1. Start MongoDB service:
   ```powershell
   net start MongoDB
   ```
2. Check MongoDB status:
   ```powershell
   mongosh --eval "db.version()"
   ```

### Issue 3: Collection Already Exists

**Error:**
```
Collection already exists
```

**Solution:**
This is normal! The script handles existing collections gracefully. It will:
- Skip creation
- Update indexes
- Not overwrite existing data

### Issue 4: Permission Denied

**Error:**
```
not authorized on modality_rag
```

**Solution:**
1. Verify user credentials in `.env`:
   ```env
   MONGO_URI=mongodb://samay2504:250403@localhost:27017/modality_rag?authSource=modality_rag
   ```
2. Re-run user setup:
   ```powershell
   python scripts/setup_mongodb_user.py
   ```

---

## 🔍 Advanced Operations

### Manual Database Operations

```powershell
# Connect to MongoDB shell
mongosh mongodb://samay2504:250403@localhost:27017/modality_rag?authSource=modality_rag

# List all collections
show collections

# Count documents in a collection
db.documents.countDocuments()

# View sample document
db.documents.findOne()

# Check indexes
db.documents.getIndexes()

# Delete all documents (keep structure)
db.documents.deleteMany({})

# Drop entire collection
db.documents.drop()
```

### Python Database Operations

```python
from pymongo import MongoClient

# Connect
client = MongoClient("mongodb://samay2504:250403@localhost:27017/modality_rag?authSource=modality_rag")
db = client.modality_rag

# Insert document
db.documents.insert_one({
    "document_id": "my_doc_001",
    "user_id": "user_123",
    "file_type": "text",
    "content": {"raw_text": "Hello World"},
    "status": "processed"
})

# Find documents
docs = db.documents.find({"user_id": "user_123"})
for doc in docs:
    print(doc)

# Update document
db.documents.update_one(
    {"document_id": "my_doc_001"},
    {"$set": {"status": "updated"}}
)

# Delete document
db.documents.delete_one({"document_id": "my_doc_001"})
```

---

## 📊 Performance Tips

1. **Use Indexes Effectively**
   - All primary IDs have unique indexes
   - User IDs are indexed for multi-tenancy
   - Timestamps indexed for chronological queries

2. **Compound Indexes**
   ```javascript
   db.documents.createIndex({ user_id: 1, created_at: -1 })
   ```

3. **Text Search**
   ```javascript
   db.documents.find({ $text: { $search: "multimodal RAG" } })
   ```

4. **TTL for Conversations**
   - Conversations auto-expire after TTL
   - Set `ttl_expires_at` field

---

## 🎯 Next Steps

After setting up MongoDB:

1. ✅ **Run the RAG API**
   ```powershell
   uvicorn src.api.main:app --reload
   ```

2. ✅ **Start Streamlit Frontend**
   ```powershell
   streamlit run frontend/streamlit_app.py
   ```

3. ✅ **Upload Documents**
   - Use the web interface or API
   - Documents will be stored in MongoDB

4. ✅ **Query Your Data**
   - Use natural language queries
   - Get AI-powered responses

---

## 📚 Additional Resources

- [MongoDB Documentation](https://docs.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Atlas (Cloud)](https://www.mongodb.com/cloud/atlas)
- [MongoDB Compass (GUI)](https://www.mongodb.com/products/compass)

---

## 🤝 Contributing

Found an issue or have a suggestion? Please open an issue or submit a pull request!

---

## 📄 License

This project is part of the Multimodal RAG System. See LICENSE for details.

---

**Happy Data Storage! 🎉**
