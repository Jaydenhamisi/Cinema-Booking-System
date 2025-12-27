"""
Request logging middleware for Cinema Booking System.
Tracks all HTTP requests with timing, request IDs, and comprehensive logging.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging_config import set_request_id, get_request_id

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all HTTP requests with:
    - Unique request ID for tracing
    - Request timing (duration)
    - Request method, path, client info
    - Response status code
    - Exception details on failures
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = set_request_id()
        
        # Start timing
        start_time = time.time()
        
        # Extract request info
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        
        # Log incoming request
        logger.info(
            f"→ {method} {path}",
            extra={
                'request_id': request_id,
                'method': method,
                'path': path,
                'client': client_host,
                'query_params': dict(request.query_params),
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log successful response
            logger.info(
                f"← {method} {path} → {response.status_code} ({duration:.3f}s)",
                extra={
                    'request_id': request_id,
                    'method': method,
                    'path': path,
                    'status_code': response.status_code,
                    'duration': duration,
                }
            )
            
            # Add request ID to response headers (useful for debugging)
            response.headers['X-Request-ID'] = request_id
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Log failed request with full exception details
            logger.error(
                f"✗ {method} {path} → FAILED ({duration:.3f}s)",
                extra={
                    'request_id': request_id,
                    'method': method,
                    'path': path,
                    'duration': duration,
                    'error': str(e),
                    'error_type': type(e).__name__,
                },
                exc_info=True  # This adds the full stack trace
            )
            
            # Re-raise the exception so FastAPI can handle it
            raise


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """
    Optional: Logs slow requests (>1 second).
    Only enable this if you want to track performance issues.
    """
    
    def __init__(self, app: ASGIApp, threshold_seconds: float = 1.0):
        super().__init__(app)
        self.threshold = threshold_seconds
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Only log if request took longer than threshold
        if duration > self.threshold:
            request_id = get_request_id()
            logger.warning(
                f"SLOW REQUEST: {request.method} {request.url.path} ({duration:.3f}s)",
                extra={
                    'request_id': request_id,
                    'method': request.method,
                    'path': request.url.path,
                    'duration': duration,
                    'threshold': self.threshold,
                }
            )
        
        return response