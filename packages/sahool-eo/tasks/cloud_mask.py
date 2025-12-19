"""
☁️ SAHOOL Cloud Masking Tasks
مهام قناع السحب

This module provides cloud masking tasks using:
- Sentinel-2 Scene Classification Layer (SCL)
- S2cloudless machine learning model
- Custom threshold-based masking
"""

from typing import Optional, List, Tuple
import logging
import numpy as np

logger = logging.getLogger(__name__)


# =============================================================================
# Scene Classification Layer Values (Sentinel-2 L2A)
# =============================================================================

class SCLClass:
    """Sentinel-2 Scene Classification Layer classes"""
    NO_DATA = 0
    SATURATED_DEFECTIVE = 1
    DARK_AREA_PIXELS = 2
    CLOUD_SHADOWS = 3
    VEGETATION = 4
    NOT_VEGETATED = 5
    WATER = 6
    UNCLASSIFIED = 7
    CLOUD_MEDIUM_PROBABILITY = 8
    CLOUD_HIGH_PROBABILITY = 9
    THIN_CIRRUS = 10
    SNOW_ICE = 11

    # Groups for masking
    CLEAR_PIXELS = [4, 5, 6, 7]  # Valid pixels
    CLOUD_PIXELS = [3, 8, 9, 10]  # Clouds and shadows
    INVALID_PIXELS = [0, 1, 2, 11]  # Invalid data


# =============================================================================
# SAHOOL Cloud Mask Task
# =============================================================================

class SahoolCloudMaskTask:
    """
    Cloud masking using Sentinel-2 Scene Classification Layer (SCL)

    This task creates a binary cloud mask from the SCL band,
    marking cloudy and shadowy pixels as invalid.

    Example:
        task = SahoolCloudMaskTask(
            scl_feature="SCL",
            output_feature="CLOUD_MASK",
            cloud_threshold=0.4
        )
        eopatch = task.execute(eopatch)
    """

    def __init__(
        self,
        scl_feature: str = "SCL",
        clp_feature: Optional[str] = "CLP",
        output_feature: str = "CLOUD_MASK",
        valid_mask_feature: str = "VALID_DATA",
        cloud_classes: Optional[List[int]] = None,
        cloud_probability_threshold: float = 0.4,
        include_shadows: bool = True,
        include_cirrus: bool = True,
        buffer_size: int = 0,
    ):
        """
        Initialize cloud mask task

        Args:
            scl_feature: Name of SCL feature in EOPatch
            clp_feature: Name of Cloud Probability feature (optional)
            output_feature: Name for output cloud mask
            valid_mask_feature: Name for output valid data mask
            cloud_classes: SCL classes to mask (default: clouds + shadows)
            cloud_probability_threshold: CLP threshold (0-1)
            include_shadows: Include cloud shadows in mask
            include_cirrus: Include thin cirrus in mask
            buffer_size: Buffer around clouds in pixels
        """
        self.scl_feature = scl_feature
        self.clp_feature = clp_feature
        self.output_feature = output_feature
        self.valid_mask_feature = valid_mask_feature
        self.cloud_probability_threshold = cloud_probability_threshold
        self.include_shadows = include_shadows
        self.include_cirrus = include_cirrus
        self.buffer_size = buffer_size

        # Define cloud classes to mask
        if cloud_classes is None:
            self.cloud_classes = [
                SCLClass.CLOUD_MEDIUM_PROBABILITY,
                SCLClass.CLOUD_HIGH_PROBABILITY,
            ]
            if include_shadows:
                self.cloud_classes.append(SCLClass.CLOUD_SHADOWS)
            if include_cirrus:
                self.cloud_classes.append(SCLClass.THIN_CIRRUS)
        else:
            self.cloud_classes = cloud_classes

    def execute(self, eopatch):
        """
        Execute cloud masking

        Args:
            eopatch: EOPatch with SCL data

        Returns:
            EOPatch with added cloud mask
        """
        try:
            from eolearn.core import FeatureType

            # Get SCL data
            scl_data = eopatch[FeatureType.MASK].get(self.scl_feature)

            if scl_data is None:
                logger.warning(f"SCL feature '{self.scl_feature}' not found in EOPatch")
                return eopatch

            # Create cloud mask from SCL
            cloud_mask = np.zeros(scl_data.shape, dtype=np.uint8)
            for cloud_class in self.cloud_classes:
                cloud_mask |= (scl_data == cloud_class).astype(np.uint8)

            # Apply CLP if available
            if self.clp_feature:
                clp_data = eopatch[FeatureType.MASK].get(self.clp_feature)
                if clp_data is not None:
                    # CLP is typically 0-255, normalize to 0-1
                    clp_normalized = clp_data.astype(np.float32) / 255.0
                    clp_mask = (clp_normalized > self.cloud_probability_threshold).astype(np.uint8)
                    cloud_mask |= clp_mask

            # Apply buffer if specified
            if self.buffer_size > 0:
                cloud_mask = self._apply_buffer(cloud_mask)

            # Create valid data mask (inverse of cloud mask)
            valid_mask = (1 - cloud_mask).astype(np.uint8)

            # Also mask no-data and saturated pixels
            invalid_classes = [SCLClass.NO_DATA, SCLClass.SATURATED_DEFECTIVE]
            for invalid_class in invalid_classes:
                valid_mask &= (scl_data != invalid_class).astype(np.uint8)

            # Add masks to EOPatch
            eopatch[FeatureType.MASK][self.output_feature] = cloud_mask
            eopatch[FeatureType.MASK][self.valid_mask_feature] = valid_mask

            # Calculate cloud coverage percentage
            total_pixels = cloud_mask.size
            cloud_pixels = np.sum(cloud_mask)
            cloud_percentage = (cloud_pixels / total_pixels) * 100

            eopatch[FeatureType.META_INFO]["cloud_coverage"] = cloud_percentage
            logger.info(f"Cloud coverage: {cloud_percentage:.1f}%")

            return eopatch

        except ImportError as e:
            logger.error(f"Missing eolearn: {e}")
            raise

    def _apply_buffer(self, mask: np.ndarray) -> np.ndarray:
        """Apply morphological dilation to buffer cloud mask"""
        from scipy import ndimage

        struct = ndimage.generate_binary_structure(2, 1)
        buffered = ndimage.binary_dilation(
            mask,
            structure=struct,
            iterations=self.buffer_size
        )
        return buffered.astype(np.uint8)


