"""
Council Manager for Multi-Agent System
مدير المجلس لنظام الوكلاء المتعددين

Manages agent councils for collaborative decision-making and consensus building.
يدير مجالس الوكلاء لاتخاذ القرارات التعاونية وبناء الإجماع.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import structlog
from datetime import datetime

from .consensus_engine import ConsensusEngine, ConsensusStrategy

logger = structlog.get_logger()


class CouncilType(Enum):
    """
    Types of agent councils
    أنواع مجالس الوكلاء
    """
    DIAGNOSIS_COUNCIL = "diagnosis_council"  # Disease/pest diagnosis | تشخيص الأمراض والآفات
    TREATMENT_COUNCIL = "treatment_council"  # Treatment planning | تخطيط العلاج
    RESOURCE_COUNCIL = "resource_council"  # Water/fertilizer optimization | تحسين المياه والأسمدة
    EMERGENCY_COUNCIL = "emergency_council"  # Crisis response | الاستجابة للأزمات
    SUSTAINABILITY_COUNCIL = "sustainability_council"  # Ecological decisions | القرارات البيئية
    HARVEST_COUNCIL = "harvest_council"  # Harvest timing and strategy | توقيت واستراتيجية الحصاد
    PLANNING_COUNCIL = "planning_council"  # Season and crop planning | تخطيط الموسم والمحاصيل


@dataclass
class AgentOpinion:
    """
    Opinion from a single agent
    رأي من وكيل واحد
    """
    agent_id: str
    agent_type: str
    recommendation: str
    confidence: float  # 0-1 scale | مقياس 0-1
    evidence: List[str] = field(default_factory=list)
    dissenting_points: List[str] = field(default_factory=list)
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate opinion data | التحقق من صحة بيانات الرأي"""
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        if not self.agent_id:
            raise ValueError("Agent ID is required")
        if not self.recommendation:
            raise ValueError("Recommendation is required")


@dataclass
class Conflict:
    """
    Represents a conflict between agent opinions
    يمثل تعارضاً بين آراء الوكلاء
    """
    conflicting_agents: List[str]
    conflict_type: str  # "recommendation", "evidence", "interpretation"
    description: str
    severity: float  # 0-1, how severe is the conflict | مدى خطورة التعارض
    resolution_suggestion: str = ""


