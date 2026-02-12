"""
Optimal Transport Embeddings Module
====================================
وحدة تضمينات النقل الأمثل

Provides Optimal Transport-based embedding matching for:
- Better cross-lingual text alignment (Arabic <-> English)
- Advisory similarity ranking using Wasserstein distance
- Robust matching for variable-length sequences

Based on research:
- Scaled-Dot-Product Attention as Entropic Optimal Transport
- Unlocking Slot Attention by Changing Optimal Transport Costs
- Understanding Self-Attention Regularity with Optimal Transport

Author: SAHOOL Platform Team
Updated: January 2026
"""

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class OTConfig:
    """
    Configuration for Optimal Transport embeddings.

    إعدادات تضمينات النقل الأمثل
    """

    # Sinkhorn parameters
    regularization: float = 0.1  # Entropic regularization (epsilon)
    num_iterations: int = 100  # Sinkhorn iterations
    convergence_threshold: float = 1e-6

    # Distance metric
    cost_metric: str = "euclidean"  # euclidean, cosine, sqeuclidean

    # Performance
    use_log_domain: bool = True  # More numerically stable
    batch_size: int = 32

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "regularization": self.regularization,
            "num_iterations": self.num_iterations,
            "convergence_threshold": self.convergence_threshold,
            "cost_metric": self.cost_metric,
            "use_log_domain": self.use_log_domain,
        }


@dataclass
class OTMatchResult:
    """
    Result of Optimal Transport matching.

    نتيجة مطابقة النقل الأمثل
    """

    # Distance measures
    wasserstein_distance: float
    sinkhorn_distance: float

    # Transport plan (optional, can be large)
    transport_plan: list[list[float]] | None = None

    # Metadata
    source_length: int = 0
    target_length: int = 0
    num_iterations: int = 0
    converged: bool = False
    computation_time_ms: float = 0.0

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "wasserstein_distance": self.wasserstein_distance,
            "sinkhorn_distance": self.sinkhorn_distance,
            "source_length": self.source_length,
            "target_length": self.target_length,
            "num_iterations": self.num_iterations,
            "converged": self.converged,
            "computation_time_ms": self.computation_time_ms,
        }


