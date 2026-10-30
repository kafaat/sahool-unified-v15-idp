# shared/scraping - Data Scraping Utilities

أدوات استخلاص بيانات الويب

Async-first, type-safe web scraping utilities built on Playwright for collecting agricultural data: weather forecasts, crop market prices, and agricultural news. Supports Arabic/English content, proxy rotation, rate limiting, retry with exponential backoff, and result caching.

## File Structure

```
shared/scraping/
├── __init__.py               # Package exports
├── browser.py                # BrowserManager, BrowserPool, browser lifecycle
├── config.py                 # ScrapingConfig and all sub-configs
├── utils.py                  # Text parsing utilities (Arabic-aware)
└── scrapers/
    ├── __init__.py
    ├── base.py               # BaseScraper ABC, RateLimiter, SimpleCache
    ├── weather.py            # WeatherScraper
    ├── market_prices.py      # MarketPriceScraper
    └── agricultural_news.py  # AgriculturalNewsScraper
```

## Key Components

### Configuration (`config.py`)

**`ScrapingConfig`** (main config, composed of sub-configs):

| Sub-config | Key Settings |
|------------|-------------|
| `BrowserConfig` | `headless=True`, `browser_type=chromium`, `timezone_id=Asia/Riyadh`, `block_ads=True` |
| `TimeoutConfig` | `navigation_timeout=30000ms`, `element_timeout=10000ms`, `network_idle_timeout=5000ms` |
| `RetryConfig` | `max_retries=3`, exponential backoff with jitter, retries on 408/429/5xx |
| `RateLimitConfig` | `min_delay=1.0s`, `max_delay=3.0s`, `requests_per_minute=30`, adaptive mode |
| `CacheConfig` | `default_ttl=3600s`, weather TTL 1800s, news TTL 900s, `max_size_mb=100` |
| `ProxyConfig` | `server`, `username`, `password`, `bypass` list |

```python
# Quick custom config
from shared.scraping import create_config
config = create_config(headless=True, proxy_server="http://proxy:8080", max_retries=5)
```

### Browser Management (`browser.py`)

- **`BrowserManager`** - Async context manager: launch, new pages, screenshots, teardown
- **`BrowserPool`** - Manages multiple browser instances for concurrent scraping
- **`create_browser(config)`** - Factory function

### Base Scraper (`scrapers/base.py`)

**`BaseScraper`** (abstract) - Inherited by all scrapers:
- `navigate(url, wait_until, timeout)` - Page navigation with rate limiting
- `extract_text(selector)`, `extract_texts(selector)` - CSS selector text extraction
- `extract_attribute(selector, attribute)` - HTML attribute extraction
- `extract_table(selector, has_header)` - HTML table to list of rows
- `extract_json(selector)` - JSON from page or element
- `with_retry(operation, func, *args)` - Exponential backoff retry wrapper
- `get_cached(url)` / `set_cached(url, data, ttl)` - Cache integration
- `abstract scrape(**kwargs) -> ScrapingResult` - Must be implemented by subclasses

**`ScrapingResult[T]`** - Typed result: `status`, `data`, `error`, `url`, `timestamp`, `duration_ms`, `retries`, `cached`

**`ScrapingStatus`**: `SUCCESS`, `PARTIAL`, `FAILED`, `CACHED`

### Specialized Scrapers

| Scraper | Output Models | Description |
|---------|--------------|-------------|
| `WeatherScraper` | `WeatherData`, `WeatherForecast`, `DailyForecast` | Multi-day forecast by coordinates |
| `MarketPriceScraper` | `CropPrice`, `MarketPriceReport`, `CropCategory`, `PriceUnit` | Crop prices by market |
| `AgriculturalNewsScraper` | `NewsArticle`, `NewsReport`, `NewsCategory` | Agricultural news articles |

### Utilities (`utils.py`)

| Function | Purpose |
|----------|---------|
| `clean_text(text)` | Strip whitespace, normalize Unicode |
| `convert_arabic_digits(text)` | Convert Arabic-Indic numerals to ASCII |
| `is_arabic_text(text)` | Detect Arabic content |
| `detect_language(text)` | Language detection (AR/EN) |
| `parse_price(text)` | Extract numeric price, handle Arabic formatting |
| `parse_temperature(text)` | Extract temperature value and unit |
| `parse_percentage(text)` | Extract percentage float |
| `extract_numbers(text)` | All numbers from text |
| `parse_date(text)` | Parse date strings including Arabic formats |
| `normalize_location(text)` | Standardize location names |
| `extract_table_data(rows, headers)` | Convert row list to dict list |

## Usage Example

```python
from shared.scraping import BrowserManager, WeatherScraper, MarketPriceScraper, ScrapingStatus, create_config

config = create_config(headless=True, requests_per_minute=20)

async with BrowserManager(config=config) as browser:
    # Scrape weather forecast
    weather_scraper = WeatherScraper(browser, config=config)
    result = await weather_scraper.scrape(lat=24.7, lon=46.7)
    if result.status == ScrapingStatus.SUCCESS:
        print(f"Temperature: {result.data.current.temperature_c}°C")
        print(f"Forecast days: {len(result.data.forecast.daily)}")

    # Scrape market prices
    price_scraper = MarketPriceScraper(browser, config=config)
    prices = await price_scraper.scrape(market="riyadh")
    if prices.status == ScrapingStatus.SUCCESS:
        for crop_price in prices.data.prices:
            print(f"{crop_price.crop_name_ar}: {crop_price.price} {crop_price.unit}")

    # Scrape agricultural news
    news_scraper = AgriculturalNewsScraper(browser)
    news = await news_scraper.scrape(language="ar", limit=10)
```

## Dependencies

```
playwright>=1.40.0    # Browser automation
```

Install browsers: `playwright install chromium`

## Notes

- Browser defaults to Chromium with Saudi Arabia timezone (`Asia/Riyadh`) and geolocation (Riyadh).
- User agents include Arabic locale variants (`USER_AGENTS_AR`) for Arabic content sites.
- Cache is in-memory (per-process). For shared cache across workers, integrate with Redis from `shared/cache/`.
- The `RateLimiter` respects both per-request minimum delay and requests-per-minute limits simultaneously.
- Screenshots are saved to `/tmp/scraping_screenshots` on error for debugging.
- This module feeds data to `shared/market_prices/` and `shared/weather_alerts/`.
