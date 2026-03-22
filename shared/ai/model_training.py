"""
Model Training Module
=====================
وحدة تدريب النماذج

Provides model configuration registration and evaluation capabilities
for local LLMs using Ollama and custom datasets.

IMPORTANT: Ollama's /api/create endpoint registers model configurations
(system prompts, templates, parameters) but does NOT perform actual
fine-tuning or weight updates. The "training" in this module creates a
derived Ollama model with an optimized system prompt built from the
provided dataset. For real fine-tuning, use external infrastructure
(torchtune, axolotl, or a dedicated training cluster).

Features:
    - Custom dataset creation from code examples
    - Model configuration via Ollama Modelfiles (system prompt, parameters)
    - Configuration-based evaluation and benchmarking
    - Progress tracking
    - Bilingual (Arabic/English) support

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Callable

import logging

logger = logging.getLogger(__name__)

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class TrainingStatus(StrEnum):
    """Status of a training job."""

    PENDING = "pending"
    PREPARING = "preparing"
    TRAINING = "training"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    CONFIGURED = "configured"  # Model configuration registered (no real fine-tuning)
    FAILED = "failed"
    CANCELLED = "cancelled"


class DatasetType(StrEnum):
    """Type of training dataset."""

    CODE_FIX = "code_fix"  # Error -> Fix pairs
    CODE_REVIEW = "code_review"  # Code -> Review pairs
    CODE_GENERATION = "code_generation"  # Prompt -> Code pairs
    TEST_GENERATION = "test_generation"  # Code -> Tests pairs
    AGRICULTURAL = "agricultural"  # SAHOOL-specific advisory


@dataclass
class TrainingExample:
    """A single training example."""

    id: str
    prompt: str
    completion: str
    language: str = "python"
    category: str = "general"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "completion": self.completion,
            "language": self.language,
            "category": self.category,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    def to_jsonl(self) -> str:
        """Convert to JSONL format for training."""
        return json.dumps(
            {
                "prompt": self.prompt,
                "completion": self.completion,
            },
            ensure_ascii=False,
        )


@dataclass
class TrainingDataset:
    """A training dataset."""

    id: str
    name: str
    name_ar: str
    description: str
    description_ar: str
    dataset_type: DatasetType
    examples: list[TrainingExample] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def add_example(self, example: TrainingExample) -> None:
        """Add an example to the dataset."""
        self.examples.append(example)
        self.updated_at = datetime.now(UTC)

    def to_jsonl(self) -> str:
        """Export dataset to JSONL format."""
        return "\n".join(ex.to_jsonl() for ex in self.examples)

    def save(self, path: str) -> None:
        """Save dataset to file."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_jsonl())

    @classmethod
    def load(cls, path: str, dataset_id: str | None = None) -> TrainingDataset:
        """Load dataset from JSONL file."""
        examples = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    examples.append(
                        TrainingExample(
                            id=str(uuid.uuid4()),
                            prompt=data["prompt"],
                            completion=data["completion"],
                        )
                    )

        return cls(
            id=dataset_id or str(uuid.uuid4()),
            name=Path(path).stem,
            name_ar=Path(path).stem,
            description=f"Loaded from {path}",
            description_ar=f"محمل من {path}",
            dataset_type=DatasetType.CODE_FIX,
            examples=examples,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "dataset_type": self.dataset_type.value,
            "examples_count": len(self.examples),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class TrainingConfig:
    """Configuration for model training."""

    base_model: str = "codellama:7b"
    output_model: str = "sahool-codefix:latest"
    epochs: int = 3
    batch_size: int = 4
    learning_rate: float = 1e-5
    warmup_steps: int = 100
    max_steps: int | None = None
    eval_steps: int = 100
    save_steps: int = 500
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "base_model": self.base_model,
            "output_model": self.output_model,
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "learning_rate": self.learning_rate,
            "warmup_steps": self.warmup_steps,
            "max_steps": self.max_steps,
            "eval_steps": self.eval_steps,
            "save_steps": self.save_steps,
            "lora_rank": self.lora_rank,
            "lora_alpha": self.lora_alpha,
            "lora_dropout": self.lora_dropout,
        }