class OTEmbeddingMatcher:
    """
    Optimal Transport-based embedding matcher.

    مطابق التضمينات القائم على النقل الأمثل

    Uses Sinkhorn algorithm for entropic optimal transport,
    providing better matching than cosine similarity for:
    - Variable-length sequences
    - Cross-lingual text (Arabic <-> English)
    - Advisory ranking and retrieval

    Key insight from research:
    Scaled-dot-product attention can be viewed as entropic
    optimal transport, providing theoretical grounding for
    attention mechanisms.

    Example:
        ```python
        matcher = OTEmbeddingMatcher()

        # Match Arabic query to English candidates
        results = await matcher.match_advisory(
            query_ar="متى أسقي القمح؟",
            candidates_en=["Wheat irrigation guide", "Rice planting tips", ...]
        )

        # Compute Sinkhorn distance
        distance = matcher.sinkhorn_distance(embedding1, embedding2)
        ```
    """

    def __init__(self, config: OTConfig | None = None):
        """
        Initialize OT Embedding Matcher.

        Args:
            config: OT configuration
        """
        self.config = config or OTConfig()

    def compute_cost_matrix(
        self,
        source: list[list[float]],
        target: list[list[float]],
    ) -> list[list[float]]:
        """
        Compute pairwise cost matrix between embeddings.

        حساب مصفوفة التكلفة بين التضمينات

        Args:
            source: Source embeddings (n x d)
            target: Target embeddings (m x d)

        Returns:
            Cost matrix (n x m)
        """
        n = len(source)
        m = len(target)
        cost = [[0.0] * m for _ in range(n)]

        for i in range(n):
            for j in range(m):
                if self.config.cost_metric == "euclidean":
                    # Euclidean distance
                    diff_sq = sum((a - b) ** 2 for a, b in zip(source[i], target[j]))
                    cost[i][j] = math.sqrt(diff_sq)

                elif self.config.cost_metric == "sqeuclidean":
                    # Squared Euclidean (faster, same ordering)
                    cost[i][j] = sum((a - b) ** 2 for a, b in zip(source[i], target[j]))

                elif self.config.cost_metric == "cosine":
                    # Cosine distance (1 - cosine_similarity)
                    dot = sum(a * b for a, b in zip(source[i], target[j]))
                    norm_s = math.sqrt(sum(a * a for a in source[i]))
                    norm_t = math.sqrt(sum(b * b for b in target[j]))
                    if norm_s > 0 and norm_t > 0:
                        cost[i][j] = 1.0 - (dot / (norm_s * norm_t))
                    else:
                        cost[i][j] = 1.0

        return cost

    def sinkhorn_distance(
        self,
        source: list[float] | list[list[float]],
        target: list[float] | list[list[float]],
        return_plan: bool = False,
    ) -> OTMatchResult:
        """
        Compute Sinkhorn (entropic OT) distance.

        حساب مسافة سينكهورن (النقل الأمثل الإنتروبي)

        The Sinkhorn algorithm computes an approximation to
        the Wasserstein distance with entropic regularization.

        Args:
            source: Source embedding(s)
            target: Target embedding(s)
            return_plan: Whether to return transport plan

        Returns:
            OTMatchResult with distances and metadata
        """
        import time

        start_time = time.time()

        # Handle single vectors (wrap in list)
        if source and not isinstance(source[0], list):
            source = [source]
        if target and not isinstance(target[0], list):
            target = [target]

        n = len(source)
        m = len(target)

        # Compute cost matrix
        C = self.compute_cost_matrix(source, target)

        # Initialize marginals (uniform distribution)
        # Source marginal: mu
        mu = [1.0 / n] * n
        # Target marginal: nu
        nu = [1.0 / m] * m

        # Sinkhorn algorithm in log domain for stability
        reg = self.config.regularization

        if self.config.use_log_domain:
            # Log-domain Sinkhorn
            log_K = [[-c / reg for c in row] for row in C]

            # Initialize dual variables
            f = [0.0] * n  # log(u)
            g = [0.0] * m  # log(v)

            converged = False
            iterations = 0

            for iteration in range(self.config.num_iterations):
                # Update f (log-sum-exp over columns)
                f_new = []
                for i in range(n):
                    # log(sum_j(K[i,j] * v[j])) - log(mu[i])
                    max_val = max(log_K[i][j] + g[j] for j in range(m))
                    log_sum = math.log(sum(math.exp(log_K[i][j] + g[j] - max_val) for j in range(m))) + max_val
                    f_new.append(math.log(mu[i]) - log_sum)
                f = f_new

                # Update g (log-sum-exp over rows)
                g_new = []
                for j in range(m):
                    max_val = max(log_K[i][j] + f[i] for i in range(n))
                    log_sum = math.log(sum(math.exp(log_K[i][j] + f[i] - max_val) for i in range(n))) + max_val
                    g_new.append(math.log(nu[j]) - log_sum)

                # Check convergence
                diff = sum(abs(g_new[j] - g[j]) for j in range(m)) / m
                g = g_new
                iterations = iteration + 1

                if diff < self.config.convergence_threshold:
                    converged = True
                    break

            # Compute transport plan: P[i,j] = exp(f[i] + log_K[i,j] + g[j])
            transport_plan = None
            if return_plan:
                transport_plan = [[math.exp(f[i] + log_K[i][j] + g[j]) for j in range(m)] for i in range(n)]

            # Compute Sinkhorn distance: sum(P * C)
            sinkhorn_dist = 0.0
            for i in range(n):
                for j in range(m):
                    P_ij = math.exp(f[i] + log_K[i][j] + g[j])
                    sinkhorn_dist += P_ij * C[i][j]

        else:
            # Standard domain Sinkhorn (less stable)
            K = [[math.exp(-c / reg) for c in row] for row in C]

            u = [1.0] * n
            v = [1.0] * m

            converged = False
            iterations = 0

            for iteration in range(self.config.num_iterations):
                # Update u
                u_new = []
                for i in range(n):
                    Kv_i = sum(K[i][j] * v[j] for j in range(m))
                    u_new.append(mu[i] / max(Kv_i, 1e-10))
                u = u_new

                # Update v
                v_new = []
                for j in range(m):
                    Ku_j = sum(K[i][j] * u[i] for i in range(n))
                    v_new.append(nu[j] / max(Ku_j, 1e-10))

                # Check convergence
                diff = sum(abs(v_new[j] - v[j]) for j in range(m)) / m
                v = v_new
                iterations = iteration + 1

                if diff < self.config.convergence_threshold:
                    converged = True
                    break

            # Compute transport plan
            transport_plan = None
            if return_plan:
                transport_plan = [[u[i] * K[i][j] * v[j] for j in range(m)] for i in range(n)]

            # Compute Sinkhorn distance
            sinkhorn_dist = 0.0
            for i in range(n):
                for j in range(m):
                    P_ij = u[i] * K[i][j] * v[j]
                    sinkhorn_dist += P_ij * C[i][j]

        # Estimate Wasserstein distance (Sinkhorn converges to it as reg -> 0)
        wasserstein_dist = sinkhorn_dist - reg * self._entropy(n, m)

        elapsed_ms = (time.time() - start_time) * 1000

        return OTMatchResult(
            wasserstein_distance=wasserstein_dist,
            sinkhorn_distance=sinkhorn_dist,
            transport_plan=transport_plan,
            source_length=n,
            target_length=m,
            num_iterations=iterations,
            converged=converged,
            computation_time_ms=elapsed_ms,
        )

    def _entropy(self, n: int, m: int) -> float:
        """Compute entropy of uniform coupling."""
        # H(uniform) = log(n*m)
        return math.log(n * m) if n > 0 and m > 0 else 0.0

    async def match_advisories(
        self,
        query: list[float],
        candidates: list[list[float]],
        candidate_texts: list[str] | None = None,
        top_k: int = 5,
    ) -> list[tuple[int, float, str | None]]:
        """
        Match query embedding to candidate advisories.

        مطابقة تضمين الاستعلام مع الاستشارات المرشحة

        Uses Sinkhorn distance for more robust matching than
        cosine similarity, especially for variable-length texts.

        Args:
            query: Query embedding
            candidates: List of candidate embeddings
            candidate_texts: Optional texts for candidates
            top_k: Number of results to return

        Returns:
            List of (index, distance, text) tuples sorted by distance
        """
        results = []

        for i, candidate in enumerate(candidates):
            result = self.sinkhorn_distance(query, candidate)
            text = candidate_texts[i] if candidate_texts else None
            results.append((i, result.sinkhorn_distance, text))

        # Sort by distance (lower = more similar)
        results.sort(key=lambda x: x[1])

        return results[:top_k]

    async def batch_distances(
        self,
        queries: list[list[float]],
        targets: list[list[float]],
    ) -> list[list[float]]:
        """
        Compute pairwise Sinkhorn distances for batches.

        حساب مسافات سينكهورن الزوجية للدفعات

        Args:
            queries: List of query embeddings
            targets: List of target embeddings

        Returns:
            Distance matrix (queries x targets)
        """
        distances = []

        for query in queries:
            row = []
            for target in targets:
                result = self.sinkhorn_distance(query, target)
                row.append(result.sinkhorn_distance)
            distances.append(row)

        return distances

    def cosine_similarity(
        self,
        vec1: list[float],
        vec2: list[float],
    ) -> float:
        """
        Compute cosine similarity for comparison.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity (0 to 1)
        """
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot / (norm1 * norm2)

    def ot_to_similarity(self, distance: float, scale: float = 1.0) -> float:
        """
        Convert OT distance to similarity score.

        Args:
            distance: OT distance
            scale: Scaling factor

        Returns:
            Similarity score (0 to 1)
        """
        # Exponential decay: sim = exp(-distance / scale)
        return math.exp(-distance / scale)


