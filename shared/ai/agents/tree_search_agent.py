"""
Tree-of-Thoughts Agent Pattern
==============================
نمط وكيل شجرة الأفكار

Implements Tree-of-Thoughts (ToT) for complex problem solving.
Based on "Tree of Thoughts: Deliberate Problem Solving with Large Language Models".

Features:
- Multiple solution paths exploration
- Branch evaluation and pruning
- Beam search for optimal solutions
- Backtracking on failure
- Monte Carlo Tree Search (MCTS) option
- Full decision tree export

Author: SAHOOL Platform Team
Updated: January 2026
"""

import math
import uuid
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import structlog

from ..llm_provider import LLMProviderManager
from .base import (
    AgentMode,
    AgentStep,
    BaseAutonomousAgent,
    ToolResult,
)

logger = structlog.get_logger()


# ============================================================================
# ENUMS & TYPES
# ============================================================================


class SearchStrategy(StrEnum):
    """استراتيجية البحث"""

    BFS = "bfs"  # Breadth-first search
    DFS = "dfs"  # Depth-first search
    BEAM = "beam"  # Beam search
    MCTS = "mcts"  # Monte Carlo Tree Search
    BEST_FIRST = "best_first"  # Best-first search


class NodeStatus(StrEnum):
    """حالة العقدة"""

    PENDING = "pending"  # Not yet evaluated
    EVALUATING = "evaluating"  # Currently being evaluated
    EXPANDED = "expanded"  # Children generated
    TERMINAL = "terminal"  # Leaf node (solution or dead end)
    PRUNED = "pruned"  # Pruned from search
    SELECTED = "selected"  # Selected as part of solution path


# ============================================================================
# THOUGHT TREE NODES
# ============================================================================


@dataclass
class ThoughtNode:
    """
    Node in the thought tree.
    عقدة في شجرة الأفكار

    Represents a single thought/state in the exploration.
    """

    node_id: str
    thought: str  # The thought content
    thought_ar: str  # Arabic version
    depth: int  # Depth in tree (0 = root)
    parent_id: str | None = None  # Parent node ID
    children_ids: list[str] = field(default_factory=list)
    status: NodeStatus = NodeStatus.PENDING

    # Evaluation scores
    value: float = 0.0  # Evaluated value (0-1)
    confidence: float = 0.0  # Confidence in this thought
    visits: int = 0  # Visit count (for MCTS)

    # Execution result (if terminal)
    result: Any = None
    execution_time_ms: float = 0.0

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "thought": self.thought,
            "thought_ar": self.thought_ar,
            "depth": self.depth,
            "parent_id": self.parent_id,
            "children_ids": self.children_ids,
            "status": self.status.value,
            "value": self.value,
            "confidence": self.confidence,
            "visits": self.visits,
            "result": self.result
            if isinstance(self.result, (str, int, float, bool, list, dict, type(None)))
            else str(self.result),
            "execution_time_ms": self.execution_time_ms,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }

    @property
    def ucb1_score(self) -> float:
        """Calculate UCB1 score for MCTS selection."""
        if self.visits == 0:
            return float("inf")

        parent_visits = self.metadata.get("parent_visits", 1)
        exploitation = self.value
        exploration = math.sqrt(2 * math.log(parent_visits) / self.visits)

        return exploitation + exploration


@dataclass
class ThoughtPath:
    """
    A complete path through the thought tree.
    مسار كامل عبر شجرة الأفكار
    """

    path_id: str
    nodes: list[ThoughtNode]
    total_value: float = 0.0
    average_confidence: float = 0.0
    is_complete: bool = False
    is_successful: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "path_id": self.path_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "total_value": self.total_value,
            "average_confidence": self.average_confidence,
            "is_complete": self.is_complete,
            "is_successful": self.is_successful,
            "depth": len(self.nodes),
        }


