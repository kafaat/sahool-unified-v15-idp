"""
GRPO Trainer Module
===================
مدرب GRPO - تدريب النماذج بتقنيات DAPO و Dr.GRPO

Advanced reinforcement learning trainer implementing:
- GRPO (Group Relative Policy Optimization)
- DAPO (Decoupled Clip and Dynamic Sampling)
- Dr.GRPO (GRPO Done Right)
- DeepSeek V3.2 improvements

Based on research from:
- DeepSeek-R1 and V3.2
- DAPO by Yu et al., 2025
- Dr. GRPO by Liu et al., 2025

Author: SAHOOL Platform Team
Updated: January 2026
"""

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, StrEnum
from typing import Any

# Type hints for optional dependencies
try:
    import torch
    from torch import Tensor

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    Tensor = Any


class GRPOVariant(StrEnum):
    """GRPO algorithm variant."""

    VANILLA = "vanilla"  # Original GRPO
    DAPO = "dapo"  # DAPO improvements
    DR_GRPO = "dr_grpo"  # GRPO Done Right
    DEEPSEEK = "deepseek"  # DeepSeek V3.2 full improvements


@dataclass
class GRPOConfig:
    """
    GRPO configuration with DAPO/Dr.GRPO/DeepSeek improvements.

    إعدادات GRPO مع تحسينات DAPO و Dr.GRPO و DeepSeek

    Attributes:
        variant: Which GRPO variant to use
        group_size: Number of samples per prompt for advantage computation
        clip_range: PPO clipping range (lower bound)
        clip_higher: DAPO asymmetric upper clip (higher than clip_range)
        kl_coef: KL divergence coefficient (0.0 for Dr.GRPO/DAPO)
        normalize_advantages: Whether to normalize advantages
        normalize_by_std: Whether to divide by std (False for Dr.GRPO)
        dynamic_sampling: DAPO - filter all-correct/all-wrong batches
        token_level_loss: DAPO - weight loss by token count
        overlong_penalty: DAPO - penalty for truncated responses
        reweight_kl: DeepSeek - importance-weighted KL
        off_policy_masking: DeepSeek - mask stale negative samples
        off_policy_threshold: Divergence threshold for masking
        keep_sampling_mask: DeepSeek - preserve top-p/k masks
        domain_kl_weights: Domain-specific KL weights
    """

    # Algorithm variant
    variant: GRPOVariant = GRPOVariant.DEEPSEEK

    # Core GRPO parameters
    group_size: int = 8
    clip_range: float = 0.2
    learning_rate: float = 1e-6
    max_grad_norm: float = 1.0
    entropy_coef: float = 0.01

    # DAPO improvements
    clip_higher: float = 0.28  # Asymmetric upper clip
    dynamic_sampling: bool = True
    token_level_loss: bool = True
    overlong_penalty: float = 0.1
    max_response_length: int = 4096

    # Dr.GRPO fixes
    kl_coef: float = 0.0  # No KL loss by default
    normalize_advantages: bool = True
    normalize_by_std: bool = False  # Don't divide by std

    # DeepSeek V3.2 improvements
    reweight_kl: bool = True
    off_policy_masking: bool = True
    off_policy_threshold: float = 0.5
    keep_sampling_mask: bool = True
    preserve_routing: bool = True  # For MoE models

    # Domain-specific KL weights
    domain_kl_weights: dict[str, float] = field(
        default_factory=lambda: {
            "math": 0.0,
            "code": 0.05,
            "agricultural": 0.0,  # SAHOOL: no KL for agricultural advisory
            "general": 0.1,
        }
    )

    # Training parameters
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    num_epochs: int = 1
    warmup_ratio: float = 0.1

    def get_effective_kl_weight(self, domain: str = "general") -> float:
        """Get KL weight for specific domain."""
        if self.kl_coef == 0.0:
            return 0.0
        return self.domain_kl_weights.get(domain, self.kl_coef)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "variant": self.variant.value,
            "group_size": self.group_size,
            "clip_range": self.clip_range,
            "clip_higher": self.clip_higher,
            "kl_coef": self.kl_coef,
            "normalize_advantages": self.normalize_advantages,
            "normalize_by_std": self.normalize_by_std,
            "dynamic_sampling": self.dynamic_sampling,
            "token_level_loss": self.token_level_loss,
            "overlong_penalty": self.overlong_penalty,
            "reweight_kl": self.reweight_kl,
            "off_policy_masking": self.off_policy_masking,
            "off_policy_threshold": self.off_policy_threshold,
            "keep_sampling_mask": self.keep_sampling_mask,
            "domain_kl_weights": self.domain_kl_weights,
        }


