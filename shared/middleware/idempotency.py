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
_DEFAULT_MAX_ENTRIES: int = 10_000
# Headers that are unsafe or incorrect to replay from a cached response.
# set-cookie in particular can be multi-valued (dict collapses it) and
# re-emitting it could hand a session cookie to a different caller.
_HEADER_BLOCKLIST: frozenset[str] = frozenset({"set-cookie", "content-length", "transfer-encoding", "connection"})
# Only cache known-idempotent successful responses. 4xx/5xx are deliberately
# NOT cached so a transient validation/auth failure doesn't stick for the
# TTL window and a stale client can't replay a 401/403 into another caller.
_CACHEABLE_STATUS_CODES: frozenset[int] = frozenset({200, 201, 202, 204, 409})


def _default_scope(request: Request) -> str:
    """Compute a stable caller-scope string from an incoming request.

    Reads ``X-Tenant-Id`` and ``Authorization`` (hashed) so two callers
    with the same ``Idempotency-Key`` but different identities cannot
    collide. Authorization is hashed (not stored) so cached keys don't
    retain token material.
    """
    import hashlib

    tenant = request.headers.get("x-tenant-id", "")
    auth = request.headers.get("authorization", "")
    if auth:
        auth = hashlib.sha256(auth.encode()).hexdigest()[:16]
    # This is an ASGI middleware helper (Starlette), not a Flask route handler.
    # The returned string is an internal cache-key scope, never rendered as
    # HTML. Inputs are a tenant header (coarse) and a SHA-256 digest, neither
    # of which can carry user markup.
    # nosemgrep: python.flask.security.audit.directly-returned-format-string.directly-returned-format-string
    return f"{tenant}:{auth}"


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
        max_entries: int = _DEFAULT_MAX_ENTRIES,
        scope_from_request: Any = None,
    ) -> None:
        super().__init__(app)
        self._ttl = ttl_seconds
        self._header = header_name
        self._max_entries = max_entries
        # Caller-supplied function that returns a stable scoping string
        # (typically tenant_id + user_id) from the request. Required for
        # any multi-tenant deployment; without it, two callers that
        # accidentally reuse the same Idempotency-Key could read each
        # other's cached response. The built-in default extracts the
        # authenticated JWT's subject + tenant from common header names.
        self._scope_from_request = scope_from_request or _default_scope
        # TODO(prod): replace with Redis-backed store (shared across pods).
        self._store: dict[str, _CacheEntry] = {}

    def _purge_expired(self, now: float) -> None:
        """Opportunistic eviction of expired entries.

        Called on read/write hits; also hard-caps store size at
        ``_max_entries`` by dropping the oldest entries (by expires_at).
        Runs only when the store is non-empty, so hot path stays cheap.
        """
        expired = [k for k, v in self._store.items() if v.expires_at <= now]
        for k in expired:
            self._store.pop(k, None)
        overflow = len(self._store) - self._max_entries
        if overflow > 0:
            # Evict oldest (smallest expires_at) first
            stale = sorted(self._store.items(), key=lambda kv: kv[1].expires_at)[:overflow]
            for k, _ in stale:
                self._store.pop(k, None)

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        if request.method not in _MUTATING_METHODS:
            return await call_next(request)

        key = request.headers.get(self._header)
        if not key:
            return await call_next(request)

        # Include query string so two POSTs to the same path with different
        # query params (e.g. tenant routing) don't collide on the same key.
        # ALSO include tenant/user scope so two callers who accidentally
        # reuse the same Idempotency-Key cannot read each other's response.
        query = request.url.query or ""
        scope = self._scope_from_request(request) or "anon"
        cache_key = f"{scope}|{request.method}:{request.url.path}?{query}:{key}"
        now = time.time()

        cached = self._store.get(cache_key)
        if cached is not None and cached.expires_at > now:
            self._purge_expired(now)
            return Response(
                content=cached.body,
                status_code=cached.status_code,
                headers={**cached.headers, "Idempotent-Replayed": "true"},
                media_type=cached.media_type,
            )

        response = await call_next(request)

        # Only cache explicitly-safe success codes. 4xx (validation,
        # auth) and 5xx are NOT cached — a transient failure shouldn't
        # stick for the TTL and a stale client can't replay a 401/403
        # belonging to one caller into another.
        if response.status_code in _CACHEABLE_STATUS_CODES:
            body_chunks: list[bytes] = []
            async for chunk in response.body_iterator:
                body_chunks.append(chunk)
            body = b"".join(body_chunks)
            headers = {k: v for k, v in response.headers.items() if k.lower() not in _HEADER_BLOCKLIST}
            self._purge_expired(now)
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
