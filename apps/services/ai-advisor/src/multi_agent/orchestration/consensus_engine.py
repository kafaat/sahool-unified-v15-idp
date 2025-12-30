"""
Consensus Engine for Multi-Agent System
محرك الإجماع لنظام الوكلاء المتعددين

Implements various consensus algorithms for agent decision-making.
ينفذ خوارزميات إجماع متنوعة لاتخاذ قرارات الوكلاء.
"""

from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import structlog
from collections import Counter
import math

logger = structlog.get_logger()


class ConsensusStrategy(Enum):
    """
    Strategies for building consensus
    استراتيجيات بناء الإجماع
    """
    MAJORITY_VOTE = "majority_vote"  # Simple majority | الأغلبية البسيطة
    WEIGHTED_CONFIDENCE = "weighted_confidence"  # Weight by agent confidence | الوزن حسب ثقة الوكيل
    EXPERTISE_WEIGHTED = "expertise_weighted"  # Weight by agent expertise | الوزن حسب خبرة الوكيل
    UNANIMOUS = "unanimous"  # Require all agents to agree | يتطلب موافقة جميع الوكلاء
    SUPERMAJORITY = "supermajority"  # Require 2/3 or more agreement | يتطلب موافقة 2/3 أو أكثر
    BAYESIAN = "bayesian"  # Bayesian belief aggregation | تجميع المعتقدات البايزية
    RANKED_CHOICE = "ranked_choice"  # Ranked choice voting | التصويت بالاختيار المصنف


