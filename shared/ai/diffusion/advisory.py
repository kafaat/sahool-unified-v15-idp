"""
Diffusion Advisory Generator
============================
مولد الاستشارات بالانتشار

Diffusion-based agricultural advisory generation using
LLaDA-style masked diffusion language models.

Features:
    - Parallel generation (faster than autoregressive)
    - Template infilling for structured advisories
    - Edit flows for updating existing advisories
    - Bidirectional context for better coherence
    - Native bilingual (Arabic/English) support

Based on:
    - LLaDA: Large Language Diffusion Models
    - Dream 7B
    - dLLM library

Author: SAHOOL Platform Team
Updated: January 2026
"""

import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Any


class EditType(str, Enum):
    """Type of edit operation for Edit Flows."""

    INSERT = "insert"
    DELETE = "delete"
    SUBSTITUTE = "substitute"


@dataclass
class EditOperation:
    """
    An edit operation for Edit Flows.

    عملية تحرير لتدفقات التحرير
    """

    edit_type: EditType
    position: int  # Token position
    content: str | None = None  # New content for insert/substitute
    length: int = 1  # Length for delete/substitute


@dataclass
class DiffusionConfig:
    """
    Configuration for diffusion language model.

    إعدادات نموذج اللغة الانتشاري
    """

    # Model settings
    model_name: str = "llada-8b-instruct"
    model_path: str | None = None

    # Generation settings
    max_length: int = 512
    temperature: float = 0.7
    top_p: float = 0.9

    # Diffusion settings
    num_steps: int = 32  # Number of diffusion steps
    noise_schedule: str = "cosine"  # linear, cosine, sqrt

    # Performance settings
    batch_size: int = 1
    use_cache: bool = True
    device: str = "auto"  # auto, cpu, cuda

    # Language settings
    default_language: str = "ar"  # Arabic default for SAHOOL

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_name": self.model_name,
            "model_path": self.model_path,
            "max_length": self.max_length,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "num_steps": self.num_steps,
            "noise_schedule": self.noise_schedule,
            "batch_size": self.batch_size,
            "use_cache": self.use_cache,
            "device": self.device,
            "default_language": self.default_language,
        }


@dataclass
class DiffusionSamplerConfig:
    """
    Configuration for diffusion sampler.

    إعدادات عينات الانتشار
    """

    # Sampling strategy
    strategy: str = "ddpm"  # ddpm, ddim, euler

    # Step configuration
    num_steps: int = 32
    guidance_scale: float = 1.5  # Classifier-free guidance

    # Mask scheduling
    mask_schedule: str = "cosine"  # linear, cosine, sqrt

    # Parallel decoding
    parallel_decoding: bool = True
    chunk_size: int = 64  # Tokens per parallel chunk


