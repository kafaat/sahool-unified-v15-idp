"""Browser management for web scraping.

This module provides a BrowserManager class for managing Playwright browser
instances with support for headless/headed modes, proxy configuration,
and user agent rotation.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from .config import ProxyConfig, ScrapingConfig, get_config

logger = logging.getLogger(__name__)


class BrowserError(Exception):
    """Base exception for browser operations."""

    pass


class BrowserLaunchError(BrowserError):
    """Raised when browser fails to launch."""

    pass


class BrowserNavigationError(BrowserError):
    """Raised when navigation fails."""

    pass


class BrowserManager:
    """Manages Playwright browser lifecycle with configuration options.

    This class provides an async context manager for browser operations,
    supporting headless/headed modes, proxy configuration, and user agent rotation.

    Example:
        >>> async with BrowserManager() as browser:
        ...     page = await browser.new_page()
        ...     await page.goto("https://example.com")
        ...     content = await page.content()
    """

    def __init__(
        self,
        config: ScrapingConfig | None = None,
        headless: bool | None = None,
        proxy: str | ProxyConfig | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Initialize the browser manager.

        Args:
            config: Full scraping configuration. Uses defaults if not provided.
            headless: Override headless mode from config.
            proxy: Proxy server URL or ProxyConfig. Overrides config.
            user_agent: Specific user agent to use. Overrides rotation.
        """
        self._config = config or get_config()
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._pages: list[Page] = []

        # Override settings
        if headless is not None:
            self._config.browser.headless = headless

        if proxy is not None:
            if isinstance(proxy, str):
                self._config.proxy = ProxyConfig(server=proxy)
            else:
                self._config.proxy = proxy

        self._fixed_user_agent = user_agent
        self._current_user_agent_index = 0

    @property
    def browser(self) -> Browser | None:
        """Get the current browser instance."""
        return self._browser

    @property
    def context(self) -> BrowserContext | None:
        """Get the current browser context."""
        return self._context

    @property
    def config(self) -> ScrapingConfig:
        """Get the current configuration."""
        return self._config

    def _get_user_agent(self) -> str:
        """Get the next user agent for rotation.

        Returns:
            User agent string.
        """
        if self._fixed_user_agent:
            return self._fixed_user_agent

        if not self._config.rotate_user_agents:
            return self._config.user_agents[0]

        # Rotate through user agents
        user_agents = self._config.user_agents
        if not user_agents:
            return (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )

        agent = user_agents[self._current_user_agent_index]
        self._current_user_agent_index = (self._current_user_agent_index + 1) % len(user_agents)
        return agent

    def _get_browser_args(self) -> list[str]:
        """Get browser launch arguments.

        Returns:
            List of browser arguments.
        """
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--disable-extensions",
            "--no-first-run",
            "--no-default-browser-check",
        ]

        if self._config.browser.headless:
            args.extend(
                [
                    "--disable-gpu",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                ]
            )

        return args

    def _get_proxy_config(self) -> dict[str, Any] | None:
        """Get proxy configuration for browser.

        Returns:
            Proxy configuration dict or None.
        """
        proxy = self._config.proxy
        if not proxy.server:
            return None

        proxy_dict: dict[str, Any] = {"server": proxy.server}
        if proxy.username:
            proxy_dict["username"] = proxy.username
        if proxy.password:
            proxy_dict["password"] = proxy.password

        return proxy_dict

    async def _launch_browser(self) -> Browser:
        """Launch the browser instance.

        Returns:
            Browser instance.

        Raises:
            BrowserLaunchError: If browser fails to launch.
        """
        browser_config = self._config.browser
        browser_type = browser_config.browser_type

        try:
            if browser_type == "chromium":
                browser = await self._playwright.chromium.launch(
                    headless=browser_config.headless,
                    args=self._get_browser_args(),
                    slow_mo=browser_config.slow_mo,
                )
            elif browser_type == "firefox":
                browser = await self._playwright.firefox.launch(
                    headless=browser_config.headless,
                    slow_mo=browser_config.slow_mo,
                )
            elif browser_type == "webkit":
                browser = await self._playwright.webkit.launch(
                    headless=browser_config.headless,
                    slow_mo=browser_config.slow_mo,
                )
            else:
                raise BrowserLaunchError(f"Unsupported browser type: {browser_type}")

            logger.info(
                "Browser launched",
                extra={
                    "browser_type": browser_type,
                    "headless": browser_config.headless,
                },
            )
            return browser

        except Exception as e:
            raise BrowserLaunchError(f"Failed to launch browser: {e}") from e

    async def _create_context(self) -> BrowserContext:
        """Create a new browser context.

        Returns:
            Browser context.
        """
        browser_config = self._config.browser
        proxy = self._get_proxy_config()

        context_options: dict[str, Any] = {
            "viewport": {
                "width": browser_config.viewport_width,
                "height": browser_config.viewport_height,
            },
            "user_agent": self._get_user_agent(),
            "locale": browser_config.accept_language.split(",")[0],
            "timezone_id": browser_config.timezone_id,
            "java_script_enabled": browser_config.javascript_enabled,
            "bypass_csp": True,
        }

        if proxy:
            context_options["proxy"] = proxy

        # Set geolocation permissions
        context_options["geolocation"] = {
            "latitude": browser_config.geolocation_latitude,
            "longitude": browser_config.geolocation_longitude,
        }
        context_options["permissions"] = ["geolocation"]

        context = await self._browser.new_context(**context_options)

        # Block resources if configured
        if browser_config.block_images or browser_config.block_ads:
            await context.route("**/*", self._route_handler)

        return context

    async def _route_handler(self, route: Any) -> None:
        """Handle route interception for blocking resources.

        Args:
            route: Playwright route object.
        """
        browser_config = self._config.browser
        resource_type = route.request.resource_type
        url = route.request.url

        # Block images
        if browser_config.block_images and resource_type in [
            "image",
            "media",
        ]:
            await route.abort()
            return

        # Block ads and trackers
        if browser_config.block_ads:
            ad_patterns = [
                "googlesyndication",
                "doubleclick",
                "googleadservices",
                "facebook.net",
                "analytics",
                "tracker",
                "adservice",
                "ad-delivery",
            ]
            if any(pattern in url for pattern in ad_patterns):
                await route.abort()
                return

        await route.continue_()

    async def __aenter__(self) -> BrowserManager:
        """Enter the async context manager.

        Returns:
            Self with initialized browser.

        Raises:
            BrowserLaunchError: If browser fails to initialize.
        """
        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._launch_browser()
            self._context = await self._create_context()
            return self
        except Exception as e:
            await self.__aexit__(type(e), e, e.__traceback__)
            raise

    async def __aexit__(
        self,
        exc_type: type | None,
        exc_val: Exception | None,
        exc_tb: Any | None,
    ) -> None:
        """Exit the async context manager and cleanup resources."""
        # Close all pages
        for page in self._pages:
            try:
                await page.close()
            except Exception:
                pass

        # Close context
        if self._context:
            try:
                await self._context.close()
            except Exception:
                pass

        # Close browser
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass

        # Stop playwright
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass

        logger.info("Browser closed")

    async def new_page(self) -> Page:
        """Create a new page in the browser context.

        Returns:
            New page instance.

        Raises:
            BrowserError: If no context is available.
        """
        if not self._context:
            raise BrowserError("Browser context not initialized")

        page = await self._context.new_page()
        self._pages.append(page)

        # Set default navigation timeout
        page.set_default_navigation_timeout(self._config.timeouts.navigation_timeout)
        page.set_default_timeout(self._config.timeouts.element_timeout)

        return page

    async def close_page(self, page: Page) -> None:
        """Close a specific page.

        Args:
            page: Page to close.
        """
        if page in self._pages:
            self._pages.remove(page)
        await page.close()

    async def new_context(self) -> BrowserContext:
        """Create a new browser context with fresh settings.

        This is useful for isolating sessions or rotating user agents.

        Returns:
            New browser context.
        """
        if not self._browser:
            raise BrowserError("Browser not initialized")

        return await self._create_context()

    async def rotate_user_agent(self) -> None:
        """Rotate to the next user agent by creating a new context."""
        if self._context:
            await self._context.close()
        self._context = await self._create_context()

    async def take_screenshot(
        self,
        page: Page,
        path: str | None = None,
        full_page: bool = True,
    ) -> bytes:
        """Take a screenshot of the page.

        Args:
            page: Page to screenshot.
            path: Optional file path to save screenshot.
            full_page: Whether to capture full page.

        Returns:
            Screenshot bytes.
        """
        screenshot_args: dict[str, Any] = {"full_page": full_page}
        if path:
            screenshot_args["path"] = path

        return await page.screenshot(**screenshot_args)


