"""
Log-injection sanitisation helper for the vegetation-analysis-service.

Centralises the small helper that several modules (cache, change_detector,
cloud_masking, eo_integration, sar_processor, boundary_endpoints) use to
neutralise user-supplied values before emitting them through Python's
``logging`` framework.

The implementation uses an explicit ``str.replace`` chain. CodeQL's
``py/log-injection`` query recognises this pattern as a sanitiser, so
wrapping a tainted value with :func:`safe_log` removes the log-injection
finding without relying on opaque regex substitution.
"""

from __future__ import annotations

__all__ = ["safe_log"]


def safe_log(value: object, max_len: int = 128) -> str:
    """Return a logging-safe representation of *value*.

    - Coerces ``None`` to an empty string.
    - Strips carriage return, line feed, NUL and tab characters so the
      value cannot forge log entries (CR/LF injection) or corrupt
      structured log parsers.
    - Truncates the result to *max_len* characters to bound log volume.
    """
    s = "" if value is None else str(value)
    # Explicit ``.replace`` calls — recognised by CodeQL's py/log-injection
    # query as log-injection sanitisers.
    s = s.replace("\r", "").replace("\n", "").replace("\x00", "").replace("\t", " ")
    if len(s) > max_len:
        s = s[:max_len]
    return s
