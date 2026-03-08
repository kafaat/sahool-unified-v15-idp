"""
Change Detection Module - كشف التغيرات
Based on: Qin et al. (2026) - Frame difference analysis for change-triggered processing

This module detects significant changes between consecutive frames to trigger
expensive MLLM analysis only when meaningful changes occur.
"""

import logging
from enum import Enum, StrEnum
from typing import Optional

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ChangeType(StrEnum):
    """Types of detected changes"""

    NO_CHANGE = "no_change"
    MINOR_CHANGE = "minor_change"
    MODERATE_CHANGE = "moderate_change"
    SIGNIFICANT_CHANGE = "significant_change"
    MAJOR_CHANGE = "major_change"


class ChangeDetectionResult(BaseModel):
    """Result of change detection analysis"""

    change_score: float = Field(..., ge=0.0, le=1.0)
    change_type: ChangeType
    threshold_used: float

    # Regional analysis
    change_regions: list[dict] = Field(default_factory=list, description="Regions with significant change")
    max_region_change: float = Field(default=0.0, ge=0.0, le=1.0, description="Maximum change score in any region")

    # Analysis metadata
    method_used: str = Field(default="structural_similarity")
    processing_time_ms: int | None = None

    # Trigger recommendation
    should_trigger_analysis: bool = Field(default=False, description="Whether to trigger expensive MLLM analysis")