@dataclass
class CouncilDecision:
    """
    Final decision from a council of agents
    القرار النهائي من مجلس الوكلاء
    """
    decision: str
    confidence: float  # 0-1 scale | مقياس 0-1
    consensus_level: float  # 0-1, how much agents agree | مدى اتفاق الوكلاء
    participating_agents: List[str]
    supporting_opinions: List[AgentOpinion]
    dissenting_opinions: List[AgentOpinion]
    resolution_notes: str = ""
    conflicts: List[Conflict] = field(default_factory=list)
    council_type: Optional[CouncilType] = None
    consensus_strategy: Optional[ConsensusStrategy] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the council decision
        الحصول على ملخص لقرار المجلس
        """
        return {
            "decision": self.decision,
            "confidence": round(self.confidence, 2),
            "consensus_level": round(self.consensus_level, 2),
            "total_agents": len(self.participating_agents),
            "supporting_agents": len(self.supporting_opinions),
            "dissenting_agents": len(self.dissenting_opinions),
            "conflicts_count": len(self.conflicts),
            "council_type": self.council_type.value if self.council_type else None,
            "timestamp": self.timestamp.isoformat()
        }


class CouncilManager:
    """
    Manages agent councils for collaborative decision-making
    يدير مجالس الوكلاء لاتخاذ القرارات التعاونية

    Coordinates multiple agents to reach consensus on complex decisions,
    handles conflicts, and builds comprehensive recommendations.

    ينسق بين وكلاء متعددين للوصول إلى إجماع بشأن القرارات المعقدة،
    ويعالج التعارضات، ويبني توصيات شاملة.
    """

    def __init__(self, consensus_engine: Optional[ConsensusEngine] = None):
        """
        Initialize Council Manager
        تهيئة مدير المجلس

        Args:
            consensus_engine: Engine for consensus building | محرك بناء الإجماع
        """
        self.consensus_engine = consensus_engine or ConsensusEngine()
        self.council_history: List[CouncilDecision] = []

        logger.info("council_manager_initialized")

    async def convene_council(
        self,
        council_type: CouncilType,
        query: str,
        agents: List[Any],
        context: Optional[Dict[str, Any]] = None,
        consensus_strategy: ConsensusStrategy = ConsensusStrategy.WEIGHTED_CONFIDENCE,
        min_confidence: float = 0.6,
    ) -> CouncilDecision:
        """
        Convene a council of agents to make a decision
        عقد مجلس من الوكلاء لاتخاذ قرار

        Args:
            council_type: Type of council to convene | نوع المجلس المراد عقده
            query: Question or issue to address | السؤال أو المسألة المراد معالجتها
            agents: List of agents to participate | قائمة الوكلاء للمشاركة
            context: Additional context | سياق إضافي
            consensus_strategy: Strategy for building consensus | استراتيجية بناء الإجماع
            min_confidence: Minimum confidence threshold | الحد الأدنى لعتبة الثقة

        Returns:
            CouncilDecision: Final decision | القرار النهائي
        """
        logger.info(
            "council_convened",
            council_type=council_type.value,
            num_agents=len(agents),
            strategy=consensus_strategy.value
        )

        try:
            # Step 1: Collect opinions from all agents
            # الخطوة 1: جمع الآراء من جميع الوكلاء
            opinions = await self.collect_opinions(agents, query, context)

            if not opinions:
                logger.warning("no_opinions_collected", council_type=council_type.value)
                return self._create_empty_decision(council_type, "No opinions collected")

            # Step 2: Build consensus from opinions
            # الخطوة 2: بناء الإجماع من الآراء
            decision = await self.build_consensus(
                opinions,
                consensus_strategy=consensus_strategy,
                council_type=council_type
            )

            # Step 3: If consensus is low or confidence is low, try to resolve conflicts
            # الخطوة 3: إذا كان الإجماع منخفضاً أو الثقة منخفضة، حاول حل التعارضات
            if decision.consensus_level < 0.7 or decision.confidence < min_confidence:
                logger.info(
                    "consensus_low_attempting_resolution",
                    consensus_level=decision.consensus_level,
                    confidence=decision.confidence
                )
                decision = await self.resolve_conflicts(opinions, decision)

            # Step 4: Store in history
            # الخطوة 4: التخزين في السجل
            self.council_history.append(decision)

            logger.info(
                "council_decision_reached",
                decision_summary=decision.get_summary()
            )

            return decision

        except Exception as e:
            logger.error(
                "council_failed",
                council_type=council_type.value,
                error=str(e),
                exc_info=True
            )
            raise

    async def collect_opinions(
        self,
        agents: List[Any],
        query: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[AgentOpinion]:
        """
        Collect opinions from all participating agents
        جمع الآراء من جميع الوكلاء المشاركين

        Args:
            agents: List of agents | قائمة الوكلاء
            query: Question to ask | السؤال المراد طرحه
            context: Additional context | سياق إضافي

        Returns:
            List of agent opinions | قائمة آراء الوكلاء
        """
        opinions = []

        for agent in agents:
            try:
                # Get agent's response | الحصول على استجابة الوكيل
                response = await agent.think(query, context=context, use_rag=True)

                # Parse response into opinion structure
                # تحليل الاستجابة إلى هيكل الرأي
                opinion = self._parse_agent_response(agent, response)
                opinions.append(opinion)

                logger.debug(
                    "opinion_collected",
                    agent_id=agent.name,
                    confidence=opinion.confidence
                )

            except Exception as e:
                logger.error(
                    "opinion_collection_failed",
                    agent_id=getattr(agent, 'name', 'unknown'),
                    error=str(e)
                )
                # Continue with other agents even if one fails
                # استمر مع الوكلاء الآخرين حتى لو فشل أحدهم
                continue

        logger.info("opinions_collected", total=len(opinions))
        return opinions

    async def build_consensus(
        self,
        opinions: List[AgentOpinion],
        consensus_strategy: ConsensusStrategy = ConsensusStrategy.WEIGHTED_CONFIDENCE,
        council_type: Optional[CouncilType] = None,
    ) -> CouncilDecision:
        """
        Build consensus from agent opinions
        بناء الإجماع من آراء الوكلاء

        Args:
            opinions: List of agent opinions | قائمة آراء الوكلاء
            consensus_strategy: Strategy to use | الاستراتيجية المراد استخدامها
            council_type: Type of council | نوع المجلس

        Returns:
            CouncilDecision: Consensus decision | قرار الإجماع
        """
        if not opinions:
            return self._create_empty_decision(council_type, "No opinions to process")

        # Use consensus engine to determine the decision
        # استخدام محرك الإجماع لتحديد القرار
        consensus_result = self.consensus_engine.apply_strategy(
            opinions,
            strategy=consensus_strategy
        )

        # Calculate consensus level
        # حساب مستوى الإجماع
        consensus_level = self._calculate_consensus_level(opinions)

        # Separate supporting and dissenting opinions
        # فصل الآراء المؤيدة والمعارضة
        supporting, dissenting = self._categorize_opinions(
            opinions,
            consensus_result['decision']
        )

        # Identify conflicts
        # تحديد التعارضات
        conflicts = self._identify_conflicts(opinions)

        decision = CouncilDecision(
            decision=consensus_result['decision'],
            confidence=consensus_result['confidence'],
            consensus_level=consensus_level,
            participating_agents=[op.agent_id for op in opinions],
            supporting_opinions=supporting,
            dissenting_opinions=dissenting,
            resolution_notes=consensus_result.get('notes', ''),
            conflicts=conflicts,
            council_type=council_type,
            consensus_strategy=consensus_strategy,
            metadata={
                'total_opinions': len(opinions),
                'strategy_details': consensus_result.get('details', {})
            }
        )

        return decision

    async def resolve_conflicts(
        self,
        opinions: List[AgentOpinion],
        initial_decision: Optional[CouncilDecision] = None,
    ) -> CouncilDecision:
        """
        Attempt to resolve conflicts between agent opinions
        محاولة حل التعارضات بين آراء الوكلاء

        Args:
            opinions: List of agent opinions | قائمة آراء الوكلاء
            initial_decision: Initial decision before resolution | القرار الأولي قبل الحل

        Returns:
            CouncilDecision: Resolved decision | القرار المحلول
        """
        logger.info("attempting_conflict_resolution", num_opinions=len(opinions))

        # If we have an initial decision, use it as starting point
        # إذا كان لدينا قرار أولي، استخدمه كنقطة بداية
        decision = initial_decision or await self.build_consensus(opinions)

        conflicts = self._identify_conflicts(opinions)

        if not conflicts:
            logger.info("no_conflicts_found")
            return decision

        # Analyze conflicts and create resolution notes
        # تحليل التعارضات وإنشاء ملاحظات الحل
        resolution_notes = []

        for conflict in conflicts:
            if conflict.severity >= 0.7:  # High severity conflict | تعارض شديد
                resolution_notes.append(
                    f"High-severity conflict detected between {', '.join(conflict.conflicting_agents)}: "
                    f"{conflict.description}. {conflict.resolution_suggestion}"
                )
            else:
                resolution_notes.append(
                    f"Minor conflict: {conflict.description}"
                )

        # Try alternative consensus strategy if original failed
        # جرب استراتيجية إجماع بديلة إذا فشلت الأصلية
        if decision.consensus_level < 0.5:
            logger.info("trying_alternative_consensus_strategy")
            alternative_result = self.consensus_engine.apply_strategy(
                opinions,
                strategy=ConsensusStrategy.EXPERTISE_WEIGHTED
            )

            decision.decision = alternative_result['decision']
            decision.confidence = alternative_result['confidence']
            decision.consensus_level = self._calculate_consensus_level(opinions)

        decision.conflicts = conflicts
        decision.resolution_notes = "\n".join(resolution_notes)

        logger.info(
            "conflict_resolution_completed",
            conflicts_count=len(conflicts),
            new_consensus_level=decision.consensus_level
        )

        return decision

    def _calculate_consensus_level(self, opinions: List[AgentOpinion]) -> float:
        """
        Calculate consensus level among opinions
        حساب مستوى الإجماع بين الآراء

        Args:
            opinions: List of agent opinions | قائمة آراء الوكلاء

        Returns:
            Consensus level (0-1) | مستوى الإجماع (0-1)
        """
        if not opinions or len(opinions) < 2:
            return 1.0

        # Group similar recommendations
        # تجميع التوصيات المتشابهة
        recommendations = {}
        total_confidence = 0

        for opinion in opinions:
            rec_key = opinion.recommendation.lower().strip()
            if rec_key not in recommendations:
                recommendations[rec_key] = []
            recommendations[rec_key].append(opinion)
            total_confidence += opinion.confidence

        # Find the largest group
        # إيجاد أكبر مجموعة
        if not recommendations:
            return 0.0

        max_group_size = max(len(group) for group in recommendations.values())
        max_group = [group for group in recommendations.values() if len(group) == max_group_size][0]

        # Calculate weighted consensus
        # حساب الإجماع الموزون
        max_group_confidence = sum(op.confidence for op in max_group)

        # Consensus is ratio of largest group's weighted confidence to total
        # الإجماع هو نسبة الثقة الموزونة لأكبر مجموعة إلى الإجمالي
        if total_confidence > 0:
            consensus = max_group_confidence / total_confidence
        else:
            consensus = max_group_size / len(opinions)

        return min(1.0, consensus)

    def _identify_conflicts(self, opinions: List[AgentOpinion]) -> List[Conflict]:
        """
        Identify conflicts between agent opinions
        تحديد التعارضات بين آراء الوكلاء

        Args:
            opinions: List of agent opinions | قائمة آراء الوكلاء

        Returns:
            List of conflicts | قائمة التعارضات
        """
        conflicts = []

        # Group opinions by recommendation
        # تجميع الآراء حسب التوصية
        recommendation_groups = {}
        for opinion in opinions:
            rec_key = opinion.recommendation.lower().strip()
            if rec_key not in recommendation_groups:
                recommendation_groups[rec_key] = []
            recommendation_groups[rec_key].append(opinion)

        # If we have multiple distinct recommendations, there's a conflict
        # إذا كان لدينا توصيات متعددة متميزة، فهناك تعارض
        if len(recommendation_groups) > 1:
            groups = list(recommendation_groups.values())

            # Compare largest groups
            # مقارنة أكبر المجموعات
            for i in range(len(groups)):
                for j in range(i + 1, len(groups)):
                    group1 = groups[i]
                    group2 = groups[j]

                    # Calculate conflict severity based on confidence and group size
                    # حساب شدة التعارض بناءً على الثقة وحجم المجموعة
                    avg_conf1 = sum(op.confidence for op in group1) / len(group1)
                    avg_conf2 = sum(op.confidence for op in group2) / len(group2)

                    severity = min(avg_conf1, avg_conf2)  # Higher confidence = more severe conflict

                    conflict = Conflict(
                        conflicting_agents=[op.agent_id for op in group1 + group2],
                        conflict_type="recommendation",
                        description=f"Disagreement between recommendations: '{group1[0].recommendation}' vs '{group2[0].recommendation}'",
                        severity=severity,
                        resolution_suggestion=f"Consider evidence from both sides. Group 1 confidence: {avg_conf1:.2f}, Group 2 confidence: {avg_conf2:.2f}"
                    )
                    conflicts.append(conflict)

        # Check for evidence conflicts (dissenting points)
        # التحقق من تعارضات الأدلة (نقاط المعارضة)
        for opinion in opinions:
            if opinion.dissenting_points:
                conflict = Conflict(
                    conflicting_agents=[opinion.agent_id],
                    conflict_type="evidence",
                    description=f"Agent {opinion.agent_id} has dissenting points: {'; '.join(opinion.dissenting_points[:2])}",
                    severity=0.3 + (0.4 * (1 - opinion.confidence)),
                    resolution_suggestion="Review dissenting evidence and validate assumptions"
                )
                conflicts.append(conflict)

        return conflicts

    def _parse_agent_response(self, agent: Any, response: Dict[str, Any]) -> AgentOpinion:
        """
        Parse agent response into AgentOpinion structure
        تحليل استجابة الوكيل إلى هيكل AgentOpinion

        Args:
            agent: The agent | الوكيل
            response: Agent's response | استجابة الوكيل

        Returns:
            AgentOpinion: Structured opinion | الرأي المهيكل
        """
        # Extract evidence and dissenting points from response
        # استخراج الأدلة ونقاط المعارضة من الاستجابة
        evidence = []
        dissenting_points = []

        response_text = response.get('response', '')

        # Simple parsing - look for evidence markers
        # تحليل بسيط - البحث عن علامات الأدلة
        if 'evidence:' in response_text.lower():
            # Extract evidence section
            # استخراج قسم الأدلة
            evidence = [line.strip('- ').strip() for line in response_text.split('evidence:')[1].split('\n')[:3] if line.strip()]

        if 'however' in response_text.lower() or 'but' in response_text.lower():
            # Extract potential dissenting points
            # استخراج نقاط المعارضة المحتملة
            dissenting_points = [line.strip() for line in response_text.split('\n') if 'however' in line.lower() or 'but' in line.lower()][:2]

        return AgentOpinion(
            agent_id=agent.name,
            agent_type=agent.role,
            recommendation=response.get('response', ''),
            confidence=response.get('confidence', 0.7),
            evidence=evidence,
            dissenting_points=dissenting_points,
            reasoning=response_text,
            metadata={
                'agent_info': agent.get_info() if hasattr(agent, 'get_info') else {}
            }
        )

    def _categorize_opinions(
        self,
        opinions: List[AgentOpinion],
        final_decision: str
    ) -> tuple[List[AgentOpinion], List[AgentOpinion]]:
        """
        Categorize opinions as supporting or dissenting
        تصنيف الآراء كمؤيدة أو معارضة

        Args:
            opinions: All opinions | جميع الآراء
            final_decision: Final decision text | نص القرار النهائي

        Returns:
            Tuple of (supporting, dissenting) opinions | مجموعة من الآراء (المؤيدة، المعارضة)
        """
        supporting = []
        dissenting = []

        decision_key = final_decision.lower().strip()

        for opinion in opinions:
            opinion_key = opinion.recommendation.lower().strip()

            # Simple similarity check - if main keywords match
            # فحص التشابه البسيط - إذا تطابقت الكلمات الرئيسية
            if self._are_similar(opinion_key, decision_key):
                supporting.append(opinion)
            else:
                dissenting.append(opinion)

        return supporting, dissenting

    def _are_similar(self, text1: str, text2: str, threshold: float = 0.5) -> bool:
        """
        Check if two texts are similar
        التحقق مما إذا كان نصان متشابهان

        Args:
            text1: First text | النص الأول
            text2: Second text | النص الثاني
            threshold: Similarity threshold | عتبة التشابه

        Returns:
            True if similar | صحيح إذا كانت متشابهة
        """
        # Simple word overlap similarity
        # تشابه تداخل الكلمات البسيط
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return False

        overlap = len(words1 & words2)
        total = len(words1 | words2)

        similarity = overlap / total if total > 0 else 0

        return similarity >= threshold

    def _create_empty_decision(
        self,
        council_type: Optional[CouncilType],
        reason: str
    ) -> CouncilDecision:
        """
        Create an empty decision when no consensus can be reached
        إنشاء قرار فارغ عندما لا يمكن الوصول إلى إجماع

        Args:
            council_type: Type of council | نوع المجلس
            reason: Reason for empty decision | سبب القرار الفارغ

        Returns:
            CouncilDecision: Empty decision | قرار فارغ
        """
        return CouncilDecision(
            decision=f"Unable to reach consensus: {reason}",
            confidence=0.0,
            consensus_level=0.0,
            participating_agents=[],
            supporting_opinions=[],
            dissenting_opinions=[],
            resolution_notes=reason,
            council_type=council_type
        )

    def get_council_history(
        self,
        council_type: Optional[CouncilType] = None,
        limit: int = 10
    ) -> List[CouncilDecision]:
        """
        Get history of council decisions
        الحصول على سجل قرارات المجلس

        Args:
            council_type: Filter by council type | التصفية حسب نوع المجلس
            limit: Maximum number of decisions to return | الحد الأقصى لعدد القرارات

        Returns:
            List of council decisions | قائمة قرارات المجلس
        """
        history = self.council_history

        if council_type:
            history = [d for d in history if d.council_type == council_type]

        # Return most recent first
        # إرجاع الأحدث أولاً
        return sorted(history, key=lambda d: d.timestamp, reverse=True)[:limit]

    def clear_history(self):
        """
        Clear council decision history
        مسح سجل قرارات المجلس
        """
        self.council_history = []
        logger.info("council_history_cleared")
