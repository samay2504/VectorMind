"""
DSAR (Data Subject Access Request) endpoints for GDPR/CCPA/DPDP compliance
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from pymongo.database import Database
from datetime import datetime

from src.api.dependencies import get_mongo_db, get_vector_manager
from src.core.vector_adapter import VectorDBManager

logger = logging.getLogger(__name__)
router = APIRouter()


class DSARRequest(BaseModel):
    """DSAR request model"""
    user_id: str
    email: EmailStr
    request_type: str  # "access", "delete", "export", "rectify"
    reason: Optional[str] = None


class DSARResponse(BaseModel):
    """DSAR response model"""
    request_id: str
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None


@router.post("/request", response_model=DSARResponse)
async def create_dsar_request(
    request: DSARRequest,
    mongo_db: Database = Depends(get_mongo_db)
) -> DSARResponse:
    """
    Create a new DSAR request
    
    Args:
        request: DSAR request details
        mongo_db: MongoDB database
    
    Returns:
        DSAR response with request ID and status
    """
    try:
        import uuid
        request_id = str(uuid.uuid4())
        
        # Store DSAR request
        dsar_doc = {
            "_id": request_id,
            "user_id": request.user_id,
            "email": request.email,
            "request_type": request.request_type,
            "reason": request.reason,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        mongo_db.dsar_requests.insert_one(dsar_doc)
        
        return DSARResponse(
            request_id=request_id,
            status="pending",
            message=f"DSAR request created. Request ID: {request_id}",
            data={"request_type": request.request_type}
        )
    
    except Exception as e:
        logger.error(f"DSAR request creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/request/{request_id}", response_model=DSARResponse)
async def get_dsar_status(
    request_id: str,
    mongo_db: Database = Depends(get_mongo_db)
) -> DSARResponse:
    """Get DSAR request status"""
    dsar = mongo_db.dsar_requests.find_one({"_id": request_id})
    if not dsar:
        raise HTTPException(status_code=404, detail="DSAR request not found")
    
    return DSARResponse(
        request_id=request_id,
        status=dsar.get("status", "unknown"),
        message=f"DSAR request status: {dsar.get('status')}",
        data={
            "request_type": dsar.get("request_type"),
            "created_at": str(dsar.get("created_at")),
            "updated_at": str(dsar.get("updated_at"))
        }
    )


@router.post("/access/{user_id}")
async def access_user_data(
    user_id: str,
    mongo_db: Database = Depends(get_mongo_db)
) -> Dict[str, Any]:
    """
    Get all data for a user (GDPR Article 15 - Right to Access)
    
    Args:
        user_id: User identifier
        mongo_db: MongoDB database
    
    Returns:
        All user data
    """
    try:
        # Find all documents associated with user
        documents = list(mongo_db.documents.find({"metadata.user_id": user_id}))
        
        # Find all queries
        queries = list(mongo_db.query_history.find({"user_id": user_id}))
        
        # Find consents
        consents = list(mongo_db.consents.find({"user_id": user_id}))
        
        # Sanitize MongoDB ObjectIds
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        for query in queries:
            query["_id"] = str(query["_id"])
        for consent in consents:
            consent["_id"] = str(consent["_id"])
        
        return {
            "user_id": user_id,
            "documents": documents,
            "queries": queries,
            "consents": consents,
            "total_documents": len(documents),
            "total_queries": len(queries)
        }
    
    except Exception as e:
        logger.error(f"Data access failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{user_id}")
async def delete_user_data(
    user_id: str,
    mongo_db: Database = Depends(get_mongo_db),
    vector_manager: VectorDBManager = Depends(get_vector_manager)
) -> Dict[str, Any]:
    """
    Delete all data for a user (GDPR Article 17 - Right to Erasure)
    
    Args:
        user_id: User identifier
        mongo_db: MongoDB database
        vector_manager: Vector DB manager
    
    Returns:
        Deletion confirmation
    """
    try:
        # Delete from MongoDB
        doc_result = mongo_db.documents.delete_many({"metadata.user_id": user_id})
        query_result = mongo_db.query_history.delete_many({"user_id": user_id})
        consent_result = mongo_db.consents.delete_many({"user_id": user_id})
        
        # Delete from vector DB
        try:
            vector_manager.delete_by_filter(
                collection_name="default",
                filter_dict={"user_id": user_id}
            )
        except Exception as e:
            logger.warning(f"Vector deletion failed: {e}")
        
        # Log the deletion (audit trail)
        mongo_db.audit_logs.insert_one({
            "user_id": user_id,
            "action": "data_deletion",
            "timestamp": datetime.utcnow(),
            "deleted_counts": {
                "documents": doc_result.deleted_count,
                "queries": query_result.deleted_count,
                "consents": consent_result.deleted_count
            }
        })
        
        return {
            "user_id": user_id,
            "status": "deleted",
            "deleted_counts": {
                "documents": doc_result.deleted_count,
                "queries": query_result.deleted_count,
                "consents": consent_result.deleted_count
            }
        }
    
    except Exception as e:
        logger.error(f"Data deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{user_id}")
async def export_user_data(
    user_id: str,
    mongo_db: Database = Depends(get_mongo_db)
) -> Dict[str, Any]:
    """
    Export all user data in portable format (GDPR Article 20 - Right to Data Portability)
    
    Args:
        user_id: User identifier
        mongo_db: MongoDB database
    
    Returns:
        Exportable user data
    """
    # Reuse access endpoint
    data = await access_user_data(user_id, mongo_db)
    
    # Add export metadata
    data["export_date"] = datetime.utcnow().isoformat()
    data["format"] = "JSON"
    
    return data