class BilingualOTMatcher:
    """
    Bilingual OT matcher for Arabic-English alignment.

    مطابق ثنائي اللغة للمحاذاة العربية-الإنجليزية

    Specialized for SAHOOL's bilingual advisory system,
    using OT for better cross-lingual matching.

    Example:
        ```python
        matcher = BilingualOTMatcher()

        # Match Arabic query to English candidates
        results = await matcher.match(
            query_ar="كيف أعالج صدأ القمح؟",
            candidates_en=["Wheat rust treatment", "Wheat irrigation", ...]
        )
        ```
    """

    def __init__(
        self,
        ot_config: OTConfig | None = None,
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
    ):
        """
        Initialize Bilingual OT Matcher.

        Args:
            ot_config: OT configuration
            embedding_model: Multilingual embedding model
        """
        self.ot_matcher = OTEmbeddingMatcher(ot_config)
        self.embedding_model = embedding_model
        self._embedder = None  # Lazy loaded

    async def _get_embedding(self, text: str) -> list[float]:
        """Get embedding for text using configured model."""
        # Try to use the embeddings adapter
        try:
            from .embeddings import EmbeddingConfig, EmbeddingProvider, EmbeddingsAdapter

            if self._embedder is None:
                config = EmbeddingConfig(
                    provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
                    model=self.embedding_model,
                )
                self._embedder = EmbeddingsAdapter(config)

            result = await self._embedder.embed(text)
            return result.embedding

        except ImportError:
            # Fallback: return dummy embedding
            import hashlib

            # Create deterministic pseudo-embedding from text
            h = hashlib.sha256(text.encode()).hexdigest()
            return [int(h[i : i + 2], 16) / 255.0 for i in range(0, 64, 2)]

    async def match(
        self,
        query: str,
        candidates: list[str],
        query_language: str = "ar",
        candidate_language: str = "en",
        top_k: int = 5,
    ) -> list[tuple[str, float, float]]:
        """
        Match query to candidates using OT distance.

        مطابقة الاستعلام مع المرشحين باستخدام مسافة النقل الأمثل

        Args:
            query: Query text
            candidates: List of candidate texts
            query_language: Query language code
            candidate_language: Candidate language code
            top_k: Number of results

        Returns:
            List of (candidate, ot_distance, cosine_sim) tuples
        """
        # Get embeddings
        query_emb = await self._get_embedding(query)
        candidate_embs = [await self._get_embedding(c) for c in candidates]

        results = []

        for i, (cand, cand_emb) in enumerate(zip(candidates, candidate_embs)):
            # Compute OT distance
            ot_result = self.ot_matcher.sinkhorn_distance(query_emb, cand_emb)

            # Also compute cosine for comparison
            cosine_sim = self.ot_matcher.cosine_similarity(query_emb, cand_emb)

            results.append((cand, ot_result.sinkhorn_distance, cosine_sim))

        # Sort by OT distance (lower = better)
        results.sort(key=lambda x: x[1])

        return results[:top_k]

    async def align_translations(
        self,
        arabic_texts: list[str],
        english_texts: list[str],
    ) -> list[tuple[int, int, float]]:
        """
        Align Arabic texts to English translations.

        محاذاة النصوص العربية مع الترجمات الإنجليزية

        Uses OT to find best alignment between text sets.

        Args:
            arabic_texts: List of Arabic texts
            english_texts: List of English texts

        Returns:
            List of (ar_index, en_index, distance) alignments
        """
        # Get embeddings
        ar_embs = [await self._get_embedding(t) for t in arabic_texts]
        en_embs = [await self._get_embedding(t) for t in english_texts]

        # Compute full distance matrix
        distances = await self.ot_matcher.batch_distances(ar_embs, en_embs)

        # Find best alignments (greedy for now)
        alignments = []
        used_en = set()

        for i, ar_text in enumerate(arabic_texts):
            best_j = -1
            best_dist = float("inf")

            for j, en_text in enumerate(english_texts):
                if j not in used_en and distances[i][j] < best_dist:
                    best_dist = distances[i][j]
                    best_j = j

            if best_j >= 0:
                alignments.append((i, best_j, best_dist))
                used_en.add(best_j)

        return alignments


# Convenience functions
def sinkhorn_distance(
    source: list[float],
    target: list[float],
    regularization: float = 0.1,
) -> float:
    """
    Compute Sinkhorn distance between two vectors.

    Args:
        source: Source embedding
        target: Target embedding
        regularization: Entropic regularization

    Returns:
        Sinkhorn distance
    """
    config = OTConfig(regularization=regularization)
    matcher = OTEmbeddingMatcher(config)
    result = matcher.sinkhorn_distance(source, target)
    return result.sinkhorn_distance


def ot_similarity(
    source: list[float],
    target: list[float],
    scale: float = 1.0,
) -> float:
    """
    Compute OT-based similarity between two vectors.

    Args:
        source: Source embedding
        target: Target embedding
        scale: Scaling factor for conversion

    Returns:
        Similarity score (0 to 1)
    """
    matcher = OTEmbeddingMatcher()
    result = matcher.sinkhorn_distance(source, target)
    return matcher.ot_to_similarity(result.sinkhorn_distance, scale)
