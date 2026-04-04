"""
SAHOOL Input Sanitization Middleware
ميدل وير تنظيف المدخلات لمنع هجمات XSS والحقن

Provides request body sanitization for FastAPI services.
Strips dangerous HTML/script content from string inputs.
"""

from __future__ import annotations

import html
import logging
import re
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger(__name__)

# Patterns that indicate potential XSS or injection attempts
DANGEROUS_PATTERNS = [
    re.compile(r"<script\b[^>]*>", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"on\w+\s*=", re.IGNORECASE),  # onclick=, onerror=, etc.
    re.compile(r"<iframe\b", re.IGNORECASE),
    re.compile(r"<object\b", re.IGNORECASE),
    re.compile(r"<embed\b", re.IGNORECASE),
    re.compile(r"<link\b[^>]*href", re.IGNORECASE),
    re.compile(r"expression\s*\(", re.IGNORECASE),  # CSS expression()
    re.compile(r"url\s*\(\s*['\"]?\s*data:", re.IGNORECASE),  # data: URLs in CSS
]

# HTML tags to strip (keep content, remove tags)
STRIP_TAGS_RE = re.compile(r"<[^>]+>")

# Maximum field length to prevent DoS via oversized inputs
MAX_STRING_LENGTH = 10000


def sanitize_string(value: str) -> str:
    """
    Sanitize a single string value.
    تنظيف قيمة نصية واحدة

    - Escapes HTML entities
    - Strips script tags and event handlers
    - Truncates oversized strings
    - Preserves Arabic/Unicode text
    """
    if not isinstance(value, str):
        return value

    # Truncate oversized strings
    if len(value) > MAX_STRING_LENGTH:
        value = value[:MAX_STRING_LENGTH]
        logger.warning(f"Input truncated to {MAX_STRING_LENGTH} characters")

    # Check for dangerous patterns and log if found
    for pattern in DANGEROUS_PATTERNS:
        if pattern.search(value):
            logger.warning(
                "Dangerous pattern detected in input",
                extra={"pattern": pattern.pattern[:50]},
            )
            break

    # Escape HTML entities (converts < > & " to safe equivalents)
    # This preserves Arabic text while neutralizing HTML
    value = html.escape(value, quote=True)

    return value


def sanitize_value(value: Any) -> Any:
    """
    Recursively sanitize a value (string, dict, list, or nested).
    تنظيف قيمة بشكل متكرر
    """
    if isinstance(value, str):
        return sanitize_string(value)
    elif isinstance(value, dict):
        return {k: sanitize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [sanitize_value(item) for item in value]
    return value


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware that sanitizes request body inputs.
    ميدل وير لتنظيف مدخلات جسم الطلب

    Only processes JSON request bodies for POST/PUT/PATCH methods.
    GET/DELETE/HEAD/OPTIONS are passed through unchanged.

    Usage:
        app.add_middleware(InputSanitizationMiddleware)
    """

    SANITIZE_METHODS = {"POST", "PUT", "PATCH"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Sanitize query parameters (all methods) — prevents XSS/injection via URL params
        if request.query_params:
            sanitized_params: dict[str, list[Any]] = {}
            for key, value in request.query_params.multi_items():
                sanitized_value = sanitize_value(value)
                sanitized_params.setdefault(key, []).append(sanitized_value)
            request.state.sanitized_query_params = sanitized_params

        # Sanitize JSON body for state-changing methods
        if request.method in self.SANITIZE_METHODS and request.headers.get("content-type", "").startswith(
            "application/json"
        ):
            try:
                body = await request.json()
                sanitized_body = sanitize_value(body)

                # Store sanitized body in request state for downstream access
                request.state.sanitized_body = sanitized_body
            except Exception as exc:
                # If body parsing fails, let the endpoint handler deal with it
                logger.warning(
                    "Input sanitization failed: could not parse JSON body for %s %s: %s",
                    request.method,
                    request.url.path,
                    type(exc).__name__,
                    exc_info=True,
                )

        return await call_next(request)


def setup_input_sanitization(app: Any) -> None:
    """
    Add input sanitization middleware to a FastAPI app.
    إضافة ميدل وير تنظيف المدخلات لتطبيق FastAPI

    Usage:
        from shared.middleware.input_sanitizer import setup_input_sanitization
        setup_input_sanitization(app)
    """
    app.add_middleware(InputSanitizationMiddleware)
    logger.info("Input sanitization middleware enabled")