@dataclass
class GRPOSample:
    """A single GRPO training sample."""

    prompt: str
    response: str
    reward: float
    log_prob: float
    ref_log_prob: float
    tokens: list[int] = field(default_factory=list)
    domain: str = "general"
    truncated: bool = False
    sampling_mask: list[bool] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GRPOBatch:
    """A batch of GRPO samples grouped by prompt."""

    prompt: str
    samples: list[GRPOSample]
    advantages: list[float] = field(default_factory=list)
    should_skip: bool = False
    skip_reason: str | None = None


@dataclass
class GRPOTrainingStats:
    """Training statistics for GRPO."""

    total_batches: int = 0
    skipped_batches: int = 0
    masked_sequences: int = 0
    total_loss: float = 0.0
    policy_loss: float = 0.0
    kl_loss: float = 0.0
    entropy_loss: float = 0.0
    mean_reward: float = 0.0
    mean_advantage: float = 0.0
    clip_fraction: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_batches": self.total_batches,
            "skipped_batches": self.skipped_batches,
            "masked_sequences": self.masked_sequences,
            "total_loss": self.total_loss,
            "policy_loss": self.policy_loss,
            "kl_loss": self.kl_loss,
            "entropy_loss": self.entropy_loss,
            "mean_reward": self.mean_reward,
            "mean_advantage": self.mean_advantage,
            "clip_fraction": self.clip_fraction,
            "timestamp": self.timestamp.isoformat(),
        }


