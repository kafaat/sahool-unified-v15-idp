"""
CDSE (Copernicus Data Space Ecosystem) client
عميل نظام بيانات كوبرنيكوس الفضائي

Handles:
- OAuth2 client credentials token management
- STAC catalog search for Sentinel-2 L2A scenes
- Scene download via Sentinel Hub Process API
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any

import os

import httpx
import structlog

logger = structlog.get_logger(__name__)

# CDSE endpoints — configurable via env vars
_SH_BASE_URL = os.getenv("SH_BASE_URL", "https://sh.dataspace.copernicus.eu")
_TOKEN_URL = os.getenv(
    "SH_TOKEN_URL",
    "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
)
_STAC_SEARCH_URL = f"{_SH_BASE_URL}/api/v1/catalog/1.0.0/search"
_PROCESS_API_URL = f"{_SH_BASE_URL}/api/v1/process"

# Evalscript: return B02, B03, B04, B08 as float32 + SCL for cloud masking
_EVALSCRIPT = """
//VERSION=3
function setup() {
  return {
    input: [{ bands: ["B02", "B03", "B04", "B08", "SCL"] }],
    output: { bands: 5, sampleType: "FLOAT32" }
  };
}
function evaluatePixel(s) {
  return [s.B02, s.B03, s.B04, s.B08, s.SCL];
}
"""


@dataclass
class _TokenCache:
    access_token: str = ""
    expires_at: float = 0.0  # epoch seconds


class CdseClient:
    """
    Async CDSE client: OAuth2 token + STAC catalog + Process API.
    Respects Retry-After headers; uses tenacity-style backoff internally.
    """

    def __init__(self, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._token = _TokenCache()
        self._lock = asyncio.Lock()
        self._http: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------ #
    # Lifecycle                                                            #
    # ------------------------------------------------------------------ #

    async def init(self) -> None:
        """Create the shared HTTP client. Call once at startup."""
        self._http = httpx.AsyncClient(timeout=60.0)

    async def close(self) -> None:
        if self._http:
            await self._http.aclose()
            self._http = None

    # ------------------------------------------------------------------ #
    # Token management                                                     #
    # ------------------------------------------------------------------ #

    async def get_token(self) -> str:
        """Return a valid Bearer token, refreshing if needed."""
        async with self._lock:
            if time.time() < self._token.expires_at - 30:
                return self._token.access_token
            await self._refresh_token()
            return self._token.access_token

    async def _refresh_token(self) -> None:
        assert self._http, "Call init() first"
        data = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        for attempt in range(3):
            try:
                resp = await self._http.post(_TOKEN_URL, data=data)
                if resp.status_code == 429:
                    wait = float(resp.headers.get("Retry-After", 5))
                    logger.warning("cdse_token_rate_limited", wait_s=wait)
                    await asyncio.sleep(wait)
                    continue
                resp.raise_for_status()
                payload = resp.json()
                self._token.access_token = payload["access_token"]
                # Use expires_in with a 30-second safety margin
                expires_in = int(payload.get("expires_in", 600))
                self._token.expires_at = time.time() + expires_in
                logger.info("cdse_token_refreshed", expires_in=expires_in)
                return
            except httpx.HTTPError as exc:
                logger.error("cdse_token_error", attempt=attempt, error=str(exc))
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError("Failed to obtain CDSE token after 3 attempts")

    # ------------------------------------------------------------------ #
    # STAC catalog search                                                  #
    # ------------------------------------------------------------------ #

    async def search_scenes(
        self,
        bbox: list[float],
        date_from: date,
        date_to: date,
        cloud_max: float = 100.0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Search Sentinel-2 L2A scenes via CDSE STAC catalog.

        Returns list of STAC feature dicts, each containing:
        - id, geometry, bbox
        - properties.datetime (acquisition timestamp)
        - properties.eo:cloud_cover
        """
        assert self._http, "Call init() first"
        token = await self.get_token()

        dt_from = date_from.strftime("%Y-%m-%dT00:00:00Z")
        dt_to = date_to.strftime("%Y-%m-%dT23:59:59Z")

        body: dict[str, Any] = {
            "bbox": bbox,
            "datetime": f"{dt_from}/{dt_to}",
            "collections": ["sentinel-2-l2a"],
            "limit": limit,
            "filter": {
                "op": "lte",
                "args": [{"property": "eo:cloud_cover"}, cloud_max],
            },
            "filter-lang": "cql2-json",
        }

        features: list[dict] = []
        next_token: str | None = None

        while True:
            if next_token:
                body["token"] = next_token

            for attempt in range(3):
                try:
                    resp = await self._http.post(
                        _STAC_SEARCH_URL,
                        json=body,
                        headers={"Authorization": f"Bearer {token}"},
                    )
                    if resp.status_code == 429:
                        wait = float(resp.headers.get("Retry-After", 5))
                        logger.warning("cdse_search_rate_limited", wait_s=wait)
                        await asyncio.sleep(wait)
                        token = await self.get_token()  # may have expired
                        continue
                    resp.raise_for_status()
                    break
                except httpx.HTTPError as exc:
                    if attempt == 2:
                        logger.error("cdse_search_failed", error=str(exc), bbox=bbox)
                        return features
                    await asyncio.sleep(2 ** attempt)

            data = resp.json()
            features.extend(data.get("features", []))

            # Pagination
            links = data.get("links", [])
            next_link = next((lk for lk in links if lk.get("rel") == "next"), None)
            if next_link:
                next_token = next_link.get("token") or next_link.get("href", "").split("token=")[-1] or None
            else:
                break

            if not next_token:
                break

        logger.info(
            "cdse_search_complete",
            bbox=bbox,
            date_from=str(date_from),
            date_to=str(date_to),
            scenes_found=len(features),
        )
        return features

    # ------------------------------------------------------------------ #
    # Process API — download band data for a field bbox                   #
    # ------------------------------------------------------------------ #

    async def download_bands(
        self,
        bbox: list[float],
        acquisition_date: date,
        width: int = 256,
        height: int = 256,
    ) -> bytes | None:
        """
        Download B02/B03/B04/B08/SCL for bbox on acquisition_date via
        Sentinel Hub Process API.  Returns raw TIFF bytes or None on failure.

        The caller (IndexProcessor) converts bytes → numpy array.
        """
        assert self._http, "Call init() first"
        token = await self.get_token()

        dt_str = acquisition_date.strftime("%Y-%m-%d")

        request_body = {
            "input": {
                "bounds": {
                    "bbox": bbox,
                    "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"},
                },
                "data": [
                    {
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": f"{dt_str}T00:00:00Z",
                                "to": f"{dt_str}T23:59:59Z",
                            },
                            "maxCloudCoverage": 100,
                        },
                    }
                ],
            },
            "output": {
                "width": width,
                "height": height,
                "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}],
            },
            "evalscript": _EVALSCRIPT,
        }

        for attempt in range(3):
            try:
                resp = await self._http.post(
                    _PROCESS_API_URL,
                    json=request_body,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=120.0,
                )
                if resp.status_code == 429:
                    wait = float(resp.headers.get("Retry-After", 10))
                    logger.warning("cdse_process_rate_limited", wait_s=wait)
                    await asyncio.sleep(wait)
                    token = await self.get_token()
                    continue
                if resp.status_code == 204:
                    # No data available for this date/bbox
                    logger.info("cdse_no_data", date=dt_str, bbox=bbox)
                    return None
                resp.raise_for_status()
                return resp.content
            except httpx.HTTPError as exc:
                if attempt == 2:
                    logger.error(
                        "cdse_download_failed",
                        date=dt_str,
                        bbox=bbox,
                        error=str(exc),
                    )
                    return None
                await asyncio.sleep(2 ** attempt)

        return None

    # ------------------------------------------------------------------ #
    # Helper: extract acquisition date from a STAC feature                #
    # ------------------------------------------------------------------ #

    @staticmethod
    def scene_date(feature: dict[str, Any]) -> date | None:
        """Parse the acquisition date from a STAC feature."""
        dt_str = feature.get("properties", {}).get("datetime")
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).date()
        except ValueError:
            return None

    @staticmethod
    def scene_cloud_cover(feature: dict[str, Any]) -> float:
        return float(feature.get("properties", {}).get("eo:cloud_cover", 0.0))
