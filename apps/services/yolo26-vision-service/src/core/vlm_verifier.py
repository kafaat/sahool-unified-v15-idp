"""
VLM Secondary Verifier for YOLO26 Vision Service.

Provides secondary verification of YOLO26 detections using multimodal
Vision-Language Models (Qwen-VL or Ollama Vision) to reduce false
positives and improve recognition of novel pest/disease variants.

Architecture (YOLO + VLM Cooperative Inspection):
    YOLO fast detection → crop suspicious region → VLM verification → merged judgment

Verdict thresholds (configurable via Settings):
    - Confirmed  (VLM confidence ≥ confirm_threshold): keep detection
    - Suspicious (suspect_threshold ≤ confidence < confirm_threshold): flag for manual review
    - Dismissed  (confidence < suspect_threshold or has_pest=False): filter out false positive
    - Error      (VLM call failed): keep detection unverified, do not discard

Providers:
    - ``qwen_vl``:  Alibaba Qwen-VL via DashScope API (cloud, best accuracy)
    - ``vllm``:     Platform-internal vLLM server (OpenAI-compat multimodal at
                    ``http://sahool-vllm:8270/v1``). Reuses the existing SAHOOL
                    vLLM service — no external GPU or cloud cost required.
    - ``ollama``:   Local Ollama Vision model (llava/bakllava, offline-first)
    - ``disabled``: VLM verification disabled (YOLO-only mode, default)
"""

from __future__ import annotations

import base64
import io
import json
import re
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

import httpx
import structlog
from PIL import Image

logger = structlog.get_logger(__name__)

# Minimum crop dimension (pixels). Regions smaller than this use the full image.
_MIN_CROP_PX = 10


# =============================================================================
# Enums
# =============================================================================


class VLMProvider(StrEnum):
    """Supported VLM providers for secondary verification.

    - ``qwen_vl``:  Alibaba Qwen-VL via DashScope REST API (cloud, highest accuracy).
    - ``vllm``:     Platform-internal vLLM server (OpenAI-compat multimodal at
                    ``http://sahool-vllm:8270/v1``).  Reuses the existing SAHOOL
                    vLLM service — no external GPU or cloud cost required.
    - ``ollama``:   Local Ollama Vision model (llava/bakllava, offline-first edge).
    - ``disabled``: VLM verification disabled (YOLO-only mode, default).
    """

    QWEN_VL = "qwen_vl"
    VLLM = "vllm"
    OLLAMA = "ollama"
    DISABLED = "disabled"


class VLMVerificationStatus(StrEnum):
    """VLM secondary verification verdict.

    - CONFIRMED:  VLM agrees with YOLO — high-confidence pest/disease present.
    - SUSPICIOUS: VLM is uncertain — flag for manual agronomist review.
    - DISMISSED:  VLM disagrees — likely YOLO false positive, filter out.
    - ERROR:      VLM call failed — keep YOLO detection unverified.
    """

    CONFIRMED = "confirmed"
    SUSPICIOUS = "suspicious"
    DISMISSED = "dismissed"
    ERROR = "error"


# =============================================================================
# Result dataclass
# =============================================================================


@dataclass
class VLMVerificationResult:
    """Result from VLM secondary verification of a single detection."""

    status: VLMVerificationStatus
    has_pest: bool
    confidence: float  # 0.0 – 1.0 (normalised from VLM 0-100 output)

    # Optional diagnosis detail
    pest_type: str | None = None
    pest_type_ar: str | None = None  # Arabic name when available
    severity: str | None = None  # "mild" / "moderate" / "severe"
    diagnosis_en: str | None = None

    provider: str = VLMProvider.DISABLED
    latency_ms: float = 0.0
    error: str | None = None  # Non-None when status == ERROR


# =============================================================================
# VLMVerifier
# =============================================================================


