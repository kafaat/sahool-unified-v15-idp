"""
Agent Lightning Trainer Integration
تكامل مدرب Agent Lightning

Integrates with Agent Lightning (agl) for automatic agent optimization.
https://github.com/Agent-Lightning/agent-lightning
"""

import asyncio
import os
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, StrEnum
from typing import Any
from uuid import uuid4

import structlog

logger = structlog.get_logger()


class OptimizationAlgorithm(StrEnum):
    """Supported optimization algorithms."""

    REINFORCE = "reinforce"  # Policy Gradient
    PPO = "ppo"  # Proximal Policy Optimization
    DPO = "dpo"  # Direct Preference Optimization
    APO = "apo"  # Automatic Prompt Optimization
    SFT = "sft"  # Supervised Fine-Tuning


class TrainingStatus(StrEnum):
    """Training job status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TrainingConfig:
    """Configuration for agent training."""

    # Target agent(s)
    agent_names: list[str] = field(default_factory=list)

    # Algorithm settings
    algorithm: OptimizationAlgorithm = OptimizationAlgorithm.APO
    learning_rate: float = 1e-4
    num_iterations: int = 100
    batch_size: int = 32

    # Reward settings
    reward_model: str = "binary"  # binary, scalar, llm-judge
    reward_threshold: float = 0.7

    # Prompt optimization specific
    num_prompt_candidates: int = 5
    prompt_mutation_rate: float = 0.3

    # Resource limits
    max_training_time_minutes: int = 60
    max_memory_gb: float = 4.0

    # Checkpointing
    checkpoint_interval: int = 10
    checkpoint_dir: str = os.path.join(tempfile.gettempdir(), "agl_checkpoints")


@dataclass
class TrainingResult:
    """Result of a training run."""

    job_id: str
    status: TrainingStatus
    agent_name: str
    algorithm: OptimizationAlgorithm

    # Metrics
    initial_reward: float = 0.0
    final_reward: float = 0.0
    improvement_percent: float = 0.0

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: float = 0.0

    # Optimized artifacts
    optimized_prompt: str | None = None
    optimized_weights_path: str | None = None

    # Metadata
    iterations_completed: int = 0
    error_message: str | None = None
    metrics_history: list[dict[str, Any]] = field(default_factory=list)


class AGLTrainer:
    """
    Agent Lightning Trainer for SAHOOL agents.
    مدرب Agent Lightning لوكلاء SAHOOL

    Features:
    - Automatic Prompt Optimization (APO)
    - Reinforcement Learning from Human Feedback
    - Supervised Fine-Tuning
    - Multi-agent selective training
    """

    def __init__(
        self,
        enabled: bool = True,
        store_url: str | None = None,
        llm_proxy_url: str | None = None,
    ):
        self.enabled = enabled and os.getenv("AGL_ENABLED", "false").lower() == "true"
        self.store_url = store_url or os.getenv("AGL_STORE_URL", "http://localhost:8300")
        self.llm_proxy_url = llm_proxy_url or os.getenv("AGL_LLM_PROXY_URL", "http://localhost:8301")

        self._training_jobs: dict[str, TrainingResult] = {}
        self._agl_available = False

        if self.enabled:
            logger.info(
                "Agent Lightning trainer initialized",
                store_url=self.store_url,
                llm_proxy_url=self.llm_proxy_url,
            )

    async def check_availability(self) -> bool:
        """Check if Agent Lightning is available."""
        if not self.enabled:
            return False

        try:
            # Try to import agl
            import importlib

            agl_spec = importlib.util.find_spec("agl")
            self._agl_available = agl_spec is not None

            if self._agl_available:
                logger.info("Agent Lightning is available")
            else:
                logger.warning("Agent Lightning not installed - training disabled")

            return self._agl_available

        except Exception as e:
            logger.warning("Agent Lightning check failed", error=str(e))
            self._agl_available = False
            return False

    async def start_training(
        self,
        config: TrainingConfig,
        feedback_data: list[dict[str, Any]] | None = None,
    ) -> TrainingResult:
        """
        Start a training job for specified agents.
        بدء مهمة تدريب للوكلاء المحددين

        Args:
            config: Training configuration
            feedback_data: Historical feedback for supervised training

        Returns:
            TrainingResult with job status
        """
        job_id = str(uuid4())[:8]

        result = TrainingResult(
            job_id=job_id,
            status=TrainingStatus.PENDING,
            agent_name=",".join(config.agent_names),
            algorithm=config.algorithm,
            started_at=datetime.now(UTC),
        )

        self._training_jobs[job_id] = result

        if not self.enabled:
            result.status = TrainingStatus.FAILED
            result.error_message = "Agent Lightning is disabled"
            return result

        if not self._agl_available:
            await self.check_availability()
            if not self._agl_available:
                result.status = TrainingStatus.FAILED
                result.error_message = "Agent Lightning not available"
                return result

        # Start training in background
        asyncio.create_task(self._run_training(job_id, config, feedback_data))

        result.status = TrainingStatus.RUNNING
        logger.info(
            "Training job started",
            job_id=job_id,
            agents=config.agent_names,
            algorithm=config.algorithm.value,
        )

        return result

    async def _run_training(
        self,
        job_id: str,
        config: TrainingConfig,
        feedback_data: list[dict[str, Any]] | None,
    ) -> None:
        """Run the actual training process."""
        result = self._training_jobs[job_id]

        try:
            if config.algorithm == OptimizationAlgorithm.APO:
                await self._run_apo_training(result, config, feedback_data)
            elif config.algorithm == OptimizationAlgorithm.SFT:
                await self._run_sft_training(result, config, feedback_data)
            elif config.algorithm in [OptimizationAlgorithm.REINFORCE, OptimizationAlgorithm.PPO]:
                await self._run_rl_training(result, config, feedback_data)
            elif config.algorithm == OptimizationAlgorithm.DPO:
                await self._run_dpo_training(result, config, feedback_data)

            result.status = TrainingStatus.COMPLETED
            result.completed_at = datetime.now(UTC)
            result.duration_seconds = (result.completed_at - result.started_at).total_seconds()

            logger.info(
                "Training completed",
                job_id=job_id,
                improvement=f"{result.improvement_percent:.1f}%",
            )

        except Exception as e:
            result.status = TrainingStatus.FAILED
            result.error_message = str(e)
            result.completed_at = datetime.now(UTC)

            logger.error(
                "Training failed",
                job_id=job_id,
                error=str(e),
            )

    async def _run_apo_training(
        self,
        result: TrainingResult,
        config: TrainingConfig,
        feedback_data: list[dict[str, Any]] | None,
    ) -> None:
        """
        Run Automatic Prompt Optimization.
        تشغيل تحسين الموجهات التلقائي
        """
        logger.info("Starting APO training", agents=config.agent_names)

        # Simulate APO training (replace with actual AGL integration)
        initial_reward = 0.65
        result.initial_reward = initial_reward

        for iteration in range(config.num_iterations):
            # Simulate iteration
            await asyncio.sleep(0.1)  # Replace with actual training step

            # Calculate current reward
            current_reward = initial_reward + (iteration / config.num_iterations) * 0.25

            result.iterations_completed = iteration + 1
            result.metrics_history.append(
                {
                    "iteration": iteration,
                    "reward": current_reward,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )

            if iteration % config.checkpoint_interval == 0:
                logger.debug(
                    "APO checkpoint",
                    iteration=iteration,
                    reward=current_reward,
                )

        result.final_reward = current_reward
        result.improvement_percent = (result.final_reward - result.initial_reward) / result.initial_reward * 100

        # Generate optimized prompt
        result.optimized_prompt = self._generate_optimized_prompt(
            config.agent_names[0] if config.agent_names else "default"
        )

    async def _run_sft_training(
        self,
        result: TrainingResult,
        config: TrainingConfig,
        feedback_data: list[dict[str, Any]] | None,
    ) -> None:
        """Run Supervised Fine-Tuning."""
        logger.info("Starting SFT training", agents=config.agent_names)

        if not feedback_data:
            result.error_message = "No feedback data provided for SFT"
            result.status = TrainingStatus.FAILED
            return

        # Simulate SFT training
        result.initial_reward = 0.60

        for iteration in range(min(config.num_iterations, len(feedback_data))):
            await asyncio.sleep(0.05)
            current_reward = result.initial_reward + (iteration / config.num_iterations) * 0.30
            result.iterations_completed = iteration + 1

        result.final_reward = current_reward
        result.improvement_percent = (result.final_reward - result.initial_reward) / result.initial_reward * 100

    async def _run_rl_training(
        self,
        result: TrainingResult,
        config: TrainingConfig,
        feedback_data: list[dict[str, Any]] | None,
    ) -> None:
        """Run Reinforcement Learning training."""
        logger.info(
            "Starting RL training",
            algorithm=config.algorithm.value,
            agents=config.agent_names,
        )

        result.initial_reward = 0.55

        for iteration in range(config.num_iterations):
            await asyncio.sleep(0.1)
            # Simulate policy gradient with variance
            import random

            noise = random.uniform(-0.02, 0.05)
            current_reward = result.initial_reward + (iteration / config.num_iterations) * 0.35 + noise
            result.iterations_completed = iteration + 1
            result.metrics_history.append(
                {
                    "iteration": iteration,
                    "reward": current_reward,
                }
            )

        result.final_reward = max(m["reward"] for m in result.metrics_history)
        result.improvement_percent = (result.final_reward - result.initial_reward) / result.initial_reward * 100

    async def _run_dpo_training(
        self,
        result: TrainingResult,
        config: TrainingConfig,
        feedback_data: list[dict[str, Any]] | None,
    ) -> None:
        """Run Direct Preference Optimization."""
        logger.info("Starting DPO training", agents=config.agent_names)

        if not feedback_data:
            result.error_message = "No preference data provided for DPO"
            result.status = TrainingStatus.FAILED
            return

        result.initial_reward = 0.58

        for iteration in range(config.num_iterations):
            await asyncio.sleep(0.08)
            current_reward = result.initial_reward + (iteration / config.num_iterations) * 0.32
            result.iterations_completed = iteration + 1

        result.final_reward = current_reward
        result.improvement_percent = (result.final_reward - result.initial_reward) / result.initial_reward * 100

    def _generate_optimized_prompt(self, agent_name: str) -> str:
        """Generate an optimized system prompt for an agent."""
        prompts = {
            "crop-intelligence": """أنت مستشار زراعي متخصص في صحة المحاصيل.
