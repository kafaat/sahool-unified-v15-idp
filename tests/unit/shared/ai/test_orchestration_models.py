"""
Tests for shared/ai/orchestration/models.py
=============================================

Tests cover:
- All enums: SwarmTopology, AgentCapability, TaskPriority, TaskStatus,
  ConsensusType, MemoryNamespace
- Pydantic models: AgentProfile, AgentScore, AgentState, Task, TaskResult,
  SwarmConfig, SwarmState, SwarmResult, Vote, ConsensusResult, MemoryEntry,
  PatternMatch, MemoryStats, RoutingDecision, RouterStats
- Properties: success_rate, ucb_score, is_expired
- Default values and field validation
"""

import math
from datetime import UTC, datetime, timedelta

import pytest

from shared.ai.orchestration.models import (
    AgentCapability,
    AgentProfile,
    AgentScore,
    AgentState,
    ConsensusResult,
    ConsensusType,
    MemoryEntry,
    MemoryNamespace,
    MemoryStats,
    PatternMatch,
    RoutingDecision,
    RouterStats,
    SwarmConfig,
    SwarmResult,
    SwarmState,
    SwarmTopology,
    Task,
    TaskPriority,
    TaskResult,
    TaskStatus,
    Vote,
)


# ─────────────────────────────────────────────────────────────────────────────
# Enum Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestSwarmTopology:
    def test_all_values(self):
        assert SwarmTopology.MESH.value == "mesh"
        assert SwarmTopology.HIERARCHICAL.value == "hierarchical"
        assert SwarmTopology.STAR.value == "star"
        assert SwarmTopology.RING.value == "ring"
        assert SwarmTopology.PIPELINE.value == "pipeline"

    def test_member_count(self):
        assert len(SwarmTopology) == 5


class TestAgentCapability:
    def test_all_values(self):
        assert AgentCapability.CROP_ANALYSIS.value == "crop_analysis"
        assert AgentCapability.IRRIGATION.value == "irrigation"
        assert AgentCapability.PEST_DETECTION.value == "pest_detection"
        assert AgentCapability.WEATHER_ANALYSIS.value == "weather_analysis"
        assert AgentCapability.SOIL_ANALYSIS.value == "soil_analysis"
        assert AgentCapability.YIELD_PREDICTION.value == "yield_prediction"
        assert AgentCapability.ADVISORY.value == "advisory"
        assert AgentCapability.RESEARCH.value == "research"
        assert AgentCapability.PLANNING.value == "planning"
        assert AgentCapability.GENERAL.value == "general"

    def test_member_count(self):
        assert len(AgentCapability) == 10


class TestTaskPriority:
    def test_all_values(self):
        assert TaskPriority.CRITICAL.value == "critical"
        assert TaskPriority.HIGH.value == "high"
        assert TaskPriority.MEDIUM.value == "medium"
        assert TaskPriority.LOW.value == "low"

    def test_member_count(self):
        assert len(TaskPriority) == 4


class TestTaskStatus:
    def test_all_values(self):
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.ROUTING.value == "routing"
        assert TaskStatus.ASSIGNED.value == "assigned"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.AGGREGATING.value == "aggregating"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"

    def test_member_count(self):
        assert len(TaskStatus) == 8


class TestConsensusType:
    def test_all_values(self):
        assert ConsensusType.RAFT.value == "raft"
        assert ConsensusType.MAJORITY_VOTING.value == "majority_voting"
        assert ConsensusType.WEIGHTED_VOTING.value == "weighted_voting"
        assert ConsensusType.UNANIMOUS.value == "unanimous"
        assert ConsensusType.QUORUM.value == "quorum"

    def test_member_count(self):
        assert len(ConsensusType) == 5


class TestMemoryNamespace:
    def test_all_values(self):
        assert MemoryNamespace.TASKS.value == "tasks"
        assert MemoryNamespace.PATTERNS.value == "patterns"
        assert MemoryNamespace.DECISIONS.value == "decisions"
        assert MemoryNamespace.KNOWLEDGE.value == "knowledge"
        assert MemoryNamespace.AGENTS.value == "agents"
        assert MemoryNamespace.ERRORS.value == "errors"

    def test_member_count(self):
        assert len(MemoryNamespace) == 6


# ─────────────────────────────────────────────────────────────────────────────
# Agent Model Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestAgentProfile:
    def test_creation(self):
        profile = AgentProfile(
            agent_id="agent-1",
            name="Crop Advisor",
            name_ar="مستشار المحاصيل",
        )
        assert profile.agent_id == "agent-1"
        assert profile.name == "Crop Advisor"
        assert profile.name_ar == "مستشار المحاصيل"
        assert profile.capabilities == []
        assert profile.specialization is None
        assert profile.metadata == {}
        assert profile.created_at is not None

    def test_with_capabilities(self):
        profile = AgentProfile(
            agent_id="agent-1",
            name="Expert",
            name_ar="خبير",
            capabilities=[AgentCapability.CROP_ANALYSIS, AgentCapability.PEST_DETECTION],
        )
        # use_enum_values=True means they are stored as strings
        assert "crop_analysis" in profile.capabilities
        assert "pest_detection" in profile.capabilities


