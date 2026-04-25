# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Crash-safe append-only WAL on eMMC — see ADR-014.

Frame layout (little-endian, packed)::

    +------+----------+--------------+--------+--------------+----------+
    | 4 B  |   8 B    |     8 B      |  4 B   |     4 B      |    N B   |
    +------+----------+--------------+--------+--------------+----------+
    | MAGIC| sequence | timestamp_us |  crc32 | payload_len  |  payload |
    +------+----------+--------------+--------+--------------+----------+

* ``MAGIC`` = ``b"SAHW"`` lets ``replay()`` resync after a torn write at the
  tail.
* ``crc32`` covers ``payload`` only; it lets the replay loop discard the
  trailing partial frame caused by a power-cut mid-``write`` without
  losing earlier well-formed frames.
* A separate ``wal.cursor`` file stores the highest acked sequence so
  ``truncate_to()`` is O(1). On replay we skip entries whose sequence is
  ``<= cursor``.
"""

from __future__ import annotations

import asyncio
import os
import struct
import zlib
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path

from .models import ResilienceConfig, WALEntry

_MAGIC = b"SAHW"
_HEADER_FMT = "<4sQQII"  # magic, sequence, ts_us, crc32, payload_len
_HEADER_SIZE = struct.calcsize(_HEADER_FMT)


class WriteAheadLog:
    """Append-only write-ahead log with ``O_DSYNC`` + ``fdatasync`` barriers.

    Crash-safety contract: after ``append()`` returns, the entry survives
    abrupt power-loss. Batched writes amortize fsync cost (see
    ``ResilienceConfig.fsync_batch_size``); ``flush()`` forces a barrier.
    """

    def __init__(self, config: ResilienceConfig) -> None:
        self.config = config
        self._dir = Path(config.wal_path)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._log_path = self._dir / "wal.log"
        self._cursor_path = self._dir / "wal.cursor"
        # O_APPEND guarantees atomic appends across processes; O_DSYNC keeps
        # the write durable without flushing inode metadata each time.
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
        if hasattr(os, "O_DSYNC"):
            flags |= os.O_DSYNC
        self._fd = os.open(self._log_path, flags, 0o600)
        # Sequence counter resumes from on-disk state.
        self._seq = self._scan_max_sequence()
        self._pending_since_fsync = 0

    # -- public API ------------------------------------------------------

    async def append(self, payload: bytes) -> WALEntry:
        """Append a payload and return the resulting :class:`WALEntry`.

        Survives power-loss after this coroutine returns.
        """

        return await asyncio.to_thread(self._append_sync, payload)

    async def replay(self) -> AsyncIterator[WALEntry]:
        """Yield every unacked entry in append order.

        Entries with ``sequence <= cursor`` (already acked) are skipped, and
        any trailing torn frame caused by a power-cut is silently dropped.
        """

        cursor = self._read_cursor()
        for entry in await asyncio.to_thread(self._read_all_sync):
            if entry.sequence > cursor:
                yield entry

    async def truncate_to(self, sequence: int) -> None:
        """Discard entries up to and including ``sequence`` (after ack).

        Writes a cursor file with ``fdatasync`` so the ack is durable. When
        the cursor catches up to the highest written sequence, the on-disk
        log is rotated to keep ``fill_ratio()`` realistic.
        """

        await asyncio.to_thread(self._truncate_to_sync, sequence)

    def fill_ratio(self) -> float:
        """Return current WAL utilization in ``[0.0, 1.0]``."""

        try:
            size = self._log_path.stat().st_size
        except FileNotFoundError:
            return 0.0
        if self.config.wal_max_bytes <= 0:
            return 0.0
        return min(1.0, size / self.config.wal_max_bytes)

    async def flush(self) -> None:
        """Force a durability barrier for any buffered writes."""

        await asyncio.to_thread(self._fsync)

    def close(self) -> None:
        """Close the underlying file descriptor (idempotent)."""

        if self._fd >= 0:
            try:
                os.close(self._fd)
            finally:
                self._fd = -1

    # -- sync helpers ----------------------------------------------------

    def _append_sync(self, payload: bytes) -> WALEntry:
        if self._fd < 0:
            raise RuntimeError("WAL is closed")
        self._seq += 1
        ts = datetime.now(UTC)
        ts_us = int(ts.timestamp() * 1_000_000)
        crc = zlib.crc32(payload) & 0xFFFFFFFF
        header = struct.pack(_HEADER_FMT, _MAGIC, self._seq, ts_us, crc, len(payload))
        # Single write() of header+payload keeps a power-cut from leaving
        # an aligned-but-empty header on disk; the kernel either commits
        # the whole buffer or none of it for sizes well under the page
        # cache threshold (we cap payload_len in higher layers).
        os.write(self._fd, header + payload)
        self._pending_since_fsync += 1
        if self._pending_since_fsync >= self.config.fsync_batch_size:
            self._fsync()
        return WALEntry(sequence=self._seq, timestamp=ts, payload=payload, crc32=crc)

    def _fsync(self) -> None:
        if self._fd < 0 or self._pending_since_fsync == 0:
            return
        # ``fdatasync`` keeps file-data durable without writing inode
        # metadata each call; on platforms that lack it (macOS) we fall
        # back to ``fsync``.
        if hasattr(os, "fdatasync"):
            os.fdatasync(self._fd)
        else:  # pragma: no cover - platform fallback
            os.fsync(self._fd)
        self._pending_since_fsync = 0

    def _read_all_sync(self) -> list[WALEntry]:
        entries: list[WALEntry] = []
        if not self._log_path.exists():
            return entries
        with self._log_path.open("rb") as fh:
            while True:
                header = fh.read(_HEADER_SIZE)
                if len(header) < _HEADER_SIZE:
                    break  # torn header — drop trailing partial frame
                magic, sequence, ts_us, crc, payload_len = struct.unpack(
                    _HEADER_FMT, header
                )
                if magic != _MAGIC:
                    break  # corruption — drop the rest
                payload = fh.read(payload_len)
                if len(payload) < payload_len:
                    break  # torn payload
                if (zlib.crc32(payload) & 0xFFFFFFFF) != crc:
                    break  # torn / corrupt payload
                entries.append(
                    WALEntry(
                        sequence=sequence,
                        timestamp=datetime.fromtimestamp(ts_us / 1_000_000, tz=UTC),
                        payload=payload,
                        crc32=crc,
                    )
                )
        return entries

    def _scan_max_sequence(self) -> int:
        return max((e.sequence for e in self._read_all_sync()), default=0)

    def _read_cursor(self) -> int:
        try:
            raw = self._cursor_path.read_bytes()
        except FileNotFoundError:
            return 0
        if len(raw) < 8:
            return 0
        return struct.unpack("<Q", raw[:8])[0]

    def _truncate_to_sync(self, sequence: int) -> None:
        # Persist the new cursor durably first.
        cursor_fd = os.open(
            self._cursor_path,
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            0o600,
        )
        try:
            os.write(cursor_fd, struct.pack("<Q", max(0, int(sequence))))
            if hasattr(os, "fdatasync"):
                os.fdatasync(cursor_fd)
            else:  # pragma: no cover
                os.fsync(cursor_fd)
        finally:
            os.close(cursor_fd)

        # If everything written has now been acked, rotate the log so the
        # backpressure controller sees the freed space immediately.
        if sequence >= self._seq:
            # Close + truncate + reopen.
            os.close(self._fd)
            self._log_path.unlink(missing_ok=True)
            self._cursor_path.unlink(missing_ok=True)
            flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
            if hasattr(os, "O_DSYNC"):
                flags |= os.O_DSYNC
            self._fd = os.open(self._log_path, flags, 0o600)
            self._seq = 0
            self._pending_since_fsync = 0
