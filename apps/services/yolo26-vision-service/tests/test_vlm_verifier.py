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
# _parse_has_pest  (robust string / numeric handling)
# =============================================================================


class TestParseHasPest:
    def test_bool_true(self):
        assert VLMVerifier._parse_has_pest(True) is True

    def test_bool_false(self):
        assert VLMVerifier._parse_has_pest(False) is False

    def test_int_nonzero(self):
        assert VLMVerifier._parse_has_pest(1) is True

    def test_int_zero(self):
        assert VLMVerifier._parse_has_pest(0) is False

    def test_string_true(self):
        assert VLMVerifier._parse_has_pest("true") is True
        assert VLMVerifier._parse_has_pest("True") is True
        assert VLMVerifier._parse_has_pest("yes") is True
        assert VLMVerifier._parse_has_pest("1") is True

    def test_string_false(self):
        # A bare bool(str) would treat "false" as True; _parse_has_pest must not.
        assert VLMVerifier._parse_has_pest("false") is False
        assert VLMVerifier._parse_has_pest("False") is False
        assert VLMVerifier._parse_has_pest("no") is False
        assert VLMVerifier._parse_has_pest("0") is False
        assert VLMVerifier._parse_has_pest("") is False

    def test_unknown_type_returns_false(self):
        assert VLMVerifier._parse_has_pest(None) is False
        assert VLMVerifier._parse_has_pest([]) is False


# =============================================================================
# _crop_region and verify() accept pre-decoded PIL Image
# =============================================================================


class TestPredecodedImage:
    def test_crop_region_accepts_pil_image(self):
        """_crop_region should accept a PIL Image without re-decoding bytes."""
        image_bytes = _make_jpeg(200, 200)
        v = VLMVerifier()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # Passing PIL Image directly should produce the same crop as bytes path.
        cropped_from_pil = v._crop_region(pil_image, [10, 10, 100, 100])
        cropped_from_bytes = v._crop_region(image_bytes, [10, 10, 100, 100])
        img_pil = Image.open(io.BytesIO(cropped_from_pil))
        img_bytes = Image.open(io.BytesIO(cropped_from_bytes))
        assert img_pil.size == img_bytes.size

    @pytest.mark.asyncio
    async def test_verify_accepts_pil_image(self):
        """verify() should accept a pre-decoded PIL Image."""
        payload = {"has_pest": True, "confidence": 80}
        v = _make_verifier(provider="qwen_vl")
        pil_image = Image.open(io.BytesIO(_make_jpeg())).convert("RGB")
        with patch.object(v, "_call_qwen_vl", new_callable=AsyncMock, return_value=payload):
            result = await v.verify(pil_image, [0, 0, 50, 50])
        assert result.status == VLMVerificationStatus.CONFIRMED


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


# =============================================================================
# _call_qwen_vl — httpx-level tests
# =============================================================================


class TestCallQwenVL:
    """Test _call_qwen_vl against a mocked httpx client (verifies HTTP mechanics)."""

    @pytest.mark.asyncio
    async def test_posts_to_qwen_url(self):
        """Should POST to the configured Qwen-VL URL."""
        v = _make_verifier(provider="qwen_vl", qwen_api_key="test-key")
        response_json = {
            "output": {
                "choices": [{"message": {"content": '{"has_pest": true, "confidence": 85, "pest_type": "aphid"}'}}]
            }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = response_json
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch.object(v, "_get_http_client", return_value=mock_client):
            result = await v._call_qwen_vl(_make_jpeg())

        assert result["has_pest"] is True
        assert result["confidence"] == 85
        assert result["pest_type"] == "aphid"
        call_url = mock_client.post.call_args[0][0]
        assert "dashscope" in call_url or "aliyuncs" in call_url

    @pytest.mark.asyncio
    async def test_handles_list_content(self):
        """Qwen-VL may return content as a list of text dicts — should join them."""
        v = _make_verifier(provider="qwen_vl")
        response_json = {
            "output": {
                "choices": [
                    {
                        "message": {
                            "content": [
                                {"text": '{"has_pest": false,'},
                                {"text": ' "confidence": 10}'},
                            ]
                        }
                    }
                ]
            }
        }
        mock_response = MagicMock()
        mock_response.json.return_value = response_json
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch.object(v, "_get_http_client", return_value=mock_client):
            result = await v._call_qwen_vl(_make_jpeg())

        assert result["has_pest"] is False
        assert result["confidence"] == 10

    @pytest.mark.asyncio
    async def test_malformed_json_returns_empty_dict(self):
        """Completely unparseable Qwen response → _extract_json returns {}."""
        v = _make_verifier(provider="qwen_vl")
        response_json = {"output": {"choices": [{"message": {"content": "not valid json at all!!!"}}]}}
        mock_response = MagicMock()
        mock_response.json.return_value = response_json
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch.object(v, "_get_http_client", return_value=mock_client):
            result = await v._call_qwen_vl(_make_jpeg())

        # _extract_json returns {} on total failure → verify() will use defaults
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_http_error_propagates(self):
        """HTTP 4xx/5xx should propagate as httpx.HTTPStatusError."""
        v = _make_verifier(provider="qwen_vl")
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401", request=MagicMock(), response=MagicMock()
        )

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch.object(v, "_get_http_client", return_value=mock_client):
            with pytest.raises(httpx.HTTPStatusError):
                await v._call_qwen_vl(_make_jpeg())


