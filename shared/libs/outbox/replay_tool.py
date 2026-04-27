"""
SAHOOL Outbox Replay Tool
=========================
أداة إعادة تشغيل الصندوق الصادر

Resets dead-lettered outbox rows so the relay picks them up again.

A row is dead-lettered when its ``retry_count`` reaches ``_MAX_RETRIES``.
Operators can inspect dead-lettered rows with:

    SELECT id, subject, tenant_id, retry_count, dead_lettered_at
    FROM outbox_messages
    WHERE dead_lettered_at IS NOT NULL
    ORDER BY dead_lettered_at;

Then replay all, a subset by subject, or individual rows by ID:

    # Python API
    from shared.libs.outbox.replay_tool import OutboxReplay

    # Dry-run inspection (no rows modified)
    info = await OutboxReplay.inspect_dead_lettered(pool)
    # → {"total": 5, "by_subject": {"sahool.ndvi.computed": 3}, "oldest_age_seconds": 7200}

    # Reset and record who triggered the replay (forensic audit)
    replayed = await OutboxReplay.reset_dead_lettered(pool, replayed_by="ops-team")
    replayed = await OutboxReplay.reset_dead_lettered(pool, subject="sahool.satellite.ndvi.computed", replayed_by="admin")
    replayed = await OutboxReplay.reset_dead_lettered(pool, ids=["<uuid>", "<uuid>"], replayed_by="automated-recovery")

    # CLI (run from repo root)
    python -m shared.libs.outbox.replay_tool --dsn postgresql://... --dry-run
    python -m shared.libs.outbox.replay_tool --dsn postgresql://... --list
    python -m shared.libs.outbox.replay_tool --dsn postgresql://... --replayed-by ops --subject sahool.satellite.ndvi.computed

After reset the relay will attempt to re-publish on the next poll tick.

⚠️  Replay safety
==================
The consumer's idempotency guard (``processed_events``) prevents duplicate
side-effects if the original message was already successfully processed before
the DLQ was triggered.

For complete write-side idempotency, side-effect tables MUST have:

    ALTER TABLE <side_effect_table>
    ADD CONSTRAINT uq_<table>_event_id UNIQUE (event_id);

This ensures that even if both the ``processed_events`` guard is missed *and*
the relay re-delivers, the DB write is physically idempotent.  See
``migration_idempotency.sql`` in this package for the pattern.

Replay does NOT guarantee delivery to the same consumer instance — it
re-enters the normal relay flow.  Ensure downstream consumers are idempotent
before replaying.

⚠️  Replay loop protection
===========================
A persistent delivery failure will cause an infinite replay loop unless
replays are rate-limited:

    DLQ grows → replay triggered → delivery fails again → DLQ grows again

Use ``OutboxReplayGuard`` to cap the number of replay operations per subject
within a rolling time window:

    from shared.libs.outbox.replay_tool import OutboxReplayGuard

    guard = OutboxReplayGuard(max_replays=5, window_seconds=3600)

    # Will raise ReplayRateLimitExceeded if > 5 replays/h for this subject
    await OutboxReplay.reset_dead_lettered(pool, subject="sahool.ndvi.computed",
                                           replayed_by="ops", guard=guard)

The guard is purely in-process (no extra DB table or external dependency).
State is scoped to the guard instance lifetime — create one long-lived guard
per process (e.g. in service lifespan) and pass it everywhere.  If the process
restarts the window resets, which is acceptable for operator-triggered replays
but means automated-recovery callers should share the same guard instance.

⚠️  Distributed replay governor (multi-instance)
==================================================
When multiple service replicas run concurrently each ``OutboxReplayGuard``
instance is isolated — one process cannot see the replay history of another.
Two replicas each configured with ``max_replays=5`` would allow up to 10
replays cluster-wide before any guard fires.

Use ``DistributedReplayGovernor`` instead to enforce cluster-wide limits
backed by the ``outbox_replay_ledger`` PostgreSQL table (see
``migration.sql``):

    from shared.libs.outbox.replay_tool import DistributedReplayGovernor

    governor = DistributedReplayGovernor(pool, max_replays=5, window_seconds=3600)

    await OutboxReplay.reset_dead_lettered(
        pool,
        subject="sahool.ndvi.computed",
        replayed_by="automated-recovery",
        guard=governor,          # ← same guard= parameter, DB-backed
    )

``DistributedReplayGovernor`` implements the same ``check()`` / ``record()``
interface as ``OutboxReplayGuard`` so callers are identical; swap is a one-line
change.  It requires no external cache (no Redis); only the PostgreSQL
connection pool that every outbox service already holds.
"""