class TestAgentScore:
    def test_defaults(self):
        score = AgentScore(
            agent_id="a1",
            capability=AgentCapability.IRRIGATION,
        )
        assert score.success_count == 0
        assert score.failure_count == 0
        assert score.total_tasks == 0
        assert score.avg_execution_time_ms == 0.0
        assert score.q_value == 0.5
        assert score.exploration_bonus == 0.1

    def test_success_rate_no_tasks(self):
        score = AgentScore(agent_id="a1", capability=AgentCapability.IRRIGATION)
        assert score.success_rate == 0.5  # Default for new agents

    def test_success_rate_with_tasks(self):
        score = AgentScore(
            agent_id="a1",
            capability=AgentCapability.IRRIGATION,
            success_count=8,
            total_tasks=10,
        )
        assert score.success_rate == 0.8

    def test_ucb_score_no_tasks(self):
        score = AgentScore(agent_id="a1", capability=AgentCapability.IRRIGATION)
        assert score.ucb_score == float("inf")

    def test_ucb_score_with_tasks(self):
        score = AgentScore(
            agent_id="a1",
            capability=AgentCapability.IRRIGATION,
            total_tasks=10,
            q_value=0.8,
            exploration_bonus=0.1,
        )
        ucb = score.ucb_score
        expected_exploitation = 0.8
        expected_exploration = 0.1 * math.sqrt(math.log(11) / 11)
        assert abs(ucb - (expected_exploitation + expected_exploration)) < 1e-6

    def test_q_value_bounds(self):
        with pytest.raises(Exception):
            AgentScore(agent_id="a1", capability=AgentCapability.IRRIGATION, q_value=1.5)
        with pytest.raises(Exception):
            AgentScore(agent_id="a1", capability=AgentCapability.IRRIGATION, q_value=-0.1)


class TestAgentState:
    def test_defaults(self):
        state = AgentState(agent_id="a1")
        assert state.is_available is True
        assert state.current_task_id is None
        assert state.load == 0.0
        assert state.error_count == 0

    def test_load_bounds(self):
        state = AgentState(agent_id="a1", load=0.5)
        assert state.load == 0.5

        with pytest.raises(Exception):
            AgentState(agent_id="a1", load=1.5)


# ─────────────────────────────────────────────────────────────────────────────
# Task Model Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestTask:
    def test_defaults(self):
        task = Task(
            description="Analyze wheat field",
            description_ar="تحليل حقل القمح",
        )
        assert task.task_id  # auto-generated UUID
        assert task.description == "Analyze wheat field"
        assert task.description_ar == "تحليل حقل القمح"
        assert task.required_capabilities == []
        # use_enum_values=True: stored as string
        assert task.priority == "medium"
        assert task.context == {}
        assert task.tenant_id == "sahool"
        assert task.field_id is None
        assert task.timeout_seconds == 300

    def test_unique_task_ids(self):
        task1 = Task(description="T1", description_ar="م1")
        task2 = Task(description="T2", description_ar="م2")
        assert task1.task_id != task2.task_id


class TestTaskResult:
    def test_creation(self):
        result = TaskResult(
            task_id="t1",
            agent_id="a1",
            status=TaskStatus.COMPLETED,
            success=True,
            result={"answer": "irrigate now"},
            execution_time_ms=150.0,
            confidence=0.95,
        )
        assert result.task_id == "t1"
        assert result.agent_id == "a1"
        assert result.success is True
        assert result.result == {"answer": "irrigate now"}
        assert result.error is None
        assert result.execution_time_ms == 150.0
        assert result.confidence == 0.95

    def test_failed_result(self):
        result = TaskResult(
            task_id="t1",
            agent_id="a1",
            status=TaskStatus.FAILED,
            success=False,
            error="Timeout",
            error_ar="انتهت المهلة",
        )
        assert result.success is False
        assert result.error == "Timeout"
        assert result.error_ar == "انتهت المهلة"


# ─────────────────────────────────────────────────────────────────────────────
# Swarm Model Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestSwarmConfig:
    def test_defaults(self):
        config = SwarmConfig(name="Test Swarm", name_ar="سرب اختبار")
        assert config.swarm_id  # auto-generated
        assert config.name == "Test Swarm"
        assert config.name_ar == "سرب اختبار"
        # use_enum_values
        assert config.topology == "star"
        assert config.min_agents == 1
        assert config.max_agents == 10
        assert config.consensus_type == "majority_voting"
        assert config.consensus_threshold == 0.5
        assert config.timeout_seconds == 60
        assert config.enable_load_balancing is True
        assert config.retry_failed_tasks is True
        assert config.max_retries == 3

    def test_min_agents_constraint(self):
        with pytest.raises(Exception):
            SwarmConfig(name="S", name_ar="س", min_agents=0)


class TestSwarmState:
    def test_defaults(self):
        state = SwarmState(swarm_id="sw1")
        assert state.active_agents == []
        assert state.pending_tasks == 0
        assert state.completed_tasks == 0
        assert state.failed_tasks == 0
        assert state.is_coordinating is False
        assert state.current_task_id is None


