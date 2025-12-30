"""
Council Manager Usage Example
مثال على استخدام مدير المجلس

Demonstrates how to use the Council and Consensus system for multi-agent decision-making.
يوضح كيفية استخدام نظام المجلس والإجماع لاتخاذ قرارات الوكلاء المتعددين.
"""

import asyncio
from typing import List
from datetime import datetime

from .council_manager import (
    CouncilManager,
    CouncilType,
    AgentOpinion,
)

from .consensus_engine import (
    ConsensusEngine,
    ConsensusStrategy,
)


class MockAgent:
    """
    Mock agent for demonstration purposes
    وكيل وهمي لأغراض التوضيح
    """

    def __init__(self, name: str, role: str, expertise_level: float = 0.8):
        self.name = name
        self.role = role
        self.expertise_level = expertise_level

    async def think(self, query: str, context=None, use_rag=True):
        """Simulate agent thinking"""
        # In real implementation, this would call Claude or another LLM
        # في التنفيذ الحقيقي، سيستدعي هذا Claude أو نموذج لغة آخر
        return {
            'agent': self.name,
            'role': self.role,
            'response': f"Mock response from {self.name} for: {query}",
            'confidence': self.expertise_level,
        }

    def get_info(self):
        """Get agent information"""
        return {
            'name': self.name,
            'role': self.role,
            'expertise': self.expertise_level
        }


async def example_diagnosis_council():
    """
    Example: Disease Diagnosis Council
    مثال: مجلس تشخيص الأمراض

    Multiple expert agents collaborate to diagnose a crop disease.
    يتعاون وكلاء خبراء متعددون لتشخيص مرض المحصول.
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Disease Diagnosis Council")
    print("مثال 1: مجلس تشخيص الأمراض")
    print("="*80 + "\n")

    # Create mock agents
    # إنشاء وكلاء وهميين
    agents = [
        MockAgent("disease_expert", "Plant Pathologist", 0.9),
        MockAgent("pest_control_expert", "Entomologist", 0.85),
        MockAgent("ecological_expert", "Agro-Ecologist", 0.8),
    ]

    # Initialize council manager
    # تهيئة مدير المجلس
    council_manager = CouncilManager()

    # Query for diagnosis
    # استعلام للتشخيص
    query = "What disease is affecting my tomato plants? Leaves show yellow spots and wilting."

    # Context information
    # معلومات السياق
    context = {
        'crop_type': 'tomato',
        'symptoms': ['yellow spots', 'wilting', 'leaf discoloration'],
        'weather': 'high humidity, warm temperatures',
        'region': 'Mediterranean'
    }

    # Convene the diagnosis council
    # عقد مجلس التشخيص
    decision = await council_manager.convene_council(
        council_type=CouncilType.DIAGNOSIS_COUNCIL,
        query=query,
        agents=agents,
        context=context,
        consensus_strategy=ConsensusStrategy.EXPERTISE_WEIGHTED,
        min_confidence=0.6
    )

    # Display results
    # عرض النتائج
    print(f"Decision: {decision.decision}")
    print(f"Confidence: {decision.confidence:.2f}")
    print(f"Consensus Level: {decision.consensus_level:.2f}")
    print(f"Participating Agents: {', '.join(decision.participating_agents)}")
    print(f"Strategy: {decision.consensus_strategy.value if decision.consensus_strategy else 'N/A'}")
    print(f"\nSupporting Opinions: {len(decision.supporting_opinions)}")
    print(f"Dissenting Opinions: {len(decision.dissenting_opinions)}")
    print(f"Conflicts: {len(decision.conflicts)}")

    if decision.resolution_notes:
        print(f"\nResolution Notes:\n{decision.resolution_notes}")

    return decision


async def example_treatment_council():
    """
    Example: Treatment Planning Council
    مثال: مجلس تخطيط العلاج

    Agents discuss and agree on the best treatment approach.
    يناقش الوكلاء ويتفقون على أفضل نهج للعلاج.
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Treatment Planning Council")
    print("مثال 2: مجلس تخطيط العلاج")
    print("="*80 + "\n")

    # Create specialized treatment agents
    # إنشاء وكلاء علاج متخصصين
    agents = [
        MockAgent("disease_expert", "Treatment Specialist", 0.9),
        MockAgent("fertilizer_expert", "Agronomist", 0.85),
        MockAgent("irrigation_advisor", "Water Management Expert", 0.8),
        MockAgent("ecological_expert", "Organic Farming Expert", 0.88),
    ]

    council_manager = CouncilManager()

    query = "What treatment should we apply for early blight on tomatoes?"

    context = {
        'disease': 'early blight',
        'crop_type': 'tomato',
        'severity': 'moderate',
        'organic_only': True,
        'budget': 'medium'
    }

    # Try different consensus strategies
    # تجربة استراتيجيات إجماع مختلفة
    strategies = [
        ConsensusStrategy.MAJORITY_VOTE,
        ConsensusStrategy.WEIGHTED_CONFIDENCE,
        ConsensusStrategy.EXPERTISE_WEIGHTED,
        ConsensusStrategy.SUPERMAJORITY,
    ]

    print("Comparing different consensus strategies:")
    print("مقارنة استراتيجيات الإجماع المختلفة:\n")

    results = {}
    for strategy in strategies:
        decision = await council_manager.convene_council(
            council_type=CouncilType.TREATMENT_COUNCIL,
            query=query,
            agents=agents,
            context=context,
            consensus_strategy=strategy,
        )

        results[strategy] = decision

        print(f"\n{strategy.value}:")
        print(f"  Confidence: {decision.confidence:.2f}")
        print(f"  Consensus: {decision.consensus_level:.2f}")
        print(f"  Supporting: {len(decision.supporting_opinions)}/{len(agents)} agents")

    # Find best strategy
    # إيجاد أفضل استراتيجية
    best_strategy = max(results.items(), key=lambda x: x[1].confidence)
    print(f"\n✓ Best strategy: {best_strategy[0].value} (confidence: {best_strategy[1].confidence:.2f})")

    return results