from __future__ import annotations

import argparse
import asyncio
import collections
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Sequence
from uuid import UUID

from shared.libs.outbox.metrics import OUTBOX_METRICS

if TYPE_CHECKING:
    from shared.libs.outbox.replay_policy import ReplayPolicyEngine

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Replay loop protection
# ---------------------------------------------------------------------------


class ReplayRateLimitExceeded(Exception):
    """Raised by ``OutboxReplayGuard.check()`` when the per-subject replay
    rate exceeds ``max_replays`` within ``window_seconds``, or when
    ``ReplayPolicyEngine`` suppresses replay due to system health signals.

    Attributes:
        subject: The NATS subject (or ``"*"`` / ``"(ids)"``) that was blocked.
        replays_in_window: Number of replays already recorded in the window.
            Set to ``0`` for policy-driven suppressions.
        max_replays: Configured ceiling.
        window_seconds: Window duration in seconds.
        policy_reason: When set, suppression originated from the policy engine
            rather than the sliding-window counter.  Values: ``"dlq_growth"``,
            ``"success_rate_too_low"``.
    """

    def __init__(
        self,
        subject: str,
        replays_in_window: int,
        max_replays: int,
        window_seconds: int,
        policy_reason: str | None = None,
    ) -> None:
        self.subject = subject
        self.replays_in_window = replays_in_window
        self.max_replays = max_replays
        self.window_seconds = window_seconds
        self.policy_reason = policy_reason
        if policy_reason:
            msg = (
                f"Replay suppressed by policy for subject={subject!r}: "
                f"reason={policy_reason!r}.  Inspect DLQ growth and replay "
                f"success rate before re-enabling."
            )
        else:
            msg = (
                f"Replay rate limit exceeded for subject={subject!r}: "
                f"{replays_in_window}/{max_replays} replays in the last "
                f"{window_seconds}s.  Possible replay loop — inspect the DLQ "
                f"before retrying."
            )
        super().__init__(msg)


class OutboxReplayGuard:
    """
    In-process sliding-window rate limiter for outbox replay operations.

    Caps the number of ``reset_dead_lettered()`` calls per NATS subject
    within a rolling ``window_seconds`` window.  Prevents replay loops where
    a persistent delivery failure causes automated-recovery to replay the same
    dead-lettered rows indefinitely.

    State is scoped to the guard instance — create **one** long-lived guard
    per process (e.g. in the service lifespan) and pass it to every
    ``reset_dead_lettered()`` call.  If the process restarts the window
    resets, which is acceptable because operators can then re-assess the
    situation before triggering another replay.

    The guard is fully asyncio-safe: all internal state is protected by a
    single ``asyncio.Lock``.  It has no external dependencies (no DB table,
    no Redis, no network calls).

    Args:
        max_replays: Maximum number of replay operations allowed per subject
            within *window_seconds*.  Defaults to ``5``.
        window_seconds: Sliding window size in seconds.  Defaults to ``3600``
            (one hour).

    Usage::

        guard = OutboxReplayGuard(max_replays=5, window_seconds=3600)

        try:
            n = await OutboxReplay.reset_dead_lettered(
                pool,
                subject="sahool.ndvi.computed",
                replayed_by="ops",
                guard=guard,
            )
        except ReplayRateLimitExceeded as exc:
            logger.warning("replay_blocked", extra={"reason": str(exc)})
    """

    def __init__(self, max_replays: int = 5, window_seconds: int = 3600) -> None:
        if max_replays < 1:
            raise ValueError("max_replays must be >= 1")
        if window_seconds < 1:
            raise ValueError("window_seconds must be >= 1")
        self._max_replays = max_replays
        self._window_seconds = window_seconds
        # subject → deque of monotonic timestamps (seconds) of recent replays
        self._history: dict[str, collections.deque] = {}
        self._lock = asyncio.Lock()

    @property
    def max_replays(self) -> int:
        return self._max_replays

    @property
    def window_seconds(self) -> int:
        return self._window_seconds

    def _evict_expired(self, subject: str, now: float) -> None:
        """Remove timestamps outside the rolling window (must hold lock)."""
        cutoff = now - self._window_seconds
        dq = self._history.get(subject)
        if dq is not None:
            while dq and dq[0] < cutoff:
                dq.popleft()

    async def check(self, subject: str) -> None:
        """Assert the rate limit has not been exceeded for *subject*.

        Raises:
            ReplayRateLimitExceeded: if the number of replays recorded for
                *subject* within the sliding window equals or exceeds
                ``max_replays``.

        This is called by ``reset_dead_lettered()`` **before** acquiring the
        advisory lock and executing the UPDATE, so rejected calls never touch
        the database.
        """
        import time  # lazy import — only used in the guard, not the whole module

        async with self._lock:
            now = time.monotonic()
            self._evict_expired(subject, now)
            in_window = len(self._history.get(subject, ()))
            if in_window >= self._max_replays:
                raise ReplayRateLimitExceeded(
                    subject=subject,
                    replays_in_window=in_window,
                    max_replays=self._max_replays,
                    window_seconds=self._window_seconds,
                )

    async def record(self, subject: str, replayed_by: str = "system") -> None:
        """Record one successful replay for *subject*.

        Called by ``reset_dead_lettered()`` **after** the UPDATE commits so
        that the counter only advances when rows were actually reset.

        Args:
            subject: NATS subject (or ``"*"`` / ``"(ids)"``).
            replayed_by: Ignored for the in-process guard (state is anonymous).
                Accepted for API compatibility with ``DistributedReplayGovernor``.
        """
        import time

        async with self._lock:
            now = time.monotonic()
            self._evict_expired(subject, now)
            if subject not in self._history:
                self._history[subject] = collections.deque()
            self._history[subject].append(now)

    async def count_in_window(self, subject: str) -> int:
        """Return the current number of replays recorded for *subject* within
        the sliding window.  Safe to call at any time without side-effects."""
        import time

        async with self._lock:
            now = time.monotonic()
            self._evict_expired(subject, now)
            return len(self._history.get(subject, ()))

    def reset(self, subject: str | None = None) -> None:
        """Clear the replay history for *subject* (or all subjects if None).

        Intended for testing and for operator-triggered manual resets after
        a confirmed system recovery.  Not async-safe — call from sync context
        or wrap in ``asyncio.run_coroutine_threadsafe``.
        """
        if subject is None:
            self._history.clear()
        else:
            self._history.pop(subject, None)


