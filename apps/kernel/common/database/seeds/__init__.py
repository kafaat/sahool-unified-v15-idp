"""
SAHOOL Database Seeders
تعبئة قاعدة البيانات

This package contains database seeding utilities for different environments.
تحتوي هذه الحزمة على أدوات تعبئة قاعدة البيانات لبيئات مختلفة.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from sqlalchemy.engine import Engine


class BaseSeeder(ABC):
    """
    فئة أساسية للتعبئة
    Base seeder class

    All seeders should inherit from this class.
    يجب أن ترث جميع أدوات التعبئة من هذه الفئة.
    """

    def __init__(self, engine: Engine):
        """
        Initialize seeder.
        تهيئة أداة التعبئة.

        Args:
            engine: SQLAlchemy engine
        """
        self.engine = engine

    @abstractmethod
    def seed(self) -> Dict[str, Any]:
        """
        Seed the database with data.
        تعبئة قاعدة البيانات بالبيانات.

        Returns:
            Dictionary containing seeding results
        """
        pass

    def _log(self, message: str, message_ar: str = ""):
        """
        سجل رسالة
        Log a message

        Args:
            message: Message in English
            message_ar: Message in Arabic (optional)
        """
        print(f"[Seeder] {message}")
        if message_ar:
            print(f"[تعبئة] {message_ar}")


__all__ = ['BaseSeeder']
