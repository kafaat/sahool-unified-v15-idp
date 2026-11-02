"""Exercise upgraded AI SDKs against local transports and an in-memory Qdrant.

Run explicitly with the constrained AI dependencies installed. No provider API,
model download, external database, or fallback search is used for acceptance.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import socket
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from uuid import UUID

import anthropic
import httpx2
import numpy as np
import pytest
from langchain_anthropic import chat_models as anthropic_chat_models
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

ROOT = Path(__file__).resolve().parents[2]


def _load(monkeypatch, name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    return module


def _packages(monkeypatch, name, source, subpackages):
    for suffix in ["", *subpackages]:
        module = ModuleType(name + suffix)
        module.__path__ = [str(source / suffix.lstrip(".").replace(".", "/"))]
        monkeypatch.setitem(sys.modules, module.__name__, module)


@pytest.fixture
def qdrant():
    client = QdrantClient(":memory:")
    try:
        yield client
    finally:
        client.close()


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def reject(*args, **kwargs):
        raise AssertionError("SDK acceptance tests must use local transports")

    monkeypatch.setattr(socket.socket, "connect", reject)
    monkeypatch.setattr(socket.socket, "connect_ex", reject)


@pytest.fixture
def advisor(monkeypatch, qdrant):
    source = ROOT / "apps/services/ai-advisor/src"
    name = "_sdk_advisor"
    _packages(monkeypatch, name, source, [".rag", ".llm", ".monitoring"])
    module = _load(monkeypatch, name + ".rag.retriever", source / "rag/retriever.py")
    monkeypatch.setattr(module, "QdrantClient", lambda **kwargs: qdrant)
    embeddings = SimpleNamespace(
        embedding_dimension=3,
        encode_query=lambda text: np.array([1.0, 0.0, 0.0]),
        encode_documents=lambda texts: np.array([[1.0, 0.0, 0.0] for _ in texts]),
    )
    retriever = module.KnowledgeRetriever(embeddings_manager=embeddings, collection_name="advisor")
    assert retriever.add_documents(
        ["wheat A", "wheat B", "barley A"],
        [
            {"tenant_id": "A", "crop": "wheat"},
            {"tenant_id": "B", "crop": "wheat"},
            {"tenant_id": "A", "crop": "barley"},
        ],
        [str(UUID(int=value)) for value in (1, 2, 3)],
    )
    return retriever


def test_advisor_qdrant_retrieval_keeps_tenant_and_metadata_filters(advisor):
    hits = advisor.retrieve("wheat", tenant_id="A", filters={"crop": "wheat"}, top_k=1)
    assert [hit.content for hit in hits] == ["wheat A"]
    assert hits[0].score == pytest.approx(1.0)
    assert advisor.retrieve("wheat", tenant_id="missing") == []
    assert advisor.retrieve("wheat", tenant_id="A", score_threshold=1.1) == []


def test_advisor_qdrant_collection_statistics(advisor):
    stats = advisor.get_collection_info()
    assert "error" not in stats
    assert stats["points_count"] == stats["vectors_count"] == 3


@pytest.fixture
def copilot(monkeypatch, qdrant):
    source = ROOT / "apps/services/copilot-api/src"
    _packages(monkeypatch, "_sdk_copilot", source, [".rag"])
    module = _load(monkeypatch, "_sdk_copilot.rag.service", source / "rag/service.py")

    async def embed(text, tenant_id):
        return SimpleNamespace(embedding=[1.0, 0.0, 0.0])

    embeddings = SimpleNamespace(
        embed=embed, dimension=3, config=SimpleNamespace(provider=SimpleNamespace(value="local-test"))
    )
    service = module.CopilotRAGService(module.RAGConfig(qdrant_collection="copilot"), embedding_service=embeddings)
    qdrant.create_collection("copilot", vectors_config=VectorParams(size=3, distance=Distance.COSINE))
    service._qdrant_client = qdrant
    service._qdrant_available = service._initialized = True
    return service


@pytest.mark.asyncio
async def test_copilot_qdrant_search_cannot_pass_via_keyword_fallback(copilot):
    await copilot.add_document("wheat A", metadata={"crop": "wheat"}, tenant_id="A")
    await copilot.add_document("wheat B", metadata={"crop": "wheat"}, tenant_id="B")
    await copilot.add_document("barley A", metadata={"crop": "barley"}, tenant_id="A")
    copilot._documents.clear()  # A broken SDK call must not pass through the in-memory fallback.
    hits = await copilot.search("wheat", tenant_id="A", metadata_filter={"crop": "wheat"}, top_k=1)
    assert [hit.document.text for hit in hits] == ["wheat A"]
    assert hits[0].match_type == "semantic" and hits[0].score == pytest.approx(1.0)
    assert await copilot.search("wheat", tenant_id="missing") == []
    copilot.config.min_score_threshold = 1.1
    assert await copilot.search("wheat", tenant_id="A") == []


@pytest.mark.asyncio
async def test_copilot_qdrant_collection_statistics(copilot):
    await copilot.add_document("wheat A", tenant_id="A")
    stats = await copilot.get_stats()
    assert stats["qdrant_points_count"] == stats["qdrant_vectors_count"] == 1


@pytest.mark.asyncio
async def test_shared_qdrant_backend_preserves_vectors_ranks_and_filters(monkeypatch, qdrant):
    module = _load(monkeypatch, "_sdk_vector_store", ROOT / "shared/ai/vector_store.py")
    backend = module.QdrantBackend()
    backend._client = qdrant
    await backend.create_collection("shared", 3, module.DistanceMetric.COSINE)
    await backend.insert(
        [
            module.VectorDocument(str(UUID(int=index)), vector, content=text, metadata={"tenant_id": tenant})
            for index, vector, text, tenant in [
                (1, [1.0, 0.0, 0.0], "exact A", "A"),
                (2, [1.0, 0.0, 0.0], "exact B", "B"),
                (3, [0.8, 0.6, 0.0], "similar A", "A"),
            ]
        ],
        "shared",
    )
    hits = await backend.search([1.0, 0.0, 0.0], "shared", top_k=2, filter={"tenant_id": "A"})
    assert [hit.content for hit in hits] == ["exact A", "similar A"]
    assert [hit.rank for hit in hits] == [1, 2]
    assert hits[0].document.vector == [1.0, 0.0, 0.0]
    assert hits[0].score == pytest.approx(1.0) and hits[0].distance == pytest.approx(0.0)
    assert await backend.search([1.0, 0.0, 0.0], "shared", filter={"tenant_id": "missing"}) == []


@pytest.fixture
def anthropic_transport(monkeypatch):
    state = SimpleNamespace(requests=[], headers=[], text="wheat advisory")

    def reply(request):
        payload = json.loads(request.content)
        state.requests.append(payload)
        state.headers.append(dict(request.headers))
        return httpx2.Response(
            200,
            json={
                "id": "msg_local_sdk_test",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": state.text}],
                "model": payload["model"],
                "stop_reason": "end_turn",
                "stop_sequence": None,
                "usage": {"input_tokens": 10, "output_tokens": 4},
            },
        )

    transport = httpx2.MockTransport(reply)
    real_sync, real_async = anthropic.Anthropic, anthropic.AsyncAnthropic
    monkeypatch.setattr(
        anthropic, "Anthropic", lambda **kwargs: real_sync(**kwargs, http_client=httpx2.Client(transport=transport))
    )
    monkeypatch.setattr(
        anthropic,
        "AsyncAnthropic",
        lambda **kwargs: real_async(**kwargs, http_client=httpx2.AsyncClient(transport=transport)),
    )
    monkeypatch.setattr(
        anthropic_chat_models, "_get_default_httpx_client", lambda **kwargs: httpx2.Client(transport=transport)
    )
    monkeypatch.setattr(
        anthropic_chat_models,
        "_get_default_async_httpx_client",
        lambda **kwargs: httpx2.AsyncClient(transport=transport),
    )
    monkeypatch.setenv("ANTHROPIC_API_KEY", "local-test-key")
    monkeypatch.setenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    monkeypatch.setenv("MAX_TOKENS", "4096")
    monkeypatch.setenv("TEMPERATURE", "0.7")
    return state


def _assert_anthropic_protocol(state):
    assert len(state.requests) == 1
    # SDK 2 defaults to an API that rejects sampling parameters. Preserve the
    # supported version explicitly, as required by Anthropic's migration guide.
    assert state.headers[0]["anthropic-version"] == "2023-06-01"
    assert state.headers[0]["authorization"] == "Bearer local-test-key"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "options",
    [{}, {"model": "claude-sonnet-4-20250514", "max_tokens": 256, "temperature": 0.2}],
)
async def test_advisor_real_anthropic_sdk_request_and_response(monkeypatch, anthropic_transport, options):
    source = ROOT / "apps/services/ai-advisor/src"
    _packages(monkeypatch, "_sdk_advisor_llm", source, [".llm", ".monitoring"])
    module = _load(monkeypatch, "_sdk_advisor_llm.llm.multi_provider", source / "llm/multi_provider.py")
    provider = module.AnthropicProvider()
    try:
        result = await provider.chat(
            [module.LLMMessage("system", "farm adviser"), module.LLMMessage("user", "wheat")], **options
        )
        assert result.content == "wheat advisory" and result.tokens_used == 14
        _assert_anthropic_protocol(anthropic_transport)
        assert anthropic_transport.requests[0] == {
            "model": options.get("model", "claude-3-5-sonnet-20241022"),
            "max_tokens": options.get("max_tokens", 4096),
            "temperature": options.get("temperature", 0.7),
            "system": "farm adviser",
            "messages": [{"role": "user", "content": "wheat"}],
        }
        await asyncio.sleep(0)  # Allow the source's local usage-accounting task to finish.
    finally:
        await provider._client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("consumer", ["agent", "supervisor"])
async def test_langchain_consumers_keep_configured_sampling(monkeypatch, anthropic_transport, consumer):
    source = ROOT / "apps/services/ai-advisor/src"
    name = "_sdk_advisor_agents"
    _packages(monkeypatch, name, source, [".agents", ".orchestration"])
    base = _load(monkeypatch, name + ".agents.base_agent", source / "agents/base_agent.py")

    class LocalAgent(base.BaseAgent):
        def get_system_prompt(self):
            return "farm adviser"

    if consumer == "agent":
        instance = LocalAgent(name="local", role="farm adviser")
    else:
        monkeypatch.setattr(sys.modules[name + ".agents"], "BaseAgent", base.BaseAgent, raising=False)
        module = _load(monkeypatch, name + ".orchestration.supervisor", source / "orchestration/supervisor.py")
        instance = module.Supervisor(agents={})
        anthropic_transport.text = json.dumps(
            {"agents_needed": [], "reasoning": "Local fixture", "query_breakdown": {}}
        )
    try:
        if consumer == "agent":
            result = await instance.think("wheat", use_rag=False)
            assert result["response"] == "wheat advisory"
            assert instance.conversation_memory.get_messages()[-1]["content"] == "wheat advisory"
        else:
            result = await instance.route_query("wheat")
            assert result["reasoning"] == "Local fixture"
        _assert_anthropic_protocol(anthropic_transport)
        request = anthropic_transport.requests[0]
        assert request["model"] == "claude-3-5-sonnet-20241022"
        assert request["max_tokens"] == 4096
        assert request["temperature"] == (0.7 if consumer == "agent" else 0.3)
        assert request["messages"] == [
            {"role": "user", "content": "wheat" if consumer == "agent" else "Query: wheat\n\nContext: {}"}
        ]
    finally:
        await instance.llm._async_client.close()
        instance.llm._client.close()


@pytest.mark.asyncio
async def test_ground_vision_real_anthropic_sdk_images_and_structured_response(monkeypatch, anthropic_transport):
    source = ROOT / "apps/services/ground-vision-service/src"
    _packages(monkeypatch, "_sdk_ground", source, [".intelligence", ".core", ".models"])
    module = _load(monkeypatch, "_sdk_ground.intelligence.mllm_reasoner", source / "intelligence/mllm_reasoner.py")
    anthropic_transport.text = json.dumps(
        {
            "crop_type": "wheat",
            "crop_type_ar": "قمح",
            "growth_stage": "vegetative",
            "growth_stage_ar": "نمو خضري",
            "confidence": 0.9,
            "reasoning": "Local fixture",
            "reasoning_ar": "بيانات اختبار محلية",
        }
    )
    provider = module.AnthropicProvider(api_key="local-test-key")
    try:
        result = await provider.analyze("wheat", [{"data": "aW1hZ2U=", "timestamp": "2026-11-02"}], module.LLMResponse)
        assert result.crop_type == "wheat" and result.confidence == 0.9
        _assert_anthropic_protocol(anthropic_transport)
        assert anthropic_transport.requests[0] == {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {"type": "base64", "media_type": "image/jpeg", "data": "aW1hZ2U="},
                        },
                        {"type": "text", "text": "[Frame timestamp: 2026-11-02]"},
                        {"type": "text", "text": "wheat"},
                    ],
                }
            ],
        }
    finally:
        await provider.client.close()


def test_scipy_and_numpy_linear_algebra_runtime():
    from scipy.linalg import solve

    coefficients = np.array([[3.0, 1.0], [1.0, 2.0]])
    np.testing.assert_allclose(coefficients @ solve(coefficients, [9.0, 8.0]), [9.0, 8.0])
