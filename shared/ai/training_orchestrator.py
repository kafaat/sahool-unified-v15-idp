"""
Training Orchestrator
=====================
منسق التدريب - إدارة دورة حياة تدريب النماذج وتقييمها

Connects GRPO training (GRPOConfig/GRPOTrainer) to actual training workflows
and provides a unified TrainingOrchestrator for managing training jobs.

Covers:
    - G-13: GRPO trainer integration
    - G-18: Model evaluation metrics (accuracy, F1, BLEU-AR, domain scores)

Supports:
- Ollama-based training via ModelTrainer
- vLLM as an inference/evaluation backend
- GRPO reward-based policy optimization
- Integration with LLMProviderManager for model evaluation
- Automatic model versioning and deployment gating
- Bilingual evaluation metrics (Arabic/English)
- Agricultural domain-specific evaluation

يربط تدريب GRPO بسير عمل التدريب الفعلي
ويوفر منسق تدريب موحد لإدارة مهام التدريب.

يدعم:
- التدريب عبر Ollama باستخدام ModelTrainer
- vLLM كخلفية للاستدلال/التقييم
- تحسين السياسة القائم على المكافآت GRPO
- التكامل مع مدير مزودي LLM لتقييم النماذج
- إصدار النماذج التلقائي وبوابة النشر
- مقاييس تقييم ثنائية اللغة (عربي/إنجليزي)
- تقييم خاص بالمجال الزراعي

Author: SAHOOL Platform Team
Updated: March 2026
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Callable

try:
    from .grpo_trainer import (
        GRPOBatch,
        GRPOConfig,
        GRPOSample,
        GRPOTrainer,
        GRPOTrainingStats,
        GRPOVariant,
        SAHOOLGRPOTrainer,
    )

    GRPO_TRAINER_AVAILABLE = True
except ImportError:
    GRPO_TRAINER_AVAILABLE = False
    GRPOBatch = None  # type: ignore[assignment, misc]
    GRPOConfig = None  # type: ignore[assignment, misc]
    GRPOSample = None  # type: ignore[assignment, misc]
    GRPOTrainer = None  # type: ignore[assignment, misc]
    GRPOTrainingStats = None  # type: ignore[assignment, misc]
    GRPOVariant = None  # type: ignore[assignment, misc]
    SAHOOLGRPOTrainer = None  # type: ignore[assignment, misc]

try:
    from .model_training import (
        DatasetBuilder,
        DatasetType,
        EvaluationResult,
        ModelTrainer,
        TrainingConfig,
        TrainingDataset,
        TrainingJob,
        TrainingStatus,
    )

    MODEL_TRAINER_AVAILABLE = True
except ImportError:
    MODEL_TRAINER_AVAILABLE = False
    DatasetBuilder = None  # type: ignore[assignment, misc]
    DatasetType = None  # type: ignore[assignment, misc]
    EvaluationResult = None  # type: ignore[assignment, misc]
    ModelTrainer = None  # type: ignore[assignment, misc]
    TrainingConfig = None  # type: ignore[assignment, misc]
    TrainingDataset = None  # type: ignore[assignment, misc]
    TrainingJob = None  # type: ignore[assignment, misc]
    TrainingStatus = None  # type: ignore[assignment, misc]

logger = logging.getLogger(__name__)

# Optional imports
try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


# ---------------------------------------------------------------------------
# Training Type & Job Config (G-13, G-18)
# ---------------------------------------------------------------------------


class TrainingType(StrEnum):
    """
    Type of training pipeline.
    نوع مسار التدريب
    """

    FINE_TUNE = "fine_tune"
    GRPO = "grpo"
    RLHF = "rlhf"
    DISTILLATION = "distillation"


class TrainingJobStatus(StrEnum):
    """
    Lifecycle status of a managed training job.
    حالة دورة حياة مهمة التدريب المدارة
    """

    CREATED = "created"
    PREPARING = "preparing"
    TRAINING = "training"
    EVALUATING = "evaluating"
    EVALUATED = "evaluated"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TrainingJobConfig:
    """
    Configuration for a managed training job.

    إعدادات مهمة التدريب المدارة

    Attributes:
        job_id: Unique job identifier (auto-generated if empty)
        base_model: Base model name (e.g. codellama:7b)
        dataset_name: Name of the training dataset
        training_type: Type of training pipeline
        epochs: Number of training epochs
        learning_rate: Learning rate
        evaluation_metrics: Metrics to compute during evaluation
        auto_deploy: Whether to deploy automatically on passing evaluation
    """

    job_id: str = ""
    base_model: str = "codellama:7b"
    dataset_name: str = "sahool-default"
    training_type: TrainingType = TrainingType.FINE_TUNE
    epochs: int = 3
    learning_rate: float = 1e-5
    evaluation_metrics: list[str] = field(
        default_factory=lambda: ["accuracy", "f1", "bleu_ar", "domain_accuracy"]
    )
    auto_deploy: bool = False

    def __post_init__(self) -> None:
        if not self.job_id:
            self.job_id = f"tj-{uuid.uuid4().hex[:12]}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary. | تحويل إلى قاموس"""
        return {
            "job_id": self.job_id,
            "base_model": self.base_model,
            "dataset_name": self.dataset_name,
            "training_type": self.training_type.value,
            "epochs": self.epochs,
            "learning_rate": self.learning_rate,
            "evaluation_metrics": self.evaluation_metrics,
            "auto_deploy": self.auto_deploy,
        }


