"""Tests for ``shared.stability.retry_classifier`` (PR-B)."""

from __future__ import annotations

import asyncio

import httpx
import pytest
from tenacity import AsyncRetrying, RetryError, Retrying

from shared.stability.retry_classifier import (
    DEFAULT_RETRYABLE,
    FailureClass,
    build_retry,
    classify,
    parse_retry_after,
)


# ── classify() ──────────────────────────────────────────────────────────────


class TestClassify:
    def test_asyncio_timeout_is_timeout(self):
        # Use asyncio.TimeoutError explicitly to verify both aliases route
        # to FailureClass.TIMEOUT on Python 3.11+.
        exc = asyncio.TimeoutError()  # noqa: UP041 — intentional alias check
        assert classify(exc) is FailureClass.TIMEOUT

    def test_builtin_timeout_is_timeout(self):
        assert classify(TimeoutError("slow")) is FailureClass.TIMEOUT

    def test_connection_error_is_network(self):
        assert classify(ConnectionError("refused")) is FailureClass.NETWORK

    def test_oserror_is_network(self):
        assert classify(OSError("io")) is FailureClass.NETWORK

    def test_unknown_exception_is_unknown(self):
        # ValueError is *not* a transient infra failure — must be UNKNOWN.
        assert classify(ValueError("bad input")) is FailureClass.UNKNOWN

    def test_httpx_connect_error_is_network(self):
        assert classify(httpx.ConnectError("dns")) is FailureClass.NETWORK

    def test_httpx_read_timeout_is_timeout(self):
        assert classify(httpx.ReadTimeout("slow")) is FailureClass.TIMEOUT

    @pytest.mark.parametrize(
        ("status", "expected"),
        [
            (429, FailureClass.RATE_LIMITED),
            (503, FailureClass.SERVICE_UNAVAILABLE),
            (500, FailureClass.SERVER_ERROR),
            (502, FailureClass.SERVER_ERROR),
            (401, FailureClass.AUTH),
            (403, FailureClass.AUTH),
            (400, FailureClass.CLIENT_ERROR),
            (404, FailureClass.CLIENT_ERROR),
            (200, FailureClass.UNKNOWN),  # HTTPStatusError on 2xx is degenerate
        ],
    )
    def test_http_status_classification(self, status: int, expected: FailureClass):
        request = httpx.Request("GET", "https://example.invalid/")
        response = httpx.Response(status, request=request)
        exc = httpx.HTTPStatusError("err", request=request, response=response)
        assert classify(exc) is expected


# ── parse_retry_after() ─────────────────────────────────────────────────────


class TestParseRetryAfter:
    def _exc(self, headers: dict[str, str] | None = None, status: int = 429):
        request = httpx.Request("GET", "https://example.invalid/")
        response = httpx.Response(status, headers=headers or {}, request=request)
        return httpx.HTTPStatusError("err", request=request, response=response)

    def test_numeric_seconds(self):
        assert parse_retry_after(self._exc({"Retry-After": "12"})) == 12.0

    def test_missing_header(self):
        assert parse_retry_after(self._exc()) is None

    def test_garbage_value(self):
        assert parse_retry_after(self._exc({"Retry-After": "soon"})) is None

    def test_negative_value_rejected(self):
        assert parse_retry_after(self._exc({"Retry-After": "-5"})) is None

    def test_absurd_value_capped(self):
        # > 1h → capped at 3600s (the comment promises a cap, not discard).
        assert parse_retry_after(self._exc({"Retry-After": "999999"})) == 3600.0

    def test_exact_one_hour_preserved(self):
        # Boundary: exactly 3600s passes through unchanged.
        assert parse_retry_after(self._exc({"Retry-After": "3600"})) == 3600.0

    def test_non_http_exception_returns_none(self):
        assert parse_retry_after(ValueError("x")) is None


# ── build_retry() ───────────────────────────────────────────────────────────