# =============================================================================
# S2cloudless Task
# =============================================================================

class S2CloudlessTask:
    """
    Cloud masking using s2cloudless machine learning model

    s2cloudless is a machine learning model trained specifically for
    Sentinel-2 cloud detection, providing more accurate results than
    simple threshold-based methods.

    Requirements:
        pip install s2cloudless

    Example:
        task = S2CloudlessTask(
            threshold=0.4,
            average_over=4,
            dilation_size=2
        )
        eopatch = task.execute(eopatch)
    """

    def __init__(
        self,
        threshold: float = 0.4,
        average_over: int = 4,
        dilation_size: int = 2,
        all_bands: bool = True,
        output_feature: str = "S2CLOUDLESS_MASK",
        probability_feature: str = "CLOUD_PROB",
    ):
        """
        Initialize s2cloudless task

        Args:
            threshold: Cloud probability threshold (0-1)
            average_over: Average over N x N pixel windows
            dilation_size: Cloud mask dilation in pixels
            all_bands: Use all 13 Sentinel-2 bands
            output_feature: Name for output mask
            probability_feature: Name for probability map
        """
        self.threshold = threshold
        self.average_over = average_over
        self.dilation_size = dilation_size
        self.all_bands = all_bands
        self.output_feature = output_feature
        self.probability_feature = probability_feature
        self._classifier = None

    def _get_classifier(self):
        """Lazy load s2cloudless classifier"""
        if self._classifier is None:
            try:
                from s2cloudless import S2PixelCloudDetector

                self._classifier = S2PixelCloudDetector(
                    threshold=self.threshold,
                    average_over=self.average_over,
                    dilation_size=self.dilation_size,
                    all_bands=self.all_bands,
                )
            except ImportError:
                logger.error("s2cloudless not installed. Run: pip install s2cloudless")
                raise

        return self._classifier

    def execute(self, eopatch):
        """
        Execute s2cloudless cloud detection

        Args:
            eopatch: EOPatch with Sentinel-2 bands

        Returns:
            EOPatch with cloud mask and probability
        """
        try:
            from eolearn.core import FeatureType

            # Get band data
            bands = eopatch[FeatureType.DATA].get("BANDS")

            if bands is None:
                logger.warning("BANDS feature not found in EOPatch")
                return eopatch

            # Prepare bands for s2cloudless
            # s2cloudless expects: (height, width, 13 bands) or (height, width, 10 bands)
            # Current shape: (time, height, width, bands)

            classifier = self._get_classifier()

            cloud_probs = []
            cloud_masks = []

            for t in range(bands.shape[0]):
                frame = bands[t]

                # Get cloud probability
                prob = classifier.get_cloud_probability_maps(frame[np.newaxis, ...])[0]
                cloud_probs.append(prob)

                # Get cloud mask
                mask = classifier.get_cloud_masks(frame[np.newaxis, ...])[0]
                cloud_masks.append(mask)

            # Stack results
            cloud_prob = np.stack(cloud_probs, axis=0)
            cloud_mask = np.stack(cloud_masks, axis=0)

            # Add to EOPatch
            eopatch[FeatureType.MASK][self.output_feature] = cloud_mask[..., np.newaxis]
            eopatch[FeatureType.DATA][self.probability_feature] = cloud_prob[..., np.newaxis]

            logger.info("s2cloudless cloud detection completed")
            return eopatch

        except Exception as e:
            logger.error(f"s2cloudless failed: {e}")
            raise


