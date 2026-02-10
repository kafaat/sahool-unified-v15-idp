"""
Hardware-Aware Inference Optimizer
==================================
محسن الاستدلال المدرك للأجهزة

Optimizes AI inference based on hardware capabilities,
applying insights from Zartbot's GPU architecture research.

Key optimizations:
- Tensor Core utilization
- Attention mechanism optimization (address SFU bottleneck)
- Memory hierarchy awareness
- Dynamic batching

Based on research from:
- Zartbot: NVIDIA GPU Architecture Analysis
- Zartbot: Groq LPU Architecture
- Flash Attention optimizations

Author: SAHOOL Platform Team
Updated: January 2026
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import StrEnum
from typing import Any


class GPUGeneration(StrEnum):
    """NVIDIA GPU generation."""

    UNKNOWN = "unknown"
    VOLTA = "volta"  # SM70 - First Tensor Cores
    TURING = "turing"  # SM75
    AMPERE = "ampere"  # SM80 - cp.async
    ADA = "ada"  # SM89
    HOPPER = "hopper"  # SM90 - TMA, WGMMA
    BLACKWELL = "blackwell"  # SM100 - TMEM
    RUBIN = "rubin"  # SM110 (predicted)


class DeviceType(StrEnum):
    """Compute device type."""

    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"  # Apple Silicon
    TPU = "tpu"
    GROQ = "groq"  # Groq LPU


@dataclass
class HardwareProfile:
    """
    Profile of detected hardware capabilities.

    ملف تعريف قدرات الأجهزة المكتشفة
    """

    device_type: DeviceType = DeviceType.CPU
    device_name: str = "CPU"

    # GPU-specific
    gpu_generation: GPUGeneration = GPUGeneration.UNKNOWN
    compute_capability: tuple[int, int] = (0, 0)
    sm_count: int = 0
    total_memory_gb: float = 0.0
    tensor_cores: bool = False

    # CPU-specific
    cpu_cores: int = 1
    cpu_threads: int = 1

    # Features
    supports_bf16: bool = False
    supports_fp16: bool = False
    supports_int8: bool = False
    supports_flash_attention: bool = False
    supports_tma: bool = False  # Tensor Memory Accelerator (Hopper+)

    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "device_type": self.device_type.value,
            "device_name": self.device_name,
            "gpu_generation": self.gpu_generation.value,
            "compute_capability": self.compute_capability,
            "sm_count": self.sm_count,
            "total_memory_gb": self.total_memory_gb,
            "tensor_cores": self.tensor_cores,
            "supports_bf16": self.supports_bf16,
            "supports_fp16": self.supports_fp16,
            "supports_int8": self.supports_int8,
            "supports_flash_attention": self.supports_flash_attention,
            "supports_tma": self.supports_tma,
        }


@dataclass
class InferenceConfig:
    """
    Hardware-aware inference configuration.

    إعدادات الاستدلال المدركة للأجهزة

    Attributes:
        precision: Compute precision (bf16, fp16, fp32, int8)
        use_tensor_cores: Enable Tensor Core operations
        flash_attention: Use Flash Attention for memory efficiency
        attention_chunk_size: Chunk size for attention (address SFU bottleneck)
        kv_cache_quantization: Quantize KV cache for memory savings
        dynamic_batching: Enable dynamic batching
        max_batch_tokens: Maximum tokens per batch
        gradient_checkpointing: Trade compute for memory
        compile_model: Use torch.compile for optimization
    """

    # Precision
    precision: str = "bf16"  # bf16, fp16, fp32, int8

    # Tensor Core optimization
    use_tensor_cores: bool = True

    # Attention optimization (address SFU bottleneck from Zartbot's analysis)
    flash_attention: bool = True
    attention_chunk_size: int = 8192  # Larger chunks for Hopper+

    # Memory optimization
    kv_cache_quantization: bool = True
    gradient_checkpointing: bool = False
    max_memory_fraction: float = 0.9

    # Batch optimization
    dynamic_batching: bool = True
    max_batch_tokens: int = 65536
    padding_strategy: str = "longest"  # longest, max_length

    # Compilation
    compile_model: bool = False
    compile_mode: str = "reduce-overhead"  # default, reduce-overhead, max-autotune

    # Groq-style deterministic execution (optional)
    deterministic_execution: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "precision": self.precision,
            "use_tensor_cores": self.use_tensor_cores,
            "flash_attention": self.flash_attention,
            "attention_chunk_size": self.attention_chunk_size,
            "kv_cache_quantization": self.kv_cache_quantization,
            "gradient_checkpointing": self.gradient_checkpointing,
            "dynamic_batching": self.dynamic_batching,
            "max_batch_tokens": self.max_batch_tokens,
        }


@dataclass
class InferenceStats:
    """
    Statistics from inference run.

    إحصائيات تشغيل الاستدلال
    """

    total_tokens: int = 0
    total_time_ms: float = 0.0
    tokens_per_second: float = 0.0
    peak_memory_gb: float = 0.0
    batch_size: int = 0
    num_batches: int = 0

    # Detailed metrics
    attention_time_ms: float = 0.0
    other_time_ms: float = 0.0

    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_tokens": self.total_tokens,
            "total_time_ms": self.total_time_ms,
            "tokens_per_second": self.tokens_per_second,
            "peak_memory_gb": self.peak_memory_gb,
            "batch_size": self.batch_size,
            "num_batches": self.num_batches,
        }


class HardwareDetector:
    """
    Detects and profiles available hardware.

    كاشف ومحلل الأجهزة المتاحة

    Based on Zartbot's GPU architecture analysis,
    this detector identifies key capabilities.
    """

    # GPU generation mapping based on compute capability
    COMPUTE_TO_GENERATION = {
        (7, 0): GPUGeneration.VOLTA,
        (7, 5): GPUGeneration.TURING,
        (8, 0): GPUGeneration.AMPERE,
        (8, 6): GPUGeneration.AMPERE,
        (8, 9): GPUGeneration.ADA,
        (9, 0): GPUGeneration.HOPPER,
        (10, 0): GPUGeneration.BLACKWELL,
        (11, 0): GPUGeneration.RUBIN,
    }

    @classmethod
    def detect(cls) -> HardwareProfile:
        """
        Detect available hardware and create profile.

        كشف الأجهزة المتاحة وإنشاء ملف تعريف
        """
        # Try CUDA first
        try:
            import torch

            if torch.cuda.is_available():
                return cls._detect_cuda()
        except ImportError:
            pass

        # Try Apple Silicon
        try:
            import torch

            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return cls._detect_mps()
        except ImportError:
            pass

        # Fallback to CPU
        return cls._detect_cpu()

    @classmethod
    def _detect_cuda(cls) -> HardwareProfile:
        """Detect CUDA GPU capabilities."""
        import torch

        props = torch.cuda.get_device_properties(0)
        cc = (props.major, props.minor)

        # Determine generation
        generation = cls.COMPUTE_TO_GENERATION.get(cc, GPUGeneration.UNKNOWN)
        if generation == GPUGeneration.UNKNOWN:
            # Try to infer from major version
            if props.major >= 11:
                generation = GPUGeneration.RUBIN
            elif props.major >= 10:
                generation = GPUGeneration.BLACKWELL
            elif props.major >= 9:
                generation = GPUGeneration.HOPPER
            elif props.major >= 8:
                generation = GPUGeneration.AMPERE

        # Determine features
        tensor_cores = props.major >= 7
        supports_bf16 = props.major >= 8
        supports_fp16 = props.major >= 7
        supports_int8 = props.major >= 7
        supports_tma = props.major >= 9  # Hopper+
        supports_flash = props.major >= 8  # Ampere+

        return HardwareProfile(
            device_type=DeviceType.CUDA,
            device_name=props.name,
            gpu_generation=generation,
            compute_capability=cc,
            sm_count=props.multi_processor_count,
            total_memory_gb=props.total_memory / (1024**3),
            tensor_cores=tensor_cores,
            supports_bf16=supports_bf16,
            supports_fp16=supports_fp16,
            supports_int8=supports_int8,
            supports_flash_attention=supports_flash,
            supports_tma=supports_tma,
        )

    @classmethod
    def _detect_mps(cls) -> HardwareProfile:
        """Detect Apple Silicon capabilities."""
        return HardwareProfile(
            device_type=DeviceType.MPS,
            device_name="Apple Silicon",
            supports_fp16=True,
            supports_bf16=False,  # MPS doesn't fully support bf16
        )

    @classmethod
    def _detect_cpu(cls) -> HardwareProfile:
        """Detect CPU capabilities."""
        import multiprocessing

        return HardwareProfile(
            device_type=DeviceType.CPU,
            device_name="CPU",
            cpu_cores=multiprocessing.cpu_count(),
            cpu_threads=multiprocessing.cpu_count(),
        )


class HardwareAwareOptimizer:
    """
    Optimizes inference based on hardware capabilities.

    محسن الاستدلال القائم على قدرات الأجهزة

    Applies insights from Zartbot's research:
    - Tensor Core evolution (Volta -> Blackwell)
    - SFU bottleneck in attention (Blackwell limitation)
    - Groq-style deterministic scheduling (optional)
    - Memory hierarchy optimization

    Example:
        ```python
        optimizer = HardwareAwareOptimizer()

        # Auto-detect and configure
        config = optimizer.get_optimal_config()

        # Apply to model
        model = optimizer.optimize_model(model)

        # Run inference with dynamic batching
        results = await optimizer.run_inference(model, inputs)
        ```
    """

    def __init__(
        self,
        profile: HardwareProfile | None = None,
        config: InferenceConfig | None = None,
    ):
        """
        Initialize Hardware-Aware Optimizer.

        Args:
            profile: Hardware profile (auto-detected if None)
            config: Inference configuration (auto-configured if None)
        """
        self.profile = profile or HardwareDetector.detect()
        self.config = config or self._create_optimal_config()
        self._stats_history: list[InferenceStats] = []

    def _create_optimal_config(self) -> InferenceConfig:
        """
        Create optimal configuration based on hardware profile.

        إنشاء إعدادات مثلى بناءً على ملف تعريف الأجهزة
        """
        config = InferenceConfig()

        # Precision selection
        if self.profile.supports_bf16:
            config.precision = "bf16"
        elif self.profile.supports_fp16:
            config.precision = "fp16"
        else:
            config.precision = "fp32"

        # Tensor Core usage
        config.use_tensor_cores = self.profile.tensor_cores

        # Flash Attention
        config.flash_attention = self.profile.supports_flash_attention

        # Attention chunk size (larger for newer GPUs)
        # Based on Zartbot's analysis of SFU bottleneck in Blackwell
        if self.profile.gpu_generation in [GPUGeneration.BLACKWELL, GPUGeneration.RUBIN]:
            # B300 has SFU bottleneck, use larger chunks
            config.attention_chunk_size = 16384
        elif self.profile.gpu_generation == GPUGeneration.HOPPER:
            config.attention_chunk_size = 8192
        elif self.profile.gpu_generation == GPUGeneration.AMPERE:
            config.attention_chunk_size = 4096
        else:
            config.attention_chunk_size = 2048

        # Memory-based batch sizing
        if self.profile.total_memory_gb >= 80:  # H100 80GB
            config.max_batch_tokens = 131072
        elif self.profile.total_memory_gb >= 40:  # A100 40GB
            config.max_batch_tokens = 65536
        elif self.profile.total_memory_gb >= 24:  # 3090/4090
            config.max_batch_tokens = 32768
        elif self.profile.total_memory_gb >= 16:
            config.max_batch_tokens = 16384
        else:
            config.max_batch_tokens = 8192

        # KV cache quantization for memory efficiency
        config.kv_cache_quantization = self.profile.supports_int8

        # Model compilation (Hopper+ benefits most)
        config.compile_model = self.profile.gpu_generation in [
            GPUGeneration.HOPPER,
            GPUGeneration.BLACKWELL,
            GPUGeneration.RUBIN,
        ]

        return config

    def get_optimal_config(self) -> InferenceConfig:
        """Get the optimal inference configuration."""
        return self.config

    def optimize_model(self, model: Any) -> Any:
        """
        Apply optimizations to model.

        تطبيق التحسينات على النموذج

        Args:
            model: Model to optimize

        Returns:
            Optimized model
        """
        # Check if model has optimization methods
        if hasattr(model, "half") and self.config.precision == "fp16":
            model = model.half()
        elif hasattr(model, "bfloat16") and self.config.precision == "bf16":
            model = model.bfloat16()

        # Enable Flash Attention if supported
        if self.config.flash_attention and hasattr(model, "enable_flash_attention"):
            model.enable_flash_attention()

        # Set attention chunk size
        if hasattr(model, "set_attention_chunk_size"):
            model.set_attention_chunk_size(self.config.attention_chunk_size)

        # Enable KV cache quantization
        if self.config.kv_cache_quantization and hasattr(model, "enable_kv_cache_quantization"):
            model.enable_kv_cache_quantization()

        # Enable gradient checkpointing
        if self.config.gradient_checkpointing and hasattr(model, "gradient_checkpointing_enable"):
            model.gradient_checkpointing_enable()

        # Compile model with torch.compile
        if self.config.compile_model:
            try:
                import torch

                if hasattr(torch, "compile"):
                    model = torch.compile(
                        model,
                        mode=self.config.compile_mode,
                    )
            except Exception:
                pass

        return model

    def create_dynamic_batch(
        self,
        inputs: list[list[int]],
    ) -> list[list[list[int]]]:
        """
        Create dynamic batches based on token limits.

        إنشاء دفعات ديناميكية بناءً على حدود الرموز

        Args:
            inputs: List of tokenized inputs

        Returns:
            List of batches
        """
        if not self.config.dynamic_batching:
            return [inputs]

        batches = []
        current_batch = []
        current_tokens = 0

        for input_ids in inputs:
            input_len = len(input_ids)

            if current_tokens + input_len > self.config.max_batch_tokens:
                if current_batch:
                    batches.append(current_batch)
                current_batch = [input_ids]
                current_tokens = input_len
            else:
                current_batch.append(input_ids)
                current_tokens += input_len

        if current_batch:
            batches.append(current_batch)

        return batches

    async def run_inference(
        self,
        model: Any,
        inputs: list[str],
        tokenizer: Any | None = None,
    ) -> tuple[list[str], InferenceStats]:
        """
        Run optimized inference.

        تشغيل الاستدلال المحسن

        Args:
            model: Model for inference
            inputs: List of input texts
            tokenizer: Tokenizer (optional)

        Returns:
            Tuple of (outputs, stats)
        """
        import time

        start_time = time.time()

        # Track memory
        peak_memory = 0.0
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.reset_peak_memory_stats()
        except ImportError:
            pass

        # Tokenize inputs (placeholder)
        if tokenizer:
            tokenized = [tokenizer.encode(inp) for inp in inputs]
        else:
            tokenized = [[ord(c) for c in inp] for inp in inputs]

        # Create dynamic batches
        batches = self.create_dynamic_batch(tokenized)

        # Run inference on batches
        outputs = []
        total_tokens = 0

        for batch in batches:
            # Placeholder inference
            batch_outputs = [f"Output for: {len(b)} tokens" for b in batch]
            outputs.extend(batch_outputs)
            total_tokens += sum(len(b) for b in batch)

        # Get peak memory
        try:
            import torch

            if torch.cuda.is_available():
                peak_memory = torch.cuda.max_memory_allocated() / (1024**3)
        except ImportError:
            pass

        elapsed_ms = (time.time() - start_time) * 1000

        stats = InferenceStats(
            total_tokens=total_tokens,
            total_time_ms=elapsed_ms,
            tokens_per_second=total_tokens / (elapsed_ms / 1000) if elapsed_ms > 0 else 0,
            peak_memory_gb=peak_memory,
            batch_size=len(inputs),
            num_batches=len(batches),
        )

        self._stats_history.append(stats)

        return outputs, stats

    def get_stats_summary(self) -> dict[str, Any]:
        """Get summary of inference statistics."""
        if not self._stats_history:
            return {"message": "No inference data"}

        total_tokens = sum(s.total_tokens for s in self._stats_history)
        total_time = sum(s.total_time_ms for s in self._stats_history)

        return {
            "total_inferences": len(self._stats_history),
            "total_tokens": total_tokens,
            "total_time_ms": total_time,
            "avg_tokens_per_second": total_tokens / (total_time / 1000) if total_time > 0 else 0,
            "avg_peak_memory_gb": sum(s.peak_memory_gb for s in self._stats_history)
            / len(self._stats_history),
        }

    def get_hardware_recommendations(self) -> list[dict[str, str]]:
        """
        Get recommendations based on hardware profile.

        الحصول على توصيات بناءً على ملف تعريف الأجهزة

        Based on Zartbot's GPU architecture analysis.
        """
        recommendations = []

        # Tensor Core recommendations
        if self.profile.tensor_cores and not self.config.use_tensor_cores:
            recommendations.append(
                {
                    "type": "performance",
                    "message": "Enable Tensor Cores for faster matrix operations",
                    "message_ar": "تمكين نوى التنسور لعمليات المصفوفات الأسرع",
                }
            )

        # Flash Attention
        if self.profile.supports_flash_attention and not self.config.flash_attention:
            recommendations.append(
                {
                    "type": "memory",
                    "message": "Enable Flash Attention for memory efficiency and speed",
                    "message_ar": "تمكين Flash Attention لكفاءة الذاكرة والسرعة",
                }
            )

        # Precision recommendations
        if self.profile.supports_bf16 and self.config.precision != "bf16":
            recommendations.append(
                {
                    "type": "precision",
                    "message": "Use BF16 precision for better training stability with same speed",
                    "message_ar": "استخدم دقة BF16 لثبات تدريب أفضل بنفس السرعة",
                }
            )

        # SFU bottleneck warning (Blackwell)
        if self.profile.gpu_generation == GPUGeneration.BLACKWELL:
            recommendations.append(
                {
                    "type": "attention",
                    "message": "Blackwell has SFU bottleneck in Softmax - use larger attention chunks",
                    "message_ar": "Blackwell لديه عنق زجاجة SFU في Softmax - استخدم قطع انتباه أكبر",
                    "source": "Zartbot GPU Analysis",
                }
            )

        # TMA recommendation (Hopper+)
        if self.profile.supports_tma:
            recommendations.append(
                {
                    "type": "memory",
                    "message": "TMA available - use Tensor Memory operations for async data loading",
                    "message_ar": "TMA متاح - استخدم عمليات ذاكرة التنسور للتحميل غير المتزامن",
                }
            )

        # Memory recommendations
        if self.profile.total_memory_gb < 16:
            recommendations.append(
                {
                    "type": "memory",
                    "message": "Limited GPU memory - enable gradient checkpointing and KV cache quantization",
                    "message_ar": "ذاكرة GPU محدودة - مكّن نقاط تفتيش التدرج وتكميم ذاكرة KV",
                }
            )

        return recommendations


# Convenience functions
def detect_hardware() -> HardwareProfile:
    """Detect available hardware."""
    return HardwareDetector.detect()


def get_optimal_inference_config() -> InferenceConfig:
    """Get optimal inference configuration for detected hardware."""
    optimizer = HardwareAwareOptimizer()
    return optimizer.get_optimal_config()


def optimize_for_inference(model: Any) -> Any:
    """Optimize model for inference based on detected hardware."""
    optimizer = HardwareAwareOptimizer()
    return optimizer.optimize_model(model)
