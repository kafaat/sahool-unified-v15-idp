"""
SAHOOL Outbox Replay Governance Policy Engine
==============================================
محرك سياسة الحوكمة لإعادة تشغيل الصندوق الصادر

Evaluates system health signals and decides whether replay should be
allowed to proceed.  Used as an optional layer inside
``DistributedReplayGovernor`` to move beyond a fixed rate limit toward
*adaptive* suppression that responds automatically to DLQ growth and
declining replay success rates.

Design
------
``ReplayPolicyEngine.evaluate(db_pool)`` queries ``outbox_messages`` for:

  * **DLQ growth rate**: rows that became dead-lettered in the last
    ``evaluate_window_seconds`` seconds, converted to rows/min.
  * **Replay success rate**: ``recovered / (recovered + failed_final)``
    for rows that reached a terminal replay state (``RECOVERED`` or
    ``FAILED_FINAL``) in the same window.

Two configurable thresholds in ``ReplayPolicy`` guard the decision:

  * ``dlq_growth_threshold`` (default 10 rows/min): if the DLQ is growing
    faster than this, further replay would add load without converging —
    suppress.
  * ``success_rate_floor`` (default 0.20): if fewer than 20 % of recent
    replay attempts recovered successfully, further replay is unlikely to
    help — suppress.

Both checks are skipped when their signals lack data (no DLQ rows or no
terminal replay rows in the window), so a fresh deployment with no
history is never incorrectly suppressed.

Usage
-----

Standalone::

    from shared.libs.outbox.replay_policy import ReplayPolicy, ReplayPolicyEngine

    engine = ReplayPolicyEngine(ReplayPolicy(dlq_growth_threshold=5, success_rate_floor=0.30))
    decision = await engine.evaluate(db_pool)
    if not decision.allowed:
        print(f"Replay suppressed: {decision.reason}")

Integrated with ``DistributedReplayGovernor``::

    from shared.libs.outbox.replay_tool import DistributedReplayGovernor
    from shared.libs.outbox.replay_policy import ReplayPolicy, ReplayPolicyEngine

    governor = DistributedReplayGovernor(
        pool,
        max_replays=5,
        window_seconds=3600,
        policy=ReplayPolicyEngine(ReplayPolicy(dlq_growth_threshold=10)),
    )

    # check() now evaluates the policy engine BEFORE the rate-limit COUNT
    await OutboxReplay.reset_dead_lettered(pool, guard=governor)

Notes
-----
* Requires the ``replay_state`` column (see ``migration.sql``) — specifically
  the ``'RECOVERED'`` and ``'FAILED_FINAL'`` values written by the relay.
* All queries are read-only; ``evaluate()`` never acquires any advisory lock.
* When ``total_terminal == 0`` (no replay outcomes yet in the window) the
  success-rate check is skipped so the system is never incorrectly suppressed
  at startup or after a long quiet period.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["ReplayPolicy", "PolicyDecision", "ReplayPolicyEngine"]

# ---------------------------------------------------------------------------
# SQL queries (read-only, no advisory lock)
# ---------------------------------------------------------------------------

_POLICY_DLQ_COUNT_SQL = """
SELECT COUNT(*) AS n
FROM outbox_messages
WHERE dead_lettered_at > NOW() - ($1 * INTERVAL '1 second')
"""

# Rows recovered after replay: published_at is set by the relay when it marks
# a REPLAYING row as successfully sent (replay_state transitions → RECOVERED).
_POLICY_RECOVERED_COUNT_SQL = """
SELECT COUNT(*) AS n
FROM outbox_messages
WHERE replay_state = 'RECOVERED'
  AND published_at > NOW() - ($1 * INTERVAL '1 second')
"""

# Rows that reached a terminal failure after replay: dead_lettered_at is
# refreshed when the relay marks a REPLAYING row as dead-lettered again
# (replay_state transitions → FAILED_FINAL).
_POLICY_FAILED_FINAL_COUNT_SQL = """
SELECT COUNT(*) AS n
FROM outbox_messages
WHERE replay_state = 'FAILED_FINAL'
  AND dead_lettered_at > NOW() - ($1 * INTERVAL '1 second')