class GRPOTrainer:
    """
    GRPO Trainer with DAPO/Dr.GRPO/DeepSeek V3.2 improvements.

    مدرب GRPO مع تحسينات DAPO و Dr.GRPO و DeepSeek V3.2

    This trainer implements state-of-the-art reinforcement learning
    techniques for language model training, specifically optimized
    for agricultural advisory generation in SAHOOL.

    Features:
        - Group-relative advantage computation (no critic needed)
        - Dynamic sampling to skip uninformative batches
        - Token-level loss weighting
        - Off-policy sequence masking
        - Domain-specific KL regularization
        - Asymmetric clipping for better exploration

    Example:
        ```python
        config = GRPOConfig(
            variant=GRPOVariant.DEEPSEEK,
            domain_kl_weights={"agricultural": 0.0}
        )

        trainer = GRPOTrainer(config)

        # Create training batch
        batch = GRPOBatch(
            prompt="How to irrigate wheat?",
            samples=[
                GRPOSample(prompt="...", response="...", reward=0.9, ...),
                GRPOSample(prompt="...", response="...", reward=0.7, ...),
            ]
        )

        # Compute advantages
        batch = trainer.compute_advantages(batch)

        # Compute loss
        loss, stats = trainer.compute_loss(batch, current_log_probs)
        ```
    """

    def __init__(self, config: GRPOConfig | None = None):
        """
        Initialize GRPO Trainer.

        Args:
            config: GRPO configuration
        """
        self.config = config or GRPOConfig()
        self._stats_history: list[GRPOTrainingStats] = []

    def compute_advantages(self, batch: GRPOBatch) -> GRPOBatch:
        """
        Compute group-relative advantages for a batch.

        حساب المزايا النسبية للمجموعة

        GRPO computes advantages relative to the group mean,
        eliminating the need for a value model (critic).

        Args:
            batch: Batch of samples for the same prompt

        Returns:
            Batch with computed advantages
        """
        rewards = [s.reward for s in batch.samples]

        # Check for dynamic sampling (DAPO)
        if self.config.dynamic_sampling:
            if all(r > 0.9 for r in rewards):
                batch.should_skip = True
                batch.skip_reason = "all_correct"
                return batch
            if all(r < 0.1 for r in rewards):
                batch.should_skip = True
                batch.skip_reason = "all_wrong"
                return batch

        # Compute group mean
        mean_reward = sum(rewards) / len(rewards)

        # Compute advantages relative to group mean
        advantages = [r - mean_reward for r in rewards]

        # Normalize advantages
        if self.config.normalize_advantages:
            if self.config.normalize_by_std:
                # Original GRPO: normalize by std
                std = math.sqrt(sum(a * a for a in advantages) / len(advantages))
                if std > 1e-8:
                    advantages = [a / std for a in advantages]
            else:
                # Dr.GRPO: normalize by mean absolute value (NOT std)
                mean_abs = sum(abs(a) for a in advantages) / len(advantages)
                if mean_abs > 1e-8:
                    advantages = [a / mean_abs for a in advantages]

        batch.advantages = advantages
        return batch

    def should_mask_sequence(
        self,
        sample: GRPOSample,
        current_log_prob: float,
    ) -> bool:
        """
        Check if sequence should be masked (DeepSeek V3.2).

        فحص ما إذا كان يجب تصفية التسلسل

        Mask highly off-policy negative samples to prevent
        destabilizing gradient updates.

        Args:
            sample: The training sample
            current_log_prob: Current policy log probability

        Returns:
            True if sequence should be masked
        """
        if not self.config.off_policy_masking:
            return False

        # Compute policy divergence
        divergence = abs(current_log_prob - sample.log_prob)

        # Get advantage (need to compute if not available)
        advantage = sample.metadata.get("advantage", 0.0)

        # Mask if negative advantage AND high divergence
        return advantage < 0 and divergence > self.config.off_policy_threshold

    def compute_policy_loss(
        self,
        batch: GRPOBatch,
        current_log_probs: list[float],
    ) -> tuple[float, dict[str, float]]:
        """
        Compute GRPO policy loss with all improvements.

        حساب خسارة السياسة مع جميع التحسينات

        Args:
            batch: Batch with computed advantages
            current_log_probs: Current policy log probabilities

        Returns:
            Tuple of (loss, metrics dict)
        """
        if batch.should_skip:
            return 0.0, {"skipped": True, "reason": batch.skip_reason}

        total_loss = 0.0
        total_weight = 0.0
        clipped_count = 0
        masked_count = 0

        for i, (sample, advantage) in enumerate(zip(batch.samples, batch.advantages)):
            current_log_prob = current_log_probs[i]

            # Store advantage in metadata for masking check
            sample.metadata["advantage"] = advantage

            # Check if should mask (DeepSeek V3.2)
            if self.should_mask_sequence(sample, current_log_prob):
                masked_count += 1
                continue

            # Compute importance ratio
            ratio = math.exp(current_log_prob - sample.log_prob)

            # Apply sampling mask if available (DeepSeek V3.2)
            if self.config.keep_sampling_mask and sample.sampling_mask:
                # The mask ensures same action space for importance sampling
                pass  # Applied at token level in full implementation

            # Compute clipped ratio (DAPO: asymmetric clipping)
            clip_low = 1.0 - self.config.clip_range
            clip_high = 1.0 + self.config.clip_higher

            clipped_ratio = max(clip_low, min(clip_high, ratio))

            if ratio != clipped_ratio:
                clipped_count += 1

            # Compute surrogate losses
            surr1 = ratio * advantage
            surr2 = clipped_ratio * advantage

            # PPO-clip objective (minimize negative advantage)
            sample_loss = -min(surr1, surr2)

            # Token-level weighting (DAPO)
            if self.config.token_level_loss and sample.tokens:
                weight = len(sample.tokens)
            else:
                weight = 1.0

            # Overlong penalty (DAPO)
            if self.config.overlong_penalty > 0 and sample.truncated:
                sample_loss += self.config.overlong_penalty

            total_loss += sample_loss * weight
            total_weight += weight

        # Normalize by total weight
        if total_weight > 0:
            total_loss /= total_weight

        metrics = {
            "policy_loss": total_loss,
            "clip_fraction": clipped_count / len(batch.samples) if batch.samples else 0,
            "masked_count": masked_count,
            "mean_advantage": sum(batch.advantages) / len(batch.advantages) if batch.advantages else 0,
        }

        return total_loss, metrics

    def compute_kl_loss(
        self,
        batch: GRPOBatch,
        current_log_probs: list[float],
    ) -> tuple[float, dict[str, float]]:
        """
        Compute KL divergence loss with DeepSeek V3.2 improvements.

        حساب خسارة KL مع تحسينات DeepSeek V3.2

        Args:
            batch: Training batch
            current_log_probs: Current policy log probabilities

        Returns:
            Tuple of (kl_loss, metrics)
        """
        if batch.should_skip:
            return 0.0, {"kl_loss": 0.0}

        # Get domain from first sample
        domain = batch.samples[0].domain if batch.samples else "general"

        # Get domain-specific KL weight
        kl_weight = self.config.get_effective_kl_weight(domain)

        if kl_weight == 0.0:
            return 0.0, {"kl_loss": 0.0, "kl_weight": 0.0}

        total_kl = 0.0

        for i, sample in enumerate(batch.samples):
            current_log_prob = current_log_probs[i]

            # KL divergence: ref_log_prob - current_log_prob
            kl_div = sample.ref_log_prob - current_log_prob

            # Reweight with importance ratio (DeepSeek V3.2)
            if self.config.reweight_kl:
                importance_ratio = math.exp(current_log_prob - sample.log_prob)
                kl_div *= importance_ratio

            total_kl += kl_div

        # Average KL
        avg_kl = total_kl / len(batch.samples) if batch.samples else 0.0

        # Apply weight
        kl_loss = kl_weight * avg_kl

        return kl_loss, {"kl_loss": kl_loss, "kl_weight": kl_weight, "raw_kl": avg_kl}

    def compute_entropy_loss(
        self,
        log_probs: list[float],
    ) -> tuple[float, dict[str, float]]:
        """
        Compute entropy bonus for exploration.

        حساب مكافأة الإنتروبيا للاستكشاف

        Args:
            log_probs: Log probabilities

        Returns:
            Tuple of (entropy_loss, metrics)
        """
        if self.config.entropy_coef == 0.0:
            return 0.0, {"entropy": 0.0}

        # Entropy = -sum(p * log(p))
        # For log_probs, entropy = -mean(log_probs) approximately
        mean_log_prob = sum(log_probs) / len(log_probs) if log_probs else 0.0
        entropy = -mean_log_prob

        # We want to maximize entropy, so minimize -entropy
        entropy_loss = -self.config.entropy_coef * entropy

        return entropy_loss, {"entropy": entropy, "entropy_loss": entropy_loss}

    def compute_loss(
        self,
        batch: GRPOBatch,
        current_log_probs: list[float],
    ) -> tuple[float, GRPOTrainingStats]:
        """
        Compute total GRPO loss.

        حساب إجمالي خسارة GRPO

        Args:
            batch: Training batch with advantages
            current_log_probs: Current policy log probabilities

        Returns:
            Tuple of (total_loss, training_stats)
        """
        # Compute component losses
        policy_loss, policy_metrics = self.compute_policy_loss(batch, current_log_probs)
        kl_loss, kl_metrics = self.compute_kl_loss(batch, current_log_probs)
        entropy_loss, entropy_metrics = self.compute_entropy_loss(current_log_probs)

        # Total loss
        total_loss = policy_loss + kl_loss + entropy_loss

        # Create stats
        stats = GRPOTrainingStats(
            total_batches=1,
            skipped_batches=1 if batch.should_skip else 0,
            masked_sequences=policy_metrics.get("masked_count", 0),
            total_loss=total_loss,
            policy_loss=policy_loss,
            kl_loss=kl_loss,
            entropy_loss=entropy_loss,
            mean_reward=sum(s.reward for s in batch.samples) / len(batch.samples) if batch.samples else 0,
            mean_advantage=policy_metrics.get("mean_advantage", 0),
            clip_fraction=policy_metrics.get("clip_fraction", 0),
        )

        self._stats_history.append(stats)

        return total_loss, stats

    def get_training_summary(self) -> dict[str, Any]:
        """Get summary of all training statistics."""
        if not self._stats_history:
            return {"message": "No training data"}

        total_batches = sum(s.total_batches for s in self._stats_history)
        skipped_batches = sum(s.skipped_batches for s in self._stats_history)
        masked_sequences = sum(s.masked_sequences for s in self._stats_history)

        return {
            "total_batches": total_batches,
            "skipped_batches": skipped_batches,
            "skip_rate": skipped_batches / total_batches if total_batches > 0 else 0,
            "masked_sequences": masked_sequences,
            "avg_loss": sum(s.total_loss for s in self._stats_history) / len(self._stats_history),
            "avg_policy_loss": sum(s.policy_loss for s in self._stats_history) / len(self._stats_history),
            "avg_kl_loss": sum(s.kl_loss for s in self._stats_history) / len(self._stats_history),
            "avg_reward": sum(s.mean_reward for s in self._stats_history) / len(self._stats_history),
            "avg_clip_fraction": sum(s.clip_fraction for s in self._stats_history) / len(self._stats_history),
        }

    def reset_stats(self) -> None:
        """Reset training statistics."""
        self._stats_history.clear()


