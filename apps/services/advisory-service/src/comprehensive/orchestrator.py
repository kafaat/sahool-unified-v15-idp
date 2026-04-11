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
from urllib.parse import quote, urlparse

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

    def _trusted_hostnames(self) -> frozenset[str]:
        """
        Return the allowlist of hostnames we are permitted to call.
        Derived from ``self.urls`` (frozen at construction time) so
        the set is constant for the life of the orchestrator.

        Using ``urllib.parse.urlparse`` here is deliberate: it's the
        primitive CodeQL's ``py/partial-ssrf`` query recognises as a
        URL parser, and checking ``parsed.hostname`` against an
        untainted allowlist is its canonical sanitizer pattern.
        Replacing the previous ``startswith`` check with this
        parse+check pair was the step that made CodeQL's dataflow
        terminate cleanly on the partial-SSRF finding.
        """
        hosts: set[str] = set()
        for base in (
            self.urls.soil_analysis,
            self.urls.pest_detection,
            self.urls.crop_intelligence,
            self.urls.irrigation_smart,
            self.urls.weather,
            self.urls.yield_prediction,
            self.urls.carbon,
            self.urls.alerts,
        ):
            host = urlparse(base).hostname
            if host:
                hosts.add(host.lower())
        return frozenset(hosts)

    async def _call(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        headers: dict,
    ) -> Section:
        import time

        # SECURITY: four-layer defence against partial SSRF. Each layer
        # is a legitimate runtime check AND a sanitizer pattern CodeQL's
        # ``py/partial-ssrf`` query recognises in its dataflow.
        #
        #   Layer 1 — FastAPI endpoint boundary: ``field_id`` validated
        #             against ^[A-Za-z0-9_-]{1,100}$ via ``Annotated[str,
        #             FastAPIPath(pattern=...)]``. Malicious input is
        #             rejected with 422 before the orchestrator runs.
        #   Layer 2 — ``_safe_id`` re-validates + URL-encodes the
        #             identifier inside the orchestrator, defending
        #             against non-FastAPI callers.
        #   Layer 3 — ``urlparse(url).hostname`` check against the
        #             trusted hostname allowlist (below). Fails closed
        #             if the URL's host is not one of the 8 downstream
        #             services.
        #   Layer 4 — ``re.fullmatch`` against ``_SAFE_URL_PATTERN``,
        #             an untainted class-level constant regex that
        #             accepts only the 8 exact URL shapes we intend
        #             to call. This is the outermost sanitizer; any
        #             URL that reaches ``client.request`` has been
        #             validated character-by-character against a
        #             literal allowlist, so there is no residual
        #             taint for CodeQL to track.
        #
        # ``re.fullmatch`` against a constant pattern is explicitly
        # listed in CodeQL's partial-SSRF sanitizer set, which is why
        # this fourth layer is the one that makes the static
        # analyzer's dataflow terminate cleanly.
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if not host or host not in self._trusted_hostnames():
            logger.error(
                "Refusing to call URL whose host is not in the trusted allowlist",
                url=url,
                host=host,
            )
            return Section(
                data=None,
                degraded=True,
                latency_ms=0.0,
                error="rejected: host not in trusted allowlist",
            )
        if not self._SAFE_URL_PATTERN.fullmatch(url):
            logger.error(
                "Refusing to call URL that does not match the safe allowlist pattern",
                url=url,
            )
            return Section(
                data=None,
                degraded=True,
                latency_ms=0.0,
                error="rejected: url not in safe pattern",
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

    # Compiled once — strict allowlist of the 8 fully-qualified URL
    # shapes this orchestrator is allowed to request. Used as the
    # outermost SSRF sanitizer in ``_call``: if the constructed URL
    # doesn't match this pattern exactly, we fail closed before any
    # outbound HTTP request. Every character class is bounded:
    #
    #   * scheme         — http or https only
    #   * host           — alphanumerics + dots + hyphens (DNS chars)
    #   * port           — optional 1-5 digit port
    #   * path namespace — one of 8 known service roots
    #   * field_id       — [A-Za-z0-9_-]{1,100}, same as _ID_PATTERN
    #
    # CodeQL's ``py/partial-ssrf`` query explicitly recognises
    # ``re.fullmatch`` against a constant pattern as a full sanitizer.
    # This is the primitive that terminates the dataflow cleanly.
    _SAFE_URL_PATTERN = re.compile(
        r"^https?://[A-Za-z0-9.-]+(?::\d{1,5})?/api/v1/"
        r"(?:"
        r"soil/fields/[A-Za-z0-9_-]{1,100}/summary"
        r"|pest/fields/[A-Za-z0-9_-]{1,100}/predictions"
        r"|crop-intelligence/fields/[A-Za-z0-9_-]{1,100}/diseases"
        r"|irrigation/fields/[A-Za-z0-9_-]{1,100}/recommendation"
        r"|weather/forecast/field/[A-Za-z0-9_-]{1,100}"
        r"|yield/fields/[A-Za-z0-9_-]{1,100}/prediction"
        r"|carbon/fields/[A-Za-z0-9_-]{1,100}/summary"
        r"|alerts/fields/[A-Za-z0-9_-]{1,100}/active"
        r")$"
    )

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
