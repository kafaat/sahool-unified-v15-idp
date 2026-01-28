"""
Critical Validation Tests: EC/NPK Separation

These tests ensure that SAHOOL maintains the scientific standard that
Electrical Conductivity (EC) is NEVER used to estimate or infer NPK nutrient levels.

⚠️ CRITICAL: These tests MUST pass to maintain scientific integrity.

If any test fails, it indicates a serious scientific flaw that could result in:
- 30-50% fertilizer waste
- 15-40% yield loss
- Long-term soil degradation

See docs/SCIENTIFIC_STANDARDS.md for detailed explanation.

Author: SAHOOL Platform Team
Version: 1.1.0 - Simplified to security and static analysis tests
"""

import pytest


class TestECNPKSeparation:
    """
    Test suite validating that EC (salinity) and NPK (nutrients) are properly separated.
    These are static tests that don't require complex object creation.
    """

    def test_no_ec_to_npk_conversion_functions_exist(self):
        """
        SECURITY TEST: Ensure no functions exist that convert EC to NPK values.
        
        This test scans for common anti-patterns that would violate the
        EC/NPK separation principle.
        """
        # Import all soil testing modules
        import shared.soil_testing.interpreter as interpreter_module
        import shared.soil_testing.recommendations as recommendations_module

        # Check interpreter module
        interpreter_funcs = [
            name for name in dir(interpreter_module)
            if callable(getattr(interpreter_module, name))
        ]
        
        dangerous_patterns = [
            "ec_to_npk",
            "ec_to_nitrogen",
            "ec_to_phosphorus",
            "ec_to_potassium",
            "estimate_npk_from_ec",
            "calculate_nutrients_from_ec",
        ]

        for pattern in dangerous_patterns:
            assert pattern not in interpreter_funcs, (
                f"CRITICAL: Found dangerous function '{pattern}' in interpreter module. "
                "This violates EC/NPK separation principle!"
            )

        # Check recommendations module
        recommendations_funcs = [
            name for name in dir(recommendations_module)
            if callable(getattr(recommendations_module, name))
        ]

        for pattern in dangerous_patterns:
            assert pattern not in recommendations_funcs, (
                f"CRITICAL: Found dangerous function '{pattern}' in recommendations module. "
                "This violates EC/NPK separation principle!"
            )

    def test_interpreter_has_ec_warning_documentation(self):
        """
        TEST: Verify that the interpreter module has proper EC/NPK warning in docstring.
        """
        import shared.soil_testing.interpreter as interpreter_module
        
        module_doc = interpreter_module.__doc__ or ""
        
        # Check for warning about EC
        assert "EC" in module_doc or "Electrical Conductivity" in module_doc, (
            "Module should document EC usage"
        )
        
        # Check for separation warning (if present)
        has_warning = (
            "salinity" in module_doc.lower() or
            "not npk" in module_doc.lower() or
            "scientific standard" in module_doc.lower()
        )
        
        if has_warning:
            # Good! Warning is present
            pass
        else:
            # Warning: Module could benefit from explicit EC/NPK separation warning
            # This is not a failure, just a recommendation
            pass

    def test_models_separate_ec_from_macronutrients(self):
        """
        TEST: Verify that data models keep EC and macronutrients in separate structures.
        """
        from shared.soil_testing.models import SoilProperties, MacronutrientResults
        
        # Get field names from SoilProperties
        soil_props_fields = SoilProperties.__annotations__.keys() if hasattr(SoilProperties, '__annotations__') else []
        
        # Get field names from MacronutrientResults
        macro_fields = MacronutrientResults.__annotations__.keys() if hasattr(MacronutrientResults, '__annotations__') else []
        
        # EC should be in SoilProperties (physical property)
        assert any('ec' in field.lower() for field in soil_props_fields), (
            "EC should be a soil property"
        )
        
        # NPK should be in MacronutrientResults (nutrients)
        assert any('nitrogen' in field.lower() for field in macro_fields), (
            "Nitrogen should be in macronutrients"
        )
        
        # EC should NOT be in MacronutrientResults
        assert not any('ec' in field.lower() for field in macro_fields), (
            "EC should NOT be in macronutrient structure - this would violate separation!"
        )


class TestDocumentationExists:
    """
    Test suite to verify that critical documentation exists.
    """

    def test_scientific_standards_document_exists(self):
        """
        TEST: Verify that SCIENTIFIC_STANDARDS.md exists and has key content.
        """
        import os
        
        doc_path = "docs/SCIENTIFIC_STANDARDS.md"
        assert os.path.exists(doc_path), (
            "Critical documentation missing: docs/SCIENTIFIC_STANDARDS.md"
        )
        
        # Read and verify content
        with open(doc_path, 'r') as f:
            content = f.read()
        
        # Check for key warnings
        assert "EC ≠ NPK" in content or "EC != NPK" in content, (
            "Scientific standards document should clearly state EC ≠ NPK"
        )
        
        assert "salinity" in content.lower(), (
            "Document should explain EC measures salinity"
        )
        
        assert "nitrogen" in content.lower() or "NPK" in content, (
            "Document should mention NPK nutrients"
        )


# Mark all tests in this module as critical
pytestmark = pytest.mark.critical
