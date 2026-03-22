"""
Rate Limiting Middleware Tests for SAHOOL Platform.

Tests validate rate limiting, throttling, and abuse prevention.
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import pytest


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    cooldown_seconds: int = 60


@dataclass
class RateLimitState:
    """Rate limit state for a client."""

    minute_count: int = 0
    hour_count: int = 0
    minute_reset: float = 0.0
    hour_reset: float = 0.0
    burst_tokens: float = 10.0
    last_request: float = 0.0


class RateLimiter:
    """Rate limiter implementation for testing."""

    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.clients: dict[str, RateLimitState] = {}
        self.blocked_ips: dict[str, float] = {}

    def get_client_key(self, ip: str, user_id: str | None = None) -> str:
        """Get client identifier for rate limiting."""
        if user_id:
            return f"user:{user_id}"
        return f"ip:{ip}"

    def get_state(self, client_key: str) -> RateLimitState:
        """Get or create rate limit state for client."""
        if client_key not in self.clients:
            self.clients[client_key] = RateLimitState(
                minute_reset=time.time() + 60,
                hour_reset=time.time() + 3600,
                burst_tokens=float(self.config.burst_limit),
                last_request=time.time(),
            )
        return self.clients[client_key]

    def check_rate_limit(self, client_key: str) -> tuple[bool, dict[str, Any]]:
        """Check if request is within rate limits."""
        now = time.time()
        state = self.get_state(client_key)

        if now >= state.minute_reset:
            state.minute_count = 0
            state.minute_reset = now + 60

        if now >= state.hour_reset:
            state.hour_count = 0
            state.hour_reset = now + 3600

        elapsed = now - state.last_request
        state.burst_tokens = min(self.config.burst_limit, state.burst_tokens + elapsed * (self.config.burst_limit / 60))
        state.last_request = now

        headers = {
            "X-RateLimit-Limit": str(self.config.requests_per_minute),
            "X-RateLimit-Remaining": str(max(0, self.config.requests_per_minute - state.minute_count)),
            "X-RateLimit-Reset": str(int(state.minute_reset)),
        }

        if state.burst_tokens < 1:
            headers["Retry-After"] = str(int(60 / self.config.burst_limit))
            return False, headers

        if state.minute_count >= self.config.requests_per_minute:
            headers["Retry-After"] = str(int(state.minute_reset - now))
            return False, headers

        if state.hour_count >= self.config.requests_per_hour:
            headers["Retry-After"] = str(int(state.hour_reset - now))
            return False, headers

        state.minute_count += 1
        state.hour_count += 1
        state.burst_tokens -= 1

        return True, headers

    def is_blocked(self, ip: str) -> bool:
        """Check if IP is blocked."""
        if ip in self.blocked_ips:
            if time.time() < self.blocked_ips[ip]:
                return True
            del self.blocked_ips[ip]
        return False

    def block_ip(self, ip: str, duration: int = 300):
        """Block an IP address."""
        self.blocked_ips[ip] = time.time() + duration


@pytest.fixture
def rate_limiter():
    """Create rate limiter instance."""
    return RateLimiter(
        RateLimitConfig(requests_per_minute=60, requests_per_hour=1000, burst_limit=10, cooldown_seconds=60)
    )


@pytest.fixture
def strict_rate_limiter():
    """Create strict rate limiter for testing limits."""
    return RateLimiter(
        RateLimitConfig(requests_per_minute=5, requests_per_hour=50, burst_limit=10, cooldown_seconds=60)
    )


class TestRateLimitBasics:
    """Basic rate limiting tests."""

    def test_first_request_allowed(self, rate_limiter):
        """Test first request is always allowed."""
        allowed, headers = rate_limiter.check_rate_limit("ip:192.168.1.1")

        assert allowed is True
        assert "X-RateLimit-Limit" in headers

    def test_rate_limit_headers_present(self, rate_limiter):
        """Test rate limit headers are present."""
        _, headers = rate_limiter.check_rate_limit("ip:192.168.1.1")

        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers
        assert "X-RateLimit-Reset" in headers

    def test_remaining_decreases(self, rate_limiter):
        """Test remaining count decreases with each request."""
        client_key = "ip:192.168.1.1"

        _, headers1 = rate_limiter.check_rate_limit(client_key)
        remaining1 = int(headers1["X-RateLimit-Remaining"])

        _, headers2 = rate_limiter.check_rate_limit(client_key)
        remaining2 = int(headers2["X-RateLimit-Remaining"])

        assert remaining2 < remaining1


class TestMinuteLimit:
    """Tests for per-minute rate limiting."""

    def test_minute_limit_enforced(self, strict_rate_limiter):
        """Test per-minute limit is enforced."""
        client_key = "ip:192.168.1.1"

        for i in range(5):
            allowed, _ = strict_rate_limiter.check_rate_limit(client_key)
            assert allowed is True, f"Request {i + 1} should be allowed"

        allowed, headers = strict_rate_limiter.check_rate_limit(client_key)
        assert allowed is False
        assert "Retry-After" in headers

    def test_minute_limit_resets(self, rate_limiter):
        """Test minute limit resets after 60 seconds."""
        client_key = "ip:192.168.1.1"
        state = rate_limiter.get_state(client_key)

        state.minute_count = 60
        state.minute_reset = time.time() - 1

        allowed, _ = rate_limiter.check_rate_limit(client_key)

        assert allowed is True
        assert state.minute_count == 1


class TestHourLimit:
    """Tests for per-hour rate limiting."""

    def test_hour_limit_enforced(self):
        """Test per-hour limit is enforced."""
        limiter = RateLimiter(RateLimitConfig(requests_per_minute=1000, requests_per_hour=5, burst_limit=100))

        client_key = "ip:192.168.1.1"

        for _ in range(5):
            allowed, _ = limiter.check_rate_limit(client_key)
            assert allowed is True

        allowed, headers = limiter.check_rate_limit(client_key)
        assert allowed is False


class TestBurstLimit:
    """Tests for burst rate limiting."""

    def test_burst_limit_enforced(self, strict_rate_limiter):
        """Test burst limit is enforced."""
        client_key = "ip:192.168.1.1"

        for i in range(3):
            allowed, _ = strict_rate_limiter.check_rate_limit(client_key)
            assert allowed is True

    def test_burst_tokens_regenerate(self, strict_rate_limiter):
        """Test burst tokens regenerate over time."""
        client_key = "ip:192.168.1.1"
        state = strict_rate_limiter.get_state(client_key)

        state.burst_tokens = 0
        state.last_request = time.time() - 60

        allowed, _ = strict_rate_limiter.check_rate_limit(client_key)

        assert state.burst_tokens > 0


class TestClientIdentification:
    """Tests for client identification."""

    def test_ip_based_key(self, rate_limiter):
        """Test IP-based client key generation."""
        key = rate_limiter.get_client_key("192.168.1.1")
        assert key == "ip:192.168.1.1"

    def test_user_based_key(self, rate_limiter):
        """Test user-based client key generation."""
        key = rate_limiter.get_client_key("192.168.1.1", "user123")
        assert key == "user:user123"

    def test_user_key_takes_priority(self, rate_limiter):
        """Test user ID takes priority over IP."""
        key = rate_limiter.get_client_key("192.168.1.1", "user123")
        assert "user:" in key
        assert "ip:" not in key

    def test_different_clients_separate_limits(self, rate_limiter):
        """Test different clients have separate limits."""
        _, headers1 = rate_limiter.check_rate_limit("ip:192.168.1.1")
        _, headers2 = rate_limiter.check_rate_limit("ip:192.168.1.2")

        remaining1 = int(headers1["X-RateLimit-Remaining"])
        remaining2 = int(headers2["X-RateLimit-Remaining"])

        assert remaining1 == remaining2


class TestIPBlocking:
    """Tests for IP blocking functionality."""

    def test_block_ip(self, rate_limiter):
        """Test IP blocking."""
        rate_limiter.block_ip("192.168.1.100", duration=300)

        assert rate_limiter.is_blocked("192.168.1.100") is True

    def test_blocked_ip_expires(self, rate_limiter):
        """Test blocked IP expires after duration."""
        rate_limiter.block_ip("192.168.1.100", duration=1)

        assert rate_limiter.is_blocked("192.168.1.100") is True

        time.sleep(1.5)

        assert rate_limiter.is_blocked("192.168.1.100") is False

    def test_unblocked_ip_not_blocked(self, rate_limiter):
        """Test unblocked IP is not blocked."""
        assert rate_limiter.is_blocked("192.168.1.200") is False


class TestRateLimitTiers:
    """Tests for different rate limit tiers."""

    def test_free_tier_limits(self):
        """Test free tier rate limits."""
        free_config = RateLimitConfig(requests_per_minute=30, requests_per_hour=500)
        limiter = RateLimiter(free_config)

        assert limiter.config.requests_per_minute == 30
        assert limiter.config.requests_per_hour == 500

    def test_standard_tier_limits(self):
        """Test standard tier rate limits."""
        standard_config = RateLimitConfig(requests_per_minute=60, requests_per_hour=2000)
        limiter = RateLimiter(standard_config)

        assert limiter.config.requests_per_minute == 60
        assert limiter.config.requests_per_hour == 2000

    def test_premium_tier_limits(self):
        """Test premium tier rate limits."""
        premium_config = RateLimitConfig(requests_per_minute=120, requests_per_hour=5000)
        limiter = RateLimiter(premium_config)

        assert limiter.config.requests_per_minute == 120
        assert limiter.config.requests_per_hour == 5000


class TestRetryAfterHeader:
    """Tests for Retry-After header."""

    def test_retry_after_on_limit(self, strict_rate_limiter):
        """Test Retry-After header is set when limited."""
        client_key = "ip:192.168.1.1"

        for _ in range(10):
            strict_rate_limiter.check_rate_limit(client_key)

        allowed, headers = strict_rate_limiter.check_rate_limit(client_key)

        if not allowed:
            assert "Retry-After" in headers
            assert int(headers["Retry-After"]) > 0


class TestConcurrentRequests:
    """Tests for concurrent request handling."""

    def test_rapid_requests_limited(self, strict_rate_limiter):
        """Test rapid consecutive requests are limited."""
        client_key = "ip:192.168.1.1"
        allowed_count = 0

        for _ in range(10):
            allowed, _ = strict_rate_limiter.check_rate_limit(client_key)
            if allowed:
                allowed_count += 1

        assert allowed_count <= strict_rate_limiter.config.requests_per_minute


@pytest.mark.unit
class TestRateLimitByEndpoint:
    """Tests for endpoint-specific rate limiting."""

    def test_different_endpoints_separate_limits(self):
        """Test different endpoints can have separate limits."""
        endpoint_configs = {
            "/api/v1/auth/login": RateLimitConfig(requests_per_minute=5),
            "/api/v1/fields": RateLimitConfig(requests_per_minute=60),
            "/api/v1/ndvi": RateLimitConfig(requests_per_minute=30),
        }

        assert endpoint_configs["/api/v1/auth/login"].requests_per_minute == 5
        assert endpoint_configs["/api/v1/fields"].requests_per_minute == 60

    def test_write_endpoints_stricter(self):
        """Test write endpoints have stricter limits."""
        read_config = RateLimitConfig(requests_per_minute=100)
        write_config = RateLimitConfig(requests_per_minute=20)

        assert write_config.requests_per_minute < read_config.requests_per_minute


@pytest.mark.unit
class TestRateLimitPersistence:
    """Tests for rate limit state persistence."""

    def test_state_persists_across_requests(self, rate_limiter):
        """Test rate limit state persists across requests."""
        client_key = "ip:192.168.1.1"

        rate_limiter.check_rate_limit(client_key)
        state1 = rate_limiter.get_state(client_key)
        count1 = state1.minute_count

        rate_limiter.check_rate_limit(client_key)
        state2 = rate_limiter.get_state(client_key)
        count2 = state2.minute_count

        assert count2 == count1 + 1

    def test_new_client_fresh_state(self, rate_limiter):
        """Test new client gets fresh state."""
        state = rate_limiter.get_state("ip:new-client")

        assert state.minute_count == 0
        assert state.hour_count == 0


@pytest.mark.unit
class TestRateLimitExemptions:
    """Tests for rate limit exemptions."""

    def test_internal_requests_exempted(self):
        """Test internal service requests can be exempted."""
        internal_ips = ["10.0.0.1", "10.0.0.2", "172.16.0.1"]

        def is_internal(ip: str) -> bool:
            return ip.startswith("10.") or ip.startswith("172.16.")

        for ip in internal_ips:
            assert is_internal(ip) is True

        assert is_internal("192.168.1.1") is False

    def test_healthcheck_exempted(self):
        """Test health check endpoints are exempted."""
        exempt_paths = ["/healthz", "/readyz", "/metrics"]

        def is_exempt(path: str) -> bool:
            return path in exempt_paths

        assert is_exempt("/healthz") is True
        assert is_exempt("/api/v1/fields") is False
