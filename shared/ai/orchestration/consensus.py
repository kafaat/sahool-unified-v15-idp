"""
Consensus Protocols
===================
بروتوكولات الإجماع

Distributed consensus protocols for multi-agent decision making.
Provides various voting and agreement mechanisms.

Inspired by Claude-Flow architecture and distributed systems theory.

Protocols:
- RaftConsensus: Sequential consistency with leader election
- MajorityVoting: Simple majority wins
- WeightedVoting: Expertise-based weighted votes
- UnanimousConsensus: All agents must agree
- QuorumConsensus: Minimum quorum required

البروتوكولات:
- إجماع Raft: الاتساق التسلسلي مع انتخاب القائد
- التصويت بالأغلبية: الأغلبية البسيطة تفوز
- التصويت الموزون: أصوات موزونة على أساس الخبرة
- الإجماع بالإجماع: يجب موافقة جميع الوكلاء
- إجماع النصاب: الحد الأدنى من النصاب مطلوب

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, UTC
from typing import Any, TypeVar

import structlog

from .models import (
    ConsensusResult,
    ConsensusType,
    Vote,
)

logger = structlog.get_logger()

T = TypeVar("T")


# ─────────────────────────────────────────────────────────────────────────────
# Base Protocol
# ─────────────────────────────────────────────────────────────────────────────


class ConsensusProtocol(ABC):
    """
    Base class for consensus protocols.
    الفئة الأساسية لبروتوكولات الإجماع

    All consensus protocols must implement the reach_consensus method
    to determine agreement among voting agents.

    يجب على جميع بروتوكولات الإجماع تنفيذ طريقة reach_consensus
    لتحديد الاتفاق بين الوكلاء المصوتين.
    """

    def __init__(
        self,
        threshold: float = 0.5,
        timeout_seconds: int = 30,
        max_rounds: int = 3,
    ):
        """
        Initialize consensus protocol.
        تهيئة بروتوكول الإجماع

        Args:
            threshold: العتبة - Minimum agreement ratio required (0-1)
            timeout_seconds: المهلة - Maximum time for consensus
            max_rounds: الجولات القصوى - Maximum voting rounds
        """
        self.threshold = threshold
        self.timeout_seconds = timeout_seconds
        self.max_rounds = max_rounds
        self._stats = {
            "consensus_reached": 0,
            "consensus_failed": 0,
            "total_rounds": 0,
            "avg_agreement_ratio": 0.0,
        }

    @property
    @abstractmethod
    def protocol_type(self) -> ConsensusType:
        """Get the consensus type | الحصول على نوع الإجماع"""
        pass

    @abstractmethod
    async def reach_consensus(
        self,
        votes: list[Vote],
        context: dict[str, Any] | None = None,
    ) -> ConsensusResult:
        """
        Attempt to reach consensus from votes.
        محاولة التوصل إلى إجماع من الأصوات

        Args:
            votes: الأصوات - List of votes from agents
            context: السياق - Optional context for decision making

        Returns:
            ConsensusResult: نتيجة الإجماع - Result with decision and confidence
        """
        pass

    def _update_stats(self, result: ConsensusResult) -> None:
        """Update protocol statistics."""
        if result.reached:
            self._stats["consensus_reached"] += 1
        else:
            self._stats["consensus_failed"] += 1

        self._stats["total_rounds"] += result.rounds

        # Update rolling average
        total = self._stats["consensus_reached"] + self._stats["consensus_failed"]
        old_avg = self._stats["avg_agreement_ratio"]
        self._stats["avg_agreement_ratio"] = (
            (old_avg * (total - 1) + result.agreement_ratio) / total
        )

    def get_stats(self) -> dict[str, Any]:
        """Get protocol statistics | الحصول على إحصائيات البروتوكول"""
        return {
            **self._stats,
            "protocol_type": self.protocol_type.value,
            "threshold": self.threshold,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Majority Voting
# ─────────────────────────────────────────────────────────────────────────────


class MajorityVoting(ConsensusProtocol):
    """
    Simple majority voting consensus.
    إجماع التصويت بالأغلبية البسيطة

    The option with the most votes wins if it exceeds the threshold.
    يفوز الخيار الذي يحصل على أكثر الأصوات إذا تجاوز العتبة.

    Example:
        >>> protocol = MajorityVoting(threshold=0.5)
        >>> votes = [
        ...     Vote(agent_id="a1", value="option_a"),
        ...     Vote(agent_id="a2", value="option_a"),
        ...     Vote(agent_id="a3", value="option_b"),
        ... ]
        >>> result = await protocol.reach_consensus(votes)
        >>> print(f"Decision: {result.decision}, Agreement: {result.agreement_ratio:.2%}")
    """

    @property
    def protocol_type(self) -> ConsensusType:
        return ConsensusType.MAJORITY_VOTING

    async def reach_consensus(
        self,
        votes: list[Vote],
        context: dict[str, Any] | None = None,
    ) -> ConsensusResult:
        """Reach consensus by simple majority."""
        start_time = datetime.now(UTC)

        if not votes:
            return ConsensusResult(
                consensus_type=self.protocol_type,
                reached=False,
                reasoning="No votes received",
                reasoning_ar="لم يتم استلام أصوات",
            )

        # Count votes for each value
        vote_counts: dict[str, list[Vote]] = defaultdict(list)
        for vote in votes:
            key = str(vote.value)
            vote_counts[key].append(vote)

        # Find the winner
        total_votes = len(votes)
        winner_key = max(vote_counts.keys(), key=lambda k: len(vote_counts[k]))
        winner_votes = vote_counts[winner_key]
        winner_count = len(winner_votes)
        agreement_ratio = winner_count / total_votes

        # Check threshold
        reached = agreement_ratio >= self.threshold

        # Calculate confidence (weighted by individual confidences)
        avg_confidence = sum(v.confidence for v in winner_votes) / winner_count

        # Find dissenting agents
        dissenting = [
            v.agent_id for v in votes
            if str(v.value) != winner_key
        ]

        duration_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

        result = ConsensusResult(
            consensus_type=self.protocol_type,
            reached=reached,
            decision=winner_votes[0].value if reached else None,
            votes=votes,
            total_votes=total_votes,
            agreement_ratio=agreement_ratio,
            confidence=avg_confidence if reached else 0.0,
            rounds=1,
            dissenting_agents=dissenting,
            reasoning=(
                f"Majority voting: {winner_count}/{total_votes} votes ({agreement_ratio:.1%}) "
                f"for decision. Threshold: {self.threshold:.1%}. "
                f"{'Consensus reached.' if reached else 'Consensus NOT reached.'}"
            ),
            reasoning_ar=(
                f"التصويت بالأغلبية: {winner_count}/{total_votes} صوت ({agreement_ratio:.1%}) "
                f"للقرار. العتبة: {self.threshold:.1%}. "
                f"{'تم التوصل للإجماع.' if reached else 'لم يتم التوصل للإجماع.'}"
            ),
            duration_ms=duration_ms,
        )

        self._update_stats(result)

        logger.info(
            "majority_voting_completed",
            reached=reached,
            agreement_ratio=agreement_ratio,
            total_votes=total_votes,
            winner_votes=winner_count,
        )

        return result


# ─────────────────────────────────────────────────────────────────────────────
# Weighted Voting
# ─────────────────────────────────────────────────────────────────────────────


class WeightedVoting(ConsensusProtocol):
    """
    Weighted voting based on agent expertise.
    التصويت الموزون بناءً على خبرة الوكيل

    Votes are weighted by the vote.weight field, allowing more experienced
    or specialized agents to have more influence.

    يتم ترجيح الأصوات بواسطة حقل الوزن، مما يسمح للوكلاء الأكثر خبرة
    أو تخصصاً بالتأثير بشكل أكبر.

    Example:
        >>> protocol = WeightedVoting(threshold=0.6)
        >>> votes = [
        ...     Vote(agent_id="expert", value="a", weight=2.0),
        ...     Vote(agent_id="novice", value="b", weight=1.0),
        ... ]
        >>> result = await protocol.reach_consensus(votes)
    """

    @property
    def protocol_type(self) -> ConsensusType:
        return ConsensusType.WEIGHTED_VOTING

    async def reach_consensus(
        self,
        votes: list[Vote],
        context: dict[str, Any] | None = None,
    ) -> ConsensusResult:
        """Reach consensus by weighted voting."""
        start_time = datetime.now(UTC)

        if not votes:
            return ConsensusResult(
                consensus_type=self.protocol_type,
                reached=False,
                reasoning="No votes received",
                reasoning_ar="لم يتم استلام أصوات",
            )

        # Calculate weighted votes for each value
        weighted_counts: dict[str, float] = defaultdict(float)
        vote_groups: dict[str, list[Vote]] = defaultdict(list)

        total_weight = sum(v.weight for v in votes)

        for vote in votes:
            key = str(vote.value)
            # Weight is multiplied by confidence
            effective_weight = vote.weight * vote.confidence
            weighted_counts[key] += effective_weight
            vote_groups[key].append(vote)

        # Find the winner
        winner_key = max(weighted_counts.keys(), key=lambda k: weighted_counts[k])
        winner_weight = weighted_counts[winner_key]
        winner_votes = vote_groups[winner_key]

        # Calculate agreement ratio based on weights
        agreement_ratio = winner_weight / (total_weight * max(v.confidence for v in votes))
        agreement_ratio = min(1.0, agreement_ratio)  # Cap at 1.0

        # Check threshold
        reached = agreement_ratio >= self.threshold

        # Confidence is the weighted average of winner confidences
        winner_total_weight = sum(v.weight for v in winner_votes)
        confidence = (
            sum(v.weight * v.confidence for v in winner_votes) / winner_total_weight
            if winner_total_weight > 0 else 0.0
        )

        # Find dissenting agents
        dissenting = [
            v.agent_id for v in votes
            if str(v.value) != winner_key
        ]

        duration_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

        result = ConsensusResult(
            consensus_type=self.protocol_type,
            reached=reached,
            decision=winner_votes[0].value if reached else None,
            votes=votes,
            total_votes=len(votes),
            agreement_ratio=agreement_ratio,
            confidence=confidence if reached else 0.0,
            rounds=1,
            dissenting_agents=dissenting,
            reasoning=(
                f"Weighted voting: {winner_weight:.2f}/{total_weight:.2f} weighted votes "
                f"({agreement_ratio:.1%}) for decision. Threshold: {self.threshold:.1%}. "
                f"{'Consensus reached.' if reached else 'Consensus NOT reached.'}"
            ),
            reasoning_ar=(
                f"التصويت الموزون: {winner_weight:.2f}/{total_weight:.2f} أصوات موزونة "
                f"({agreement_ratio:.1%}) للقرار. العتبة: {self.threshold:.1%}. "
                f"{'تم التوصل للإجماع.' if reached else 'لم يتم التوصل للإجماع.'}"
            ),
            duration_ms=duration_ms,
        )

        self._update_stats(result)

        logger.info(
            "weighted_voting_completed",
            reached=reached,
            agreement_ratio=agreement_ratio,
            winner_weight=winner_weight,
            total_weight=total_weight,
        )

        return result


# ─────────────────────────────────────────────────────────────────────────────
# Raft Consensus
# ─────────────────────────────────────────────────────────────────────────────


class RaftConsensus(ConsensusProtocol):
    """
    Raft-inspired sequential consensus protocol.
    بروتوكول إجماع متسلسل مستوحى من Raft

    Implements a simplified Raft-like protocol with:
    - Leader election based on term and vote confidence
    - Sequential proposal and acceptance
    - Multiple rounds if consensus not reached

    ينفذ بروتوكولاً مبسطاً شبيهاً بـ Raft مع:
    - انتخاب القائد بناءً على المدة وثقة التصويت
    - الاقتراح والقبول المتسلسل
    - جولات متعددة إذا لم يتم التوصل للإجماع

    Example:
        >>> protocol = RaftConsensus(threshold=0.5, max_rounds=3)
        >>> votes = [
        ...     Vote(agent_id="a1", value="proposal_1", confidence=0.9),
        ...     Vote(agent_id="a2", value="proposal_2", confidence=0.7),
        ...     Vote(agent_id="a3", value="proposal_1", confidence=0.8),
        ... ]
        >>> result = await protocol.reach_consensus(votes)
    """

    def __init__(
        self,
        threshold: float = 0.5,
        timeout_seconds: int = 30,
        max_rounds: int = 3,
    ):
        super().__init__(threshold, timeout_seconds, max_rounds)
        self._current_term = 0
        self._current_leader: str | None = None

    @property
    def protocol_type(self) -> ConsensusType:
        return ConsensusType.RAFT

    async def reach_consensus(
        self,
        votes: list[Vote],
        context: dict[str, Any] | None = None,
    ) -> ConsensusResult:
        """Reach consensus using Raft-inspired protocol."""
        start_time = datetime.now(UTC)
        context = context or {}

        if not votes:
            return ConsensusResult(
                consensus_type=self.protocol_type,
                reached=False,
                reasoning="No votes received",
                reasoning_ar="لم يتم استلام أصوات",
            )

        rounds_used = 0
        current_votes = votes.copy()
        final_decision = None
        final_agreement = 0.0
        final_confidence = 0.0

        for round_num in range(1, self.max_rounds + 1):
            rounds_used = round_num
            self._current_term += 1

            # Phase 1: Leader election
            leader = self._elect_leader(current_votes)
            self._current_leader = leader.agent_id

            logger.debug(
                "raft_leader_elected",
                term=self._current_term,
                leader=leader.agent_id,
                round=round_num,
            )

            # Phase 2: Leader proposes
            proposal = leader.value

            # Phase 3: Count acceptances (votes matching proposal)
            acceptances = [v for v in current_votes if str(v.value) == str(proposal)]
            acceptance_ratio = len(acceptances) / len(current_votes)

            final_decision = proposal
            final_agreement = acceptance_ratio
            final_confidence = (
                sum(v.confidence for v in acceptances) / len(acceptances)
                if acceptances else 0.0
            )

            # Check if consensus reached
            if acceptance_ratio >= self.threshold:
                break

            # Prepare for next round - agents may change votes
            # In a real Raft, this would involve log replication
            # Here we simulate by removing lowest-confidence dissenters
            if round_num < self.max_rounds:
                dissenters = [v for v in current_votes if str(v.value) != str(proposal)]
                if dissenters:
                    # Convert lowest confidence dissenter
                    weakest = min(dissenters, key=lambda v: v.confidence)
                    # Create new vote aligned with leader
                    converted_vote = Vote(
                        agent_id=weakest.agent_id,
                        value=proposal,
                        confidence=weakest.confidence * 0.8,  # Reduced confidence
                        weight=weakest.weight,
                        reasoning=f"Aligned with leader in round {round_num}",
                        reasoning_ar=f"تم التوافق مع القائد في الجولة {round_num}",
                    )
                    current_votes = [
                        v if v.agent_id != weakest.agent_id else converted_vote
                        for v in current_votes
                    ]

        reached = final_agreement >= self.threshold
        dissenting = [
            v.agent_id for v in current_votes
            if str(v.value) != str(final_decision)
        ]

        duration_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

        result = ConsensusResult(
            consensus_type=self.protocol_type,
            reached=reached,
            decision=final_decision if reached else None,
            votes=current_votes,
            total_votes=len(votes),
            agreement_ratio=final_agreement,
            confidence=final_confidence if reached else 0.0,
            rounds=rounds_used,
            dissenting_agents=dissenting,
            reasoning=(
                f"Raft consensus: Term {self._current_term}, Leader: {self._current_leader}. "
                f"{rounds_used} round(s), {final_agreement:.1%} agreement. "
                f"{'Consensus reached.' if reached else 'Consensus NOT reached.'}"
            ),
            reasoning_ar=(
                f"إجماع Raft: المدة {self._current_term}، القائد: {self._current_leader}. "
                f"{rounds_used} جولة، {final_agreement:.1%} اتفاق. "
                f"{'تم التوصل للإجماع.' if reached else 'لم يتم التوصل للإجماع.'}"
            ),
            duration_ms=duration_ms,
        )

        self._update_stats(result)

        logger.info(
            "raft_consensus_completed",
            reached=reached,
            term=self._current_term,
            rounds=rounds_used,
            agreement_ratio=final_agreement,
        )

        return result

    def _elect_leader(self, votes: list[Vote]) -> Vote:
        """
        Elect leader based on confidence and weight.
        انتخاب القائد بناءً على الثقة والوزن
        """
        # Leader is the vote with highest (confidence * weight)
        return max(votes, key=lambda v: v.confidence * v.weight)

    def get_current_term(self) -> int:
        """Get current term number | الحصول على رقم المدة الحالية"""
        return self._current_term

    def get_current_leader(self) -> str | None:
        """Get current leader ID | الحصول على معرف القائد الحالي"""
        return self._current_leader


# ─────────────────────────────────────────────────────────────────────────────
# Unanimous Consensus
# ─────────────────────────────────────────────────────────────────────────────


class UnanimousConsensus(ConsensusProtocol):
    """
    Unanimous consensus - all agents must agree.
    إجماع بالإجماع - يجب موافقة جميع الوكلاء

    Used for critical decisions where complete agreement is required.
    يُستخدم للقرارات الحرجة التي تتطلب الموافقة الكاملة.

    Example:
        >>> protocol = UnanimousConsensus()
        >>> votes = [
        ...     Vote(agent_id="a1", value="approve"),
        ...     Vote(agent_id="a2", value="approve"),
        ...     Vote(agent_id="a3", value="approve"),
        ... ]
        >>> result = await protocol.reach_consensus(votes)
        >>> print(f"Unanimous: {result.reached}")  # True
    """

    def __init__(self, timeout_seconds: int = 30, max_rounds: int = 1):
        super().__init__(threshold=1.0, timeout_seconds=timeout_seconds, max_rounds=max_rounds)

    @property
    def protocol_type(self) -> ConsensusType:
        return ConsensusType.UNANIMOUS

    async def reach_consensus(
        self,
        votes: list[Vote],
        context: dict[str, Any] | None = None,
    ) -> ConsensusResult:
        """Reach consensus only if all votes agree."""
        start_time = datetime.now(UTC)

        if not votes:
            return ConsensusResult(
                consensus_type=self.protocol_type,
                reached=False,
                reasoning="No votes received",
                reasoning_ar="لم يتم استلام أصوات",
            )

        # Check if all votes have the same value
        first_value = str(votes[0].value)
        all_agree = all(str(v.value) == first_value for v in votes)

        agreement_ratio = 1.0 if all_agree else (
            max(
                sum(1 for v in votes if str(v.value) == val)
                for val in {str(v.value) for v in votes}
            ) / len(votes)
        )

        dissenting = [
            v.agent_id for v in votes
            if str(v.value) != first_value
        ]

        # Confidence is average of all confidences if unanimous
        confidence = (
            sum(v.confidence for v in votes) / len(votes)
            if all_agree else 0.0
        )

        duration_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

        result = ConsensusResult(
            consensus_type=self.protocol_type,
            reached=all_agree,
            decision=votes[0].value if all_agree else None,
            votes=votes,
            total_votes=len(votes),
            agreement_ratio=agreement_ratio,
            confidence=confidence,
            rounds=1,
            dissenting_agents=dissenting,
            reasoning=(
                f"Unanimous consensus: {len(votes)} votes. "
                f"{'All agents agree.' if all_agree else f'{len(dissenting)} agent(s) dissent.'}"
            ),
            reasoning_ar=(
                f"إجماع بالإجماع: {len(votes)} صوت. "
                f"{'جميع الوكلاء متفقون.' if all_agree else f'{len(dissenting)} وكيل مختلف.'}"
            ),
            duration_ms=duration_ms,
        )

        self._update_stats(result)

        logger.info(
            "unanimous_consensus_completed",
            reached=all_agree,
            total_votes=len(votes),
            dissenting=len(dissenting),
        )

        return result


# ─────────────────────────────────────────────────────────────────────────────
# Quorum Consensus
# ─────────────────────────────────────────────────────────────────────────────


class QuorumConsensus(ConsensusProtocol):
    """
    Quorum-based consensus with minimum participants.
    إجماع على أساس النصاب مع الحد الأدنى من المشاركين

    Requires a minimum number of votes before evaluating consensus.
    يتطلب حداً أدنى من الأصوات قبل تقييم الإجماع.

    Example:
        >>> protocol = QuorumConsensus(threshold=0.5, min_quorum=3)
        >>> # Will fail if fewer than 3 votes received
    """

    def __init__(
        self,
        threshold: float = 0.5,
        timeout_seconds: int = 30,
        min_quorum: int = 3,
        max_rounds: int = 1,
    ):
        super().__init__(threshold, timeout_seconds, max_rounds)
        self.min_quorum = min_quorum

    @property
    def protocol_type(self) -> ConsensusType:
        return ConsensusType.QUORUM

    async def reach_consensus(
        self,
        votes: list[Vote],
        context: dict[str, Any] | None = None,
    ) -> ConsensusResult:
        """Reach consensus with quorum requirement."""
        start_time = datetime.now(UTC)

        # Check quorum
        if len(votes) < self.min_quorum:
            return ConsensusResult(
                consensus_type=self.protocol_type,
                reached=False,
                votes=votes,
                total_votes=len(votes),
                agreement_ratio=0.0,
                reasoning=(
                    f"Quorum not met: {len(votes)}/{self.min_quorum} votes received."
                ),
                reasoning_ar=(
                    f"لم يتم الوصول للنصاب: {len(votes)}/{self.min_quorum} صوت تم استلامه."
                ),
                duration_ms=(datetime.now(UTC) - start_time).total_seconds() * 1000,
            )

        # Use majority voting once quorum is met
        vote_counts: dict[str, list[Vote]] = defaultdict(list)
        for vote in votes:
            key = str(vote.value)
            vote_counts[key].append(vote)

        winner_key = max(vote_counts.keys(), key=lambda k: len(vote_counts[k]))
        winner_votes = vote_counts[winner_key]
        agreement_ratio = len(winner_votes) / len(votes)

        reached = agreement_ratio >= self.threshold

        confidence = (
            sum(v.confidence for v in winner_votes) / len(winner_votes)
            if winner_votes else 0.0
        )

        dissenting = [
            v.agent_id for v in votes
            if str(v.value) != winner_key
        ]

        duration_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

        result = ConsensusResult(
            consensus_type=self.protocol_type,
            reached=reached,
            decision=winner_votes[0].value if reached else None,
            votes=votes,
            total_votes=len(votes),
            agreement_ratio=agreement_ratio,
            confidence=confidence if reached else 0.0,
            rounds=1,
            dissenting_agents=dissenting,
            reasoning=(
                f"Quorum consensus: {len(votes)}/{self.min_quorum} quorum met. "
                f"{len(winner_votes)}/{len(votes)} votes ({agreement_ratio:.1%}) for decision. "
                f"{'Consensus reached.' if reached else 'Consensus NOT reached.'}"
            ),
            reasoning_ar=(
                f"إجماع النصاب: {len(votes)}/{self.min_quorum} تم الوصول للنصاب. "
                f"{len(winner_votes)}/{len(votes)} صوت ({agreement_ratio:.1%}) للقرار. "
                f"{'تم التوصل للإجماع.' if reached else 'لم يتم التوصل للإجماع.'}"
            ),
            duration_ms=duration_ms,
        )

        self._update_stats(result)

        logger.info(
            "quorum_consensus_completed",
            reached=reached,
            quorum_met=True,
            total_votes=len(votes),
            agreement_ratio=agreement_ratio,
        )

        return result


# ─────────────────────────────────────────────────────────────────────────────
# Consensus Manager
# ─────────────────────────────────────────────────────────────────────────────


class ConsensusManager:
    """
    Manager for consensus protocols.
    مدير بروتوكولات الإجماع

    Provides a unified interface for different consensus protocols
    and handles protocol selection based on context.

    يوفر واجهة موحدة لبروتوكولات الإجماع المختلفة
    ويتعامل مع اختيار البروتوكول بناءً على السياق.

    Example:
        >>> manager = ConsensusManager()
        >>> votes = [Vote(agent_id="a1", value="yes"), ...]
        >>> result = await manager.reach_consensus(
        ...     votes,
        ...     protocol_type=ConsensusType.MAJORITY_VOTING,
        ... )
    """

    def __init__(self, default_protocol: ConsensusType = ConsensusType.MAJORITY_VOTING):
        """
        Initialize consensus manager.
        تهيئة مدير الإجماع

        Args:
            default_protocol: البروتوكول الافتراضي - Default protocol type
        """
        self.default_protocol = default_protocol

        # Protocol instances
        self._protocols: dict[ConsensusType, ConsensusProtocol] = {
            ConsensusType.MAJORITY_VOTING: MajorityVoting(),
            ConsensusType.WEIGHTED_VOTING: WeightedVoting(),
            ConsensusType.RAFT: RaftConsensus(),
            ConsensusType.UNANIMOUS: UnanimousConsensus(),
            ConsensusType.QUORUM: QuorumConsensus(),
        }

    def get_protocol(self, protocol_type: ConsensusType) -> ConsensusProtocol:
        """Get protocol instance | الحصول على نسخة البروتوكول"""
        return self._protocols.get(
            protocol_type,
            self._protocols[self.default_protocol],
        )

    def configure_protocol(
        self,
        protocol_type: ConsensusType,
        threshold: float | None = None,
        timeout_seconds: int | None = None,
        max_rounds: int | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Configure a protocol's parameters.
        تكوين معاملات البروتوكول

        Args:
            protocol_type: نوع البروتوكول - Protocol to configure
            threshold: العتبة - New threshold value
            timeout_seconds: المهلة - New timeout
            max_rounds: الجولات القصوى - New max rounds
            **kwargs: معاملات إضافية - Protocol-specific parameters
        """
        protocol = self._protocols.get(protocol_type)
        if not protocol:
            return

        if threshold is not None:
            protocol.threshold = threshold
        if timeout_seconds is not None:
            protocol.timeout_seconds = timeout_seconds
        if max_rounds is not None:
            protocol.max_rounds = max_rounds

        # Protocol-specific configuration
        if protocol_type == ConsensusType.QUORUM and "min_quorum" in kwargs:
            if isinstance(protocol, QuorumConsensus):
                protocol.min_quorum = kwargs["min_quorum"]

    async def reach_consensus(
        self,
        votes: list[Vote],
        protocol_type: ConsensusType | None = None,
        context: dict[str, Any] | None = None,
    ) -> ConsensusResult:
        """
        Reach consensus using specified or default protocol.
        التوصل للإجماع باستخدام البروتوكول المحدد أو الافتراضي

        Args:
            votes: الأصوات - List of votes
            protocol_type: نوع البروتوكول - Protocol to use (optional)
            context: السياق - Additional context

        Returns:
            ConsensusResult: نتيجة الإجماع
        """
        protocol_type = protocol_type or self.default_protocol
        protocol = self.get_protocol(protocol_type)
        return await protocol.reach_consensus(votes, context)

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for all protocols | الحصول على إحصائيات جميع البروتوكولات"""
        return {
            protocol_type.value: protocol.get_stats()
            for protocol_type, protocol in self._protocols.items()
        }


# ─────────────────────────────────────────────────────────────────────────────
# Module-level Functions
# ─────────────────────────────────────────────────────────────────────────────

_consensus_manager: ConsensusManager | None = None


def get_consensus_manager() -> ConsensusManager:
    """Get the global consensus manager | الحصول على مدير الإجماع العام"""
    global _consensus_manager
    if _consensus_manager is None:
        _consensus_manager = ConsensusManager()
    return _consensus_manager


async def reach_consensus(
    votes: list[Vote],
    protocol_type: ConsensusType = ConsensusType.MAJORITY_VOTING,
    context: dict[str, Any] | None = None,
) -> ConsensusResult:
    """
    Convenience function to reach consensus.
    دالة مساعدة للتوصل للإجماع

    Args:
        votes: الأصوات - List of votes
        protocol_type: نوع البروتوكول - Consensus protocol to use
        context: السياق - Optional context

    Returns:
        ConsensusResult: نتيجة الإجماع
    """
    manager = get_consensus_manager()
    return await manager.reach_consensus(votes, protocol_type, context)