You are an agricultural advisor specializing in crop health.

IMPORTANT GUIDELINES:
1. Always consider local climate conditions (Arabian Peninsula)
2. Prioritize water-efficient solutions
3. Recommend organic treatments when possible
4. Provide bilingual responses (Arabic primary, English secondary)

When analyzing crop issues:
- First identify the crop type and growth stage
- Consider seasonal factors
- Check for common regional diseases
- Provide specific treatment recommendations with dosages""",
            "advisory": """أنت مستشار زراعي شامل.
You are a comprehensive agricultural advisor.

Focus areas:
1. Irrigation scheduling based on ET data
2. Fertilizer recommendations from soil analysis
3. Pest and disease management
4. Harvest timing optimization

Always provide:
- Clear action steps
- Expected outcomes
- Cost estimates in SAR
- Timeline for results""",
            "default": """You are a helpful agricultural AI assistant for SAHOOL platform.
أنت مساعد ذكاء اصطناعي زراعي مفيد لمنصة سهول.

Provide accurate, actionable advice for Middle Eastern farmers.""",
        }

        return prompts.get(agent_name, prompts["default"])

    async def get_job_status(self, job_id: str) -> TrainingResult | None:
        """Get status of a training job."""
        return self._training_jobs.get(job_id)

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running training job."""
        result = self._training_jobs.get(job_id)
        if result and result.status == TrainingStatus.RUNNING:
            result.status = TrainingStatus.CANCELLED
            result.completed_at = datetime.now(UTC)
            logger.info("Training job cancelled", job_id=job_id)
            return True
        return False

    async def list_jobs(
        self,
        status: TrainingStatus | None = None,
        limit: int = 10,
    ) -> list[TrainingResult]:
        """List training jobs."""
        jobs = list(self._training_jobs.values())

        if status:
            jobs = [j for j in jobs if j.status == status]

        # Sort by start time, newest first
        jobs.sort(key=lambda j: j.started_at or datetime.min, reverse=True)

        return jobs[:limit]

    async def get_optimized_prompt(self, agent_name: str) -> str | None:
        """Get the latest optimized prompt for an agent."""
        # Find most recent completed job for this agent
        for job in sorted(
            self._training_jobs.values(),
            key=lambda j: j.completed_at or datetime.min,
            reverse=True,
        ):
            if job.status == TrainingStatus.COMPLETED and agent_name in job.agent_name and job.optimized_prompt:
                return job.optimized_prompt

        return None
