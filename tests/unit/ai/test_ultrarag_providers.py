# ═══════════════════════════════════════════════════════════════════════════════
# UltraRAG Providers Tests
# اختبارات مزودات UltraRAG
# ═══════════════════════════════════════════════════════════════════════════════

import pytest
from unittest.mock import AsyncMock, MagicMock

from shared.ai.ultrarag.providers import AgriRAGProvider, CodeRAGProvider
from shared.ai.ultrarag.providers.agri_provider import AgriQueryContext, AgriAdvisoryResult
from shared.ai.ultrarag.providers.code_provider import CodeQueryContext, CodeAnalysisResult
from shared.ai.ultrarag.models import TriRAGConfig, EntityType, RelationType


# ═══════════════════════════════════════════════════════════════════════════════
# AgriRAGProvider Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgriRAGProvider:
    """Tests for AgriRAGProvider"""

    @pytest.fixture
    def provider(self):
        """Create AgriRAGProvider instance"""
        return AgriRAGProvider()

    @pytest.fixture
    def custom_config_provider(self):
        """Create AgriRAGProvider with custom config"""
        config = TriRAGConfig(
            dense_weight=0.5,
            sparse_weight=0.3,
            kg_weight=0.2,
            kg_max_hops=3,
        )
        return AgriRAGProvider(config=config)

    @pytest.mark.asyncio
    async def test_initialize(self, provider):
        """Test provider initialization"""
        await provider.initialize()
        assert provider._initialized is True
        assert provider._kg_retriever is not None
        assert provider._tri_rag is not None

    @pytest.mark.asyncio
    async def test_knowledge_graph_loaded(self, provider):
        """Test agricultural knowledge graph is loaded"""
        await provider.initialize()

        # Check entities exist
        entities = provider._kg_retriever._entities
        assert len(entities) > 0

        # Check for crop entities
        crop_ids = [eid for eid in entities if eid.startswith("crop_")]
        assert len(crop_ids) >= 5  # wheat, barley, date_palm, tomato, cucumber, alfalfa

        # Check for disease entities
        disease_ids = [eid for eid in entities if eid.startswith("disease_")]
        assert len(disease_ids) >= 4

        # Check for treatment entities
        treat_ids = [eid for eid in entities if eid.startswith("treat_")]
        assert len(treat_ids) >= 5

    @pytest.mark.asyncio
    async def test_diagnose_disease(self, provider):
        """Test disease diagnosis"""
        result = await provider.diagnose_disease(
            symptoms="yellowing leaves and rust spots",
            crop_type="wheat",
        )

        assert isinstance(result, AgriAdvisoryResult)
        assert result.query is not None
        assert "wheat" in result.query.lower() or "disease" in result.query.lower()
        assert result.advisory is not None
        assert result.advisory_ar is not None

    @pytest.mark.asyncio
    async def test_recommend_irrigation(self, provider):
        """Test irrigation recommendation"""
        result = await provider.recommend_irrigation(
            crop_type="wheat",
            growth_stage="tillering",
            soil_moisture=35.0,
        )

        assert isinstance(result, AgriAdvisoryResult)
        assert "wheat" in result.query.lower()
        assert "tillering" in result.query.lower()
        assert result.metadata.get("soil_moisture") == 35.0

    @pytest.mark.asyncio
    async def test_recommend_fertilizer(self, provider):
        """Test fertilizer recommendation"""
        result = await provider.recommend_fertilizer(
            crop_type="wheat",
            growth_stage="tillering",
            soil_analysis={"nitrogen": 18, "phosphorus": 25},
        )

        assert isinstance(result, AgriAdvisoryResult)
        assert "wheat" in result.query.lower()
        assert result.metadata.get("soil_analysis") is not None

    @pytest.mark.asyncio
    async def test_predict_yield(self, provider):
        """Test yield prediction"""
        result = await provider.predict_yield(
            crop_type="wheat",
            area_hectares=10.5,
            growth_stage="heading",
        )

        assert isinstance(result, AgriAdvisoryResult)
        assert "wheat" in result.query.lower()
        assert result.metadata.get("area_hectares") == 10.5

    @pytest.mark.asyncio
    async def test_general_query(self, provider):
        """Test general agricultural query"""
        result = await provider.general_query(
            query="Best practices for wheat irrigation in winter",
        )

        assert isinstance(result, AgriAdvisoryResult)
        assert result.query is not None

    def test_custom_config(self, custom_config_provider):
        """Test custom configuration"""
        assert custom_config_provider.config.dense_weight == 0.5
        assert custom_config_provider.config.sparse_weight == 0.3
        assert custom_config_provider.config.kg_weight == 0.2
        assert custom_config_provider.config.kg_max_hops == 3


