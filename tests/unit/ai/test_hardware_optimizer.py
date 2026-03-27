"""
Hardware Optimizer Tests - اختبارات محسن الأجهزة
=================================================

Tests for hardware detection, inference configuration,
dynamic batching, and model optimization.
"""

from unittest.mock import MagicMock, patch

from shared.ai.hardware_optimizer import (
    DeviceType,
    GPUGeneration,
    HardwareAwareOptimizer,
    HardwareDetector,
    HardwareProfile,
    InferenceConfig,
    InferenceStats,
)

# =============================================================================
# HardwareProfile Tests
# =============================================================================


class TestHardwareProfile:
    """Tests for HardwareProfile dataclass."""

    def test_default_profile_is_cpu(self):
        profile = HardwareProfile()
        assert profile.device_type == DeviceType.CPU
        assert profile.device_name == "CPU"
        assert profile.gpu_generation == GPUGeneration.UNKNOWN
        assert profile.tensor_cores is False

    def test_cuda_profile(self):
        profile = HardwareProfile(
            device_type=DeviceType.CUDA,
            device_name="NVIDIA A100",
            gpu_generation=GPUGeneration.AMPERE,
            compute_capability=(8, 0),
            sm_count=108,
            total_memory_gb=40.0,
            tensor_cores=True,
            supports_bf16=True,
            supports_fp16=True,
            supports_int8=True,
            supports_flash_attention=True,
        )
        assert profile.device_type == DeviceType.CUDA
        assert profile.tensor_cores is True
        assert profile.supports_bf16 is True

    def test_to_dict(self):
        profile = HardwareProfile(
            device_type=DeviceType.CUDA,
            device_name="RTX 3090",
            gpu_generation=GPUGeneration.AMPERE,
            compute_capability=(8, 6),
            total_memory_gb=24.0,
            tensor_cores=True,
        )
        d = profile.to_dict()
        assert d["device_type"] == "cuda"
        assert d["device_name"] == "RTX 3090"
        assert d["gpu_generation"] == "ampere"
        assert d["tensor_cores"] is True
        assert d["total_memory_gb"] == 24.0

    def test_mps_profile(self):
        profile = HardwareProfile(
            device_type=DeviceType.MPS,
            device_name="Apple Silicon",
            supports_fp16=True,
            supports_bf16=False,
        )
        assert profile.device_type == DeviceType.MPS
        assert profile.supports_fp16 is True
        assert profile.supports_bf16 is False


# =============================================================================
# InferenceConfig Tests
# =============================================================================


class TestInferenceConfig:
    """Tests for InferenceConfig dataclass."""

    def test_default_config(self):
        config = InferenceConfig()
        assert config.precision == "bf16"
        assert config.use_tensor_cores is True
        assert config.flash_attention is True
        assert config.dynamic_batching is True
        assert config.max_batch_tokens == 65536

    def test_to_dict(self):
        config = InferenceConfig(precision="fp16", max_batch_tokens=32768)
        d = config.to_dict()
        assert d["precision"] == "fp16"
        assert d["max_batch_tokens"] == 32768
        assert d["dynamic_batching"] is True


# =============================================================================
# InferenceStats Tests
# =============================================================================


class TestInferenceStats:
    """Tests for InferenceStats dataclass."""

    def test_default_stats(self):
        stats = InferenceStats()
        assert stats.total_tokens == 0
        assert stats.total_time_ms == 0.0
        assert stats.tokens_per_second == 0.0

    def test_to_dict(self):
        stats = InferenceStats(
            total_tokens=1000,
            total_time_ms=500.0,
            tokens_per_second=2000.0,
            peak_memory_gb=8.0,
        )
        d = stats.to_dict()
        assert d["total_tokens"] == 1000
        assert d["tokens_per_second"] == 2000.0


# =============================================================================
# HardwareDetector Tests
# =============================================================================


