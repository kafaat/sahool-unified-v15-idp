"""
Pytest configuration for field_chat tests
Sets up in-memory SQLite database for testing
"""

import asyncio
import sys
from pathlib import Path

import pytest

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def _init_db():
    """Initialize database synchronously before tests"""
    from tortoise import Tortoise

    async def _init():
        await Tortoise.init(
            db_url="sqlite://:memory:",
            modules={"models": ["src.models"]},
        )
        await Tortoise.generate_schemas()

    loop = asyncio.new_event_loop()
    loop.run_until_complete(_init())
    loop.close()


def _close_db():
    """Close database connections"""
    from tortoise import Tortoise

    async def _close():
        await Tortoise.close_connections()

    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(_close())
        loop.close()
    except Exception:
        pass


# Initialize DB before any tests are collected
_init_db()


def pytest_sessionfinish(session, exitstatus):
    """Clean up after all tests"""
    _close_db()


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def clean_db():
    """Clean database between tests"""
    yield
    # Clean up after each test synchronously
    from tortoise import Tortoise

    async def _clean():
        from src.models import ChatAttachment, ChatMessage, ChatParticipant, ChatThread

        try:
            await ChatMessage.all().delete()
            await ChatParticipant.all().delete()
            await ChatAttachment.all().delete()
            await ChatThread.all().delete()
        except Exception:
            pass

    if Tortoise._inited:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(_clean())
        loop.close()
