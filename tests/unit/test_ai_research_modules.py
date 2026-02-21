"""
Tests for AI Research Modules
=============================
اختبارات وحدات البحث في الذكاء الاصطناعي

Tests for:
- GRPO Trainer (DAPO/Dr.GRPO/DeepSeek techniques)
- Diffusion Advisory Generator
- OT-based Embeddings
- Hardware-Aware Optimizer

Author: SAHOOL Platform Team
Updated: January 2026
"""

import math
import pytest
from unittest.mock import MagicMock, patch


# =============================================================================
# GRPO Trainer Tests
# =============================================================================


class TestGRPOConfig:
    """Tests for GRPO configuration."""

    def test_default_config(self):
        """Test default GRPO configuration."""
        from shared.ai.grpo_trainer import GRPOConfig, GRPOVariant

        config = GRPOConfig()

        assert config.variant == GRPOVariant.DEEPSEEK
        assert config.group_size == 8
        assert config.clip_range == 0.2
        assert config.clip_higher == 0.28
        assert config.kl_coef == 0.0  # Dr.GRPO default
        assert config.normalize_by_std is False  # Dr.GRPO fix
        assert config.dynamic_sampling is True  # DAPO
        assert config.off_policy_masking is True  # DeepSeek V3.2

    def test_domain_kl_weights(self):
        """Test domain-specific KL weights."""
        from shared.ai.grpo_trainer import GRPOConfig

        config = GRPOConfig(kl_coef=0.1)

        # Agricultural should be zero
        assert config.get_effective_kl_weight("agricultural") == 0.0
        # Math should be zero
        assert config.get_effective_kl_weight("math") == 0.0
        # General should use default
        assert config.get_effective_kl_weight("general") == 0.1

    def test_config_to_dict(self):
        """Test configuration serialization."""
        from shared.ai.grpo_trainer import GRPOConfig

        config = GRPOConfig()
        result = config.to_dict()

        assert "variant" in result
        assert "clip_range" in result
        assert "domain_kl_weights" in result


