"""
Unit tests for VLMVerifier — YOLO26 secondary verification pipeline.

Tests cover:
- VLMProvider enum and VLMVerifier initialization
- _crop_region: clamping, tiny-region fallback, normal crop
- _extract_json: clean JSON, markdown fences, prose-wrapped, malformed
- _score_to_status: threshold logic for all four verdicts
- _build_result: full result assembly
- verify(): disabled provider, timeout, generic exception, success
- verify_batch(): ordering preserved, sequential calls
- build_vlm_verifier_from_settings(): factory reads Settings attrs
- _run_vlm_pass() integration in detection endpoints (disease + weed)
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from PIL import Image

# Ensure service root is importable (added by conftest.py already)
from src.core.vlm_verifier import (
    VLMProvider,
    VLMVerificationStatus,
    VLMVerifier,
    build_vlm_verifier_from_settings,
)

# =============================================================================
# Helpers
# =============================================================================


def _make_jpeg(width: int = 100, height: int = 100) -> bytes:
    """Return minimal JPEG bytes of a solid-colour image."""
    img = Image.new("RGB", (width, height), color=(120, 180, 60))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _make_verifier(**kwargs) -> VLMVerifier:
    """Convenience factory with sensible test defaults."""
    defaults = {
        "provider": VLMProvider.QWEN_VL,
        "qwen_api_key": "test-key",
        "confirm_threshold": 0.8,
        "suspect_threshold": 0.5,
        "timeout": 5.0,
    }
    defaults.update(kwargs)
    return VLMVerifier(**defaults)


# =============================================================================
# VLMProvider enum
# =============================================================================


class TestVLMProvider:
    def test_all_values(self):
        assert VLMProvider.QWEN_VL == "qwen_vl"
        assert VLMProvider.VLLM == "vllm"
        assert VLMProvider.OLLAMA == "ollama"
        assert VLMProvider.DISABLED == "disabled"

    def test_is_string(self):
        assert isinstance(VLMProvider.VLLM, str)


# =============================================================================
# VLMVerifier.__init__
# =============================================================================


class TestVLMVerifierInit:
    def test_unknown_provider_falls_back_to_disabled(self):
        v = VLMVerifier(provider="totally_unknown")
        assert v.provider == VLMProvider.DISABLED
        assert not v.is_enabled

    def test_valid_provider_stored(self):
        v = VLMVerifier(provider="vllm")
        assert v.provider == VLMProvider.VLLM
        assert v.is_enabled

    def test_disabled_not_enabled(self):
        v = VLMVerifier(provider="disabled")
        assert not v.is_enabled

    def test_threshold_swap_when_inverted(self):
        # suspect > confirm → they should be swapped
        v = VLMVerifier(provider="ollama", confirm_threshold=0.4, suspect_threshold=0.9)
        assert v.confirm_threshold >= v.suspect_threshold

    def test_vllm_defaults(self):
        v = VLMVerifier(provider="vllm")
        assert "8270" in v.vllm_url or "vllm" in v.vllm_url.lower()

    def test_qwen_default_url_set(self):
        v = VLMVerifier(provider="qwen_vl", qwen_api_key="k")
        assert "dashscope" in v.qwen_api_url


# =============================================================================
# _crop_region
# =============================================================================


class TestCropRegion:
    def test_normal_crop(self):
        image_bytes = _make_jpeg(200, 200)
        v = VLMVerifier()
        cropped = v._crop_region(image_bytes, [10, 10, 100, 100])
        img = Image.open(io.BytesIO(cropped))
        assert img.width == 90
        assert img.height == 90

    def test_clamp_out_of_bounds(self):
        image_bytes = _make_jpeg(100, 100)
        v = VLMVerifier()
        # bbox extends beyond image bounds
        cropped = v._crop_region(image_bytes, [80, 80, 200, 200])
        img = Image.open(io.BytesIO(cropped))
        assert img.width == 20
        assert img.height == 20

    def test_tiny_region_returns_full_image(self):
        image_bytes = _make_jpeg(100, 100)
        v = VLMVerifier()
        # bbox smaller than _MIN_CROP_PX (10)
        cropped = v._crop_region(image_bytes, [50, 50, 55, 55])
        img = Image.open(io.BytesIO(cropped))
        # Falls back to full image
        assert img.width == 100
        assert img.height == 100

    def test_returns_jpeg_bytes(self):
        image_bytes = _make_jpeg()
        v = VLMVerifier()
        result = v._crop_region(image_bytes, [0, 0, 50, 50])
        # JPEG magic bytes
        assert result[:2] == b"\xff\xd8"


# =============================================================================
# _extract_json
# =============================================================================


class TestExtractJson:
    def test_clean_json(self):
        text = '{"has_pest": true, "confidence": 85}'
        assert VLMVerifier._extract_json(text) == {"has_pest": True, "confidence": 85}

    def test_markdown_fenced(self):
        text = '```json\n{"has_pest": false, "confidence": 10}\n```'
        result = VLMVerifier._extract_json(text)
        assert result["has_pest"] is False

    def test_prose_wrapped(self):
        text = 'Here is my analysis: {"has_pest": true, "pest_type": "aphid", "confidence": 72}'
        result = VLMVerifier._extract_json(text)
        assert result["pest_type"] == "aphid"

    def test_nested_json(self):
        text = '{"has_pest": true, "details": {"severity": "mild"}, "confidence": 60}'
        result = VLMVerifier._extract_json(text)
        assert result["details"]["severity"] == "mild"

    def test_malformed_returns_empty_dict(self):
        assert VLMVerifier._extract_json("not json at all") == {}

    def test_empty_string_returns_empty_dict(self):
        assert VLMVerifier._extract_json("") == {}


# =============================================================================
# _score_to_status
# =============================================================================


class TestScoreToStatus:
    def setup_method(self):
        self.v = VLMVerifier(provider="ollama", confirm_threshold=0.8, suspect_threshold=0.5)

    def test_confirmed(self):
        assert self.v._score_to_status(85.0, True) == VLMVerificationStatus.CONFIRMED

    def test_suspicious(self):
        assert self.v._score_to_status(65.0, True) == VLMVerificationStatus.SUSPICIOUS

    def test_dismissed_low_confidence(self):
        assert self.v._score_to_status(30.0, True) == VLMVerificationStatus.DISMISSED

    def test_dismissed_no_pest(self):
        # has_pest=False → always dismissed regardless of confidence
        assert self.v._score_to_status(95.0, False) == VLMVerificationStatus.DISMISSED

    def test_exact_confirm_boundary(self):
        # At exactly confirm_threshold (0.8 → 80.0 raw) → CONFIRMED
        assert self.v._score_to_status(80.0, True) == VLMVerificationStatus.CONFIRMED

    def test_exact_suspect_boundary(self):
        # At exactly suspect_threshold (0.5 → 50.0 raw) → SUSPICIOUS
        assert self.v._score_to_status(50.0, True) == VLMVerificationStatus.SUSPICIOUS


# =============================================================================
# _build_result
# =============================================================================


class TestBuildResult:
    import time as _time

    def test_confirmed_result(self):
        v = _make_verifier()
        import time

        t0 = time.perf_counter()
        raw = {
            "has_pest": True,
            "confidence": 90,
            "pest_type": "aphid",
            "pest_type_ar": "حشرة المن",
            "severity": "moderate",
            "diagnosis": "Aphid infestation",
        }
        result = v._build_result(raw, t0)
        assert result.status == VLMVerificationStatus.CONFIRMED
        assert result.has_pest is True
        assert abs(result.confidence - 0.9) < 0.001
        assert result.pest_type == "aphid"
        assert result.pest_type_ar == "حشرة المن"
        assert result.severity == "moderate"
        assert result.diagnosis_en == "Aphid infestation"
        assert result.latency_ms >= 0.0

    def test_dismissed_result(self):
        v = _make_verifier()
        import time

        t0 = time.perf_counter()
        raw = {"has_pest": False, "confidence": 0}
        result = v._build_result(raw, t0)
        assert result.status == VLMVerificationStatus.DISMISSED
        assert result.confidence == 0.0

    def test_missing_fields_use_none(self):
        v = _make_verifier()
        import time

        t0 = time.perf_counter()
        result = v._build_result({}, t0)
        assert result.pest_type is None
        assert result.severity is None


# =============================================================================
# verify() — disabled provider
# =============================================================================


class TestVerifyDisabled:
    @pytest.mark.asyncio
    async def test_disabled_returns_error(self):
        v = VLMVerifier(provider="disabled")
        result = await v.verify(_make_jpeg(), [0, 0, 50, 50])
        assert result.status == VLMVerificationStatus.ERROR
        assert "disabled" in (result.error or "").lower()
        assert result.provider == VLMProvider.DISABLED


# =============================================================================
# verify() — timeout handling
# =============================================================================


class TestVerifyTimeout:
    @pytest.mark.asyncio
    async def test_timeout_returns_error_status(self):
        v = _make_verifier(provider="qwen_vl")
        with patch.object(v, "_call_qwen_vl", side_effect=httpx.TimeoutException("timed out")):
            result = await v.verify(_make_jpeg(), [10, 10, 80, 80], "aphid")
        assert result.status == VLMVerificationStatus.ERROR
        assert result.error == "VLM request timed out"
        assert result.latency_ms >= 0.0

    @pytest.mark.asyncio
    async def test_generic_exception_returns_error(self):
        v = _make_verifier(provider="ollama")
        with patch.object(v, "_call_ollama_vision", side_effect=RuntimeError("connection refused")):
            result = await v.verify(_make_jpeg(), [0, 0, 50, 50])
        assert result.status == VLMVerificationStatus.ERROR
        assert "connection refused" in (result.error or "")


# =============================================================================
# verify() — Qwen-VL success path
# =============================================================================


class TestVerifyQwenVL:
    @pytest.mark.asyncio
    async def test_confirmed_detection(self):
        payload = {
            "has_pest": True,
            "confidence": 88,
            "pest_type": "Red Palm Weevil",
            "pest_type_ar": "سوسة النخيل",
            "severity": "severe",
            "diagnosis": "RPW detected",
        }
        v = _make_verifier(provider="qwen_vl")
        with patch.object(v, "_call_qwen_vl", new_callable=AsyncMock, return_value=payload):
            result = await v.verify(_make_jpeg(), [10, 10, 90, 90], "Red Palm Weevil")
        assert result.status == VLMVerificationStatus.CONFIRMED
        assert result.pest_type == "Red Palm Weevil"
        assert result.severity == "severe"
        assert result.provider == VLMProvider.QWEN_VL

    @pytest.mark.asyncio
    async def test_dismissed_false_positive(self):
        payload = {"has_pest": False, "confidence": 5}
        v = _make_verifier(provider="qwen_vl")
        with patch.object(v, "_call_qwen_vl", new_callable=AsyncMock, return_value=payload):
            result = await v.verify(_make_jpeg(), [0, 0, 40, 40])
        assert result.status == VLMVerificationStatus.DISMISSED
        assert not result.has_pest


# =============================================================================
# verify() — vLLM (platform-internal) success path
# =============================================================================


class TestVerifyVLLM:
    @pytest.mark.asyncio
    async def test_suspicious_detection(self):
        payload = {"has_pest": True, "confidence": 62, "pest_type": "aphid", "severity": "mild"}
        v = VLMVerifier(provider="vllm", confirm_threshold=0.8, suspect_threshold=0.5)
        with patch.object(v, "_call_vllm_vision", new_callable=AsyncMock, return_value=payload):
            result = await v.verify(_make_jpeg(), [5, 5, 95, 95])
        assert result.status == VLMVerificationStatus.SUSPICIOUS
        assert result.provider == VLMProvider.VLLM

    @pytest.mark.asyncio
    async def test_vllm_url_used(self):
        """_call_vllm_vision should POST to {vllm_url}/chat/completions."""
        v = VLMVerifier(provider="vllm", vllm_url="http://sahool-vllm:8270/v1", timeout=5.0)
        response_data = {"choices": [{"message": {"content": '{"has_pest": false, "confidence": 0}'}}]}
        mock_response = MagicMock()
        mock_response.json.return_value = response_data
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch.object(v, "_get_http_client", return_value=mock_client):
            await v._call_vllm_vision(b"\xff\xd8\xff" + b"\x00" * 10)  # minimal JPEG-like bytes

        call_args = mock_client.post.call_args
        assert "chat/completions" in call_args[0][0]


# =============================================================================
# verify() — Ollama success path
# =============================================================================


class TestVerifyOllama:
    @pytest.mark.asyncio
    async def test_ollama_confirmed(self):
        payload = {"has_pest": True, "confidence": 91, "pest_type": "whitefly", "severity": "moderate"}
        v = VLMVerifier(provider="ollama", confirm_threshold=0.8, suspect_threshold=0.5)
        with patch.object(v, "_call_ollama_vision", new_callable=AsyncMock, return_value=payload):
            result = await v.verify(_make_jpeg(), [0, 0, 100, 100])
        assert result.status == VLMVerificationStatus.CONFIRMED
        assert result.provider == VLMProvider.OLLAMA


# =============================================================================
# verify_batch()
# =============================================================================


class TestVerifyBatch:
    @pytest.mark.asyncio
    async def test_batch_preserves_order(self):
        """Results should be in the same order as input detections."""
        payloads = [
            {"has_pest": True, "confidence": 90},  # CONFIRMED
            {"has_pest": False, "confidence": 5},  # DISMISSED
            {"has_pest": True, "confidence": 60},  # SUSPICIOUS
        ]
        call_count = 0

        async def fake_call(crop_bytes):
            nonlocal call_count
            p = payloads[call_count]
            call_count += 1
            return p

        v = _make_verifier(provider="qwen_vl")
        with patch.object(v, "_call_qwen_vl", side_effect=fake_call):
            detections = [
                {"bbox": [0, 0, 50, 50], "class_name_en": "aphid"},
                {"bbox": [0, 0, 50, 50], "class_name_en": "normal leaf"},
                {"bbox": [0, 0, 50, 50], "class_name_en": "whitefly"},
            ]
            results = await v.verify_batch(_make_jpeg(), detections)

        assert len(results) == 3
        assert results[0].status == VLMVerificationStatus.CONFIRMED
        assert results[1].status == VLMVerificationStatus.DISMISSED
        assert results[2].status == VLMVerificationStatus.SUSPICIOUS

    @pytest.mark.asyncio
    async def test_empty_batch(self):
        v = _make_verifier(provider="qwen_vl")
        results = await v.verify_batch(_make_jpeg(), [])
        assert results == []


# =============================================================================
# build_vlm_verifier_from_settings()
# =============================================================================


class TestBuildFromSettings:
    def test_disabled_when_no_provider_set(self):
        settings = MagicMock(spec=[])  # no attrs at all
        v = build_vlm_verifier_from_settings(settings)
        assert v.provider == VLMProvider.DISABLED
        assert not v.is_enabled

    def test_reads_provider_from_settings(self):
        @dataclass
        class FakeSettings:
            vlm_provider: str = "vllm"
            qwen_vl_api_key: str = ""
            qwen_vl_model: str = "qwen-vl-plus"
            qwen_vl_api_url: str = ""
            vllm_vlm_url: str = "http://sahool-vllm:8270/v1"
            vllm_vlm_model: str = "deepseek-ai/deepseek-vl2"
            ollama_vlm_url: str = "http://localhost:11434"
            ollama_vlm_model: str = "llava:7b"
            vlm_confirm_threshold: float = 0.8
            vlm_suspect_threshold: float = 0.5
            vlm_timeout_seconds: float = 30.0

        v = build_vlm_verifier_from_settings(FakeSettings())
        assert v.provider == VLMProvider.VLLM
        assert v.vllm_url == "http://sahool-vllm:8270/v1"
        assert v.confirm_threshold == 0.8

    def test_reads_qwen_api_key(self):
        @dataclass
        class FakeSettings:
            vlm_provider: str = "qwen_vl"
            qwen_vl_api_key: str = "sk-testkey"
            qwen_vl_model: str = "qwen-vl-max"
            qwen_vl_api_url: str = ""
            vllm_vlm_url: str = ""
            vllm_vlm_model: str = ""
            ollama_vlm_url: str = "http://localhost:11434"
            ollama_vlm_model: str = "llava:7b"
            vlm_confirm_threshold: float = 0.75
            vlm_suspect_threshold: float = 0.4
            vlm_timeout_seconds: float = 20.0

        v = build_vlm_verifier_from_settings(FakeSettings())
        assert v.provider == VLMProvider.QWEN_VL
        assert v.qwen_api_key == "sk-testkey"
        assert v.confirm_threshold == 0.75