@dataclass
class EvaluationResult:
    """Result from model evaluation.

    NOTE: When produced by ModelTrainer, these metrics are configuration-based
    (system prompt + parameters via Ollama /api/create), NOT from actual
    fine-tuning. Accuracy is estimated via string similarity against dataset
    examples and should not be interpreted as true ML training metrics.
    """

    model: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    examples_evaluated: int
    correct_predictions: int
    average_latency_ms: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model": self.model,
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "examples_evaluated": self.examples_evaluated,
            "correct_predictions": self.correct_predictions,
            "average_latency_ms": self.average_latency_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class TrainingJob:
    """A training job."""

    id: str
    dataset_id: str
    config: TrainingConfig
    status: TrainingStatus = TrainingStatus.PENDING
    progress: float = 0.0
    current_step: int = 0
    total_steps: int = 0
    loss: float | None = None
    evaluation_result: EvaluationResult | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "dataset_id": self.dataset_id,
            "config": self.config.to_dict(),
            "status": self.status.value,
            "progress": self.progress,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "loss": self.loss,
            "evaluation_result": self.evaluation_result.to_dict() if self.evaluation_result else None,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat(),
        }


class DatasetBuilder:
    """
    Builder for creating training datasets.

    منشئ مجموعات البيانات للتدريب

    Example:
        builder = DatasetBuilder()

        # Add code fix examples
        builder.add_code_fix_example(
            original="x= 1",
            fixed="x = 1",
            error_message="E225 missing whitespace around operator"
        )

        dataset = builder.build("code-fixes", "إصلاحات الكود")
    """

    def __init__(self):
        """Initialize DatasetBuilder."""
        self._examples: list[TrainingExample] = []
        self._dataset_type: DatasetType = DatasetType.CODE_FIX

    def add_code_fix_example(
        self,
        original: str,
        fixed: str,
        error_message: str,
        language: str = "python",
        rule_id: str | None = None,
    ) -> DatasetBuilder:
        """
        Add a code fix example.

        إضافة مثال إصلاح كود

        Args:
            original: Original code with error
            fixed: Fixed code
            error_message: Error message describing the issue
            language: Programming language
            rule_id: Optional rule ID (e.g., F401)

        Returns:
            Self for chaining
        """
        prompt = f"""Fix the following {language} code that has this error:
Error: {error_message}

Code:
```{language}
{original}
```

Return only the fixed code:"""

        self._examples.append(
            TrainingExample(
                id=str(uuid.uuid4()),
                prompt=prompt,
                completion=fixed,
                language=language,
                category="code_fix",
                metadata={"rule_id": rule_id, "error_message": error_message},
            )
        )

        return self

    def add_code_review_example(
        self,
        code: str,
        review: str,
        language: str = "python",
    ) -> DatasetBuilder:
        """
        Add a code review example.

        إضافة مثال مراجعة كود

        Args:
            code: Code to review
            review: Review comments
            language: Programming language

        Returns:
            Self for chaining
        """
        prompt = f"""Review this {language} code and provide feedback on bugs, security issues, and improvements:

```{language}
{code}
```

Provide your review:"""

        self._examples.append(
            TrainingExample(
                id=str(uuid.uuid4()),
                prompt=prompt,
                completion=review,
                language=language,
                category="code_review",
            )
        )
        self._dataset_type = DatasetType.CODE_REVIEW

        return self

    def add_test_generation_example(
        self,
        code: str,
        tests: str,
        language: str = "python",
        framework: str = "pytest",
    ) -> DatasetBuilder:
        """
        Add a test generation example.

        إضافة مثال توليد اختبارات

        Args:
            code: Code to test
            tests: Generated test code
            language: Programming language
            framework: Test framework

        Returns:
            Self for chaining
        """
        prompt = f"""Generate {framework} tests for this {language} code:

```{language}
{code}
```

Return the test code:"""

        self._examples.append(
            TrainingExample(
                id=str(uuid.uuid4()),
                prompt=prompt,
                completion=tests,
                language=language,
                category="test_generation",
                metadata={"framework": framework},
            )
        )
        self._dataset_type = DatasetType.TEST_GENERATION

        return self

    def add_agricultural_advisory_example(
        self,
        query: str,
        response: str,
        crop_type: str | None = None,
        language_code: str = "en",
    ) -> DatasetBuilder:
        """
        Add an agricultural advisory example.

        إضافة مثال استشارة زراعية

        Args:
            query: Farmer's question
            response: Expert advisory response
            crop_type: Type of crop
            language_code: Language code (en/ar)

        Returns:
            Self for chaining
        """
        context = f"Crop: {crop_type}" if crop_type else "General"

        prompt = f"""You are an agricultural advisor for SAHOOL platform.
Context: {context}

Farmer's Question: {query}

Provide expert advice:"""

        self._examples.append(
            TrainingExample(
                id=str(uuid.uuid4()),
                prompt=prompt,
                completion=response,
                language=language_code,
                category="agricultural",
                metadata={"crop_type": crop_type},
            )
        )
        self._dataset_type = DatasetType.AGRICULTURAL

        return self

    def from_diagnostic_reports(
        self,
        reports_dir: str,
    ) -> DatasetBuilder:
        """
        Build dataset from diagnostic report files.

        بناء مجموعة بيانات من ملفات تقارير التشخيص

        Args:
            reports_dir: Directory containing report JSON files

        Returns:
            Self for chaining
        """
        reports_path = Path(reports_dir)

        for report_file in reports_path.glob("*.json"):
            try:
                with open(report_file, encoding="utf-8") as f:
                    report = json.load(f)

                for diagnostic in report.get("diagnostics", []):
                    if diagnostic.get("suggestion") and diagnostic.get("source_code"):
                        self.add_code_fix_example(
                            original=diagnostic["source_code"],
                            fixed=diagnostic["suggestion"],
                            error_message=diagnostic["message"],
                            rule_id=diagnostic.get("rule_id"),
                        )
            except (json.JSONDecodeError, KeyError):
                continue

        return self

    def build(
        self,
        name: str,
        name_ar: str,
        description: str = "",
        description_ar: str = "",
    ) -> TrainingDataset:
        """
        Build the training dataset.

        بناء مجموعة بيانات التدريب

        Args:
            name: Dataset name
            name_ar: Arabic dataset name
            description: Dataset description
            description_ar: Arabic description

        Returns:
            TrainingDataset
        """
        return TrainingDataset(
            id=str(uuid.uuid4()),
            name=name,
            name_ar=name_ar,
            description=description or f"Training dataset with {len(self._examples)} examples",
            description_ar=description_ar or f"مجموعة بيانات تدريب بـ {len(self._examples)} مثال",
            dataset_type=self._dataset_type,
            examples=self._examples,
        )