class TestGRPOTrainer:
    """Tests for GRPO Trainer."""

    def test_compute_advantages(self):
        """Test group-relative advantage computation."""
        from shared.ai.grpo_trainer import GRPOTrainer, GRPOConfig, GRPOBatch, GRPOSample

        trainer = GRPOTrainer(GRPOConfig(normalize_advantages=False))

        # Create batch with varying rewards
        samples = [
            GRPOSample(prompt="test", response="r1", reward=0.8, log_prob=-1.0, ref_log_prob=-1.0),
            GRPOSample(prompt="test", response="r2", reward=0.6, log_prob=-1.0, ref_log_prob=-1.0),
            GRPOSample(prompt="test", response="r3", reward=0.4, log_prob=-1.0, ref_log_prob=-1.0),
            GRPOSample(prompt="test", response="r4", reward=0.2, log_prob=-1.0, ref_log_prob=-1.0),
        ]
        batch = GRPOBatch(prompt="test", samples=samples)

        # Compute advantages
        result = trainer.compute_advantages(batch)

        # Mean reward is 0.5, so advantages should be relative to that
        assert len(result.advantages) == 4
        assert result.advantages[0] > 0  # 0.8 > 0.5
        assert result.advantages[1] > 0  # 0.6 > 0.5
        assert result.advantages[2] < 0  # 0.4 < 0.5
        assert result.advantages[3] < 0  # 0.2 < 0.5

    def test_dynamic_sampling_skip_all_correct(self):
        """Test DAPO dynamic sampling - skip all correct."""
        from shared.ai.grpo_trainer import GRPOTrainer, GRPOConfig, GRPOBatch, GRPOSample

        trainer = GRPOTrainer(GRPOConfig(dynamic_sampling=True))

        # All high rewards
        samples = [
            GRPOSample(prompt="test", response="r1", reward=0.95, log_prob=-1.0, ref_log_prob=-1.0),
            GRPOSample(prompt="test", response="r2", reward=0.92, log_prob=-1.0, ref_log_prob=-1.0),
        ]
        batch = GRPOBatch(prompt="test", samples=samples)

        result = trainer.compute_advantages(batch)

        assert result.should_skip is True
        assert result.skip_reason == "all_correct"

    def test_dynamic_sampling_skip_all_wrong(self):
        """Test DAPO dynamic sampling - skip all wrong."""
        from shared.ai.grpo_trainer import GRPOTrainer, GRPOConfig, GRPOBatch, GRPOSample

        trainer = GRPOTrainer(GRPOConfig(dynamic_sampling=True))

        # All low rewards
        samples = [
            GRPOSample(prompt="test", response="r1", reward=0.05, log_prob=-1.0, ref_log_prob=-1.0),
            GRPOSample(prompt="test", response="r2", reward=0.08, log_prob=-1.0, ref_log_prob=-1.0),
        ]
        batch = GRPOBatch(prompt="test", samples=samples)

        result = trainer.compute_advantages(batch)

        assert result.should_skip is True
        assert result.skip_reason == "all_wrong"

    def test_off_policy_masking(self):
        """Test DeepSeek V3.2 off-policy sequence masking."""
        from shared.ai.grpo_trainer import GRPOTrainer, GRPOConfig, GRPOSample

        trainer = GRPOTrainer(
            GRPOConfig(
                off_policy_masking=True,
                off_policy_threshold=0.5,
            )
        )

        # Sample with negative advantage and high divergence
        sample = GRPOSample(
            prompt="test",
            response="test",
            reward=0.3,
            log_prob=-2.0,
            ref_log_prob=-2.0,
            metadata={"advantage": -0.2},  # Negative advantage
        )

        # High divergence (current much different from original)
        should_mask = trainer.should_mask_sequence(sample, -3.0)  # divergence = 1.0 > 0.5
        assert should_mask is True

        # Low divergence
        should_mask = trainer.should_mask_sequence(sample, -2.1)  # divergence = 0.1 < 0.5
        assert should_mask is False

    def test_dr_grpo_no_std_normalization(self):
        """Test Dr.GRPO: normalize by mean abs, not std."""
        from shared.ai.grpo_trainer import GRPOTrainer, GRPOConfig, GRPOBatch, GRPOSample

        trainer = GRPOTrainer(
            GRPOConfig(
                normalize_advantages=True,
                normalize_by_std=False,  # Dr.GRPO
            )
        )

        samples = [
            GRPOSample(prompt="test", response="r1", reward=1.0, log_prob=-1.0, ref_log_prob=-1.0),
            GRPOSample(prompt="test", response="r2", reward=0.0, log_prob=-1.0, ref_log_prob=-1.0),
        ]
        batch = GRPOBatch(prompt="test", samples=samples)

        result = trainer.compute_advantages(batch)

        # With mean abs normalization, advantages should be normalized
        assert len(result.advantages) == 2
        # Mean is 0.5, so advantages are [0.5, -0.5], mean_abs = 0.5
        # Normalized: [1.0, -1.0]
        assert abs(result.advantages[0] - 1.0) < 0.01
        assert abs(result.advantages[1] - (-1.0)) < 0.01

    def test_grpo_tips(self):
        """Test GRPO tips list."""
        from shared.ai.grpo_trainer import get_grpo_tips

        tips = get_grpo_tips()

        assert len(tips) >= 10
        assert all("name" in tip for tip in tips)
        assert all("source" in tip for tip in tips)

        # Check for key techniques
        tip_names = [t["name"].lower() for t in tips]
        assert any("kl" in name for name in tip_names)
        assert any("clip" in name for name in tip_names)
        assert any("off-policy" in name for name in tip_names)


class TestSAHOOLGRPOTrainer:
    """Tests for SAHOOL-specific GRPO trainer."""

    def test_default_agricultural_config(self):
        """Test SAHOOL trainer has agricultural defaults."""
        from shared.ai.grpo_trainer import SAHOOLGRPOTrainer

        trainer = SAHOOLGRPOTrainer()

        # Check agricultural-specific config
        assert trainer.config.kl_coef == 0.0
        assert "agricultural" in trainer.config.domain_kl_weights
        assert trainer.config.domain_kl_weights["agricultural"] == 0.0

    def test_create_advisory_batch(self):
        """Test creating advisory training batch."""
        from shared.ai.grpo_trainer import SAHOOLGRPOTrainer

        trainer = SAHOOLGRPOTrainer()

        batch = trainer.create_advisory_batch(
            prompt="كيف أسقي القمح؟",
            responses=["الري كل 10 أيام", "الري كل 7 أيام"],
            rewards=[0.9, 0.7],
            domain="irrigation",
        )

        assert len(batch.samples) == 2
        assert batch.samples[0].domain == "irrigation"
        assert len(batch.advantages) == 2