class TestHardwareDetector:
    """Tests for HardwareDetector."""

    def test_detect_cpu_fallback(self):
        """When no GPU is available, should fall back to CPU."""
        with patch.dict("sys.modules", {"torch": None}):
            # Force ImportError for torch
            profile = HardwareDetector._detect_cpu()
            assert profile.device_type == DeviceType.CPU
            assert profile.cpu_cores > 0

    def test_detect_mps(self):
        profile = HardwareDetector._detect_mps()
        assert profile.device_type == DeviceType.MPS
        assert profile.device_name == "Apple Silicon"
        assert profile.supports_fp16 is True
        assert profile.supports_bf16 is False

    def test_compute_to_generation_mapping(self):
        mapping = HardwareDetector.COMPUTE_TO_GENERATION
        assert mapping[(7, 0)] == GPUGeneration.VOLTA
        assert mapping[(8, 0)] == GPUGeneration.AMPERE
        assert mapping[(8, 9)] == GPUGeneration.ADA
        assert mapping[(9, 0)] == GPUGeneration.HOPPER
        assert mapping[(10, 0)] == GPUGeneration.BLACKWELL


# =============================================================================
# HardwareAwareOptimizer Tests
# =============================================================================


class TestHardwareAwareOptimizer:
    """Tests for HardwareAwareOptimizer."""

    def test_cpu_optimal_config(self):
        """CPU profile should generate conservative config."""
        profile = HardwareProfile(
            device_type=DeviceType.CPU,
            device_name="CPU",
            supports_bf16=False,
            supports_fp16=False,
        )
        optimizer = HardwareAwareOptimizer(profile=profile)
        config = optimizer.get_optimal_config()
        assert config.precision == "fp32"
        assert config.use_tensor_cores is False
        assert config.flash_attention is False

    def test_ampere_optimal_config(self):
        """Ampere GPU should enable bf16 and flash attention."""
        profile = HardwareProfile(
            device_type=DeviceType.CUDA,
            device_name="A100",
            gpu_generation=GPUGeneration.AMPERE,
            total_memory_gb=40.0,
            tensor_cores=True,
            supports_bf16=True,
            supports_fp16=True,
            supports_int8=True,
            supports_flash_attention=True,
        )
        optimizer = HardwareAwareOptimizer(profile=profile)
        config = optimizer.get_optimal_config()
        assert config.precision == "bf16"
        assert config.use_tensor_cores is True
        assert config.flash_attention is True
        assert config.attention_chunk_size == 4096
        assert config.max_batch_tokens == 65536
        assert config.kv_cache_quantization is True

    def test_hopper_optimal_config(self):
        """Hopper GPU should enable larger attention chunks and compilation."""
        profile = HardwareProfile(
            device_type=DeviceType.CUDA,
            device_name="H100",
            gpu_generation=GPUGeneration.HOPPER,
            total_memory_gb=80.0,
            tensor_cores=True,
            supports_bf16=True,
            supports_fp16=True,
            supports_int8=True,
            supports_flash_attention=True,
            supports_tma=True,
        )
        optimizer = HardwareAwareOptimizer(profile=profile)
        config = optimizer.get_optimal_config()
        assert config.attention_chunk_size == 8192
        assert config.max_batch_tokens == 131072
        assert config.compile_model is True

    def test_blackwell_optimal_config(self):
        """Blackwell GPU should use largest attention chunks."""
        profile = HardwareProfile(
            device_type=DeviceType.CUDA,
            device_name="B300",
            gpu_generation=GPUGeneration.BLACKWELL,
            total_memory_gb=80.0,
            tensor_cores=True,
            supports_bf16=True,
            supports_fp16=True,
            supports_int8=True,
            supports_flash_attention=True,
            supports_tma=True,
        )
        optimizer = HardwareAwareOptimizer(profile=profile)
        config = optimizer.get_optimal_config()
        assert config.attention_chunk_size == 16384
        assert config.compile_model is True

    def test_small_gpu_memory_batch_sizing(self):
        """Small GPU should get smaller batch sizes."""
        profile = HardwareProfile(
            device_type=DeviceType.CUDA,
            total_memory_gb=8.0,
            supports_bf16=True,
        )
        optimizer = HardwareAwareOptimizer(profile=profile)
        config = optimizer.get_optimal_config()
        assert config.max_batch_tokens == 8192

    def test_fp16_fallback_without_bf16(self):
        """When bf16 not supported, should fall back to fp16."""
        profile = HardwareProfile(
            device_type=DeviceType.CUDA,
            supports_bf16=False,
            supports_fp16=True,
        )
        optimizer = HardwareAwareOptimizer(profile=profile)
        config = optimizer.get_optimal_config()
        assert config.precision == "fp16"

    def test_custom_config_override(self):
        """Custom config should override auto-detection."""
        profile = HardwareProfile()
        custom_config = InferenceConfig(precision="int8", max_batch_tokens=1024)
        optimizer = HardwareAwareOptimizer(profile=profile, config=custom_config)
        assert optimizer.config.precision == "int8"
        assert optimizer.config.max_batch_tokens == 1024

    # ─── Dynamic Batching Tests ────────────────────────────────────────────

    def test_dynamic_batching_single_batch(self):
        """Inputs that fit in one batch."""
        profile = HardwareProfile()
        config = InferenceConfig(dynamic_batching=True, max_batch_tokens=100)
        optimizer = HardwareAwareOptimizer(profile=profile, config=config)

        inputs = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]  # 9 tokens total
        batches = optimizer.create_dynamic_batch(inputs)
        assert len(batches) == 1
        assert len(batches[0]) == 3

    def test_dynamic_batching_multiple_batches(self):
        """Inputs that exceed token limit should split into batches."""
        profile = HardwareProfile()
        config = InferenceConfig(dynamic_batching=True, max_batch_tokens=5)
        optimizer = HardwareAwareOptimizer(profile=profile, config=config)

        inputs = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]  # 3 tokens each
        batches = optimizer.create_dynamic_batch(inputs)
        assert len(batches) >= 2

    def test_dynamic_batching_disabled(self):
        """When disabled, all inputs in single batch."""
        profile = HardwareProfile()
        config = InferenceConfig(dynamic_batching=False, max_batch_tokens=1)
        optimizer = HardwareAwareOptimizer(profile=profile, config=config)

        inputs = [[1, 2, 3], [4, 5, 6]]
        batches = optimizer.create_dynamic_batch(inputs)
        assert len(batches) == 1
        assert len(batches[0]) == 2

    def test_dynamic_batching_empty_input(self):
        """Empty input list returns empty batches."""
        profile = HardwareProfile()
        config = InferenceConfig(dynamic_batching=True)
        optimizer = HardwareAwareOptimizer(profile=profile, config=config)

        batches = optimizer.create_dynamic_batch([])
        assert len(batches) == 0

    def test_dynamic_batching_large_single_input(self):
        """Single input larger than batch limit goes in its own batch."""
        profile = HardwareProfile()
        config = InferenceConfig(dynamic_batching=True, max_batch_tokens=5)
        optimizer = HardwareAwareOptimizer(profile=profile, config=config)

        inputs = [list(range(10))]  # 10 tokens
        batches = optimizer.create_dynamic_batch(inputs)
        assert len(batches) == 1
        assert len(batches[0]) == 1

    # ─── Model Optimization Tests ──────────────────────────────────────────

    def test_optimize_model_fp16(self):
        """Model optimization with fp16."""
        model = MagicMock()
        model.half.return_value = model

        profile = HardwareProfile()
        config = InferenceConfig(
            precision="fp16",
            flash_attention=False,
            kv_cache_quantization=False,
            gradient_checkpointing=False,
            compile_model=False,
        )
        optimizer = HardwareAwareOptimizer(profile=profile, config=config)
        result = optimizer.optimize_model(model)
        model.half.assert_called_once()

    def test_optimize_model_flash_attention(self):
        """Model optimization enables flash attention when supported."""
        model = MagicMock()

        profile = HardwareProfile()
        config = InferenceConfig(
            precision="fp32",
            flash_attention=True,
            kv_cache_quantization=False,
            gradient_checkpointing=False,
            compile_model=False,
        )
        optimizer = HardwareAwareOptimizer(profile=profile, config=config)
        optimizer.optimize_model(model)
        model.enable_flash_attention.assert_called_once()


# =============================================================================
# Enum Tests
# =============================================================================


class TestEnums:
    """Tests for hardware optimizer enums."""

    def test_gpu_generation_values(self):
        assert GPUGeneration.VOLTA == "volta"
        assert GPUGeneration.HOPPER == "hopper"
        assert GPUGeneration.BLACKWELL == "blackwell"

    def test_device_type_values(self):
        assert DeviceType.CPU == "cpu"
        assert DeviceType.CUDA == "cuda"
        assert DeviceType.MPS == "mps"
        assert DeviceType.GROQ == "groq"
