"""
Conversation management API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import redis

from src.core.memory import ConversationMemory, create_conversation_memory
from src.config import settings

router = APIRouter()


class ConversationCreateRequest(BaseModel):
    """Request to create a new conversation"""
    user_id: str = Field(..., description="User identifier")
    metadata: Optional[Dict] = Field(default=None, description="Optional metadata")


class MessageAddRequest(BaseModel):
    """Request to add a message to conversation"""
    conversation_id: str = Field(..., description="Conversation ID")
    role: str = Field(..., description="Message role (user/assistant/system)")
    content: str = Field(..., description="Message content")
    metadata: Optional[Dict] = Field(default=None, description="Optional metadata")


class ConversationResponse(BaseModel):
    """Conversation data response"""
    conversation_id: str
    user_id: str
    created_at: str
    updated_at: str
    messages: List[Dict]
    metadata: Dict


def get_conversation_memory() -> ConversationMemory:
    """Dependency to get conversation memory instance"""
    try:
        return create_conversation_memory(
            redis_url=settings.redis_url,
            ttl_seconds=settings.conversation_ttl_seconds,
            max_history=settings.max_conversation_history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize conversation memory: {str(e)}")


@router.post("/create")
async def create_conversation(
    request: ConversationCreateRequest,
    memory: ConversationMemory = Depends(get_conversation_memory)
):
    """
    Create a new conversation
    
    Args:
        request: Conversation creation request
        memory: Conversation memory instance
        
    Returns:
        Conversation ID
    """
    try:
        conversation_id = memory.create_conversation(
            user_id=request.user_id,
            metadata=request.metadata
        )
        
        return {
            "conversation_id": conversation_id,
            "status": "created",
            "user_id": request.user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message")
async def add_message(
    request: MessageAddRequest,
    memory: ConversationMemory = Depends(get_conversation_memory)
):
    """
    Add a message to conversation
    
    Args:
        request: Message addition request
        memory: Conversation memory instance
        
    Returns:
        Success status
    """
    try:
        success = memory.add_message(
            conversation_id=request.conversation_id,
            role=request.role,
            content=request.content,
            metadata=request.metadata
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {request.conversation_id} not found or expired"
            )
        
        return {
            "status": "success",
            "conversation_id": request.conversation_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    memory: ConversationMemory = Depends(get_conversation_memory)
):
    """
    Get full conversation data
    
    Args:
        conversation_id: Conversation identifier
        memory: Conversation memory instance
        
    Returns:
        Full conversation data
    """
    try:
        conversation = memory.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found or expired"
            )
        
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    limit: Optional[int] = None,
    memory: ConversationMemory = Depends(get_conversation_memory)
):
    """
    Get conversation messages
    
    Args:
        conversation_id: Conversation identifier
        limit: Maximum number of messages to return
        memory: Conversation memory instance
        
    Returns:
        List of messages
    """
    try:
        messages = memory.get_messages(conversation_id, limit=limit)
        
        return {
            "conversation_id": conversation_id,
            "messages": messages,
            "count": len(messages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}/context")
async def get_context(
    conversation_id: str,
    max_messages: Optional[int] = None,
    memory: ConversationMemory = Depends(get_conversation_memory)
):
    """
    Get formatted conversation context
    
    Args:
        conversation_id: Conversation identifier
        max_messages: Maximum messages to include
        memory: Conversation memory instance
        
    Returns:
        Formatted context string
    """
    try:
        context = memory.get_context(conversation_id, max_messages=max_messages)
        
        return {
            "conversation_id": conversation_id,
            "context": context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}")
async def get_user_conversations(
    user_id: str,
    memory: ConversationMemory = Depends(get_conversation_memory)
):
    """
    Get all conversation IDs for a user
    
    Args:
        user_id: User identifier
        memory: Conversation memory instance
        
    Returns:
        List of conversation IDs
    """
    try:
        conversation_ids = memory.get_user_conversations(user_id)
        
        return {
            "user_id": user_id,
            "conversations": conversation_ids,
            "count": len(conversation_ids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    memory: ConversationMemory = Depends(get_conversation_memory)
):
    """
    Delete a conversation
    
    Args:
        conversation_id: Conversation identifier
        memory: Conversation memory instance
        
    Returns:
        Success status
    """
    try:
        success = memory.delete_conversation(conversation_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )
        
        return {
            "status": "deleted",
            "conversation_id": conversation_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/user/{user_id}")
async def clear_user_conversations(
    user_id: str,
    memory: ConversationMemory = Depends(get_conversation_memory)
):
    """
    Clear all conversations for a user
    
    Args:
        user_id: User identifier
        memory: Conversation memory instance
        
    Returns:
        Number of conversations deleted
    """
    try:
        deleted_count = memory.clear_user_conversations(user_id)
        
        return {
            "status": "cleared",
            "user_id": user_id,
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{conversation_id}/extend")
async def extend_conversation_ttl(
    conversation_id: str,
    memory: ConversationMemory = Depends(get_conversation_memory)
):
    """
    Extend conversation TTL
    
    Args:
        conversation_id: Conversation identifier
        memory: Conversation memory instance
        
    Returns:
        Success status
    """
    try:
        success = memory.extend_ttl(conversation_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )
        
        return {
            "status": "extended",
            "conversation_id": conversation_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_memory_stats(
    memory: ConversationMemory = Depends(get_conversation_memory)
):
    """
    Get conversation memory statistics
    
    Args:
        memory: Conversation memory instance
        
    Returns:
        Memory statistics
    """
    try:
        stats = memory.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
