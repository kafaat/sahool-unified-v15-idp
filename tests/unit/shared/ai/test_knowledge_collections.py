"""
Tests for shared/ai/knowledge/collections.py
===============================================
اختبارات ثوابت مجموعات المعرفة

Tests cover:
- Collection constant values
- COLLECTION_DIRECTORY_MAP structure
- ALL_COLLECTIONS list completeness
"""

import pytest

from shared.ai.knowledge.collections import (
    CROP_KNOWLEDGE,
    PEST_KNOWLEDGE,
    CROP_WATER_REQUIREMENTS,
    IRRIGATION_PRACTICES,
    GENERAL_AGRICULTURE,
    SOIL_KNOWLEDGE,
    FERTILIZER_KNOWLEDGE,
    WEATHER_KNOWLEDGE,
    REMOTE_SENSING_KNOWLEDGE,
    SMART_AGRICULTURE_KNOWLEDGE,
    RESEARCH_REFERENCES,
    PRECISION_FARMING_KNOWLEDGE,
    DIGITAL_TWIN_KNOWLEDGE,
    COLLECTION_DIRECTORY_MAP,
    ALL_COLLECTIONS,
)


class TestCollectionConstants:
    def test_crop_knowledge(self):
        assert CROP_KNOWLEDGE == "crop_knowledge"

    def test_pest_knowledge(self):
        assert PEST_KNOWLEDGE == "pest_knowledge"

    def test_crop_water_requirements(self):
        assert CROP_WATER_REQUIREMENTS == "crop_water_requirements"

    def test_irrigation_practices(self):
        assert IRRIGATION_PRACTICES == "irrigation_practices"

    def test_general_agriculture(self):
        assert GENERAL_AGRICULTURE == "general_agriculture"

    def test_soil_knowledge(self):
        assert SOIL_KNOWLEDGE == "soil_knowledge"

    def test_fertilizer_knowledge(self):
        assert FERTILIZER_KNOWLEDGE == "fertilizer_knowledge"

    def test_weather_knowledge(self):
        assert WEATHER_KNOWLEDGE == "weather_knowledge"

    def test_remote_sensing_knowledge(self):
        assert REMOTE_SENSING_KNOWLEDGE == "remote_sensing_knowledge"

    def test_smart_agriculture_knowledge(self):
        assert SMART_AGRICULTURE_KNOWLEDGE == "smart_agriculture_knowledge"

    def test_research_references(self):
        assert RESEARCH_REFERENCES == "research_references"

    def test_precision_farming_knowledge(self):
        assert PRECISION_FARMING_KNOWLEDGE == "precision_farming_knowledge"

    def test_digital_twin_knowledge(self):
        assert DIGITAL_TWIN_KNOWLEDGE == "digital_twin_knowledge"


class TestAllCollections:
    def test_contains_all_collections(self):
        expected = {
            CROP_KNOWLEDGE,
            PEST_KNOWLEDGE,
            CROP_WATER_REQUIREMENTS,
            IRRIGATION_PRACTICES,
            GENERAL_AGRICULTURE,
            SOIL_KNOWLEDGE,
            FERTILIZER_KNOWLEDGE,
            WEATHER_KNOWLEDGE,
            REMOTE_SENSING_KNOWLEDGE,
            SMART_AGRICULTURE_KNOWLEDGE,
            RESEARCH_REFERENCES,
            PRECISION_FARMING_KNOWLEDGE,
            DIGITAL_TWIN_KNOWLEDGE,
        }
        assert set(ALL_COLLECTIONS) == expected

    def test_count(self):
        assert len(ALL_COLLECTIONS) == 13

    def test_no_duplicates(self):
        assert len(ALL_COLLECTIONS) == len(set(ALL_COLLECTIONS))


class TestCollectionDirectoryMap:
    def test_is_dict(self):
        assert isinstance(COLLECTION_DIRECTORY_MAP, dict)

    def test_all_collections_in_map(self):
        """Every collection in ALL_COLLECTIONS should be a key in the directory map."""
        for collection in ALL_COLLECTIONS:
            assert collection in COLLECTION_DIRECTORY_MAP, f"{collection} missing from COLLECTION_DIRECTORY_MAP"

    def test_values_are_lists(self):
        for key, value in COLLECTION_DIRECTORY_MAP.items():
            assert isinstance(value, list), f"{key} value should be a list"

    def test_crop_knowledge_dir(self):
        assert "docs/knowledge-base/crops/" in COLLECTION_DIRECTORY_MAP[CROP_KNOWLEDGE]

    def test_empty_dirs_for_metadata_routed(self):
        """Some collections are populated via metadata routing, so their dirs are empty."""
        assert COLLECTION_DIRECTORY_MAP[CROP_WATER_REQUIREMENTS] == []
        assert COLLECTION_DIRECTORY_MAP[RESEARCH_REFERENCES] == []
