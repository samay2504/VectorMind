"""
Setup MongoDB user and database for Modality RAG System
Run this script first to create the database and user
"""

from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def setup_mongodb_user():
    """
    Connect to MongoDB and create user with proper permissions
    """
    try:
        # Connect without authentication first (assumes MongoDB is running locally)
        logger.info("🔌 Connecting to MongoDB (no auth)...")
        client = MongoClient('mongodb://localhost:27017/')
        
        # Test connection
        client.admin.command('ping')
        logger.info("✅ Connected to MongoDB successfully!")
        
        # Database and user details
        db_name = "modality_rag"
        username = "samay2504"
        password = "250403"
        
        # Switch to the target database
        db = client[db_name]
        
        logger.info(f"\n📊 Creating database: {db_name}")
        logger.info(f"👤 Creating user: {username}")
        
        # Create user with readWrite role
        try:
            db.command("createUser", username, pwd=password, roles=[
                {"role": "readWrite", "db": db_name},
                {"role": "dbAdmin", "db": db_name}
            ])
            logger.info(f"✅ User '{username}' created successfully!")
        except Exception as e:
            if "already exists" in str(e):
                logger.info(f"ℹ️  User '{username}' already exists")
                # Update password
                try:
                    db.command("updateUser", username, pwd=password)
                    logger.info(f"✅ Password updated for user '{username}'")
                except Exception as update_error:
                    logger.warning(f"⚠️  Could not update password: {update_error}")
            else:
                raise
        
        # Test the new credentials
        logger.info("\n🔐 Testing authentication with new credentials...")
        test_uri = f"mongodb://{username}:{password}@localhost:27017/{db_name}?authSource={db_name}"
        test_client = MongoClient(test_uri)
        test_client.admin.command('ping')
        logger.info("✅ Authentication test successful!")
        test_client.close()
        
        logger.info("\n" + "="*60)
        logger.info("✅ MongoDB Setup Complete!")
        logger.info("="*60)
        logger.info(f"\n📊 Database: {db_name}")
        logger.info(f"👤 User: {username}")
        logger.info(f"🔗 Connection URI:")
        logger.info(f"   mongodb://{username}:{password}@localhost:27017/{db_name}?authSource={db_name}")
        logger.info("\n✨ You can now run: python scripts/init_mongodb.py")
        logger.info("="*60)
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error setting up MongoDB: {e}")
        logger.info("\n💡 Troubleshooting steps:")
        logger.info("1. Make sure MongoDB is running: net start MongoDB")
        logger.info("2. Check if MongoDB allows local connections without auth")
        logger.info("3. Or connect using existing admin credentials")
        return False


if __name__ == "__main__":
    logger.info("🚀 MongoDB User Setup Script")
    logger.info("="*60)
    
    success = setup_mongodb_user()
    
    if not success:
        import sys
        sys.exit(1)
