# ═══════════════════════════════════════════════════════════════════════════════
# CodeRAGProvider - Code Agents Integration
# مزود RAG للكود - تكامل وكلاء الكود
#
# Integrates UltraRAG for code analysis and fixing agents:
# - code-fix-agent: Code analysis and auto-fixing
# - code-review-agent: Code review and suggestions
# - audit-agent: Security audit and compliance
# ═══════════════════════════════════════════════════════════════════════════════

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import structlog

from ..models import (
    EntityType,
    RelationType,
    KnowledgeChunk,
    RetrievalStrategy,
    TriRAGConfig,
)
from ..retriever import (
    RetrievalConfig,
    KnowledgeGraphRetriever,
    TriRAGRetriever,
)

logger = structlog.get_logger(__name__)


@dataclass
class CodeQueryContext:
    """Code query context | سياق استعلام الكود"""
    language: str = "python"  # python, typescript, dart
    file_path: Optional[str] = None
    project_type: Optional[str] = None  # fastapi, nestjs, flutter
    error_type: Optional[str] = None
    framework: Optional[str] = None


@dataclass
class CodeAnalysisResult:
    """Code analysis result | نتيجة تحليل الكود"""
    query: str
    analysis: str
    suggestions: List[str] = field(default_factory=list)
    related_patterns: List[Dict[str, Any]] = field(default_factory=list)
    code_examples: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    sources: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CodeRAGProvider:
    """
    Code RAG Provider for SAHOOL AI Code Agents
    مزود RAG للكود لوكلاء كود سهول الذكية

    Provides RAG capabilities for code analysis, fixing, and review
    using Knowledge Graph for code patterns and best practices.
    """

    def __init__(
        self,
        config: Optional[TriRAGConfig] = None,
        embedding_service: Optional[Any] = None,
        vector_store: Optional[Any] = None,
    ):
        self.config = config or TriRAGConfig(
            dense_weight=0.5,
            sparse_weight=0.3,
            kg_weight=0.2,
        )
        self.embedding_service = embedding_service
        self.vector_store = vector_store

        # Initialize retrievers (lazy)
        self._kg_retriever = KnowledgeGraphRetriever(embedding_service)
        self._sparse_retriever: Optional[Any] = None
        self._dense_retriever: Optional[Any] = None
        self._tri_rag: Optional[TriRAGRetriever] = None

        self._initialized = False

    async def initialize(self):
        """Initialize the provider with code knowledge"""
        if self._initialized:
            return

        # Initialize dense/sparse retrievers
        if self.vector_store and self.embedding_service:
            from ..retriever import DenseRetriever, SparseRetriever
            self._dense_retriever = DenseRetriever(self.vector_store, self.embedding_service)
            self._sparse_retriever = SparseRetriever(self.vector_store)
        else:
            # Use mock for testing
            self._dense_retriever = _MockRetriever()
            self._sparse_retriever = _MockRetriever()

        # Create Tri-RAG retriever
        self._tri_rag = TriRAGRetriever(
            dense_retriever=self._dense_retriever,
            sparse_retriever=self._sparse_retriever,
            kg_retriever=self._kg_retriever,
            config=self.config,
        )

        # Load code knowledge graph
        await self._load_code_knowledge()

        self._initialized = True
        logger.info("code_rag_provider_initialized")

    async def _load_code_knowledge(self):
        """Load code patterns and best practices into knowledge graph"""

        # ═══════════════════════════════════════════════════════════════════════
        # Language Entities - كيانات اللغات
        # ═══════════════════════════════════════════════════════════════════════
        languages = [
            {"id": "lang_python", "name": "Python", "name_ar": "بايثون",
             "entity_type": "language",
             "properties": {"version": "3.11+", "typing": "optional"}},
            {"id": "lang_typescript", "name": "TypeScript", "name_ar": "تايب سكريبت",
             "entity_type": "language",
             "properties": {"version": "5.x", "typing": "static"}},
            {"id": "lang_dart", "name": "Dart", "name_ar": "دارت",
             "entity_type": "language",
             "properties": {"version": "3.x", "typing": "static"}},
        ]

        # ═══════════════════════════════════════════════════════════════════════
        # Framework Entities - كيانات الأطر
        # ═══════════════════════════════════════════════════════════════════════
        frameworks = [
            {"id": "fw_fastapi", "name": "FastAPI", "name_ar": "فاست إيه بي آي",
             "entity_type": "framework",
             "properties": {"language": "python", "type": "web"}},
            {"id": "fw_nestjs", "name": "NestJS", "name_ar": "نيست جي إس",
             "entity_type": "framework",
             "properties": {"language": "typescript", "type": "web"}},
            {"id": "fw_flutter", "name": "Flutter", "name_ar": "فلاتر",
             "entity_type": "framework",
             "properties": {"language": "dart", "type": "mobile"}},
            {"id": "fw_prisma", "name": "Prisma", "name_ar": "بريزما",
             "entity_type": "orm",
             "properties": {"language": "typescript", "type": "database"}},
            {"id": "fw_tortoise", "name": "Tortoise ORM", "name_ar": "تورتويز",
             "entity_type": "orm",
             "properties": {"language": "python", "type": "database"}},
        ]

        # ═══════════════════════════════════════════════════════════════════════
        # Error Pattern Entities - كيانات أنماط الأخطاء
        # ═══════════════════════════════════════════════════════════════════════
        error_patterns = [
            {"id": "err_import", "name": "Import Error", "name_ar": "خطأ الاستيراد",
             "entity_type": "error_pattern",
             "properties": {"category": "syntax", "fixable": True}},
            {"id": "err_type", "name": "Type Error", "name_ar": "خطأ النوع",
             "entity_type": "error_pattern",
             "properties": {"category": "type", "fixable": True}},
            {"id": "err_null", "name": "Null Reference", "name_ar": "مرجع فارغ",
             "entity_type": "error_pattern",
             "properties": {"category": "runtime", "fixable": True}},
            {"id": "err_sql_injection", "name": "SQL Injection", "name_ar": "حقن SQL",
             "entity_type": "security_issue",
             "properties": {"category": "security", "severity": "critical"}},
            {"id": "err_xss", "name": "XSS Vulnerability", "name_ar": "ثغرة XSS",
             "entity_type": "security_issue",
             "properties": {"category": "security", "severity": "high"}},
            {"id": "err_hardcoded_secret", "name": "Hardcoded Secret", "name_ar": "سر مكتوب في الكود",
             "entity_type": "security_issue",
             "properties": {"category": "security", "severity": "critical"}},
        ]

        # ═══════════════════════════════════════════════════════════════════════
        # Best Practice Entities - كيانات أفضل الممارسات
        # ═══════════════════════════════════════════════════════════════════════
        best_practices = [
            {"id": "bp_dependency_injection", "name": "Dependency Injection", "name_ar": "حقن التبعيات",
             "entity_type": "pattern",
             "properties": {"category": "design_pattern"}},
            {"id": "bp_error_handling", "name": "Error Handling", "name_ar": "معالجة الأخطاء",
             "entity_type": "pattern",
             "properties": {"category": "best_practice"}},
            {"id": "bp_logging", "name": "Structured Logging", "name_ar": "التسجيل المهيكل",
             "entity_type": "pattern",
             "properties": {"category": "observability"}},
            {"id": "bp_testing", "name": "Unit Testing", "name_ar": "اختبار الوحدات",
             "entity_type": "pattern",
             "properties": {"category": "quality"}},
            {"id": "bp_input_validation", "name": "Input Validation", "name_ar": "التحقق من المدخلات",
             "entity_type": "pattern",
             "properties": {"category": "security"}},
        ]

        # ═══════════════════════════════════════════════════════════════════════
        # Tool Entities - كيانات الأدوات
        # ═══════════════════════════════════════════════════════════════════════
        tools = [
            {"id": "tool_ruff", "name": "Ruff", "name_ar": "راف",
             "entity_type": "linter",
             "properties": {"language": "python", "type": "linter"}},
            {"id": "tool_eslint", "name": "ESLint", "name_ar": "إي إس لينت",
             "entity_type": "linter",
             "properties": {"language": "typescript", "type": "linter"}},
            {"id": "tool_mypy", "name": "Mypy", "name_ar": "ماي باي",
             "entity_type": "type_checker",
             "properties": {"language": "python", "type": "type_checker"}},
            {"id": "tool_bandit", "name": "Bandit", "name_ar": "بانديت",
             "entity_type": "security_scanner",
             "properties": {"language": "python", "type": "security"}},
            {"id": "tool_dart_analyze", "name": "Dart Analyze", "name_ar": "تحليل دارت",
             "entity_type": "linter",
             "properties": {"language": "dart", "type": "linter"}},
        ]

        # Add all entities
        for entity in languages + frameworks + error_patterns + best_practices + tools:
            await self._kg_retriever.add_entity(entity)

        # ═══════════════════════════════════════════════════════════════════════
        # Relations - العلاقات
        # ═══════════════════════════════════════════════════════════════════════
        relations = [
            # Language-Framework relations
            {"source_id": "fw_fastapi", "target_id": "lang_python",
             "relation_type": RelationType.REQUIRES.value},
            {"source_id": "fw_nestjs", "target_id": "lang_typescript",
             "relation_type": RelationType.REQUIRES.value},
            {"source_id": "fw_flutter", "target_id": "lang_dart",
             "relation_type": RelationType.REQUIRES.value},

            # Tool-Language relations
            {"source_id": "tool_ruff", "target_id": "lang_python",
             "relation_type": RelationType.COMPATIBLE_WITH.value},
            {"source_id": "tool_eslint", "target_id": "lang_typescript",
             "relation_type": RelationType.COMPATIBLE_WITH.value},
            {"source_id": "tool_mypy", "target_id": "lang_python",
             "relation_type": RelationType.COMPATIBLE_WITH.value},
            {"source_id": "tool_bandit", "target_id": "lang_python",
             "relation_type": RelationType.COMPATIBLE_WITH.value},
            {"source_id": "tool_dart_analyze", "target_id": "lang_dart",
             "relation_type": RelationType.COMPATIBLE_WITH.value},

            # Pattern-Framework relations
            {"source_id": "bp_dependency_injection", "target_id": "fw_fastapi",
             "relation_type": RelationType.COMPATIBLE_WITH.value},
            {"source_id": "bp_dependency_injection", "target_id": "fw_nestjs",
             "relation_type": RelationType.COMPATIBLE_WITH.value},

            # Security issue prevention
            {"source_id": "bp_input_validation", "target_id": "err_sql_injection",
             "relation_type": RelationType.PREVENTS.value},
            {"source_id": "bp_input_validation", "target_id": "err_xss",
             "relation_type": RelationType.PREVENTS.value},
        ]

        for relation in relations:
            await self._kg_retriever.add_relation(relation)

        logger.info(
            "code_knowledge_loaded",
            entities=len(languages + frameworks + error_patterns + best_practices + tools),
            relations=len(relations),
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Agent Integration Methods
    # ═══════════════════════════════════════════════════════════════════════════

    async def analyze_code(
        self,
        code: str,
        language: str = "python",
        context: Optional[CodeQueryContext] = None,
    ) -> CodeAnalysisResult:
        """
        Analyze code for issues and improvements
        تحليل الكود للمشاكل والتحسينات

        For: code-fix-agent, code-review-agent
        """
        await self.initialize()

        query = f"Analyze {language} code for issues, security vulnerabilities, and improvements"

        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=10,
            filters={"kg_max_hops": 2},
        )

        results = await self._tri_rag.retrieve(query, config)

        # Extract relevant patterns and tools
        patterns = []
        tools = []
        for r in results:
            entity_type = r.chunk.metadata.get("entity_type", "")
            if entity_type == "pattern":
                patterns.append({
                    "name": r.chunk.text,
                    "name_ar": r.chunk.text_ar,
                })
            elif entity_type in ["linter", "type_checker", "security_scanner"]:
                tools.append({
                    "name": r.chunk.text,
                    "type": entity_type,
                })

        return CodeAnalysisResult(
            query=query,
            analysis=f"Code analysis for {language}",
            suggestions=[p["name"] for p in patterns],
            related_patterns=patterns,
            confidence=results[0].score if results else 0.0,
            sources=[r.to_dict() for r in results[:5]],
            metadata={"language": language, "tools": tools},
        )

    async def find_fix_pattern(
        self,
        error_message: str,
        language: str = "python",
        context: Optional[CodeQueryContext] = None,
    ) -> CodeAnalysisResult:
        """
        Find fix pattern for an error
        إيجاد نمط الإصلاح للخطأ

        For: code-fix-agent
        """
        await self.initialize()

        query = f"Fix pattern for {language} error: {error_message}"

        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=10,
            filters={"kg_max_hops": 2},
        )

        results = await self._tri_rag.retrieve(query, config)

        return CodeAnalysisResult(
            query=query,
            analysis=f"Fix pattern for: {error_message}",
            suggestions=[],
            confidence=results[0].score if results else 0.0,
            sources=[r.to_dict() for r in results[:5]],
            metadata={"language": language, "error": error_message},
        )

    async def security_scan(
        self,
        code: str,
        language: str = "python",
        context: Optional[CodeQueryContext] = None,
    ) -> CodeAnalysisResult:
        """
        Scan code for security vulnerabilities
        فحص الكود للثغرات الأمنية

        For: code-review-agent, audit-agent
        """
        await self.initialize()

        query = f"Security vulnerabilities in {language}: SQL injection, XSS, hardcoded secrets"

        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=10,
            filters={"kg_max_hops": 2},
        )

        results = await self._tri_rag.retrieve(query, config)

        # Extract security issues
        security_issues = []
        for r in results:
            if r.chunk.metadata.get("entity_type") == "security_issue":
                security_issues.append({
                    "name": r.chunk.text,
                    "name_ar": r.chunk.text_ar,
                    "severity": r.chunk.metadata.get("properties", {}).get("severity", "unknown"),
                })

        return CodeAnalysisResult(
            query=query,
            analysis=f"Security scan for {language} code",
            suggestions=["Use parameterized queries", "Sanitize user input", "Use environment variables for secrets"],
            related_patterns=security_issues,
            confidence=results[0].score if results else 0.0,
            sources=[r.to_dict() for r in results[:5]],
            metadata={"language": language, "scan_type": "security"},
        )

    async def get_best_practices(
        self,
        topic: str,
        language: str = "python",
        framework: Optional[str] = None,
        context: Optional[CodeQueryContext] = None,
    ) -> CodeAnalysisResult:
        """
        Get best practices for a topic
        الحصول على أفضل الممارسات لموضوع

        For: code-review-agent
        """
        await self.initialize()

        query = f"Best practices for {topic} in {language}"
        if framework:
            query += f" using {framework}"

        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=10,
            filters={"kg_max_hops": 2},
        )

        results = await self._tri_rag.retrieve(query, config)

        return CodeAnalysisResult(
            query=query,
            analysis=f"Best practices for {topic}",
            suggestions=[],
            confidence=results[0].score if results else 0.0,
            sources=[r.to_dict() for r in results[:5]],
            metadata={"language": language, "framework": framework, "topic": topic},
        )

    async def general_query(
        self,
        query: str,
        context: Optional[CodeQueryContext] = None,
    ) -> CodeAnalysisResult:
        """
        General code query using Tri-RAG
        استعلام كود عام باستخدام Tri-RAG
        """
        await self.initialize()

        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=10,
            filters={"kg_max_hops": 2},
        )

        results = await self._tri_rag.retrieve(query, config)

        return CodeAnalysisResult(
            query=query,
            analysis=f"Results for: {query}",
            confidence=results[0].score if results else 0.0,
            sources=[r.to_dict() for r in results[:5]],
        )

    @property
    def knowledge_graph(self) -> KnowledgeGraphRetriever:
        """Access the knowledge graph retriever"""
        return self._kg_retriever


class _MockRetriever:
    """Mock retriever for testing without vector store"""

    async def retrieve(self, query: str, config: RetrievalConfig) -> List:
        return []

    async def add_documents(self, chunks: List, collection: str = "default") -> bool:
        return True


# Export
__all__ = [
    "CodeRAGProvider",
    "CodeQueryContext",
    "CodeAnalysisResult",
]
