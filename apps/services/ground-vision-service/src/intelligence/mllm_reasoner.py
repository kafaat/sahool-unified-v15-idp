"""
MLLM-based Crop Timeline Reasoner - محلل الخط الزمني للمحاصيل
Based on: Qin et al. (2026) - Change-triggered MLLM invocation

This module uses Multimodal Large Language Models to analyze crop timelines
and provide semantic understanding of agricultural operations.
"""

import base64
import logging
import os
from datetime import UTC, datetime, timezone
from typing import Optional, Protocol

from pydantic import BaseModel, Field

from ..core.change_detection import ChangeDetector
from ..models.anomaly import AnomalySeverity, AnomalyType
from ..models.timeline import (
    CROP_TYPE_AR,
    GROWTH_STAGE_AR,
    CropTimelineAnalysis,
    CropTimelineEntry,
    CropType,
    FieldContext,
    GrowthStage,
    TimeSeriesFrame,
)

logger = logging.getLogger(__name__)


class LLMResponse(BaseModel):
    """Structured response from LLM"""

    crop_type: str
    crop_type_ar: str
    growth_stage: str
    growth_stage_ar: str
    confidence: float
    operations: list[dict] = Field(default_factory=list)
    anomalies: list[dict] = Field(default_factory=list)
    reasoning: str
    reasoning_ar: str
    health_score: float | None = None
    recommendations: list[str] = Field(default_factory=list)
    recommendations_ar: list[str] = Field(default_factory=list)


class LLMProvider(Protocol):
    """Protocol for LLM providers"""

    async def analyze(self, prompt: str, images: list[dict], response_format: type[BaseModel]) -> LLMResponse:
        """Analyze images with prompt."""
        ...


class AnthropicProvider:
    """Anthropic Claude provider for MLLM analysis."""

    def __init__(self, api_key: str | None = None):
        """Initialize Anthropic provider."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None

    def _ensure_client(self):
        """Ensure client is initialized."""
        if self.client is None:
            try:
                from anthropic import AsyncAnthropic

                self.client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                logger.error("anthropic package not installed")
                raise

    async def analyze(self, prompt: str, images: list[dict], response_format: type[BaseModel]) -> LLMResponse:
        """Analyze images using Claude."""
        self._ensure_client()

        # Build message content with images
        content = []

        for img in images:
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": img["data"],
                    },
                }
            )
            content.append(
                {
                    "type": "text",
                    "text": f"[Frame timestamp: {img['timestamp']}]",
                }
            )

        content.append(
            {
                "type": "text",
                "text": prompt,
            }
        )

        # Call Claude
        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": content}],
        )

        # Parse response
        return self._parse_response(response.content[0].text)

    def _parse_response(self, text: str) -> LLMResponse:
        """Parse LLM response into structured format."""
        import json

        try:
            # Try to extract JSON from response
            start_idx = text.find("{")
            end_idx = text.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                data = json.loads(json_str)
                return LLMResponse(**data)
        except Exception as e:
            logger.warning(f"Failed to parse JSON response: {e}")

        # Fallback to default response
        return LLMResponse(
            crop_type="unknown",
            crop_type_ar="غير معروف",
            growth_stage="unknown",
            growth_stage_ar="غير معروف",
            confidence=0.0,
            reasoning=text,
            reasoning_ar="",
        )


class OllamaProvider:
    """Ollama local LLM provider for MLLM analysis."""

    def __init__(self, base_url: str | None = None, model: str = "llava:13b"):
        """Initialize Ollama provider."""
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model

    async def analyze(self, prompt: str, images: list[dict], response_format: type[BaseModel]) -> LLMResponse:
        """Analyze images using Ollama."""
        import aiohttp

        # Ollama multimodal API
        url = f"{self.base_url}/api/generate"

        # Prepare request
        image_data = [img["data"] for img in images]

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": image_data,
            "stream": False,
            "format": "json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Ollama API error: {response.status}")
                result = await response.json()

        return self._parse_response(result.get("response", ""))

    def _parse_response(self, text: str) -> LLMResponse:
        """Parse LLM response into structured format."""
        import json

        try:
            start_idx = text.find("{")
            end_idx = text.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                data = json.loads(json_str)
                return LLMResponse(**data)
        except Exception as e:
            logger.warning(f"Failed to parse JSON response: {e}")

        return LLMResponse(
            crop_type="unknown",
            crop_type_ar="غير معروف",
            growth_stage="unknown",
            growth_stage_ar="غير معروف",
            confidence=0.0,
            reasoning=text,
            reasoning_ar="",
        )


class CropTimelineReasoner:
    """
    Multimodal LLM-based crop timeline analysis.

    Based on: Qin et al. (2026) - Change-triggered MLLM invocation

    This reasoner uses expensive MLLM calls only when significant changes
    are detected in the frame sequence, optimizing costs while maintaining
    accuracy.
    """

    ANALYSIS_PROMPT_TEMPLATE = """
