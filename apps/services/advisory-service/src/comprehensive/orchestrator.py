"""
Comprehensive (Jeevn-style) advisory module.

Aggregates per-field insights from multiple SAHOOL services into a
single response — the agricultural equivalent of a "dashboard in one
request":

    POST /api/v1/advisory/comprehensive/{field_id}

returns, in one payload:
    * nutrients   — NPK + Zn + S + pH recommendations
    * pests       — active pest predictions + IPM actions
    * diseases    — disease risk + preventive actions
    * irrigation  — next-irrigation advice + water balance
    * weather     — short-range forecast + agronomic flags
    * yield       — current yield forecast + confidence
    * carbon      — per-season carbon balance (NEW in Phase 2)
    * alerts      — active alerts merged from alert-service

This matches the user experience of Farmonaut's Jeevn AI (one question
→ comprehensive answer) without forcing the web/mobile client to
orchestrate ten downstream calls. The orchestration, graceful-
degradation, and bilingual Arabic/English messaging all live here.

Graceful degradation: each downstream call is wrapped in try/except
with a hard timeout. If a service is down, its section comes back as
`null` with a `degraded: true` flag in the envelope — the comprehensive
response still returns the data from the services that DID respond.
This matches the platform convention of never failing an aggregate
call because of one slow dependency.
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx
import structlog

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Service URL registry (resolved from env vars per platform convention)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ServiceUrls:
    field_management: str
    weather: str
    irrigation_smart: str
    soil_analysis: str
    pest_detection: str
    crop_intelligence: str
    yield_prediction: str
    vegetation_analysis: str
    carbon: str
    alerts: str

    @classmethod
    def from_env(cls, env: dict[str, str]) -> ServiceUrls:
        return cls(
            field_management=env.get("FIELD_MANAGEMENT_URL", "http://field-management-service:3000"),
            weather=env.get("WEATHER_SERVICE_URL", "http://weather-service:8092"),
            irrigation_smart=env.get("IRRIGATION_SMART_URL", "http://irrigation-smart:8094"),
            soil_analysis=env.get("SOIL_ANALYSIS_URL", "http://soil-analysis-service:8134"),
            pest_detection=env.get("PEST_DETECTION_URL", "http://pest-detection-service:8125"),
            crop_intelligence=env.get("CROP_INTELLIGENCE_URL", "http://crop-intelligence-service:8095"),
            yield_prediction=env.get("YIELD_PREDICTION_URL", "http://yield-prediction-service:8152"),
            vegetation_analysis=env.get(
                "VEGETATION_ANALYSIS_URL",
                "http://vegetation-analysis-service:8090",
            ),
            carbon=env.get("CARBON_SERVICE_URL", "http://carbon-service:8195"),
            alerts=env.get("ALERT_SERVICE_URL", "http://alert-service:8113"),
        )


# ---------------------------------------------------------------------------
# Per-section result wrappers
# ---------------------------------------------------------------------------


@dataclass
class Section:
    """Envelope for a single downstream call's result."""

    data: Any | None
    degraded: bool
    latency_ms: float
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "data": self.data,
            "degraded": self.degraded,
            "latency_ms": round(self.latency_ms, 1),
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# The orchestrator
# ---------------------------------------------------------------------------