# ═══════════════════════════════════════════════════════════════════════════════
# CodeRAGProvider Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestCodeRAGProvider:
    """Tests for CodeRAGProvider"""

    @pytest.fixture
    def provider(self):
        """Create CodeRAGProvider instance"""
        return CodeRAGProvider()

    @pytest.mark.asyncio
    async def test_initialize(self, provider):
        """Test provider initialization"""
        await provider.initialize()
        assert provider._initialized is True
        assert provider._kg_retriever is not None
        assert provider._tri_rag is not None

    @pytest.mark.asyncio
    async def test_knowledge_graph_loaded(self, provider):
        """Test code knowledge graph is loaded"""
        await provider.initialize()

        entities = provider._kg_retriever._entities
        assert len(entities) > 0

        # Check for language entities
        lang_ids = [eid for eid in entities if eid.startswith("lang_")]
        assert len(lang_ids) >= 3  # python, typescript, dart

        # Check for framework entities
        fw_ids = [eid for eid in entities if eid.startswith("fw_")]
        assert len(fw_ids) >= 4

        # Check for tool entities
        tool_ids = [eid for eid in entities if eid.startswith("tool_")]
        assert len(tool_ids) >= 4

    @pytest.mark.asyncio
    async def test_analyze_code(self, provider):
        """Test code analysis"""
        result = await provider.analyze_code(
            code="def foo(): pass",
            language="python",
        )

        assert isinstance(result, CodeAnalysisResult)
        assert "python" in result.query.lower()
        assert result.analysis is not None

    @pytest.mark.asyncio
    async def test_find_fix_pattern(self, provider):
        """Test fix pattern finding"""
        result = await provider.find_fix_pattern(
            error_message="NameError: name 'foo' is not defined",
            language="python",
        )

        assert isinstance(result, CodeAnalysisResult)
        assert result.metadata.get("error") is not None

    @pytest.mark.asyncio
    async def test_security_scan(self, provider):
        """Test security scan"""
        result = await provider.security_scan(
            code="cursor.execute('SELECT * FROM users WHERE id = ' + user_id)",
            language="python",
        )

        assert isinstance(result, CodeAnalysisResult)
        assert result.metadata.get("scan_type") == "security"

    @pytest.mark.asyncio
    async def test_get_best_practices(self, provider):
        """Test best practices retrieval"""
        result = await provider.get_best_practices(
            topic="error handling",
            language="python",
            framework="fastapi",
        )

        assert isinstance(result, CodeAnalysisResult)
        assert result.metadata.get("topic") == "error handling"
        assert result.metadata.get("framework") == "fastapi"

    @pytest.mark.asyncio
    async def test_general_query(self, provider):
        """Test general code query"""
        result = await provider.general_query(
            query="How to implement dependency injection in FastAPI",
        )

        assert isinstance(result, CodeAnalysisResult)
        assert result.query is not None


# ═══════════════════════════════════════════════════════════════════════════════
# AgriQueryContext Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgriQueryContext:
    """Tests for AgriQueryContext"""

    def test_default_context(self):
        """Test default context creation"""
        ctx = AgriQueryContext()
        assert ctx.language == "both"
        assert ctx.crop_type is None
        assert ctx.region is None

    def test_custom_context(self):
        """Test custom context creation"""
        ctx = AgriQueryContext(
            crop_type="wheat",
            growth_stage="tillering",
            region="riyadh",
            language="ar",
        )
        assert ctx.crop_type == "wheat"
        assert ctx.growth_stage == "tillering"
        assert ctx.region == "riyadh"
        assert ctx.language == "ar"


# ═══════════════════════════════════════════════════════════════════════════════
# CodeQueryContext Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestCodeQueryContext:
    """Tests for CodeQueryContext"""

    def test_default_context(self):
        """Test default context creation"""
        ctx = CodeQueryContext()
        assert ctx.language == "python"
        assert ctx.file_path is None

    def test_custom_context(self):
        """Test custom context creation"""
        ctx = CodeQueryContext(
            language="typescript",
            file_path="/app/src/main.ts",
            project_type="nestjs",
            framework="nestjs",
        )
        assert ctx.language == "typescript"
        assert ctx.file_path == "/app/src/main.ts"
        assert ctx.project_type == "nestjs"


# ═══════════════════════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestProvidersIntegration:
    """Integration tests for providers"""

    @pytest.mark.asyncio
    async def test_agri_provider_multiple_queries(self):
        """Test multiple queries to AgriRAGProvider"""
        provider = AgriRAGProvider()
        await provider.initialize()

        # Query 1: Disease diagnosis
        r1 = await provider.diagnose_disease("rust spots", "wheat")
        assert r1.confidence >= 0

        # Query 2: Irrigation
        r2 = await provider.recommend_irrigation("barley", "heading")
        assert r2.confidence >= 0

        # Query 3: Fertilizer
        r3 = await provider.recommend_fertilizer("tomato", "flowering")
        assert r3.confidence >= 0

    @pytest.mark.asyncio
    async def test_code_provider_multiple_queries(self):
        """Test multiple queries to CodeRAGProvider"""
        provider = CodeRAGProvider()
        await provider.initialize()

        # Query 1: Python analysis
        r1 = await provider.analyze_code("def foo(): pass", "python")
        assert r1.analysis is not None

        # Query 2: TypeScript analysis
        r2 = await provider.analyze_code("const x: number = 1;", "typescript")
        assert r2.analysis is not None

        # Query 3: Security scan
        r3 = await provider.security_scan("password = '123456'", "python")
        assert r3.analysis is not None

    @pytest.mark.asyncio
    async def test_both_providers_together(self):
        """Test both providers can work together"""
        agri = AgriRAGProvider()
        code = CodeRAGProvider()

        await agri.initialize()
        await code.initialize()

        # Both should be initialized independently
        assert agri._initialized is True
        assert code._initialized is True

        # Both should have separate knowledge graphs
        assert len(agri._kg_retriever._entities) > 0
        assert len(code._kg_retriever._entities) > 0

        # Entities should be different
        agri_ids = set(agri._kg_retriever._entities.keys())
        code_ids = set(code._kg_retriever._entities.keys())
        assert len(agri_ids & code_ids) == 0  # No overlap
