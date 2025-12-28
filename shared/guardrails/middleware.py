"""
AI Safety Guardrails - FastAPI Middleware
=========================================
FastAPI middleware for applying guardrails to all AI requests/responses.

Integrates input filtering, output filtering, and policy enforcement.

Author: SAHOOL Platform Team
Updated: December 2025
"""

import json
import logging
import time
from typing import Callable, Optional

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .input_filter import InputFilter, sanitize_input, compute_input_hash
from .output_filter import OutputFilter, sanitize_output
from .policies import (
    ContentSafetyLevel,
    PolicyManager,
    TrustLevel,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Guardrails Configuration
# ─────────────────────────────────────────────────────────────────────────────


class GuardrailsConfig:
    """Configuration for guardrails middleware"""

    def __init__(
        self,
        enabled: bool = True,
        log_violations: bool = True,
        block_violations: bool = True,
        mask_pii: bool = True,
        add_disclaimers: bool = True,
        strict_topic_check: bool = False,
        # Paths to exclude from guardrails
        exclude_paths: Optional[list[str]] = None,
        # Paths that require strict checking
        strict_paths: Optional[list[str]] = None,
    ):
        self.enabled = enabled
        self.log_violations = log_violations
        self.block_violations = block_violations
        self.mask_pii = mask_pii
        self.add_disclaimers = add_disclaimers
        self.strict_topic_check = strict_topic_check
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/favicon.ico",
        ]
        self.strict_paths = strict_paths or [
            "/api/v1/ai/chat",
            "/api/v1/ai/completion",
            "/api/v1/recommendations",
        ]


# ─────────────────────────────────────────────────────────────────────────────
# Violation Logger
# ─────────────────────────────────────────────────────────────────────────────


class ViolationLogger:
    """
    Logs guardrail violations for monitoring and analysis.

    In production, this should integrate with observability stack
    (e.g., Prometheus, Grafana, ELK).
    """

    def __init__(self):
        self.violations = []
        self.logger = logging.getLogger("guardrails.violations")

    def log_input_violation(
        self,
        request_id: str,
        user_id: Optional[str],
        trust_level: TrustLevel,
        violations: list[str],
        metadata: dict,
    ):
        """Log input violation"""
        violation_record = {
            "timestamp": time.time(),
            "type": "input_violation",
            "request_id": request_id,
            "user_id": user_id,
            "trust_level": trust_level.value,
            "violations": violations,
            "metadata": metadata,
        }

        self.violations.append(violation_record)
        self.logger.warning(
            f"Input violation: request_id={request_id} user_id={user_id} "
            f"violations={violations}"
        )

        # Alert on critical violations
        if metadata.get("injection_patterns") or metadata.get("blocked_topic"):
            self.logger.critical(f"Critical input violation: {violation_record}")

    def log_output_violation(
        self,
        request_id: str,
        user_id: Optional[str],
        warnings: list[str],
        metadata: dict,
    ):
        """Log output violation/warning"""
        violation_record = {
            "timestamp": time.time(),
            "type": "output_warning",
            "request_id": request_id,
            "user_id": user_id,
            "warnings": warnings,
            "metadata": metadata,
        }

        self.violations.append(violation_record)
        self.logger.warning(
            f"Output warning: request_id={request_id} user_id={user_id} "
            f"warnings={warnings}"
        )

        # Alert on safety issues
        if metadata.get("safety_issues"):
            self.logger.error(f"Output safety issue: {violation_record}")

    def get_recent_violations(self, limit: int = 100) -> list[dict]:
        """Get recent violations"""
        return self.violations[-limit:]

    def get_user_violations(self, user_id: str) -> list[dict]:
        """Get violations for specific user"""
        return [v for v in self.violations if v.get("user_id") == user_id]


# Global violation logger
violation_logger = ViolationLogger()


# ─────────────────────────────────────────────────────────────────────────────
# Guardrails Middleware
# ─────────────────────────────────────────────────────────────────────────────


class GuardrailsMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for AI Safety Guardrails.

    Applies input/output filtering to all requests matching configured paths.

    Usage:
        app = FastAPI()
        config = GuardrailsConfig(enabled=True)
        app.add_middleware(GuardrailsMiddleware, config=config)
    """

    def __init__(
        self,
        app: ASGIApp,
        config: Optional[GuardrailsConfig] = None,
        policy_manager: Optional[PolicyManager] = None,
    ):
        super().__init__(app)
        self.config = config or GuardrailsConfig()
        self.policy_manager = policy_manager or PolicyManager()
        self.input_filter = InputFilter(self.policy_manager)
        self.output_filter = OutputFilter(self.policy_manager)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through guardrails"""

        # Skip if disabled
        if not self.config.enabled:
            return await call_next(request)

        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.config.exclude_paths):
            return await call_next(request)

        # Generate request ID
        request_id = request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")

        # Extract user info (from JWT or headers)
        user_id = self._extract_user_id(request)
        trust_level = self._get_user_trust_level(request)

        # Determine if strict checking required
        strict_check = any(
            request.url.path.startswith(path) for path in self.config.strict_paths
        )

        # Process request
        try:
            # 1. Filter input (for POST/PUT requests with body)
            if request.method in ["POST", "PUT", "PATCH"]:
                request = await self._filter_input(
                    request, request_id, user_id, trust_level, strict_check
                )

            # 2. Call next middleware/endpoint
            response = await call_next(request)

            # 3. Filter output (for JSON responses)
            if response.headers.get("content-type", "").startswith("application/json"):
                response = await self._filter_output(
                    response, request_id, user_id, trust_level
                )

            # Add guardrails headers
            response.headers["X-Guardrails-Applied"] = "true"
            response.headers["X-Trust-Level"] = trust_level.value

            return response

        except HTTPException as e:
            # Pass through HTTP exceptions
            raise

        except Exception as e:
            logger.error(f"Guardrails middleware error: {e}", exc_info=True)
            # Don't block request on middleware errors
            return await call_next(request)

    async def _filter_input(
        self,
        request: Request,
        request_id: str,
        user_id: Optional[str],
        trust_level: TrustLevel,
        strict_check: bool,
    ) -> Request:
        """Filter request input"""

        # Read request body
        body = await request.body()
        if not body:
            return request

        try:
            # Parse JSON body
            data = json.loads(body)

            # Extract text fields to filter
            text_fields = self._extract_text_fields(data)
            if not text_fields:
                return request

            # Filter each text field
            for field_path, text in text_fields:
                # Sanitize
                text = sanitize_input(text)

                # Apply input filter
                result = self.input_filter.filter_input(
                    text=text,
                    trust_level=trust_level,
                    mask_pii=self.config.mask_pii,
                    strict_topic_check=strict_check or self.config.strict_topic_check,
                )

                # Handle violations
                if not result.is_safe:
                    # Log violation
                    if self.config.log_violations:
                        violation_logger.log_input_violation(
                            request_id=request_id,
                            user_id=user_id,
                            trust_level=trust_level,
                            violations=result.violations,
                            metadata=result.metadata,
                        )

                    # Block if configured
                    if self.config.block_violations:
                        raise HTTPException(
                            status_code=400,
                            detail={
                                "error": "input_validation_failed",
                                "message_en": "Your input contains unsafe or prohibited content",
                                "message_ar": "مدخلك يحتوي على محتوى غير آمن أو محظور",
                                "violations": result.violations,
                                "violations_ar": result.violations_ar,
                                "safety_level": result.safety_level.value,
                                "request_id": request_id,
                            },
                        )

                # Replace with filtered text
                self._set_field_value(data, field_path, result.filtered_text)

                # Log warnings
                if result.warnings and self.config.log_violations:
                    logger.info(
                        f"Input warnings: request_id={request_id} "
                        f"warnings={result.warnings}"
                    )

            # Update request body with filtered data
            filtered_body = json.dumps(data).encode("utf-8")

            # Create new request with filtered body
            async def receive():
                return {"type": "http.request", "body": filtered_body}

            request._receive = receive

        except json.JSONDecodeError:
            # Not JSON, skip filtering
            pass

        return request

    async def _filter_output(
        self,
        response: Response,
        request_id: str,
        user_id: Optional[str],
        trust_level: TrustLevel,
    ) -> Response:
        """Filter response output"""

        # Read response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        if not body:
            return response

        try:
            # Parse JSON response
            data = json.loads(body)

            # Extract text fields to filter
            text_fields = self._extract_text_fields(data)
            if not text_fields:
                return response

            # Filter each text field
            for field_path, text in text_fields:
                # Sanitize
                text = sanitize_output(text)

                # Apply output filter
                result = self.output_filter.filter_output(
                    text=text,
                    trust_level=trust_level,
                    language="ar" if self._is_arabic(text) else "en",
                    mask_pii=self.config.mask_pii,
                )

                # Log warnings
                if result.warnings and self.config.log_violations:
                    violation_logger.log_output_violation(
                        request_id=request_id,
                        user_id=user_id,
                        warnings=result.warnings,
                        metadata=result.metadata,
                    )

                # Replace with filtered text
                self._set_field_value(data, field_path, result.filtered_output)

            # Create new response with filtered data
            filtered_body = json.dumps(data).encode("utf-8")

            return Response(
                content=filtered_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type="application/json",
            )

        except json.JSONDecodeError:
            # Not JSON, return original
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
            )

    def _extract_text_fields(
        self, data: dict, path: str = ""
    ) -> list[tuple[str, str]]:
        """
        Recursively extract text fields from JSON data.

        Returns:
            List of (field_path, text) tuples
        """
        text_fields = []

        # Common field names for AI content
        ai_field_names = {
            "prompt",
            "query",
            "question",
            "message",
            "content",
            "text",
            "response",
            "answer",
            "completion",
            "input",
            "output",
        }

        if isinstance(data, dict):
            for key, value in data.items():
                field_path = f"{path}.{key}" if path else key

                if isinstance(value, str) and key.lower() in ai_field_names:
                    # Found a text field
                    if len(value) > 10:  # Only filter substantial text
                        text_fields.append((field_path, value))

                elif isinstance(value, (dict, list)):
                    # Recurse into nested structures
                    text_fields.extend(self._extract_text_fields(value, field_path))

        elif isinstance(data, list):
            for i, item in enumerate(data):
                field_path = f"{path}[{i}]"
                if isinstance(item, (dict, list)):
                    text_fields.extend(self._extract_text_fields(item, field_path))

        return text_fields

    def _set_field_value(self, data: dict, field_path: str, value: str):
        """Set value at field path in nested dict"""
        parts = field_path.split(".")
        current = data

        for i, part in enumerate(parts[:-1]):
            # Handle array indices
            if "[" in part:
                key, idx = part.split("[")
                idx = int(idx.rstrip("]"))
                current = current[key][idx]
            else:
                current = current[part]

        # Set final value
        last_part = parts[-1]
        if "[" in last_part:
            key, idx = last_part.split("[")
            idx = int(idx.rstrip("]"))
            current[key][idx] = value
        else:
            current[last_part] = value

    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request"""
        # Try to get from state (set by auth middleware)
        if hasattr(request.state, "user_id"):
            return request.state.user_id

        # Try to get from custom header
        return request.headers.get("X-User-ID")

    def _get_user_trust_level(self, request: Request) -> TrustLevel:
        """Determine user trust level from request"""
        # Extract user attributes
        user_id = self._extract_user_id(request)

        # Get from state if available (set by auth middleware)
        if hasattr(request.state, "trust_level"):
            return request.state.trust_level

        if hasattr(request.state, "principal"):
            principal = request.state.principal
            roles = principal.get("roles", [])
            is_premium = "premium" in roles
            is_verified = principal.get("verified", False)

            return self.policy_manager.get_user_trust_level(
                user_id=user_id,
                roles=roles,
                is_premium=is_premium,
                is_verified=is_verified,
            )

        # Default to untrusted for unauthenticated users
        return TrustLevel.UNTRUSTED if not user_id else TrustLevel.BASIC

    def _is_arabic(self, text: str) -> bool:
        """Check if text is primarily Arabic"""
        arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF")
        return arabic_chars > len(text) * 0.3


# ─────────────────────────────────────────────────────────────────────────────
# Utility Functions
# ─────────────────────────────────────────────────────────────────────────────


def setup_guardrails(
    app: FastAPI,
    config: Optional[GuardrailsConfig] = None,
    policy_manager: Optional[PolicyManager] = None,
):
    """
    Setup guardrails middleware on FastAPI app.

    Usage:
        app = FastAPI()
        setup_guardrails(app, GuardrailsConfig(enabled=True))

    Args:
        app: FastAPI application
        config: Guardrails configuration
        policy_manager: Policy manager instance
    """
    config = config or GuardrailsConfig()
    app.add_middleware(GuardrailsMiddleware, config=config, policy_manager=policy_manager)

    logger.info(
        f"AI Safety Guardrails enabled: "
        f"block_violations={config.block_violations} "
        f"mask_pii={config.mask_pii}"
    )


def get_violation_stats() -> dict:
    """
    Get guardrail violation statistics.

    Returns:
        Dictionary with violation counts and trends
    """
    violations = violation_logger.get_recent_violations(limit=1000)

    stats = {
        "total_violations": len(violations),
        "input_violations": sum(1 for v in violations if v["type"] == "input_violation"),
        "output_warnings": sum(1 for v in violations if v["type"] == "output_warning"),
        "critical_violations": sum(
            1
            for v in violations
            if v.get("metadata", {}).get("injection_patterns")
            or v.get("metadata", {}).get("blocked_topic")
        ),
        "by_trust_level": {},
    }

    # Count by trust level
    for violation in violations:
        level = violation.get("trust_level", "unknown")
        stats["by_trust_level"][level] = stats["by_trust_level"].get(level, 0) + 1

    return stats
