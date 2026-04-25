# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""End-to-end pipeline test: WAL → fusion → PROSAIL → safety gateway.

This is the cross-ADR contract test for v3.1: it proves the four
modules compose correctly and the data-flow matches what the
``digital-twin-engine`` (port 8253) and the prescription-safety
service rely on in production.

The test is in-process and pure-Python on purpose. The components have
deep unit-test coverage in their own packages; what's only verifiable
at the integration level is the *flow*:

1. Multi-sensor reflectance frames arrive at the edge and are written
   to the durable WAL (ADR-014).
2. The replay path drains the WAL into the spatio-temporal fusion
   layer (ADR-011), which produces a fused per-band reflectance state.
3. The fused state feeds the PROSAIL inversion (ADR-015), which
   retrieves canopy parameters (LAI, Cab) and their k-NN uncertainty.
4. The retrieval feeds an irrigation prescription whose safety is
   adjudicated by the prescription-safety gateway (ADR-013), with
   real ``ForbiddenSubstanceChecker`` and ``DosageToleranceChecker``
   instances wired in.
"""

from __future__ import annotations

import json
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from shared.edge_resilience import ResilienceConfig, WriteAheadLog
from shared.prescription_safety import (
    DecisionEnum,
    DosageToleranceChecker,
    ForbiddenSubstanceChecker,
    PrescriptionGateway,
    PrescriptionRequest,
    RateRange,
)
from shared.process_models.prosail_inversion import (
    ProsailGeometry,
    generate_lut,
    invert,
)
from shared.process_models.radiative_transfer import (
    CanopyParameters,
    LeafOpticalProperties,
    prospect_reflectance,
    sail_canopy_reflectance,
)
from shared.spatiotemporal import (
    EKF,
    FactorGraph,
    FusionConfig,
    SensorFrame,
)

_GEOM = ProsailGeometry(sun_zenith_deg=30.0, view_zenith_deg=0.0, relative_azimuth_deg=0.0)
_BANDS = ("blue", "green", "red", "red_edge", "nir", "swir")


def _truth_reflectance(lai: float, cab: float) -> dict[str, float]:
    """Forward-model reflectance for a known canopy state — the
    "ground truth" the pipeline must recover after fusion + inversion.
    """

    leaf = LeafOpticalProperties(chlorophyll_ug_cm2=cab)
    canopy = CanopyParameters(
        lai=lai,
        sun_zenith_deg=_GEOM.sun_zenith_deg,
        view_zenith_deg=_GEOM.view_zenith_deg,
    )
    return sail_canopy_reflectance(prospect_reflectance(leaf), canopy)


def _add_noise(reflectance: dict[str, float], offset: float) -> dict[str, float]:
    """Tiny additive bias per band — simulates two miscalibrated sensors
    whose mean we recover by fusion.
    """

    return {band: max(0.0, value + offset) for band, value in reflectance.items()}


@pytest.mark.asyncio
async def test_e2e_wal_fusion_prosail_safety_pipeline() -> None:
    """Full happy-path pipeline. Every step must succeed and the final
    safety decision must approve a prescription that respects the
    label and the agronomic ground truth.
    """

    truth_lai = 2.7
    truth_cab = 42.0
    truth_reflectance = _truth_reflectance(truth_lai, truth_cab)
    base_ts = datetime(2026, 4, 25, 8, 0, tzinfo=UTC)

    # ---- 1. Edge WAL: persist two miscalibrated reflectance frames -----
    with tempfile.TemporaryDirectory() as wal_dir:
        wal = WriteAheadLog(ResilienceConfig(wal_path=str(Path(wal_dir)), fsync_batch_size=1))
        try:
            for sensor_id, offset, dt_ms in (
                ("multispec-A", +0.005, 0),
                ("multispec-B", -0.005, 200),
            ):
                obs = _add_noise(truth_reflectance, offset)
                payload = json.dumps(
                    {
                        "sensor_id": sensor_id,
                        "timestamp": (base_ts + timedelta(milliseconds=dt_ms)).isoformat(),
                        "values": obs,
                        # Sensor noise covariance — drives the
                        # information-weighted fusion downstream.
                        "covariance": dict.fromkeys(obs, 0.0001),
                    }
                ).encode()
                await wal.append(payload)

            # ---- 2. Replay → SensorFrame stream ------------------------
            frames: list[SensorFrame] = []
            async for entry in wal.replay():
                record = json.loads(entry.payload)
                frames.append(
                    SensorFrame(
                        sensor_id=record["sensor_id"],
                        timestamp=datetime.fromisoformat(record["timestamp"]),
                        position=(0.0, 0.0, None),
                        values={k: float(v) for k, v in record["values"].items()},
                        covariance={k: float(v) for k, v in record["covariance"].items()},
                    )
                )
                # Ack the entry so a subsequent run starts from a clean WAL.
                await wal.truncate_to(entry.sequence)
            assert len(frames) == 2

            # ---- 3. Spatio-temporal fusion -----------------------------
            # Streaming EKF: incrementally fuse the two miscalibrated
            # sensors; per-band posterior mean must lie between the two
            # observed values, very close to the unbiased truth.
            ekf = EKF(FusionConfig())
            for frame in frames:
                ekf.update(frame)
            ekf_state = ekf.state()
            for band in _BANDS:
                if band not in truth_reflectance:
                    continue
                # Both sensors bracket the truth ±0.005; the fused state
                # should sit much closer than either individual reading.
                obs_a = frames[0].values[band]
                obs_b = frames[1].values[band]
                lo, hi = min(obs_a, obs_b), max(obs_a, obs_b)
                assert lo - 1e-9 <= ekf_state.state[band] <= hi + 1e-9

            # Batch refinement via the factor graph (auto solver picks
            # closed_form because covariances are diagonal). Equivalent
            # to information-weighted mean for two identically-noisy
            # sensors — i.e. the average — which is the unbiased
            # estimator of the truth.
            fg = FactorGraph(FusionConfig(alignment_window_ms=500))
            fg.add_frames(frames)
            fused = fg.optimize()
            assert len(fused) == 1
            fused_reflectance = fused[0].state
            for band, truth_value in truth_reflectance.items():
                assert fused_reflectance[band] == pytest.approx(truth_value, abs=1e-6)

            # ---- 4. PROSAIL inversion ----------------------------------
            lut = generate_lut(
                {"LAI": (0.5, 6.0), "Cab": (10.0, 60.0)},
                density=10,
                geometry=_GEOM,
            )
            retrieval = invert(fused_reflectance, _GEOM, lut=lut, top_k=5, backend="kd_tree")
            # Grid step: LAI ≈ 0.61, Cab ≈ 5.6. Recovery within those
            # tolerances is the contract ADR-015 commits to.
            assert retrieval.parameters["LAI"] == pytest.approx(truth_lai, abs=0.7)
            assert retrieval.parameters["Cab"] == pytest.approx(truth_cab, abs=7.0)
            assert retrieval.uncertainty["LAI"] >= 0.0
            assert retrieval.diagnostics["backend"] == "kd_tree"

            # ---- 5. Prescription safety gateway ------------------------
            # An LAI of 2.7 and Cab of 42 indicates a healthy mid-stage
            # crop; an irrigation prescription of 25 mm is well within
            # the tolerance band, the product is on neither blocklist,
            # and the gateway must approve.
            request = PrescriptionRequest(
                tenant_id="tenant-001",
                prescription_id="rx-2026-0425-001",
                prescription_type="irrigation",
                field_id="FIELD-003",
                crop="wheat",
                product="freshwater",
                rate=25.0,
                rate_unit="mm",
                target={
                    "growth_stage": "tillering",
                    "retrieved_lai": retrieval.parameters["LAI"],
                    "retrieved_cab": retrieval.parameters["Cab"],
                },
            )
            gateway = PrescriptionGateway(
                checkers=[
                    ForbiddenSubstanceChecker.from_iterable(["paraquat", "endosulfan"]),
                    DosageToleranceChecker(
                        rates={
                            ("wheat", "freshwater"): RateRange(min_rate=10.0, max_rate=50.0, unit="mm"),
                        }
                    ),
                ]
            )
            decision = await gateway.check(request)
            assert decision.decision == DecisionEnum.APPROVED
            # Audit trail invariant: every checker contributed evidence.
            assert {ev.checker for ev in decision.evidence} == {
                "forbidden_substance",
                "dosage_tolerance",
            }
        finally:
            wal.close()


@pytest.mark.asyncio
async def test_e2e_pipeline_blocks_forbidden_substance() -> None:
    """Negative path: identical retrieval, but a forbidden product must
    short-circuit the gateway to ``REJECTED`` regardless of dosage.
    """

    truth_reflectance = _truth_reflectance(lai=2.7, cab=42.0)
    base_ts = datetime(2026, 4, 25, 8, 0, tzinfo=UTC)

    with tempfile.TemporaryDirectory() as wal_dir:
        wal = WriteAheadLog(ResilienceConfig(wal_path=str(Path(wal_dir))))
        try:
            await wal.append(
                json.dumps(
                    {
                        "sensor_id": "multispec-A",
                        "timestamp": base_ts.isoformat(),
                        "values": _add_noise(truth_reflectance, 0.0),
                        "covariance": dict.fromkeys(truth_reflectance, 0.0001),
                    }
                ).encode()
            )
            frames: list[SensorFrame] = []
            async for entry in wal.replay():
                record = json.loads(entry.payload)
                frames.append(
                    SensorFrame(
                        sensor_id=record["sensor_id"],
                        timestamp=datetime.fromisoformat(record["timestamp"]),
                        position=(0.0, 0.0, None),
                        values={k: float(v) for k, v in record["values"].items()},
                        covariance={k: float(v) for k, v in record["covariance"].items()},
                    )
                )

            fg = FactorGraph(FusionConfig())
            fg.add_frames(frames)
            fused_reflectance = fg.optimize()[0].state

            lut = generate_lut(
                {"LAI": (0.5, 6.0), "Cab": (10.0, 60.0)},
                density=8,
                geometry=_GEOM,
            )
            retrieval = invert(fused_reflectance, _GEOM, lut=lut, top_k=5)

            request = PrescriptionRequest(
                tenant_id="tenant-001",
                prescription_id="rx-block-001",
                prescription_type="pesticide",
                field_id="FIELD-003",
                crop="wheat",
                product="Paraquat",
                rate=2.0,
                rate_unit="L/ha",
                target={"retrieved_lai": retrieval.parameters["LAI"]},
            )
            gateway = PrescriptionGateway(
                checkers=[
                    ForbiddenSubstanceChecker.from_iterable(["paraquat", "endosulfan"]),
                ]
            )
            decision = await gateway.check(request)
            assert decision.decision == DecisionEnum.REJECTED
            codes = {reason.code for reason in decision.reasons}
            assert "FORBIDDEN_SUBSTANCE" in codes
        finally:
            wal.close()
