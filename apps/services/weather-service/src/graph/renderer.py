"""
Server-side weather graph renderer.

Emits a self-contained SVG chart for a series of daily weather values
(temperature, precipitation, humidity, wind). Zero dependencies — we
build the SVG by hand so the weather service doesn't need to ship
matplotlib, plotly, or a headless browser.

The chart is stored in-memory + served back via a signed URL at
`GET /api/v1/weather/graphs/{graph_id}`. This mirrors the Farmonaut
`get-past-weather-graph` pattern where the API returns a URL and the
client loads the image as an <img src="..."> — much lighter on the
mobile client than shipping the JSON and building a chart in Dart.

Each SVG is ~5-15 KB and renders identically on any modern browser
(including Chrome Android, mobile Safari, and Flutter's WebView).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Literal

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


GraphMetric = Literal["temperature", "precipitation", "humidity", "wind", "combined"]


@dataclass
class DailyPoint:
    """One day of weather observations."""

    date: str  # ISO 8601 date (YYYY-MM-DD)
    temp_min_c: float | None = None
    temp_max_c: float | None = None
    precipitation_mm: float | None = None
    humidity_pct: float | None = None
    wind_speed_kmh: float | None = None


@dataclass
class GraphRequest:
    field_id: str
    tenant_id: str
    metric: GraphMetric
    points: list[DailyPoint]
    language: Literal["ar", "en"] = "ar"
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------


# Theme — matches SAHOOL web + mobile brand colours.
_THEME = {
    "bg": "#ffffff",
    "grid": "#e5e7eb",
    "axis": "#6b7280",
    "text": "#1f2937",
    "temp_min": "#60a5fa",
    "temp_max": "#f87171",
    "precipitation": "#22c55e",
    "humidity": "#0ea5e9",
    "wind": "#a78bfa",
    "title": "#166534",
}


class WeatherGraphRenderer:
    """Generates SVG weather charts for per-field history."""

    WIDTH = 720
    HEIGHT = 360
    MARGIN_LEFT = 56
    MARGIN_RIGHT = 24
    MARGIN_TOP = 48
    MARGIN_BOTTOM = 44

    @property
    def plot_w(self) -> int:
        return self.WIDTH - self.MARGIN_LEFT - self.MARGIN_RIGHT

    @property
    def plot_h(self) -> int:
        return self.HEIGHT - self.MARGIN_TOP - self.MARGIN_BOTTOM

    def render(self, req: GraphRequest) -> str:
        """Return the SVG as a UTF-8 string."""
        if not req.points:
            return self._empty_svg(req)

        title = self._title_for(req)
        body = self._plot_body(req)
        axes = self._axes(req)
        footer = self._footer(req)

        direction = "rtl" if req.language == "ar" else "ltr"
        font_family = (
            "'Noto Sans Arabic','Tajawal','Cairo',sans-serif"
            if req.language == "ar"
            else "-apple-system,'Segoe UI',Roboto,Arial,sans-serif"
        )

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.WIDTH} {self.HEIGHT}" width="{self.WIDTH}" height="{self.HEIGHT}" font-family="{font_family}" direction="{direction}">
  <rect width="100%" height="100%" fill="{_THEME["bg"]}"/>
  <text x="{self.WIDTH // 2}" y="28" text-anchor="middle" fill="{_THEME["title"]}" font-size="18" font-weight="700">{self._esc(title)}</text>
  {axes}
  {body}
  {footer}
</svg>"""

    # ------------------------------------------------------------------
    # Drawing primitives
    # ------------------------------------------------------------------

    def _plot_body(self, req: GraphRequest) -> str:
        metric = req.metric
        if metric == "temperature":
            return self._line_series(req, "temp_max_c", _THEME["temp_max"]) + self._line_series(
                req, "temp_min_c", _THEME["temp_min"]
            )
        if metric == "precipitation":
            return self._bar_series(req, "precipitation_mm", _THEME["precipitation"])
        if metric == "humidity":
            return self._line_series(req, "humidity_pct", _THEME["humidity"])
        if metric == "wind":
            return self._line_series(req, "wind_speed_kmh", _THEME["wind"])
        # combined: temperature + precipitation overlay
        return (
            self._bar_series(req, "precipitation_mm", _THEME["precipitation"])
            + self._line_series(req, "temp_max_c", _THEME["temp_max"])
            + self._line_series(req, "temp_min_c", _THEME["temp_min"])
        )

    def _line_series(self, req: GraphRequest, attr: str, colour: str) -> str:
        values = [getattr(p, attr) for p in req.points]
        if not any(v is not None for v in values):
            return ""
        vmin, vmax = self._value_bounds(values)
        n = len(req.points)
        points = []
        for i, v in enumerate(values):
            if v is None:
                continue
            x = self.MARGIN_LEFT + (i / max(n - 1, 1)) * self.plot_w
            y = self.MARGIN_TOP + self.plot_h - ((v - vmin) / max(vmax - vmin, 0.01)) * self.plot_h
            points.append(f"{x:.1f},{y:.1f}")
        if not points:
            return ""
        return (
            f'<polyline points="{" ".join(points)}" fill="none" '
            f'stroke="{colour}" stroke-width="2.5" stroke-linecap="round" '
            f'stroke-linejoin="round"/>'
        )

    def _bar_series(self, req: GraphRequest, attr: str, colour: str) -> str:
        values = [getattr(p, attr) for p in req.points]
        if not any(v is not None and v > 0 for v in values):
            return ""
        vmax = max((v for v in values if v is not None), default=1.0) or 1.0
        n = len(req.points)
        bar_w = self.plot_w / n * 0.7
        bars = []
        for i, v in enumerate(values):
            if v is None or v <= 0:
                continue
            x = self.MARGIN_LEFT + (i / max(n - 1, 1)) * self.plot_w - bar_w / 2
            h = (v / vmax) * self.plot_h
            y = self.MARGIN_TOP + self.plot_h - h
            bars.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" fill="{colour}" opacity="0.75"/>'
            )
        return "".join(bars)

    def _axes(self, req: GraphRequest) -> str:
        # Gridlines + left Y axis + bottom X axis labels.
        parts = []
        # Grid
        for i in range(5):
            y = self.MARGIN_TOP + (i / 4) * self.plot_h
            parts.append(
                f'<line x1="{self.MARGIN_LEFT}" y1="{y:.1f}" '
                f'x2="{self.WIDTH - self.MARGIN_RIGHT}" y2="{y:.1f}" '
                f'stroke="{_THEME["grid"]}" stroke-width="1"/>'
            )
        # Bottom axis
        parts.append(
            f'<line x1="{self.MARGIN_LEFT}" y1="{self.HEIGHT - self.MARGIN_BOTTOM}" '
            f'x2="{self.WIDTH - self.MARGIN_RIGHT}" y2="{self.HEIGHT - self.MARGIN_BOTTOM}" '
            f'stroke="{_THEME["axis"]}" stroke-width="1.5"/>'
        )
        # Date labels (first, middle, last — avoid clutter on long series)
        n = len(req.points)
        if n > 0:
            indices = {0, n // 2, n - 1} if n >= 3 else {0, n - 1}
            for i in sorted(indices):
                x = self.MARGIN_LEFT + (i / max(n - 1, 1)) * self.plot_w
                y = self.HEIGHT - self.MARGIN_BOTTOM + 16
                parts.append(
                    f'<text x="{x:.1f}" y="{y}" text-anchor="middle" '
                    f'fill="{_THEME["axis"]}" font-size="10">'
                    f"{self._esc(req.points[i].date)}</text>"
                )
        return "".join(parts)

    def _footer(self, req: GraphRequest) -> str:
        if req.language == "ar":
            label = f"مُوَلَّد في {req.timestamp.strftime('%Y-%m-%d %H:%M UTC')}"
        else:
            label = f"Generated {req.timestamp.strftime('%Y-%m-%d %H:%M UTC')}"
        return (
            f'<text x="{self.WIDTH - self.MARGIN_RIGHT}" '
            f'y="{self.HEIGHT - 8}" text-anchor="end" '
            f'fill="{_THEME["axis"]}" font-size="10">{self._esc(label)}</text>'
        )

    def _empty_svg(self, req: GraphRequest) -> str:
        msg = "لا توجد بيانات" if req.language == "ar" else "No data"
        return (
            f'<?xml version="1.0" encoding="UTF-8"?>'
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {self.WIDTH} {self.HEIGHT}" '
            f'width="{self.WIDTH}" height="{self.HEIGHT}">'
            f'<rect width="100%" height="100%" fill="{_THEME["bg"]}"/>'
            f'<text x="{self.WIDTH // 2}" y="{self.HEIGHT // 2}" '
            f'text-anchor="middle" fill="{_THEME["axis"]}" font-size="16">'
            f"{msg}</text></svg>"
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _title_for(self, req: GraphRequest) -> str:
        titles_ar = {
            "temperature": "درجات الحرارة اليومية",
            "precipitation": "هطول الأمطار اليومي",
            "humidity": "الرطوبة النسبية",
            "wind": "سرعة الرياح",
            "combined": "نظرة عامة على الطقس",
        }
        titles_en = {
            "temperature": "Daily Temperatures",
            "precipitation": "Daily Precipitation",
            "humidity": "Relative Humidity",
            "wind": "Wind Speed",
            "combined": "Weather Overview",
        }
        return (titles_ar if req.language == "ar" else titles_en)[req.metric]

    @staticmethod
    def _value_bounds(values: list[float | None]) -> tuple[float, float]:
        finite = [v for v in values if v is not None]
        if not finite:
            return (0.0, 1.0)
        vmin, vmax = min(finite), max(finite)
        if vmin == vmax:
            vmin -= 1
            vmax += 1
        return (vmin, vmax)

    @staticmethod
    def _esc(s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ---------------------------------------------------------------------------
# URL signing + in-memory store
# ---------------------------------------------------------------------------


class GraphStore:
    """
    Minimal in-memory graph cache. Each generated SVG is keyed by a
    random graph_id and served via GET /api/v1/weather/graphs/{graph_id}.
    The URL carries an HMAC signature so un-authorised clients can't
    guess graph IDs.

    Cache TTL is 2 hours by default (long enough for the user to load
    the page and refresh a few times, short enough that stale data
    doesn't pile up). On process restart the cache is lost — clients
    re-request and the graph regenerates.
    """

    TTL_SECONDS = 2 * 60 * 60

    def __init__(self, signing_secret: str | None = None):
        self._store: dict[str, tuple[str, datetime, str, str]] = {}
        self._secret = signing_secret or os.getenv(
            "WEATHER_GRAPH_SIGNING_SECRET",
            "dev-change-me-in-production",  # nosec B105 - dev fallback only
        )

    def store(self, svg: str, field_id: str, tenant_id: str) -> tuple[str, str, datetime]:
        """
        Persist an SVG + return (graph_id, signed_url_path, expires_at).
        The caller prepends its own scheme+host for the full URL.
        """
        graph_id = secrets.token_urlsafe(16)
        expires_at = datetime.now(UTC) + timedelta(seconds=self.TTL_SECONDS)
        self._store[graph_id] = (svg, expires_at, field_id, tenant_id)
        signature = self._sign(graph_id, tenant_id)
        url_path = f"/api/v1/weather/graphs/{graph_id}?tid={tenant_id}&sig={signature}"
        self._gc_expired()
        return graph_id, url_path, expires_at

    def fetch(self, graph_id: str, tenant_id: str, signature: str) -> str | None:
        """Return SVG if found + signature valid, None otherwise."""
        row = self._store.get(graph_id)
        if not row:
            return None
        svg, expires_at, _, stored_tenant = row
        if datetime.now(UTC) > expires_at:
            self._store.pop(graph_id, None)
            return None
        if stored_tenant != tenant_id:
            return None
        if not hmac.compare_digest(signature, self._sign(graph_id, tenant_id)):
            return None
        return svg

    def _sign(self, graph_id: str, tenant_id: str) -> str:
        msg = f"{graph_id}:{tenant_id}".encode()
        digest = hmac.new(self._secret.encode(), msg, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")

    def _gc_expired(self) -> None:
        now = datetime.now(UTC)
        stale = [k for k, v in self._store.items() if v[1] < now]
        for k in stale:
            self._store.pop(k, None)