# ---------------------------------------------------------------------------
# SQL for DistributedReplayGovernor
# ---------------------------------------------------------------------------

_GOVERNOR_COUNT_SQL = """
SELECT COUNT(*) AS n
FROM outbox_replay_ledger
WHERE subject = $1
  AND replayed_at > NOW() - ($2 * INTERVAL '1 second')
"""

_GOVERNOR_INSERT_SQL = """
INSERT INTO outbox_replay_ledger (subject, replayed_at, replayed_by, instance_id)
VALUES ($1, NOW(), $2, $3)
"""

# Read-only snapshot query for inspect_governor() — no advisory lock needed.
_GOVERNOR_INSPECT_SQL = """
SELECT
    COUNT(*)                                                              AS replays_in_window,
    MIN(replayed_at)                                                      AS oldest_replay_at,
    MAX(replayed_at)                                                      AS newest_replay_at,
    ARRAY_AGG(DISTINCT instance_id) FILTER (WHERE instance_id IS NOT NULL) AS instances_seen
FROM outbox_replay_ledger
WHERE subject = $1
  AND replayed_at > NOW() - ($2 * INTERVAL '1 second')
"""

# Transaction-level advisory lock for the governor: prevents two concurrent
# check+insert pairs from racing inside the same DB transaction.  Uses a
# different namespace key (1, 20291) to avoid colliding with the replay-tool
# advisory lock (1, 20290).
# Key mnemonics (hex → ASCII): 0x4F42 = "OB" (OutBox), 0x4F43 = "OC" (OutBox Coordination).
_GOVERNOR_LOCK_SQL = "SELECT pg_advisory_xact_lock(1, 20291)"


