"""
Input Validation Middleware
وسيط التحقق من المدخلات
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)

class InputValidationMiddleware(BaseHTTPMiddleware):
    """Validates and sanitizes all incoming requests"""

    MAX_BODY_SIZE = 1024 * 1024  # 1MB
    MAX_QUERY_LENGTH = 5000
    BLOCKED_CONTENT_TYPES = ['application/x-www-form-urlencoded']

    async def dispatch(self, request: Request, call_next):
        # Check content length
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > self.MAX_BODY_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Request body too large"
            )

        # Validate content type for POST/PUT
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.headers.get('content-type', '')
            if any(blocked in content_type for blocked in self.BLOCKED_CONTENT_TYPES):
                raise HTTPException(
                    status_code=415,
                    detail="Unsupported content type"
                )

        # Validate query parameters length
        query_string = str(request.query_params)
        if len(query_string) > self.MAX_QUERY_LENGTH:
            raise HTTPException(
                status_code=414,
                detail="Query string too long"
            )

        # Log request (without sensitive data)
        logger.info(f"Request: {request.method} {request.url.path}")

        response = await call_next(request)
        return response


def validate_query_input(query: str, max_length: int = 5000) -> str:
    """Validate user query input"""
    if not query or not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    query = query.strip()

    if len(query) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Query exceeds maximum length of {max_length} characters"
        )

    # Check for suspicious patterns using PromptGuard if available
    try:
        from ..security.prompt_guard import PromptGuard
        sanitized, is_safe, warnings = PromptGuard.validate_and_sanitize(query)

        if not is_safe:
            logger.warning(f"Suspicious query detected: {warnings}")
            # Don't reject, but log and use sanitized version

        return sanitized
    except ImportError:
        # PromptGuard not available, just return the query
        logger.debug("PromptGuard not available, skipping advanced validation")
        return query