أنت خبير زراعي متخصص في تحليل صور الحقول الزراعية.

## السياق
- معرف الحقل: {field_id}
- الموقع: {location_name} ({lat}, {lon})
- المساحة: {area_hectares} هكتار
- المحصول المتوقع: {expected_crop} / {expected_crop_ar}
- تاريخ الزراعة المتوقع: {expected_planting_date}
- الدورة الزراعية السابقة: {rotation_history}
- نوع التربة: {soil_type}
- نظام الري: {irrigation_type}

## المطلوب
حلل سلسلة الصور الزمنية التالية وحدد:
1. نوع المحصول الفعلي (crop_type, crop_type_ar)
2. مرحلة النمو الحالية (growth_stage, growth_stage_ar)
3. نسبة الثقة بالتحليل (confidence: 0.0-1.0)
4. أي عمليات زراعية مرئية (operations: [{{"type": "...", "type_ar": "...", "confidence": 0.0-1.0}}])
5. أي حالات غير طبيعية (anomalies: [{{"type": "...", "severity": "...", "description": "...", "description_ar": "..."}}])
6. درجة صحة المحصول (health_score: 0.0-1.0)
7. التوصيات (recommendations, recommendations_ar)
8. التفسير (reasoning, reasoning_ar)

## أنواع المحاصيل المعروفة
wheat/قمح, barley/شعير, rice/أرز, corn/ذرة, sorghum/ذرة رفيعة, alfalfa/برسيم,
date_palm/نخيل, citrus/حمضيات, olive/زيتون, tomato/طماطم, cucumber/خيار,
potato/بطاطا, onion/بصل, grape/عنب

## مراحل النمو المعروفة
fallow/بور, prepared/معدة, planting/زراعة, germination/إنبات, emergence/بزوغ,
seedling/شتلة, vegetative/نمو خضري, tillering/تفريع, jointing/عقد السيقان,
booting/انتفاخ السنبلة, heading/إسبال, flowering/إزهار, grain_fill/امتلاء الحبوب,
maturity/نضج, harvest_ready/جاهز للحصاد, harvested/محصود

## الصور
الصور مرتبة زمنياً من الأقدم إلى الأحدث.

