"""
Audit Logger for compliance and security tracking
Records all sensitive operations for audit trails
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pymongo.database import Database

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Types of audit events"""
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    DATA_EXPORT = "data_export"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    CONSENT_GRANTED = "consent_granted"
    CONSENT_WITHDRAWN = "consent_withdrawn"
    DSAR_REQUEST = "dsar_request"
    QUERY_EXECUTED = "query_executed"
    DOCUMENT_INGESTED = "document_ingested"
    AUTHENTICATION_FAILED = "authentication_failed"
    AUTHORIZATION_FAILED = "authorization_failed"
    CONFIGURATION_CHANGED = "configuration_changed"


class AuditSeverity(str, Enum):
    """Severity levels for audit events"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLogger:
    """Audit logging system for compliance"""
    
    def __init__(self, mongo_db: Database, retention_days: int = 2555):
        """
        Initialize audit logger
        
        Args:
            mongo_db: MongoDB database instance
            retention_days: Days to retain audit logs (default: 7 years for compliance)
        """
        self.db = mongo_db
        self.audit_collection = self.db.audit_logs
        self.retention_days = retention_days
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for performance and TTL"""
        try:
            # Performance indexes
            self.audit_collection.create_index("user_id")
            self.audit_collection.create_index("event_type")
            self.audit_collection.create_index("timestamp")
            self.audit_collection.create_index([("user_id", 1), ("timestamp", -1)])
            
            # TTL index for automatic cleanup (optional)
            # self.audit_collection.create_index("timestamp", expireAfterSeconds=self.retention_days*86400)
            
            logger.info("Audit log indexes created")
        except Exception as e:
            logger.warning(f"Failed to create audit indexes: {e}")
    
    def log(
        self,
        event_type: AuditEventType,
        user_id: Optional[str],
        action: str,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True
    ) -> str:
        """
        Log an audit event
        
        Args:
            event_type: Type of event
            user_id: User who performed the action
            action: Description of the action
            resource: Resource affected
            details: Additional details
            severity: Event severity
            ip_address: Client IP address
            user_agent: Client user agent
            success: Whether the action was successful
        
        Returns:
            Audit log ID
        """
        try:
            import uuid
            
            audit_id = str(uuid.uuid4())
            timestamp = datetime.utcnow()
            
            audit_doc = {
                "_id": audit_id,
                "timestamp": timestamp,
                "event_type": event_type.value,
                "severity": severity.value,
                "user_id": user_id,
                "action": action,
                "resource": resource,
                "success": success,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "details": details or {},
                "session_id": details.get("session_id") if details else None
            }
            
            self.audit_collection.insert_one(audit_doc)
            
            # Log to application logger as well
            log_message = f"AUDIT: {event_type.value} - {action} by {user_id or 'anonymous'}"
            if severity == AuditSeverity.CRITICAL:
                logger.critical(log_message)
            elif severity == AuditSeverity.ERROR:
                logger.error(log_message)
            elif severity == AuditSeverity.WARNING:
                logger.warning(log_message)
            else:
                logger.info(log_message)
            
            return audit_id
        
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
            # Audit logging failure should not break the application
            return ""
    
    def log_data_access(
        self,
        user_id: str,
        resource: str,
        query: Optional[str] = None,
        results_count: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> str:
        """Log data access event"""
        return self.log(
            event_type=AuditEventType.DATA_ACCESS,
            user_id=user_id,
            action=f"Accessed data: {resource}",
            resource=resource,
            details={
                "query": query,
                "results_count": results_count
            },
            ip_address=ip_address
        )
    
    def log_data_modification(
        self,
        user_id: str,
        resource: str,
        operation: str,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> str:
        """Log data modification event"""
        return self.log(
            event_type=AuditEventType.DATA_MODIFICATION,
            user_id=user_id,
            action=f"Modified data: {operation}",
            resource=resource,
            details={"changes": changes},
            severity=AuditSeverity.WARNING,
            ip_address=ip_address
        )
    
    def log_data_deletion(
        self,
        user_id: str,
        resource: str,
        reason: Optional[str] = None,
        records_deleted: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> str:
        """Log data deletion event"""
        return self.log(
            event_type=AuditEventType.DATA_DELETION,
            user_id=user_id,
            action=f"Deleted data: {resource}",
            resource=resource,
            details={
                "reason": reason,
                "records_deleted": records_deleted
            },
            severity=AuditSeverity.WARNING,
            ip_address=ip_address
        )
    
    def log_dsar_request(
        self,
        user_id: str,
        request_type: str,
        request_id: str,
        ip_address: Optional[str] = None
    ) -> str:
        """Log DSAR (Data Subject Access Request) event"""
        return self.log(
            event_type=AuditEventType.DSAR_REQUEST,
            user_id=user_id,
            action=f"DSAR request: {request_type}",
            resource=f"dsar/{request_id}",
            details={"request_type": request_type},
            severity=AuditSeverity.WARNING,
            ip_address=ip_address
        )
    
    def log_authentication(
        self,
        user_id: str,
        success: bool,
        method: str = "password",
        ip_address: Optional[str] = None,
        failure_reason: Optional[str] = None
    ) -> str:
        """Log authentication attempt"""
        event_type = AuditEventType.USER_LOGIN if success else AuditEventType.AUTHENTICATION_FAILED
        severity = AuditSeverity.INFO if success else AuditSeverity.WARNING
        
        return self.log(
            event_type=event_type,
            user_id=user_id,
            action=f"Authentication {'succeeded' if success else 'failed'}: {method}",
            details={
                "method": method,
                "failure_reason": failure_reason
            },
            severity=severity,
            ip_address=ip_address,
            success=success
        )
    
    def get_user_audit_trail(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[AuditEventType]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit trail for a user
        
        Args:
            user_id: User identifier
            start_date: Start of date range
            end_date: End of date range
            event_types: Filter by event types
            limit: Maximum number of records
        
        Returns:
            List of audit events
        """
        try:
            query = {"user_id": user_id}
            
            # Date range filter
            if start_date or end_date:
                query["timestamp"] = {}
                if start_date:
                    query["timestamp"]["$gte"] = start_date
                if end_date:
                    query["timestamp"]["$lte"] = end_date
            
            # Event type filter
            if event_types:
                query["event_type"] = {"$in": [et.value for et in event_types]}
            
            logs = list(
                self.audit_collection
                .find(query)
                .sort("timestamp", -1)
                .limit(limit)
            )
            
            # Convert ObjectId to string
            for log in logs:
                log["_id"] = str(log["_id"])
            
            return logs
        
        except Exception as e:
            logger.error(f"Failed to get audit trail: {e}")
            return []
    
    def get_audit_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get audit statistics
        
        Args:
            start_date: Start of date range
            end_date: End of date range
        
        Returns:
            Statistics dictionary
        """
        try:
            match_stage = {}
            
            if start_date or end_date:
                match_stage["timestamp"] = {}
                if start_date:
                    match_stage["timestamp"]["$gte"] = start_date
                if end_date:
                    match_stage["timestamp"]["$lte"] = end_date
            
            pipeline = []
            if match_stage:
                pipeline.append({"$match": match_stage})
            
            pipeline.extend([
                {
                    "$group": {
                        "_id": "$event_type",
                        "count": {"$sum": 1},
                        "successes": {
                            "$sum": {"$cond": ["$success", 1, 0]}
                        },
                        "failures": {
                            "$sum": {"$cond": ["$success", 0, 1]}
                        }
                    }
                }
            ])
            
            results = list(self.audit_collection.aggregate(pipeline))
            
            stats = {
                "total_events": sum(r["count"] for r in results),
                "by_event_type": {
                    r["_id"]: {
                        "count": r["count"],
                        "successes": r["successes"],
                        "failures": r["failures"]
                    }
                    for r in results
                },
                "date_range": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }
            
            return stats
        
        except Exception as e:
            logger.error(f"Failed to get audit statistics: {e}")
            return {"error": str(e)}
    
    def search_audit_logs(
        self,
        search_query: Dict[str, Any],
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Advanced search in audit logs
        
        Args:
            search_query: MongoDB query dictionary
            limit: Maximum number of records
        
        Returns:
            List of matching audit events
        """
        try:
            logs = list(
                self.audit_collection
                .find(search_query)
                .sort("timestamp", -1)
                .limit(limit)
            )
            
            for log in logs:
                log["_id"] = str(log["_id"])
            
            return logs
        
        except Exception as e:
            logger.error(f"Failed to search audit logs: {e}")
            return []
