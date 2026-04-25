# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Unit tests for the crash-safe WAL (ADR-014)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from shared.edge_resilience import ResilienceConfig, WriteAheadLog


def _cfg(tmp: Path, **kwargs: object) -> ResilienceConfig:
    return ResilienceConfig(
        wal_path=str(tmp),
        wal_max_bytes=kwargs.pop("wal_max_bytes", 4096),
        fsync_batch_size=kwargs.pop("fsync_batch_size", 1),
        **kwargs,  # type: ignore[arg-type]
    )


@pytest.mark.asyncio
async def test_append_and_replay_round_trip(tmp_path: Path) -> None:
    wal = WriteAheadLog(_cfg(tmp_path))
    try:
        await wal.append(b"hello")
        await wal.append(b"world")
        await wal.flush()
        entries = [e async for e in wal.replay()]
    finally:
        wal.close()

    assert [e.payload for e in entries] == [b"hello", b"world"]
    assert [e.sequence for e in entries] == [1, 2]


@pytest.mark.asyncio
async def test_replay_skips_acked_entries(tmp_path: Path) -> None:
    wal = WriteAheadLog(_cfg(tmp_path))
    try:
        e1 = await wal.append(b"a")
        await wal.append(b"b")
        await wal.append(b"c")
        await wal.truncate_to(e1.sequence)  # ack first only
        # truncate_to rotates only when *all* entries are acked, so file
        # is still intact and we can verify cursor filtering.
        entries = [e async for e in wal.replay()]
        assert [e.payload for e in entries] == [b"b", b"c"]
    finally:
        wal.close()


@pytest.mark.asyncio
async def test_full_truncate_rotates_log(tmp_path: Path) -> None:
    wal = WriteAheadLog(_cfg(tmp_path))
    try:
        for i in range(5):
            entry = await wal.append(f"p{i}".encode())
        await wal.truncate_to(entry.sequence)
        # Log file should be empty after a full ack.
        assert wal.fill_ratio() == 0.0
        # Subsequent appends restart sequence numbering.
        new = await wal.append(b"after-rotate")
        assert new.sequence == 1
    finally:
        wal.close()


@pytest.mark.asyncio
async def test_replay_after_reopen_recovers_state(tmp_path: Path) -> None:
    wal = WriteAheadLog(_cfg(tmp_path))
    try:
        await wal.append(b"durable-1")
        await wal.append(b"durable-2")
        await wal.flush()
    finally:
        wal.close()

    # Re-open simulates a crash + restart.
    wal2 = WriteAheadLog(_cfg(tmp_path))
    try:
        entries = [e async for e in wal2.replay()]
        assert [e.payload for e in entries] == [b"durable-1", b"durable-2"]
        # New appends continue numbering after the highest existing sequence.
        e3 = await wal2.append(b"durable-3")
        assert e3.sequence == 3
    finally:
        wal2.close()


@pytest.mark.asyncio
async def test_replay_handles_torn_tail(tmp_path: Path) -> None:
    wal = WriteAheadLog(_cfg(tmp_path))
    try:
        await wal.append(b"good-1")
        await wal.append(b"good-2")
        await wal.flush()
    finally:
        wal.close()

    # Append a partial / corrupt frame to simulate a power-cut mid-write.
    log_file = tmp_path / "wal.log"
    with log_file.open("ab") as fh:
        fh.write(b"\x00" * 12)  # not enough bytes to form a valid header

    wal2 = WriteAheadLog(_cfg(tmp_path))
    try:
        entries = [e async for e in wal2.replay()]
        assert [e.payload for e in entries] == [b"good-1", b"good-2"]
    finally:
        wal2.close()


@pytest.mark.asyncio
async def test_fill_ratio_tracks_size(tmp_path: Path) -> None:
    wal = WriteAheadLog(_cfg(tmp_path, wal_max_bytes=512))
    try:
        assert wal.fill_ratio() == 0.0
        await wal.append(b"x" * 100)
        await wal.flush()
        ratio = wal.fill_ratio()
        # Header (28 B) + payload (100 B) ≈ 0.25 of 512.
        assert 0.20 <= ratio <= 0.40
    finally:
        wal.close()


@pytest.mark.asyncio
async def test_close_is_idempotent(tmp_path: Path) -> None:
    wal = WriteAheadLog(_cfg(tmp_path))
    wal.close()
    wal.close()  # must not raise
    with pytest.raises(RuntimeError, match="closed"):
        await wal.append(b"after-close")


def test_init_creates_directory(tmp_path: Path) -> None:
    sub = tmp_path / "deep" / "nested" / "wal"
    wal = WriteAheadLog(ResilienceConfig(wal_path=str(sub)))
    try:
        assert os.path.isdir(sub)
    finally:
        wal.close()
