"""Base scraper class with common functionality.

This module provides the BaseScraper abstract class with common methods
for navigation, waiting, extraction, rate limiting, and retry logic.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeout

from ..browser import BrowserManager
from ..config import RateLimitConfig, RetryConfig, ScrapingConfig, get_config
from ..utils import clean_text

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ScrapingError(Exception):
    """Base exception for scraping operations."""

    def __init__(
        self,
        message: str,
        url: str | None = None,
        status_code: int | None = None,
    ) -> None:
        """Initialize scraping error.

        Args:
            message: Error message.
            url: URL that caused the error.
            status_code: HTTP status code if applicable.
        """
        super().__init__(message)
        self.url = url
        self.status_code = status_code


class NavigationError(ScrapingError):
    """Raised when page navigation fails."""

    pass


class ExtractionError(ScrapingError):
    """Raised when data extraction fails."""

    pass


class RateLimitError(ScrapingError):
    """Raised when rate limit is exceeded."""

    pass


class ScrapingStatus(Enum):
    """Status of a scraping operation."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    CACHED = "cached"


@dataclass
class ScrapingResult(Generic[T]):
    """Result of a scraping operation."""

    status: ScrapingStatus
    data: T | None = None
    error: str | None = None
    url: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    cached: bool = False
    duration_ms: float = 0.0
    retries: int = 0


class SimpleCache:
    """Simple in-memory cache for scraped data."""

    def __init__(self, default_ttl: int = 3600) -> None:
        """Initialize cache.

        Args:
            default_ttl: Default time-to-live in seconds.
        """
        self._cache: dict[str, dict[str, Any]] = {}
        self._default_ttl = default_ttl

    def _generate_key(self, url: str, params: dict | None = None) -> str:
        """Generate cache key from URL and parameters.

        Args:
            url: Request URL.
            params: Optional request parameters.

        Returns:
            Cache key string.
        """
        key_data = url
        if params:
            key_data += json.dumps(params, sort_keys=True)
        return hashlib.sha256(key_data.encode()).hexdigest()

    def get(
        self,
        url: str,
        params: dict | None = None,
    ) -> Any | None:
        """Get cached data.

        Args:
            url: Request URL.
            params: Optional request parameters.

        Returns:
            Cached data or None if not found/expired.
        """
        key = self._generate_key(url, params)
        entry = self._cache.get(key)

        if not entry:
            return None

        if time.time() > entry["expires_at"]:
            del self._cache[key]
            return None

        return entry["data"]

    def set(
        self,
        url: str,
        data: Any,
        params: dict | None = None,
        ttl: int | None = None,
    ) -> None:
        """Store data in cache.

        Args:
            url: Request URL.
            data: Data to cache.
            params: Optional request parameters.
            ttl: Time-to-live in seconds.
        """
        key = self._generate_key(url, params)
        self._cache[key] = {
            "data": data,
            "expires_at": time.time() + (ttl or self._default_ttl),
        }

    def clear(self) -> None:
        """Clear all cached data."""
        self._cache.clear()

    def remove(self, url: str, params: dict | None = None) -> None:
        """Remove specific entry from cache.

        Args:
            url: Request URL.
            params: Optional request parameters.
        """
        key = self._generate_key(url, params)
        self._cache.pop(key, None)


class RateLimiter:
    """Rate limiter for controlling request frequency."""

    def __init__(self, config: RateLimitConfig | None = None) -> None:
        """Initialize rate limiter.

        Args:
            config: Rate limiting configuration.
        """
        self._config = config or RateLimitConfig()
        self._last_request_time: float = 0.0
        self._request_times: list[float] = []

    async def wait(self) -> None:
        """Wait if necessary to respect rate limits."""
        now = time.time()

        # Clean old request times (older than 1 minute)
        self._request_times = [t for t in self._request_times if now - t < 60]

        # Check requests per minute
        if self._config.requests_per_minute > 0 and len(self._request_times) >= self._config.requests_per_minute:
            sleep_time = 60 - (now - self._request_times[0])
            if sleep_time > 0:
                logger.debug(f"Rate limit: waiting {sleep_time:.2f}s (requests/min limit)")
                await asyncio.sleep(sleep_time)

        # Minimum delay between requests
        time_since_last = now - self._last_request_time
        if time_since_last < self._config.min_delay:
            delay = random.uniform(
                self._config.min_delay,
                self._config.max_delay,
            )
            wait_time = delay - time_since_last
            if wait_time > 0:
                logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)

        self._last_request_time = time.time()
        self._request_times.append(self._last_request_time)


