# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Unit tests for the Prescription Safety Gateway (ADR-013)."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from shared.prescription_safety import (
    CheckerResult,
    DecisionEnum,
    DosageToleranceChecker,
    ForbiddenSubstanceChecker,
    PesticideComplianceCheckerAdapter,
    PrescriptionGateway,
    PrescriptionRequest,
    RateRange,
    Reason,
)


def _request(**overrides: object) -> PrescriptionRequest:
    base: dict = {
        "tenant_id": "farm-01",
        "prescription_id": "rx-001",
        "prescription_type": "fertilizer",
        "field_id": "FIELD-003",
        "crop": "wheat",
        "product": "Urea 46%",
        "rate": 46.0,
        "rate_unit": "kg/ha",
    }
    base.update(overrides)
    return PrescriptionRequest(**base)  # type: ignore[arg-type]


@dataclass
class _StubChecker:
    name: str
    result: CheckerResult

    async def check(self, request: PrescriptionRequest) -> CheckerResult:
        return self.result


def _ok(name: str = "stub") -> _StubChecker:
    return _StubChecker(name=name, result=CheckerResult.ok())


def _fail(name: str, *, blocking: bool, severity: str = "warning") -> _StubChecker:
    return _StubChecker(
        name=name,
        result=CheckerResult(
            passed=False,
            blocking=blocking,
            reasons=[
                Reason(
                    code="STUB",
                    message_en="stub failed",
                    message_ar="فشل الفاحص",
                    severity=severity,
                    source_checker=name,
                )
            ],
            evidence={"stub": True},
        ),
    )


# ---------------------------------------------------------------------------
# ForbiddenSubstanceChecker
# ---------------------------------------------------------------------------


class TestForbiddenSubstanceChecker:
    @pytest.mark.asyncio
    async def test_clean_request_passes(self) -> None:
        checker = ForbiddenSubstanceChecker.from_iterable(["paraquat", "ddt"])
        result = await checker.check(_request(product="Urea 46%"))
        assert result.passed is True
        assert result.blocking is False
        assert result.reasons == []
        assert result.evidence["matched"] is False

    @pytest.mark.asyncio
    @pytest.mark.parametrize("forbidden", ["Paraquat", "PARAQUAT", "  paraquat  "])
    async def test_blocks_forbidden_case_and_whitespace_insensitive(self, forbidden: str) -> None:
        checker = ForbiddenSubstanceChecker.from_iterable(["paraquat"])
        result = await checker.check(_request(product=forbidden))
        assert result.passed is False
        assert result.blocking is True
        assert len(result.reasons) == 1
        assert result.reasons[0].code == "FORBIDDEN_SUBSTANCE"
        assert result.reasons[0].severity == "critical"

    @pytest.mark.asyncio
    async def test_empty_blocklist_never_blocks(self) -> None:
        checker = ForbiddenSubstanceChecker.from_iterable([])
        result = await checker.check(_request(product="Anything"))
        assert result.passed is True
        assert result.blocking is False


# ---------------------------------------------------------------------------
# DosageToleranceChecker
# ---------------------------------------------------------------------------


@pytest.fixture()
def dosage_checker() -> DosageToleranceChecker:
    return DosageToleranceChecker(
        rates={
            ("wheat", "urea 46%"): RateRange(min_rate=40.0, max_rate=60.0, unit="kg/ha"),
        }
    )


class TestDosageToleranceChecker:
    @pytest.mark.asyncio
    async def test_within_window_passes(self, dosage_checker: DosageToleranceChecker) -> None:
        result = await dosage_checker.check(_request(rate=50.0))
        assert result.passed is True
        assert result.blocking is False

    @pytest.mark.asyncio
    async def test_at_lower_soft_edge_passes(self, dosage_checker: DosageToleranceChecker) -> None:
        # min 40 → soft lo = 36
        result = await dosage_checker.check(_request(rate=36.0))
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_outside_soft_within_hard_emits_review(
        self, dosage_checker: DosageToleranceChecker
    ) -> None:
        # max 60 → soft hi = 66, hard hi = 72
        result = await dosage_checker.check(_request(rate=70.0))
        assert result.passed is False
        assert result.blocking is False
        assert result.reasons[0].code == "DOSAGE_OUT_OF_TOLERANCE"
        assert result.reasons[0].severity == "warning"

    @pytest.mark.asyncio
    async def test_beyond_hard_window_blocks(
        self, dosage_checker: DosageToleranceChecker
    ) -> None:
        result = await dosage_checker.check(_request(rate=100.0))
        assert result.passed is False
        assert result.blocking is True
        assert result.reasons[0].code == "DOSAGE_HARD_LIMIT_EXCEEDED"
        assert result.reasons[0].severity == "critical"

    @pytest.mark.asyncio
    async def test_unit_mismatch_blocks(self, dosage_checker: DosageToleranceChecker) -> None:
        result = await dosage_checker.check(_request(rate_unit="L/ha"))
        assert result.passed is False
        assert result.blocking is True
        assert result.reasons[0].code == "DOSAGE_UNIT_MISMATCH"

    @pytest.mark.asyncio
    async def test_missing_reference_emits_review(self) -> None:
        checker = DosageToleranceChecker(rates={})
        result = await checker.check(_request())
        assert result.passed is False
        assert result.blocking is False
        assert result.reasons[0].code == "UNCHECKED_DOSAGE_NO_REFERENCE"