class TestBuildRetry:
    def test_returns_sync_retrying_by_default(self):
        retry = build_retry()
        assert isinstance(retry, Retrying)

    def test_async_flag_returns_async_retrying(self):
        retry = build_retry(asynchronous=True)
        assert isinstance(retry, AsyncRetrying)

    def test_invalid_max_attempts(self):
        with pytest.raises(ValueError):
            build_retry(max_attempts=0)

    def test_default_classes(self):
        # Sanity: defaults exclude AUTH, CLIENT_ERROR, UNKNOWN.
        assert FailureClass.AUTH not in DEFAULT_RETRYABLE
        assert FailureClass.CLIENT_ERROR not in DEFAULT_RETRYABLE
        assert FailureClass.UNKNOWN not in DEFAULT_RETRYABLE
        assert FailureClass.NETWORK in DEFAULT_RETRYABLE
        assert FailureClass.TIMEOUT in DEFAULT_RETRYABLE

    def test_retries_network_error_then_succeeds(self):
        retry = build_retry(max_attempts=3, multiplier=0.0001, max_wait=0.001)
        attempts = {"n": 0}

        def flaky() -> str:
            attempts["n"] += 1
            if attempts["n"] < 2:
                raise ConnectionError("transient")
            return "ok"

        for attempt in retry:
            with attempt:
                result = flaky()
        assert result == "ok"
        assert attempts["n"] == 2

    def test_does_not_retry_unknown_exceptions(self):
        retry = build_retry(max_attempts=5, multiplier=0.0001, max_wait=0.001)
        attempts = {"n": 0}

        def explode() -> None:
            attempts["n"] += 1
            raise ValueError("not retryable")

        with pytest.raises(ValueError):
            for attempt in retry:
                with attempt:
                    explode()
        assert attempts["n"] == 1

    def test_auth_failures_are_never_retried(self):
        # Even when caller explicitly asks for AUTH retries, we must refuse.
        retry = build_retry(
            failure_classes={FailureClass.AUTH, FailureClass.NETWORK},
            max_attempts=5,
            multiplier=0.0001,
            max_wait=0.001,
        )

        request = httpx.Request("GET", "https://example.invalid/")
        response = httpx.Response(401, request=request)
        attempts = {"n": 0}

        def auth_fail() -> None:
            attempts["n"] += 1
            raise httpx.HTTPStatusError("denied", request=request, response=response)

        with pytest.raises(httpx.HTTPStatusError):
            for attempt in retry:
                with attempt:
                    auth_fail()
        assert attempts["n"] == 1

    def test_only_auth_requested_collapses_to_single_attempt(self):
        retry = build_retry(
            failure_classes={FailureClass.AUTH},
            max_attempts=5,
            multiplier=0.0001,
            max_wait=0.001,
        )
        attempts = {"n": 0}

        def boom() -> None:
            attempts["n"] += 1
            raise ConnectionError("ignored class")

        with pytest.raises(ConnectionError):
            for attempt in retry:
                with attempt:
                    boom()
        assert attempts["n"] == 1

    def test_max_attempts_respected_for_persistent_failure(self):
        retry = build_retry(max_attempts=3, multiplier=0.0001, max_wait=0.001)
        attempts = {"n": 0}

        def always_fail() -> None:
            attempts["n"] += 1
            raise ConnectionError("nope")

        with pytest.raises((ConnectionError, RetryError)):
            for attempt in retry:
                with attempt:
                    always_fail()
        assert attempts["n"] == 3

    def test_retry_after_header_caps_wait(self):
        # End-to-end: retry succeeds and overall elapsed time stays bounded by
        # max_wait (i.e. an absurd Retry-After value is capped).
        retry = build_retry(
            failure_classes={FailureClass.RATE_LIMITED, FailureClass.NETWORK},
            max_attempts=2,
            multiplier=0.0001,
            max_wait=0.05,
        )
        request = httpx.Request("GET", "https://example.invalid/")
        attempts = {"n": 0}

        def flaky_429() -> str:
            attempts["n"] += 1
            if attempts["n"] < 2:
                response = httpx.Response(429, headers={"Retry-After": "10"}, request=request)
                raise httpx.HTTPStatusError("rate", request=request, response=response)
            return "ok"

        import time

        start = time.monotonic()
        for attempt in retry:
            with attempt:
                result = flaky_429()
        elapsed = time.monotonic() - start

        assert result == "ok"
        # Wait must be capped by max_wait (~0.05s), not 10s from header.
        assert elapsed < 1.0