class ConsensusEngine:
    """
    Engine for applying consensus strategies to agent opinions
    محرك لتطبيق استراتيجيات الإجماع على آراء الوكلاء

    Implements various consensus algorithms to aggregate agent opinions
    into a single decision with confidence scores.

    ينفذ خوارزميات إجماع متنوعة لتجميع آراء الوكلاء
    في قرار واحد مع درجات الثقة.
    """

    def __init__(self):
        """
        Initialize Consensus Engine
        تهيئة محرك الإجماع
        """
        self.strategy_map: Dict[ConsensusStrategy, Callable] = {
            ConsensusStrategy.MAJORITY_VOTE: self._majority_vote,
            ConsensusStrategy.WEIGHTED_CONFIDENCE: self._weighted_confidence,
            ConsensusStrategy.EXPERTISE_WEIGHTED: self._expertise_weighted,
            ConsensusStrategy.UNANIMOUS: self._unanimous,
            ConsensusStrategy.SUPERMAJORITY: self._supermajority,
            ConsensusStrategy.BAYESIAN: self._bayesian,
            ConsensusStrategy.RANKED_CHOICE: self._ranked_choice,
        }

        logger.info("consensus_engine_initialized", strategies=len(self.strategy_map))

    def apply_strategy(
        self,
        opinions: List[Any],  # List[AgentOpinion]
        strategy: ConsensusStrategy = ConsensusStrategy.WEIGHTED_CONFIDENCE,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Apply a consensus strategy to agent opinions
        تطبيق استراتيجية الإجماع على آراء الوكلاء

        Args:
            opinions: List of agent opinions | قائمة آراء الوكلاء
            strategy: Consensus strategy to use | استراتيجية الإجماع المراد استخدامها
            context: Additional context | سياق إضافي

        Returns:
            Dict containing decision, confidence, and notes
            قاموس يحتوي على القرار والثقة والملاحظات
        """
        if not opinions:
            logger.warning("no_opinions_for_consensus")
            return {
                'decision': 'No consensus possible - no opinions',
                'confidence': 0.0,
                'notes': 'No agent opinions were provided'
            }

        logger.info(
            "applying_consensus_strategy",
            strategy=strategy.value,
            num_opinions=len(opinions)
        )

        try:
            strategy_func = self.strategy_map.get(strategy)
            if not strategy_func:
                logger.error("unknown_strategy", strategy=strategy.value)
                # Fall back to majority vote
                # الرجوع إلى التصويت بالأغلبية
                strategy_func = self._majority_vote

            result = strategy_func(opinions, context)

            logger.info(
                "consensus_result",
                strategy=strategy.value,
                confidence=result.get('confidence', 0.0)
            )

            return result

        except Exception as e:
            logger.error(
                "consensus_strategy_failed",
                strategy=strategy.value,
                error=str(e),
                exc_info=True
            )
            # Return a default result
            # إرجاع نتيجة افتراضية
            return {
                'decision': 'Consensus failed',
                'confidence': 0.0,
                'notes': f'Error applying strategy: {str(e)}'
            }

    def _majority_vote(
        self,
        opinions: List[Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simple majority vote - most common recommendation wins
        التصويت بالأغلبية البسيطة - التوصية الأكثر شيوعاً تفوز

        Args:
            opinions: List of agent opinions | قائمة آراء الوكلاء
            context: Additional context | سياق إضافي

        Returns:
            Consensus result | نتيجة الإجماع
        """
        if not opinions:
            return {'decision': 'No opinions', 'confidence': 0.0, 'notes': ''}

        # Count recommendations
        # عد التوصيات
        recommendations = [op.recommendation for op in opinions]
        counter = Counter(recommendations)
        most_common = counter.most_common(1)[0]

        decision = most_common[0]
        vote_count = most_common[1]
        total_votes = len(opinions)

        # Confidence is the ratio of votes
        # الثقة هي نسبة الأصوات
        confidence = vote_count / total_votes

        # Get average confidence of agents who voted for winning recommendation
        # الحصول على متوسط ثقة الوكلاء الذين صوتوا للتوصية الفائزة
        winning_opinions = [op for op in opinions if op.recommendation == decision]
        avg_agent_confidence = sum(op.confidence for op in winning_opinions) / len(winning_opinions)

        # Combine vote ratio with agent confidence
        # الجمع بين نسبة التصويت وثقة الوكيل
        final_confidence = (confidence * 0.6) + (avg_agent_confidence * 0.4)

        notes = f"Majority vote: {vote_count}/{total_votes} agents agreed. Average agent confidence: {avg_agent_confidence:.2f}"

        return {
            'decision': decision,
            'confidence': final_confidence,
            'notes': notes,
            'details': {
                'vote_count': vote_count,
                'total_votes': total_votes,
                'vote_ratio': confidence,
                'avg_agent_confidence': avg_agent_confidence
            }
        }

    def _weighted_confidence(
        self,
        opinions: List[Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Weight recommendations by agent confidence scores
        ترجيح التوصيات حسب درجات ثقة الوكيل

        Args:
            opinions: List of agent opinions | قائمة آراء الوكلاء
            context: Additional context | سياق إضافي

        Returns:
            Consensus result | نتيجة الإجماع
        """
        if not opinions:
            return {'decision': 'No opinions', 'confidence': 0.0, 'notes': ''}

        # Group opinions by recommendation and sum confidence scores
        # تجميع الآراء حسب التوصية وجمع درجات الثقة
        weighted_votes: Dict[str, float] = {}
        weighted_counts: Dict[str, int] = {}

        for opinion in opinions:
            rec = opinion.recommendation
            if rec not in weighted_votes:
                weighted_votes[rec] = 0
                weighted_counts[rec] = 0

            weighted_votes[rec] += opinion.confidence
            weighted_counts[rec] += 1

        # Find recommendation with highest weighted score
        # إيجاد التوصية بأعلى درجة مرجحة
        if not weighted_votes:
            return {'decision': 'No valid opinions', 'confidence': 0.0, 'notes': ''}

        decision = max(weighted_votes.items(), key=lambda x: x[1])[0]
        winning_weight = weighted_votes[decision]
        total_weight = sum(weighted_votes.values())

        # Confidence is the proportion of total confidence weight
        # الثقة هي نسبة الوزن الإجمالي للثقة
        confidence = winning_weight / total_weight if total_weight > 0 else 0

        # Also factor in the number of agents
        # أيضاً احسب عدد الوكلاء
        agent_ratio = weighted_counts[decision] / len(opinions)

        # Combine weight ratio with agent ratio
        # الجمع بين نسبة الوزن ونسبة الوكيل
        final_confidence = (confidence * 0.7) + (agent_ratio * 0.3)

        notes = (
            f"Weighted confidence: {weighted_counts[decision]} agents with "
            f"combined confidence {winning_weight:.2f}/{total_weight:.2f}"
        )

        return {
            'decision': decision,
            'confidence': final_confidence,
            'notes': notes,
            'details': {
                'winning_weight': winning_weight,
                'total_weight': total_weight,
                'weight_ratio': confidence,
                'agent_count': weighted_counts[decision],
                'agent_ratio': agent_ratio
            }
        }

    def _expertise_weighted(
        self,
        opinions: List[Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Weight recommendations by agent expertise in the domain
        ترجيح التوصيات حسب خبرة الوكيل في المجال

        Args:
            opinions: List of agent opinions | قائمة آراء الوكلاء
            context: Additional context | سياق إضافي

        Returns:
            Consensus result | نتيجة الإجماع
        """
        if not opinions:
            return {'decision': 'No opinions', 'confidence': 0.0, 'notes': ''}

        # Define expertise weights for different agent types
        # تحديد أوزان الخبرة لأنواع الوكلاء المختلفة
        expertise_weights = {
            'disease_expert': 1.5,
            'irrigation_advisor': 1.3,
            'ecological_expert': 1.4,
            'fertilizer_expert': 1.3,
            'weather_analyst': 1.2,
            'pest_control_expert': 1.5,
            'default': 1.0
        }

        # Context can override expertise weights
        # يمكن للسياق تجاوز أوزان الخبرة
        if context and 'expertise_weights' in context:
            expertise_weights.update(context['expertise_weights'])

        # Calculate weighted votes using both confidence and expertise
        # حساب الأصوات المرجحة باستخدام كل من الثقة والخبرة
        weighted_votes: Dict[str, float] = {}
        vote_details: Dict[str, List[tuple]] = {}

        for opinion in opinions:
            rec = opinion.recommendation
            if rec not in weighted_votes:
                weighted_votes[rec] = 0
                vote_details[rec] = []

            # Get expertise weight for this agent type
            # الحصول على وزن الخبرة لنوع الوكيل هذا
            agent_type_key = opinion.agent_id.lower()
            expertise_weight = expertise_weights.get(agent_type_key, expertise_weights['default'])

            # Combined weight = confidence × expertise
            # الوزن المشترك = الثقة × الخبرة
            combined_weight = opinion.confidence * expertise_weight

            weighted_votes[rec] += combined_weight
            vote_details[rec].append((opinion.agent_id, opinion.confidence, expertise_weight))

        # Find recommendation with highest weighted score
        # إيجاد التوصية بأعلى درجة مرجحة
        if not weighted_votes:
            return {'decision': 'No valid opinions', 'confidence': 0.0, 'notes': ''}

        decision = max(weighted_votes.items(), key=lambda x: x[1])[0]
        winning_weight = weighted_votes[decision]
        total_weight = sum(weighted_votes.values())

        confidence = winning_weight / total_weight if total_weight > 0 else 0

        # Get details of winning votes
        # الحصول على تفاصيل الأصوات الفائزة
        winning_details = vote_details[decision]
        agent_list = ', '.join([f"{agent}(conf:{conf:.2f}, exp:{exp:.2f})"
                                for agent, conf, exp in winning_details])

        notes = (
            f"Expertise-weighted consensus: {len(winning_details)} agents with "
            f"combined weight {winning_weight:.2f}/{total_weight:.2f}. "
            f"Agents: {agent_list}"
        )

        return {
            'decision': decision,
            'confidence': confidence,
            'notes': notes,
            'details': {
                'winning_weight': winning_weight,
                'total_weight': total_weight,
                'participating_agents': len(winning_details),
                'expertise_applied': True
            }
        }

    def _unanimous(
        self,
        opinions: List[Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Require unanimous agreement from all agents
        يتطلب موافقة بالإجماع من جميع الوكلاء

        Args:
            opinions: List of agent opinions | قائمة آراء الوكلاء
            context: Additional context | سياق إضافي

        Returns:
            Consensus result | نتيجة الإجماع
        """
        if not opinions:
            return {'decision': 'No opinions', 'confidence': 0.0, 'notes': ''}

        # Check if all recommendations are the same
        # التحقق مما إذا كانت جميع التوصيات متشابهة
        recommendations = [op.recommendation for op in opinions]
        unique_recommendations = set(recommendations)

        if len(unique_recommendations) == 1:
            # Unanimous agreement
            # موافقة بالإجماع
            decision = recommendations[0]

            # Average confidence of all agents
            # متوسط ثقة جميع الوكلاء
            avg_confidence = sum(op.confidence for op in opinions) / len(opinions)

            notes = f"Unanimous agreement: All {len(opinions)} agents agreed with average confidence {avg_confidence:.2f}"

            return {
                'decision': decision,
                'confidence': avg_confidence,
                'notes': notes,
                'details': {
                    'unanimous': True,
                    'agent_count': len(opinions),
                    'avg_confidence': avg_confidence
                }
            }
        else:
            # No unanimous agreement - fall back to majority
            # لا يوجد اتفاق بالإجماع - الرجوع إلى الأغلبية
            fallback_result = self._majority_vote(opinions, context)

            notes = (
                f"Unanimous agreement not reached. {len(unique_recommendations)} different recommendations. "
                f"Falling back to majority: {fallback_result['notes']}"
            )

            return {
                'decision': fallback_result['decision'],
                'confidence': fallback_result['confidence'] * 0.7,  # Reduce confidence since not unanimous
                'notes': notes,
                'details': {
                    'unanimous': False,
                    'unique_recommendations': len(unique_recommendations),
                    'fallback_used': 'majority_vote'
                }
            }

    def _supermajority(
        self,
        opinions: List[Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Require supermajority (2/3 or more) agreement
        يتطلب موافقة الأغلبية العظمى (2/3 أو أكثر)

        Args:
            opinions: List of agent opinions | قائمة آراء الوكلاء
            context: Additional context | سياق إضافي

        Returns:
            Consensus result | نتيجة الإجماع
        """
        if not opinions:
            return {'decision': 'No opinions', 'confidence': 0.0, 'notes': ''}

        # Default supermajority threshold is 2/3
        # عتبة الأغلبية العظمى الافتراضية هي 2/3
        threshold = context.get('supermajority_threshold', 2/3) if context else 2/3

        # Count recommendations
        # عد التوصيات
        recommendations = [op.recommendation for op in opinions]
        counter = Counter(recommendations)
        most_common = counter.most_common(1)[0]

        decision = most_common[0]
        vote_count = most_common[1]
        total_votes = len(opinions)
        vote_ratio = vote_count / total_votes

        if vote_ratio >= threshold:
            # Supermajority achieved
            # تم الحصول على الأغلبية العظمى
            winning_opinions = [op for op in opinions if op.recommendation == decision]
            avg_confidence = sum(op.confidence for op in winning_opinions) / len(winning_opinions)

            # Boost confidence since we have supermajority
            # تعزيز الثقة لأن لدينا الأغلبية العظمى
            final_confidence = min(1.0, (vote_ratio * 0.5) + (avg_confidence * 0.5))

            notes = (
                f"Supermajority achieved: {vote_count}/{total_votes} agents ({vote_ratio:.1%}) agreed. "
                f"Threshold: {threshold:.1%}"
            )

            return {
                'decision': decision,
                'confidence': final_confidence,
                'notes': notes,
                'details': {
                    'supermajority': True,
                    'vote_count': vote_count,
                    'total_votes': total_votes,
                    'vote_ratio': vote_ratio,
                    'threshold': threshold
                }
            }
        else:
            # Supermajority not reached - fall back to weighted confidence
            # لم يتم الوصول إلى الأغلبية العظمى - الرجوع إلى الثقة المرجحة
            fallback_result = self._weighted_confidence(opinions, context)

            notes = (
                f"Supermajority not reached ({vote_ratio:.1%} < {threshold:.1%}). "
                f"Falling back to weighted confidence: {fallback_result['notes']}"
            )

            return {
                'decision': fallback_result['decision'],
                'confidence': fallback_result['confidence'] * 0.8,  # Reduce confidence
                'notes': notes,
                'details': {
                    'supermajority': False,
                    'vote_ratio': vote_ratio,
                    'threshold': threshold,
                    'fallback_used': 'weighted_confidence'
                }
            }

    def _bayesian(
        self,
        opinions: List[Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Bayesian belief aggregation - combine probabilities
        تجميع المعتقدات البايزية - الجمع بين الاحتمالات

        Args:
            opinions: List of agent opinions | قائمة آراء الوكلاء
            context: Additional context | سياق إضافي

        Returns:
            Consensus result | نتيجة الإجماع
        """
        if not opinions:
            return {'decision': 'No opinions', 'confidence': 0.0, 'notes': ''}

        # Group opinions by recommendation
        # تجميع الآراء حسب التوصية
        recommendation_groups: Dict[str, List[Any]] = {}
        for opinion in opinions:
            rec = opinion.recommendation
            if rec not in recommendation_groups:
                recommendation_groups[rec] = []
            recommendation_groups[rec].append(opinion)

        # Calculate Bayesian posterior for each recommendation
        # حساب البوستريور البايزي لكل توصية
        bayesian_scores: Dict[str, float] = {}

        # Prior probability (uniform)
        # الاحتمال القبلي (موحد)
        prior = 1.0 / len(recommendation_groups)

        for rec, group in recommendation_groups.items():
            # Combine confidences using Bayesian updating
            # الجمع بين الثقات باستخدام التحديث البايزي
            # P(rec | evidence) ∝ P(evidence | rec) × P(rec)

            # Start with prior
            # ابدأ بالاحتمال القبلي
            posterior = prior

            # Update with each agent's confidence (treating as likelihood)
            # التحديث بثقة كل وكيل (يعامل كاحتمالية)
            for opinion in group:
                # Likelihood ratio: confidence vs. (1 - confidence)
                # نسبة الاحتمالية: الثقة مقابل (1 - الثقة)
                likelihood = opinion.confidence / max(1 - opinion.confidence, 0.01)
                posterior *= likelihood

            bayesian_scores[rec] = posterior

        # Normalize scores to probabilities
        # تطبيع الدرجات إلى احتمالات
        total_score = sum(bayesian_scores.values())
        if total_score > 0:
            for rec in bayesian_scores:
                bayesian_scores[rec] /= total_score

        # Select recommendation with highest posterior probability
        # اختيار التوصية بأعلى احتمال بوستريور
        decision = max(bayesian_scores.items(), key=lambda x: x[1])[0]
        confidence = bayesian_scores[decision]

        supporting_agents = len(recommendation_groups[decision])

        notes = (
            f"Bayesian aggregation: Posterior probability {confidence:.2%} "
            f"with {supporting_agents} supporting agents"
        )

        return {
            'decision': decision,
            'confidence': confidence,
            'notes': notes,
            'details': {
                'posterior_probability': confidence,
                'supporting_agents': supporting_agents,
                'all_posteriors': bayesian_scores,
                'method': 'bayesian'
            }
        }

    def _ranked_choice(
        self,
        opinions: List[Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ranked choice voting - agents can have preferences
        التصويت بالاختيار المصنف - يمكن أن يكون للوكلاء تفضيلات

        Args:
            opinions: List of agent opinions | قائمة آراء الوكلاء
            context: Additional context | سياق إضافي

        Returns:
            Consensus result | نتيجة الإجماع
        """
        if not opinions:
            return {'decision': 'No opinions', 'confidence': 0.0, 'notes': ''}

        # For now, treat confidence as ranking
        # في الوقت الحالي، عامل الثقة كتصنيف
        # Higher confidence = higher ranking
        # ثقة أعلى = تصنيف أعلى

        # Group by recommendation and calculate ranked scores
        # التجميع حسب التوصية وحساب درجات التصنيف
        ranked_scores: Dict[str, float] = {}
        vote_counts: Dict[str, int] = {}

        for opinion in opinions:
            rec = opinion.recommendation
            if rec not in ranked_scores:
                ranked_scores[rec] = 0
                vote_counts[rec] = 0

            # Score is confidence squared (to emphasize high confidence)
            # الدرجة هي الثقة المربعة (للتأكيد على الثقة العالية)
            ranked_scores[rec] += opinion.confidence ** 2
            vote_counts[rec] += 1

        # Find recommendation with highest ranked score
        # إيجاد التوصية بأعلى درجة مصنفة
        if not ranked_scores:
            return {'decision': 'No valid opinions', 'confidence': 0.0, 'notes': ''}

        decision = max(ranked_scores.items(), key=lambda x: x[1])[0]
        winning_score = ranked_scores[decision]
        total_score = sum(ranked_scores.values())

        # Confidence based on score proportion
        # الثقة بناءً على نسبة الدرجة
        confidence = winning_score / total_score if total_score > 0 else 0

        # Also factor in number of votes
        # أيضاً احسب عدد الأصوات
        vote_proportion = vote_counts[decision] / len(opinions)

        # Combine score and vote proportion
        # الجمع بين الدرجة ونسبة التصويت
        final_confidence = (confidence * 0.6) + (vote_proportion * 0.4)

        notes = (
            f"Ranked choice: {vote_counts[decision]} agents with "
            f"ranked score {winning_score:.2f}/{total_score:.2f}"
        )

        return {
            'decision': decision,
            'confidence': final_confidence,
            'notes': notes,
            'details': {
                'ranked_score': winning_score,
                'total_score': total_score,
                'score_ratio': confidence,
                'vote_count': vote_counts[decision],
                'vote_proportion': vote_proportion
            }
        }

    def compare_strategies(
        self,
        opinions: List[Any],
        strategies: Optional[List[ConsensusStrategy]] = None
    ) -> Dict[ConsensusStrategy, Dict[str, Any]]:
        """
        Compare results of different consensus strategies
        مقارنة نتائج استراتيجيات الإجماع المختلفة

        Args:
            opinions: List of agent opinions | قائمة آراء الوكلاء
            strategies: Strategies to compare (all if None) | الاستراتيجيات للمقارنة

        Returns:
            Dict mapping strategies to their results
            قاموس يربط الاستراتيجيات بنتائجها
        """
        if strategies is None:
            strategies = list(ConsensusStrategy)

        results = {}

        for strategy in strategies:
            try:
                result = self.apply_strategy(opinions, strategy)
                results[strategy] = result
            except Exception as e:
                logger.error(
                    "strategy_comparison_failed",
                    strategy=strategy.value,
                    error=str(e)
                )
                results[strategy] = {
                    'decision': 'Error',
                    'confidence': 0.0,
                    'notes': f'Failed: {str(e)}'
                }

        logger.info(
            "strategies_compared",
            num_strategies=len(results),
            num_opinions=len(opinions)
        )

        return results

    def get_best_strategy(
        self,
        opinions: List[Any],
        criteria: str = 'confidence'
    ) -> tuple[ConsensusStrategy, Dict[str, Any]]:
        """
        Determine the best strategy for given opinions
        تحديد أفضل استراتيجية للآراء المعطاة

        Args:
            opinions: List of agent opinions | قائمة آراء الوكلاء
            criteria: Selection criteria ('confidence' or 'consensus') | معايير الاختيار

        Returns:
            Tuple of (best_strategy, result) | مجموعة من (أفضل_استراتيجية، النتيجة)
        """
        results = self.compare_strategies(opinions)

        if not results:
            return ConsensusStrategy.MAJORITY_VOTE, {'decision': 'No results', 'confidence': 0.0}

        if criteria == 'confidence':
            # Choose strategy with highest confidence
            # اختيار الاستراتيجية بأعلى ثقة
            best = max(results.items(), key=lambda x: x[1].get('confidence', 0))
        else:
            # Choose based on other criteria (future implementation)
            # الاختيار بناءً على معايير أخرى (تنفيذ مستقبلي)
            best = max(results.items(), key=lambda x: x[1].get('confidence', 0))

        logger.info(
            "best_strategy_selected",
            strategy=best[0].value,
            confidence=best[1].get('confidence', 0),
            criteria=criteria
        )

        return best[0], best[1]