@dataclass
class ThoughtTree:
    """
    Complete thought tree for exploration.
    شجرة أفكار كاملة للاستكشاف
    """

    tree_id: str
    task: str
    task_ar: str
    root_id: str
    nodes: dict[str, ThoughtNode] = field(default_factory=dict)
    best_path: ThoughtPath | None = None
    explored_paths: list[ThoughtPath] = field(default_factory=list)
    strategy: SearchStrategy = SearchStrategy.BEAM
    max_depth: int = 5
    beam_width: int = 3
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    def add_node(self, node: ThoughtNode) -> None:
        """Add a node to the tree."""
        self.nodes[node.node_id] = node
        if node.parent_id and node.parent_id in self.nodes:
            self.nodes[node.parent_id].children_ids.append(node.node_id)

    def get_node(self, node_id: str) -> ThoughtNode | None:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_children(self, node_id: str) -> list[ThoughtNode]:
        """Get children of a node."""
        node = self.nodes.get(node_id)
        if not node:
            return []
        return [self.nodes[cid] for cid in node.children_ids if cid in self.nodes]

    def get_path_to_node(self, node_id: str) -> list[ThoughtNode]:
        """Get the path from root to a node."""
        path = []
        current_id = node_id

        while current_id:
            node = self.nodes.get(current_id)
            if not node:
                break
            path.insert(0, node)
            current_id = node.parent_id

        return path

    def get_leaf_nodes(self) -> list[ThoughtNode]:
        """Get all leaf nodes."""
        return [
            n for n in self.nodes.values() if not n.children_ids or n.status == NodeStatus.TERMINAL
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "tree_id": self.tree_id,
            "task": self.task,
            "task_ar": self.task_ar,
            "root_id": self.root_id,
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
            "best_path": self.best_path.to_dict() if self.best_path else None,
            "explored_paths_count": len(self.explored_paths),
            "strategy": self.strategy.value,
            "max_depth": self.max_depth,
            "beam_width": self.beam_width,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_nodes": len(self.nodes),
        }

    def to_mermaid(self) -> str:
        """Export tree as Mermaid diagram."""
        lines = ["graph TD"]

        for node_id, node in self.nodes.items():
            # Node label
            short_thought = node.thought[:30].replace('"', "'")
            status_icon = {
                NodeStatus.PENDING: "⏳",
                NodeStatus.EVALUATING: "🔄",
                NodeStatus.EXPANDED: "📂",
                NodeStatus.TERMINAL: "✓" if node.result else "✗",
                NodeStatus.PRUNED: "✂️",
                NodeStatus.SELECTED: "⭐",
            }.get(node.status, "")

            lines.append(f'    {node_id}["{status_icon} {short_thought}..."]')

            # Edges to children
            for child_id in node.children_ids:
                if child_id in self.nodes:
                    child = self.nodes[child_id]
                    edge_label = f"{child.value:.2f}"
                    lines.append(f"    {node_id} -->|{edge_label}| {child_id}")

        return "\n".join(lines)


# ============================================================================
# TREE SEARCH AGENT
# ============================================================================


