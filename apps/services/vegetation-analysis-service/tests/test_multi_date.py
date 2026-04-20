"""Regression tests for Phase-3 multi-date helpers + endpoints.

Pins:
  * ``sample_dates_at_interval`` — step validation, cap enforcement,
    end-date inclusion.
  * ``bucket_into_composites`` — bucket boundaries, quantile output,
    status classification, degenerate inputs, stat='median' vs 'mean'.
  * ``status_for_ndvi`` — threshold table matches the UI.
  * The three endpoints exist in main.py with the correct path,
  verify auth + ownership, and only accept mappable indices.
"""

from __future__ import annotations

import ast
import os
import sys
from datetime import UTC, date, datetime, timedelta

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from multi_date import (  # noqa: E402
    MAX_SAMPLES,
    bucket_into_composites,
    sample_dates_at_interval,
    status_for_ndvi,
)

_MAIN_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "main.py")
with open(_MAIN_PATH, encoding="utf-8") as _f:
    _MAIN_SRC = _f.read()
_MAIN_AST = ast.parse(_MAIN_SRC)


# =============================================================================
# sample_dates_at_interval
# =============================================================================


def test_sample_dates_defaults_to_last_30_days():
    today = datetime.now(UTC).date().isoformat()
    out = sample_dates_at_interval(None, None, 7)
    assert out[-1] == today
    assert len(out) >= 4  # ~30/7 + end cap


def test_sample_dates_respects_explicit_window():
    out = sample_dates_at_interval("2026-01-01", "2026-01-22", 7)
    assert out == ["2026-01-01", "2026-01-08", "2026-01-15", "2026-01-22"]


def test_sample_dates_appends_end_when_step_misaligned():
    """When the step doesn't land exactly on `end`, the end must still
    be represented — otherwise the filmstrip would drop the most
    recent acquisition."""
    out = sample_dates_at_interval("2026-01-01", "2026-01-25", 7)
    assert out[-1] == "2026-01-25"
    assert "2026-01-22" in out


def test_sample_dates_caps_at_max_samples():
    out = sample_dates_at_interval("2020-01-01", "2026-01-01", 1)
    assert len(out) <= MAX_SAMPLES


def test_sample_dates_preserves_end_date_when_at_cap():
    """Regression pin (Copilot review #1704 round 2): when the loop
    fills ``max_samples`` before reaching ``end_date``, the most recent
    acquisition must NOT be silently dropped — it must replace the
    last entry. Otherwise filmstrip/compare views show a window that
    ends arbitrary days before the user-selected range."""
    out = sample_dates_at_interval("2026-01-01", "2026-06-01", 1, max_samples=5)
    assert len(out) == 5
    assert out[-1] == "2026-06-01", f"end_date dropped on cap; got {out!r}"


def test_sample_dates_does_not_replace_when_end_already_sampled():
    """Edge: when the loop naturally lands on end_date as its last
    sample, we must not overwrite a valid entry."""
    out = sample_dates_at_interval("2026-01-01", "2026-01-08", 7, max_samples=5)
    # step=7 hits 2026-01-01 and 2026-01-08 exactly; both should remain
    assert out == ["2026-01-01", "2026-01-08"]


@pytest.mark.parametrize("step", [0, -1, 91, 365])
def test_sample_dates_rejects_invalid_step(step):
    with pytest.raises(ValueError):
        sample_dates_at_interval(None, None, step)


def test_sample_dates_rejects_inverted_window():
    with pytest.raises(ValueError):
        sample_dates_at_interval("2026-02-01", "2026-01-01", 7)


# =============================================================================
# bucket_into_composites
# =============================================================================


def _synthetic_points(values: list[float], *, start: str = "2026-01-01") -> list[dict]:
    """Emit one timeseries point per value at 1-day cadence."""
    base = date.fromisoformat(start)
    return [{"date": (base + timedelta(days=i)).isoformat(), "ndvi": v} for i, v in enumerate(values)]


def test_bucket_groups_by_step_days():
    points = _synthetic_points([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.4], start="2026-01-01")
    buckets = bucket_into_composites(points, index_name="ndvi", step_days=3)

    # 7 days, step=3 → buckets: [Jan1-3], [Jan4-6], [Jan7-7]
    assert len(buckets) == 3
    first = buckets[0]
    assert first["window_start"] == "2026-01-01"
    assert first["window_end"] == "2026-01-03"
    assert first["count"] == 3
    assert first["mean"] == pytest.approx(0.6)
    assert first["median"] == pytest.approx(0.6)


def test_bucket_computes_p25_p75_when_enough_samples():
    points = _synthetic_points([0.2, 0.4, 0.6, 0.8, 1.0], start="2026-01-01")
    buckets = bucket_into_composites(points, index_name="ndvi", step_days=7)
    assert len(buckets) == 1
    b = buckets[0]
    assert 0.2 < b["p25"] < b["p75"] < 1.0


def test_bucket_falls_back_to_min_max_when_few_samples():
    points = _synthetic_points([0.3, 0.7], start="2026-01-01")
    buckets = bucket_into_composites(points, index_name="ndvi", step_days=7)
    assert len(buckets) == 1
    b = buckets[0]
    assert b["p25"] == b["min"] == 0.3
    assert b["p75"] == b["max"] == 0.7


