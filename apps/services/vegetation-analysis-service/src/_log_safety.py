"""
Log-injection sanitisation helper for the vegetation-analysis-service.

Centralises the small helper that several modules (cache, change_detector,
cloud_masking, eo_integration, sar_processor, boundary_endpoints) use to
neutralise user-supplied values before emitting them through Python's
``logging`` framework.

The implementation uses an explicit ``str.replace`` chain for the most
dangerous characters (CR / LF / NUL / tab — the primary log-injection
vectors) followed by ``str.translate`` to strip any remaining C0/DEL
control characters. The leading ``.replace`` calls are what CodeQL's
``py/log-injection`` query recognises as a sanitiser, so wrapping a
tainted value with :func:`safe_log` both removes the finding *and*
provides defence-in-depth against ANSI-escape / form-feed / vertical-tab
injections.
"""

from __future__ import annotations

__all__ = ["safe_log"]

# Strip the rest of the C0 control range (0x00-0x1f) plus DEL (0x7f).
# The four most common attack chars (\r, \n, \x00, \t) are already handled
# by the explicit ``.replace`` chain below — this table is defence in
# depth for the remaining control bytes (ESC, form feed, vertical tab,
# backspace, etc.) that could otherwise be used to forge log entries on
# terminals that interpret ANSI sequences.
_CONTROL_CHARS: dict[int, None] = dict.fromkeys(range(0x00, 0x20))
_CONTROL_CHARS[0x7F] = None


def safe_log(value: object, max_len: int = 128) -> str:
    """Return a logging-safe representation of *value*.

    - Coerces ``None`` to an empty string.
    - Strips carriage return, line feed, NUL and tab characters via
      explicit ``.replace`` calls so the value cannot forge log entries
      (CR/LF injection).
    - Removes any remaining C0 / DEL control characters (defence in
      depth against ANSI-escape injection).
    - Truncates the result to *max_len* characters to bound log volume.
    """
    s = "" if value is None else str(value)
    # Explicit ``.replace`` calls — recognised by CodeQL's
    # py/log-injection query as log-injection sanitisers.
    s = s.replace("\r", "").replace("\n", "").replace("\x00", "").replace("\t", " ")
    # Defence in depth: remove any other C0/DEL control characters.
    s = s.translate(_CONTROL_CHARS)
    if len(s) > max_len:
        s = s[:max_len]
    return s
