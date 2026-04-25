# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Unit tests for the power-good monitor (ADR-014)."""

from __future__ import annotations

import pytest

from shared.edge_resilience import (
    PowerMonitor,
    PowerState,
    ResilienceConfig,
)


@pytest.mark.asyncio
async def test_best_effort_yields_unknown_once_when_no_gpio() -> None:
    monitor = PowerMonitor(ResilienceConfig(supercap_gpio=None))
    states = [s async for s in monitor.states()]
    assert states == [PowerState.UNKNOWN]


@pytest.mark.asyncio
async def test_emits_normal_then_shutdown_on_transition() -> None:
    readings = iter([True, True, False])  # power-good, power-good, discharging

    def _read() -> bool:
        return next(readings)

    monitor = PowerMonitor(
        ResilienceConfig(supercap_gpio=17),
        poll_interval=0,
        reader=_read,
        max_iterations=3,
    )
    states = [s async for s in monitor.states()]
    assert states == [PowerState.NORMAL, PowerState.SHUTDOWN_SOON]


@pytest.mark.asyncio
async def test_only_emits_on_transition_not_every_poll() -> None:
    # Five "power-good" reads in a row → exactly one NORMAL emission.
    monitor = PowerMonitor(
        ResilienceConfig(supercap_gpio=17),
        poll_interval=0,
        reader=lambda: True,
        max_iterations=5,
    )
    states = [s async for s in monitor.states()]
    assert states == [PowerState.NORMAL]


@pytest.mark.asyncio
async def test_shutdown_soon_terminates_stream() -> None:
    monitor = PowerMonitor(
        ResilienceConfig(supercap_gpio=17),
        poll_interval=0,
        reader=lambda: False,
        max_iterations=10,
    )
    states = [s async for s in monitor.states()]
    # First read trips SHUTDOWN_SOON and the generator exits.
    assert states == [PowerState.SHUTDOWN_SOON]


@pytest.mark.asyncio
async def test_supports_async_reader() -> None:
    async def _async_read() -> bool:
        return False

    monitor = PowerMonitor(
        ResilienceConfig(supercap_gpio=17),
        poll_interval=0,
        reader=_async_read,
        max_iterations=2,
    )
    states = [s async for s in monitor.states()]
    assert states == [PowerState.SHUTDOWN_SOON]