"""


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ReplayPolicy:
    """Configuration knobs for the replay governance policy engine.

    Attributes:
        dlq_growth_threshold: Maximum DLQ growth rate (rows/min) before
            replay is suppressed.  Default ``10.0``.  Set lower (e.g. ``2.0``)
            in environments where any sustained DLQ growth is alarming.
        success_rate_floor: Minimum fraction of recent replay attempts that
            must have succeeded (``RECOVERED / (RECOVERED + FAILED_FINAL)``)
            for replay to be allowed.  Default ``0.20`` (20 %).  Set higher
            (e.g. ``0.50``) to require a healthier signal before re-enabling.
        evaluate_window_seconds: Look-back window (seconds) for both the DLQ
            rate and the success-rate calculations.  Default ``300`` (5 min).
            Minimum ``60`` seconds.  Shorter windows react faster to sudden
            degradation; longer windows smooth out transient spikes.
    """

    dlq_growth_threshold: float = 10.0
    success_rate_floor: float = 0.20
    evaluate_window_seconds: int = 300

    def __post_init__(self) -> None:
        if self.evaluate_window_seconds < 60:
            raise ValueError(
                f"evaluate_window_seconds must be >= 60 to avoid misleading rate "
                f"calculations; got {self.evaluate_window_seconds}"
            )


@dataclass
class PolicyDecision:
    """Result returned by ``ReplayPolicyEngine.evaluate()``.

    Attributes:
        allowed: ``True`` when replay should proceed; ``False`` when it
            should be suppressed.
        reason: Human-readable code explaining the decision.
            * ``"ok"``                  — all signals healthy, replay allowed.
            * ``"dlq_growth"``          — DLQ growth rate exceeds threshold.
            * ``"success_rate_too_low"``— recovered/failed ratio below floor.
    """

    allowed: bool
    reason: str


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class ReplayPolicyEngine:
    """
    Evaluates system health signals and returns a ``PolicyDecision``.

    Args:
        policy: Configuration for the two health-check thresholds.
            Defaults to ``ReplayPolicy()`` (sensible production defaults).

    Thread/async safety:
        ``evaluate()`` is a pure async read — it acquires no locks and
        performs three short ``SELECT COUNT(*)`` queries.  Multiple
        concurrent callers are safe.
    """

    def __init__(self, policy: ReplayPolicy | None = None) -> None:
        self._policy = policy or ReplayPolicy()

    @property
    def policy(self) -> ReplayPolicy:
        """The active ``ReplayPolicy`` configuration."""
        return self._policy

    async def evaluate(self, db_pool) -> PolicyDecision:
        """Query ``outbox_messages`` and return a ``PolicyDecision``.

        Checks:
        1. DLQ growth rate (rows/min in ``evaluate_window_seconds``).
        2. Replay success rate (``RECOVERED / (RECOVERED + FAILED_FINAL)``).

        Both checks are evaluated in a single pool-acquire block with three
        ``fetchrow`` calls.  The method never modifies any table and does not
        acquire advisory locks.

        Returns:
            ``PolicyDecision(allowed=True, reason="ok")`` when all signals
            are healthy, or ``PolicyDecision(allowed=False, reason=<code>)``
            when suppression is warranted.
        """
        window = self._policy.evaluate_window_seconds

        async with db_pool.acquire() as conn:
            dlq_row = await conn.fetchrow(_POLICY_DLQ_COUNT_SQL, window)
            recovered_row = await conn.fetchrow(_POLICY_RECOVERED_COUNT_SQL, window)
            failed_final_row = await conn.fetchrow(_POLICY_FAILED_FINAL_COUNT_SQL, window)

        recent_dlq = int(dlq_row["n"]) if dlq_row else 0
        recent_recovered = int(recovered_row["n"]) if recovered_row else 0
        recent_failed_final = int(failed_final_row["n"]) if failed_final_row else 0

        # --- Check 1: DLQ growth rate ---
        # Convert window count to rows/min.
        dlq_rate_per_min = (recent_dlq / window) * 60 if window > 0 else 0.0
        if dlq_rate_per_min >= self._policy.dlq_growth_threshold:
            return PolicyDecision(allowed=False, reason="dlq_growth")

        # --- Check 2: Replay success rate ---
        # Only evaluated when there is at least one terminal replay outcome in
        # the window to avoid false suppression at startup or after long quiet.
        total_terminal = recent_recovered + recent_failed_final
        if total_terminal > 0:
            success_rate = recent_recovered / total_terminal
            if success_rate < self._policy.success_rate_floor:
                return PolicyDecision(allowed=False, reason="success_rate_too_low")

        return PolicyDecision(allowed=True, reason="ok")