class DistributedReplayGovernor:
    """
    Cluster-wide sliding-window rate limiter for outbox replay operations.

    Enforces ``max_replays`` per NATS subject within a rolling
    ``window_seconds`` window **across all service instances** by recording
    every successful replay into the ``outbox_replay_ledger`` PostgreSQL table
    and querying it before each new replay attempt.

    This is the distributed successor to ``OutboxReplayGuard``.  Both classes
    implement the same ``check()`` / ``record()`` interface so they are
    interchangeable as the ``guard=`` argument to ``reset_dead_lettered()``.

    Design:
        * **No Redis / no external cache** — only the asyncpg pool already
          held by every outbox service.
        * ``check()`` opens a short transaction, acquires advisory lock
          ``pg_advisory_xact_lock(1, 20291)`` (OC = OutBox Coordination),
          counts rows in ``outbox_replay_ledger`` for the subject within the
          window, and raises ``ReplayRateLimitExceeded`` if the limit is
          reached.  The advisory lock serialises concurrent checkers so the
          count is always fresh before any insert.
        * When an optional ``policy`` is provided, ``check()`` calls
          ``await policy.evaluate(db_pool)`` **before** the advisory-lock
          COUNT.  If the policy suppresses replay,
          ``ReplayRateLimitExceeded`` is raised with ``policy_reason`` set.
        * ``record()`` inserts one row into ``outbox_replay_ledger`` after a
          successful ``reset_dead_lettered()`` commit.  ``check()`` does NOT
          insert — only ``record()`` does — so aborted or blocked replays
          never consume rate-limit budget.
        * Old ledger rows can be purged safely:
          ``DELETE FROM outbox_replay_ledger WHERE replayed_at < NOW() - INTERVAL '7 days'``

    Args:
        db_pool: asyncpg connection pool (shared with the outbox relay).
        max_replays: Maximum replays allowed per subject per *window_seconds*.
            Defaults to ``5``.
        window_seconds: Rolling window size in seconds.  Defaults to ``3600``.
        instance_id: Human-readable identifier for the current process (e.g.
            pod name, hostname).  Stored in ``outbox_replay_ledger.instance_id``
            for forensic tracing.  Defaults to ``None``.
        policy: Optional ``ReplayPolicyEngine`` for adaptive, SLO-driven
            suppression.  When provided, ``check()`` evaluates system health
            signals (DLQ growth rate, replay success rate) before the
            sliding-window COUNT.  Defaults to ``None`` (disabled).

    Usage::

        from shared.libs.outbox.replay_policy import ReplayPolicy, ReplayPolicyEngine

        governor = DistributedReplayGovernor(
            pool,
            max_replays=5,
            window_seconds=3600,
            instance_id="worker-pod-0",
            policy=ReplayPolicyEngine(ReplayPolicy(dlq_growth_threshold=5)),
        )

        try:
            n = await OutboxReplay.reset_dead_lettered(
                pool,
                subject="sahool.ndvi.computed",
                replayed_by="automated-recovery",
                guard=governor,
            )
        except ReplayRateLimitExceeded as exc:
            logger.warning("replay_blocked_cluster_wide",
                           extra={"reason": str(exc)})
    """

    def __init__(
        self,
        db_pool,
        max_replays: int = 5,
        window_seconds: int = 3600,
        instance_id: str | None = None,
        policy: ReplayPolicyEngine | None = None,
    ) -> None:
        if max_replays < 1:
            raise ValueError("max_replays must be >= 1")
        if window_seconds < 1:
            raise ValueError("window_seconds must be >= 1")
        self._db_pool = db_pool
        self._max_replays = max_replays
        self._window_seconds = window_seconds
        self._instance_id = instance_id
        self._policy = policy

    @property
    def max_replays(self) -> int:
        return self._max_replays

    @property
    def window_seconds(self) -> int:
        return self._window_seconds

    async def check(self, subject: str) -> None:
        """Assert the cluster-wide rate limit has not been exceeded for *subject*.

        When a ``policy`` was provided at construction time, the policy engine
        is evaluated first.  If it suppresses replay,
        ``ReplayRateLimitExceeded`` is raised with ``policy_reason`` set before
        any advisory lock or COUNT query is executed.

        Then acquires ``pg_advisory_xact_lock(1, 20291)`` inside a transaction
        to serialise concurrent callers, counts rows in
        ``outbox_replay_ledger`` for *subject* within the sliding window, and
        raises ``ReplayRateLimitExceeded`` if the count equals or exceeds
        ``max_replays``.

        Raises:
            ReplayRateLimitExceeded: if the policy engine suppresses replay,
                or if the sliding-window count equals or exceeds ``max_replays``.
        """
        # --- Policy check (no DB lock, read-only) ---
        if self._policy is not None:
            decision = await self._policy.evaluate(self._db_pool)
            if not decision.allowed:
                raise ReplayRateLimitExceeded(
                    subject=subject,
                    replays_in_window=0,
                    max_replays=self._max_replays,
                    window_seconds=self._window_seconds,
                    policy_reason=decision.reason,
                )

        # --- Sliding-window rate-limit check (advisory lock) ---
        async with self._db_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(_GOVERNOR_LOCK_SQL)
                row = await conn.fetchrow(
                    _GOVERNOR_COUNT_SQL, subject, self._window_seconds
                )
                in_window = int(row["n"]) if row else 0
                if in_window >= self._max_replays:
                    raise ReplayRateLimitExceeded(
                        subject=subject,
                        replays_in_window=in_window,
                        max_replays=self._max_replays,
                        window_seconds=self._window_seconds,
                    )

    async def record(self, subject: str, replayed_by: str = "system") -> None:
        """Insert one ledger row for *subject* after a successful replay.

        Called by ``reset_dead_lettered()`` **after** the UPDATE commits so
        that only rows that were actually reset are counted against the limit.

        Args:
            subject: NATS subject (or ``"*"`` / ``"(ids)"``).
            replayed_by: Same ``replayed_by`` passed to ``reset_dead_lettered()``.
                Stored in the ledger for forensic tracing.
        """
        async with self._db_pool.acquire() as conn:
            await conn.execute(
                _GOVERNOR_INSERT_SQL, subject, replayed_by, self._instance_id
            )

    async def count_in_window(self, subject: str) -> int:
        """Return the current cluster-wide replay count for *subject* within
        the sliding window.  Read-only; safe to call at any time."""
        async with self._db_pool.acquire() as conn:
            row = await conn.fetchrow(
                _GOVERNOR_COUNT_SQL, subject, self._window_seconds
            )
            return int(row["n"]) if row else 0

