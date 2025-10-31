"""
View MongoDB Database Structure and Contents
Quick utility to inspect the modality_rag database
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pymongo import MongoClient
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()


def view_database():
    """View database structure and sample data"""
    
    mongo_uri = os.getenv("MONGO_URI", "mongodb://samay2504:250403@localhost:27017/modality_rag?authSource=modality_rag")
    db_name = os.getenv("MONGO_DB", "modality_rag")
    
    print("="*80)
    print("📊 MODALITY RAG - MONGODB DATABASE VIEWER")
    print("="*80)
    
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        print(f"\n🗄️  Database: {db_name}")
        print(f"🔗 Connection: {mongo_uri.replace(mongo_uri.split('@')[0].split('//')[1], '***:***')}")
        
        collections = db.list_collection_names()
        print(f"\n📂 Total Collections: {len(collections)}\n")
        
        for idx, coll_name in enumerate(collections, 1):
            coll = db[coll_name]
            count = coll.count_documents({})
            indexes = list(coll.list_indexes())
            
            print(f"{idx}. 📁 {coll_name.upper()}")
            print(f"   {'─'*70}")
            print(f"   Documents: {count}")
            print(f"   Indexes:   {len(indexes)}")
            
            # Show index details
            print(f"   Index Details:")
            for index in indexes:
                idx_name = index.get('name', 'unknown')
                keys = index.get('key', {})
                unique = index.get('unique', False)
                keys_str = ', '.join([f"{k}: {v}" for k, v in keys.items()])
                unique_str = " [UNIQUE]" if unique else ""
                print(f"      • {idx_name}: ({keys_str}){unique_str}")
            
            # Show sample document if exists
            if count > 0:
                print(f"\n   📄 Sample Document:")
                sample = coll.find_one()
                if sample:
                    # Remove _id for cleaner display
                    if '_id' in sample:
                        del sample['_id']
                    
                    # Pretty print with proper formatting
                    sample_json = json.dumps(sample, default=str, indent=6)
                    for line in sample_json.split('\n'):
                        print(f"      {line}")
            
            print()
        
        print("="*80)
        print("✅ Database inspection complete!")
        print("="*80)
        
        # Collection-specific statistics
        print("\n📊 COLLECTION STATISTICS")
        print("─"*80)
        
        stats = {
            'documents': db['documents'].count_documents({}),
            'images': db['images'].count_documents({}),
            'pdfs': db['pdfs'].count_documents({}),
            'conversations': db['conversations'].count_documents({}),
            'audit_logs': db['audit_logs'].count_documents({}),
            'consents': db['consents'].count_documents({}),
        }
        
        print(f"  📄 Text Documents:     {stats['documents']:>5}")
        print(f"  🖼️  Images:             {stats['images']:>5}")
        print(f"  📕 PDFs:               {stats['pdfs']:>5}")
        print(f"  💬 Conversations:      {stats['conversations']:>5}")
        print(f"  📋 Audit Logs:         {stats['audit_logs']:>5}")
        print(f"  🔒 Consents:           {stats['consents']:>5}")
        print(f"  {'─'*40}")
        print(f"  📊 Total Documents:    {sum(stats.values()):>5}")
        print("="*80)
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    view_database()
