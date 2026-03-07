"""Agricultural news scraper.

This module provides the AgriculturalNewsScraper class for collecting
agricultural news and updates from various sources.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from ..browser import BrowserManager
from ..config import ScrapingConfig
from ..utils import (
    clean_text,
    detect_language,
    is_arabic_text,
    parse_date,
)
from .base import BaseScraper, ScrapingResult, ScrapingStatus

logger = logging.getLogger(__name__)


class NewsCategory(Enum):
    """Categories of agricultural news."""

    GENERAL = "general"
    CROPS = "crops"
    LIVESTOCK = "livestock"
    TECHNOLOGY = "technology"
    MARKET = "market"
    POLICY = "policy"
    WEATHER = "weather"
    RESEARCH = "research"
    EVENTS = "events"
    IRRIGATION = "irrigation"
    PESTS = "pests"


# Category keywords for classification
CATEGORY_KEYWORDS: dict[NewsCategory, list[str]] = {
    NewsCategory.CROPS: [
        "crop",
        "wheat",
        "barley",
        "rice",
        "harvest",
        "planting",
        "محصول",
        "قمح",
        "شعير",
        "أرز",
        "حصاد",
        "زراعة",
    ],
    NewsCategory.LIVESTOCK: [
        "livestock",
        "cattle",
        "sheep",
        "goat",
        "poultry",
        "dairy",
        "ماشية",
        "أبقار",
        "أغنام",
        "ماعز",
        "دواجن",
        "ألبان",
    ],
    NewsCategory.TECHNOLOGY: [
        "technology",
        "drone",
        "ai",
        "sensor",
        "smart",
        "automation",
        "تقنية",
        "طائرة",
        "ذكاء اصطناعي",
        "استشعار",
        "ذكي",
    ],
    NewsCategory.MARKET: [
        "market",
        "price",
        "export",
        "import",
        "trade",
        "sales",
        "سوق",
        "سعر",
        "تصدير",
        "استيراد",
        "تجارة",
        "مبيعات",
    ],
    NewsCategory.POLICY: [
        "policy",
        "government",
        "ministry",
        "regulation",
        "subsidy",
        "سياسة",
        "حكومة",
        "وزارة",
        "تنظيم",
        "دعم",
    ],
    NewsCategory.WEATHER: [
        "weather",
        "rain",
        "drought",
        "temperature",
        "climate",
        "طقس",
        "مطر",
        "جفاف",
        "حرارة",
        "مناخ",
    ],
    NewsCategory.RESEARCH: [
        "research",
        "study",
        "university",
        "science",
        "innovation",
        "بحث",
        "دراسة",
        "جامعة",
        "علم",
        "ابتكار",
    ],
    NewsCategory.IRRIGATION: [
        "irrigation",
        "water",
        "drip",
        "sprinkler",
        "groundwater",
        "ري",
        "مياه",
        "تنقيط",
        "رشاش",
        "مياه جوفية",
    ],
    NewsCategory.PESTS: [
        "pest",
        "disease",
        "insect",
        "fungus",
        "weed",
        "control",
        "آفة",
        "مرض",
        "حشرة",
        "فطر",
        "أعشاب",
        "مكافحة",
    ],
    NewsCategory.EVENTS: [
        "event",
        "conference",
        "exhibition",
        "fair",
        "workshop",
        "حدث",
        "مؤتمر",
        "معرض",
        "ورشة",
    ],
}


@dataclass
class NewsArticle:
    """Agricultural news article."""

    title: str
    title_ar: str | None = None
    summary: str | None = None
    summary_ar: str | None = None
    content: str | None = None
    url: str | None = None
    image_url: str | None = None
    author: str | None = None
    source: str = ""
    source_ar: str | None = None
    category: str = "general"
    tags: list[str] = field(default_factory=list)
    published_date: datetime | None = None
    scraped_at: datetime = field(default_factory=datetime.now)
    language: str = "en"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "title_ar": self.title_ar,
            "summary": self.summary,
            "summary_ar": self.summary_ar,
            "content": self.content,
            "url": self.url,
            "image_url": self.image_url,
            "author": self.author,
            "source": self.source,
            "source_ar": self.source_ar,
            "category": self.category,
            "tags": self.tags,
            "published_date": (self.published_date.isoformat() if self.published_date else None),
            "scraped_at": self.scraped_at.isoformat(),
            "language": self.language,
        }


@dataclass
class NewsReport:
    """Collection of news articles."""

    articles: list[NewsArticle] = field(default_factory=list)
    source: str | None = None
    query: str | None = None
    category: str | None = None
    fetched_at: datetime = field(default_factory=datetime.now)
    total_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "articles": [a.to_dict() for a in self.articles],
            "source": self.source,
            "query": self.query,
            "category": self.category,
            "fetched_at": self.fetched_at.isoformat(),
            "total_count": self.total_count,
        }

    def filter_by_category(self, category: str) -> list[NewsArticle]:
        """Filter articles by category."""
        return [a for a in self.articles if a.category == category]

    def filter_by_language(self, language: str) -> list[NewsArticle]:
        """Filter articles by language."""
        return [a for a in self.articles if a.language == language]


class AgriculturalNewsScraper(BaseScraper):
    """Scraper for agricultural news from various sources.

    This scraper collects agricultural news, updates, and articles
    from news sites and agricultural portals.

    Example:
        >>> async with BrowserManager() as browser:
        ...     scraper = AgriculturalNewsScraper(browser)
        ...     result = await scraper.scrape_news(category="crops")
        ...     if result.status == ScrapingStatus.SUCCESS:
        ...         for article in result.data.articles:
        ...             print(f"{article.title} - {article.source}")
    """

    # News source configurations
    SOURCES = {
        "mewa": {
            "url": "https://mewa.gov.sa/ar/MediaCenter/News",
            "name": "Ministry of Environment, Water and Agriculture",
            "name_ar": "وزارة البيئة والمياه والزراعة",
            "language": "ar",
        },
        "fao": {
            "url": "https://www.fao.org/newsroom/en/",
            "name": "Food and Agriculture Organization",
            "name_ar": "منظمة الأغذية والزراعة",
            "language": "en",
        },
        "reuters_agri": {
            "url": "https://www.reuters.com/business/agriculture/",
            "name": "Reuters Agriculture",
            "name_ar": "رويترز الزراعة",
            "language": "en",
        },
    }

    def __init__(
        self,
        browser: BrowserManager,
        config: ScrapingConfig | None = None,
    ) -> None:
        """Initialize the news scraper.

        Args:
            browser: Browser manager instance.
            config: Scraping configuration.
        """
        super().__init__(browser, config)

    def _classify_category(self, text: str) -> str:
        """Classify article category based on content.

        Args:
            text: Article title or content.

        Returns:
            Category string.
        """
        text_lower = text.lower()

        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return category.value

        return NewsCategory.GENERAL.value

    def _extract_tags(self, text: str) -> list[str]:
        """Extract tags from article text.

        Args:
            text: Article text.

        Returns:
            List of tags.
        """
        tags = []
        text_lower = text.lower()

        # Check for category keywords as tags
        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower and keyword not in tags:
                    # Only add English tags
                    if not is_arabic_text(keyword):
                        tags.append(keyword.lower())
                    if len(tags) >= 5:
                        break
            if len(tags) >= 5:
                break

        return tags

    async def scrape_news(
        self,
        query: str | None = None,
        category: str | None = None,
        source: str | None = None,
        limit: int = 20,
        language: str | None = None,
    ) -> ScrapingResult[NewsReport]:
        """Scrape agricultural news articles.

        Args:
            query: Search query for news.
            category: Filter by news category.
            source: Specific source to scrape.
            limit: Maximum number of articles.
            language: Filter by language ('ar', 'en').

        Returns:
            ScrapingResult containing NewsReport.
        """
        import time

        start_time = time.time()

        # Check cache
        cache_key = f"news_{query}_{category}_{source}_{limit}"
        cached = self.get_cached(cache_key)
        if cached:
            return ScrapingResult(
                status=ScrapingStatus.CACHED,
                data=cached,
                cached=True,
                duration_ms=(time.time() - start_time) * 1000,
            )

        articles: list[NewsArticle] = []

        try:
            # Select sources to scrape
            sources_to_scrape = [source] if source else list(self.SOURCES.keys())

            for src in sources_to_scrape:
                if src not in self.SOURCES:
                    continue

                source_config = self.SOURCES[src]

                # Filter by language if specified
                if language and source_config.get("language") != language:
                    continue

                try:
                    src_articles = await self._scrape_source(src, source_config, query, limit - len(articles))
                    articles.extend(src_articles)

                    if len(articles) >= limit:
                        break

                except Exception as e:
                    logger.warning(f"Failed to scrape {src}: {e}")
                    continue

            # Filter by category if specified
            if category:
                articles = [
                    a for a in articles if a.category == category or self._classify_category(a.title) == category
                ]

            # Limit results
            articles = articles[:limit]

            report = NewsReport(
                articles=articles,
                source=source,
                query=query,
                category=category,
                total_count=len(articles),
            )

            # Cache result
            self.set_cached(
                cache_key,
                report,
                ttl=self._config.cache.news_ttl,
            )

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"News scraped: {len(articles)} articles in {duration_ms:.0f}ms")

            return ScrapingResult(
                status=ScrapingStatus.SUCCESS,
                data=report,
                duration_ms=duration_ms,
            )

        except Exception as e:
            logger.error(f"News scraping failed: {e}")
            return ScrapingResult(
                status=ScrapingStatus.FAILED,
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000,
            )

    async def _scrape_source(
        self,
        source_name: str,
        source_config: dict[str, Any],
        query: str | None,
        limit: int,
    ) -> list[NewsArticle]:
        """Scrape articles from a specific source.

        Args:
            source_name: Source identifier.
            source_config: Source configuration.
            query: Search query.
            limit: Maximum articles.

        Returns:
            List of scraped articles.
        """
        url = source_config["url"]
        if query:
            # Add search parameter if applicable
            url = f"{url}?q={query}"

        await self.with_retry(
            f"Navigate to {source_name}",
            self.navigate,
            url,
            wait_until="domcontentloaded",
        )

        articles: list[NewsArticle] = []

        # Try common news article patterns
        article_selectors = [
            "article",
            ".news-item",
            ".article-item",
            ".news-card",
            ".story",
            "[class*='news']",
            "[class*='article']",
        ]

        for selector in article_selectors:
            try:
                elements = await self._page.query_selector_all(selector)
                if not elements:
                    continue

                for element in elements[:limit]:
                    try:
                        article = await self._extract_article(element, source_config)
                        if article and article.title:
                            articles.append(article)
                            if len(articles) >= limit:
                                break
                    except Exception:
                        continue

                if articles:
                    break

            except Exception:
                continue

        # If no articles found with specific selectors, try generic extraction
        if not articles:
            articles = await self._extract_generic_articles(source_config, limit)

        return articles

    async def _extract_article(
        self,
        element: Any,
        source_config: dict[str, Any],
    ) -> NewsArticle | None:
        """Extract article data from an element.

        Args:
            element: Playwright element handle.
            source_config: Source configuration.

        Returns:
            NewsArticle or None.
        """
        # Title
        title_element = await element.query_selector("h1, h2, h3, .title, .headline, [class*='title']")
        title = ""
        if title_element:
            title = await title_element.text_content()
            title = clean_text(title) if title else ""

        if not title:
            return None

        # URL
        url = None
        link_element = await element.query_selector("a")
        if link_element:
            url = await link_element.get_attribute("href")
            # Make absolute URL if relative
            if url and not url.startswith("http"):
                base_url = source_config["url"].rsplit("/", 1)[0]
                url = f"{base_url}/{url.lstrip('/')}"

        # Summary
        summary_element = await element.query_selector("p, .summary, .excerpt, .description, [class*='summary']")
        summary = ""
        if summary_element:
            summary = await summary_element.text_content()
            summary = clean_text(summary) if summary else ""

        # Image
        image_url = None
        img_element = await element.query_selector("img")
        if img_element:
            image_url = await img_element.get_attribute("src")

        # Date
        date_element = await element.query_selector("time, .date, .published, [class*='date']")
        published_date = None
        if date_element:
            date_text = await date_element.text_content()
            if date_text:
                published_date = parse_date(date_text)
            # Try datetime attribute
            if not published_date:
                datetime_attr = await date_element.get_attribute("datetime")
                if datetime_attr:
                    published_date = parse_date(datetime_attr)

        # Detect language
        language = detect_language(title)

        # Classify category
        category = self._classify_category(title + " " + summary)

        # Extract tags
        tags = self._extract_tags(title + " " + summary)

        article = NewsArticle(
            title=title,
            title_ar=title if language == "ar" else None,
            summary=summary,
            summary_ar=summary if language == "ar" else None,
            url=url,
            image_url=image_url,
            source=source_config.get("name", "Unknown"),
            source_ar=source_config.get("name_ar"),
            category=category,
            tags=tags,
            published_date=published_date,
            language=language,
        )

        return article

    async def _extract_generic_articles(
        self,
        source_config: dict[str, Any],
        limit: int,
    ) -> list[NewsArticle]:
        """Extract articles using generic patterns.

        Args:
            source_config: Source configuration.
            limit: Maximum articles.

        Returns:
            List of articles.
        """
        articles: list[NewsArticle] = []

        # Get all links with potential news content
        links = await self._page.query_selector_all("a[href]")

        for link in links[: limit * 3]:  # Check more links than needed
            try:
                href = await link.get_attribute("href")
                text = await link.text_content()

                if not href or not text:
                    continue

                text = clean_text(text)

                # Filter out navigation links
                if len(text) < 20:
                    continue
                if any(skip in text.lower() for skip in ["menu", "home", "about", "contact", "login"]):
                    continue

                language = detect_language(text)
                category = self._classify_category(text)

                article = NewsArticle(
                    title=text,
                    title_ar=text if language == "ar" else None,
                    url=href if href.startswith("http") else None,
                    source=source_config.get("name", "Unknown"),
                    source_ar=source_config.get("name_ar"),
                    category=category,
                    language=language,
                )

                articles.append(article)

                if len(articles) >= limit:
                    break

            except Exception:
                continue

        return articles

    async def scrape(self, **kwargs: Any) -> ScrapingResult[NewsReport]:
        """Perform news scraping.

        Args:
            **kwargs: Scraping parameters.

        Returns:
            ScrapingResult with NewsReport.
        """
        return await self.scrape_news(**kwargs)

    async def get_trending_topics(
        self,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get trending agricultural topics from news.

        Args:
            limit: Number of topics to return.

        Returns:
            List of trending topics with counts.
        """
        result = await self.scrape_news(limit=50)

        if result.status != ScrapingStatus.SUCCESS or not result.data:
            return []

        # Count tag occurrences
        tag_counts: dict[str, int] = {}
        for article in result.data.articles:
            for tag in article.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Sort by count and return top topics
        sorted_tags = sorted(
            tag_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return [{"topic": tag, "count": count} for tag, count in sorted_tags[:limit]]

    async def get_news_by_crop(
        self,
        crop: str,
        limit: int = 10,
    ) -> ScrapingResult[NewsReport]:
        """Get news articles related to a specific crop.

        Args:
            crop: Crop name.
            limit: Maximum articles.

        Returns:
            ScrapingResult with NewsReport.
        """
        return await self.scrape_news(query=crop, limit=limit)