_RESET_ALL_SQL = """
UPDATE outbox_messages
SET dead_lettered_at = NULL,
    retry_count      = 0,
    claimed_at       = NULL,
    claimed_by       = NULL,
    replay_state     = 'REPLAYING'
WHERE dead_lettered_at IS NOT NULL
"""

_RESET_BY_SUBJECT_SQL = """
UPDATE outbox_messages
SET dead_lettered_at = NULL,
    retry_count      = 0,
    claimed_at       = NULL,
    claimed_by       = NULL,
    replay_state     = 'REPLAYING'
WHERE dead_lettered_at IS NOT NULL
  AND subject = $1
"""

_RESET_BY_IDS_SQL = """
UPDATE outbox_messages
SET dead_lettered_at = NULL,
    retry_count      = 0,
    claimed_at       = NULL,
    claimed_by       = NULL,
    replay_state     = 'REPLAYING'
WHERE dead_lettered_at IS NOT NULL
  AND id = ANY($1::uuid[])
"""

_COUNT_DLQ_SQL = """
SELECT COUNT(*) AS n
FROM outbox_messages
WHERE dead_lettered_at IS NOT NULL
"""

# Transaction-level advisory lock — automatically released on commit/rollback.
# Two-argument form uses (int4, int4): namespace=1 (SAHOOL outbox advisory-lock
# namespace), key=_ADVISORY_LOCK_KEY.
#
# A pre-computed literal integer is used instead of hashtext('outbox-replay')
# to avoid any dependency on the hashtext() function and to make the lock
# identity fully transparent in code review without requiring a DB query.
# The value 20290 was chosen as a stable, unique identifier for the outbox
# replay operation (hex 0x4F42 = "OB" for OutBox).
_ADVISORY_LOCK_KEY: int = 20290  # stable int4 key for "outbox-replay" within namespace 1
_ADVISORY_LOCK_SQL = f"SELECT pg_advisory_xact_lock(1, {_ADVISORY_LOCK_KEY})"

_LIST_DLQ_SQL = """
SELECT id, subject, tenant_id, retry_count, dead_lettered_at
FROM outbox_messages
WHERE dead_lettered_at IS NOT NULL
ORDER BY dead_lettered_at
"""

# Count by subject + oldest dead_lettered_at for dry-run inspection.
_INSPECT_DLQ_SQL = """
SELECT
    subject,
    COUNT(*) AS n,
    MIN(dead_lettered_at) AS oldest_dead_lettered_at
FROM outbox_messages
WHERE dead_lettered_at IS NOT NULL
GROUP BY subject
ORDER BY n DESC
"""


