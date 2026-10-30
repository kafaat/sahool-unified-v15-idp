"""Regression checks for annotation resolution and lazy model imports."""

import importlib
import sys
import types
import unittest
from pathlib import Path
from typing import get_type_hints

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

    def test_importing_loader_does_not_import_model_implementations(self):
        loader = importlib.import_module(PACKAGE + ".services.model_loader")
        self.assertNotIn(PACKAGE + ".models.agricultural_models", sys.modules)
        self.assertIsNone(loader._agri_scorer)
        self.assertIsNone(loader._hf_advisor)
        self.assertIsNone(loader._nllb_translator)


if __name__ == "__main__":
    unittest.main()
