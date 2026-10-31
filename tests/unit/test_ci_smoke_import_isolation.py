"""Keep fresh-import smoke checks from invalidating collected unit-test imports."""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch, sentinel
from uuid import uuid4

import pytest

from tests.smoke import test_branch_imports as smoke_tests

pytestmark = pytest.mark.unit


def _probe(module_name: str) -> None:
    smoke_tests.TestBranchModuleImports().test_module_imports_without_error(module_name)


@pytest.fixture
def probe_module(tmp_path, monkeypatch):
    name = f"_sahool_ci_import_probe_{uuid4().hex}"
    path = tmp_path / f"{name}.py"
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join(filter(None, [str(tmp_path), os.environ.get("PYTHONPATH")])))
    yield name, path
    for module_name in tuple(sys.modules):
        if module_name == name or module_name.startswith(name + "_"):
            sys.modules.pop(module_name, None)


@pytest.mark.asyncio
@pytest.mark.parametrize("function_name", ["generate_text", "generate_with_ollama_fallback"])
async def test_smoke_probe_preserves_module_identity_and_collected_function_mocks(function_name):
    """The original cache eviction breaks both aliases after pytest collection."""
    provider = importlib.import_module("shared.ai.llm_provider")
    parent = importlib.import_module("shared.ai")
    collected_function = getattr(provider, function_name)
    original_globals = collected_function.__globals__

    _probe("shared.ai.llm_provider")

    assert sys.modules["shared.ai.llm_provider"] is provider
    assert parent.llm_provider is provider
    assert collected_function.__globals__ is original_globals is provider.__dict__
    manager = SimpleNamespace(generate=AsyncMock(return_value=sentinel.response))
    with patch("shared.ai.llm_provider.get_llm_manager", return_value=manager) as get_manager:
        assert await collected_function("local regression prompt") is sentinel.response
    get_manager.assert_called_once_with("sahool")
    manager.generate.assert_awaited_once()


def test_probe_executes_fresh_source_without_replacing_cached_parent_module(probe_module):
    name, path = probe_module
    path.write_text("VALUE = 'original'\n", encoding="utf-8")
    cached = importlib.import_module(name)
    path.write_text("raise RuntimeError('fresh import was actually executed')\n", encoding="utf-8")

    with pytest.raises(pytest.fail.Exception, match="fresh import was actually executed"):
        _probe(name)
    assert sys.modules[name] is cached
    assert cached.VALUE == "original"


def test_missing_optional_dependency_retains_existing_skip_semantics(probe_module):
    name, path = probe_module
    path.write_text("import _sahool_intentionally_absent_optional_dependency\n", encoding="utf-8")
    with pytest.raises(pytest.skip.Exception, match="missing dependency"):
        _probe(name)


def test_actual_circular_import_still_fails(probe_module):
    name, path = probe_module
    peer = name + "_peer"
    path.write_text(f"from {peer} import VALUE\n", encoding="utf-8")
    path.with_name(peer + ".py").write_text(f"from {name} import VALUE\n", encoding="utf-8")
    with pytest.raises(pytest.fail.Exception, match="Circular import"):
        _probe(name)


@pytest.mark.parametrize("exception", ["NameError", "AttributeError", "RuntimeError"])
def test_internal_import_errors_are_failures_not_optional_skips(probe_module, exception):
    name, path = probe_module
    path.write_text(f"raise {exception}('broken internal import')\n", encoding="utf-8")
    with pytest.raises(pytest.fail.Exception, match=f"{exception}: broken internal import"):
        _probe(name)


@pytest.mark.parametrize(("exit_code", "message"), [(0, "completion report"), (7, "exited with 7")])
def test_process_exit_cannot_masquerade_as_successful_import(probe_module, exit_code, message):
    name, path = probe_module
    path.write_text(f"raise SystemExit({exit_code})\n", encoding="utf-8")
    with pytest.raises(pytest.fail.Exception, match=message):
        _probe(name)


def test_import_output_does_not_hide_completion_report(probe_module):
    name, path = probe_module
    path.write_text("print('module startup diagnostic')\nVALUE = 1\n", encoding="utf-8")
    _probe(name)


def test_import_timeout_is_bounded_and_fails(monkeypatch):
    def timed_out(command, **kwargs):
        assert kwargs["timeout"] == 30
        raise subprocess.TimeoutExpired(command, kwargs["timeout"])

    monkeypatch.setattr(smoke_tests.subprocess, "run", timed_out)
    with pytest.raises(pytest.fail.Exception, match="timed out after 30 seconds"):
        _probe("shared.ai.llm_provider")