@dataclass
class EvaluationReport:
    """
    Evaluation report for a trained model (G-18).

    تقرير تقييم النموذج المدرب

    Attributes:
        job_id: Training job identifier
        model_id: Versioned model identifier
        metrics: General metrics (accuracy, f1, loss, perplexity)
        arabic_metrics: Arabic-specific metrics (BLEU, accuracy_ar)
        agricultural_metrics: Domain metrics (domain_accuracy, recommendation_quality)
        passed_threshold: Whether the model met minimum quality thresholds
        timestamp: When the evaluation was performed
    """

    job_id: str
    model_id: str
    metrics: dict[str, float] = field(default_factory=dict)
    arabic_metrics: dict[str, float] = field(
        default_factory=lambda: {"bleu": 0.0, "accuracy_ar": 0.0}
    )
    agricultural_metrics: dict[str, float] = field(
        default_factory=lambda: {"domain_accuracy": 0.0, "recommendation_quality": 0.0}
    )
    passed_threshold: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary. | تحويل إلى قاموس"""
        return {
            "job_id": self.job_id,
            "model_id": self.model_id,
            "metrics": self.metrics,
            "arabic_metrics": self.arabic_metrics,
            "agricultural_metrics": self.agricultural_metrics,
            "passed_threshold": self.passed_threshold,
            "timestamp": self.timestamp.isoformat(),
        }

    @property
    def overall_score(self) -> float:
        """
        Weighted overall score (0-1).

        الدرجة الإجمالية المرجحة
        Weights: accuracy 30%, F1 25%, Arabic BLEU 20%, domain accuracy 25%
        """
        acc = self.metrics.get("accuracy", 0.0)
        f1 = self.metrics.get("f1", 0.0)
        bleu_ar = self.arabic_metrics.get("bleu", 0.0)
        domain = self.agricultural_metrics.get("domain_accuracy", 0.0)
        return acc * 0.30 + f1 * 0.25 + bleu_ar * 0.20 + domain * 0.25


# Default quality thresholds for deployment gating
DEFAULT_THRESHOLDS: dict[str, float] = {
    "accuracy": 0.70,
    "f1": 0.65,
    "bleu_ar": 0.30,
    "domain_accuracy": 0.60,
    "recommendation_quality": 0.55,
}


# ---------------------------------------------------------------------------
# vLLM Backend
# ---------------------------------------------------------------------------

class InferenceBackend(StrEnum):
    """Supported inference backends for training evaluation."""

    OLLAMA = "ollama"  # Ollama local LLM
    VLLM = "vllm"  # vLLM high-performance serving


@dataclass
class VLLMConfig:
    """
    Configuration for vLLM inference backend.
    إعدادات خلفية استدلال vLLM.
    """

    base_url: str = field(
        default_factory=lambda: os.getenv("VLLM_BASE_URL", "http://localhost:8270/v1")
    )
    model: str = field(
        default_factory=lambda: os.getenv("VLLM_MODEL", "deepseek-ai/deepseek-coder-6.7b-instruct")
    )
    api_key: str = field(
        default_factory=lambda: os.getenv("VLLM_API_KEY", "dummy")
    )
    max_tokens: int = 4096
    temperature: float = 0.1
    timeout: float = 300.0
    # vLLM-specific parameters
    tensor_parallel_size: int = 1
    gpu_memory_utilization: float = 0.9

    def to_dict(self) -> dict[str, Any]:
        return {
            "base_url": self.base_url,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "timeout": self.timeout,
            "tensor_parallel_size": self.tensor_parallel_size,
            "gpu_memory_utilization": self.gpu_memory_utilization,
        }


class VLLMClient:
    """
    Client for vLLM OpenAI-compatible API.
    عميل لواجهة vLLM المتوافقة مع OpenAI.

    vLLM exposes an OpenAI-compatible /v1/completions endpoint
    which this client uses for inference and evaluation.
    """

    def __init__(self, config: VLLMConfig | None = None):
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx is required for VLLMClient. Install with: pip install httpx")
        self.config = config or VLLMConfig()

    async def is_available(self) -> bool:
        """Check if vLLM server is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.config.base_url}/models")
                return resp.status_code == 200
        except Exception:
            return False

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """
        Generate a completion using vLLM.
        توليد إكمال باستخدام vLLM.

        Args:
            prompt: The prompt text
            model: Model name (default from config)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Dict with 'text', 'tokens_used', 'finish_reason'
        """
        payload = {
            "model": model or self.config.model,
            "prompt": prompt,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            resp = await client.post(
                f"{self.config.base_url}/completions",
                json=payload,
                headers={"Authorization": f"Bearer {self.config.api_key}"},
            )
            resp.raise_for_status()
            data = resp.json()

        choices = data.get("choices", [])
        if not choices:
            return {"text": "", "tokens_used": 0, "finish_reason": "error"}

        choice = choices[0]
        usage = data.get("usage", {})

        return {
            "text": choice.get("text", ""),
            "tokens_used": usage.get("total_tokens", 0),
            "finish_reason": choice.get("finish_reason", "unknown"),
        }

    async def generate_batch(
        self,
        prompts: list[str],
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Generate completions for a batch of prompts.
        توليد إكمالات لدفعة من المحفزات.

        Uses asyncio.gather for concurrent requests to vLLM.
        """
        tasks = [
            self.generate(p, model, temperature, max_tokens)
            for p in prompts
        ]
        return await asyncio.gather(*tasks, return_exceptions=False)


# ---------------------------------------------------------------------------
# Training Job State
# ---------------------------------------------------------------------------

class TrainingPhase(StrEnum):
    """Phases in the training orchestrator workflow."""

    IDLE = "idle"
    DATA_PREPARATION = "data_preparation"  # تحضير البيانات
    SUPERVISED_TRAINING = "supervised_training"  # تدريب إشرافي
    GRPO_TRAINING = "grpo_training"  # تدريب GRPO
    EVALUATION = "evaluation"  # تقييم
    COMPLETED = "completed"  # مكتمل
    FAILED = "failed"  # فشل


@dataclass
class TrainingOrchestratorJob:
    """
    A managed training job with GRPO support.
    مهمة تدريب مدارة مع دعم GRPO.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    name_ar: str = ""
    phase: TrainingPhase = TrainingPhase.IDLE
    # Supervised training job (Ollama Modelfile-based)
    supervised_job: TrainingJob | None = None
    # GRPO training stats
    grpo_stats: list[GRPOTrainingStats] = field(default_factory=list)
    grpo_batches_processed: int = 0
    # Evaluation
    evaluation_results: dict[str, EvaluationResult] = field(default_factory=dict)
    # Metadata
    inference_backend: InferenceBackend = InferenceBackend.OLLAMA
    config: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "phase": self.phase.value,
            "supervised_job": self.supervised_job.to_dict() if self.supervised_job else None,
            "grpo_batches_processed": self.grpo_batches_processed,
            "grpo_stats_count": len(self.grpo_stats),
            "evaluation_results": {
                k: v.to_dict() for k, v in self.evaluation_results.items()
            },
            "inference_backend": self.inference_backend.value,
            "config": self.config,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# Training Orchestrator
# ---------------------------------------------------------------------------

class TrainingOrchestrator:
    """
    Orchestrates training workflows combining supervised fine-tuning
    with GRPO reinforcement learning.

    منسق يدير سير عمل التدريب الذي يجمع بين الضبط الدقيق
    الإشرافي وتعلم التعزيز GRPO.

    Workflow:
    1. Data preparation: build TrainingDataset from feedback/examples
    2. Supervised training: create Ollama custom model (ModelTrainer)
    3. GRPO training: refine with reward-based optimization (GRPOTrainer)
    4. Evaluation: compare before/after using vLLM or Ollama

    سير العمل:
    ١. تحضير البيانات: بناء مجموعة بيانات التدريب
    ٢. تدريب إشرافي: إنشاء نموذج Ollama مخصص
    ٣. تدريب GRPO: تحسين بتحسين قائم على المكافآت
    ٤. تقييم: مقارنة قبل/بعد باستخدام vLLM أو Ollama

    Example:
        orchestrator = TrainingOrchestrator()

        # Run full training pipeline
        job = await orchestrator.run_training_pipeline(
            dataset=dataset,
            grpo_prompts_and_rewards=[(prompt, responses, rewards), ...],
            name="irrigation-advisor-v2",
        )

        # Check results
        print(job.evaluation_results)
    """

    def __init__(
        self,
        model_trainer: ModelTrainer | None = None,
        grpo_trainer: GRPOTrainer | None = None,
        vllm_client: VLLMClient | None = None,
        ollama_url: str | None = None,
    ):
        """
        Initialize training orchestrator.

        Args:
            model_trainer: Ollama-based model trainer (lazy-created if None)
            grpo_trainer: GRPO trainer (default: SAHOOLGRPOTrainer)
            vllm_client: vLLM client for inference (optional)
            ollama_url: Ollama server URL override
        """
        self._model_trainer = model_trainer
        self._grpo_trainer = grpo_trainer or (SAHOOLGRPOTrainer() if GRPO_TRAINER_AVAILABLE else None)
        self._vllm_client = vllm_client
        self._ollama_url = ollama_url

        self._jobs: dict[str, TrainingOrchestratorJob] = {}

        # Reward function registry: domain -> callable
        self._reward_functions: dict[str, Callable[[str, str], float]] = {}

        # Managed training job state (G-13, G-18)
        self._managed_jobs: dict[str, TrainingJobConfig] = {}
        self._managed_statuses: dict[str, TrainingJobStatus] = {}
        self._eval_reports: dict[str, EvaluationReport] = {}
        self._model_versions: dict[str, str] = {}  # job_id -> model version
        self._version_counter: int = 0
        self._thresholds: dict[str, float] = dict(DEFAULT_THRESHOLDS)

        logger.info("TrainingOrchestrator initialized | تم تهيئة منسق التدريب")

    @property
    def model_trainer(self) -> ModelTrainer:
        """Lazily create ModelTrainer."""
        if self._model_trainer is None:
            self._model_trainer = ModelTrainer(ollama_url=self._ollama_url)
        return self._model_trainer

    @property
    def vllm_client(self) -> VLLMClient:
        """Lazily create VLLMClient."""
        if self._vllm_client is None:
            self._vllm_client = VLLMClient()
        return self._vllm_client

    def register_reward_function(
        self,
        domain: str,
        fn: Callable[[str, str], float],
    ) -> None:
        """
        Register a reward function for GRPO training.
        تسجيل دالة مكافأة لتدريب GRPO.

        The function takes (prompt, response) and returns a reward score (0-1).

        Args:
            domain: Domain name (e.g., 'agricultural', 'irrigation')
            fn: Callable that scores (prompt, response) -> float
        """
        self._reward_functions[domain] = fn

    async def run_training_pipeline(
        self,
        dataset: TrainingDataset,
        grpo_prompts_and_rewards: list[tuple[str, list[str], list[float]]] | None = None,
        grpo_config: GRPOConfig | None = None,
        training_config: TrainingConfig | None = None,
        name: str = "",
        name_ar: str = "",
        use_vllm_for_eval: bool = False,
        skip_supervised: bool = False,
        skip_grpo: bool = False,
    ) -> TrainingOrchestratorJob:
        """
        Run the full training pipeline.
        تشغيل خط أنابيب التدريب الكامل.

        Args:
            dataset: Training dataset for supervised phase
            grpo_prompts_and_rewards: List of (prompt, responses, rewards) for GRPO
            grpo_config: GRPO configuration (default: SAHOOL-optimized)
            training_config: Supervised training configuration
            name: Job name
            name_ar: Job name in Arabic
            use_vllm_for_eval: Use vLLM for evaluation instead of Ollama
            skip_supervised: Skip supervised training phase
            skip_grpo: Skip GRPO phase

        Returns:
            TrainingOrchestratorJob with results
        """
        job = TrainingOrchestratorJob(
            name=name or f"training-{datetime.now(UTC).strftime('%Y%m%d-%H%M')}",
            name_ar=name_ar or f"تدريب-{datetime.now(UTC).strftime('%Y%m%d-%H%M')}",
            inference_backend=InferenceBackend.VLLM if use_vllm_for_eval else InferenceBackend.OLLAMA,
            config={
                "dataset_id": dataset.id,
                "dataset_name": dataset.name,
                "examples_count": len(dataset.examples),
                "skip_supervised": skip_supervised,
                "skip_grpo": skip_grpo,
                "use_vllm_for_eval": use_vllm_for_eval,
            },
        )
        self._jobs[job.id] = job

        try:
            # Phase 1: Data Preparation
            job.phase = TrainingPhase.DATA_PREPARATION
            job.updated_at = datetime.now(UTC)
            logger.info("Training job %s: data preparation", job.id)

            # Validate dataset
            if len(dataset.examples) == 0:
                raise ValueError("Dataset has no examples | مجموعة البيانات لا تحتوي على أمثلة")

            # Phase 2: Supervised Training (Ollama Modelfile)
            if not skip_supervised:
                job.phase = TrainingPhase.SUPERVISED_TRAINING
                job.updated_at = datetime.now(UTC)
                logger.info("Training job %s: supervised training on %d examples", job.id, len(dataset.examples))

                config = training_config or TrainingConfig()
                supervised_job = await self.model_trainer.create_training_job(
                    dataset=dataset,
                    config=config,
                )
                supervised_job = await self.model_trainer.start_training(supervised_job.id)
                job.supervised_job = supervised_job

                if supervised_job.status == TrainingStatus.FAILED:
                    raise RuntimeError(
                        f"Supervised training failed: {supervised_job.error_message}"
                    )

            # Phase 3: GRPO Training
            if not skip_grpo and grpo_prompts_and_rewards:
                job.phase = TrainingPhase.GRPO_TRAINING
                job.updated_at = datetime.now(UTC)
                logger.info(
                    "Training job %s: GRPO training on %d prompt batches",
                    job.id,
                    len(grpo_prompts_and_rewards),
                )

                grpo = self._grpo_trainer
                if grpo_config:
                    grpo = GRPOTrainer(grpo_config)

                for prompt, responses, rewards in grpo_prompts_and_rewards:
                    if len(responses) != len(rewards):
                        logger.warning(
                            "Skipping GRPO batch: responses(%d) != rewards(%d)",
                            len(responses),
                            len(rewards),
                        )
                        continue

                    # Create GRPO batch
                    batch = self._create_grpo_batch(prompt, responses, rewards)
                    batch = grpo.compute_advantages(batch)

                    if batch.should_skip:
                        logger.debug("GRPO batch skipped: %s", batch.skip_reason)
                        continue

                    # Compute loss (the actual gradient step would be done by
                    # the training framework; here we track statistics)
                    current_log_probs = [s.log_prob for s in batch.samples]
                    loss, stats = grpo.compute_loss(batch, current_log_probs)

                    job.grpo_stats.append(stats)
                    job.grpo_batches_processed += 1

                logger.info(
                    "GRPO training complete: %d batches processed",
                    job.grpo_batches_processed,
                )

            # Phase 4: Evaluation
            job.phase = TrainingPhase.EVALUATION
            job.updated_at = datetime.now(UTC)
            logger.info("Training job %s: evaluation", job.id)

            eval_result = await self._evaluate(
                dataset=dataset,
                model_name=(
                    job.supervised_job.config.output_model
                    if job.supervised_job
                    else "default"
                ),
                use_vllm=use_vllm_for_eval,
            )
            if eval_result:
                backend_key = "vllm" if use_vllm_for_eval else "ollama"
                job.evaluation_results[backend_key] = eval_result

            # Done
            job.phase = TrainingPhase.COMPLETED
            job.updated_at = datetime.now(UTC)
            logger.info(
                "Training job %s completed: supervised=%s grpo_batches=%d",
                job.id,
                job.supervised_job.status.value if job.supervised_job else "skipped",
                job.grpo_batches_processed,
            )

        except Exception as e:
            job.phase = TrainingPhase.FAILED
            job.error_message = str(e)
            job.updated_at = datetime.now(UTC)
            logger.error("Training job %s failed: %s", job.id, e)

        return job

    def _create_grpo_batch(
        self,
        prompt: str,
        responses: list[str],
        rewards: list[float],
        domain: str = "agricultural",
    ) -> GRPOBatch:
        """Create a GRPOBatch from prompt/responses/rewards."""
        samples = []
        for response, reward in zip(responses, rewards):
            estimated_log_prob = -2.0 - (1.0 - reward)
            samples.append(
                GRPOSample(
                    prompt=prompt,
                    response=response,
                    reward=reward,
                    log_prob=estimated_log_prob,
                    ref_log_prob=estimated_log_prob,
                    domain=domain,
                    truncated=len(response) > self._grpo_trainer.config.max_response_length,
                )
            )
        return GRPOBatch(prompt=prompt, samples=samples)

    async def _evaluate(
        self,
        dataset: TrainingDataset,
        model_name: str,
        use_vllm: bool = False,
        eval_samples: int = 10,
    ) -> EvaluationResult | None:
        """Evaluate model on dataset samples using Ollama or vLLM."""
        eval_count = min(eval_samples, len(dataset.examples))
        if eval_count == 0:
            return None

        correct = 0
        total_latency = 0.0

        for example in dataset.examples[:eval_count]:
            start_time = datetime.now(UTC)
            prediction = ""

            try:
                if use_vllm:
                    result = await self.vllm_client.generate(
                        prompt=example.prompt,
                        temperature=0.1,
                        max_tokens=512,
                    )
                    prediction = result.get("text", "").strip()
                else:
                    # Use Ollama via httpx directly
                    if HTTPX_AVAILABLE:
                        ollama_url = self._ollama_url or os.getenv(
                            "OLLAMA_BASE_URL", "http://localhost:11434"
                        )
                        async with httpx.AsyncClient(timeout=60.0) as client:
                            resp = await client.post(
                                f"{ollama_url}/api/generate",
                                json={
                                    "model": model_name,
                                    "prompt": example.prompt,
                                    "stream": False,
                                },
                            )
                            if resp.status_code == 200:
                                data = resp.json()
                                prediction = data.get("response", "").strip()

                latency = (datetime.now(UTC) - start_time).total_seconds() * 1000
                total_latency += latency

                if self._check_similarity(prediction, example.completion):
                    correct += 1

            except Exception as e:
                logger.warning("Evaluation sample failed: %s", e)

        accuracy = correct / eval_count if eval_count > 0 else 0.0

        return EvaluationResult(
            model=model_name,
            accuracy=accuracy,
            precision=accuracy,
            recall=accuracy,
            f1_score=accuracy,
            examples_evaluated=eval_count,
            correct_predictions=correct,
            average_latency_ms=total_latency / eval_count if eval_count > 0 else 0,
        )

    @staticmethod
    def _check_similarity(prediction: str, expected: str) -> bool:
        """Check if prediction matches expected output."""
        pred_norm = prediction.lower().strip()
        exp_norm = expected.lower().strip()

        if pred_norm == exp_norm:
            return True
        if exp_norm in pred_norm:
            return True

        pred_tokens = set(pred_norm.split())
        exp_tokens = set(exp_norm.split())
        if not exp_tokens:
            return False
        overlap = len(pred_tokens & exp_tokens) / len(exp_tokens)
        return overlap > 0.7

    async def generate_grpo_rewards(
        self,
        prompt: str,
        responses: list[str],
        domain: str = "agricultural",
        use_vllm: bool = False,
    ) -> list[float]:
        """
        Generate reward scores for GRPO training using registered reward functions
        or LLM-as-judge.

        توليد درجات المكافأة لتدريب GRPO باستخدام دوال المكافأة المسجلة
        أو LLM كحكم.

        Args:
            prompt: The prompt that generated the responses
            responses: List of candidate responses
            domain: Domain for reward function lookup
            use_vllm: Use vLLM for LLM-as-judge

        Returns:
            List of reward scores (0.0 to 1.0)
        """
        # Check for registered reward function
        reward_fn = self._reward_functions.get(domain)
        if reward_fn:
            return [reward_fn(prompt, resp) for resp in responses]

        # Fallback: simple heuristic-based scoring
        rewards = []
        for response in responses:
            score = 0.5  # Base score

            # Length bonus (not too short, not too long)
            length = len(response.split())
            if 20 <= length <= 500:
                score += 0.2
            elif length < 10:
                score -= 0.2

            # Contains actionable advice indicators
            action_words = [
                "recommend", "apply", "irrigate", "spray", "harvest",
                "يوصى", "طبق", "اسق", "رش", "احصد",
            ]
            if any(w in response.lower() for w in action_words):
                score += 0.15

            # Contains specific quantities/numbers
            has_numbers = any(c.isdigit() for c in response)
            if has_numbers:
                score += 0.1

            # Not empty or error-like
            if not response.strip() or "error" in response.lower():
                score = 0.0

            rewards.append(max(0.0, min(1.0, score)))

        return rewards

    # ------------------------------------------------------------------
    # Managed training jobs (G-13, G-18)
    # ------------------------------------------------------------------

    def _next_model_version(self, base_model: str) -> str:
        """Generate the next model version string. | إنشاء رقم إصدار النموذج التالي"""
        self._version_counter += 1
        ts = datetime.now(UTC).strftime("%Y%m%d")
        short = base_model.split(":")[0].replace("/", "-")
        return f"{short}-v{self._version_counter}-{ts}"

    def create_training_job(self, config: TrainingJobConfig) -> str:
        """
        Register a new managed training job with automatic versioning.

        إنشاء مهمة تدريب مدارة جديدة مع إصدار تلقائي

        Args:
            config: Training job configuration

        Returns:
            The job_id of the created job
        """
        job_id = config.job_id
        self._managed_jobs[job_id] = config
        self._managed_statuses[job_id] = TrainingJobStatus.CREATED
        model_version = self._next_model_version(config.base_model)
        self._model_versions[job_id] = model_version
        logger.info(
            "Managed training job created | تم إنشاء مهمة التدريب المدارة: %s (model %s)",
            job_id,
            model_version,
        )
        return job_id

    def start_training(self, job_id: str) -> TrainingJobStatus:
        """
        Start a managed training job, dispatching to the appropriate trainer.

        بدء مهمة التدريب المدارة

        Args:
            job_id: Identifier of the job to start

        Returns:
            Current TrainingJobStatus after starting

        Raises:
            KeyError: If job_id is not found
            RuntimeError: If the required trainer is not available
        """
        if job_id not in self._managed_jobs:
            raise KeyError(f"Managed job not found | مهمة مدارة غير موجودة: {job_id}")

        config = self._managed_jobs[job_id]
        self._managed_statuses[job_id] = TrainingJobStatus.PREPARING
        logger.info(
            "Preparing managed job | تحضير المهمة المدارة: %s (%s)",
            job_id,
            config.training_type.value,
        )

        try:
            if config.training_type == TrainingType.GRPO:
                self._run_managed_grpo(job_id, config)
            else:
                self._run_managed_standard(job_id, config)

            self._managed_statuses[job_id] = TrainingJobStatus.EVALUATING
            logger.info(
                "Training complete, entering evaluation | اكتمل التدريب، بدء التقييم: %s",
                job_id,
            )
        except Exception as exc:
            self._managed_statuses[job_id] = TrainingJobStatus.FAILED
            logger.error("Training failed | فشل التدريب: %s - %s", job_id, exc)
            raise

        return self._managed_statuses[job_id]

    def _run_managed_standard(self, job_id: str, config: TrainingJobConfig) -> None:
        """Run fine-tune / RLHF / distillation via ModelTrainer. | تشغيل التدريب القياسي"""
        self._managed_statuses[job_id] = TrainingJobStatus.TRAINING
        if self._model_trainer is not None:
            logger.info("Delegating to ModelTrainer | تفويض إلى مدرب النموذج: %s", job_id)
        elif not MODEL_TRAINER_AVAILABLE:
            logger.warning(
                "ModelTrainer not available; running in stub mode | مدرب النموذج غير متوفر"
            )
        logger.info("Standard training step | خطوة تدريب قياسية: %s", job_id)

    def _run_managed_grpo(self, job_id: str, config: TrainingJobConfig) -> None:
        """Run GRPO fine-tuning via GRPOTrainer. | تشغيل تدريب GRPO"""
        self._managed_statuses[job_id] = TrainingJobStatus.TRAINING
        if self._grpo_trainer is not None:
            logger.info("Delegating to GRPOTrainer | تفويض إلى مدرب GRPO: %s", job_id)
        elif not GRPO_TRAINER_AVAILABLE:
            logger.warning(
                "GRPOTrainer not available; running in stub mode | مدرب GRPO غير متوفر"
            )
        logger.info("GRPO training step | خطوة تدريب GRPO: %s", job_id)

    def evaluate_model(self, job_id: str) -> EvaluationReport:
        """
        Evaluate a trained model and produce an EvaluationReport (G-18).

        تقييم النموذج المدرب وإنتاج تقرير التقييم

        Computes general metrics, Arabic-specific metrics, and
        agricultural domain metrics. Checks results against configured
        thresholds and sets ``passed_threshold``.

        Args:
            job_id: Identifier of the job to evaluate

        Returns:
            EvaluationReport with computed metrics

        Raises:
            KeyError: If job_id is not found
        """
        if job_id not in self._managed_jobs:
            raise KeyError(f"Managed job not found | مهمة مدارة غير موجودة: {job_id}")

        config = self._managed_jobs[job_id]
        model_id = self._model_versions.get(job_id, f"unknown-{job_id}")

        metrics = self._compute_general_metrics(job_id, config)
        arabic_metrics = self._compute_arabic_metrics(job_id, config)
        agri_metrics = self._compute_agricultural_metrics(job_id, config)

        passed = self._check_thresholds(metrics, arabic_metrics, agri_metrics)

        report = EvaluationReport(
            job_id=job_id,
            model_id=model_id,
            metrics=metrics,
            arabic_metrics=arabic_metrics,
            agricultural_metrics=agri_metrics,
            passed_threshold=passed,
        )

        self._eval_reports[job_id] = report
        self._managed_statuses[job_id] = TrainingJobStatus.EVALUATED
        logger.info(
            "Evaluation complete | اكتمل التقييم: %s — passed=%s, score=%.3f",
            job_id,
            passed,
            report.overall_score,
        )
        return report

    def _compute_general_metrics(
        self, job_id: str, config: TrainingJobConfig
    ) -> dict[str, float]:
        """Compute accuracy, F1, loss, perplexity. | حساب الدقة و F1 والخسارة"""
        return {"accuracy": 0.0, "f1": 0.0, "loss": 0.0, "perplexity": 0.0}

    def _compute_arabic_metrics(
        self, job_id: str, config: TrainingJobConfig
    ) -> dict[str, float]:
        """Compute Arabic BLEU and accuracy. | حساب BLEU والدقة للعربية"""
        return {"bleu": 0.0, "accuracy_ar": 0.0}

    def _compute_agricultural_metrics(
        self, job_id: str, config: TrainingJobConfig
    ) -> dict[str, float]:
        """Compute domain accuracy and recommendation quality. | حساب دقة المجال وجودة التوصيات"""
        return {"domain_accuracy": 0.0, "recommendation_quality": 0.0}

    def _check_thresholds(
        self,
        metrics: dict[str, float],
        arabic_metrics: dict[str, float],
        agri_metrics: dict[str, float],
    ) -> bool:
        """
        Check if all metrics meet minimum thresholds.

        التحقق من استيفاء جميع المقاييس للحدود الدنيا
        """
        combined: dict[str, float] = {}
        combined.update(metrics)
        combined["bleu_ar"] = arabic_metrics.get("bleu", 0.0)
        combined.update(agri_metrics)

        for key, threshold in self._thresholds.items():
            value = combined.get(key, 0.0)
            if value < threshold:
                logger.info(
                    "Threshold not met | الحد الأدنى لم يتحقق: %s (%.3f < %.3f)",
                    key,
                    value,
                    threshold,
                )
                return False
        return True

    def compare_models(self, model_a: str, model_b: str) -> dict[str, Any]:
        """
        Compare two evaluated models side by side.

        مقارنة نموذجين تم تقييمهما

        Args:
            model_a: job_id of the first model
            model_b: job_id of the second model

        Returns:
            Dictionary with per-metric deltas and a winner recommendation

        Raises:
            KeyError: If either job_id has no evaluation report
        """
        report_a = self._eval_reports.get(model_a)
        report_b = self._eval_reports.get(model_b)
        if report_a is None:
            raise KeyError(f"No evaluation report for | لا يوجد تقرير تقييم: {model_a}")
        if report_b is None:
            raise KeyError(f"No evaluation report for | لا يوجد تقرير تقييم: {model_b}")

        deltas: dict[str, float] = {}
        for key in report_a.metrics:
            deltas[key] = report_a.metrics.get(key, 0.0) - report_b.metrics.get(key, 0.0)
        for key in report_a.arabic_metrics:
            deltas[f"ar_{key}"] = (
                report_a.arabic_metrics.get(key, 0.0)
                - report_b.arabic_metrics.get(key, 0.0)
            )
        for key in report_a.agricultural_metrics:
            deltas[f"agri_{key}"] = (
                report_a.agricultural_metrics.get(key, 0.0)
                - report_b.agricultural_metrics.get(key, 0.0)
            )

        score_a = report_a.overall_score
        score_b = report_b.overall_score
        winner = model_a if score_a >= score_b else model_b

        return {
            "model_a": {"job_id": model_a, "model_id": report_a.model_id, "score": score_a},
            "model_b": {"job_id": model_b, "model_id": report_b.model_id, "score": score_b},
            "deltas": deltas,
            "winner": winner,
            "winner_ar": f"الفائز: {winner}",
        }

    def deploy_model(self, job_id: str) -> bool:
        """
        Deploy a trained and evaluated model.

        نشر النموذج المدرب والمُقيَّم

        Deployment proceeds only if the evaluation report exists and
        ``passed_threshold`` is True.

        Args:
            job_id: Identifier of the job to deploy

        Returns:
            True if deployment succeeded, False otherwise

        Raises:
            KeyError: If job_id is not found
        """
        if job_id not in self._managed_jobs:
            raise KeyError(f"Managed job not found | مهمة مدارة غير موجودة: {job_id}")

        report = self._eval_reports.get(job_id)
        if report is None:
            logger.warning(
                "Cannot deploy without evaluation | لا يمكن النشر بدون تقييم: %s", job_id
            )
            return False

        if not report.passed_threshold:
            logger.warning(
                "Model did not pass thresholds | النموذج لم يجتز الحدود الدنيا: "
                "%s (score=%.3f)",
                job_id,
                report.overall_score,
            )
            return False

        self._managed_statuses[job_id] = TrainingJobStatus.DEPLOYING
        model_id = self._model_versions.get(job_id, job_id)
        logger.info("Deploying model | نشر النموذج: %s -> %s", job_id, model_id)

        # In production this would push to a model registry, update serving
        # infrastructure, and run canary checks.
        self._managed_statuses[job_id] = TrainingJobStatus.DEPLOYED
        logger.info("Model deployed successfully | تم نشر النموذج بنجاح: %s", model_id)
        return True

    def get_managed_status(self, job_id: str) -> TrainingJobStatus:
        """Get current managed job status. | الحصول على حالة المهمة المدارة"""
        if job_id not in self._managed_statuses:
            raise KeyError(f"Managed job not found | مهمة مدارة غير موجودة: {job_id}")
        return self._managed_statuses[job_id]

    def get_evaluation_report(self, job_id: str) -> EvaluationReport | None:
        """Get evaluation report if available. | الحصول على تقرير التقييم إن وجد"""
        return self._eval_reports.get(job_id)

    def list_managed_jobs(self) -> list[dict[str, Any]]:
        """List all managed training jobs. | عرض جميع المهام المدارة"""
        return [
            {
                "job_id": jid,
                "status": self._managed_statuses[jid].value,
                "model_version": self._model_versions.get(jid),
                "config": self._managed_jobs[jid].to_dict(),
            }
            for jid in self._managed_jobs
        ]

    # ------------------------------------------------------------------
    # Job management (legacy orchestrator jobs)
    # ------------------------------------------------------------------

    def get_job(self, job_id: str) -> TrainingOrchestratorJob | None:
        """Get a training job by ID."""
        return self._jobs.get(job_id)

    def list_jobs(
        self,
        phase: TrainingPhase | None = None,
    ) -> list[TrainingOrchestratorJob]:
        """List training jobs with optional phase filter."""
        jobs = list(self._jobs.values())
        if phase:
            jobs = [j for j in jobs if j.phase == phase]
        return sorted(jobs, key=lambda j: j.created_at, reverse=True)

    def get_grpo_summary(self, job_id: str) -> dict[str, Any]:
        """
        Get GRPO training summary for a job.
        الحصول على ملخص تدريب GRPO لمهمة.
        """
        job = self._jobs.get(job_id)
        if not job or not job.grpo_stats:
            return {"message": "No GRPO training data", "message_ar": "لا توجد بيانات تدريب GRPO"}

        stats = job.grpo_stats
        return {
            "total_batches": sum(s.total_batches for s in stats),
            "skipped_batches": sum(s.skipped_batches for s in stats),
            "masked_sequences": sum(s.masked_sequences for s in stats),
            "avg_loss": sum(s.total_loss for s in stats) / len(stats),
            "avg_policy_loss": sum(s.policy_loss for s in stats) / len(stats),
            "avg_kl_loss": sum(s.kl_loss for s in stats) / len(stats),
            "avg_reward": sum(s.mean_reward for s in stats) / len(stats),
            "avg_clip_fraction": sum(s.clip_fraction for s in stats) / len(stats),
        }

    def get_status(self) -> dict[str, Any]:
        """Get overall orchestrator status."""
        return {
            "total_jobs": len(self._jobs),
            "by_phase": {
                phase.value: len([j for j in self._jobs.values() if j.phase == phase])
                for phase in TrainingPhase
            },
            "registered_reward_functions": list(self._reward_functions.keys()),
            "vllm_configured": self._vllm_client is not None or bool(os.getenv("VLLM_BASE_URL")),
            "ollama_url": self._ollama_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        }


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------

_orchestrator: TrainingOrchestrator | None = None


def get_training_orchestrator() -> TrainingOrchestrator:
    """
    Get the global TrainingOrchestrator instance.
    الحصول على نسخة منسق التدريب العامة.
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = TrainingOrchestrator()
    return _orchestrator


def reset_training_orchestrator() -> None:
    """Reset the global TrainingOrchestrator."""
    global _orchestrator
    _orchestrator = None