class TreeSearchAgent(BaseAutonomousAgent):
    """
    Agent using Tree-of-Thoughts for exploration.
    وكيل يستخدم شجرة الأفكار للاستكشاف

    Features:
    - Multiple solution path exploration
    - Configurable search strategies (BFS, DFS, Beam, MCTS)
    - Branch evaluation and pruning
    - Backtracking on failure
    - Full decision tree visualization

    Usage:
        class MyTreeAgent(TreeSearchAgent):
            async def generate_thoughts(self, node, context):
                # Generate possible next thoughts
                return [ThoughtNode(...), ThoughtNode(...)]

            async def evaluate_thought(self, node, context):
                # Evaluate a single thought
                return 0.8  # Value between 0 and 1

            async def is_solution(self, node, context):
                # Check if this is a valid solution
                return True/False
    """

    # Search limits
    MAX_NODES = 100
    MAX_DEPTH = 10
    DEFAULT_BEAM_WIDTH = 3

    def __init__(
        self,
        agent_id: str,
        name: str,
        name_ar: str,
        description: str,
        description_ar: str,
        mode: AgentMode = AgentMode.HYBRID,
        tenant_id: str = "sahool",
        llm_manager: LLMProviderManager | None = None,
        enable_audit: bool = True,
        strategy: SearchStrategy = SearchStrategy.BEAM,
        beam_width: int = 3,
        max_depth: int = 5,
    ):
        """
        Initialize Tree Search agent.

        Args:
            agent_id: Unique agent identifier
            name: Agent name (English)
            name_ar: Agent name (Arabic)
            description: Agent description
            description_ar: Agent description (Arabic)
            mode: Operation mode
            tenant_id: Tenant ID for multi-tenancy
            llm_manager: LLM provider manager
            enable_audit: Enable audit logging
            strategy: Search strategy to use
            beam_width: Width for beam search
            max_depth: Maximum tree depth
        """
        super().__init__(
            agent_id=agent_id,
            name=name,
            name_ar=name_ar,
            description=description,
            description_ar=description_ar,
            mode=mode,
            tenant_id=tenant_id,
            llm_manager=llm_manager,
            enable_audit=enable_audit,
        )

        self.strategy = strategy
        self.beam_width = beam_width
        self.max_depth = max_depth

        # Current search state
        self.current_tree: ThoughtTree | None = None
        self.search_history: list[ThoughtTree] = []

        logger.info(
            "tree_search_agent_initialized",
            agent_id=self.agent_id,
            strategy=self.strategy.value,
            beam_width=self.beam_width,
            max_depth=self.max_depth,
        )

    # ========================================================================
    # ABSTRACT METHODS - Must be implemented by subclasses
    # ========================================================================

    @abstractmethod
    async def generate_thoughts(
        self,
        node: ThoughtNode,
        context: dict[str, Any],
    ) -> list[ThoughtNode]:
        """
        Generate possible next thoughts from current node.
        توليد الأفكار التالية الممكنة من العقدة الحالية

        Args:
            node: Current thought node
            context: Execution context

        Returns:
            List of possible next thoughts
        """
        pass

    @abstractmethod
    async def evaluate_thought(
        self,
        node: ThoughtNode,
        context: dict[str, Any],
    ) -> float:
        """
        Evaluate a thought node.
        تقييم عقدة فكرية

        Args:
            node: Thought to evaluate
            context: Execution context

        Returns:
            Value between 0 and 1
        """
        pass

    @abstractmethod
    async def is_solution(
        self,
        node: ThoughtNode,
        context: dict[str, Any],
    ) -> bool:
        """
        Check if a node represents a valid solution.
        التحقق مما إذا كانت العقدة تمثل حلاً صالحاً

        Args:
            node: Thought to check
            context: Execution context

        Returns:
            True if this is a solution
        """
        pass

    async def generate_initial_thought(
        self,
        task: str,
        task_ar: str,
        context: dict[str, Any],
    ) -> ThoughtNode:
        """
        Generate the initial thought (root node).
        توليد الفكرة الأولية (العقدة الجذر)

        Can be overridden for custom initialization.
        """
        return ThoughtNode(
            node_id=str(uuid.uuid4()),
            thought=f"Start: {task}",
            thought_ar=f"البداية: {task_ar}",
            depth=0,
            status=NodeStatus.EXPANDED,
            value=0.5,
            confidence=1.0,
        )

    # ========================================================================
    # TREE SEARCH EXECUTION
    # ========================================================================

    async def search(
        self,
        task: str,
        task_ar: str,
        context: dict[str, Any] | None = None,
    ) -> ThoughtTree:
        """
        Run tree search for a task.
        تشغيل البحث في الشجرة لمهمة

        Args:
            task: Task description in English
            task_ar: Task description in Arabic
            context: Additional context

        Returns:
            Complete ThoughtTree with exploration results
        """
        context = context or {}
        start_time = datetime.now(UTC)

        # Create initial tree
        root = await self.generate_initial_thought(task, task_ar, context)

        self.current_tree = ThoughtTree(
            tree_id=str(uuid.uuid4()),
            task=task,
            task_ar=task_ar,
            root_id=root.node_id,
            strategy=self.strategy,
            max_depth=self.max_depth,
            beam_width=self.beam_width,
            created_at=start_time,
        )
        self.current_tree.add_node(root)

        logger.info(
            "tree_search_started",
            agent_id=self.agent_id,
            tree_id=self.current_tree.tree_id,
            strategy=self.strategy.value,
        )

        try:
            # Run search based on strategy
            if self.strategy == SearchStrategy.BFS:
                await self._search_bfs(context)
            elif self.strategy == SearchStrategy.DFS:
                await self._search_dfs(root.node_id, context)
            elif self.strategy == SearchStrategy.BEAM:
                await self._search_beam(context)
            elif self.strategy == SearchStrategy.MCTS:
                await self._search_mcts(context)
            elif self.strategy == SearchStrategy.BEST_FIRST:
                await self._search_best_first(context)

            # Find best path
            self.current_tree.best_path = await self._find_best_path()

        except Exception as e:
            logger.error(
                "tree_search_failed",
                agent_id=self.agent_id,
                tree_id=self.current_tree.tree_id,
                error=str(e),
            )

        # Finalize
        self.current_tree.completed_at = datetime.now(UTC)
        self.search_history.append(self.current_tree)

        # Audit log
        if self.audit_logger:
            self.audit_logger.log_agent_execution(
                agent_id=self.agent_id,
                task=task[:500],
                success=self.current_tree.best_path is not None,
                execution_time_ms=(self.current_tree.completed_at - start_time).total_seconds()
                * 1000,
                steps_executed=len(self.current_tree.nodes),
            )

        logger.info(
            "tree_search_completed",
            agent_id=self.agent_id,
            tree_id=self.current_tree.tree_id,
            total_nodes=len(self.current_tree.nodes),
            has_solution=self.current_tree.best_path is not None,
        )

        return self.current_tree

    # ========================================================================
    # SEARCH STRATEGIES
    # ========================================================================

    async def _search_bfs(self, context: dict[str, Any]) -> None:
        """Breadth-first search."""
        queue = [self.current_tree.root_id]
        nodes_explored = 0

        while queue and nodes_explored < self.MAX_NODES:
            node_id = queue.pop(0)
            node = self.current_tree.get_node(node_id)

            if not node or node.depth >= self.max_depth:
                continue

            nodes_explored += 1

            # Check if solution
            if await self.is_solution(node, context):
                node.status = NodeStatus.TERMINAL
                continue

            # Generate children
            node.status = NodeStatus.EVALUATING
            children = await self.generate_thoughts(node, context)

            for child in children:
                child.parent_id = node_id
                child.depth = node.depth + 1

                # Evaluate child
                child.value = await self.evaluate_thought(child, context)
                child.status = NodeStatus.PENDING

                self.current_tree.add_node(child)
                queue.append(child.node_id)

            node.status = NodeStatus.EXPANDED

    async def _search_dfs(
        self,
        node_id: str,
        context: dict[str, Any],
        nodes_explored: int = 0,
    ) -> bool:
        """Depth-first search with backtracking."""
        if nodes_explored >= self.MAX_NODES:
            return False

        node = self.current_tree.get_node(node_id)
        if not node or node.depth >= self.max_depth:
            return False

        # Check if solution
        if await self.is_solution(node, context):
            node.status = NodeStatus.TERMINAL
            return True

        # Generate and evaluate children
        node.status = NodeStatus.EVALUATING
        children = await self.generate_thoughts(node, context)

        # Sort by estimated value
        for child in children:
            child.parent_id = node_id
            child.depth = node.depth + 1
            child.value = await self.evaluate_thought(child, context)
            self.current_tree.add_node(child)

        children.sort(key=lambda c: c.value, reverse=True)
        node.status = NodeStatus.EXPANDED

        # Recurse on children
        for child in children:
            if await self._search_dfs(child.node_id, context, nodes_explored + 1):
                return True

        return False

    async def _search_beam(self, context: dict[str, Any]) -> None:
        """Beam search - keep top-k candidates at each level."""
        current_level = [self.current_tree.root_id]
        nodes_explored = 0

        for depth in range(self.max_depth):
            if not current_level or nodes_explored >= self.MAX_NODES:
                break

            next_level: list[tuple[str, float]] = []

            for node_id in current_level:
                node = self.current_tree.get_node(node_id)
                if not node:
                    continue

                nodes_explored += 1

                # Check if solution
                if await self.is_solution(node, context):
                    node.status = NodeStatus.TERMINAL
                    continue

                # Generate children
                node.status = NodeStatus.EVALUATING
                children = await self.generate_thoughts(node, context)

                for child in children:
                    child.parent_id = node_id
                    child.depth = depth + 1
                    child.value = await self.evaluate_thought(child, context)

                    self.current_tree.add_node(child)
                    next_level.append((child.node_id, child.value))

                node.status = NodeStatus.EXPANDED

            # Keep top beam_width candidates
            next_level.sort(key=lambda x: x[1], reverse=True)
            current_level = [nid for nid, _ in next_level[: self.beam_width]]

            # Mark pruned nodes
            pruned = [nid for nid, _ in next_level[self.beam_width :]]
            for nid in pruned:
                node = self.current_tree.get_node(nid)
                if node:
                    node.status = NodeStatus.PRUNED

    async def _search_mcts(
        self,
        context: dict[str, Any],
        iterations: int = 50,
    ) -> None:
        """Monte Carlo Tree Search."""
        for _ in range(iterations):
            # Selection - select most promising node
            node_id = await self._mcts_select(self.current_tree.root_id)
            node = self.current_tree.get_node(node_id)

            if not node:
                continue

            # Expansion - generate children if not terminal
            if node.status != NodeStatus.TERMINAL and node.depth < self.max_depth:
                children = await self.generate_thoughts(node, context)

                if children:
                    for child in children:
                        child.parent_id = node_id
                        child.depth = node.depth + 1
                        self.current_tree.add_node(child)

                    node.status = NodeStatus.EXPANDED
                    node_id = children[0].node_id  # Select first child
                    node = children[0]

            # Simulation - evaluate the node
            value = await self.evaluate_thought(node, context)

            # Check if solution
            if await self.is_solution(node, context):
                node.status = NodeStatus.TERMINAL
                value = 1.0

            # Backpropagation - update values up the tree
            await self._mcts_backpropagate(node_id, value)

    async def _mcts_select(self, node_id: str) -> str:
        """Select node using UCB1."""
        node = self.current_tree.get_node(node_id)
        if not node:
            return node_id

        if not node.children_ids or node.status == NodeStatus.TERMINAL:
            return node_id

        # Select child with highest UCB1 score
        children = self.current_tree.get_children(node_id)
        if not children:
            return node_id

        # Update parent visits in metadata
        for child in children:
            child.metadata["parent_visits"] = node.visits

        best_child = max(children, key=lambda c: c.ucb1_score)
        return await self._mcts_select(best_child.node_id)

    async def _mcts_backpropagate(self, node_id: str, value: float) -> None:
        """Backpropagate value up the tree."""
        current_id = node_id

        while current_id:
            node = self.current_tree.get_node(current_id)
            if not node:
                break

            node.visits += 1
            # Running average of values
            node.value = (node.value * (node.visits - 1) + value) / node.visits

            current_id = node.parent_id

    async def _search_best_first(self, context: dict[str, Any]) -> None:
        """Best-first search using priority queue."""
        # Priority queue: (negative_value, node_id) - heapq is min-heap
        import heapq

        priority_queue: list[tuple[float, str]] = [(-0.5, self.current_tree.root_id)]
        nodes_explored = 0

        while priority_queue and nodes_explored < self.MAX_NODES:
            _, node_id = heapq.heappop(priority_queue)
            node = self.current_tree.get_node(node_id)

            if not node or node.depth >= self.max_depth:
                continue

            if node.status in [NodeStatus.EXPANDED, NodeStatus.TERMINAL]:
                continue

            nodes_explored += 1

            # Check if solution
            if await self.is_solution(node, context):
                node.status = NodeStatus.TERMINAL
                continue

            # Generate children
            node.status = NodeStatus.EVALUATING
            children = await self.generate_thoughts(node, context)

            for child in children:
                child.parent_id = node_id
                child.depth = node.depth + 1
                child.value = await self.evaluate_thought(child, context)

                self.current_tree.add_node(child)
                heapq.heappush(priority_queue, (-child.value, child.node_id))

            node.status = NodeStatus.EXPANDED

    # ========================================================================
    # PATH EXTRACTION
    # ========================================================================

    async def _find_best_path(self) -> ThoughtPath | None:
        """Find the best solution path in the tree."""
        if not self.current_tree:
            return None

        # Get all terminal (solution) nodes
        terminal_nodes = [
            n for n in self.current_tree.nodes.values() if n.status == NodeStatus.TERMINAL
        ]

        if not terminal_nodes:
            return None

        # Find path with highest total value
        best_path = None
        best_value = -float("inf")

        for terminal in terminal_nodes:
            path_nodes = self.current_tree.get_path_to_node(terminal.node_id)
            total_value = sum(n.value for n in path_nodes)
            avg_confidence = sum(n.confidence for n in path_nodes) / len(path_nodes)

            if total_value > best_value:
                best_value = total_value
                best_path = ThoughtPath(
                    path_id=str(uuid.uuid4()),
                    nodes=path_nodes,
                    total_value=total_value,
                    average_confidence=avg_confidence,
                    is_complete=True,
                    is_successful=True,
                )

                # Mark nodes as selected
                for node in path_nodes:
                    node.status = NodeStatus.SELECTED

        return best_path

    def get_solution_steps(self) -> list[dict[str, Any]]:
        """Get solution as a list of steps."""
        if not self.current_tree or not self.current_tree.best_path:
            return []

        return [
            {
                "step": i + 1,
                "thought": node.thought,
                "thought_ar": node.thought_ar,
                "value": node.value,
                "confidence": node.confidence,
            }
            for i, node in enumerate(self.current_tree.best_path.nodes)
        ]

    # ========================================================================
    # VISUALIZATION & EXPORT
    # ========================================================================

    def export_tree(self, tree_id: str | None = None) -> dict[str, Any]:
        """Export tree for debugging or learning."""
        if tree_id:
            tree = next((t for t in self.search_history if t.tree_id == tree_id), None)
        else:
            tree = self.current_tree

        if not tree:
            return {"error": "Tree not found"}

        return {
            "tree": tree.to_dict(),
            "mermaid_diagram": tree.to_mermaid(),
            "solution_steps": self.get_solution_steps(),
            "summary": {
                "total_nodes": len(tree.nodes),
                "max_depth_reached": max(n.depth for n in tree.nodes.values()),
                "terminal_nodes": sum(
                    1 for n in tree.nodes.values() if n.status == NodeStatus.TERMINAL
                ),
                "pruned_nodes": sum(
                    1 for n in tree.nodes.values() if n.status == NodeStatus.PRUNED
                ),
                "has_solution": tree.best_path is not None,
            },
        }

    # ========================================================================
    # BASE CLASS IMPLEMENTATION
    # ========================================================================

    def _register_default_tools(self) -> None:
        """Register default tools - override in subclass."""
        pass

    async def decompose_task(
        self,
        task: str,
        context: dict[str, Any],
    ) -> list[AgentStep]:
        """
        Decompose task using tree search.

        Runs tree search and converts best path to AgentSteps.
        """
        # Run tree search
        tree = await self.search(
            task=task,
            task_ar=context.get("task_ar", task),
            context=context,
        )

        # Convert solution path to AgentSteps
        if not tree.best_path:
            return []

        agent_steps = []
        for i, node in enumerate(tree.best_path.nodes):
            agent_step = AgentStep(
                step_id=node.node_id,
                step_number=i + 1,
                description=node.thought,
                description_ar=node.thought_ar,
                reasoning=f"Value: {node.value:.2f}, Confidence: {node.confidence:.2f}",
                status="completed" if node.status == NodeStatus.SELECTED else "pending",
            )
            agent_steps.append(agent_step)

        return agent_steps

    async def validate_step_result(
        self,
        step: AgentStep,
        result: ToolResult,
        context: dict[str, Any],
    ) -> tuple[bool, str | None]:
        """Validate step result."""
        return result.success, None if result.success else result.error


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def create_thought_node(
    thought: str,
    thought_ar: str,
    depth: int = 0,
    parent_id: str | None = None,
    value: float = 0.5,
    confidence: float = 0.8,
) -> ThoughtNode:
    """Helper to create a ThoughtNode."""
    return ThoughtNode(
        node_id=str(uuid.uuid4()),
        thought=thought,
        thought_ar=thought_ar,
        depth=depth,
        parent_id=parent_id,
        value=value,
        confidence=confidence,
    )
