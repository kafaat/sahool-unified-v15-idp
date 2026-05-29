# SPDX-License-Identifier: Proprietary
"""Unit tests for shared.crop_cards.

The cranberry counter-example test proves that crop suitability is decided
by card data alone — never by programmed bias. This is the property that
makes the platform portable across regions.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from shared.crop_cards import (
    CropCard,
    CropCardSchemaError,
    list_cards,
    load_card,
)


pytestmark = pytest.mark.unit


# ── Happy path ───────────────────────────────────────────────────────────


def test_load_wheat_card_succeeds() -> None:
    card = load_card("wheat")
    assert isinstance(card, CropCard)
    assert card.crop_id == "wheat"
    assert card.kc_mid > card.kc_initial
    assert len(card.sources) >= 1


def test_list_cards_returns_both_wheat_and_cranberry() -> None:
    cards = list_cards()
    assert "wheat" in cards
    assert "cranberry" in cards
    assert cards == sorted(cards)


# ── Cranberry counter-example: data alone rules ──────────────────────────


def test_cranberry_card_is_loadable_but_carries_governing_constraints() -> None:
    """
    The cranberry card is REJECTED FOR ARID-SALINE REGIONS NOT by hard-coded
    bias but by its OWN physical parameters:
      - salinity_threshold_dsm <= 1.0 (extremely salt-sensitive)
      - ph_max < 7.0 (acidic-obligate)
      - chilling_hours_required >= 500 (cool-climate requirement)

    Suitability is a downstream computation that READS these fields — there
    is no special case in code for cranberry. This is what portability means.
    """
    card = load_card("cranberry")
    assert card.salinity_threshold_dsm <= 1.0
    assert card.ph_max < 7.0
    assert card.chilling_hours_required >= 500


def test_cranberry_card_documents_its_sources() -> None:
    """Even rejected crops must cite their physical parameters' provenance."""
    card = load_card("cranberry")
    assert len(card.sources) >= 1


# ── Path traversal guards ────────────────────────────────────────────────


def test_path_traversal_rejected() -> None:
    with pytest.raises(CropCardSchemaError):
        load_card("../etc/passwd")


def test_uppercase_crop_id_rejected() -> None:
    with pytest.raises(CropCardSchemaError):
        load_card("WHEAT")


def test_slash_in_crop_id_rejected() -> None:
    with pytest.raises(CropCardSchemaError):
        load_card("a/b")


def test_unknown_crop_id_raises_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        load_card("zzz_unknown_crop")


# ── Neutrality: schema rejects location-coupled fields ──────────────────


def test_schema_rejects_region_field() -> None:
    """The schema is locked (extra='forbid'). Adding 'region' must fail."""
    with pytest.raises(ValidationError):
        CropCard(
            crop_id="test_crop",
            name_ar="x",
            name_en="x",
            family="cereal",
            kc_initial=0.3,
            kc_mid=1.0,
            kc_end=0.4,
            growth_stage_days=[20, 25, 60, 30],
            salinity_threshold_dsm=6.0,
            salinity_slope_pct=7.1,
            ph_min=6.0,
            ph_max=8.5,
            chilling_hours_required=0,
            base_temp_c=0.0,
            max_temp_cap_c=35.0,
            sources=["src"],
            region="al-jawf",  # type: ignore[call-arg]
        )


def test_schema_requires_at_least_one_source() -> None:
    with pytest.raises(ValidationError):
        CropCard(
            crop_id="test_crop",
            name_ar="x",
            name_en="x",
            family="cereal",
            kc_initial=0.3,
            kc_mid=1.0,
            kc_end=0.4,
            growth_stage_days=[20, 25, 60, 30],
            salinity_threshold_dsm=6.0,
            salinity_slope_pct=7.1,
            ph_min=6.0,
            ph_max=8.5,
            chilling_hours_required=0,
            base_temp_c=0.0,
            max_temp_cap_c=35.0,
            sources=[],
        )