class ModelTrainer:
    """
    Model configuration manager using Ollama.

    مدير تكوين النماذج باستخدام Ollama

    IMPORTANT: This class does NOT perform real fine-tuning or weight updates.
    Ollama's /api/create endpoint only registers model configurations (system
    prompts, templates, parameters). The resulting model is the base model with
    a custom system prompt derived from the dataset.

    For actual fine-tuning, use external training infrastructure such as
    torchtune, axolotl, or a dedicated training cluster.

    Example:
        trainer = ModelTrainer()

        # Create and start a configuration job (NOT real training)
        job = await trainer.create_training_job(
            dataset=dataset,
            config=TrainingConfig(base_model="codellama:7b")
        )

        # Job will complete with status CONFIGURED (not COMPLETED)
        job = await trainer.start_training(job.id)
        assert job.status == TrainingStatus.CONFIGURED
    """

    def __init__(
        self,
        ollama_url: str | None = None,
        models_dir: str | None = None,
    ):
        """
        Initialize ModelTrainer.

        Args:
            ollama_url: Ollama server URL
            models_dir: Directory for custom models
        """
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx is required. Install with: pip install httpx")

        self.ollama_url = ollama_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.models_dir = models_dir or os.path.expanduser("~/.ollama/models")
        self._jobs: dict[str, TrainingJob] = {}
        self._datasets: dict[str, TrainingDataset] = {}
        self._progress_callbacks: dict[str, Callable[[TrainingJob], None]] = {}

    async def create_training_job(
        self,
        dataset: TrainingDataset,
        config: TrainingConfig | None = None,
        progress_callback: Callable[[TrainingJob], None] | None = None,
    ) -> TrainingJob:
        """
        Create a new training job.

        إنشاء مهمة تدريب جديدة

        Args:
            dataset: Training dataset
            config: Training configuration
            progress_callback: Optional callback for progress updates

        Returns:
            TrainingJob
        """
        config = config or TrainingConfig()

        job = TrainingJob(
            id=str(uuid.uuid4()),
            dataset_id=dataset.id,
            config=config,
            total_steps=len(dataset.examples) * config.epochs // config.batch_size,
        )

        self._jobs[job.id] = job
        self._datasets[dataset.id] = dataset

        if progress_callback:
            self._progress_callbacks[job.id] = progress_callback

        return job

    async def start_training(self, job_id: str) -> TrainingJob:
        """
        Start a training job.

        بدء مهمة التدريب

        Args:
            job_id: Job ID

        Returns:
            Updated TrainingJob
        """
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")

        job.status = TrainingStatus.PREPARING
        job.started_at = datetime.now(UTC)
        self._notify_progress(job)

        try:
            # Get dataset
            dataset = self._datasets.get(job.dataset_id)
            if not dataset:
                raise ValueError(f"Dataset not found: {job.dataset_id}")

            # Create Modelfile for training
            modelfile_content = self._create_modelfile(job.config, dataset)

            # Create custom model using Ollama
            job.status = TrainingStatus.TRAINING
            self._notify_progress(job)

            await self._train_model(job, modelfile_content)

            # Evaluate model (configuration-based, not training-based)
            job.status = TrainingStatus.EVALUATING
            self._notify_progress(job)

            eval_result = await self._evaluate_model(job.config.output_model, dataset)
            job.evaluation_result = eval_result

            # Mark as configured (not trained) - Ollama /api/create only registers
            # system prompts and parameters, no actual weight updates occur.
            job.status = TrainingStatus.CONFIGURED
            job.progress = 100.0
            job.completed_at = datetime.now(UTC)
            self._notify_progress(job)

            logger.info(
                "Model '%s' configured (not fine-tuned) from base '%s'. "
                "Configuration-based evaluation accuracy: %.2f",
                job.config.output_model,
                job.config.base_model,
                eval_result.accuracy,
            )

        except Exception as e:
            job.status = TrainingStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now(UTC)
            self._notify_progress(job)
            raise

        return job

    def _create_modelfile(
        self,
        config: TrainingConfig,
        dataset: TrainingDataset,
    ) -> str:
        """Create Ollama Modelfile content."""
        # Build system prompt from dataset
        system_prompt = self._build_system_prompt(dataset)

        # Create Modelfile
        modelfile = f"""FROM {config.base_model}

# System prompt optimized for {dataset.dataset_type.value}
SYSTEM \"\"\"
{system_prompt}
\"\"\"

# Training parameters
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
PARAMETER stop "<|endoftext|>"

# License
LICENSE \"\"\"
SAHOOL Platform - Proprietary
\"\"\"
"""
        return modelfile

    def _build_system_prompt(self, dataset: TrainingDataset) -> str:
        """Build optimized system prompt from dataset."""
        if dataset.dataset_type == DatasetType.CODE_FIX:
            return """You are an expert code fixer for the SAHOOL platform.
Your task is to fix code issues identified by linters like Ruff, ESLint, Mypy, and Bandit.
Always return only the fixed code without explanations.
Preserve the original code structure and style.
Fix only the identified issues, don't add unnecessary changes."""

        elif dataset.dataset_type == DatasetType.CODE_REVIEW:
            return """You are an expert code reviewer for the SAHOOL platform.
Review code for: bugs, security vulnerabilities, performance issues, and style.
Provide clear, actionable feedback in a structured format.
Focus on important issues first."""

        elif dataset.dataset_type == DatasetType.TEST_GENERATION:
            return """You are an expert test generator for the SAHOOL platform.
Generate comprehensive unit tests that cover:
- Normal cases
- Edge cases
- Error handling
Use pytest for Python and Vitest for TypeScript."""

        elif dataset.dataset_type == DatasetType.AGRICULTURAL:
            return """You are an agricultural expert advisor for the SAHOOL platform.
أنت مستشار زراعي خبير لمنصة سهول.
Provide accurate, actionable advice for farmers in the Middle East.
قدم نصائح دقيقة وقابلة للتنفيذ للمزارعين.
Consider local climate, soil conditions, and available resources."""

        return "You are an AI assistant for the SAHOOL agricultural platform."

    async def _train_model(
        self,
        job: TrainingJob,
        modelfile_content: str,
    ) -> None:
        """Register model configuration using Ollama create API.

        NOTE: Ollama's /api/create registers model configurations (system prompts,
        templates) but does NOT perform actual fine-tuning/weight updates.
        Real fine-tuning requires external training infrastructure (e.g., torchtune,
        axolotl, or a dedicated training cluster).

        This method creates a derived model with a custom system prompt and parameters
        based on the training dataset, but no gradient-based learning occurs.
        """
        logger.warning(
            "Model training requested for job %s, but Ollama /api/create only "
            "registers model configurations (system prompt, parameters). "
            "No actual fine-tuning/weight updates will occur. "
            "For real training, use external infrastructure.",
            job.id,
        )

        async with httpx.AsyncClient(timeout=600.0) as client:
            # Register model configuration via Ollama (not real training)
            response = await client.post(
                f"{self.ollama_url}/api/create",
                json={
                    "name": job.config.output_model,
                    "modelfile": modelfile_content,
                    "stream": False,
                },
            )
            response.raise_for_status()

            # Mark as configured - this is NOT real training, just model registration
            job.current_step = job.total_steps
            job.progress = 100.0
            job.loss = None  # No real loss computed
            self._notify_progress(job)

    async def _evaluate_model(
        self,
        model: str,
        dataset: TrainingDataset,
        eval_samples: int = 10,
    ) -> EvaluationResult:
        """Evaluate configured model on dataset samples.

        NOTE: These metrics reflect the base model's performance with a custom
        system prompt, NOT the result of fine-tuning. Accuracy, precision,
        recall, and F1 are configuration-based estimates using simple string
        similarity, not proper ML evaluation metrics.
        """
        correct = 0
        total_latency = 0.0
        eval_count = min(eval_samples, len(dataset.examples))

        async with httpx.AsyncClient(timeout=60.0) as client:
            for example in dataset.examples[:eval_count]:
                start_time = datetime.now(UTC)

                try:
                    response = await client.post(
                        f"{self.ollama_url}/api/generate",
                        json={
                            "model": model,
                            "prompt": example.prompt,
                            "stream": False,
                        },
                    )

                    latency = (datetime.now(UTC) - start_time).total_seconds() * 1000
                    total_latency += latency

                    if response.status_code == 200:
                        data = response.json()
                        prediction = data.get("response", "").strip()

                        # Simple similarity check
                        if self._check_similarity(prediction, example.completion):
                            correct += 1

                except Exception:
                    # Individual evaluation failures (network, model errors) should not
                    # stop the entire evaluation loop. Failed examples are counted as
                    # incorrect, which is reflected in the accuracy metrics.
                    pass

        accuracy = correct / eval_count if eval_count > 0 else 0

        return EvaluationResult(
            model=model,
            accuracy=accuracy,
            precision=accuracy,  # Simplified
            recall=accuracy,  # Simplified
            f1_score=accuracy,  # Simplified
            examples_evaluated=eval_count,
            correct_predictions=correct,
            average_latency_ms=total_latency / eval_count if eval_count > 0 else 0,
        )

    def _check_similarity(self, prediction: str, expected: str) -> bool:
        """Check if prediction is similar to expected output."""
        # Normalize strings
        pred_normalized = prediction.lower().strip()
        exp_normalized = expected.lower().strip()

        # Exact match
        if pred_normalized == exp_normalized:
            return True

        # Contains check (for code fixes)
        if exp_normalized in pred_normalized:
            return True

        # Basic token overlap
        pred_tokens = set(pred_normalized.split())
        exp_tokens = set(exp_normalized.split())
        overlap = len(pred_tokens & exp_tokens) / len(exp_tokens) if exp_tokens else 0

        return overlap > 0.7

    def _notify_progress(self, job: TrainingJob) -> None:
        """Notify progress callback."""
        callback = self._progress_callbacks.get(job.id)
        if callback:
            callback(job)

    async def get_job_status(self, job_id: str) -> TrainingJob | None:
        """Get training job status."""
        return self._jobs.get(job_id)

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a training job."""
        job = self._jobs.get(job_id)
        if job and job.status in [
            TrainingStatus.PENDING,
            TrainingStatus.PREPARING,
            TrainingStatus.TRAINING,
        ]:
            job.status = TrainingStatus.CANCELLED
            job.completed_at = datetime.now(UTC)
            return True
        return False

    async def list_jobs(self) -> list[TrainingJob]:
        """List all training jobs."""
        return list(self._jobs.values())


# Convenience functions
def create_code_fix_dataset(
    examples: list[tuple[str, str, str]],
    name: str = "code-fixes",
) -> TrainingDataset:
    """
    Create a code fix dataset from examples.

    إنشاء مجموعة بيانات إصلاح الكود

    Args:
        examples: List of (original, fixed, error_message) tuples
        name: Dataset name

    Returns:
        TrainingDataset
    """
    builder = DatasetBuilder()

    for original, fixed, error in examples:
        builder.add_code_fix_example(original, fixed, error)

    return builder.build(name, f"مجموعة {name}")


async def train_code_fixer(
    dataset: TrainingDataset,
    base_model: str = "codellama:7b",
    output_model: str = "sahool-codefix:latest",
) -> TrainingJob:
    """
    Configure a code fixer model via Ollama (NOT real fine-tuning).

    تكوين نموذج إصلاح الكود عبر Ollama (ليس تدريبًا حقيقيًا)

    NOTE: This registers a model configuration with a custom system prompt
    derived from the dataset. No weight updates or gradient-based learning
    occurs. The resulting job will have status CONFIGURED, not COMPLETED.

    Args:
        dataset: Training dataset (used to build the system prompt)
        base_model: Base model to configure on top of
        output_model: Name for the configured model

    Returns:
        TrainingJob with status CONFIGURED
    """
    logger.warning(
        "train_code_fixer() registers a model configuration via Ollama, "
        "not actual fine-tuning. For real training, use external infrastructure."
    )
    trainer = ModelTrainer()

    config = TrainingConfig(
        base_model=base_model,
        output_model=output_model,
    )

    job = await trainer.create_training_job(dataset, config)
    return await trainer.start_training(job.id)