async def example_emergency_council():
    """
    Example: Emergency Response Council
    مثال: مجلس الاستجابة للطوارئ

    Rapid decision-making for urgent agricultural issues.
    اتخاذ قرار سريع لقضايا زراعية عاجلة.
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Emergency Response Council")
    print("مثال 3: مجلس الاستجابة للطوارئ")
    print("="*80 + "\n")

    # Create emergency response team
    # إنشاء فريق الاستجابة للطوارئ
    agents = [
        MockAgent("disease_expert", "Emergency Disease Control", 0.95),
        MockAgent("pest_control_expert", "Pest Emergency Specialist", 0.92),
        MockAgent("irrigation_advisor", "Water Crisis Manager", 0.88),
        MockAgent("weather_analyst", "Climate Emergency Expert", 0.85),
    ]

    council_manager = CouncilManager()

    query = "Urgent: Severe pest outbreak detected. What immediate action should be taken?"

    context = {
        'emergency_type': 'pest_outbreak',
        'severity': 'severe',
        'affected_area': '50 hectares',
        'time_constraint': '24 hours',
        'crop_value': 'high'
    }

    # Use unanimous strategy for critical decisions
    # استخدام استراتيجية الإجماع للقرارات الحرجة
    decision = await council_manager.convene_council(
        council_type=CouncilType.EMERGENCY_COUNCIL,
        query=query,
        agents=agents,
        context=context,
        consensus_strategy=ConsensusStrategy.UNANIMOUS,
        min_confidence=0.8
    )

    print(f"Emergency Decision: {decision.decision}")
    print(f"Confidence: {decision.confidence:.2f}")
    print(f"Consensus Level: {decision.consensus_level:.2f}")
    print(f"Response Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if decision.conflicts:
        print(f"\n⚠ Warning: {len(decision.conflicts)} conflicts detected")
        for i, conflict in enumerate(decision.conflicts, 1):
            print(f"  {i}. {conflict.description} (severity: {conflict.severity:.2f})")

    return decision


async def example_consensus_comparison():
    """
    Example: Compare All Consensus Strategies
    مثال: مقارنة جميع استراتيجيات الإجماع

    Demonstrates the ConsensusEngine's ability to compare strategies.
    يوضح قدرة محرك الإجماع على مقارنة الاستراتيجيات.
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Consensus Strategy Comparison")
    print("مثال 4: مقارنة استراتيجيات الإجماع")
    print("="*80 + "\n")

    # Create sample opinions
    # إنشاء آراء عينة
    opinions = [
        AgentOpinion(
            agent_id="disease_expert",
            agent_type="Pathologist",
            recommendation="Apply copper-based fungicide",
            confidence=0.9,
            evidence=["Symptom match", "Regional prevalence", "Lab tests"],
        ),
        AgentOpinion(
            agent_id="ecological_expert",
            agent_type="Ecologist",
            recommendation="Apply copper-based fungicide",
            confidence=0.85,
            evidence=["Organic approved", "Environmental safety"],
            dissenting_points=["May need additional measures"],
        ),
        AgentOpinion(
            agent_id="fertilizer_expert",
            agent_type="Agronomist",
            recommendation="Improve soil nutrition first",
            confidence=0.75,
            evidence=["Nutrient deficiency detected"],
            dissenting_points=["Fungicide may not address root cause"],
        ),
        AgentOpinion(
            agent_id="irrigation_advisor",
            agent_type="Water Expert",
            recommendation="Apply copper-based fungicide",
            confidence=0.8,
            evidence=["Moisture conditions favorable for fungus"],
        ),
    ]

    # Create consensus engine
    # إنشاء محرك الإجماع
    engine = ConsensusEngine()

    # Compare all strategies
    # مقارنة جميع الاستراتيجيات
    results = engine.compare_strategies(opinions)

    print("Strategy Comparison Results:")
    print("نتائج مقارنة الاستراتيجيات:\n")

    for strategy, result in results.items():
        print(f"\n{strategy.value}:")
        print(f"  Decision: {result['decision'][:60]}...")
        print(f"  Confidence: {result['confidence']:.2f}")
        if 'details' in result:
            print(f"  Details: {result['details']}")

    # Find best strategy
    # إيجاد أفضل استراتيجية
    best_strategy, best_result = engine.get_best_strategy(opinions, criteria='confidence')

    print(f"\n\n✓ Recommended Strategy: {best_strategy.value}")
    print(f"  Confidence: {best_result['confidence']:.2f}")
    print(f"  Decision: {best_result['decision']}")

    return results


