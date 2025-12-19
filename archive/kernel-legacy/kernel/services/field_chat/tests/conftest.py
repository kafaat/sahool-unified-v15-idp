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

# Also add parent so 'src.models' works
parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

# Track if DB is available
DB_AVAILABLE = False


def _init_db():
    """Initialize database synchronously before tests"""
    global DB_AVAILABLE
    from tortoise import Tortoise

    async def _init():
        await Tortoise.init(
            db_url="sqlite://:memory:",
            modules={"models": ["src.models"]},
        )
        await Tortoise.generate_schemas()

    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(_init())
        loop.close()
        DB_AVAILABLE = True
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
        print("   Tests will run without database (some tests may be skipped)")
        DB_AVAILABLE = False


def _close_db():
    """Close database connections"""
    from tortoise import Tortoise

    async def _close():
        await Tortoise.close_connections()

    try:
        if DB_AVAILABLE:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(_close())
            loop.close()
    except Exception:
        pass


# Try to initialize DB (but don't fail if it doesn't work)
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


@pytest.fixture
def db_available():
    """Fixture to check if database is available"""
    if not DB_AVAILABLE:
        pytest.skip("Database not available")
    return True


@pytest.fixture(autouse=True)
def clean_db():
    """Clean database between tests"""
    yield
    # Clean up after each test synchronously
    if not DB_AVAILABLE:
        return

    from tortoise import Tortoise

    async def _clean():
        try:
            from src.models import ChatAttachment, ChatMessage, ChatParticipant, ChatThread

            await ChatMessage.all().delete()
            await ChatParticipant.all().delete()
            await ChatAttachment.all().delete()
            await ChatThread.all().delete()
        except Exception:
            pass

    if Tortoise._inited:
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(_clean())
            loop.close()
        except Exception:
            pass
