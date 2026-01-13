"""
Pytest configuration for yield-engine tests
تكوين pytest لاختبارات محرك الإنتاجية
"""

import os
import sys
from pathlib import Path

# Get the service root directory (yield-engine/)
service_root = Path(__file__).parent.parent
src_path = service_root / "src"
repo_root = service_root.parent.parent.parent

# Add paths to sys.path for proper imports
# إضافة المسارات لاستيراد الوحدات بشكل صحيح
sys.path.insert(0, str(service_root))
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "apps" / "services"))

# Mock shared.errors_py if not available (for isolated testing)
try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers
except ImportError:
    # Create mock functions if shared module not available
    import sys
    from unittest.mock import MagicMock

    mock_errors_py = MagicMock()
    mock_errors_py.add_request_id_middleware = MagicMock()
    mock_errors_py.setup_exception_handlers = MagicMock()
    sys.modules["shared"] = MagicMock()
    sys.modules["shared.errors_py"] = mock_errors_py
