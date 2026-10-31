"""Offline security contracts: pinned optional models and bound satellite SQL.

SQL functions are compiled from their actual source with only annotations and
framework decorators removed, avoiding service startup and external connections.
"""

import ast
import asyncio
import importlib.util
import logging
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
SERVICE = ROOT / "apps/services"


def source_function(path, name):
    tree = ast.parse(path.read_text())
    node = next(n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef) and n.name == name)
    node.decorator_list = []
    node.returns = None
    for arg in node.args.args:
        arg.annotation = None
    node.args.defaults = [ast.Constant(None) for _ in node.args.defaults]
    module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    namespace = {"logger": Mock()}
    exec(compile(module, str(path), "exec"), namespace)
    return namespace[name], namespace


def run_async(coroutine):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coroutine)
    finally:
        loop.close()


class Connection:
    def __init__(self):
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def fetch(self, sql, *args):
        self.calls.append((sql, args))
        return []

    async def fetchval(self, sql, *args):
        self.calls.append((sql, args))
        return 0

    def acquire(self):
        return self


class ModelRevisionContracts(unittest.TestCase):
    def setUp(self):
        path = SERVICE / "field-intelligence/src/models/agricultural_models.py"
        spec = importlib.util.spec_from_file_location("isolated_agricultural_models", path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_mutable_or_missing_revision_refuses_loading(self):
        transformers = types.SimpleNamespace(AutoTokenizer=Mock(), AutoModelForCausalLM=Mock(), pipeline=Mock())
        torch = types.SimpleNamespace(cuda=types.SimpleNamespace(is_available=lambda: False), float32="float32")
        for revision in ("", "main", "v1.0", "a" * 39, "z" * 40):
            with (
                self.subTest(revision=revision),
                patch.dict(os.environ, {"CROP_ADVISOR_MODEL": "org/model", "CROP_ADVISOR_REVISION": revision}),
                patch.dict(sys.modules, {"transformers": transformers, "torch": torch}),
            ):
                model = self.module.HFAdvisorModel()
                self.assertFalse(model.load())
                self.assertFalse(model.is_available())
        transformers.AutoTokenizer.from_pretrained.assert_not_called()
        transformers.AutoModelForCausalLM.from_pretrained.assert_not_called()

    def test_same_commit_pins_model_and_tokenizer(self):
        revision = "a" * 40
        tokenizer = Mock()
        model = Mock()
        transformers = types.SimpleNamespace(AutoTokenizer=tokenizer, AutoModelForCausalLM=model, pipeline=Mock())
        torch = types.SimpleNamespace(cuda=types.SimpleNamespace(is_available=lambda: False), float32="float32")
        with (
            patch.dict(os.environ, {"CROP_ADVISOR_MODEL": "org/model", "CROP_ADVISOR_REVISION": revision}),
            patch.dict(sys.modules, {"transformers": transformers, "torch": torch}),
        ):
            advisor = self.module.HFAdvisorModel()
            self.assertTrue(advisor.load())
            for loader in (tokenizer, model):
                self.assertEqual(loader.from_pretrained.call_args.kwargs["revision"], revision)
                self.assertIs(loader.from_pretrained.call_args.kwargs["trust_remote_code"], False)


class SatelliteSQLContracts(unittest.TestCase):
    def test_scheduler_search_and_status_are_bound(self):
        function, namespace = source_function(SERVICE / "vegetation-analysis-service/src/main.py", "get_scheduler_logs")
        connection = Connection()
        namespace["_db_pool"] = connection
        payload = "x'; DROP TABLE fields; --"
        run_async(function(period="30d", status="failed", search=payload, page=2, limit=25, user=None))
        self.assertEqual(len(connection.calls), 2)
        for sql, args in connection.calls:
            self.assertNotIn(payload, sql)
            self.assertEqual(args[:3], ("30", "failed", f"%{payload}%"))
        self.assertEqual(connection.calls[1][1][-2:], (25, 25))

    def test_scheduler_absent_filters_bind_nulls(self):
        function, namespace = source_function(SERVICE / "vegetation-analysis-service/src/main.py", "get_scheduler_logs")
        connection = Connection()
        namespace["_db_pool"] = connection
        run_async(function(period="7d", status="unrecognized", search=None, page=1, limit=10, user=None))
        self.assertEqual(connection.calls[0][1], ("7", None, None))

    def test_timeseries_identifiers_are_allowlisted(self):
        function, _ = source_function(
            SERVICE / "vegetation-analysis-service/src/satellite_storage.py", "get_timeseries"
        )
        for index in ("NDVI", "evi", "lai", "ndwi", "ndvi; DROP TABLE fields; --"):
            with self.subTest(index=index):
                connection = Connection()
                holder = types.SimpleNamespace(_pool=connection)
                run_async(function(holder, "tenant'", "field'", index, "2026-01-01", "2026-02-01"))
                sql, args = connection.calls[0]
                self.assertNotIn("DROP TABLE", sql)
                self.assertNotIn("tenant'", sql)
                self.assertNotIn("field'", sql)
                chosen = index.lower() if index.lower() in ("ndvi", "evi", "lai", "ndwi") else "ndvi"
                self.assertEqual(args, ("tenant'", "field'", chosen, "2026-01-01", "2026-02-01"))
                self.assertIn("CASE $3", sql)

    def test_acquisition_dates_are_optional_bound_parameters(self):
        function, _ = source_function(
            SERVICE / "vegetation-analysis-service/src/satellite_storage.py", "get_acquisition_plan"
        )
        for start, end in ((None, None), ("2026-01-01", None), (None, "2026-02-01"), ("2026-01-01", "2026-02-01")):
            with self.subTest(start=start, end=end):
                connection = Connection()
                run_async(function(types.SimpleNamespace(_pool=connection), "tenant'", "field'", start, end))
                sql, args = connection.calls[0]
                self.assertEqual(args, ("tenant'", "field'", start, end))
                self.assertNotIn("tenant'", sql)
                self.assertIn("$3::date IS NULL", sql)
                self.assertIn("$4::date IS NULL", sql)


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    unittest.main()