class SAHOOLGRPOTrainer(GRPOTrainer):
    """
    SAHOOL-specific GRPO trainer optimized for agricultural advisory.

    مدرب GRPO مخصص لسهول ومحسن للاستشارات الزراعية

    This trainer is pre-configured with settings optimized for
    training agricultural advisory models:
    - No KL regularization for agricultural domain
    - Token-level loss for variable-length advisories
    - Dynamic sampling to focus on informative examples

    Example:
        ```python
        trainer = SAHOOLGRPOTrainer()

        # Train on advisory batch
        batch = GRPOBatch(
            prompt="متى أسقي القمح؟",
            samples=[...]
        )

        batch = trainer.compute_advantages(batch)
        loss, stats = trainer.compute_loss(batch, current_log_probs)
        ```
    """

    def __init__(self, config: GRPOConfig | None = None):
        """Initialize SAHOOL GRPO Trainer with optimized defaults."""
        if config is None:
            config = GRPOConfig(
                variant=GRPOVariant.DEEPSEEK,
                # No KL for agricultural domain
                kl_coef=0.0,
                domain_kl_weights={
                    "agricultural": 0.0,
                    "irrigation": 0.0,
                    "fertilizer": 0.0,
                    "pest_control": 0.0,
                    "general": 0.05,
                },
                # DAPO improvements
                dynamic_sampling=True,
                token_level_loss=True,
                clip_higher=0.28,
                # DeepSeek improvements
                off_policy_masking=True,
                reweight_kl=True,
                keep_sampling_mask=True,
            )

        super().__init__(config)

    def create_advisory_batch(
        self,
        prompt: str,
        responses: list[str],
        rewards: list[float],
        domain: str = "agricultural",
    ) -> GRPOBatch:
        """
        Create a training batch from advisory responses.

        إنشاء دفعة تدريب من استجابات الاستشارات

        Args:
            prompt: The farmer's question
            responses: List of advisory responses
            rewards: Reward scores for each response
            domain: Advisory domain

        Returns:
            GRPOBatch ready for training
        """
        samples = []
        for response, reward in zip(responses, rewards):
            # Estimate log prob (placeholder - real implementation uses model)
            estimated_log_prob = -2.0 - (1.0 - reward)  # Higher reward = higher prob

            sample = GRPOSample(
                prompt=prompt,
                response=response,
                reward=reward,
                log_prob=estimated_log_prob,
                ref_log_prob=estimated_log_prob,  # Reference = initial policy
                domain=domain,
                truncated=len(response) > self.config.max_response_length,
            )
            samples.append(sample)

        batch = GRPOBatch(prompt=prompt, samples=samples)
        return self.compute_advantages(batch)


