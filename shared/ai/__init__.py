"""
SAHOOL AI Module
================
وحدة الذكاء الاصطناعي لمنصة سهول

AI utilities and context engineering for the SAHOOL agricultural platform.
Provides context compression, memory management, recommendation evaluation,
automated code analysis/fixing, model training, audit logging, and circuit breakers.

Modules:
    - context_engineering: Context compression, memory, and evaluation
    - auto_fix: Automated code diagnostics and fixing
    - ollama_client: Local LLM integration via Ollama
    - model_training: Fine-tuning and training capabilities
    - audit: Unified AI audit logging with cost tracking
    - circuit_breaker: Resilience pattern for external services
    - metrics: Prometheus-compatible observability metrics

Author: SAHOOL Platform Team
Updated: January 2026
"""

from .context_engineering import (
    # Compression
    ContextCompressor,
    CompressionResult,
    CompressionStrategy,
    # Memory
    FarmMemory,
    MemoryEntry,
    MemoryConfig,
    # Evaluation
    RecommendationEvaluator,
    EvaluationResult,
    EvaluationCriteria,
)

from .auto_fix import (
    # Engine
    AutoFixEngine,
    quick_diagnose,
    quick_fix,
    # Diagnostics
    CodeDiagnostics,
    DiagnosticError,
    # Fixers
    CodeFixer,
    FixerError,
    # Models
    Diagnostic,
    DiagnosticReport,
    DiagnosticSeverity,
    DiagnosticCategory,
    CodeFix,
    FixPlan,
    FixResult,
    FixStrategy,
    FixConfidence,
    ToolType,
    AuditEntry,
)

# Audit logging
from .audit import (
    AIAuditLogger,
    AuditEvent,
    AuditEventType,
    SafetyLevel,
    calculate_cost,
    get_audit_logger,
    get_cost_summary,
    log_agent_call,
    LLM_COSTS,
)

# Circuit breaker
from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitBreakerStats,
    CircuitState,
    get_circuit_breaker,
    get_ollama_circuit_breaker,
    get_anthropic_circuit_breaker,
    get_openai_circuit_breaker,
    get_all_circuit_breakers,
    reset_all_circuit_breakers,
)

# Metrics
from .metrics import (
    AIMetricsCollector,
    MetricType,
    MetricValue,
    get_metrics_collector,
)

# Validation
from .validation import (
    AIValidator,
    ValidationResult,
    ValidationIssue,
    ValidationLevel,
    ThreatCategory,
    Severity,
    get_validator,
    validate_prompt,
    validate_response,
    is_safe_prompt,
    is_safe_response,
)

# LLM Provider Manager (optional - requires httpx)
try:
    from .llm_provider import (
        LLMProviderManager,
        LLMProvider,
        LLMConfig,
        LLMResponse,
        LLMProviderError,
        AllProvidersFailedError,
        get_llm_manager,
        generate_text,
        generate_with_ollama_fallback,
    )
    LLM_MANAGER_AVAILABLE = True
except ImportError:
    LLM_MANAGER_AVAILABLE = False

# Ollama client (optional - requires httpx)
try:
    from .ollama_client import (
        OllamaClient,
        OllamaConfig,
        OllamaError,
        OllamaModel,
        OllamaResponse,
        analyze_code_with_ollama,
        fix_code_with_ollama,
        generate_tests_with_ollama,
    )
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Model training (optional - requires httpx)
try:
    from .model_training import (
        DatasetBuilder,
        DatasetType,
        ModelTrainer,
        TrainingConfig,
        TrainingDataset,
        TrainingExample,
        TrainingJob,
        TrainingStatus,
        EvaluationResult as TrainingEvalResult,
        create_code_fix_dataset,
        train_code_fixer,
    )
    TRAINING_AVAILABLE = True
except ImportError:
    TRAINING_AVAILABLE = False

__version__ = "1.4.0"

__all__ = [
    # Context Engineering - Compression
    "ContextCompressor",
    "CompressionResult",
    "CompressionStrategy",
    # Context Engineering - Memory
    "FarmMemory",
    "MemoryEntry",
    "MemoryConfig",
    # Context Engineering - Evaluation
    "RecommendationEvaluator",
    "EvaluationResult",
    "EvaluationCriteria",
    # Auto-Fix - Engine
    "AutoFixEngine",
    "quick_diagnose",
    "quick_fix",
    # Auto-Fix - Diagnostics
    "CodeDiagnostics",
    "DiagnosticError",
    # Auto-Fix - Fixers
    "CodeFixer",
    "FixerError",
    # Auto-Fix - Models
    "Diagnostic",
    "DiagnosticReport",
    "DiagnosticSeverity",
    "DiagnosticCategory",
    "CodeFix",
    "FixPlan",
    "FixResult",
    "FixStrategy",
    "FixConfidence",
    "ToolType",
    "AuditEntry",
    # Audit logging
    "AIAuditLogger",
    "AuditEvent",
    "AuditEventType",
    "SafetyLevel",
    "calculate_cost",
    "get_audit_logger",
    "get_cost_summary",
    "log_agent_call",
    "LLM_COSTS",
    # Circuit breaker
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerError",
    "CircuitBreakerStats",
    "CircuitState",
    "get_circuit_breaker",
    "get_ollama_circuit_breaker",
    "get_anthropic_circuit_breaker",
    "get_openai_circuit_breaker",
    "get_all_circuit_breakers",
    "reset_all_circuit_breakers",
    # Metrics
    "AIMetricsCollector",
    "MetricType",
    "MetricValue",
    "get_metrics_collector",
    # Validation
    "AIValidator",
    "ValidationResult",
    "ValidationIssue",
    "ValidationLevel",
    "ThreatCategory",
    "Severity",
    "get_validator",
    "validate_prompt",
    "validate_response",
    "is_safe_prompt",
    "is_safe_response",
    # Availability flags
    "OLLAMA_AVAILABLE",
    "TRAINING_AVAILABLE",
    "LLM_MANAGER_AVAILABLE",
]

# Add LLM Manager exports if available
if LLM_MANAGER_AVAILABLE:
    __all__.extend([
        "LLMProviderManager",
        "LLMProvider",
        "LLMConfig",
        "LLMResponse",
        "LLMProviderError",
        "AllProvidersFailedError",
        "get_llm_manager",
        "generate_text",
        "generate_with_ollama_fallback",
    ])

# Add Ollama exports if available
if OLLAMA_AVAILABLE:
    __all__.extend([
        "OllamaClient",
        "OllamaConfig",
        "OllamaError",
        "OllamaModel",
        "OllamaResponse",
        "analyze_code_with_ollama",
        "fix_code_with_ollama",
        "generate_tests_with_ollama",
    ])

# Add training exports if available
if TRAINING_AVAILABLE:
    __all__.extend([
        "DatasetBuilder",
        "DatasetType",
        "ModelTrainer",
        "TrainingConfig",
        "TrainingDataset",
        "TrainingExample",
        "TrainingJob",
        "TrainingStatus",
        "TrainingEvalResult",
        "create_code_fix_dataset",
        "train_code_fixer",
    ])
