"""Test configuration for audit-retention-worker.

CI runs `pytest apps/services/` from the repo root. Multiple services
export a `src/` package, so pytest's auto-collection can import the
wrong `src` into sys.modules and subsequent test files in OTHER
services pick up the cached version. Without this conftest the
retention worker's tests intermittently fail with errors like
`AttributeError: module 'src.retention' has no attribute …` when a
sibling service's `src.retention` (if any) gets imported first.

Mirrors apps/services/audit-service/tests/conftest.py — same pattern,
same justification.
"""

import os
import sys

# 1. Ensure this service's root is on sys.path so `import src.retention`
#    resolves to THIS service's module, not a sibling's.
_SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)

# 2. Evict any cached `src`/`src.*` modules that don't belong to THIS
#    service. If a previous test run imported a sibling's src package,
#    it would be cached under the same name and win on name lookup.
for _mod_name in list(sys.modules):
    if not (_mod_name == "src" or _mod_name.startswith("src.")):
        continue
    _mod_obj = sys.modules.get(_mod_name)
    _mod_file = getattr(_mod_obj, "__file__", None) or ""
    if not _mod_file or not os.path.abspath(_mod_file).startswith(_SERVICE_ROOT):
        del sys.modules[_mod_name]
