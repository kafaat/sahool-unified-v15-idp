"""Playwright-based web scraping utilities for agricultural data.

This package provides async-first, type-safe web scraping utilities
designed for collecting agricultural data from various sources including
weather services, market price portals, and agricultural news sites.

Features:
- Async context manager for browser lifecycle
- Headless and headed browser modes
- Proxy support and user agent rotation
- Rate limiting and retry logic
- Result caching
- Bilingual support (Arabic/English)

Example:
    >>> from shared.scraping import BrowserManager, WeatherScraper
    >>>
    >>> async with BrowserManager() as browser:
    ...     scraper = WeatherScraper(browser)
    ...     weather = await scraper.scrape_forecast(lat=24.7, lon=46.7)
    ...     if weather.status == ScrapingStatus.SUCCESS:
    ...         print(f"Temperature: {weather.data.current.temperature_c}C")

Example with configuration:
    >>> from shared.scraping import (
    ...     BrowserManager,
    ...     MarketPriceScraper,
    ...     create_config,
    ... )
    >>>
    >>> config = create_config(
    ...     headless=True,
    ...     proxy_server="http://proxy:8080",
    ...     max_retries=5,
    ... )
    >>>
    >>> async with BrowserManager(config=config) as browser:
    ...     scraper = MarketPriceScraper(browser, config=config)
    ...     prices = await scraper.scrape_prices(market="riyadh")
"""

from __future__ import annotations

try:
    # Browser management
    from .browser import (
        BrowserError,
        BrowserLaunchError,
        BrowserManager,
        BrowserNavigationError,
        BrowserPool,
        create_browser,
    )

    # Configuration
    from .config import (
        USER_AGENTS,
        USER_AGENTS_AR,
        BrowserConfig,
        CacheConfig,
        ProxyConfig,
        RateLimitConfig,
        RetryConfig,
        ScrapingConfig,
        TimeoutConfig,
        create_config,
        get_config,
    )
    from .scrapers.agricultural_news import (
        AgriculturalNewsScraper,
        NewsArticle,
        NewsCategory,
        NewsReport,
    )

    # Base scraper and utilities
    from .scrapers.base import (
        BaseScraper,
        ExtractionError,
        NavigationError,
        RateLimiter,
        RateLimitError,
        ScrapingError,
        ScrapingResult,
        ScrapingStatus,
        SimpleCache,
    )
    from .scrapers.market_prices import (
        CropCategory,
        CropPrice,
        MarketPriceReport,
        MarketPriceScraper,
        PriceUnit,
    )

    # Specialized scrapers
    from .scrapers.weather import (
        DailyForecast,
        WeatherData,
        WeatherForecast,
        WeatherScraper,
    )

    # Utility functions
    from .utils import (
        clean_text,
        convert_arabic_digits,
        detect_language,
        extract_first_number,
        extract_numbers,
        extract_table_data,
        is_arabic_text,
        merge_dict_lists,
        normalize_location,
        parse_date,
        parse_percentage,
        parse_price,
        parse_temperature,
        sanitize_filename,
    )
except ImportError:
    # playwright package not installed — scraping features unavailable.
    pass

__all__ = [
    # Browser
    "BrowserManager",
    "BrowserPool",
    "BrowserError",
    "BrowserLaunchError",
    "BrowserNavigationError",
    "create_browser",
    # Configuration
    "ScrapingConfig",
    "BrowserConfig",
    "TimeoutConfig",
    "RetryConfig",
    "RateLimitConfig",
    "CacheConfig",
    "ProxyConfig",
    "get_config",
    "create_config",
    "USER_AGENTS",
    "USER_AGENTS_AR",
    # Base scraper
    "BaseScraper",
    "ScrapingResult",
    "ScrapingStatus",
    "ScrapingError",
    "NavigationError",
    "ExtractionError",
    "RateLimitError",
    "SimpleCache",
    "RateLimiter",
    # Weather
    "WeatherScraper",
    "WeatherData",
    "WeatherForecast",
    "DailyForecast",
    # Market prices
    "MarketPriceScraper",
    "CropPrice",
    "MarketPriceReport",
    "CropCategory",
    "PriceUnit",
    # News
    "AgriculturalNewsScraper",
    "NewsArticle",
    "NewsReport",
    "NewsCategory",
    # Utilities
    "clean_text",
    "convert_arabic_digits",
    "extract_numbers",
    "extract_first_number",
    "extract_table_data",
    "parse_date",
    "parse_price",
    "parse_temperature",
    "parse_percentage",
    "normalize_location",
    "sanitize_filename",
    "is_arabic_text",
    "detect_language",
    "merge_dict_lists",
]

__version__ = "16.0.0"