class OutboxReplay:
    """
    Async helpers for replaying dead-lettered outbox rows.

    All methods accept an asyncpg pool (or connection) and return the
    number of rows reset.
    """

    @staticmethod
    async def inspect_governor(
        db_pool,
        subject: str,
        window_seconds: int,
        max_replays: int | None = None,
    ) -> dict:
        """Return a read-only snapshot of governor state for *subject*.

        Queries ``outbox_replay_ledger`` for replays in the given window and
        returns a structured dict suitable for CLI display or Grafana JSON.

        This method is **safe and read-only** — it acquires no advisory lock
        and modifies nothing.

        Args:
            db_pool: asyncpg pool.
            subject: NATS subject to inspect (use ``"*"`` for the global
                all-subject wildcard if your governor uses that notation).
            window_seconds: Sliding window size in seconds to examine.
            max_replays: Optional ceiling from the governor configuration.
                When provided, ``utilization_pct`` is computed.  Pass
                ``governor.max_replays`` for an accurate reading.

        Returns:
            A dict with keys:
            ``replays_in_window``   — count of replays in the window.
            ``limit``               — *max_replays* if provided, else ``None``.
            ``window_seconds``      — the requested window size.
            ``is_blocked``          — ``True`` when
                                     ``replays_in_window >= limit`` (and
                                     *limit* is known).
            ``utilization_pct``     — window fill % (0–100), or ``None``.
            ``oldest_replay_at``    — ISO 8601 timestamp of the oldest ledger
                                     row in window, or ``None``.
            ``newest_replay_at``    — ISO 8601 timestamp of the most recent
                                     ledger row in window, or ``None``.
            ``instances_seen``      — list of distinct ``instance_id`` values
                                     that recorded replays in the window.

        Example::

            info = await OutboxReplay.inspect_governor(
                pool, "sahool.ndvi.computed", 3600, max_replays=5
            )
            # {
            #   "replays_in_window": 3,
            #   "limit": 5,
            #   "window_seconds": 3600,
            #   "is_blocked": False,
            #   "utilization_pct": 60.0,
            #   "oldest_replay_at": "2026-04-27T14:00:00+00:00",
            #   "newest_replay_at": "2026-04-27T15:30:00+00:00",
            #   "instances_seen": ["worker-pod-0", "worker-pod-1"],
            # }
        """
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(_GOVERNOR_INSPECT_SQL, subject, window_seconds)

        replays_in_window = int(row["replays_in_window"]) if row else 0
        oldest = row["oldest_replay_at"] if row else None
        newest = row["newest_replay_at"] if row else None
        instances = list(row["instances_seen"] or []) if row else []

        def _ts(dt: datetime | None) -> str | None:
            if dt is None:
                return None
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat()

        is_blocked: bool | None = None
        utilization_pct: float | None = None
        if max_replays is not None:
            is_blocked = replays_in_window >= max_replays
            utilization_pct = (replays_in_window / max_replays * 100) if max_replays > 0 else 0.0

        return {
            "replays_in_window": replays_in_window,
            "limit": max_replays,
            "window_seconds": window_seconds,
            "is_blocked": is_blocked,
            "utilization_pct": utilization_pct,
            "oldest_replay_at": _ts(oldest),
            "newest_replay_at": _ts(newest),
            "instances_seen": instances,
        }

    @staticmethod
    async def count_dead_lettered(db_pool) -> int:
        """Return the current number of dead-lettered rows."""
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(_COUNT_DLQ_SQL)
            return int(row["n"]) if row else 0

    @staticmethod
    async def list_dead_lettered(db_pool) -> list[dict]:
        """Return all dead-lettered rows as a list of dicts (for inspection)."""
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(_LIST_DLQ_SQL)
        return [dict(r) for r in rows]

    @staticmethod
    async def inspect_dead_lettered(db_pool) -> dict:
        """Return a dry-run summary of dead-lettered rows.

        Returns a dict with:
        ``total``              — total DLQ row count
        ``by_subject``         — dict mapping subject → row count
        ``oldest_age_seconds`` — age in seconds of the oldest DLQ row
                                 (``None`` when there are no DLQ rows)

        This is safe to call without modifying any rows.  Use it to
        understand the impact of a replay before triggering one.

        Example::

            info = await OutboxReplay.inspect_dead_lettered(pool)
            # {
            #   "total": 12,
            #   "by_subject": {
            #     "sahool.satellite.ndvi.computed": 9,
            #     "sahool.weather.updated": 3,
            #   },
            #   "oldest_age_seconds": 7200,
            # }
        """
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(_INSPECT_DLQ_SQL)

        if not rows:
            return {"total": 0, "by_subject": {}, "oldest_age_seconds": None}

        by_subject: dict[str, int] = {}
        total = 0
        oldest: datetime | None = None

        for r in rows:
            count = int(r["n"])
            by_subject[r["subject"]] = count
            total += count
            dlq_ts = r["oldest_dead_lettered_at"]
            if dlq_ts is not None:
                if oldest is None or dlq_ts < oldest:
                    oldest = dlq_ts

        oldest_age: float | None = None
        if oldest is not None:
            now = datetime.now(tz=timezone.utc)
            # asyncpg returns timezone-aware datetimes for TIMESTAMPTZ columns
            # and naive datetimes for plain TIMESTAMP columns.  Both cases are
            # handled: timezone-aware values are compared directly; naive
            # values are assumed UTC and converted before computing the age.
            if oldest.tzinfo is None:
                oldest = oldest.replace(tzinfo=timezone.utc)
            oldest_age = (now - oldest).total_seconds()

        return {
            "total": total,
            "by_subject": by_subject,
            "oldest_age_seconds": oldest_age,
        }

    @staticmethod
    async def reset_dead_lettered(
        db_pool,
        *,
        subject: str | None = None,
        ids: Sequence[str | UUID] | None = None,
        replayed_by: str = "system",
        guard: OutboxReplayGuard | DistributedReplayGovernor | None = None,
    ) -> int:
        """
        Reset dead-lettered rows so the relay retries them.

        Args:
            db_pool: asyncpg pool.
            subject: If given, reset only rows matching this NATS subject.
            ids: If given, reset only the listed row UUIDs.
                 ``subject`` and ``ids`` are mutually exclusive.
            replayed_by: Human-readable identifier of who/what triggered the
                replay.  Stored in the structured audit log record for forensic
                tracing.  Examples: ``"ops-team"``, ``"admin-ui"``,
                ``"automated-recovery"``.
            guard: Optional rate-limit guard.  Accepts either an
                ``OutboxReplayGuard`` (in-process, single-instance) or a
                ``DistributedReplayGovernor`` (DB-backed, cluster-wide).  When
                provided, the rate limit is checked **before** any DLQ UPDATE.
                If the rate limit is exceeded a ``ReplayRateLimitExceeded``
                exception is raised immediately — no rows are modified and the
                ``outbox_replay_blocked_total`` metric is incremented.

        Returns:
            Number of rows reset.

        Raises:
            ValueError: if both *subject* and *ids* are provided.
            ReplayRateLimitExceeded: if *guard* is set and the per-subject
                rate limit has been exceeded.
        """
        if subject is not None and ids is not None:
            raise ValueError("Provide either 'subject' or 'ids', not both.")

        # Determine metric labels before touching the DB.
        if ids is not None:
            reason = "by_ids"
            metric_subject = "(ids)"
        elif subject is not None:
            reason = "by_subject"
            metric_subject = subject
        else:
            reason = "all"
            metric_subject = "*"

        # --- Rate-limit check (before advisory lock / DB round-trip) ---
        if guard is not None:
            try:
                await guard.check(metric_subject)
            except ReplayRateLimitExceeded as exc:
                blocked_reason = "policy" if exc.policy_reason else "rate_limit"
                OUTBOX_METRICS.replay_blocked(subject=metric_subject, reason=blocked_reason)
                if exc.policy_reason:
                    OUTBOX_METRICS.replay_policy_suppressed(reason=exc.policy_reason)
                raise

        # Acquire a transaction-level advisory lock before mutating rows.
        # This serializes concurrent replay callers (two ops-team members,
        # automated-recovery + CLI) so they cannot reset the same DLQ rows
        # simultaneously — which would produce wasted relay load and
        # misleading audit log entries.  The lock is released automatically
        # when the transaction commits or rolls back.
        async with db_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(_ADVISORY_LOCK_SQL)
                if ids is not None:
                    str_ids = [str(i) for i in ids]
                    status = await conn.execute(_RESET_BY_IDS_SQL, str_ids)
                elif subject is not None:
                    status = await conn.execute(_RESET_BY_SUBJECT_SQL, subject)
                else:
                    status = await conn.execute(_RESET_ALL_SQL)

        # asyncpg returns a status string like "UPDATE 5"
        try:
            count = int(status.split()[-1])
        except (IndexError, ValueError):
            count = 0

        # Record replay volume in Prometheus so it can be tracked alongside
        # the DLQ rate (outbox_dead_lettered_total) in dashboards and SLOs.
        if count > 0:
            OUTBOX_METRICS.record_replay(subject=metric_subject, reason=reason, count=count)
            # Advance the guard window only when rows were actually reset so
            # no-op replays (count == 0) do not consume rate-limit budget.
            if guard is not None:
                await guard.record(metric_subject, replayed_by=replayed_by)

        # Forensic audit log — every replay is permanently traceable.
        logger.info(
            "outbox_replay_reset",
            extra={
                "rows_reset": count,
                "replayed_by": replayed_by,
                "replayed_at": datetime.now(tz=timezone.utc).isoformat(),
                "filter_subject": subject,
                "filter_ids": [str(i) for i in ids] if ids else None,
            },
        )
        return count


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m shared.libs.outbox.replay_tool",
        description="Reset dead-lettered outbox rows so the relay retries them.",
    )
    p.add_argument(
        "--dsn",
        required=True,
        help="asyncpg-compatible PostgreSQL DSN, e.g. postgresql://user:pass@host/db",
    )
    p.add_argument(
        "--subject",
        default=None,
        help="Reset only rows matching this NATS subject.",
    )
    p.add_argument(
        "--id",
        dest="ids",
        nargs="*",
        default=None,
        help="Reset only these row UUIDs (space-separated).",
    )
    p.add_argument(
        "--list",
        action="store_true",
        help="List all dead-lettered rows (id, subject, retries, age) and exit.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Show a summary (total, by-subject count, oldest age) without "
            "modifying any rows.  Use this to assess impact before replaying."
        ),
    )
    p.add_argument(
        "--replayed-by",
        dest="replayed_by",
        default="cli",
        help="Identifier stored in the audit log for this replay operation (default: cli).",
    )
    p.add_argument(
        "--governor-status",
        dest="governor_status",
        action="store_true",
        help=(
            "Show the current governor state for --subject: replays in window, "
            "utilisation %%, oldest/newest replay timestamps, and instances seen.  "
            "Requires --subject and --window-seconds / --max-replays."
        ),
    )
    p.add_argument(
        "--window-seconds",
        dest="window_seconds",
        type=int,
        default=3600,
        help="Governor sliding-window size in seconds (default: 3600).  Used with --governor-status.",
    )
    p.add_argument(
        "--max-replays",
        dest="max_replays",
        type=int,
        default=None,
        help="Governor ceiling (max_replays).  When given with --governor-status, shows utilisation %%.",
    )
    return p


