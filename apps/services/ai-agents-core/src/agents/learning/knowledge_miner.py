"""
SAHOOL Knowledge Miner Agent
وكيل التنقيب عن المعرفة

Extracts and organizes knowledge:
- Pattern discovery
- Rule extraction
- Knowledge graph building
- Best practices identification
"""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any

from ..base_agent import AgentAction, AgentLayer, AgentPercept, AgentType, BaseAgent

logger = logging.getLogger(__name__)


class KnowledgeMinerAgent(BaseAgent):
    """وكيل التنقيب عن المعرفة"""

    def __init__(self, agent_id: str = "knowledge_miner_001"):
        super().__init__(
            agent_id=agent_id,
            name="Knowledge Miner Agent",
            name_ar="وكيل التنقيب عن المعرفة",
            agent_type=AgentType.LEARNING,
            layer=AgentLayer.LEARNING,
            description="Discovers patterns and extracts knowledge",
            description_ar="يكتشف الأنماط ويستخرج المعرفة",
        )

        # Discovered patterns
        self.patterns: dict[str, dict[str, Any]] = {}

        # Extracted rules
        self.rules: list[dict[str, Any]] = []

        # Knowledge graph (simplified)
        self.knowledge_graph: dict[str, set[str]] = defaultdict(set)

        # Data buffer for mining
        self.data_buffer: list[dict[str, Any]] = []

    async def perceive(self, percept: AgentPercept) -> None:
        """استقبال البيانات للتنقيب"""
        if percept.percept_type == "transaction_data":
            self.data_buffer.append(percept.data)

            # Mine when buffer is full
            if len(self.data_buffer) >= 100:
                await self._mine_patterns()

        elif percept.percept_type == "knowledge_update":
            # Update knowledge graph
            entity1 = percept.data.get("entity1")
            entity2 = percept.data.get("entity2")
            relation = percept.data.get("relation")

            if entity1 and entity2:
                self.knowledge_graph[entity1].add(f"{relation}:{entity2}")

    async def _mine_patterns(self) -> None:
        """التنقيب عن الأنماط"""
        if not self.data_buffer:
            return

        # Find frequent action sequences
        action_sequences = defaultdict(int)
        for data in self.data_buffer:
            action = data.get("action_type", "")
            context = data.get("context", {})
            key = f"{context.get('crop_type', 'any')}_{action}"
            action_sequences[key] += 1

        # Extract patterns with high frequency
        for pattern, count in action_sequences.items():
            if count >= 5:  # Minimum support
                self.patterns[pattern] = {
                    "frequency": count,
                    "confidence": count / len(self.data_buffer),
                    "discovered_at": datetime.now().isoformat(),
                }

        # Clear buffer
        self.data_buffer = []

    async def _extract_rules(self) -> None:
        """استخراج القواعد"""
        for pattern, info in self.patterns.items():
            if info["confidence"] > 0.7:
                parts = pattern.split("_")
                if len(parts) >= 2:
                    crop = parts[0]
                    action = "_".join(parts[1:])

                    rule = {
                        "if": {"crop_type": crop},
                        "then": {"recommended_action": action},
                        "confidence": info["confidence"],
                        "support": info["frequency"],
                    }
                    self.rules.append(rule)

    async def think(self) -> AgentAction | None:
        """التفكير في استخراج المعرفة"""
        # Extract rules from patterns
        await self._extract_rules()

        if self.rules:
            new_rules = [r for r in self.rules if r.get("is_new", True)]
            if new_rules:
                return AgentAction(
                    action_type="new_knowledge_discovered",
                    parameters={
                        "rules": new_rules[:5],
                        "patterns_count": len(self.patterns),
                        "graph_size": len(self.knowledge_graph),
                    },
                    confidence=0.75,
                    priority=4,
                    reasoning=f"تم اكتشاف {len(new_rules)} قاعدة جديدة",
                    source_agent=self.agent_id,
                )

        return None

    async def act(self, action: AgentAction) -> dict[str, Any]:
        """تنفيذ الإجراء"""
        return {
            "action_type": action.action_type,
            "knowledge_extracted": action.parameters,
            "success": True,
        }

    def query_knowledge(self, entity: str) -> list[str]:
        """الاستعلام عن المعرفة"""
        return list(self.knowledge_graph.get(entity, set()))

    def get_rule_for_crop(self, crop_type: str) -> list[dict[str, Any]]:
        """الحصول على القواعد للمحصول"""
        return [r for r in self.rules if r.get("if", {}).get("crop_type") == crop_type]