# =============================================================================
# Diffusion Advisory Generator Tests
# =============================================================================


class TestDiffusionConfig:
    """Tests for Diffusion configuration."""

    def test_default_config(self):
        """Test default diffusion configuration."""
        from shared.ai.diffusion import DiffusionConfig

        config = DiffusionConfig()

        assert config.model_name == "llada-8b-instruct"
        assert config.num_steps == 32
        assert config.default_language == "ar"  # Arabic default for SAHOOL

    def test_config_to_dict(self):
        """Test configuration serialization."""
        from shared.ai.diffusion import DiffusionConfig

        config = DiffusionConfig()
        result = config.to_dict()

        assert "model_name" in result
        assert "num_steps" in result


class TestMaskScheduler:
    """Tests for mask scheduler."""

    def test_cosine_schedule(self):
        """Test cosine mask schedule."""
        from shared.ai.diffusion.advisory import MaskScheduler

        scheduler = MaskScheduler(schedule="cosine", num_steps=10)

        # Alpha schedule decreases: step 0 = fully preserved (1.0), step N = fully masked (0.0)
        ratio_0 = scheduler.get_mask_ratio(0)
        ratio_10 = scheduler.get_mask_ratio(10)

        assert ratio_0 > ratio_10
        assert ratio_0 >= 0.9  # Step 0: almost fully preserved

    def test_linear_schedule(self):
        """Test linear mask schedule."""
        from shared.ai.diffusion.advisory import MaskScheduler

        scheduler = MaskScheduler(schedule="linear", num_steps=10)

        # Linear alpha schedule decreases monotonically from 1.0 to 0.0
        ratios = [scheduler.get_mask_ratio(i) for i in range(11)]

        # Check monotonic decrease
        for i in range(len(ratios) - 1):
            assert ratios[i] >= ratios[i + 1]


class TestDiffusionAdvisoryGenerator:
    """Tests for Diffusion Advisory Generator."""

    @pytest.mark.asyncio
    async def test_generate(self):
        """Test basic generation."""
        from shared.ai.diffusion import DiffusionAdvisoryGenerator

        generator = DiffusionAdvisoryGenerator()

        result = await generator.generate(
            prompt="كيف أسقي القمح؟",
            context={"crop": "wheat"},
        )

        assert result.text is not None
        assert result.num_steps > 0
        assert result.model == "llada-8b-instruct"

    @pytest.mark.asyncio
    async def test_infill(self):
        """Test template infilling."""
        from shared.ai.diffusion import DiffusionAdvisoryGenerator

        generator = DiffusionAdvisoryGenerator()

        template = "يُنصح بالري كل [MASK] أيام"
        result = await generator.infill(template)

        assert result.text is not None
        assert "[MASK]" not in result.text or result.tokens_generated > 0

    @pytest.mark.asyncio
    async def test_edit(self):
        """Test edit flows."""
        from shared.ai.diffusion import DiffusionAdvisoryGenerator, EditOperation, EditType

        generator = DiffusionAdvisoryGenerator()

        original = "الري كل 10 أيام"
        edits = [
            EditOperation(
                edit_type=EditType.SUBSTITUTE,
                position=2,
                content="7",
                length=1,
            )
        ]

        result = await generator.edit(original, edits)

        assert result.text is not None

    @pytest.mark.asyncio
    async def test_generate_from_template(self):
        """Test generation from predefined template."""
        from shared.ai.diffusion import DiffusionAdvisoryGenerator

        generator = DiffusionAdvisoryGenerator()

        result = await generator.generate_from_template(
            template_name="irrigation",
            context={"crop": "wheat", "stage": "tillering"},
        )

        assert result.text is not None


# =============================================================================
# OT Embeddings Tests
# =============================================================================


class TestOTConfig:
    """Tests for OT configuration."""

    def test_default_config(self):
        """Test default OT configuration."""
        from shared.ai.ot_embeddings import OTConfig

        config = OTConfig()

        assert config.regularization == 0.1
        assert config.num_iterations == 100
        assert config.cost_metric == "euclidean"


