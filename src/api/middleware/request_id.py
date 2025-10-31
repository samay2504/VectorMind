"""
Request ID Middleware
Adds unique request ID to every request for tracing
"""

import logging
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID to every request
    Useful for distributed tracing and log correlation
    """
    
    def __init__(self, app, header_name: str = "X-Request-ID"):
        """
        Initialize Request ID middleware
        
        Args:
            app: FastAPI application
            header_name: Header name for request ID
        """
        super().__init__(app)
        self.header_name = header_name
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and add request ID
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
        
        Returns:
            Response with request ID header
        """
        # Check if request already has an ID (from proxy/load balancer)
        request_id = request.headers.get(self.header_name)
        
        if not request_id:
            # Generate new request ID
            request_id = str(uuid.uuid4())
        
        # Store request ID in request state for access in handlers
        request.state.request_id = request_id
        
        # Add to response headers
        response = await call_next(request)
        response.headers[self.header_name] = request_id
        
        return response


def get_request_id(request: Request) -> str:
    """
    Helper function to get request ID from request
    
    Args:
        request: FastAPI request object
    
    Returns:
        Request ID string
    """
    return getattr(request.state, "request_id", "unknown")
