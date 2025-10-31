"""
Conversation memory management for stateless API with Redis backend
"""
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("redis not installed. Install with: pip install redis")

logger = logging.getLogger(__name__)


class ConversationMemory:
    """
    Redis-backed conversation memory for stateless API
    
    Features:
    - Store conversation history per user/session
    - Automatic expiration (TTL)
    - Message history with context
    - Search conversation history
    - Export/import conversations
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        ttl_seconds: int = 3600,
        max_history: int = 10
    ):
        """
        Initialize conversation memory
        
        Args:
            redis_client: Redis client instance
            ttl_seconds: Time-to-live for conversations (default: 1 hour)
            max_history: Maximum messages to keep per conversation
        """
        if not REDIS_AVAILABLE:
            raise ImportError("redis is required. Install with: pip install redis")
        
        self.redis_client = redis_client
        self.ttl_seconds = ttl_seconds
        self.max_history = max_history
        self.key_prefix = "conversation:"
        
        logger.info(f"ConversationMemory initialized (TTL: {ttl_seconds}s, max_history: {max_history})")
    
    def get_conversation_key(self, conversation_id: str) -> str:
        """Generate Redis key for conversation"""
        return f"{self.key_prefix}{conversation_id}"
    
    def create_conversation(self, user_id: str, metadata: Optional[Dict] = None) -> str:
        """
        Create a new conversation
        
        Args:
            user_id: User identifier
            metadata: Optional conversation metadata
            
        Returns:
            Conversation ID
        """
        conversation_id = str(uuid.uuid4())
        
        conversation_data = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "messages": [],
            "metadata": metadata or {}
        }
        
        key = self.get_conversation_key(conversation_id)
        self.redis_client.setex(
            key,
            self.ttl_seconds,
            json.dumps(conversation_data)
        )
        
        # Store user's conversation list
        user_key = f"user_conversations:{user_id}"
        self.redis_client.sadd(user_key, conversation_id)
        self.redis_client.expire(user_key, self.ttl_seconds)
        
        logger.info(f"Created conversation {conversation_id} for user {user_id}")
        return conversation_id
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Add a message to conversation
        
        Args:
            conversation_id: Conversation identifier
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            Success status
        """
        try:
            key = self.get_conversation_key(conversation_id)
            conversation_json = self.redis_client.get(key)
            
            if not conversation_json:
                logger.warning(f"Conversation {conversation_id} not found or expired")
                return False
            
            conversation = json.loads(conversation_json)
            
            # Create message
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            # Add to messages
            conversation["messages"].append(message)
            
            # Trim to max history
            if len(conversation["messages"]) > self.max_history:
                conversation["messages"] = conversation["messages"][-self.max_history:]
            
            # Update timestamp
            conversation["updated_at"] = datetime.utcnow().isoformat()
            
            # Save back to Redis
            self.redis_client.setex(
                key,
                self.ttl_seconds,
                json.dumps(conversation)
            )
            
            logger.debug(f"Added {role} message to conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            return False
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Get full conversation data
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Conversation data or None if not found
        """
        try:
            key = self.get_conversation_key(conversation_id)
            conversation_json = self.redis_client.get(key)
            
            if not conversation_json:
                return None
            
            return json.loads(conversation_json)
            
        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            return None
    
    def get_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get conversation messages
        
        Args:
            conversation_id: Conversation identifier
            limit: Maximum number of messages to return (None = all)
            
        Returns:
            List of messages
        """
        conversation = self.get_conversation(conversation_id)
        
        if not conversation:
            return []
        
        messages = conversation.get("messages", [])
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_context(
        self,
        conversation_id: str,
        max_messages: Optional[int] = None
    ) -> str:
        """
        Get conversation context as formatted string
        
        Args:
            conversation_id: Conversation identifier
            max_messages: Maximum messages to include (None = use default)
            
        Returns:
            Formatted conversation context
        """
        messages = self.get_messages(
            conversation_id,
            limit=max_messages or self.max_history
        )
        
        if not messages:
            return ""
        
        context_lines = []
        for msg in messages:
            role = msg["role"].upper()
            content = msg["content"]
            context_lines.append(f"{role}: {content}")
        
        return "\n".join(context_lines)
    
    def get_user_conversations(self, user_id: str) -> List[str]:
        """
        Get all conversation IDs for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of conversation IDs
        """
        try:
            user_key = f"user_conversations:{user_id}"
            conv_ids = self.redis_client.smembers(user_key)
            return [cid.decode() if isinstance(cid, bytes) else cid for cid in conv_ids]
        except Exception as e:
            logger.error(f"Error getting user conversations: {str(e)}")
            return []
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Success status
        """
        try:
            # Get conversation to find user
            conversation = self.get_conversation(conversation_id)
            
            # Delete conversation
            key = self.get_conversation_key(conversation_id)
            deleted = self.redis_client.delete(key)
            
            # Remove from user's conversation list
            if conversation:
                user_id = conversation.get("user_id")
                if user_id:
                    user_key = f"user_conversations:{user_id}"
                    self.redis_client.srem(user_key, conversation_id)
            
            logger.info(f"Deleted conversation {conversation_id}")
            return deleted > 0
            
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            return False
    
    def clear_user_conversations(self, user_id: str) -> int:
        """
        Clear all conversations for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of conversations deleted
        """
        try:
            conv_ids = self.get_user_conversations(user_id)
            deleted_count = 0
            
            for conv_id in conv_ids:
                if self.delete_conversation(conv_id):
                    deleted_count += 1
            
            # Clear user conversation list
            user_key = f"user_conversations:{user_id}"
            self.redis_client.delete(user_key)
            
            logger.info(f"Cleared {deleted_count} conversations for user {user_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing user conversations: {str(e)}")
            return 0
    
    def extend_ttl(self, conversation_id: str) -> bool:
        """
        Extend conversation TTL
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Success status
        """
        try:
            key = self.get_conversation_key(conversation_id)
            return self.redis_client.expire(key, self.ttl_seconds)
        except Exception as e:
            logger.error(f"Error extending TTL: {str(e)}")
            return False
    
    def export_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Export conversation as JSON-serializable dict
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Conversation data
        """
        return self.get_conversation(conversation_id)
    
    def import_conversation(self, conversation_data: Dict) -> bool:
        """
        Import a conversation from exported data
        
        Args:
            conversation_data: Exported conversation data
            
        Returns:
            Success status
        """
        try:
            conversation_id = conversation_data.get("conversation_id")
            if not conversation_id:
                logger.error("No conversation_id in import data")
                return False
            
            key = self.get_conversation_key(conversation_id)
            self.redis_client.setex(
                key,
                self.ttl_seconds,
                json.dumps(conversation_data)
            )
            
            # Add to user's conversation list
            user_id = conversation_data.get("user_id")
            if user_id:
                user_key = f"user_conversations:{user_id}"
                self.redis_client.sadd(user_key, conversation_id)
                self.redis_client.expire(user_key, self.ttl_seconds)
            
            logger.info(f"Imported conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing conversation: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics
        
        Returns:
            Statistics dictionary
        """
        try:
            # Count conversations
            pattern = f"{self.key_prefix}*"
            conversation_keys = list(self.redis_client.scan_iter(match=pattern, count=100))
            
            return {
                "total_conversations": len(conversation_keys),
                "ttl_seconds": self.ttl_seconds,
                "max_history": self.max_history
            }
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {}


def create_conversation_memory(
    redis_url: str,
    ttl_seconds: int = 3600,
    max_history: int = 10
) -> ConversationMemory:
    """
    Factory function to create ConversationMemory with Redis connection
    
    Args:
        redis_url: Redis connection URL
        ttl_seconds: Time-to-live for conversations
        max_history: Maximum messages per conversation
        
    Returns:
        ConversationMemory instance
    """
    redis_client = redis.from_url(redis_url, decode_responses=True)
    return ConversationMemory(redis_client, ttl_seconds, max_history)