async def _main(args: argparse.Namespace) -> None:
    try:
        import asyncpg
    except ImportError:
        print("ERROR: asyncpg is required. Install it with: pip install asyncpg")
        raise SystemExit(1)

    pool = await asyncpg.create_pool(args.dsn, min_size=1, max_size=2)
    try:
        if args.governor_status:
            subject = args.subject or "*"
            info = await OutboxReplay.inspect_governor(
                pool,
                subject=subject,
                window_seconds=args.window_seconds,
                max_replays=args.max_replays,
            )
            print(f"Governor status for subject={subject!r}  window={args.window_seconds}s")
            print("-" * 60)
            print(f"  Replays in window : {info['replays_in_window']}")
            if info["limit"] is not None:
                blocked_str = "YES (blocking)" if info["is_blocked"] else "no"
                print(f"  Limit             : {info['limit']}")
                print(f"  Utilisation       : {info['utilization_pct']:.1f}%")
                print(f"  Blocked           : {blocked_str}")
            print(f"  Oldest replay     : {info['oldest_replay_at'] or 'n/a'}")
            print(f"  Newest replay     : {info['newest_replay_at'] or 'n/a'}")
            instances = info["instances_seen"]
            print(f"  Instances seen    : {', '.join(instances) if instances else 'none'}")
            return

        if args.dry_run:
            info = await OutboxReplay.inspect_dead_lettered(pool)
            if info["total"] == 0:
                print("No dead-lettered rows.")
                return
            print(f"Dead-lettered rows: {info['total']}")
            if info["oldest_age_seconds"] is not None:
                hours = info["oldest_age_seconds"] / 3600
                print(f"Oldest row age:     {hours:.1f} hours")
            print("\nBy subject:")
            for subj, n in sorted(info["by_subject"].items(), key=lambda kv: -kv[1]):
                print(f"  {n:>6}  {subj}")
            print("\n(dry-run — no rows modified)")
            return

        if args.list:
            rows = await OutboxReplay.list_dead_lettered(pool)
            if not rows:
                print("No dead-lettered rows.")
                return
            now = datetime.now(tz=timezone.utc)
            print(f"{'ID':<38}  {'SUBJECT':<45}  {'RETRIES':>7}  {'AGE':>10}  DEAD_LETTERED_AT")
            print("-" * 120)
            for r in rows:
                dlq_ts = r["dead_lettered_at"]
                if dlq_ts is not None:
                    if dlq_ts.tzinfo is None:
                        dlq_ts = dlq_ts.replace(tzinfo=timezone.utc)
                    age_h = f"{(now - dlq_ts).total_seconds() / 3600:.1f}h"
                else:
                    age_h = "?"
                print(
                    f"{str(r['id']):<38}  {r['subject']:<45}  {r['retry_count']:>7}  {age_h:>10}  {r['dead_lettered_at']}"
                )
            return

        count = await OutboxReplay.reset_dead_lettered(
            pool,
            subject=args.subject,
            ids=args.ids,
            replayed_by=args.replayed_by,
        )
        print(f"Reset {count} dead-lettered row(s).  (replayed_by={args.replayed_by!r})")
    finally:
        await pool.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _args = _build_parser().parse_args()
    asyncio.run(_main(_args))
