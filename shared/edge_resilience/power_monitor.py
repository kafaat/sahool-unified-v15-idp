# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Power-good monitor — see ADR-014.

Two backends:

* **sysfs**: when ``ResilienceConfig.supercap_gpio`` is set, the monitor
  reads ``/sys/class/gpio/gpio{N}/value`` on a fixed cadence and emits
  ``SHUTDOWN_SOON`` whenever the line goes low (supercap discharging).
* **best-effort**: when no GPIO is configured, the monitor immediately
  yields ``UNKNOWN`` once and stays silent — devices without a supercap
  still benefit from the WAL but cannot guarantee a 5-s grace window.

The monitor is async-iterable so callers can integrate it with a normal
``async for`` shutdown coroutine in ``edge-orchestrator-service``.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from pathlib import Path

from .models import PowerState, ResilienceConfig

#: Default poll interval for the sysfs backend. Edge devices typically run
#: this at 100 Hz, but tests inject a faster cadence via ``poll_interval``.
DEFAULT_POLL_INTERVAL_S = 0.05


class PowerMonitor:
    """Subscribes to a GPIO / sysfs power-good line.

    When supercap discharge starts, transitions to ``SHUTDOWN_SOON`` and
    the orchestrator has at least 5 s to flush WAL + close NATS cleanly.
    Devices without a configured GPIO operate in best-effort mode and
    only ever report ``UNKNOWN``.
    """

    def __init__(
        self,
        config: ResilienceConfig,
        *,
        poll_interval: float = DEFAULT_POLL_INTERVAL_S,
        reader: Callable[[], Awaitable[bool] | bool] | None = None,
        max_iterations: int | None = None,
    ) -> None:
        self.config = config
        self._poll_interval = poll_interval
        self._reader = reader
        # ``max_iterations`` keeps tests bounded; ``None`` means run forever.
        self._max_iterations = max_iterations

    async def states(self) -> AsyncIterator[PowerState]:
        """Async generator yielding power-state transitions.

        Emits ``UNKNOWN`` once when no GPIO is configured. Otherwise polls
        the configured reader and yields a state on every transition.
        """

        if self.config.supercap_gpio is None and self._reader is None:
            yield PowerState.UNKNOWN
            return

        last: PowerState | None = None
        read = self._build_reader()
        iterations = 0
        while self._max_iterations is None or iterations < self._max_iterations:
            iterations += 1
            ok = await _maybe_await(read())
            new = PowerState.NORMAL if ok else PowerState.SHUTDOWN_SOON
            if new != last:
                last = new
                yield new
            if new is PowerState.SHUTDOWN_SOON:
                # Once we've signalled imminent shutdown, the orchestrator
                # owns the grace window — stop polling so we don't churn.
                return
            await asyncio.sleep(self._poll_interval)

    # -- internals -------------------------------------------------------

    def _build_reader(self) -> Callable[[], Awaitable[bool] | bool]:
        if self._reader is not None:
            return self._reader
        gpio = self.config.supercap_gpio
        path = Path(f"/sys/class/gpio/gpio{gpio}/value")

        def _read() -> bool:
            try:
                return path.read_text().strip() == "1"
            except OSError:
                # Treat I/O errors as "power good" so a transient sysfs
                # glitch never falsely triggers a shutdown sequence.
                return True

        return _read


async def _maybe_await(result):  # type: ignore[no-untyped-def]
    if asyncio.iscoroutine(result) or isinstance(result, Awaitable):
        return await result
    return result