# ---------------------------------------------------------------------------
# PesticideComplianceCheckerAdapter
# ---------------------------------------------------------------------------


class TestPesticideAdapter:
    @pytest.mark.asyncio
    async def test_non_pesticide_request_is_ok(self) -> None:
        adapter = PesticideComplianceCheckerAdapter()
        result = await adapter.check(_request(prescription_type="fertilizer"))
        assert result.passed is True
        assert result.blocking is False
        assert result.reasons == []


# ---------------------------------------------------------------------------
# PrescriptionGateway aggregation
# ---------------------------------------------------------------------------


class TestPrescriptionGateway:
    @pytest.mark.asyncio
    async def test_no_checkers_approves_with_info(self) -> None:
        gateway = PrescriptionGateway(checkers=[])
        decision = await gateway.check(_request())
        assert decision.decision == DecisionEnum.APPROVED
        assert decision.reasons[0].code == "UNCHECKED_NO_CHECKERS_CONFIGURED"
        assert decision.correlation_id

    @pytest.mark.asyncio
    async def test_all_pass_returns_approved(self) -> None:
        gateway = PrescriptionGateway(checkers=[_ok("a"), _ok("b")])
        decision = await gateway.check(_request())
        assert decision.decision == DecisionEnum.APPROVED
        assert decision.reasons == []
        assert {e.checker for e in decision.evidence} == {"a", "b"}

    @pytest.mark.asyncio
    async def test_non_blocking_failure_returns_review(self) -> None:
        gateway = PrescriptionGateway(checkers=[_ok("a"), _fail("b", blocking=False)])
        decision = await gateway.check(_request())
        assert decision.decision == DecisionEnum.REVIEW
        assert any(r.source_checker == "b" for r in decision.reasons)

    @pytest.mark.asyncio
    async def test_blocking_failure_short_circuits_to_rejected(self) -> None:
        third = _ok("c")
        gateway = PrescriptionGateway(
            checkers=[_ok("a"), _fail("b", blocking=True, severity="critical"), third]
        )
        decision = await gateway.check(_request())
        assert decision.decision == DecisionEnum.REJECTED
        assert {e.checker for e in decision.evidence} == {"a", "b"}

    @pytest.mark.asyncio
    async def test_reasons_sorted_by_severity(self) -> None:
        gateway = PrescriptionGateway(
            checkers=[
                _fail("warn", blocking=False, severity="warning"),
                _fail("crit", blocking=False, severity="critical"),
            ]
        )
        decision = await gateway.check(_request())
        assert [r.severity for r in decision.reasons] == ["critical", "warning"]

    @pytest.mark.asyncio
    async def test_correlation_id_is_passed_through(self) -> None:
        gateway = PrescriptionGateway(checkers=[_ok("a")])
        decision = await gateway.check(_request(), correlation_id="trace-xyz")
        assert decision.correlation_id == "trace-xyz"

    @pytest.mark.asyncio
    async def test_checker_exception_is_caught(self) -> None:
        @dataclass
        class Boom:
            name: str = "boom"

            async def check(self, request: PrescriptionRequest) -> CheckerResult:
                raise RuntimeError("kaboom")

        gateway = PrescriptionGateway(checkers=[Boom(), _ok("a")])
        decision = await gateway.check(_request())
        assert decision.decision == DecisionEnum.REVIEW
        assert any(r.code == "UNCHECKED_EXCEPTION" for r in decision.reasons)
        assert any(e.checker == "a" for e in decision.evidence)

    @pytest.mark.asyncio
    async def test_checker_with_bad_return_type_is_caught(self) -> None:
        @dataclass
        class Liar:
            name: str = "liar"

            async def check(self, request: PrescriptionRequest):  # type: ignore[no-untyped-def]
                return "not a CheckerResult"

        gateway = PrescriptionGateway(checkers=[Liar()])
        decision = await gateway.check(_request())
        assert decision.decision == DecisionEnum.REVIEW
        assert decision.reasons[0].code == "UNCHECKED_BAD_RETURN_TYPE"

    def test_invalid_mode_raises(self) -> None:
        with pytest.raises(ValueError):
            PrescriptionGateway(checkers=[], mode="invalid")

    @pytest.mark.asyncio
    async def test_end_to_end_with_default_checkers(self) -> None:
        gateway = PrescriptionGateway(
            checkers=[
                ForbiddenSubstanceChecker.from_iterable(["paraquat"]),
                DosageToleranceChecker(
                    rates={
                        ("wheat", "urea 46%"): RateRange(40, 60, "kg/ha"),
                    }
                ),
                PesticideComplianceCheckerAdapter(),
            ]
        )

        # 1. Forbidden product → REJECTED, short-circuits before dosage runs
        decision = await gateway.check(_request(product="Paraquat"))
        assert decision.decision == DecisionEnum.REJECTED
        assert {e.checker for e in decision.evidence} == {"forbidden_substance"}

        # 2. Allowed product but extreme dose → REJECTED via dosage hard limit
        decision = await gateway.check(_request(rate=200.0))
        assert decision.decision == DecisionEnum.REJECTED
        assert any(r.code == "DOSAGE_HARD_LIMIT_EXCEEDED" for r in decision.reasons)

        # 3. Allowed product, in-tolerance dose, non-pesticide → APPROVED
        decision = await gateway.check(_request(rate=50.0))
        assert decision.decision == DecisionEnum.APPROVED
