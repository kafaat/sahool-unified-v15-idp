"""
Unit tests for the Phase 2 weather-service graph renderer + URL store.

Tests cover:

* SVG generation for each metric type (temperature, precipitation,
  humidity, wind, combined)
* Language switching (ar RTL vs en LTR)
* Empty-series handling
* HMAC-signed URL round-trip (store → fetch)
* Tenant isolation (cross-tenant fetch must fail)
* Signature tampering detection
* TTL expiry
"""

from __future__ import annotations

import importlib.util
import os
import sys
from datetime import UTC, datetime, timedelta

import pytest


def _load_by_path(name: str, path: str):
    """
    Load a Python file as a module WITHOUT adding its parent directory
    to sys.path. We register the module in sys.modules before calling
    exec_module so @dataclass decorators can resolve the containing
    module via cls.__module__.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_renderer_mod = _load_by_path(
    "phase2_weather_renderer",
    os.path.join(
        _REPO_ROOT,
        "apps",
        "services",
        "weather-service",
        "src",
        "graph",
        "renderer.py",
    ),
)

DailyPoint = _renderer_mod.DailyPoint
GraphRequest = _renderer_mod.GraphRequest
GraphStore = _renderer_mod.GraphStore
WeatherGraphRenderer = _renderer_mod.WeatherGraphRenderer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_points() -> list[DailyPoint]:
    """14 days of realistic mid-summer wheat-field readings."""
    base = datetime(2026, 4, 1, tzinfo=UTC)
    points = []
    for i in range(14):
        points.append(
            DailyPoint(
                date=(base + timedelta(days=i)).strftime("%Y-%m-%d"),
                temp_min_c=18.0 + (i % 3) * 0.5,
                temp_max_c=32.0 + (i % 5),
                precipitation_mm=0.0 if i < 10 else 5.0 + i,
                humidity_pct=40.0 + (i % 4) * 5,
                wind_speed_kmh=10.0 + (i % 3) * 2,
            )
        )
    return points


@pytest.fixture
def renderer() -> WeatherGraphRenderer:
    return WeatherGraphRenderer()


@pytest.fixture
def store() -> GraphStore:
    return GraphStore(signing_secret="test-secret-32-characters-long-for-hmac")


# ---------------------------------------------------------------------------
# Renderer tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "metric", ["temperature", "precipitation", "humidity", "wind", "combined"]
)
def test_render_all_metrics(
    metric, renderer: WeatherGraphRenderer, sample_points: list[DailyPoint]
):
    req = GraphRequest(
        field_id="F-001",
        tenant_id="t-1",
        metric=metric,
        points=sample_points,
    )
    svg = renderer.render(req)
    assert svg.startswith("<?xml version=")
    assert "<svg" in svg
    # Title must appear (Arabic default)
    assert 'font-size="18"' in svg
    # Viewbox matches renderer constants
    assert f'viewBox="0 0 {renderer.WIDTH} {renderer.HEIGHT}"' in svg


def test_render_arabic_is_rtl(
    renderer: WeatherGraphRenderer, sample_points: list[DailyPoint]
):
    req = GraphRequest(
        field_id="F-001",
        tenant_id="t-1",
        metric="temperature",
        points=sample_points,
        language="ar",
    )
    svg = renderer.render(req)
    assert 'direction="rtl"' in svg
    assert "Noto Sans Arabic" in svg


def test_render_english_is_ltr(
    renderer: WeatherGraphRenderer, sample_points: list[DailyPoint]
):
    req = GraphRequest(
        field_id="F-001",
        tenant_id="t-1",
        metric="temperature",
        points=sample_points,
        language="en",
    )
    svg = renderer.render(req)
    assert 'direction="ltr"' in svg
    assert "Daily Temperatures" in svg


def test_render_empty_points_returns_no_data_svg(renderer: WeatherGraphRenderer):
    req = GraphRequest(
        field_id="F-empty", tenant_id="t-1", metric="temperature", points=[]
    )
    svg = renderer.render(req)
    assert "<svg" in svg
    # Arabic "no data" message
    assert "لا توجد بيانات" in svg


def test_render_single_point_does_not_crash(renderer: WeatherGraphRenderer):
    req = GraphRequest(
        field_id="F-one",
        tenant_id="t-1",
        metric="humidity",
        points=[DailyPoint(date="2026-04-11", humidity_pct=55.0)],
    )
    svg = renderer.render(req)
    assert "<svg" in svg


def test_render_none_values_filter_out(renderer: WeatherGraphRenderer):
    # All values None — should render gracefully (no polylines)
    req = GraphRequest(
        field_id="F-none",
        tenant_id="t-1",
        metric="temperature",
        points=[
            DailyPoint(date="2026-04-01", temp_max_c=None, temp_min_c=None),
            DailyPoint(date="2026-04-02", temp_max_c=None, temp_min_c=None),
        ],
    )
    svg = renderer.render(req)
    assert "<svg" in svg
    # No polyline points were generated
    assert "<polyline" not in svg


def test_value_bounds_handles_all_none():
    vmin, vmax = WeatherGraphRenderer._value_bounds([None, None])
    assert vmin < vmax  # Always a valid interval


def test_value_bounds_handles_single_value():
    vmin, vmax = WeatherGraphRenderer._value_bounds([7.0])
    assert vmin < vmax  # Pads to avoid degenerate axis


def test_escape_html_entities(renderer: WeatherGraphRenderer):
    req = GraphRequest(
        field_id='<script>alert("xss")</script>',
        tenant_id="t-1",
        metric="temperature",
        points=[
            DailyPoint(date='<script>', temp_max_c=25.0, temp_min_c=15.0),
        ],
    )
    svg = renderer.render(req)
    # The dangerous tag must have been escaped in rendered content
    assert "<script>" not in svg or "&lt;script&gt;" in svg


# ---------------------------------------------------------------------------
# Store tests — signing, fetching, tenant isolation, TTL
# ---------------------------------------------------------------------------


def test_store_and_fetch_roundtrip(store: GraphStore):
    svg = "<svg>hello</svg>"
    graph_id, url_path, expires_at = store.store(
        svg, field_id="F-1", tenant_id="t-1"
    )
    # URL path format check
    assert graph_id in url_path
    assert "tid=t-1" in url_path
    assert "sig=" in url_path
    assert expires_at > datetime.now(UTC)

    # Extract signature from url_path
    sig = url_path.split("sig=")[1]
    fetched = store.fetch(graph_id, tenant_id="t-1", signature=sig)
    assert fetched == svg


def test_fetch_rejects_wrong_tenant(store: GraphStore):
    svg = "<svg>tenant-test</svg>"
    graph_id, url_path, _ = store.store(svg, field_id="F-1", tenant_id="t-1")
    sig = url_path.split("sig=")[1]
    # Attempt to fetch as a different tenant with same signature
    fetched = store.fetch(graph_id, tenant_id="t-OTHER", signature=sig)
    assert fetched is None


def test_fetch_rejects_tampered_signature(store: GraphStore):
    svg = "<svg>sig-test</svg>"
    graph_id, _, _ = store.store(svg, field_id="F-1", tenant_id="t-1")
    bogus = "a" * 43  # base64-urlsafe of SHA-256 is 43 chars
    assert store.fetch(graph_id, tenant_id="t-1", signature=bogus) is None


def test_fetch_unknown_graph_id(store: GraphStore):
    assert store.fetch("nonexistent", tenant_id="t-1", signature="x") is None


def test_expired_graph_evicted(store: GraphStore):
    # Manually inject an already-expired entry
    expired_at = datetime.now(UTC) - timedelta(seconds=1)
    store._store["expired-id"] = ("<svg/>", expired_at, "F-1", "t-1")
    sig = store._sign("expired-id", "t-1")
    assert store.fetch("expired-id", tenant_id="t-1", signature=sig) is None
    # Expired entry was garbage-collected on fetch attempt
    assert "expired-id" not in store._store
