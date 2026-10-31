"""Regression checks for annotation resolution and lazy model imports."""

import asyncio
import importlib
import sys
import types
import unittest
from pathlib import Path
from typing import get_type_hints
from unittest.mock import AsyncMock, patch

SOURCE = Path(__file__).resolve().parents[1] / "src"
PACKAGE = "_field_intelligence_type_contracts"


class ModelTypeContracts(unittest.TestCase):
    def setUp(self):
        package = types.ModuleType(PACKAGE)
        package.__path__ = [str(SOURCE)]
        sys.modules[PACKAGE] = package
        self.addCleanup(self.clean_modules)

    @staticmethod
    def clean_modules():
        for name in list(sys.modules):
            if name == PACKAGE or name.startswith(PACKAGE + "."):
                del sys.modules[name]

    def test_weather_annotations_resolve_to_request_models(self):
        api = importlib.import_module(PACKAGE + ".api.ai_analysis")
        schemas = importlib.import_module(PACKAGE + ".models.analysis_schemas")
        hints = get_type_hints(api._build_meteo_block)
        self.assertEqual(hints["meteo"], schemas.MeteoPayload | None)
        self.assertEqual(hints["weather"], schemas.WeatherPayload | None)
        self.assertEqual(hints["return"], str)

    def test_weather_block_handles_absent_inputs(self):
        api = importlib.import_module(PACKAGE + ".api.ai_analysis")
        self.assertIsInstance(api._build_meteo_block(None, None), str)

    def test_request_and_provider_text_cannot_inject_log_lines(self):
        api = importlib.import_module(PACKAGE + ".api.ai_analysis")
        forged = "field\r\nFORGED_EVENT"
        req = api.AnalyzeFieldRequest(
            field=api.FieldInfo(id=forged, name="Field", lat=16.0, lng=45.0),
            cdse=api.CdseStats(indice="NDVI", value=0.4),
            indice=forged,
        )
        with (
            patch.dict(api.os.environ, {"OPENROUTER_API_KEY": "test-only"}),
            patch.object(api, "_run_agent", new=AsyncMock(side_effect=RuntimeError(forged))),
            self.assertLogs(api.logger, level="INFO") as captured,
            self.assertRaises(api.HTTPException),
        ):
            asyncio.run(api.analyze_field(req))
        self.assertGreaterEqual(len(captured.records), 2)
        for record in captured.records:
            message = record.getMessage()
            self.assertNotIn("FORGED_EVENT", message)
            self.assertNotIn("\r", message)
            self.assertNotIn("\n", message)

    def test_importing_loader_does_not_import_model_implementations(self):
        loader = importlib.import_module(PACKAGE + ".services.model_loader")
        self.assertNotIn(PACKAGE + ".models.agricultural_models", sys.modules)
        self.assertIsNone(loader._agri_scorer)
        self.assertIsNone(loader._hf_advisor)
        self.assertIsNone(loader._nllb_translator)


if __name__ == "__main__":
    unittest.main()
