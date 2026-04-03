"""Scraping configuration settings.

This module provides configuration for web scraping operations including
user agents, timeouts, retry settings, and rate limiting parameters.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field

# Common user agents for rotation
USER_AGENTS: list[str] = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Firefox on Linux
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

# Arabic locale user agents
USER_AGENTS_AR: list[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 ar-SA",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0 ar-SA",
]


@dataclass
class TimeoutConfig:
    """Timeout configuration for scraping operations."""

    # Page navigation timeout in milliseconds
    navigation_timeout: int = 30000

    # Element wait timeout in milliseconds
    element_timeout: int = 10000

    # Script execution timeout in milliseconds
    script_timeout: int = 30000

    # Network idle timeout in milliseconds
    network_idle_timeout: int = 5000


@dataclass
class RetryConfig:
    """Retry configuration for failed operations."""

    # Maximum number of retry attempts
    max_retries: int = 3

    # Base delay between retries in seconds
    base_delay: float = 1.0

    # Maximum delay between retries in seconds
    max_delay: float = 30.0

    # Exponential backoff multiplier
    backoff_multiplier: float = 2.0

    # Jitter factor (0-1) to add randomness to delays
    jitter: float = 0.1

    # HTTP status codes that should trigger a retry
    retry_status_codes: list[int] = field(default_factory=lambda: [408, 429, 500, 502, 503, 504])


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""

    # Minimum delay between requests in seconds
    min_delay: float = 1.0

    # Maximum delay between requests in seconds
    max_delay: float = 3.0

    # Requests per minute limit (0 = unlimited)
    requests_per_minute: int = 30

    # Enable adaptive rate limiting based on response times
    adaptive: bool = True


@dataclass
class CacheConfig:
    """Cache configuration for scraped data."""

    # Enable caching
    enabled: bool = True

    # Default TTL in seconds (1 hour)
    default_ttl: int = 3600

    # Weather data TTL in seconds (30 minutes)
    weather_ttl: int = 1800

    # Market price TTL in seconds (1 hour)
    market_price_ttl: int = 3600

    # News TTL in seconds (15 minutes)
    news_ttl: int = 900

    # Maximum cache size in MB
    max_size_mb: int = 100


@dataclass
class ProxyConfig:
    """Proxy configuration."""

    # Proxy server URL (e.g., "http://proxy:8080")
    server: str | None = None

    # Proxy username
    username: str | None = None

    # Proxy password
    password: str | None = None

    # Bypass proxy for these domains
    bypass: list[str] = field(default_factory=list)


@dataclass
class BrowserConfig:
    """Browser configuration."""

    # Run in headless mode
    headless: bool = True

    # Browser type: chromium, firefox, webkit
    browser_type: str = "chromium"

    # Viewport width
    viewport_width: int = 1920

    # Viewport height
    viewport_height: int = 1080

    # Accept language header
    accept_language: str = "en-US,en;q=0.9,ar;q=0.8"

    # Timezone ID
    timezone_id: str = "Asia/Riyadh"

    # Geolocation (Saudi Arabia default)
    geolocation_latitude: float = 24.7136
    geolocation_longitude: float = 46.6753

    # Enable JavaScript
    javascript_enabled: bool = True

    # Block images to speed up scraping
    block_images: bool = False

    # Block ads and trackers
    block_ads: bool = True

    # Slow down operations by this amount (ms) for debugging
    slow_mo: int = 0


@dataclass
class ScrapingConfig:
    """Main scraping configuration."""

    browser: BrowserConfig = field(default_factory=BrowserConfig)
    timeouts: TimeoutConfig = field(default_factory=TimeoutConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    proxy: ProxyConfig = field(default_factory=ProxyConfig)

    # User agents for rotation
    user_agents: list[str] = field(default_factory=lambda: USER_AGENTS.copy())

    # Enable user agent rotation
    rotate_user_agents: bool = True

    # Log level for scraping operations
    log_level: str = "INFO"

    # Save screenshots on error
    screenshot_on_error: bool = True

    # Screenshot directory
    screenshot_dir: str = os.path.join(tempfile.gettempdir(), "scraping_screenshots")


# Default configuration instance
default_config = ScrapingConfig()


def get_config() -> ScrapingConfig:
    """Get the default scraping configuration.

    Returns:
        ScrapingConfig: Default configuration instance.
    """
    return default_config


def create_config(
    headless: bool = True,
    proxy_server: str | None = None,
    max_retries: int = 3,
    requests_per_minute: int = 30,
    cache_enabled: bool = True,
) -> ScrapingConfig:
    """Create a custom scraping configuration.

    Args:
        headless: Run browser in headless mode.
        proxy_server: Optional proxy server URL.
        max_retries: Maximum number of retry attempts.
        requests_per_minute: Rate limit for requests.
        cache_enabled: Enable result caching.

    Returns:
        ScrapingConfig: Custom configuration instance.
    """
    return ScrapingConfig(
        browser=BrowserConfig(headless=headless),
        proxy=ProxyConfig(server=proxy_server),
        retry=RetryConfig(max_retries=max_retries),
        rate_limit=RateLimitConfig(requests_per_minute=requests_per_minute),
        cache=CacheConfig(enabled=cache_enabled),
    )