class TestOTEmbeddingMatcher:
    """Tests for OT Embedding Matcher."""

    def test_compute_cost_matrix_euclidean(self):
        """Test Euclidean cost matrix computation."""
        from shared.ai.ot_embeddings import OTEmbeddingMatcher

        matcher = OTEmbeddingMatcher()

        source = [[1.0, 0.0], [0.0, 1.0]]
        target = [[1.0, 1.0], [0.0, 0.0]]

        cost = matcher.compute_cost_matrix(source, target)

        assert len(cost) == 2
        assert len(cost[0]) == 2
        # Distance from [1,0] to [0,0] should be 1.0
        assert abs(cost[0][1] - 1.0) < 0.01

    def test_sinkhorn_distance_identical(self):
        """Test Sinkhorn distance for identical vectors."""
        from shared.ai.ot_embeddings import OTEmbeddingMatcher

        matcher = OTEmbeddingMatcher()

        vec = [1.0, 2.0, 3.0]
        result = matcher.sinkhorn_distance(vec, vec)

        # Distance to self should be very small
        assert result.sinkhorn_distance < 0.1
        assert result.converged is True

    def test_sinkhorn_distance_different(self):
        """Test Sinkhorn distance for different vectors."""
        from shared.ai.ot_embeddings import OTEmbeddingMatcher

        matcher = OTEmbeddingMatcher()

        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 0.0, 1.0]

        result = matcher.sinkhorn_distance(vec1, vec2)

        # Distance should be positive
        assert result.sinkhorn_distance > 0
        assert result.computation_time_ms > 0

    def test_ot_to_similarity(self):
        """Test OT distance to similarity conversion."""
        from shared.ai.ot_embeddings import OTEmbeddingMatcher

        matcher = OTEmbeddingMatcher()

        # Zero distance = similarity 1.0
        sim = matcher.ot_to_similarity(0.0)
        assert abs(sim - 1.0) < 0.01

        # Large distance = low similarity
        sim = matcher.ot_to_similarity(10.0)
        assert sim < 0.1

    @pytest.mark.asyncio
    async def test_match_advisories(self):
        """Test advisory matching."""
        from shared.ai.ot_embeddings import OTEmbeddingMatcher

        matcher = OTEmbeddingMatcher()

        query = [1.0, 0.5, 0.0]
        candidates = [
            [1.0, 0.5, 0.1],  # Similar
            [0.0, 0.0, 1.0],  # Different
            [0.9, 0.6, 0.0],  # Very similar
        ]

        results = await matcher.match_advisories(query, candidates, top_k=2)

        assert len(results) == 2
        # Results should be sorted by distance (lowest first)
        assert results[0][1] < results[1][1]


class TestBilingualOTMatcher:
    """Tests for Bilingual OT Matcher."""

    @pytest.mark.asyncio
    async def test_match(self):
        """Test bilingual matching."""
        pytest.importorskip("sentence_transformers", reason="sentence-transformers not installed")
        from shared.ai.ot_embeddings import BilingualOTMatcher

        matcher = BilingualOTMatcher()

        results = await matcher.match(
            query="كيف أعالج صدأ القمح؟",
            candidates=["Wheat rust treatment", "Rice planting", "Wheat irrigation"],
            top_k=2,
        )

        assert len(results) == 2
        # Results should have (text, ot_distance, cosine_sim)
        assert len(results[0]) == 3


# =============================================================================
# Hardware Optimizer Tests
# =============================================================================


class TestHardwareProfile:
    """Tests for Hardware Profile."""

    def test_default_profile(self):
        """Test default hardware profile."""
        from shared.ai.hardware_optimizer import HardwareProfile, DeviceType

        profile = HardwareProfile()

        assert profile.device_type == DeviceType.CPU
        assert profile.tensor_cores is False

    def test_profile_to_dict(self):
        """Test profile serialization."""
        from shared.ai.hardware_optimizer import HardwareProfile

        profile = HardwareProfile()
        result = profile.to_dict()

        assert "device_type" in result
        assert "tensor_cores" in result