أجب بتنسيق JSON فقط.
"""

    def __init__(
        self,
        llm_provider: LLMProvider | None = None,
        change_detector: ChangeDetector | None = None,
        change_threshold: float = 0.15,
        max_frames_per_analysis: int = 5,
    ):
        """
        Initialize crop timeline reasoner.

        Args:
            llm_provider: LLM provider for analysis (auto-detected if None)
            change_detector: Change detector for triggering analysis
            change_threshold: Threshold for triggering MLLM analysis
            max_frames_per_analysis: Maximum frames to include in analysis
        """
        self.change_threshold = change_threshold
        self.max_frames = max_frames_per_analysis

        # Initialize change detector
        self.change_detector = change_detector or ChangeDetector(trigger_threshold=change_threshold)

        # Auto-detect LLM provider
        if llm_provider is None:
            self.llm = self._auto_detect_provider()
        else:
            self.llm = llm_provider

        logger.info(f"CropTimelineReasoner initialized with {type(self.llm).__name__}")

    def _auto_detect_provider(self) -> LLMProvider:
        """Auto-detect available LLM provider."""
        # Try Anthropic first
        if os.getenv("ANTHROPIC_API_KEY"):
            return AnthropicProvider()

        # Fall back to Ollama
        return OllamaProvider()

    async def should_analyze(
        self,
        frames: list[TimeSeriesFrame],
        frame_images: list[bytes],
    ) -> bool:
        """
        Determine if MLLM analysis should be triggered.

        Args:
            frames: Time series frames metadata
            frame_images: Actual frame image bytes

        Returns:
            True if analysis should be triggered
        """
        if len(frames) < 2:
            return True  # Always analyze first frames

        # Convert last two frames to numpy for change detection
        import io

        import numpy as np
        from PIL import Image

        # Load last two images
        img1 = Image.open(io.BytesIO(frame_images[-2]))
        img2 = Image.open(io.BytesIO(frame_images[-1]))

        arr1 = np.array(img1)
        arr2 = np.array(img2)

        # Compute change
        result = await self.change_detector.compute_change(arr1, arr2)

        logger.debug(f"Change score: {result.change_score:.3f}, trigger: {result.should_trigger_analysis}")

        return result.should_trigger_analysis

    async def analyze_timeline(
        self,
        field_id: str,
        frames: list[TimeSeriesFrame],
        frame_images: list[bytes],
        context: FieldContext,
        force: bool = False,
    ) -> CropTimelineAnalysis | None:
        """
        Analyze temporal sequence to identify crop stages and events.

        Only invokes expensive MLLM when significant change detected,
        unless force=True.

        Args:
            field_id: Field identifier
            frames: Time series frame metadata
            frame_images: Frame image bytes
            context: Field context information
            force: Force analysis regardless of change detection

        Returns:
            CropTimelineAnalysis or None if no analysis needed
        """
        import time

        start_time = time.time()

        # Check if analysis is warranted
        if not force and len(frames) >= 2:
            should_run = await self.should_analyze(frames, frame_images)
            if not should_run:
                logger.debug(f"Skipping MLLM analysis for {field_id} - no significant change")
                return None

        # Select frames for analysis (most recent)
        selected_frames = frames[-self.max_frames :]
        selected_images = frame_images[-self.max_frames :]

        # Build prompt
        prompt = self._build_prompt(field_id, context)

        # Prepare images for MLLM
        image_data = [
            {
                "data": base64.b64encode(img_bytes).decode(),
                "timestamp": frame.captured_at.isoformat(),
            }
            for frame, img_bytes in zip(selected_frames, selected_images)
        ]

        # Query MLLM
        try:
            response = await self.llm.analyze(
                prompt=prompt,
                images=image_data,
                response_format=LLMResponse,
            )
        except Exception as e:
            logger.error(f"MLLM analysis failed: {e}")
            return None

        processing_time = int((time.time() - start_time) * 1000)

        # Convert response to CropTimelineAnalysis
        analysis = CropTimelineAnalysis(
            analysis_id=f"analysis_{field_id}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            field_id=field_id,
            crop_type=self._parse_crop_type(response.crop_type),
            crop_type_ar=response.crop_type_ar
            or CROP_TYPE_AR.get(self._parse_crop_type(response.crop_type), "غير معروف"),
            current_stage=self._parse_growth_stage(response.growth_stage),
            current_stage_ar=response.growth_stage_ar
            or GROWTH_STAGE_AR.get(self._parse_growth_stage(response.growth_stage), "غير معروف"),
            stage_confidence=response.confidence,
            health_score=response.health_score,
            operations_detected=response.operations,
            anomalies=response.anomalies,
            reasoning=response.reasoning,
            reasoning_ar=response.reasoning_ar,
            recommendations=response.recommendations,
            recommendations_ar=response.recommendations_ar,
            frames_analyzed=len(selected_frames),
            processing_time_ms=processing_time,
            model_used=type(self.llm).__name__,
            tenant_id=context.tenant_id,
        )

        logger.info(
            f"Analyzed {field_id}: {analysis.crop_type.value} at {analysis.current_stage.value} "
            f"(confidence: {analysis.stage_confidence:.2f})"
        )

        return analysis

    def _build_prompt(
        self,
        field_id: str,
        context: FieldContext,
    ) -> str:
        """Build analysis prompt with field context."""
        return self.ANALYSIS_PROMPT_TEMPLATE.format(
            field_id=field_id,
            location_name=context.location_name,
            lat=context.lat,
            lon=context.lon,
            area_hectares=context.area_hectares,
            expected_crop=context.expected_crop.value if context.expected_crop else "unknown",
            expected_crop_ar=context.expected_crop_ar or "غير محدد",
            expected_planting_date=context.expected_planting_date.isoformat()
            if context.expected_planting_date
            else "غير محدد",
            rotation_history=str(context.rotation_history) if context.rotation_history else "غير متوفر",
            soil_type=context.soil_type or "غير محدد",
            irrigation_type=context.irrigation_type or "غير محدد",
        )

    def _parse_crop_type(self, value: str) -> CropType:
        """Parse crop type from string."""
        try:
            return CropType(value.lower())
        except ValueError:
            return CropType.UNKNOWN

    def _parse_growth_stage(self, value: str) -> GrowthStage:
        """Parse growth stage from string."""
        try:
            return GrowthStage(value.lower())
        except ValueError:
            return GrowthStage.UNKNOWN


class TimelineEntryGenerator:
    """Generate timeline entries from analysis results."""

    def __init__(self, tenant_id: str):
        """Initialize generator."""
        self.tenant_id = tenant_id

    def create_entry(
        self,
        analysis: CropTimelineAnalysis,
        evidence_frames: list[str],
    ) -> CropTimelineEntry:
        """Create a timeline entry from analysis."""
        return CropTimelineEntry(
            entry_id=f"entry_{analysis.field_id}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            field_id=analysis.field_id,
            crop_type=analysis.crop_type,
            crop_type_ar=analysis.crop_type_ar,
            growth_stage=analysis.current_stage,
            growth_stage_ar=analysis.current_stage_ar,
            confidence=analysis.stage_confidence,
            evidence_frames=evidence_frames,
            analysis_method="mllm",
            notes=analysis.reasoning[:500] if analysis.reasoning else None,
            notes_ar=analysis.reasoning_ar[:500] if analysis.reasoning_ar else None,
            tenant_id=self.tenant_id,
        )