@dataclass
class GenerationResult:
    """
    Result of diffusion generation.

    نتيجة التوليد بالانتشار
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    text_ar: str | None = None
    num_steps: int = 0
    total_time_ms: float = 0.0
    tokens_generated: int = 0
    model: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def tokens_per_second(self) -> float:
        """Calculate generation speed."""
        if self.total_time_ms > 0:
            return self.tokens_generated / (self.total_time_ms / 1000)
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "text_ar": self.text_ar,
            "num_steps": self.num_steps,
            "total_time_ms": self.total_time_ms,
            "tokens_generated": self.tokens_generated,
            "tokens_per_second": self.tokens_per_second,
            "model": self.model,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


class MaskScheduler:
    """
    Noise/mask scheduler for diffusion process.

    مجدول القناع لعملية الانتشار

    Controls how masks are applied during forward process
    and removed during reverse process.
    """

    def __init__(self, schedule: str = "cosine", num_steps: int = 32):
        """
        Initialize mask scheduler.

        Args:
            schedule: Schedule type (linear, cosine, sqrt)
            num_steps: Total diffusion steps
        """
        self.schedule = schedule
        self.num_steps = num_steps
        self._alphas = self._compute_alphas()

    def _compute_alphas(self) -> list[float]:
        """Compute alpha schedule (mask probabilities)."""
        alphas = []

        for t in range(self.num_steps + 1):
            ratio = t / self.num_steps

            if self.schedule == "linear":
                alpha = 1.0 - ratio
            elif self.schedule == "cosine":
                alpha = math.cos(ratio * math.pi / 2) ** 2
            elif self.schedule == "sqrt":
                alpha = math.sqrt(1.0 - ratio)
            else:
                alpha = 1.0 - ratio

            alphas.append(alpha)

        return alphas

    def get_mask_ratio(self, step: int) -> float:
        """
        Get mask ratio for given step.

        Args:
            step: Current diffusion step (0 = fully masked)

        Returns:
            Ratio of tokens to keep unmasked
        """
        if step >= len(self._alphas):
            return 1.0
        return self._alphas[step]

    def get_unmask_count(self, step: int, total_tokens: int) -> int:
        """
        Get number of tokens to unmask at this step.

        Args:
            step: Current diffusion step
            total_tokens: Total number of tokens

        Returns:
            Number of tokens to unmask
        """
        current_ratio = self.get_mask_ratio(step)
        prev_ratio = self.get_mask_ratio(step - 1) if step > 0 else 0.0

        unmask_ratio = current_ratio - prev_ratio
        return max(1, int(unmask_ratio * total_tokens))


class DiffusionAdvisoryGenerator:
    """
    Diffusion-based agricultural advisory generator.

    مولد الاستشارات الزراعية القائم على الانتشار

    Uses masked diffusion language models for generating
    agricultural advisories with:
    - Parallel generation (faster than autoregressive)
    - Template infilling (fill [MASK] tokens)
    - Edit flows (modify existing text)
    - Bidirectional context (better coherence)

    Example:
        ```python
        generator = DiffusionAdvisoryGenerator()

        # Generate advisory
        result = await generator.generate(
            prompt="كيف أسقي القمح في مرحلة التفريع؟",
            context={"crop": "wheat", "stage": "tillering"}
        )
        print(result.text)

        # Template infilling
        template = "يُنصح بالري كل [MASK] أيام بمعدل [MASK] مم"
        result = await generator.infill(template, context={...})

        # Edit existing advisory
        result = await generator.edit(
            original="الري كل 10 أيام",
            edits=[EditOperation(EditType.SUBSTITUTE, 8, "14", 2)]
        )
        ```
    """

    # Arabic agricultural templates
    TEMPLATES = {
        "irrigation": "يُنصح بري [MASK] كل [MASK] أيام بمعدل [MASK] مم للحصول على [MASK]",
        "fertilizer": "أضف [MASK] بمعدل [MASK] كجم/هكتار في مرحلة [MASK] لـ[MASK]",
        "pest_control": "لمكافحة [MASK]، استخدم [MASK] بمعدل [MASK] مع مراعاة [MASK]",
        "harvest": "يُفضل الحصاد عندما [MASK] ويكون [MASK] للحصول على [MASK]",
    }

    MASK_TOKEN = "[MASK]"

    def __init__(
        self,
        config: DiffusionConfig | None = None,
        sampler_config: DiffusionSamplerConfig | None = None,
    ):
        """
        Initialize Diffusion Advisory Generator.

        Args:
            config: Model configuration
            sampler_config: Sampler configuration
        """
        self.config = config or DiffusionConfig()
        self.sampler_config = sampler_config or DiffusionSamplerConfig()
        self._scheduler = MaskScheduler(
            schedule=self.config.noise_schedule,
            num_steps=self.sampler_config.num_steps,
        )
        self._model = None  # Lazy loaded
        self._tokenizer = None

    async def generate(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        language: str | None = None,
        max_length: int | None = None,
        num_steps: int | None = None,
    ) -> GenerationResult:
        """
        Generate advisory using diffusion.

        توليد استشارة باستخدام الانتشار

        Args:
            prompt: Input prompt (question from farmer)
            context: Additional context (crop, field, etc.)
            language: Output language (ar/en)
            max_length: Maximum output length
            num_steps: Number of diffusion steps

        Returns:
            GenerationResult with generated text
        """
        import time

        start_time = time.time()

        language = language or self.config.default_language
        max_length = max_length or self.config.max_length
        num_steps = num_steps or self.sampler_config.num_steps

        # Prepare input
        full_prompt = self._prepare_prompt(prompt, context, language)

        # Tokenize (simulated for now)
        tokens = self._tokenize(full_prompt)

        # Initialize with all masks
        output_tokens = [self.MASK_TOKEN] * max_length

        # Reverse diffusion process
        for step in range(num_steps):
            # Get number of tokens to unmask at this step
            unmask_count = self._scheduler.get_unmask_count(step, max_length)

            # Predict tokens for masked positions (simulated)
            predicted_tokens = await self._predict_tokens(
                tokens,
                output_tokens,
                step,
                num_steps,
            )

            # Select top tokens to unmask based on confidence
            output_tokens = self._unmask_tokens(
                output_tokens,
                predicted_tokens,
                unmask_count,
            )

        # Decode output
        generated_text = self._decode(output_tokens)

        elapsed_ms = (time.time() - start_time) * 1000

        return GenerationResult(
            text=generated_text,
            text_ar=generated_text if language == "ar" else None,
            num_steps=num_steps,
            total_time_ms=elapsed_ms,
            tokens_generated=len([t for t in output_tokens if t != self.MASK_TOKEN]),
            model=self.config.model_name,
            metadata={"context": context, "language": language},
        )

    async def infill(
        self,
        template: str,
        context: dict[str, Any] | None = None,
        num_steps: int | None = None,
    ) -> GenerationResult:
        """
        Fill in masked positions in template.

        ملء المواضع المقنعة في القالب

        This is a key advantage of diffusion models - they can
        naturally fill in blanks while considering both left
        and right context.

        Args:
            template: Template with [MASK] tokens
            context: Context for filling
            num_steps: Number of diffusion steps

        Returns:
            GenerationResult with filled template
        """
        import time

        start_time = time.time()

        num_steps = num_steps or self.sampler_config.num_steps

        # Parse template into tokens
        tokens = template.split()
        mask_positions = [
            i for i, t in enumerate(tokens) if t == self.MASK_TOKEN or self.MASK_TOKEN in t
        ]

        if not mask_positions:
            # No masks to fill
            return GenerationResult(
                text=template,
                num_steps=0,
                total_time_ms=0,
                tokens_generated=0,
                model=self.config.model_name,
            )

        # Infilling diffusion process
        output_tokens = tokens.copy()

        for step in range(num_steps):
            # Predict values for masked positions
            for pos in mask_positions:
                if output_tokens[pos] == self.MASK_TOKEN or self.MASK_TOKEN in output_tokens[pos]:
                    # Get prediction considering both contexts
                    prediction = await self._predict_single_token(
                        output_tokens,
                        pos,
                        context,
                        step,
                        num_steps,
                    )

                    # Probabilistically unmask based on step
                    unmask_prob = self._scheduler.get_mask_ratio(step + 1)
                    if self._should_unmask(unmask_prob):
                        output_tokens[pos] = prediction

        # Reconstruct text
        generated_text = " ".join(output_tokens)
        elapsed_ms = (time.time() - start_time) * 1000

        return GenerationResult(
            text=generated_text,
            num_steps=num_steps,
            total_time_ms=elapsed_ms,
            tokens_generated=len(mask_positions),
            model=self.config.model_name,
            metadata={"template": template, "mask_positions": mask_positions},
        )

    async def edit(
        self,
        original: str,
        edits: list[EditOperation],
        num_steps: int | None = None,
    ) -> GenerationResult:
        """
        Edit existing text using Edit Flows.

        تحرير النص الموجود باستخدام تدفقات التحرير

        Edit Flows allow making insertions, deletions, and
        substitutions while maintaining coherence.

        Args:
            original: Original text to edit
            edits: List of edit operations
            num_steps: Number of diffusion steps for refinement

        Returns:
            GenerationResult with edited text
        """
        import time

        start_time = time.time()

        num_steps = num_steps or self.sampler_config.num_steps // 2  # Fewer steps for edits

        # Parse into tokens
        tokens = original.split()

        # Apply edits (in reverse order to maintain positions)
        for edit in sorted(edits, key=lambda e: e.position, reverse=True):
            if edit.edit_type == EditType.INSERT:
                # Insert new content
                new_tokens = edit.content.split() if edit.content else [self.MASK_TOKEN]
                tokens = tokens[: edit.position] + new_tokens + tokens[edit.position :]

            elif edit.edit_type == EditType.DELETE:
                # Delete tokens
                end_pos = min(edit.position + edit.length, len(tokens))
                tokens = tokens[: edit.position] + tokens[end_pos:]

            elif edit.edit_type == EditType.SUBSTITUTE:
                # Replace with masks then fill
                end_pos = min(edit.position + edit.length, len(tokens))
                if edit.content:
                    new_tokens = edit.content.split()
                else:
                    new_tokens = [self.MASK_TOKEN] * edit.length
                tokens = tokens[: edit.position] + new_tokens + tokens[end_pos:]

        # Refine with diffusion (fill any remaining masks)
        output_tokens = tokens

        # Find positions that need refinement
        refine_positions = [i for i, t in enumerate(output_tokens) if self.MASK_TOKEN in t]

        # Refinement diffusion
        for step in range(num_steps):
            for pos in refine_positions:
                if self.MASK_TOKEN in output_tokens[pos]:
                    prediction = await self._predict_single_token(
                        output_tokens,
                        pos,
                        None,
                        step,
                        num_steps,
                    )
                    unmask_prob = self._scheduler.get_mask_ratio(step + 1)
                    if self._should_unmask(unmask_prob):
                        output_tokens[pos] = prediction

        generated_text = " ".join(output_tokens)
        elapsed_ms = (time.time() - start_time) * 1000

        return GenerationResult(
            text=generated_text,
            num_steps=num_steps,
            total_time_ms=elapsed_ms,
            tokens_generated=len(refine_positions),
            model=self.config.model_name,
            metadata={"original": original, "edits": [str(e) for e in edits]},
        )

    async def generate_from_template(
        self,
        template_name: str,
        context: dict[str, Any],
    ) -> GenerationResult:
        """
        Generate advisory from predefined template.

        توليد استشارة من قالب محدد مسبقاً

        Args:
            template_name: Name of template (irrigation, fertilizer, etc.)
            context: Context for filling template

        Returns:
            GenerationResult with generated advisory
        """
        template = self.TEMPLATES.get(template_name)
        if not template:
            raise ValueError(f"Unknown template: {template_name}")

        return await self.infill(template, context)

    def _prepare_prompt(
        self,
        prompt: str,
        context: dict[str, Any] | None,
        language: str,
    ) -> str:
        """Prepare full prompt with context."""
        parts = []

        # Add system instruction
        if language == "ar":
            parts.append("أنت مستشار زراعي خبير لمنصة سهول.")
        else:
            parts.append("You are an expert agricultural advisor for SAHOOL platform.")

        # Add context
        if context:
            context_str = ", ".join(f"{k}: {v}" for k, v in context.items())
            parts.append(f"Context: {context_str}")

        # Add question
        parts.append(f"Question: {prompt}")
        parts.append("Advisory:")

        return "\n".join(parts)

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenization (placeholder for real tokenizer)."""
        return text.split()

    def _decode(self, tokens: list[str]) -> str:
        """Decode tokens back to text."""
        # Filter out remaining masks and join
        clean_tokens = [t for t in tokens if t != self.MASK_TOKEN]
        return " ".join(clean_tokens)

    async def _predict_tokens(
        self,
        input_tokens: list[str],
        current_output: list[str],
        step: int,
        total_steps: int,
    ) -> list[tuple[str, float]]:
        """
        Predict tokens for masked positions.

        This is a placeholder - in production, this would call
        the actual diffusion model.

        Returns:
            List of (token, confidence) tuples
        """
        # Simulate prediction with agricultural vocabulary
        agricultural_vocab = [
            # Arabic irrigation terms
            "الري",
            "السقي",
            "الماء",
            "التربة",
            "الرطوبة",
            "مم",
            "لتر",
            "يوم",
            "أيام",
            "أسبوع",
            # English terms
            "irrigation",
            "water",
            "soil",
            "moisture",
            "mm",
            "liters",
            "days",
            "week",
            # Numbers
            "5",
            "7",
            "10",
            "14",
            "20",
            "25",
            "30",
            # Actions
            "يُنصح",
            "أضف",
            "تجنب",
            "راقب",
        ]

        import random

        predictions = []

        for i, token in enumerate(current_output):
            if token == self.MASK_TOKEN:
                # Confidence increases with steps
                confidence = 0.5 + (step / total_steps) * 0.5
                predicted = random.choice(agricultural_vocab)
                predictions.append((predicted, confidence))
            else:
                predictions.append((token, 1.0))

        return predictions

    async def _predict_single_token(
        self,
        tokens: list[str],
        position: int,
        context: dict[str, Any] | None,
        step: int,
        total_steps: int,
    ) -> str:
        """Predict a single token at given position."""
        predictions = await self._predict_tokens(
            [],
            tokens,
            step,
            total_steps,
        )

        if position < len(predictions):
            return predictions[position][0]

        return self.MASK_TOKEN

    def _unmask_tokens(
        self,
        current: list[str],
        predictions: list[tuple[str, float]],
        count: int,
    ) -> list[str]:
        """Unmask top-k tokens based on confidence."""
        # Find masked positions with their predictions
        masked_with_scores = []
        for i, (token, (pred, conf)) in enumerate(zip(current, predictions)):
            if token == self.MASK_TOKEN:
                masked_with_scores.append((i, pred, conf))

        # Sort by confidence and unmask top-k
        masked_with_scores.sort(key=lambda x: x[2], reverse=True)

        result = current.copy()
        for i, pred, _ in masked_with_scores[:count]:
            result[i] = pred

        return result

    def _should_unmask(self, probability: float) -> bool:
        """Probabilistically decide whether to unmask."""
        import random

        return random.random() < probability


# Convenience functions
async def generate_advisory(
    prompt: str,
    context: dict[str, Any] | None = None,
    language: str = "ar",
) -> GenerationResult:
    """
    Generate agricultural advisory using diffusion.

    توليد استشارة زراعية باستخدام الانتشار

    Args:
        prompt: Farmer's question
        context: Additional context
        language: Output language

    Returns:
        GenerationResult
    """
    generator = DiffusionAdvisoryGenerator()
    return await generator.generate(prompt, context, language)


async def infill_template(
    template: str,
    context: dict[str, Any] | None = None,
) -> GenerationResult:
    """
    Fill masked template using diffusion.

    ملء قالب مقنع باستخدام الانتشار

    Args:
        template: Template with [MASK] tokens
        context: Context for filling

    Returns:
        GenerationResult
    """
    generator = DiffusionAdvisoryGenerator()
    return await generator.infill(template, context)
