"""
Tests for Knowledge Collection Constants
=========================================
اختبارات ثوابت مجموعات المعرفة

Tests for collection names, directory mapping, and completeness.
"""

from __future__ import annotations

import pytest

from shared.ai.knowledge.collections import (
    ALL_COLLECTIONS,
    COLLECTION_DIRECTORY_MAP,
    CROP_KNOWLEDGE,
    CROP_WATER_REQUIREMENTS,
    DIGITAL_TWIN_KNOWLEDGE,
    FERTILIZER_KNOWLEDGE,
    GENERAL_AGRICULTURE,
    IRRIGATION_PRACTICES,
    PEST_KNOWLEDGE,
    PRECISION_FARMING_KNOWLEDGE,
    REMOTE_SENSING_KNOWLEDGE,
    RESEARCH_REFERENCES,
    SMART_AGRICULTURE_KNOWLEDGE,
    SOIL_KNOWLEDGE,
    WEATHER_KNOWLEDGE,
)


class TestCollectionConstants:
    """Tests for collection name constants."""

    @pytest.mark.unit
    def test_collection_values(self):
        """Test all collection constant values."""
        assert CROP_KNOWLEDGE == "crop_knowledge"
        assert PEST_KNOWLEDGE == "pest_knowledge"
        assert CROP_WATER_REQUIREMENTS == "crop_water_requirements"
        assert IRRIGATION_PRACTICES == "irrigation_practices"
        assert GENERAL_AGRICULTURE == "general_agriculture"
        assert SOIL_KNOWLEDGE == "soil_knowledge"
        assert FERTILIZER_KNOWLEDGE == "fertilizer_knowledge"
        assert WEATHER_KNOWLEDGE == "weather_knowledge"
        assert REMOTE_SENSING_KNOWLEDGE == "remote_sensing_knowledge"

    @pytest.mark.unit
    def test_all_collections_count(self):
        """Test that ALL_COLLECTIONS has 13 entries."""
        assert len(ALL_COLLECTIONS) == 13

    @pytest.mark.unit
    def test_all_collections_contents(self):
        """Test ALL_COLLECTIONS contains all defined collections."""
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

    @pytest.mark.unit
    def test_no_duplicate_collections(self):
        """Test no duplicate collection names."""
        assert len(ALL_COLLECTIONS) == len(set(ALL_COLLECTIONS))


class TestCollectionDirectoryMap:
    """Tests for COLLECTION_DIRECTORY_MAP."""

    @pytest.mark.unit
    def test_all_collections_mapped(self):
        """Test every collection has a directory mapping."""
        for coll in ALL_COLLECTIONS:
            assert coll in COLLECTION_DIRECTORY_MAP, f"Collection '{coll}' not mapped"

    @pytest.mark.unit
    def test_directory_paths_format(self):
        """Test directory paths end with /."""
        for coll, dirs in COLLECTION_DIRECTORY_MAP.items():
            for d in dirs:
                assert d.endswith("/"), f"Directory '{d}' for '{coll}' should end with /"

    @pytest.mark.unit
    def test_crop_knowledge_mapping(self):
        """Test crop knowledge maps to crops directory."""
        assert "docs/knowledge-base/crops/" in COLLECTION_DIRECTORY_MAP[CROP_KNOWLEDGE]

    @pytest.mark.unit
    def test_pest_knowledge_mapping(self):
        """Test pest knowledge maps to diseases directory."""
        assert "docs/knowledge-base/diseases/" in COLLECTION_DIRECTORY_MAP[PEST_KNOWLEDGE]

    @pytest.mark.unit
    def test_soil_knowledge_mapping(self):
        """Test soil knowledge maps to soils directory."""
        assert "docs/knowledge-base/soils/" in COLLECTION_DIRECTORY_MAP[SOIL_KNOWLEDGE]

    @pytest.mark.unit
    def test_fertilizer_knowledge_mapping(self):
        """Test fertilizer knowledge maps to fertilization directory."""
        assert "docs/knowledge-base/fertilization/" in COLLECTION_DIRECTORY_MAP[FERTILIZER_KNOWLEDGE]

    @pytest.mark.unit
    def test_weather_knowledge_mapping(self):
        """Test weather knowledge maps to weather directory."""
        assert "docs/knowledge-base/weather/" in COLLECTION_DIRECTORY_MAP[WEATHER_KNOWLEDGE]

    @pytest.mark.unit
    def test_remote_sensing_knowledge_mapping(self):
        """Test remote sensing maps to remote-sensing directory."""
        assert "docs/knowledge-base/remote-sensing/" in COLLECTION_DIRECTORY_MAP[REMOTE_SENSING_KNOWLEDGE]

    @pytest.mark.unit
    def test_general_agriculture_mapping(self):
        """Test general agriculture maps to best-practices and monitoring directories."""
        dirs = COLLECTION_DIRECTORY_MAP[GENERAL_AGRICULTURE]
        assert any("best-practices" in d for d in dirs)
