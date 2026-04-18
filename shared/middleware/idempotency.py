"""
SAHOOL Idempotency Middleware
==============================

Provides `IdempotencyMiddleware`, an ASGI/Starlette middleware that makes
mutating HTTP requests safe to retry. When a client sends the same
`Idempotency-Key` header twice for the same path and method, the second
request short-circuits and returns the cached response from the first.

Scope:
    Applied to POST, PATCH, and DELETE requests only. GET/HEAD/OPTIONS/PUT
    are untouched. Requests without an `Idempotency-Key` header are passed
    through unchanged.

Current store:
    Simple in-process dict with 10-minute TTL. This is sufficient for a
    single replica but unsafe for horizontally scaled deployments.

TODO:
    Swap the in-memory store for Redis (shared across replicas) before
    wiring this middleware into any production service. Keys should be
    scoped by tenant_id + user_id + method + path + idempotency_key.

Not wired by default:
    This module only defines the middleware. Services opt in via
    ``app.add_middleware(IdempotencyMiddleware)`` — no service does so yet.
"""

from __future__ import annotations

import time
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

_MUTATING_METHODS: frozenset[str] = frozenset({"POST", "PATCH", "DELETE"})
_DEFAULT_TTL_SECONDS: int = 600  # 10 minutes


class _CacheEntry:
    __slots__ = ("status_code", "body", "headers", "media_type", "expires_at")

    def __init__(
        self,
        status_code: int,
        body: bytes,
        headers: dict[str, str],
        media_type: str | None,
        expires_at: float,
    ) -> None:
        self.status_code = status_code
        self.body = body
        self.headers = headers
        self.media_type = media_type
        self.expires_at = expires_at


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Cache responses for mutating requests keyed by `Idempotency-Key`.

    Args:
        app: ASGI app.
        ttl_seconds: Lifetime of a cached response. Default: 600s (10 min).
        header_name: Header name to read. Default: ``Idempotency-Key``.
    """

    def __init__(
        self,
        app: ASGIApp,
        ttl_seconds: int = _DEFAULT_TTL_SECONDS,
        header_name: str = "Idempotency-Key",
    ) -> None:
        super().__init__(app)
        self._ttl = ttl_seconds
        self._header = header_name
        # TODO(prod): replace with Redis-backed store (shared across pods).
        self._store: dict[str, _CacheEntry] = {}

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        if request.method not in _MUTATING_METHODS:
            return await call_next(request)

        key = request.headers.get(self._header)
        if not key:
            return await call_next(request)

        cache_key = f"{request.method}:{request.url.path}:{key}"
        now = time.time()

        cached = self._store.get(cache_key)
        if cached is not None and cached.expires_at > now:
            return Response(
                content=cached.body,
                status_code=cached.status_code,
                headers={**cached.headers, "Idempotent-Replayed": "true"},
                media_type=cached.media_type,
            )

        response = await call_next(request)

        # Only cache successful / expected client-visible responses.
        if 200 <= response.status_code < 500:
            body_chunks: list[bytes] = []
            async for chunk in response.body_iterator:
                body_chunks.append(chunk)
            body = b"".join(body_chunks)
            headers = {k: v for k, v in response.headers.items() if k.lower() != "content-length"}
            self._store[cache_key] = _CacheEntry(
                status_code=response.status_code,
                body=body,
                headers=headers,
                media_type=response.media_type,
                expires_at=now + self._ttl,
            )
            return Response(
                content=body,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type,
            )

        return response