class TestSwarmResult:
    def test_creation(self):
        result = SwarmResult(
            swarm_id="sw1",
            task_id="t1",
            success=True,
            consensus_reached=True,
            consensus_confidence=0.9,
            agents_participated=3,
            summary="All agents agree",
            summary_ar="جميع الوكلاء متفقون",
        )
        assert result.success is True
        assert result.consensus_reached is True
        assert result.consensus_confidence == 0.9
        assert result.agents_participated == 3
        assert result.summary == "All agents agree"


# ─────────────────────────────────────────────────────────────────────────────
# Consensus Model Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestVote:
    def test_creation(self):
        vote = Vote(
            agent_id="a1",
            value="approve",
            confidence=0.85,
            weight=1.5,
            reasoning="Good data",
            reasoning_ar="بيانات جيدة",
        )
        assert vote.agent_id == "a1"
        assert vote.value == "approve"
        assert vote.confidence == 0.85
        assert vote.weight == 1.5
        assert vote.reasoning == "Good data"

    def test_defaults(self):
        vote = Vote(agent_id="a1", value="yes")
        assert vote.confidence == 1.0
        assert vote.weight == 1.0
        assert vote.reasoning is None


class TestConsensusResult:
    def test_creation(self):
        result = ConsensusResult(
            consensus_type=ConsensusType.MAJORITY_VOTING,
            reached=True,
            decision="irrigate",
            total_votes=5,
            agreement_ratio=0.8,
            confidence=0.9,
        )
        assert result.consensus_id  # auto-generated
        assert result.reached is True
        assert result.decision == "irrigate"
        assert result.total_votes == 5
        assert result.agreement_ratio == 0.8
        assert result.dissenting_agents == []

    def test_defaults(self):
        result = ConsensusResult(
            consensus_type=ConsensusType.RAFT,
            reached=False,
        )
        assert result.decision is None
        assert result.total_votes == 0
        assert result.rounds == 1
        assert result.duration_ms == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Memory Model Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestMemoryEntry:
    def test_creation(self):
        entry = MemoryEntry(
            namespace=MemoryNamespace.KNOWLEDGE,
            key="wheat_irrigation",
            value={"schedule": "every 10 days"},
        )
        assert entry.entry_id  # auto-generated
        assert entry.key == "wheat_irrigation"
        assert entry.value == {"schedule": "every 10 days"}
        assert entry.metadata == {}
        assert entry.embedding is None
        assert entry.access_count == 0
        assert entry.tenant_id == "sahool"
        assert entry.expires_at is None

    def test_is_expired_no_expiry(self):
        entry = MemoryEntry(
            namespace=MemoryNamespace.TASKS,
            key="k",
            value="v",
        )
        assert entry.is_expired is False

    def test_is_expired_future(self):
        entry = MemoryEntry(
            namespace=MemoryNamespace.TASKS,
            key="k",
            value="v",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        assert entry.is_expired is False

    def test_is_expired_past(self):
        entry = MemoryEntry(
            namespace=MemoryNamespace.TASKS,
            key="k",
            value="v",
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        assert entry.is_expired is True


class TestPatternMatch:
    def test_creation(self):
        entry = MemoryEntry(
            namespace=MemoryNamespace.PATTERNS,
            key="drought",
            value="pattern data",
        )
        match = PatternMatch(entry=entry, similarity=0.92, match_type="semantic")
        assert match.similarity == 0.92
        assert match.match_type == "semantic"
        assert match.entry.key == "drought"

    def test_similarity_bounds(self):
        entry = MemoryEntry(
            namespace=MemoryNamespace.PATTERNS,
            key="k",
            value="v",
        )
        with pytest.raises(Exception):
            PatternMatch(entry=entry, similarity=1.5)


class TestMemoryStats:
    def test_defaults(self):
        stats = MemoryStats()
        assert stats.total_entries == 0
        assert stats.by_namespace == {}
        assert stats.cache_hits == 0
        assert stats.cache_misses == 0
        assert stats.avg_access_time_ms == 0.0
        assert stats.memory_usage_bytes == 0
        assert stats.last_cleanup is None


# ─────────────────────────────────────────────────────────────────────────────
# Routing Model Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestRoutingDecision:
    def test_creation(self):
        decision = RoutingDecision(
            task_id="t1",
            selected_agent_id="a1",
            candidate_scores={"a1": 0.9, "a2": 0.7},
            selection_method="q_learning",
        )
        assert decision.decision_id  # auto-generated
        assert decision.task_id == "t1"
        assert decision.selected_agent_id == "a1"
        assert decision.candidate_scores == {"a1": 0.9, "a2": 0.7}
        assert decision.exploration_used is False
        assert decision.reasoning is None


class TestRouterStats:
    def test_defaults(self):
        stats = RouterStats()
        assert stats.total_routing_decisions == 0
        assert stats.exploration_count == 0
        assert stats.exploitation_count == 0
        assert stats.avg_routing_time_ms == 0.0
        assert stats.successful_routings == 0
        assert stats.failed_routings == 0
        assert stats.agents_registered == 0
        assert stats.by_capability == {}