class ComprehensiveAdvisoryOrchestrator:
    """
    Fans out parallel calls to downstream services, applies a per-call
    timeout, and assembles the unified response. Does NOT cache — that's
    the caller's (Kong / web client) responsibility.
    """

    DEFAULT_TIMEOUT_SEC = 8.0

    def __init__(self, urls: ServiceUrls, timeout: float | None = None):
        self.urls = urls
        self.timeout = timeout or self.DEFAULT_TIMEOUT_SEC

    async def collect(
        self,
        field_id: str,
        tenant_id: str,
        auth_header: str | None = None,
    ) -> dict[str, Any]:
        """
        Call all downstream services in parallel. Returns a dict
        with one key per section plus a top-level summary:

          {
            "field_id": "...",
            "generated_at": "...",
            "overall_status": "healthy|degraded|critical",
            "sections": {
              "nutrients": { "data": ..., "degraded": ..., ... },
              "pests": { ... },
              ...
            },
            "alerts_count": 3,
            "sources_degraded": 1,
            "latency_ms_total": 1234
          }
        """
        headers = self._headers(tenant_id, auth_header)

        # SECURITY: defense-in-depth — even though the FastAPI endpoint
        # already validates field_id against ^[A-Za-z0-9_-]+$, we also
        # URL-encode it here so any future code path that bypasses the
        # endpoint (direct orchestrator instantiation in tests, internal
        # service-to-service calls, etc.) cannot accidentally construct
        # an SSRF vector by injecting ``../`` or ``://host`` into the
        # URL. ``quote(safe='')`` escapes everything including ``/`` and
        # ``.``, so the ``field_id`` interpolation is guaranteed to stay
        # within the intended path segment.
        safe_field_id = self._safe_id(field_id)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Parallel fan-out. Each helper wraps its own errors so
            # a single failure doesn't abort the whole gather().
            (
                nutrients,
                pests,
                diseases,
                irrigation,
                weather,
                yield_forecast,
                carbon,
                alerts,
            ) = await asyncio.gather(
                self._call_nutrients(client, headers, safe_field_id),
                self._call_pests(client, headers, safe_field_id),
                self._call_diseases(client, headers, safe_field_id),
                self._call_irrigation(client, headers, safe_field_id),
                self._call_weather(client, headers, safe_field_id),
                self._call_yield(client, headers, safe_field_id),
                self._call_carbon(client, headers, safe_field_id),
                self._call_alerts(client, headers, safe_field_id),
            )

        sections = {
            "nutrients": nutrients.to_dict(),
            "pests": pests.to_dict(),
            "diseases": diseases.to_dict(),
            "irrigation": irrigation.to_dict(),
            "weather": weather.to_dict(),
            "yield": yield_forecast.to_dict(),
            "carbon": carbon.to_dict(),
            "alerts": alerts.to_dict(),
        }

        degraded_count = sum(1 for s in sections.values() if s["degraded"])
        total_latency = sum(s["latency_ms"] for s in sections.values())
        alerts_data = alerts.data if isinstance(alerts.data, list) else []
        alerts_count = len(alerts_data)

        overall_status = self._compute_overall_status(
            degraded_count=degraded_count,
            alerts_count=alerts_count,
            has_critical_alert=any(isinstance(a, dict) and a.get("severity") == "critical" for a in alerts_data),
        )

        from datetime import UTC, datetime

        return {
            "field_id": field_id,
            "tenant_id": tenant_id,
            "generated_at": datetime.now(UTC).isoformat(),
            "overall_status": overall_status,
            "sections": sections,
            "alerts_count": alerts_count,
            "sources_degraded": degraded_count,
            "latency_ms_total": round(total_latency, 1),
        }

    # ------------------------------------------------------------------
    # Downstream callers — all share the same shape
    # ------------------------------------------------------------------

    async def _call_nutrients(self, client: httpx.AsyncClient, headers: dict, field_id: str) -> Section:
        return await self._call(
            client,
            "GET",
            f"{self.urls.soil_analysis}/api/v1/soil/fields/{field_id}/summary",
            headers,
        )

    async def _call_pests(self, client: httpx.AsyncClient, headers: dict, field_id: str) -> Section:
        return await self._call(
            client,
            "GET",
            f"{self.urls.pest_detection}/api/v1/pest/fields/{field_id}/predictions",
            headers,
        )

    async def _call_diseases(self, client: httpx.AsyncClient, headers: dict, field_id: str) -> Section:
        return await self._call(
            client,
            "GET",
            f"{self.urls.crop_intelligence}/api/v1/crop-intelligence/fields/{field_id}/diseases",
            headers,
        )

    async def _call_irrigation(self, client: httpx.AsyncClient, headers: dict, field_id: str) -> Section:
        return await self._call(
            client,
            "GET",
            f"{self.urls.irrigation_smart}/api/v1/irrigation/fields/{field_id}/recommendation",
            headers,
        )

    async def _call_weather(self, client: httpx.AsyncClient, headers: dict, field_id: str) -> Section:
        return await self._call(
            client,
            "GET",
            f"{self.urls.weather}/api/v1/weather/forecast/field/{field_id}",
            headers,
        )

    async def _call_yield(self, client: httpx.AsyncClient, headers: dict, field_id: str) -> Section:
        return await self._call(
            client,
            "GET",
            f"{self.urls.yield_prediction}/api/v1/yield/fields/{field_id}/prediction",
            headers,
        )

    async def _call_carbon(self, client: httpx.AsyncClient, headers: dict, field_id: str) -> Section:
        return await self._call(
            client,
            "GET",
            f"{self.urls.carbon}/api/v1/carbon/fields/{field_id}/summary",
            headers,
        )

    async def _call_alerts(self, client: httpx.AsyncClient, headers: dict, field_id: str) -> Section:
        return await self._call(
            client,
            "GET",
            f"{self.urls.alerts}/api/v1/alerts/fields/{field_id}/active",
            headers,
        )

    # ------------------------------------------------------------------
    # Unified call helper with timeout + error mapping
    # ------------------------------------------------------------------

    def _trusted_base_urls(self) -> tuple[str, ...]:
        """
        Return the tuple of base URLs the orchestrator is allowed to
        call. Every URL passed to ``_call`` must start with one of
        these. Computed once per request — ``self.urls`` is frozen at
        construction time so the tuple is constant.
        """
        return (
            self.urls.soil_analysis.rstrip("/") + "/",
            self.urls.pest_detection.rstrip("/") + "/",
            self.urls.crop_intelligence.rstrip("/") + "/",
            self.urls.irrigation_smart.rstrip("/") + "/",
            self.urls.weather.rstrip("/") + "/",
            self.urls.yield_prediction.rstrip("/") + "/",
            self.urls.carbon.rstrip("/") + "/",
            self.urls.alerts.rstrip("/") + "/",
        )

    async def _call(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        headers: dict,
    ) -> Section:
        import time

        # SECURITY: third line of defence against SSRF. Even though
        # `field_id` was validated at the FastAPI boundary (Layer 1)
        # and re-validated + URL-encoded via ``_safe_id`` (Layer 2),
        # we also gate every outbound HTTP request on an explicit
        # allowlist of trusted base URLs. If a bug in URL construction
        # (wrong base, typo, malicious `urls` override) ever produces a
        # URL that doesn't start with one of the ServiceUrls bases, we
        # fail closed before ``client.request`` is called.
        #
        # CodeQL recognises an explicit `startswith` check against an
        # untainted allowlist as a partial-SSRF sanitizer, so this is
        # the primitive that makes the ``py/partial-ssrf`` query's
        # dataflow terminate cleanly.
        trusted_bases = self._trusted_base_urls()
        if not any(url.startswith(base) for base in trusted_bases):
            logger.error(
                "Refusing to call URL not under trusted base",
                url=url,
            )
            return Section(
                data=None,
                degraded=True,
                latency_ms=0.0,
                error="rejected: url not under trusted base",
            )

        start = time.perf_counter()
        try:
            resp = await client.request(method, url, headers=headers)
            elapsed_ms = (time.perf_counter() - start) * 1000

            if resp.status_code == 200:
                body = resp.json()
                # Many services wrap payloads in {"success": true, "data": ...}
                data = body.get("data") if isinstance(body, dict) else body
                return Section(data=data, degraded=False, latency_ms=elapsed_ms, error=None)
            elif resp.status_code == 404:
                # "No data for this field" is NOT a failure — return
                # degraded=False with data=None so the UI shows "لا
                # توجد بيانات" instead of an error banner.
                return Section(data=None, degraded=False, latency_ms=elapsed_ms, error=None)
            else:
                return Section(
                    data=None,
                    degraded=True,
                    latency_ms=elapsed_ms,
                    error=f"HTTP {resp.status_code}: {resp.text[:200]}",
                )
        except httpx.TimeoutException:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.warning("Timeout calling downstream", url=url, timeout=self.timeout)
            return Section(
                data=None,
                degraded=True,
                latency_ms=elapsed_ms,
                error=f"timeout after {self.timeout}s",
            )
        except httpx.RequestError as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.warning("Network error calling downstream", url=url, error=str(e))
            return Section(
                data=None,
                degraded=True,
                latency_ms=elapsed_ms,
                error=f"network: {type(e).__name__}",
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.error("Unexpected error calling downstream", url=url, error=str(e))
            return Section(
                data=None,
                degraded=True,
                latency_ms=elapsed_ms,
                error=f"unexpected: {type(e).__name__}",
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    # Compiled once — ^[A-Za-z0-9_-]+$ is the same pattern FastAPI
    # enforces at the endpoint boundary (see main.py). Keeping a local
    # copy means the orchestrator stays safe even if it's used outside
    # the FastAPI request lifecycle (tests, internal calls, scripts).
    _ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,100}$")

    @classmethod
    def _safe_id(cls, field_id: str) -> str:
        """
        Validate + URL-encode an identifier before interpolating it
        into a downstream URL. Raises ValueError on obviously bad
        input so the caller fails loudly instead of emitting a
        malformed request. The ``quote(safe='')`` wrapper is
        belt-and-suspenders: even if the pattern changed to allow a
        slash or dot, the URL encoding would still escape it.
        """
        if not isinstance(field_id, str) or not cls._ID_PATTERN.match(field_id):
            raise ValueError(f"Invalid field identifier: {field_id!r}")
        return quote(field_id, safe="")

    @staticmethod
    def _headers(tenant_id: str, auth_header: str | None) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "X-Tenant-Id": tenant_id,
        }
        if auth_header:
            headers["Authorization"] = auth_header
        return headers

    @staticmethod
    def _compute_overall_status(degraded_count: int, alerts_count: int, has_critical_alert: bool) -> str:
        """
        Overall status decision tree:
          critical  — any critical alert OR more than half the sections
                      are degraded
          degraded  — at least one section degraded but no critical
                      alerts
          healthy   — everything is green
        """
        if has_critical_alert or degraded_count >= 4:
            return "critical"
        if degraded_count > 0 or alerts_count > 0:
            return "degraded"
        return "healthy"