@asynccontextmanager
async def create_browser(
    headless: bool = True,
    proxy: str | None = None,
    user_agent: str | None = None,
    config: ScrapingConfig | None = None,
) -> AsyncIterator[BrowserManager]:
    """Create a browser manager as an async context manager.

    Args:
        headless: Run in headless mode.
        proxy: Optional proxy server URL.
        user_agent: Optional fixed user agent.
        config: Optional full configuration.

    Yields:
        BrowserManager instance.

    Example:
        >>> async with create_browser(headless=True) as browser:
        ...     page = await browser.new_page()
        ...     await page.goto("https://example.com")
    """
    manager = BrowserManager(
        config=config,
        headless=headless,
        proxy=proxy,
        user_agent=user_agent,
    )

    async with manager as browser:
        yield browser


class BrowserPool:
    """Pool of browser instances for parallel scraping.

    This class manages multiple browser instances for concurrent operations.
    """

    def __init__(
        self,
        pool_size: int = 3,
        config: ScrapingConfig | None = None,
    ) -> None:
        """Initialize the browser pool.

        Args:
            pool_size: Number of browsers in the pool.
            config: Scraping configuration.
        """
        self._pool_size = pool_size
        self._config = config
        self._browsers: list[BrowserManager] = []
        self._available: asyncio.Queue[BrowserManager] = asyncio.Queue()
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize all browsers in the pool."""
        if self._initialized:
            return

        for _ in range(self._pool_size):
            manager = BrowserManager(config=self._config)
            await manager.__aenter__()
            self._browsers.append(manager)
            await self._available.put(manager)

        self._initialized = True
        logger.info(f"Browser pool initialized with {self._pool_size} browsers")

    async def close(self) -> None:
        """Close all browsers in the pool."""
        for browser in self._browsers:
            await browser.__aexit__(None, None, None)

        self._browsers.clear()
        self._initialized = False
        logger.info("Browser pool closed")

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[BrowserManager]:
        """Acquire a browser from the pool.

        Yields:
            BrowserManager instance.
        """
        if not self._initialized:
            await self.initialize()

        browser = await self._available.get()
        try:
            yield browser
        finally:
            await self._available.put(browser)

    async def __aenter__(self) -> BrowserPool:
        """Enter the async context manager."""
        await self.initialize()
        return self

    async def __aexit__(
        self,
        exc_type: type | None,
        exc_val: Exception | None,
        exc_tb: Any | None,
    ) -> None:
        """Exit the async context manager."""
        await self.close()