class ChangeDetector:
    """
    Detect significant changes between consecutive frames.
    Uses multiple methods to detect both gradual and sudden changes.

    Based on: Qin et al. (2026) - Change-triggered MLLM invocation
    """

    # Default thresholds for change classification
    MINOR_THRESHOLD = 0.05
    MODERATE_THRESHOLD = 0.10
    SIGNIFICANT_THRESHOLD = 0.15
    MAJOR_THRESHOLD = 0.25

    def __init__(
        self,
        trigger_threshold: float = 0.15,
        use_ssim: bool = True,
        use_histogram: bool = True,
        region_size: int = 64,
    ):
        """
        Initialize change detector.

        Args:
            trigger_threshold: Threshold for triggering MLLM analysis
            use_ssim: Use Structural Similarity Index
            use_histogram: Use histogram comparison
            region_size: Size of regions for localized analysis
        """
        self.trigger_threshold = trigger_threshold
        self.use_ssim = use_ssim
        self.use_histogram = use_histogram
        self.region_size = region_size

        logger.info(f"ChangeDetector initialized with threshold={trigger_threshold}")

    async def compute_change(
        self, frame1: np.ndarray, frame2: np.ndarray, mask: np.ndarray | None = None
    ) -> ChangeDetectionResult:
        """
        Compute change score between two frames.

        Args:
            frame1: First frame (earlier)
            frame2: Second frame (later)
            mask: Optional mask for region of interest

        Returns:
            ChangeDetectionResult with score and analysis
        """
        import time

        start_time = time.time()

        # Ensure frames are same size
        if frame1.shape != frame2.shape:
            logger.warning(f"Frame shape mismatch: {frame1.shape} vs {frame2.shape}")
            # Resize frame2 to match frame1
            frame2 = self._resize_to_match(frame2, frame1.shape)

        # Convert to grayscale if color
        gray1 = self._to_grayscale(frame1)
        gray2 = self._to_grayscale(frame2)

        # Apply mask if provided
        if mask is not None:
            gray1 = gray1 * mask
            gray2 = gray2 * mask

        scores = []

        # Method 1: Mean Absolute Difference (fast)
        mad_score = self._compute_mad(gray1, gray2)
        scores.append(mad_score)

        # Method 2: Structural Similarity (more robust)
        if self.use_ssim:
            ssim_score = self._compute_ssim_change(gray1, gray2)
            scores.append(ssim_score)

        # Method 3: Histogram comparison
        if self.use_histogram:
            hist_score = self._compute_histogram_change(gray1, gray2)
            scores.append(hist_score)

        # Combine scores (weighted average)
        weights = [0.3]  # MAD weight
        if self.use_ssim:
            weights.append(0.5)  # SSIM weight
        if self.use_histogram:
            weights.append(0.2)  # Histogram weight

        # Normalize weights
        weights = np.array(weights) / sum(weights)
        combined_score = float(np.dot(scores, weights))

        # Regional analysis
        change_regions = self._analyze_regions(gray1, gray2)
        max_region_change = max([r["change_score"] for r in change_regions], default=0.0)

        # Classify change type
        change_type = self._classify_change(combined_score)

        # Determine if should trigger analysis
        should_trigger = combined_score >= self.trigger_threshold or max_region_change >= self.trigger_threshold * 1.5

        processing_time = int((time.time() - start_time) * 1000)

        return ChangeDetectionResult(
            change_score=combined_score,
            change_type=change_type,
            threshold_used=self.trigger_threshold,
            change_regions=change_regions,
            max_region_change=max_region_change,
            method_used="multi_method_fusion",
            processing_time_ms=processing_time,
            should_trigger_analysis=should_trigger,
        )

    def _to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale if needed."""
        if len(image.shape) == 3:
            # RGB to grayscale
            return np.dot(image[..., :3], [0.299, 0.587, 0.114])
        return image.astype(float)

    def _resize_to_match(self, image: np.ndarray, target_shape: tuple) -> np.ndarray:
        """Resize image to match target shape using simple interpolation."""
        # Simple nearest-neighbor resize for now
        # In production, use cv2.resize
        target_h, target_w = target_shape[:2]
        src_h, src_w = image.shape[:2]

        y_ratio = src_h / target_h
        x_ratio = src_w / target_w

        if len(image.shape) == 3:
            result = np.zeros((target_h, target_w, image.shape[2]), dtype=image.dtype)
        else:
            result = np.zeros((target_h, target_w), dtype=image.dtype)

        for y in range(target_h):
            for x in range(target_w):
                src_y = int(y * y_ratio)
                src_x = int(x * x_ratio)
                result[y, x] = image[src_y, src_x]

        return result

    def _compute_mad(self, gray1: np.ndarray, gray2: np.ndarray) -> float:
        """Compute Mean Absolute Difference."""
        # Normalize to [0, 1]
        max_val = max(gray1.max(), gray2.max(), 1)
        g1 = gray1 / max_val
        g2 = gray2 / max_val

        mad = np.mean(np.abs(g1 - g2))
        return float(min(mad * 2, 1.0))  # Scale for better sensitivity

    def _compute_ssim_change(self, gray1: np.ndarray, gray2: np.ndarray) -> float:
        """
        Compute change based on Structural Similarity Index.
        Returns 1 - SSIM (so higher = more change).
        """
        # Simplified SSIM implementation
        # Constants for stability
        C1 = (0.01 * 255) ** 2
        C2 = (0.03 * 255) ** 2

        # Local statistics using sliding window
        window_size = 11

        # Compute means
        mu1 = self._uniform_filter(gray1, window_size)
        mu2 = self._uniform_filter(gray2, window_size)

        # Compute variances and covariance
        sigma1_sq = self._uniform_filter(gray1**2, window_size) - mu1**2
        sigma2_sq = self._uniform_filter(gray2**2, window_size) - mu2**2
        sigma12 = self._uniform_filter(gray1 * gray2, window_size) - mu1 * mu2

        # SSIM formula
        numerator = (2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)
        denominator = (mu1**2 + mu2**2 + C1) * (sigma1_sq + sigma2_sq + C2)

        ssim_map = numerator / (denominator + 1e-10)
        mean_ssim = float(np.mean(ssim_map))

        # Return change score (1 - SSIM)
        return float(max(0, min(1, 1 - mean_ssim)))

    def _uniform_filter(self, image: np.ndarray, size: int) -> np.ndarray:
        """Apply uniform filter (box blur) for SSIM computation."""
        # Simple box filter implementation
        kernel_size = size
        pad = kernel_size // 2

        # Pad image
        padded = np.pad(image, pad, mode="reflect")

        # Cumulative sum for fast box filter
        cumsum = np.cumsum(np.cumsum(padded, axis=0), axis=1)

        # Compute box filter result
        result = np.zeros_like(image)
        for y in range(image.shape[0]):
            for x in range(image.shape[1]):
                y1, y2 = y, y + kernel_size
                x1, x2 = x, x + kernel_size

                total = cumsum[y2, x2] - cumsum[y1, x2] - cumsum[y2, x1] + cumsum[y1, x1]
                result[y, x] = total / (kernel_size * kernel_size)

        return result

    def _compute_histogram_change(self, gray1: np.ndarray, gray2: np.ndarray) -> float:
        """Compute change based on histogram comparison."""
        # Compute histograms
        bins = 64
        range_min = min(gray1.min(), gray2.min())
        range_max = max(gray1.max(), gray2.max())

        hist1, _ = np.histogram(gray1.ravel(), bins=bins, range=(range_min, range_max))
        hist2, _ = np.histogram(gray2.ravel(), bins=bins, range=(range_min, range_max))

        # Normalize histograms
        hist1 = hist1.astype(float) / (hist1.sum() + 1e-10)
        hist2 = hist2.astype(float) / (hist2.sum() + 1e-10)

        # Chi-square distance
        chi_sq = np.sum((hist1 - hist2) ** 2 / (hist1 + hist2 + 1e-10))

        # Normalize to [0, 1]
        return float(min(chi_sq / 2, 1.0))

    def _analyze_regions(self, gray1: np.ndarray, gray2: np.ndarray) -> list[dict]:
        """Analyze changes in image regions."""
        regions = []
        h, w = gray1.shape

        for y in range(0, h, self.region_size):
            for x in range(0, w, self.region_size):
                y_end = min(y + self.region_size, h)
                x_end = min(x + self.region_size, w)

                region1 = gray1[y:y_end, x:x_end]
                region2 = gray2[y:y_end, x:x_end]

                # Compute MAD for region
                max_val = max(region1.max(), region2.max(), 1)
                r1 = region1 / max_val
                r2 = region2 / max_val
                change_score = float(np.mean(np.abs(r1 - r2)) * 2)

                if change_score > self.MINOR_THRESHOLD:
                    regions.append(
                        {
                            "x": x,
                            "y": y,
                            "width": x_end - x,
                            "height": y_end - y,
                            "change_score": min(change_score, 1.0),
                        }
                    )

        return regions

    def _classify_change(self, score: float) -> ChangeType:
        """Classify change score into categories."""
        if score < self.MINOR_THRESHOLD:
            return ChangeType.NO_CHANGE
        elif score < self.MODERATE_THRESHOLD:
            return ChangeType.MINOR_CHANGE
        elif score < self.SIGNIFICANT_THRESHOLD:
            return ChangeType.MODERATE_CHANGE
        elif score < self.MAJOR_THRESHOLD:
            return ChangeType.SIGNIFICANT_CHANGE
        else:
            return ChangeType.MAJOR_CHANGE


class TemporalChangeTracker:
    """
    Track changes over time to detect gradual transitions
    that might not trigger individual frame comparisons.
    """

    def __init__(self, window_size: int = 10):
        """
        Initialize temporal tracker.

        Args:
            window_size: Number of frames to track
        """
        self.window_size = window_size
        self.change_history: list[ChangeDetectionResult] = []
        self.cumulative_change: float = 0.0

    def add_result(self, result: ChangeDetectionResult) -> dict:
        """
        Add a new change detection result and analyze trends.

        Args:
            result: Change detection result to add

        Returns:
            Analysis of temporal trends
        """
        self.change_history.append(result)
        self.cumulative_change += result.change_score

        # Keep only recent history
        if len(self.change_history) > self.window_size:
            removed = self.change_history.pop(0)
            self.cumulative_change -= removed.change_score

        return self._analyze_trends()

    def _analyze_trends(self) -> dict:
        """Analyze change trends over the window."""
        if len(self.change_history) < 2:
            return {
                "trend": "insufficient_data",
                "average_change": 0.0,
                "acceleration": 0.0,
            }

        scores = [r.change_score for r in self.change_history]
        avg_change = float(np.mean(scores))

        # Calculate trend (increasing/decreasing)
        if len(scores) >= 3:
            first_half = np.mean(scores[: len(scores) // 2])
            second_half = np.mean(scores[len(scores) // 2 :])
            acceleration = float(second_half - first_half)
        else:
            acceleration = 0.0

        if acceleration > 0.05:
            trend = "accelerating"
        elif acceleration < -0.05:
            trend = "decelerating"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "average_change": avg_change,
            "acceleration": acceleration,
            "cumulative_change": self.cumulative_change,
            "window_count": len(self.change_history),
        }

    def should_trigger_gradual(self, threshold: float = 0.5) -> bool:
        """
        Check if gradual changes warrant MLLM analysis.

        Args:
            threshold: Cumulative change threshold

        Returns:
            True if gradual changes are significant
        """
        return self.cumulative_change >= threshold