class TestInferenceConfig:
    """Tests for Inference Config."""

    def test_default_config(self):
        """Test default inference configuration."""
        from shared.ai.hardware_optimizer import InferenceConfig

        config = InferenceConfig()

        assert config.precision == "bf16"
        assert config.flash_attention is True
        assert config.dynamic_batching is True


class TestHardwareDetector:
    """Tests for Hardware Detector."""

    def test_detect_cpu(self):
        """Test CPU detection."""
        from shared.ai.hardware_optimizer import HardwareDetector, DeviceType

        # This should at least return CPU profile
        profile = HardwareDetector.detect()

        assert profile.device_type in [DeviceType.CPU, DeviceType.CUDA, DeviceType.MPS]


class TestHardwareAwareOptimizer:
    """Tests for Hardware-Aware Optimizer."""

    def test_create_optimal_config(self):
        """Test optimal config creation."""
        from shared.ai.hardware_optimizer import HardwareAwareOptimizer

        optimizer = HardwareAwareOptimizer()
        config = optimizer.get_optimal_config()

        assert config is not None
        assert config.precision in ["bf16", "fp16", "fp32"]

    def test_create_dynamic_batch(self):
        """Test dynamic batch creation."""
        from shared.ai.hardware_optimizer import HardwareAwareOptimizer, InferenceConfig

        config = InferenceConfig(
            dynamic_batching=True,
            max_batch_tokens=100,
        )
        optimizer = HardwareAwareOptimizer(config=config)

        # Create inputs with varying lengths
        inputs = [
            list(range(30)),  # 30 tokens
            list(range(40)),  # 40 tokens
            list(range(50)),  # 50 tokens
        ]

        batches = optimizer.create_dynamic_batch(inputs)

        # Should split into multiple batches due to token limit
        assert len(batches) >= 2

    def test_get_hardware_recommendations(self):
        """Test hardware recommendations."""
        from shared.ai.hardware_optimizer import HardwareAwareOptimizer

        optimizer = HardwareAwareOptimizer()
        recommendations = optimizer.get_hardware_recommendations()

        assert isinstance(recommendations, list)
        # Should have at least some recommendations
        for rec in recommendations:
            assert "type" in rec
            assert "message" in rec

    @pytest.mark.asyncio
    async def test_run_inference(self):
        """Test inference execution."""
        from shared.ai.hardware_optimizer import HardwareAwareOptimizer

        optimizer = HardwareAwareOptimizer()

        # Mock model
        model = MagicMock()

        inputs = ["Hello", "World"]
        outputs, stats = await optimizer.run_inference(model, inputs)

        assert len(outputs) == 2
        assert stats.total_tokens > 0
        assert stats.batch_size == 2


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests across modules."""

    @pytest.mark.asyncio
    async def test_grpo_with_diffusion_output(self):
        """Test GRPO training with diffusion-generated outputs."""
        from shared.ai.grpo_trainer import SAHOOLGRPOTrainer
        from shared.ai.diffusion import DiffusionAdvisoryGenerator

        # Generate advisories
        generator = DiffusionAdvisoryGenerator()
        result1 = await generator.generate("How to irrigate wheat?")
        result2 = await generator.generate("How to irrigate wheat?")

        # Create training batch
        trainer = SAHOOLGRPOTrainer()
        batch = trainer.create_advisory_batch(
            prompt="How to irrigate wheat?",
            responses=[result1.text, result2.text],
            rewards=[0.9, 0.7],
        )

        # Compute advantages
        batch = trainer.compute_advantages(batch)

        assert len(batch.advantages) == 2

    @pytest.mark.asyncio
    async def test_ot_matching_with_hardware_optimization(self):
        """Test OT matching with hardware-optimized embeddings."""
        from shared.ai.ot_embeddings import OTEmbeddingMatcher
        from shared.ai.hardware_optimizer import HardwareAwareOptimizer

        # Get optimal config
        optimizer = HardwareAwareOptimizer()
        config = optimizer.get_optimal_config()

        # Create OT matcher
        matcher = OTEmbeddingMatcher()

        # Run matching
        query = [1.0, 0.5, 0.0]
        candidates = [[1.0, 0.5, 0.1], [0.0, 0.0, 1.0]]

        results = await matcher.match_advisories(query, candidates)

        assert len(results) == 2