# =============================================================================
# Composite Cloud Mask Task
# =============================================================================

class CompositeCloudMaskTask:
    """
    Combine multiple cloud masking methods for robust detection

    This task combines SCL-based and s2cloudless masks using
    voting or union strategies for more reliable cloud masking.
    """

    def __init__(
        self,
        method: str = "union",  # "union", "intersection", "voting"
        voting_threshold: int = 2,
        output_feature: str = "COMPOSITE_CLOUD_MASK",
    ):
        """
        Initialize composite cloud mask task

        Args:
            method: Combination method
            voting_threshold: Minimum votes for voting method
            output_feature: Name for output mask
        """
        self.method = method
        self.voting_threshold = voting_threshold
        self.output_feature = output_feature

    def execute(self, eopatch, mask_features: List[str]):
        """
        Combine multiple cloud masks

        Args:
            eopatch: EOPatch with cloud masks
            mask_features: List of mask feature names to combine

        Returns:
            EOPatch with composite mask
        """
        try:
            from eolearn.core import FeatureType

            masks = []
            for feature in mask_features:
                mask = eopatch[FeatureType.MASK].get(feature)
                if mask is not None:
                    masks.append(mask)

            if not masks:
                logger.warning("No cloud masks found to combine")
                return eopatch

            # Stack masks
            stacked = np.stack(masks, axis=-1)

            if self.method == "union":
                # Any mask detecting cloud
                composite = np.any(stacked, axis=-1).astype(np.uint8)
            elif self.method == "intersection":
                # All masks must detect cloud
                composite = np.all(stacked, axis=-1).astype(np.uint8)
            elif self.method == "voting":
                # Majority voting
                vote_count = np.sum(stacked, axis=-1)
                composite = (vote_count >= self.voting_threshold).astype(np.uint8)
            else:
                raise ValueError(f"Unknown method: {self.method}")

            eopatch[FeatureType.MASK][self.output_feature] = composite[..., np.newaxis]

            return eopatch

        except Exception as e:
            logger.error(f"Composite mask failed: {e}")
            raise