class BaseScraper(ABC):
    """Abstract base class for web scrapers.

    This class provides common functionality for all scrapers including
    navigation, waiting, extraction, rate limiting, and retry logic.
    """

    def __init__(
        self,
        browser: BrowserManager,
        config: ScrapingConfig | None = None,
    ) -> None:
        """Initialize the scraper.

        Args:
            browser: Browser manager instance.
            config: Scraping configuration.
        """
        self._browser = browser
        self._config = config or get_config()
        self._page: Page | None = None
        self._cache = SimpleCache(self._config.cache.default_ttl)
        self._rate_limiter = RateLimiter(self._config.rate_limit)

    @property
    def browser(self) -> BrowserManager:
        """Get the browser manager."""
        return self._browser

    @property
    def page(self) -> Page | None:
        """Get the current page."""
        return self._page

    @property
    def cache(self) -> SimpleCache:
        """Get the cache instance."""
        return self._cache

    async def _ensure_page(self) -> Page:
        """Ensure a page is available.

        Returns:
            Current or new page instance.
        """
        if not self._page or self._page.is_closed():
            self._page = await self._browser.new_page()
        return self._page

    async def navigate(
        self,
        url: str,
        wait_until: str = "domcontentloaded",
        timeout: int | None = None,
    ) -> None:
        """Navigate to a URL.

        Args:
            url: URL to navigate to.
            wait_until: Wait condition ('load', 'domcontentloaded', 'networkidle').
            timeout: Navigation timeout in milliseconds.

        Raises:
            NavigationError: If navigation fails.
        """
        page = await self._ensure_page()
        await self._rate_limiter.wait()

        try:
            response = await page.goto(
                url,
                wait_until=wait_until,
                timeout=timeout or self._config.timeouts.navigation_timeout,
            )

            if response and response.status >= 400:
                raise NavigationError(
                    f"HTTP {response.status} for {url}",
                    url=url,
                    status_code=response.status,
                )

            logger.debug(f"Navigated to {url}")

        except PlaywrightTimeout as e:
            raise NavigationError(f"Navigation timeout for {url}", url=url) from e
        except Exception as e:
            if not isinstance(e, NavigationError):
                raise NavigationError(f"Navigation failed: {e}", url=url) from e
            raise

    async def wait_for(
        self,
        selector: str,
        state: str = "visible",
        timeout: int | None = None,
    ) -> None:
        """Wait for an element to reach a state.

        Args:
            selector: CSS selector for element.
            state: State to wait for ('attached', 'detached', 'visible', 'hidden').
            timeout: Wait timeout in milliseconds.
        """
        page = await self._ensure_page()
        await page.wait_for_selector(
            selector,
            state=state,
            timeout=timeout or self._config.timeouts.element_timeout,
        )

    async def wait_for_load(self, timeout: int | None = None) -> None:
        """Wait for page to finish loading.

        Args:
            timeout: Wait timeout in milliseconds.
        """
        page = await self._ensure_page()
        await page.wait_for_load_state(
            "networkidle",
            timeout=timeout or self._config.timeouts.network_idle_timeout,
        )

    async def extract_text(
        self,
        selector: str,
        default: str = "",
    ) -> str:
        """Extract text content from an element.

        Args:
            selector: CSS selector for element.
            default: Default value if element not found.

        Returns:
            Cleaned text content.
        """
        page = await self._ensure_page()
        try:
            element = await page.query_selector(selector)
            if element:
                text = await element.text_content()
                return clean_text(text) if text else default
        except Exception as e:
            logger.debug(f"Failed to extract text from {selector}: {e}")

        return default

    async def extract_texts(self, selector: str) -> list[str]:
        """Extract text from multiple elements.

        Args:
            selector: CSS selector for elements.

        Returns:
            List of cleaned text contents.
        """
        page = await self._ensure_page()
        try:
            elements = await page.query_selector_all(selector)
            texts = []
            for element in elements:
                text = await element.text_content()
                if text:
                    texts.append(clean_text(text))
            return texts
        except Exception as e:
            logger.debug(f"Failed to extract texts from {selector}: {e}")
            return []

    async def extract_attribute(
        self,
        selector: str,
        attribute: str,
        default: str = "",
    ) -> str:
        """Extract an attribute from an element.

        Args:
            selector: CSS selector for element.
            attribute: Attribute name to extract.
            default: Default value if not found.

        Returns:
            Attribute value.
        """
        page = await self._ensure_page()
        try:
            element = await page.query_selector(selector)
            if element:
                value = await element.get_attribute(attribute)
                return value or default
        except Exception as e:
            logger.debug(f"Failed to extract {attribute} from {selector}: {e}")

        return default

    async def extract_table(
        self,
        selector: str,
        has_header: bool = True,
    ) -> list[list[str]]:
        """Extract data from an HTML table.

        Args:
            selector: CSS selector for table element.
            has_header: Whether table has a header row.

        Returns:
            List of rows (each row is a list of cell values).
        """
        page = await self._ensure_page()
        rows = []

        try:
            # Get all rows
            row_elements = await page.query_selector_all(f"{selector} tr")

            for row in row_elements:
                cells = []
                # Get both th and td cells
                cell_elements = await row.query_selector_all("th, td")
                for cell in cell_elements:
                    text = await cell.text_content()
                    cells.append(clean_text(text) if text else "")
                if cells:
                    rows.append(cells)

        except Exception as e:
            logger.debug(f"Failed to extract table from {selector}: {e}")

        return rows

    async def extract_json(
        self,
        selector: str | None = None,
    ) -> dict[str, Any] | None:
        """Extract JSON data from page or element.

        Args:
            selector: Optional CSS selector for element containing JSON.

        Returns:
            Parsed JSON data or None.
        """
        page = await self._ensure_page()
        try:
            if selector:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    return json.loads(text) if text else None
            else:
                content = await page.content()
                # Try to find JSON in script tags
                import re

                json_match = re.search(
                    r"<script[^>]*type=[\"']application/json[\"'][^>]*>(.*?)</script>",
                    content,
                    re.DOTALL,
                )
                if json_match:
                    return json.loads(json_match.group(1))

        except json.JSONDecodeError as e:
            logger.debug(f"Failed to parse JSON: {e}")
        except Exception as e:
            logger.debug(f"Failed to extract JSON: {e}")

        return None

    async def click(self, selector: str) -> None:
        """Click an element.

        Args:
            selector: CSS selector for element.
        """
        page = await self._ensure_page()
        await page.click(selector)

    async def fill(self, selector: str, value: str) -> None:
        """Fill an input field.

        Args:
            selector: CSS selector for input.
            value: Value to fill.
        """
        page = await self._ensure_page()
        await page.fill(selector, value)

    async def screenshot(
        self,
        path: str | None = None,
        full_page: bool = True,
    ) -> bytes:
        """Take a screenshot of the current page.

        Args:
            path: Optional file path to save screenshot.
            full_page: Capture full page.

        Returns:
            Screenshot bytes.
        """
        page = await self._ensure_page()
        return await self._browser.take_screenshot(page, path, full_page)

    async def with_retry(
        self,
        operation: str,
        func: Any,
        *args: Any,
        retry_config: RetryConfig | None = None,
        **kwargs: Any,
    ) -> Any:
        """Execute a function with retry logic.

        Args:
            operation: Name of the operation for logging.
            func: Async function to execute.
            *args: Positional arguments for function.
            retry_config: Retry configuration.
            **kwargs: Keyword arguments for function.

        Returns:
            Function result.

        Raises:
            ScrapingError: If all retries fail.
        """
        config = retry_config or self._config.retry
        last_error: Exception | None = None

        for attempt in range(config.max_retries + 1):
            try:
                return await func(*args, **kwargs)

            except Exception as e:
                last_error = e
                if attempt < config.max_retries:
                    # Calculate delay with exponential backoff
                    delay = min(
                        config.base_delay * (config.backoff_multiplier**attempt),
                        config.max_delay,
                    )
                    # Add jitter
                    jitter = delay * config.jitter * random.random()
                    total_delay = delay + jitter

                    logger.warning(
                        f"{operation} failed (attempt {attempt + 1}/{config.max_retries + 1}): {e}. "
                        f"Retrying in {total_delay:.2f}s"
                    )
                    await asyncio.sleep(total_delay)

        raise ScrapingError(f"{operation} failed after {config.max_retries + 1} attempts: {last_error}")

    def get_cached(
        self,
        url: str,
        params: dict | None = None,
    ) -> Any | None:
        """Get data from cache.

        Args:
            url: Request URL.
            params: Optional parameters.

        Returns:
            Cached data or None.
        """
        if not self._config.cache.enabled:
            return None
        return self._cache.get(url, params)

    def set_cached(
        self,
        url: str,
        data: Any,
        params: dict | None = None,
        ttl: int | None = None,
    ) -> None:
        """Store data in cache.

        Args:
            url: Request URL.
            data: Data to cache.
            params: Optional parameters.
            ttl: Time-to-live in seconds.
        """
        if self._config.cache.enabled:
            self._cache.set(url, data, params, ttl)

    async def close(self) -> None:
        """Close the scraper and release resources."""
        if self._page and not self._page.is_closed():
            await self._browser.close_page(self._page)
            self._page = None

    @abstractmethod
    async def scrape(self, **kwargs: Any) -> ScrapingResult:
        """Perform the scraping operation.

        This method must be implemented by subclasses.

        Args:
            **kwargs: Scraping parameters.

        Returns:
            Scraping result.
        """
        pass
