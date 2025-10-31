"""
Logging Middleware
Structured logging for all HTTP requests and responses
"""

import logging
import time
import json
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for structured HTTP request/response logging
    Logs request details, response status, and timing
    """
    
    def __init__(
        self,
        app,
        log_request_body: bool = False,
        log_response_body: bool = False,
        exclude_paths: list = None
    ):
        """
        Initialize Logging middleware
        
        Args:
            app: FastAPI application
            log_request_body: Whether to log request body (careful with large payloads)
            log_response_body: Whether to log response body
            exclude_paths: Paths to exclude from logging (e.g., /healthz)
        """
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.exclude_paths = exclude_paths or ["/healthz", "/metrics"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
        
        Returns:
            Response
        """
        # Skip logging for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Get request ID if available
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Start timer
        start_time = time.time()
        
        # Build request log
        request_log = {
            "event": "http_request",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
        
        # Optionally log request body (be careful with large files)
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if len(body) < 10000:  # Only log small bodies
                    request_log["request_body"] = body.decode("utf-8")[:1000]
            except Exception as e:
                request_log["request_body_error"] = str(e)
        
        logger.info(json.dumps(request_log))
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Build response log
            response_log = {
                "event": "http_response",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            }
            
            # Log at appropriate level based on status code
            if response.status_code >= 500:
                logger.error(json.dumps(response_log))
            elif response.status_code >= 400:
                logger.warning(json.dumps(response_log))
            else:
                logger.info(json.dumps(response_log))
            
            return response
        
        except Exception as e:
            # Log exception
            duration = time.time() - start_time
            error_log = {
                "event": "http_error",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
                "error_type": type(e).__name__,
                "duration_ms": round(duration * 1000, 2),
            }
            logger.error(json.dumps(error_log))
            raise


class StructuredLogger:
    """Helper class for structured logging"""
    
    def __init__(self, logger_name: str = __name__):
        """
        Initialize structured logger
        
        Args:
            logger_name: Name of the logger
        """
        self.logger = logging.getLogger(logger_name)
    
    def log(
        self,
        level: str,
        event: str,
        **kwargs
    ):
        """
        Log structured message
        
        Args:
            level: Log level (info, warning, error, etc.)
            event: Event name
            **kwargs: Additional fields
        """
        log_data = {
            "event": event,
            "timestamp": time.time(),
            **kwargs
        }
        
        log_message = json.dumps(log_data)
        
        if level == "info":
            self.logger.info(log_message)
        elif level == "warning":
            self.logger.warning(log_message)
        elif level == "error":
            self.logger.error(log_message)
        elif level == "critical":
            self.logger.critical(log_message)
        elif level == "debug":
            self.logger.debug(log_message)
    
    def info(self, event: str, **kwargs):
        """Log info message"""
        self.log("info", event, **kwargs)
    
    def warning(self, event: str, **kwargs):
        """Log warning message"""
        self.log("warning", event, **kwargs)
    
    def error(self, event: str, **kwargs):
        """Log error message"""
        self.log("error", event, **kwargs)
    
    def critical(self, event: str, **kwargs):
        """Log critical message"""
        self.log("critical", event, **kwargs)
    
    def debug(self, event: str, **kwargs):
        """Log debug message"""
        self.log("debug", event, **kwargs)