# =============================================================================
# _call_ollama_vision — httpx-level tests
# =============================================================================


class TestCallOllamaVision:
    """Test _call_ollama_vision against a mocked httpx client."""

    @pytest.mark.asyncio
    async def test_posts_to_ollama_generate(self):
        """Should POST to {ollama_url}/api/generate."""
        v = VLMVerifier(provider="ollama", ollama_url="http://localhost:11434", ollama_model="llava:7b")
        response_json = {"response": '{"has_pest": true, "confidence": 78, "severity": "moderate"}'}
        mock_response = MagicMock()
        mock_response.json.return_value = response_json
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch.object(v, "_get_http_client", return_value=mock_client):
            result = await v._call_ollama_vision(_make_jpeg())

        assert result["has_pest"] is True
        assert result["confidence"] == 78
        call_url = mock_client.post.call_args[0][0]
        assert "/api/generate" in call_url

    @pytest.mark.asyncio
    async def test_malformed_json_returns_empty_dict(self):
        """Completely unparseable Ollama response → {} so verify() uses safe defaults."""
        v = VLMVerifier(provider="ollama", ollama_url="http://localhost:11434")
        response_json = {"response": "```no braces here at all```"}
        mock_response = MagicMock()
        mock_response.json.return_value = response_json
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch.object(v, "_get_http_client", return_value=mock_client):
            result = await v._call_ollama_vision(_make_jpeg())

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_timeout_bubbles_up_to_verify(self):
        """A timeout from _call_ollama_vision should be caught by verify() → ERROR status."""
        v = VLMVerifier(provider="ollama", timeout=1.0)
        with patch.object(v, "_call_ollama_vision", side_effect=httpx.TimeoutException("timeout")):
            result = await v.verify(_make_jpeg(), [0, 0, 50, 50])
        assert result.status == VLMVerificationStatus.ERROR
        assert result.error == "VLM request timed out"


# =============================================================================
# _crop_region — RGB normalisation for pre-decoded images
# =============================================================================


class TestCropRegionRGBNorm:
    """Ensure _crop_region converts RGBA/P-mode PIL images to RGB before JPEG save."""

    def test_rgba_image_saves_without_error(self):
        """RGBA input (pre-decoded) must not raise OSError when saving as JPEG."""
        rgba_img = Image.new("RGBA", (200, 200), color=(100, 150, 200, 128))
        v = _make_verifier()
        crop_bytes = v._crop_region(rgba_img, [10, 10, 100, 100])
        # Should not raise; result should be valid JPEG bytes
        assert crop_bytes[:2] == b"\xff\xd8"  # JPEG magic bytes

    def test_p_mode_image_saves_without_error(self):
        """Palette-mode (P) input must be converted and saved successfully."""
        p_img = Image.new("P", (150, 150))
        v = _make_verifier()
        crop_bytes = v._crop_region(p_img, [0, 0, 80, 80])
        assert crop_bytes[:2] == b"\xff\xd8"

    def test_rgb_image_unchanged_path(self):
        """RGB images should pass through _crop_region without additional conversion."""
        rgb_img = Image.new("RGB", (100, 100), color=(80, 160, 40))
        v = _make_verifier()
        crop_bytes = v._crop_region(rgb_img, [5, 5, 60, 60])
        assert crop_bytes[:2] == b"\xff\xd8"