async def example_council_history():
    """
    Example: Council Decision History
    مثال: سجل قرارات المجلس

    Demonstrates tracking and reviewing council decisions.
    يوضح تتبع ومراجعة قرارات المجلس.
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Council History Tracking")
    print("مثال 5: تتبع سجل المجلس")
    print("="*80 + "\n")

    council_manager = CouncilManager()

    # Create some sample decisions
    # إنشاء بعض القرارات العينة
    agents = [
        MockAgent("disease_expert", "Pathologist", 0.9),
        MockAgent("pest_control_expert", "Entomologist", 0.85),
    ]

    queries = [
        ("Diagnose leaf spots on wheat", CouncilType.DIAGNOSIS_COUNCIL),
        ("Plan irrigation for corn field", CouncilType.RESOURCE_COUNCIL),
        ("Respond to frost warning", CouncilType.EMERGENCY_COUNCIL),
    ]

    for query, council_type in queries:
        decision = await council_manager.convene_council(
            council_type=council_type,
            query=query,
            agents=agents,
            consensus_strategy=ConsensusStrategy.WEIGHTED_CONFIDENCE
        )
        print(f"✓ Created {council_type.value} decision")

    # Review history
    # مراجعة السجل
    print("\n\nCouncil Decision History:")
    print("سجل قرارات المجلس:\n")

    history = council_manager.get_council_history(limit=10)

    for i, decision in enumerate(history, 1):
        print(f"\n{i}. {decision.council_type.value if decision.council_type else 'N/A'}")
        print(f"   Time: {decision.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Confidence: {decision.confidence:.2f}")
        print(f"   Consensus: {decision.consensus_level:.2f}")
        print(f"   Agents: {len(decision.participating_agents)}")

    # Filter by type
    # التصفية حسب النوع
    print(f"\n\nEmergency Council Decisions:")
    emergency_decisions = council_manager.get_council_history(
        council_type=CouncilType.EMERGENCY_COUNCIL
    )
    print(f"Found {len(emergency_decisions)} emergency decisions")

    return history


async def main():
    """
    Run all examples
    تشغيل جميع الأمثلة
    """
    print("\n" + "="*80)
    print("SAHOOL Multi-Agent Council and Consensus System")
    print("نظام المجلس والإجماع لنظام SAHOOL متعدد الوكلاء")
    print("="*80)

    # Run examples
    # تشغيل الأمثلة
    await example_diagnosis_council()
    await example_treatment_council()
    await example_emergency_council()
    await example_consensus_comparison()
    await example_council_history()

    print("\n" + "="*80)
    print("Examples completed successfully!")
    print("اكتملت الأمثلة بنجاح!")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Run the examples
    # تشغيل الأمثلة
    asyncio.run(main())
