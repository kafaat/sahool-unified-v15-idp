"""Multi-date comparison helpers (composites, filmstrip, multi-date compare).

These helpers power the Phase-3 map visualization endpoints:

  * ``bucket_into_composites`` — groups a list of timeseries points into
    ``step_days``-sized windows and computes descriptive statistics
    (median / mean / min / max / p25 / p75) per bucket. Mirrors the
    EOSDA "7-day median composite" pattern.

  * ``sample_dates_at_interval`` — turns a ``(start, end, step_days)``
    window into a concrete list of ISO dates, capped at ``max_samples``
    to avoid runaway queries.

  * ``status_for_ndvi`` — single bilingual health-status mapping reused
    across the three endpoints (kept inline so we don't pull the full
    IndexInterpreter for a trivial NDVI categorisation).

Kept side-effect-free so the tests don't need the FastAPI app loaded.
"""

from __future__ import annotations

import statistics
from collections.abc import Iterable
from datetime import UTC, date, datetime, timedelta
from typing import Any

# Maximum filmstrip/compare samples. EOSDA/OneSoil cap at ~20 thumbnails;
# we honour the same ceiling so a 1-year + step_days=1 call doesn't OOM.
MAX_SAMPLES = 20

# Minimum sensible step — Sentinel-2 revisit is 5 days, so anything
# smaller than that is decorative but we allow it for development.
MIN_STEP_DAYS = 1
MAX_STEP_DAYS = 90


def _parse_iso(value: str | None, *, default: date) -> date:
    if not value:
        return default
    try:
        return date.fromisoformat(value)
    except ValueError as e:
        raise ValueError(f"Invalid ISO date: {value!r}") from e


def sample_dates_at_interval(
    start: str | None,
    end: str | None,
    step_days: int,
    *,
    max_samples: int = MAX_SAMPLES,
) -> list[str]:
    """Return ISO dates spaced ``step_days`` apart between *start* and *end*.

    Defaults: ``end=today``, ``start=end - 30 days``.
    Capped at ``max_samples`` — callers that need more must either
    loosen the cap or widen the step.
    """
    if step_days < MIN_STEP_DAYS or step_days > MAX_STEP_DAYS:
        raise ValueError(f"step_days must be in [{MIN_STEP_DAYS}, {MAX_STEP_DAYS}], got {step_days}")

    today = datetime.now(UTC).date()
    end_date = _parse_iso(end, default=today)
    start_date = _parse_iso(start, default=end_date - timedelta(days=30))

    if start_date > end_date:
        raise ValueError("start must be <= end")

    out: list[str] = []
    cursor = start_date
    while cursor <= end_date and len(out) < max_samples:
        out.append(cursor.isoformat())
        cursor = cursor + timedelta(days=step_days)
    # Ensure the last date is represented when the step doesn't land on it
    if out and out[-1] != end_date.isoformat() and len(out) < max_samples:
        out.append(end_date.isoformat())
    return out


def status_for_ndvi(value: float | None) -> dict[str, str]:
    """Bilingual health-status bucket for a single NDVI-like value.

    Shared across composite / filmstrip / multi-date-compare so the UI
    doesn't have to replicate the thresholds.
    """
    if value is None:
        return {"key": "unknown", "en": "Unknown", "ar": "غير معروف"}
    if value >= 0.6:
        return {"key": "excellent", "en": "Excellent", "ar": "ممتاز"}
    if value >= 0.4:
        return {"key": "good", "en": "Good", "ar": "جيد"}
    if value >= 0.2:
        return {"key": "moderate", "en": "Moderate", "ar": "متوسط"}
    return {"key": "poor", "en": "Poor", "ar": "ضعيف"}


def _pick_value(point: dict, index_name: str) -> float | None:
    """Pull *index_name* from a timeseries point, with graceful fallback.

    Timeseries points historically ship ``ndvi`` / ``ndwi`` / ``evi`` at
    top level (simulated path) or a nested ``indices`` dict (real path).
    Accept both so callers don't need to branch.
    """
    if index_name in point and isinstance(point[index_name], (int, float)):
        return float(point[index_name])
    nested = point.get("indices")
    if isinstance(nested, dict) and index_name in nested:
        raw = nested[index_name]
        if isinstance(raw, (int, float)):
            return float(raw)
    return None


def bucket_into_composites(
    points: Iterable[dict],
    *,
    index_name: str,
    step_days: int,
    start: str | None = None,
    end: str | None = None,
    stat: str = "median",
) -> list[dict[str, Any]]:
    """Group *points* into ``step_days``-sized buckets and summarise.

    Returns a list of dicts shaped:

        {
          "window_start": "YYYY-MM-DD",
          "window_end":   "YYYY-MM-DD",
          "mean":         0.62,
          "median":       0.61,
          "min":          0.51,
          "max":          0.70,
          "p25":          0.55,
          "p75":          0.66,
          "count":        3,
          "status":       {"key": "excellent", "en": "...", "ar": "..."},
        }

    ``stat`` decides which value is surfaced as the canonical one for
    health-status classification — "median" is the EOSDA default.
    """
    if step_days < MIN_STEP_DAYS or step_days > MAX_STEP_DAYS:
        raise ValueError(f"step_days must be in [{MIN_STEP_DAYS}, {MAX_STEP_DAYS}], got {step_days}")
    if stat not in {"median", "mean"}:
        raise ValueError(f"stat must be 'median' or 'mean', got {stat!r}")

    # Parse points into (date, value) pairs we actually care about.
    parsed: list[tuple[date, float]] = []
    for p in points:
        d = p.get("date")
        v = _pick_value(p, index_name)
        if not d or v is None:
            continue
        try:
            day = datetime.fromisoformat(d.replace("Z", "+00:00")).date()
        except ValueError:
            try:
                day = date.fromisoformat(d[:10])
            except ValueError:
                continue
        parsed.append((day, v))

    if not parsed:
        return []

    parsed.sort(key=lambda t: t[0])
    today = datetime.now(UTC).date()
    end_date = _parse_iso(end, default=parsed[-1][0] if parsed else today)
    start_date = _parse_iso(start, default=parsed[0][0])

    buckets: list[dict[str, Any]] = []
    cursor = start_date
    while cursor <= end_date:
        window_end = min(cursor + timedelta(days=step_days - 1), end_date)
        members = [v for (d_, v) in parsed if cursor <= d_ <= window_end]
        if members:
            chosen = statistics.median(members) if stat == "median" else statistics.fmean(members)
            summary = {
                "window_start": cursor.isoformat(),
                "window_end": window_end.isoformat(),
                "count": len(members),
                "mean": round(statistics.fmean(members), 4),
                "median": round(statistics.median(members), 4),
                "min": round(min(members), 4),
                "max": round(max(members), 4),
                "status": status_for_ndvi(chosen),
            }
            if len(members) >= 4:
                quantiles = statistics.quantiles(members, n=4)
                summary["p25"] = round(quantiles[0], 4)
                summary["p75"] = round(quantiles[2], 4)
            else:
                summary["p25"] = summary["min"]
                summary["p75"] = summary["max"]
            buckets.append(summary)
        cursor = window_end + timedelta(days=1)

    return buckets
