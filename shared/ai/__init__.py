"""
SAHOOL AI Module
================
وحدة الذكاء الاصطناعي لمنصة سهول

AI utilities and context engineering for the SAHOOL agricultural platform.
Provides context compression, memory management, recommendation evaluation,
automated code analysis/fixing, and model training.

Modules:
    - context_engineering: Context compression, memory, and evaluation
    - auto_fix: Automated code diagnostics and fixing
    - ollama_client: Local LLM integration via Ollama
    - model_training: Fine-tuning and training capabilities

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

__version__ = "1.2.0"

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
    # Availability flags
    "OLLAMA_AVAILABLE",
    "TRAINING_AVAILABLE",
]

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