# Convenience functions
def create_grpo_config_for_domain(domain: str) -> GRPOConfig:
    """
    Create optimized GRPO config for specific domain.

    إنشاء إعدادات GRPO محسنة لمجال معين

    Args:
        domain: Domain name (agricultural, math, code, etc.)

    Returns:
        Optimized GRPOConfig
    """
    configs = {
        "agricultural": GRPOConfig(
            variant=GRPOVariant.DEEPSEEK,
            kl_coef=0.0,  # No KL for agricultural
            dynamic_sampling=True,
            token_level_loss=True,
        ),
        "math": GRPOConfig(
            variant=GRPOVariant.DEEPSEEK,
            kl_coef=0.0,  # DeepSeek: zero KL for math
            dynamic_sampling=True,
            token_level_loss=True,
            clip_higher=0.3,  # More exploration
        ),
        "code": GRPOConfig(
            variant=GRPOVariant.DEEPSEEK,
            kl_coef=0.05,  # Light KL for code
            dynamic_sampling=True,
            token_level_loss=True,
        ),
    }

    return configs.get(domain, GRPOConfig())


def get_grpo_tips() -> list[dict[str, str]]:
    """
    Get list of GRPO tips and tricks with sources.

    قائمة نصائح وحيل GRPO مع المصادر

    Returns:
        List of tips with name, description, and source
    """
    return [
        {
            "name": "Zero gradient signal filtering",
            "name_ar": "تصفية إشارة التدرج الصفرية",
            "description": "Skip batches where all responses are correct or all wrong",
            "source": "DAPO by Yu et al., 2025",
        },
        {
            "name": "Active sampling",
            "name_ar": "أخذ العينات النشط",
            "description": "Dynamically select informative training batches",
            "source": "DAPO by Yu et al., 2025",
        },
        {
            "name": "Token-level loss",
            "name_ar": "الخسارة على مستوى الرمز",
            "description": "Weight loss by response length for longer responses",
            "source": "DAPO by Yu et al., 2025",
        },
        {
            "name": "No KL loss",
            "name_ar": "بدون خسارة KL",
            "description": "Remove KL penalty for better exploration",
            "source": "DAPO & Dr.GRPO, 2025",
        },
        {
            "name": "Clip higher",
            "name_ar": "قطع أعلى",
            "description": "Asymmetric PPO clipping with higher upper bound",
            "source": "DAPO by Yu et al., 2025",
        },
        {
            "name": "No std normalization",
            "name_ar": "بدون تطبيع بالانحراف المعياري",
            "description": "Normalize advantages by mean absolute value, not std",
            "source": "Dr. GRPO by Liu et al., 2025",
        },
        {
            "name": "Reweighted KL",
            "name_ar": "KL معاد ترجيحه",
            "description": "Weight KL term by importance ratio",
            "source": "DeepSeek V3.2, Liu et al., 2025",
        },
        {
            "name": "Off-policy sequence masking",
            "name_ar": "تصفية التسلسلات خارج السياسة",
            "description": "Mask stale negative samples to prevent destabilization",
            "source": "DeepSeek V3.2, Liu et al., 2025",
        },
        {
            "name": "Keep sampling mask",
            "name_ar": "الاحتفاظ بقناع أخذ العينات",
            "description": "Preserve top-p/top-k masks during training",
            "source": "DeepSeek V3.2, Liu et al., 2025",
        },
        {
            "name": "Domain-specific KL",
            "name_ar": "KL خاص بالمجال",
            "description": "Use different KL weights per domain (zero for math)",
            "source": "DeepSeek V3.2, Liu et al., 2025",
        },
        {
            "name": "Per-reward group normalization",
            "name_ar": "تطبيع المجموعة حسب المكافأة",
            "description": "Normalize rewards within groups before aggregation",
            "source": "GDPO by Liu et al., 2026",
        },
    ]