def test_bucket_status_uses_chosen_stat():
    """With stat='median', the status classification must be driven by
    the median value, not the mean — so a skewed outlier can't move
    the bucket from 'good' to 'excellent'."""
    points = _synthetic_points([0.4, 0.4, 0.4, 0.4, 0.95], start="2026-01-01")
    med = bucket_into_composites(points, index_name="ndvi", step_days=7, stat="median")
    mean = bucket_into_composites(points, index_name="ndvi", step_days=7, stat="mean")
    assert med[0]["status"]["key"] == "good"
    assert mean[0]["status"]["key"] in {"good", "excellent"}  # outlier can shift it


def test_bucket_handles_nested_indices_dict():
    """Real-path timeseries ships {date, indices: {ndre: 0.4, ...}}
    instead of flat fields. The bucketing must handle both shapes."""
    points = [
        {"date": "2026-01-01", "indices": {"ndre": 0.3}},
        {"date": "2026-01-02", "indices": {"ndre": 0.5}},
    ]
    buckets = bucket_into_composites(points, index_name="ndre", step_days=7)
    assert len(buckets) == 1
    assert buckets[0]["mean"] == pytest.approx(0.4)


def test_bucket_skips_points_missing_index():
    """Points that don't carry the requested index must not inflate
    counts nor pull averages towards 0."""
    points = [
        {"date": "2026-01-01", "ndvi": 0.5},
        {"date": "2026-01-02", "ndwi": 0.3},  # different index
        {"date": "2026-01-03", "ndvi": 0.7},
    ]
    buckets = bucket_into_composites(points, index_name="ndvi", step_days=7)
    assert buckets[0]["count"] == 2
    assert buckets[0]["mean"] == pytest.approx(0.6)


def test_bucket_returns_empty_for_no_matching_points():
    points = [{"date": "2026-01-01", "savi": 0.5}]
    assert bucket_into_composites(points, index_name="ndvi", step_days=7) == []


@pytest.mark.parametrize("stat", ["worst", "", "sum"])
def test_bucket_rejects_unsupported_stat(stat):
    with pytest.raises(ValueError):
        bucket_into_composites([], index_name="ndvi", step_days=7, stat=stat)


# =============================================================================
# status_for_ndvi
# =============================================================================


@pytest.mark.parametrize(
    "value,expected",
    [
        (0.9, "excellent"),
        (0.6, "excellent"),
        (0.5, "good"),
        (0.4, "good"),
        (0.3, "moderate"),
        (0.2, "moderate"),
        (0.1, "poor"),
        (-0.1, "poor"),
        (None, "unknown"),
    ],
)
def test_status_thresholds(value, expected):
    assert status_for_ndvi(value)["key"] == expected


def test_status_always_bilingual():
    s = status_for_ndvi(0.6)
    assert s["en"] and s["ar"]


# =============================================================================
# Endpoint AST pins
# =============================================================================


def _find_route(method: str, path: str):
    for node in ast.walk(_MAIN_AST):
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        for deco in node.decorator_list:
            if not isinstance(deco, ast.Call):
                continue
            if not isinstance(deco.func, ast.Attribute):
                continue
            if deco.func.attr != method:
                continue
            if deco.args and isinstance(deco.args[0], ast.Constant):
                if deco.args[0].value == path:
                    return node
    return None


def test_composite_endpoint_registered():
    node = _find_route("get", "/v1/indices/{field_id}/{index_name}/composite")
    assert node is not None
    src = ast.get_source_segment(_MAIN_SRC, node) or ""
    assert "get_current_user" in src
    assert "_verify_field_owned_by_tenant" in src
    assert "_MAPPABLE_INDICES" in src
    assert "bucket_into_composites" in src


def test_filmstrip_endpoint_registered():
    node = _find_route("get", "/v1/indices/{field_id}/{index_name}/filmstrip")
    assert node is not None
    src = ast.get_source_segment(_MAIN_SRC, node) or ""
    assert "get_current_user" in src
    assert "_verify_field_owned_by_tenant" in src
    assert "_MAPPABLE_INDICES" in src
    # Filmstrip must ship rasterUrl per frame for the carousel UI.
    assert "rasterUrl" in src


def test_multi_date_compare_endpoint_registered():
    node = _find_route("post", "/v1/indices/{field_id}/{index_name}/multi-date-compare")
    assert node is not None
    src = ast.get_source_segment(_MAIN_SRC, node) or ""
    assert "get_current_user" in src
    assert "_verify_field_owned_by_tenant" in src
    assert "_MAPPABLE_INDICES" in src
    # Guard against the legacy 2-only behaviour creeping back in.
    assert "delta_from_previous" in src


def test_multi_date_compare_has_request_model():
    """The body validator (`MultiDateCompareRequest`) must be present —
    without it the 12-date cap is only honoured at runtime."""
    names = {n.name for n in ast.walk(_MAIN_AST) if isinstance(n, ast.ClassDef) and n.name == "MultiDateCompareRequest"}
    assert "MultiDateCompareRequest" in names
