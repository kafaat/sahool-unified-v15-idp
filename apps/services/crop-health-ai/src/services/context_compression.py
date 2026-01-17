"""
Context Compression Service
خدمة ضغط السياق

Compresses image + field data into optimized context representation
for efficient AI model processing.

Features:
- Image compression and encoding
- Field data normalization
- Historical pattern compression
- Spatial context encoding
"""

import base64
import hashlib
import io
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any

import numpy as np

logger = logging.getLogger("sahool-vision")


@dataclass
class CompressedFieldContext:
    """Compressed field context representation"""

    field_id: str
    crop_type: str
    severity_score: float
    disease_frequency: dict[str, int]
    avg_confidence: float
    historical_diseases: list[str]
    location_hash: str  # Spatial locality indicator
    temporal_pattern: str  # 'seasonal', 'sporadic', 'persistent'
    last_diagnosis_days_ago: int
    field_health_score: float
    compression_ratio: float
    metadata_hash: str


@dataclass
class CompressedImageContext:
    """Compressed image context"""

    image_hash: str
    image_size_bytes: int
    compressed_size_bytes: int
    compression_ratio: float
    image_features: dict[str, float]
    preprocessing_applied: list[str]


class ContextCompressionService:
    """
    Compress image and field data for efficient AI processing
    """

    def __init__(self):
        # Compression quality settings
        self.target_image_size = (224, 224)  # Neural network input size
        self.max_history_records = 50  # Keep last N diagnoses per field
        self.feature_extraction_enabled = True

    def compress_image_context(
        self,
        image_bytes: bytes,
        image_features: dict[str, float] | None = None,
    ) -> CompressedImageContext:
        """
        Compress image to optimized context representation

        Args:
            image_bytes: Raw image data
            image_features: Pre-computed image features (colors, patterns, etc)

        Returns:
            CompressedImageContext with compression metadata
        """
        try:
            from PIL import Image

            original_size = len(image_bytes)

            # Calculate image hash for deduplication
            image_hash = hashlib.sha256(image_bytes).hexdigest()[:16]

            # Extract dimensions
            image = Image.open(io.BytesIO(image_bytes))
            width, height = image.size

            # Preprocessing steps applied
            preprocessing = []

            # 1. Resize for neural network
            if (width, height) != self.target_image_size:
                image = image.resize(self.target_image_size, Image.Resampling.LANCZOS)
                preprocessing.append("resize")

            # 2. Convert to RGB if needed
            if image.mode != "RGB":
                image = image.convert("RGB")
                preprocessing.append("color_convert")

            # 3. Compress with PIL
            compressed_buffer = io.BytesIO()
            image.save(
                compressed_buffer,
                format="JPEG",
                quality=85,  # Balance quality vs compression
                optimize=True,
            )
            compressed_bytes = compressed_buffer.getvalue()
            compressed_size = len(compressed_bytes)

            # 4. Extract basic features if not provided
            if image_features is None:
                image_features = self._extract_image_features(image)
            else:
                preprocessing.append("features_provided")

            compression_ratio = (1 - compressed_size / original_size) * 100

            logger.info(
                f"🖼️  Image compression: {original_size:,}B → {compressed_size:,}B "
                f"({compression_ratio:.1f}% reduction)"
            )

            return CompressedImageContext(
                image_hash=image_hash,
                image_size_bytes=original_size,
                compressed_size_bytes=compressed_size,
                compression_ratio=compression_ratio,
                image_features=image_features,
                preprocessing_applied=preprocessing,
            )

        except Exception as e:
            logger.error(f"Image compression failed: {e}")
            # Return uncompressed context on error
            return CompressedImageContext(
                image_hash=hashlib.sha256(image_bytes).hexdigest()[:16],
                image_size_bytes=len(image_bytes),
                compressed_size_bytes=len(image_bytes),
                compression_ratio=0.0,
                image_features={},
                preprocessing_applied=["error_uncompressed"],
            )

    def compress_field_context(
        self,
        field_id: str,
        crop_type: str,
        current_severity: float,
        disease_history: list[dict[str, Any]],
        lat: float | None = None,
        lng: float | None = None,
    ) -> CompressedFieldContext:
        """
        Compress field context with historical disease patterns

        Args:
            field_id: Unique field identifier
            crop_type: Type of crop
            current_severity: Current disease severity (0-1)
            disease_history: List of past diagnoses
            lat: Latitude
            lng: Longitude

        Returns:
            CompressedFieldContext with patterns and history
        """
        try:
            # 1. Calculate location hash (spatial locality)
            location_hash = self._hash_location(lat, lng)

            # 2. Analyze disease frequency
            disease_freq = {}
            for record in disease_history[-self.max_history_records :]:
                disease = record.get("disease_id", "unknown")
                if disease != "healthy":
                    disease_freq[disease] = disease_freq.get(disease, 0) + 1

            # 3. Get unique historical diseases
            historical_diseases = list(disease_freq.keys())[-10:]  # Last 10 unique diseases

            # 4. Calculate average confidence
            confidences = [
                r.get("confidence", 0.5)
                for r in disease_history[-self.max_history_records :]
            ]
            avg_confidence = np.mean(confidences) if confidences else 0.5

            # 5. Determine temporal pattern
            temporal_pattern = self._analyze_temporal_pattern(disease_history)

            # 6. Calculate days since last diagnosis
            if disease_history:
                last_timestamp = disease_history[0].get("timestamp")
                if isinstance(last_timestamp, str):
                    last_timestamp = datetime.fromisoformat(
                        last_timestamp.replace("Z", "+00:00")
                    )
                days_ago = (datetime.utcnow() - last_timestamp).days
            else:
                days_ago = 999

            # 7. Calculate field health score (inverse of disease presence)
            healthy_diagnoses = sum(
                1
                for r in disease_history[-self.max_history_records :]
                if r.get("disease_id") == "healthy"
            )
            field_health = (
                healthy_diagnoses / len(disease_history[-self.max_history_records :])
                if disease_history
                else 1.0
            )

            # 8. Calculate context size for compression ratio
            context_dict = {
                "field_id": field_id,
                "crop_type": crop_type,
                "disease_freq": disease_freq,
                "temporal_pattern": temporal_pattern,
            }
            compressed_json = json.dumps(context_dict)
            uncompressed_size = len(json.dumps(disease_history))
            compressed_size = len(compressed_json)
            compression_ratio = (
                (1 - compressed_size / uncompressed_size) * 100
                if uncompressed_size > 0
                else 0
            )

            # 9. Create metadata hash
            metadata_str = f"{field_id}_{crop_type}_{temporal_pattern}"
            metadata_hash = hashlib.sha256(metadata_str.encode(), usedforsecurity=False).hexdigest()[:12]

            logger.info(
                f"🌾 Field context compressed: {field_id} "
                f"({len(disease_history)} diagnoses → {len(disease_freq)} patterns)"
            )

            return CompressedFieldContext(
                field_id=field_id,
                crop_type=crop_type,
                severity_score=current_severity,
                disease_frequency=disease_freq,
                avg_confidence=avg_confidence,
                historical_diseases=historical_diseases,
                location_hash=location_hash,
                temporal_pattern=temporal_pattern,
                last_diagnosis_days_ago=days_ago,
                field_health_score=field_health,
                compression_ratio=compression_ratio,
                metadata_hash=metadata_hash,
            )

        except Exception as e:
            logger.error(f"Field context compression failed: {e}")
            return CompressedFieldContext(
                field_id=field_id,
                crop_type=crop_type,
                severity_score=current_severity,
                disease_frequency={},
                avg_confidence=0.5,
                historical_diseases=[],
                location_hash="unknown",
                temporal_pattern="unknown",
                last_diagnosis_days_ago=0,
                field_health_score=0.5,
                compression_ratio=0.0,
                metadata_hash="unknown",
            )

    def create_model_prompt_context(
        self,
        image_context: CompressedImageContext,
        field_context: CompressedFieldContext,
        disease_candidates: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Create optimized prompt context for AI model

        Combines compressed image and field data for efficient inference.
        This reduces context size while preserving diagnostic value.

        Args:
            image_context: Compressed image data
            field_context: Compressed field context
            disease_candidates: List of likely diseases to focus on

        Returns:
            Dict with optimized context for model input
        """
        prompt_context = {
            "image_info": {
                "hash": image_context.image_hash,
                "original_size_kb": image_context.image_size_bytes / 1024,
                "compression_ratio": f"{image_context.compression_ratio:.1f}%",
                "features": image_context.image_features,
                "preprocessing": image_context.preprocessing_applied,
            },
            "field_context": {
                "field_id": field_context.field_id,
                "crop": field_context.crop_type,
                "health_score": f"{field_context.field_health_score:.2f}",
                "severity": f"{field_context.severity_score:.2f}",
                "avg_confidence_history": f"{field_context.avg_confidence:.2f}",
                "pattern": field_context.temporal_pattern,
                "days_since_last": field_context.last_diagnosis_days_ago,
            },
            "disease_insights": {
                "recent_diseases": field_context.historical_diseases,
                "frequency_distribution": field_context.disease_frequency,
                "candidates": disease_candidates or [],
            },
            "compression_metadata": {
                "total_compression": f"{field_context.compression_ratio:.1f}%",
                "context_hash": field_context.metadata_hash,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }

        return prompt_context

    def _extract_image_features(self, image) -> dict[str, float]:
        """Extract basic image features for context"""
        try:
            img_array = np.array(image, dtype=np.float32) / 255.0

            # Calculate color statistics
            features = {
                "mean_brightness": float(np.mean(img_array)),
                "std_brightness": float(np.std(img_array)),
                "red_dominance": float(np.mean(img_array[:, :, 0])),
                "green_dominance": float(np.mean(img_array[:, :, 1])),
                "blue_dominance": float(np.mean(img_array[:, :, 2])),
                "color_variance": float(np.var(img_array)),
            }

            return features
        except Exception as e:
            logger.warning(f"Feature extraction failed: {e}")
            return {}

    def _hash_location(self, lat: float | None, lng: float | None) -> str:
        """Create hash of location for spatial locality"""
        if lat is None or lng is None:
            return "unknown"

        # Round to 2 decimal places (≈1km precision)
        location_str = f"{lat:.2f}_{lng:.2f}"
        return hashlib.sha256(location_str.encode(), usedforsecurity=False).hexdigest()[:8]

    def _analyze_temporal_pattern(self, disease_history: list[dict]) -> str:
        """
        Analyze temporal disease pattern

        Returns: 'seasonal', 'sporadic', 'persistent', 'improving', 'unknown'
        """
        if len(disease_history) < 3:
            return "unknown"

        try:
            # Count disease occurrence in recent history
            recent = disease_history[:20]  # Last 20 diagnoses
            disease_count = sum(
                1 for r in recent if r.get("disease_id") != "healthy"
            )

            # Analyze dates if available
            timestamps = []
            for record in recent:
                ts = record.get("timestamp")
                if ts:
                    if isinstance(ts, str):
                        ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    timestamps.append(ts)

            # Pattern classification
            disease_ratio = disease_count / len(recent)

            if disease_ratio > 0.7:
                return "persistent"  # Most recent diagnoses are diseased
            elif disease_ratio > 0.4:
                return "seasonal"  # Intermittent disease presence
            elif disease_ratio > 0.1:
                return "sporadic"  # Occasional disease detection
            else:
                return "improving"  # Mostly healthy

        except Exception as e:
            logger.warning(f"Temporal pattern analysis failed: {e}")
            return "unknown"

    def get_compression_stats(
        self,
        image_context: CompressedImageContext,
        field_context: CompressedFieldContext,
    ) -> dict[str, Any]:
        """Get compression statistics for monitoring"""
        return {
            "image_compression_ratio": f"{image_context.compression_ratio:.1f}%",
            "field_context_compression": f"{field_context.compression_ratio:.1f}%",
            "combined_reduction": f"{(image_context.compression_ratio + field_context.compression_ratio) / 2:.1f}%",
            "image_size_kb": image_context.compressed_size_bytes / 1024,
            "field_records_retained": f"1-{min(len(field_context.historical_diseases) * 3, self.max_history_records)}",
            "timestamp": datetime.utcnow().isoformat(),
        }


# Singleton instance
context_compression_service = ContextCompressionService()