class VLMVerifier:
    """
    VLM secondary verifier for YOLO26 agricultural detections.

    Calls Qwen-VL (DashScope), the platform's internal vLLM server, or Ollama
    Vision to validate each YOLO detection region and return a structured verdict.

    Provider selection (Pain Points addressed):
        - ``vllm``    → uses ``sahool-vllm:8270`` already on the platform.
                        No external API key, no cloud cost. (Pain Point 2 ✓)
        - ``qwen_vl`` → DashScope cloud, best multimodal accuracy. (Pain Point 3 ✓)
        - ``ollama``  → local Jetson/edge box via llava. (Pain Point 1 + 2 ✓)

    Usage::

        verifier = VLMVerifier(provider="vllm")
        result = await verifier.verify(image_bytes, [x1, y1, x2, y2], "Red Palm Weevil")
    """

    # Qwen-VL DashScope endpoint
    _QWEN_VL_DEFAULT_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

    # Structured verification prompt — requests bilingual JSON output
    _PROMPT = (
        "You are an expert agricultural inspector. "
        "Examine the crop image carefully for pest infestation or plant disease symptoms.\n\n"
        "Respond ONLY with a valid JSON object — no markdown, no extra text:\n"
        '{"has_pest": true_or_false, '
        '"pest_type": "disease or pest name in English, or null", '
        '"pest_type_ar": "disease or pest name in Arabic, or null", '
        '"confidence": <integer 0-100>, '
        '"severity": "mild or moderate or severe, or null", '
        '"diagnosis": "one-sentence diagnosis in English, or null"}'
    )

    def __init__(
        self,
        provider: str = VLMProvider.DISABLED,
        # Qwen-VL (DashScope)
        qwen_api_key: str = "",
        qwen_model: str = "qwen-vl-plus",
        qwen_api_url: str = "",
        # vLLM (platform-internal OpenAI-compat)
        vllm_url: str = "http://sahool-vllm:8270/v1",
        vllm_model: str = "deepseek-ai/deepseek-vl2",
        # Ollama Vision (local edge)
        ollama_url: str = "http://localhost:11434",
        ollama_model: str = "llava:7b",
        # Thresholds
        confirm_threshold: float = 0.8,
        suspect_threshold: float = 0.5,
        timeout: float = 30.0,
    ) -> None:
        try:
            self.provider = VLMProvider(provider)
        except ValueError:
            logger.warning("vlm_unknown_provider", provider=provider, fallback="disabled")
            self.provider = VLMProvider.DISABLED

        self.qwen_api_key = qwen_api_key
        self.qwen_model = qwen_model
        self.qwen_api_url = qwen_api_url or self._QWEN_VL_DEFAULT_URL
        self.vllm_url = vllm_url.rstrip("/")
        self.vllm_model = vllm_model
        self.ollama_url = ollama_url.rstrip("/")
        self.ollama_model = ollama_model

        if suspect_threshold > confirm_threshold:
            logger.warning(
                "vlm_threshold_order_warning",
                suspect_threshold=suspect_threshold,
                confirm_threshold=confirm_threshold,
                message="suspect_threshold must be <= confirm_threshold; swapping",
            )
            suspect_threshold, confirm_threshold = confirm_threshold, suspect_threshold

        self.confirm_threshold = confirm_threshold
        self.suspect_threshold = suspect_threshold
        self.timeout = timeout

        # Reusable HTTP client — shared across all provider calls on this instance.
        # Avoids per-call TCP handshake overhead (especially important in verify_batch).
        # Callers should invoke ``await verifier.aclose()`` when done with the verifier.
        self._http_client: httpx.AsyncClient | None = None

        logger.info(
            "vlm_verifier_initialized",
            provider=self.provider,
            confirm_threshold=confirm_threshold,
            suspect_threshold=suspect_threshold,
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def is_enabled(self) -> bool:
        """Return True when VLM verification is active (provider ≠ disabled)."""
        return self.provider != VLMProvider.DISABLED

    def _get_http_client(self) -> httpx.AsyncClient:
        """Return the shared :class:`httpx.AsyncClient`, creating it on first call."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=self.timeout)
        return self._http_client

    async def aclose(self) -> None:
        """Close the shared HTTP client.  Call this when the verifier is no longer needed."""
        if self._http_client is not None and not self._http_client.is_closed:
            await self._http_client.aclose()
        self._http_client = None

    async def verify(
        self,
        image: bytes | Image.Image,
        bbox: list[float],
        pest_type_hint: str | None = None,
    ) -> VLMVerificationResult:
        """
        Secondary-verify a single YOLO detection via VLM.

        Args:
            image: Full-image JPEG/PNG bytes, or a pre-decoded
                :class:`PIL.Image.Image` (pass the latter when verifying
                multiple detections from the same image to avoid repeated
                decode overhead).
            bbox: Detection bounding box ``[x1, y1, x2, y2]`` in pixel coordinates.
            pest_type_hint: YOLO predicted class name (used for logging only).

        Returns:
            :class:`VLMVerificationResult` with verdict and diagnosis.
        """
        if not self.is_enabled:
            return VLMVerificationResult(
                status=VLMVerificationStatus.ERROR,
                has_pest=False,
                confidence=0.0,
                provider=VLMProvider.DISABLED,
                error="VLM verification is disabled",
            )

        t0 = time.perf_counter()
        try:
            crop_bytes = self._crop_region(image, bbox)

            if self.provider == VLMProvider.QWEN_VL:
                raw = await self._call_qwen_vl(crop_bytes)
            elif self.provider == VLMProvider.VLLM:
                raw = await self._call_vllm_vision(crop_bytes)
            else:  # OLLAMA
                raw = await self._call_ollama_vision(crop_bytes)

            return self._build_result(raw, t0)

        except httpx.TimeoutException:
            latency_ms = (time.perf_counter() - t0) * 1000
            logger.warning(
                "vlm_timeout",
                provider=self.provider,
                pest_type_hint=pest_type_hint,
                latency_ms=round(latency_ms, 2),
            )
            return VLMVerificationResult(
                status=VLMVerificationStatus.ERROR,
                has_pest=False,
                confidence=0.0,
                provider=self.provider,
                latency_ms=round(latency_ms, 2),
                error="VLM request timed out",
            )
        except Exception as exc:
            latency_ms = (time.perf_counter() - t0) * 1000
            logger.error(
                "vlm_call_failed",
                provider=self.provider,
                pest_type_hint=pest_type_hint,
                error=str(exc),
                latency_ms=round(latency_ms, 2),
            )
            return VLMVerificationResult(
                status=VLMVerificationStatus.ERROR,
                has_pest=False,
                confidence=0.0,
                provider=self.provider,
                latency_ms=round(latency_ms, 2),
                error=str(exc),
            )

    async def verify_batch(
        self,
        image: bytes | Image.Image,
        detections: list[dict[str, Any]],
    ) -> list[VLMVerificationResult]:
        """
        Sequentially verify multiple detections from one image.

        Sequential (not concurrent) to avoid saturating VLM rate limits.

        Args:
            image: Full-image bytes, or a pre-decoded :class:`PIL.Image.Image`.
                Pass a pre-decoded image to avoid redundant decode on each call.
            detections: List of detection dicts each containing ``"bbox"``
                (pixel coords list) and optionally ``"class_name_en"``.

        Returns:
            One :class:`VLMVerificationResult` per input detection, same order.
        """
        results: list[VLMVerificationResult] = []
        for det in detections:
            bbox: list[float] = det.get("bbox", [0.0, 0.0, 0.0, 0.0])
            hint: str | None = det.get("class_name_en")
            results.append(await self.verify(image, bbox, hint))
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _crop_region(self, image: bytes | Image.Image, bbox: list[float]) -> bytes:
        """
        Crop the detection region from the full image.

        Accepts either raw image bytes or a pre-decoded :class:`PIL.Image.Image`
        so that callers processing multiple detections can decode the image once
        and pass the same object for every crop.

        Clamps coordinates to image bounds. Falls back to the full image
        when the region is smaller than ``_MIN_CROP_PX`` in either dimension.

        Returns:
            JPEG-encoded bytes of the cropped region.
        """
        if isinstance(image, bytes):
            img = Image.open(io.BytesIO(image)).convert("RGB")
        else:
            img = image
        x1, y1, x2, y2 = (int(v) for v in bbox)

        # Clamp to image bounds
        x1 = max(0, min(x1, img.width))
        y1 = max(0, min(y1, img.height))
        x2 = max(0, min(x2, img.width))
        y2 = max(0, min(y2, img.height))

        if x2 - x1 < _MIN_CROP_PX or y2 - y1 < _MIN_CROP_PX:
            crop = img  # Use full image for tiny regions
        else:
            crop = img.crop((x1, y1, x2, y2))

        buf = io.BytesIO()
        crop.save(buf, format="JPEG", quality=85)
        return buf.getvalue()

    @staticmethod
    def _encode_image(image_bytes: bytes) -> str:
        """Return base64-encoded image string."""
        return base64.b64encode(image_bytes).decode("utf-8")

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        """
        Extract the first JSON object from a VLM text response.

        Handles responses wrapped in markdown code fences or with
        surrounding prose.
        """
        text = text.strip()

        # 1. Try first curly-brace JSON block (handles nested objects too)
        depth = 0
        start = -1
        for i, ch in enumerate(text):
            if ch == "{":
                if depth == 0:
                    start = i
                depth += 1
            elif ch == "}":
                if depth > 0:
                    depth -= 1
                    if depth == 0 and start != -1:
                        candidate = text[start : i + 1]
                        try:
                            return json.loads(candidate)
                        except (json.JSONDecodeError, ValueError):
                            # Try next occurrence
                            start = -1
                            depth = 0

        # 2. Fallback: regex for simple (non-nested) JSON object
        match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except (json.JSONDecodeError, ValueError):
                pass

        # 3. Last resort: try whole string
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return {}

    @staticmethod
    def _parse_has_pest(value: Any) -> bool:
        """Robustly parse the ``has_pest`` field from VLM output.

        Handles booleans, integers/floats, and string representations
        so that a provider returning ``"false"`` (a truthy string) is
        not incorrectly treated as ``True``.
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            v = value.strip().lower()
            if v in {"true", "1", "yes", "y"}:
                return True
            if v in {"false", "0", "no", "n", ""}:
                return False
        return False

    def _score_to_status(self, raw_confidence: float, has_pest: bool) -> VLMVerificationStatus:
        """
        Map raw VLM confidence (0-100 scale) and has_pest flag to a verdict.

        Args:
            raw_confidence: VLM confidence in the 0-100 range.
            has_pest: Whether the VLM believes a pest/disease is present.

        Returns:
            :class:`VLMVerificationStatus` verdict.
        """
        if not has_pest:
            return VLMVerificationStatus.DISMISSED

        normalised = raw_confidence / 100.0
        if normalised >= self.confirm_threshold:
            return VLMVerificationStatus.CONFIRMED
        if normalised >= self.suspect_threshold:
            return VLMVerificationStatus.SUSPICIOUS
        return VLMVerificationStatus.DISMISSED

    def _build_result(self, raw: dict[str, Any], t0: float) -> VLMVerificationResult:
        """Build a :class:`VLMVerificationResult` from parsed VLM JSON output."""
        has_pest: bool = self._parse_has_pest(raw.get("has_pest", False))
        raw_conf: float = max(0.0, min(100.0, float(raw.get("confidence", 0.0))))
        pest_type: str | None = raw.get("pest_type") or None
        pest_type_ar: str | None = raw.get("pest_type_ar") or None
        severity: str | None = raw.get("severity") or None
        diagnosis: str | None = raw.get("diagnosis") or None

        status = self._score_to_status(raw_conf, has_pest)
        normalised_conf = raw_conf / 100.0 if has_pest else 0.0
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        logger.debug(
            "vlm_result",
            provider=self.provider,
            status=status,
            has_pest=has_pest,
            confidence=normalised_conf,
            latency_ms=latency_ms,
        )

        return VLMVerificationResult(
            status=status,
            has_pest=has_pest,
            confidence=normalised_conf,
            pest_type=pest_type,
            pest_type_ar=pest_type_ar,
            severity=severity,
            diagnosis_en=diagnosis,
            provider=self.provider,
            latency_ms=latency_ms,
        )

    # ------------------------------------------------------------------
    # Provider-specific callers
    # ------------------------------------------------------------------

    async def _call_qwen_vl(self, crop_bytes: bytes) -> dict[str, Any]:
        """
        Call Alibaba Qwen-VL via DashScope REST API.

        Endpoint: POST https://dashscope.aliyuncs.com/api/v1/services/aigc/
                         multimodal-generation/generation
        """
        img_b64 = self._encode_image(crop_bytes)
        headers = {
            "Authorization": f"Bearer {self.qwen_api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.qwen_model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"image": f"data:image/jpeg;base64,{img_b64}"},
                            {"text": self._PROMPT},
                        ],
                    }
                ]
            },
            "parameters": {"result_format": "message"},
        }

        client = self._get_http_client()
        response = await client.post(self.qwen_api_url, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        content = result.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", "")

        # Qwen-VL may return content as a list of {"text": "..."} dicts
        if isinstance(content, list):
            content = " ".join(part.get("text", "") for part in content if isinstance(part, dict))

        return self._extract_json(str(content))

    async def _call_vllm_vision(self, crop_bytes: bytes) -> dict[str, Any]:
        """
        Call the platform's internal vLLM server using the OpenAI-compatible
        multimodal chat/completions endpoint.

        The SAHOOL vLLM service runs at ``http://sahool-vllm:8270/v1`` and
        serves any model loaded via the ``VLLM_MODEL`` environment variable.
        When a vision-capable model is loaded (e.g. ``deepseek-ai/deepseek-vl2``,
        ``llava-hf/llava-1.5-7b-hf``), images can be sent as OpenAI-format
        ``image_url`` content blocks.

        No external API key needed — reuses the existing internal service.
        """
        img_b64 = self._encode_image(crop_bytes)
        payload: dict[str, Any] = {
            "model": self.vllm_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"},
                        },
                        {"type": "text", "text": self._PROMPT},
                    ],
                }
            ],
            "temperature": 0.1,
            "max_tokens": 256,
        }

        client = self._get_http_client()
        response = await client.post(
            f"{self.vllm_url}/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()

        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        return self._extract_json(str(content))

    async def _call_ollama_vision(self, crop_bytes: bytes) -> dict[str, Any]:
        """
        Call Ollama Vision model (llava, bakllava) via local Ollama API.

        Endpoint: POST http://localhost:11434/api/generate
        """
        img_b64 = self._encode_image(crop_bytes)
        payload: dict[str, Any] = {
            "model": self.ollama_model,
            "prompt": self._PROMPT,
            "images": [img_b64],
            "stream": False,
            "format": "json",
        }

        client = self._get_http_client()
        response = await client.post(
            f"{self.ollama_url}/api/generate",
            json=payload,
        )
        response.raise_for_status()

        result = response.json()
        content = result.get("response", "")
        return self._extract_json(str(content))


# =============================================================================
# Factory
# =============================================================================


def build_vlm_verifier_from_settings(settings: Any) -> VLMVerifier:
    """
    Instantiate a :class:`VLMVerifier` from the service :class:`Settings`.

    All VLM settings are optional and default to safe values (disabled).
    Set ``VLM_PROVIDER=vllm`` to use the platform's existing internal vLLM
    service at ``http://sahool-vllm:8270/v1`` without any external API key.
    """
    return VLMVerifier(
        provider=getattr(settings, "vlm_provider", VLMProvider.DISABLED),
        # Qwen-VL
        qwen_api_key=getattr(settings, "qwen_vl_api_key", ""),
        qwen_model=getattr(settings, "qwen_vl_model", "qwen-vl-plus"),
        qwen_api_url=getattr(settings, "qwen_vl_api_url", ""),
        # vLLM (internal platform service)
        vllm_url=getattr(settings, "vllm_vlm_url", "http://sahool-vllm:8270/v1"),
        vllm_model=getattr(settings, "vllm_vlm_model", "deepseek-ai/deepseek-vl2"),
        # Ollama
        ollama_url=getattr(settings, "ollama_vlm_url", "http://localhost:11434"),
        ollama_model=getattr(settings, "ollama_vlm_model", "llava:7b"),
        # Thresholds
        confirm_threshold=getattr(settings, "vlm_confirm_threshold", 0.8),
        suspect_threshold=getattr(settings, "vlm_suspect_threshold", 0.5),
        timeout=getattr(settings, "vlm_timeout_seconds", 30.0),
    )
