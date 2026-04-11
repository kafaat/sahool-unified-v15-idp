"""
IPCC Tier 1 Carbon Footprint Engine
محرك حساب البصمة الكربونية وفقاً للمستوى الأول من إرشادات IPCC

References:
    - IPCC 2019 Refinement to the 2006 IPCC Guidelines for National
      Greenhouse Gas Inventories, Volume 4: Agriculture, Forestry and
      Other Land Use (AFOLU).
    - GHG Protocol Agricultural Guidance (WRI/WBCSD).
    - FAO Eco-efficient Agriculture studies for Middle East / MENA.

All factors are Tier 1 defaults — region-agnostic but well-documented.
Tier 2 (region-specific) and Tier 3 (process-model) factors can override
these via a future calibration table without changing the API surface.

Emission factors are expressed in:
    * kg CO2e per unit of activity (fuel litre, kg fertiliser N, hour of
      machinery operation, etc.)
    * "CO2e" = carbon-dioxide equivalent, rolling in CH4 (×25 GWP100) +
      N2O (×298 GWP100) alongside direct CO2 per AR5.

Sequestration factors are expressed as NEGATIVE kg CO2e (carbon taken
OUT of the atmosphere) for operations that lock carbon into soil or
biomass: cover cropping, no-till, biochar application, agroforestry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Emission factors — IPCC Tier 1 defaults
# ---------------------------------------------------------------------------

# Diesel combustion — IPCC 2019 Vol 2 Ch 3 Table 3.2.1 (stationary/mobile).
# 2.68 kg CO2 + 0.00001 kg CH4 (×25) + 0.00007 kg N2O (×298) = 2.70 kg CO2e/L.
FUEL_DIESEL_CO2E_PER_LITRE = 2.70

# Gasoline combustion
FUEL_GASOLINE_CO2E_PER_LITRE = 2.34

# Nitrogen fertiliser (synthetic) — IPCC Tier 1 N2O emission factor
# EF1 = 0.01 kg N2O-N / kg N applied (direct). Volatilization + leaching
# indirect factor adds ~0.003. Total N2O = 0.013 kg / kg N.
# 0.013 × 44/28 (N2O molecular weight) × 298 (GWP) = ~6.11 kg CO2e / kg N.
FERTILIZER_N_CO2E_PER_KG = 6.11

# Phosphorus (P2O5) — embodied emissions from production (Tier 1 default).
FERTILIZER_P_CO2E_PER_KG = 1.50

# Potassium (K2O) — embodied emissions from production.
FERTILIZER_K_CO2E_PER_KG = 0.65

# Machinery embodied emissions (amortised per operating hour) — FAO default.
MACHINERY_CO2E_PER_HOUR = 3.2

# Pesticide spraying — default embodied emissions per kg active ingredient.
PESTICIDE_CO2E_PER_KG = 8.4

# Residue burning (rice/wheat stubble) — IPCC Tier 1 default (kg CO2e/ha).
RESIDUE_BURNING_CO2E_PER_HA = 850.0


# ---------------------------------------------------------------------------
# Sequestration factors — negative emissions
# ---------------------------------------------------------------------------

# Cover cropping — long-term SOC gain (kg CO2e sequestered per ha per year).
# FAO estimate: 0.3-0.5 t CO2/ha/yr. We use 400 kg CO2e/ha/yr as Tier 1.
COVER_CROPPING_CO2E_SEQ_PER_HA_YEAR = 400.0

# No-till / reduced tillage — additional SOC gain vs conventional plowing.
NO_TILL_CO2E_SEQ_PER_HA_YEAR = 300.0

# Biochar — highly effective but rate depends on application rate.
# Default: 2.5 t CO2e sequestered per tonne of biochar applied.
BIOCHAR_CO2E_SEQ_PER_TONNE = 2500.0


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class OperationInput:
    """
    Subset of field_operations columns that the engine needs. Populated
    either from the carbon-service DB reader OR from an incoming NATS
    event payload — both sources must produce this shape.
    """

    operation_id: str
    operation_type: str  # plowing | land_preparation | fertilization | ...
    area_hectares: float | None = None
    duration_hours: float | None = None
    fuel_liters: float | None = None
    fuel_type: str = "diesel"  # diesel | gasoline
    # Fertiliser applied (kg nutrient, NOT kg product)
    nitrogen_kg: float | None = None
    phosphorus_kg: float | None = None
    potassium_kg: float | None = None
    # Pesticide active ingredient (kg)
    pesticide_kg: float | None = None
    # Biochar (tonnes)
    biochar_tonnes: float | None = None
    # Whether cover cropping applies (used for sequestration).
    is_cover_cropping: bool = False
    is_no_till: bool = False
    is_residue_burning: bool = False
    # Arbitrary metadata pass-through
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CarbonBreakdown:
    """Per-source emission breakdown so the UI can show a stacked chart."""

    fuel: float = 0.0
    fertilizer_n: float = 0.0
    fertilizer_p: float = 0.0
    fertilizer_k: float = 0.0
    machinery: float = 0.0
    pesticide: float = 0.0
    residue_burning: float = 0.0
    # Sequestration is stored as POSITIVE values here; the engine subtracts
    # them from the emission total when computing the net.
    cover_cropping_seq: float = 0.0
    no_till_seq: float = 0.0
    biochar_seq: float = 0.0


@dataclass
class CarbonResult:
    operation_id: str
    operation_type: str
    emissions_kg: float
    sequestration_kg: float
    net_kg: float
    methodology: str
    emission_source_type: str
    carbon_credit_eligible: bool
    breakdown: CarbonBreakdown
    warnings: list[str]


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class IpccTier1Engine:
    """
    Compute per-operation CO2e using IPCC Tier 1 default factors.

    The engine is deliberately pure (no DB, no NATS) so it's trivially
    unit-testable. A separate orchestrator wires it to DB reads + writes.
    """

    METHODOLOGY = "IPCC-Tier1"

    def compute(self, op: OperationInput) -> CarbonResult:
        breakdown = CarbonBreakdown()
        warnings: list[str] = []

        # ── Fuel combustion ────────────────────────────────────────────
        if op.fuel_liters and op.fuel_liters > 0:
            factor = (
                FUEL_DIESEL_CO2E_PER_LITRE
                if op.fuel_type == "diesel"
                else FUEL_GASOLINE_CO2E_PER_LITRE
            )
            breakdown.fuel = op.fuel_liters * factor

        # ── Fertiliser embodied + in-field N2O ────────────────────────
        if op.nitrogen_kg and op.nitrogen_kg > 0:
            breakdown.fertilizer_n = op.nitrogen_kg * FERTILIZER_N_CO2E_PER_KG
        if op.phosphorus_kg and op.phosphorus_kg > 0:
            breakdown.fertilizer_p = (
                op.phosphorus_kg * FERTILIZER_P_CO2E_PER_KG
            )
        if op.potassium_kg and op.potassium_kg > 0:
            breakdown.fertilizer_k = op.potassium_kg * FERTILIZER_K_CO2E_PER_KG

        # ── Machinery embodied emissions (per hour) ────────────────────
        if op.duration_hours and op.duration_hours > 0:
            breakdown.machinery = op.duration_hours * MACHINERY_CO2E_PER_HOUR

        # ── Pesticide ──────────────────────────────────────────────────
        if op.pesticide_kg and op.pesticide_kg > 0:
            breakdown.pesticide = op.pesticide_kg * PESTICIDE_CO2E_PER_KG

        # ── Residue burning (if applicable) ────────────────────────────
        if op.is_residue_burning and op.area_hectares and op.area_hectares > 0:
            breakdown.residue_burning = (
                op.area_hectares * RESIDUE_BURNING_CO2E_PER_HA
            )
            warnings.append(
                "Residue burning is a high-intensity emission source. "
                "Consider alternatives (incorporation, baling)."
            )

        # ── Sequestration ──────────────────────────────────────────────
        # Applied at a per-month rate (1/12th of annual) to match the
        # operation-level granularity of the source data.
        if op.is_cover_cropping and op.area_hectares and op.area_hectares > 0:
            breakdown.cover_cropping_seq = (
                op.area_hectares * COVER_CROPPING_CO2E_SEQ_PER_HA_YEAR / 12
            )
        if op.is_no_till and op.area_hectares and op.area_hectares > 0:
            breakdown.no_till_seq = (
                op.area_hectares * NO_TILL_CO2E_SEQ_PER_HA_YEAR / 12
            )
        if op.biochar_tonnes and op.biochar_tonnes > 0:
            breakdown.biochar_seq = (
                op.biochar_tonnes * BIOCHAR_CO2E_SEQ_PER_TONNE
            )

        emissions = (
            breakdown.fuel
            + breakdown.fertilizer_n
            + breakdown.fertilizer_p
            + breakdown.fertilizer_k
            + breakdown.machinery
            + breakdown.pesticide
            + breakdown.residue_burning
        )
        sequestration = (
            breakdown.cover_cropping_seq
            + breakdown.no_till_seq
            + breakdown.biochar_seq
        )
        net = emissions - sequestration

        # Carbon credits are generally issued for net-negative operations
        # backed by a verified methodology. The eligibility flag is
        # conservative — only flips TRUE when sequestration exceeds
        # emissions AND the sequestration source is a well-known one.
        credit_eligible = (
            sequestration > 0
            and net < 0
            and (op.is_cover_cropping or op.is_no_till or bool(op.biochar_tonnes))
        )

        source_type = self._primary_source(breakdown)

        if emissions == 0 and sequestration == 0:
            warnings.append(
                "No computable inputs — operation has no fuel, fertiliser, "
                "or machinery hours recorded."
            )

        return CarbonResult(
            operation_id=op.operation_id,
            operation_type=op.operation_type,
            emissions_kg=round(emissions, 2),
            sequestration_kg=round(sequestration, 2),
            net_kg=round(net, 2),
            methodology=self.METHODOLOGY,
            emission_source_type=source_type,
            carbon_credit_eligible=credit_eligible,
            breakdown=breakdown,
            warnings=warnings,
        )

    @staticmethod
    def _primary_source(b: CarbonBreakdown) -> str:
        """Pick the biggest-contributing category for dashboard slicing."""
        candidates = [
            ("fuel", b.fuel),
            (
                "fertilizer_n",
                b.fertilizer_n + b.fertilizer_p + b.fertilizer_k,
            ),
            ("machinery", b.machinery),
            ("pesticide", b.pesticide),
            ("residue_burning", b.residue_burning),
            (
                "sequestration",
                b.cover_cropping_seq + b.no_till_seq + b.biochar_seq,
            ),
        ]
        candidates.sort(key=lambda x: x[1], reverse=True)
        if candidates[0][1] == 0:
            return "mixed"
        return candidates[0][0]
