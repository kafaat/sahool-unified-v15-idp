"""Scrapers package for agricultural data collection.

This package provides specialized scrapers for different types of
agricultural data including weather, market prices, and news.
"""

from .agricultural_news import AgriculturalNewsScraper, NewsArticle
from .base import BaseScraper, ScrapingError, ScrapingResult
from .market_prices import CropPrice, MarketPriceScraper
from .weather import WeatherData, WeatherForecast, WeatherScraper

__all__ = [
    # Base
    "BaseScraper",
    "ScrapingError",
    "ScrapingResult",
    # Weather
    "WeatherScraper",
    "WeatherData",
    "WeatherForecast",
    # Market Prices
    "MarketPriceScraper",
    "CropPrice",
    # News
    "AgriculturalNewsScraper",
    "NewsArticle",
]
