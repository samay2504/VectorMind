"""
Consent Manager for GDPR/CCPA/DPDP compliance
Tracks user consents for data processing
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from pymongo.database import Database

logger = logging.getLogger(__name__)


class ConsentType(str, Enum):
    """Types of consent"""
    DATA_PROCESSING = "data_processing"
    DATA_STORAGE = "data_storage"
    DATA_SHARING = "data_sharing"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    PROFILING = "profiling"


class ConsentStatus(str, Enum):
    """Consent status"""
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class ConsentManager:
    """Manage user consents for compliance"""
    
    def __init__(self, mongo_db: Database, consent_expiry_days: int = 365):
        """
        Initialize consent manager
        
        Args:
            mongo_db: MongoDB database instance
            consent_expiry_days: Days until consent expires (default: 1 year)
        """
        self.db = mongo_db
        self.consents_collection = self.db.consents
        self.consent_expiry_days = consent_expiry_days
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for performance"""
        try:
            self.consents_collection.create_index("user_id")
            self.consents_collection.create_index([("user_id", 1), ("consent_type", 1)])
            self.consents_collection.create_index("granted_at")
            self.consents_collection.create_index("expires_at")
            logger.info("Consent collection indexes created")
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    def grant_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None,
        expiry_days: Optional[int] = None
    ) -> str:
        """
        Record user consent
        
        Args:
            user_id: User identifier
            consent_type: Type of consent
            purpose: Purpose of data processing
            metadata: Additional metadata
            expiry_days: Custom expiry (overrides default)
        
        Returns:
            Consent ID
        """
        try:
            import uuid
            
            consent_id = str(uuid.uuid4())
            granted_at = datetime.utcnow()
            expires_at = granted_at + timedelta(days=expiry_days or self.consent_expiry_days)
            
            consent_doc = {
                "_id": consent_id,
                "user_id": user_id,
                "consent_type": consent_type.value,
                "status": ConsentStatus.GRANTED.value,
                "purpose": purpose,
                "granted_at": granted_at,
                "expires_at": expires_at,
                "withdrawn_at": None,
                "metadata": metadata or {},
                "version": "1.0",
                "ip_address": metadata.get("ip_address") if metadata else None,
                "user_agent": metadata.get("user_agent") if metadata else None
            }
            
            self.consents_collection.insert_one(consent_doc)
            logger.info(f"Consent granted: {consent_id} for user {user_id}")
            
            return consent_id
        
        except Exception as e:
            logger.error(f"Failed to grant consent: {e}")
            raise
    
    def withdraw_consent(self, user_id: str, consent_id: str, reason: Optional[str] = None) -> bool:
        """
        Withdraw user consent
        
        Args:
            user_id: User identifier
            consent_id: Consent ID to withdraw
            reason: Optional reason for withdrawal
        
        Returns:
            True if successful
        """
        try:
            result = self.consents_collection.update_one(
                {"_id": consent_id, "user_id": user_id},
                {
                    "$set": {
                        "status": ConsentStatus.WITHDRAWN.value,
                        "withdrawn_at": datetime.utcnow(),
                        "withdrawal_reason": reason
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Consent withdrawn: {consent_id} for user {user_id}")
                return True
            else:
                logger.warning(f"Consent not found: {consent_id}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to withdraw consent: {e}")
            return False
    
    def check_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        auto_expire: bool = True
    ) -> bool:
        """
        Check if user has valid consent
        
        Args:
            user_id: User identifier
            consent_type: Type of consent to check
            auto_expire: Automatically expire old consents
        
        Returns:
            True if consent is valid
        """
        try:
            # Find most recent consent of this type
            consent = self.consents_collection.find_one(
                {
                    "user_id": user_id,
                    "consent_type": consent_type.value
                },
                sort=[("granted_at", -1)]
            )
            
            if not consent:
                return False
            
            # Check status
            if consent["status"] == ConsentStatus.WITHDRAWN.value:
                return False
            
            # Check expiry
            if consent["expires_at"] < datetime.utcnow():
                if auto_expire:
                    self.consents_collection.update_one(
                        {"_id": consent["_id"]},
                        {"$set": {"status": ConsentStatus.EXPIRED.value}}
                    )
                return False
            
            return consent["status"] == ConsentStatus.GRANTED.value
        
        except Exception as e:
            logger.error(f"Failed to check consent: {e}")
            return False
    
    def get_user_consents(self, user_id: str, active_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get all consents for a user
        
        Args:
            user_id: User identifier
            active_only: Only return active (granted) consents
        
        Returns:
            List of consent records
        """
        try:
            query = {"user_id": user_id}
            
            if active_only:
                query["status"] = ConsentStatus.GRANTED.value
                query["expires_at"] = {"$gt": datetime.utcnow()}
            
            consents = list(self.consents_collection.find(query).sort("granted_at", -1))
            
            # Convert ObjectId to string
            for consent in consents:
                consent["_id"] = str(consent["_id"])
            
            return consents
        
        except Exception as e:
            logger.error(f"Failed to get user consents: {e}")
            return []
    
    def get_consent_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get summary of user's consent status
        
        Args:
            user_id: User identifier
        
        Returns:
            Summary dictionary
        """
        consents = self.get_user_consents(user_id)
        
        summary = {
            "user_id": user_id,
            "total_consents": len(consents),
            "active_consents": 0,
            "withdrawn_consents": 0,
            "expired_consents": 0,
            "by_type": {}
        }
        
        for consent in consents:
            status = consent["status"]
            consent_type = consent["consent_type"]
            
            if status == ConsentStatus.GRANTED.value and consent["expires_at"] > datetime.utcnow():
                summary["active_consents"] += 1
                summary["by_type"][consent_type] = "active"
            elif status == ConsentStatus.WITHDRAWN.value:
                summary["withdrawn_consents"] += 1
                if consent_type not in summary["by_type"]:
                    summary["by_type"][consent_type] = "withdrawn"
            elif status == ConsentStatus.EXPIRED.value or consent["expires_at"] <= datetime.utcnow():
                summary["expired_consents"] += 1
                if consent_type not in summary["by_type"]:
                    summary["by_type"][consent_type] = "expired"
        
        return summary
    
    def bulk_grant_consents(
        self,
        user_id: str,
        consent_types: List[ConsentType],
        purpose: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Grant multiple consents at once
        
        Args:
            user_id: User identifier
            consent_types: List of consent types to grant
            purpose: Purpose of data processing
            metadata: Additional metadata
        
        Returns:
            List of consent IDs
        """
        consent_ids = []
        
        for consent_type in consent_types:
            try:
                consent_id = self.grant_consent(user_id, consent_type, purpose, metadata)
                consent_ids.append(consent_id)
            except Exception as e:
                logger.error(f"Failed to grant consent {consent_type}: {e}")
        
        return consent_ids
    
    def expire_old_consents(self, batch_size: int = 1000) -> int:
        """
        Batch expire old consents
        
        Args:
            batch_size: Number of records to process
        
        Returns:
            Number of expired consents
        """
        try:
            result = self.consents_collection.update_many(
                {
                    "status": ConsentStatus.GRANTED.value,
                    "expires_at": {"$lt": datetime.utcnow()}
                },
                {"$set": {"status": ConsentStatus.EXPIRED.value}},
                limit=batch_size
            )
            
            expired_count = result.modified_count
            if expired_count > 0:
                logger.info(f"Expired {expired_count} old consents")
            
            return expired_count
        
        except Exception as e:
            logger.error(f"Failed to expire consents: {e}")
            return 0
    
    def require_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        auto_request: bool = False
    ) -> bool:
        """
        Decorator-friendly consent check
        
        Args:
            user_id: User identifier
            consent_type: Required consent type
            auto_request: If True, create a consent request
        
        Returns:
            True if consent is valid
        """
        has_consent = self.check_consent(user_id, consent_type)
        
        if not has_consent and auto_request:
            logger.info(f"Consent required but not found: {consent_type} for {user_id}")
            # Could trigger email/notification here
        
        return has_consent
