"""Offline model-loading security and compatibility for the two RAG consumers.

Run with the AI service dependencies installed. All models are generated locally;
these checks require neither downloaded model weights nor a running provider.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest
from sentence_transformers import SentenceTransformer, models

pytestmark = pytest.mark.unit
REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture(autouse=True)
def offline_models(monkeypatch, tmp_path):
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("HF_HOME", str(tmp_path / "hub-cache"))
    monkeypatch.delenv("COPILOT_EMBEDDING_MODEL", raising=False)
    monkeypatch.delenv("COPILOT_EMBEDDING_PROVIDER", raising=False)


@pytest.fixture
def local_builtin_model(tmp_path):
    model = SentenceTransformer(modules=[models.BoW(vocab=["wheat", "water", "قمح"])], device="cpu")
    path = tmp_path / "builtin-model"
    model.save(str(path))
    return path, model.encode(["wheat water", "قمح"], convert_to_numpy=True)


@pytest.fixture
def local_custom_model(tmp_path):
    path = tmp_path / "custom-model"
    path.mkdir()
    marker = tmp_path / "custom-module-executed"
    (path / "modeling_probe.py").write_text(
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text('executed')\n"
        "class Probe:\n"
        "    @classmethod\n"
        "    def load(cls, *args, **kwargs):\n"
        "        raise RuntimeError('untrusted probe module was loaded')\n",
        encoding="utf-8",
    )
    (path / "modules.json").write_text(
        json.dumps([{"idx": 0, "name": "0", "path": "", "type": "modeling_probe.Probe"}]), encoding="utf-8"
    )
    return path, marker


def test_untrusted_local_model_cannot_execute_custom_python(local_custom_model):
    """CVE-2026-68770: False must prevent execution, not merely emit a warning."""
    path, marker = local_custom_model
    try:
        with pytest.raises(ValueError, match="trust_remote_code=True"):
            SentenceTransformer(str(path), trust_remote_code=False, local_files_only=True, device="cpu")
    finally:
        assert not marker.exists(), "A custom local module executed despite trust_remote_code=False"


def test_explicitly_trusted_custom_module_control_is_reachable(local_custom_model):
    """Prove that the rejected fixture actually reaches the dynamic loader."""
    path, marker = local_custom_model
    with pytest.raises(RuntimeError, match="untrusted probe module was loaded"):
        SentenceTransformer(str(path), trust_remote_code=True, local_files_only=True, device="cpu")
    assert marker.read_text() == "executed"


def test_standard_local_model_still_loads_with_trust_disabled(local_builtin_model):
    path, expected = local_builtin_model
    model = SentenceTransformer(str(path), trust_remote_code=False, local_files_only=True, device="cpu")
    np.testing.assert_array_equal(model.encode(["wheat water", "قمح"], convert_to_numpy=True), expected)


def _load_source_module(monkeypatch, name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    return module


def test_ai_advisor_real_embeddings_manager_loads_and_encodes(local_builtin_model, monkeypatch):
    path, expected = local_builtin_model
    namespace = "_sahool_dependency_ai_advisor"
    source = REPO_ROOT / "apps/services/ai-advisor/src"
    # Isolate this service's relative imports from other services also named src.
    for name, location in [(namespace, source), (namespace + ".rag", source / "rag")]:
        package = ModuleType(name)
        package.__path__ = [str(location)]
        monkeypatch.setitem(sys.modules, name, package)
    _load_source_module(monkeypatch, namespace + ".config", source / "config.py")
    module = _load_source_module(monkeypatch, namespace + ".rag.embeddings", source / "rag/embeddings.py")
    manager = module.EmbeddingsManager(model_name=str(path), device="cpu")
    assert manager.embedding_dimension == 3
    np.testing.assert_array_equal(manager.encode(["wheat water", "قمح"]), expected)
    np.testing.assert_array_equal(manager.encode_query("wheat water"), expected[0])


@pytest.mark.asyncio
async def test_copilot_real_embedding_service_uses_the_local_model(local_builtin_model, monkeypatch):
    path, expected = local_builtin_model
    module = _load_source_module(
        monkeypatch,
        "_sahool_dependency_copilot_embeddings",
        REPO_ROOT / "apps/services/copilot-api/src/rag/embeddings.py",
    )
    service = module.EmbeddingService(module.EmbeddingConfig(model=str(path), cache_enabled=True))
    assert await service.initialize()
    assert service._model is not None, "The compatibility check must not pass through the random fallback"
    result = await service.embed("wheat water")
    assert result.dimension == 3
    assert result.provider == "sentence_transformers"
    np.testing.assert_array_equal(result.embedding, expected[0])
    repeated = await service.embed("wheat water")
    assert repeated.cached
    np.testing.assert_array_equal(repeated.embedding, expected[0])
