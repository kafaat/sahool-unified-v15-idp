"""
SAHOOL Human-Machine Collaborative Irrigation Decision Framework Tests
اختبارات إطار قرارات الري التعاوني بين الإنسان والآلة

This module contains comprehensive unit tests for the HMC (Human-Machine Collaborative)
Irrigation Decision Framework, covering:
- Pydantic models for goals, constraints, and experience rules
- The four collaboration dimensions (Goal Anchoring, Experience Injection,
  Supervision Calibration, Value Upgrade)
- The collaborative engine workflow
- Validation checklist
- Integration with SAHOOL services

Test Structure:
- conftest.py: Shared fixtures and mocks
- test_models.py: Pydantic model validation tests
- test_dimensions.py: Dimension-specific logic tests
- test_collaborative_engine.py: Main engine workflow tests
- test_checklist.py: Validation checklist tests
- test_integration.py: Integration with farm advisor and other services
"""
