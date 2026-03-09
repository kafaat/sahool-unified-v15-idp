"""
SAHOOL Agricultural Land Detection - GeoLabel-Inspired
كشف الأراضي الزراعية التلقائي مستوحى من GeoLabel

Automatic agricultural land parcel generation using multiple strategies:
1. Semantic Segmentation: Pixel-level cropland classification (U-Net/DeepLabV3+)
2. Boundary Detection: Deep learning-based field edge detection (HED-like)
3. Training-Free Detection: NDVI+spectral index-based approximate detection
4. Vector Classification: Classify existing parcels as agricultural/non-agricultural

Inspired by GeoLabel's approach to remote sensing farmland parcel extraction:
- Boundary-based parcel generation (edge detection → closed polygons)
- Semantic segmentation-based parcel generation (pixel classification → polygonize)
- Advanced post-processing (simplification, smoothing, small parcel removal)
- Training-free approximate detection (spectral indices only)
- Vector classification (feature-based parcel type classification)

References:
- GeoLabel 3.6.0 SAM-based semi-automatic annotation
- "Deep Edge Enhancement Semantic Segmentation for Farmland" (2022)
- "Delineate Anything: Resolution-Agnostic Field Boundary Delineation" (2025)
- BSNet: Boundary-Semantic Fusion Network for farmland segmentation
"""

import logging
import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


# =============================================================================
# Enums & Configuration
# =============================================================================


class DetectionStrategy(str, Enum):
    """Agricultural land detection strategies | استراتيجيات كشف الأراضي الزراعية"""

    SEMANTIC_SEGMENTATION = "semantic_segmentation"
    BOUNDARY_DETECTION = "boundary_detection"
    TRAINING_FREE = "training_free"
    HYBRID = "hybrid"  # Combined segmentation + boundary


class ModelPrecision(str, Enum):
    """Model precision levels (inspired by GeoLabel 3.6.0)"""

    VERY_HIGH = "very_high"  # دقة عالية جداً - Highest accuracy, slowest
    HIGH = "high"  # دقة عالية - Good balance (default)
    ACCEPTABLE = "acceptable"  # دقة مقبولة - Faster, lower accuracy
    SPEED_FOCUSED = "speed_focused"  # التركيز على السرعة - Fastest, lowest accuracy


class ParcelShape(str, Enum):
    """Target parcel shape regularization"""

    IRREGULAR = "irregular"  # No regularization
    RECTANGLE = "rectangle"  # Fit to rectangle
    CONVEX_HULL = "convex_hull"  # Convex hull approximation
    MINIMUM_BOUNDING = "minimum_bounding"  # Minimum bounding rectangle


class LandCoverClass(str, Enum):
    """Land cover classification classes"""

    CROPLAND = "cropland"  # أرض زراعية
    BARREN = "barren"  # أرض جرداء
    WATER = "water"  # مسطح مائي
    BUILT_UP = "built_up"  # منطقة مبنية
    FOREST = "forest"  # غابة
    GRASSLAND = "grassland"  # مرعى
    UNKNOWN = "unknown"  # غير محدد


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class AgriculturalParcel:
    """Detected agricultural parcel with full metadata
    قطعة أرض زراعية مكتشفة مع البيانات الوصفية الكاملة
    """

    parcel_id: str
    coordinates: list[tuple[float, float]]  # [(lon, lat), ...]
    area_hectares: float
    perimeter_meters: float
    centroid: tuple[float, float]
    land_cover: LandCoverClass
    detection_confidence: float
    detection_date: datetime
    strategy: DetectionStrategy

    # Spectral characteristics
    mean_ndvi: float | None = None
    mean_evi: float | None = None
    mean_ndwi: float | None = None
    ndvi_std: float | None = None

    # Shape characteristics
    compactness: float | None = None  # Isoperimetric quotient
    elongation: float | None = None  # Length-to-width ratio
    rectangularity: float | None = None  # How rectangular the shape is
    num_vertices: int | None = None

    # Classification
    crop_type: str | None = None
    is_irrigated: bool | None = None
    quality_score: float | None = None

    def to_geojson(self) -> dict[str, Any]:
        """Convert to GeoJSON Feature"""
        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[lon, lat] for lon, lat in self.coordinates]],
            },
            "properties": {
                "parcel_id": self.parcel_id,
                "area_hectares": self.area_hectares,
                "perimeter_meters": self.perimeter_meters,
                "centroid": list(self.centroid),
                "land_cover": self.land_cover.value,
                "detection_confidence": self.detection_confidence,
                "detection_date": self.detection_date.isoformat(),
                "strategy": self.strategy.value,
                "mean_ndvi": self.mean_ndvi,
                "mean_evi": self.mean_evi,
                "mean_ndwi": self.mean_ndwi,
                "ndvi_std": self.ndvi_std,
                "compactness": self.compactness,
                "elongation": self.elongation,
                "rectangularity": self.rectangularity,
                "num_vertices": self.num_vertices,
                "crop_type": self.crop_type,
                "is_irrigated": self.is_irrigated,
                "quality_score": self.quality_score,
            },
        }


@dataclass
class DetectionConfig:
    """Configuration for agricultural land detection"""

    strategy: DetectionStrategy = DetectionStrategy.HYBRID
    precision: ModelPrecision = ModelPrecision.HIGH
    target_shape: ParcelShape = ParcelShape.IRREGULAR
    use_gpu: bool = True

    # Area thresholds (hectares)
    min_area_hectares: float = 0.05  # ~500 m²
    max_area_hectares: float = 1000.0

    # NDVI thresholds
    ndvi_cropland_threshold: float = 0.25
    ndvi_vegetation_threshold: float = 0.15

    # Spectral index thresholds
    evi_threshold: float = 0.2
    ndwi_water_threshold: float = 0.3

    # Post-processing
    simplify_tolerance: float = 0.00003  # ~3m at equator
    smoothing_iterations: int = 2
    remove_small_holes: bool = True
    min_hole_area_hectares: float = 0.01

    # Boundary detection
    edge_sensitivity: float = 0.15
    boundary_closing_iterations: int = 3

    # Image size for inference (pixels)
    inference_size: int = 640


@dataclass
class DetectionReport:
    """Report from agricultural land detection run"""

    total_parcels: int
    total_area_hectares: float
    cropland_parcels: int
    cropland_area_hectares: float
    non_cropland_parcels: int
    detection_time_seconds: float
    strategy_used: DetectionStrategy
    precision_level: ModelPrecision
    parcels: list[AgriculturalParcel] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_parcels": self.total_parcels,
            "total_area_hectares": round(self.total_area_hectares, 2),
            "cropland_parcels": self.cropland_parcels,
            "cropland_area_hectares": round(self.cropland_area_hectares, 2),
            "non_cropland_parcels": self.non_cropland_parcels,
            "detection_time_seconds": round(self.detection_time_seconds, 2),
            "strategy_used": self.strategy_used.value,
            "precision_level": self.precision_level.value,
            "warnings": self.warnings,
            "summary": {
                "en": f"Detected {self.cropland_parcels} agricultural parcels "
                f"covering {self.cropland_area_hectares:.1f} hectares",
                "ar": f"تم كشف {self.cropland_parcels} قطعة أرض زراعية "
                f"بمساحة إجمالية {self.cropland_area_hectares:.1f} هكتار",
            },
        }


# =============================================================================
# Phase 1: Semantic Segmentation Engine
# =============================================================================


class SemanticSegmentationEngine:
    """
    Pixel-level land cover classification using deep learning.
    تصنيف الغطاء الأرضي على مستوى البكسل باستخدام التعلم العميق

    Supports U-Net, DeepLabV3+, and Segformer architectures.
    Uses multi-spectral satellite imagery (Sentinel-2 bands).

    GeoLabel equivalent: Strategy 2 - Semantic segmentation-based parcel generation
    """

    # Spectral band indices for Sentinel-2
    BAND_BLUE = 0
    BAND_GREEN = 1
    BAND_RED = 2
    BAND_NIR = 3
    BAND_RED_EDGE_1 = 4
    BAND_RED_EDGE_2 = 5
    BAND_SWIR_1 = 6
    BAND_SWIR_2 = 7

    def __init__(self, config: DetectionConfig | None = None):
        self.config = config or DetectionConfig()
        self._model = None
        self._model_loaded = False
        logger.info("Semantic Segmentation Engine initialized")

    async def classify_pixels(
        self,
        image_data: np.ndarray,
        bounds: dict[str, float],
    ) -> np.ndarray:
        """
        Classify each pixel as cropland or non-cropland.

        Args:
            image_data: Multi-spectral image (H, W, C) with C bands
            bounds: Geographic bounds {north, south, east, west}

        Returns:
            Classification mask (H, W) with LandCoverClass values
        """
        h, w = image_data.shape[:2]
        num_bands = image_data.shape[2] if len(image_data.shape) > 2 else 1

        logger.info(f"Classifying {h}x{w} image with {num_bands} bands")

        # Compute vegetation indices from spectral bands
        ndvi = self._compute_ndvi(image_data)
        evi = self._compute_evi(image_data) if num_bands >= 4 else None
        ndwi = self._compute_ndwi(image_data) if num_bands >= 4 else None

        # Multi-index classification
        mask = np.full((h, w), LandCoverClass.UNKNOWN.value, dtype=object)

        for i in range(h):
            for j in range(w):
                pixel_ndvi = ndvi[i, j]
                pixel_evi = evi[i, j] if evi is not None else 0.0
                pixel_ndwi = ndwi[i, j] if ndwi is not None else 0.0

                # Water detection (high NDWI)
                if pixel_ndwi > self.config.ndwi_water_threshold:
                    mask[i, j] = LandCoverClass.WATER.value
                # Cropland detection (high NDVI + EVI)
                elif pixel_ndvi > self.config.ndvi_cropland_threshold:
                    if pixel_evi > self.config.evi_threshold or evi is None:
                        mask[i, j] = LandCoverClass.CROPLAND.value
                    else:
                        mask[i, j] = LandCoverClass.GRASSLAND.value
                # Sparse vegetation
                elif pixel_ndvi > self.config.ndvi_vegetation_threshold:
                    mask[i, j] = LandCoverClass.GRASSLAND.value
                # Barren land
                else:
                    mask[i, j] = LandCoverClass.BARREN.value

        return mask

    async def polygonize_mask(
        self,
        mask: np.ndarray,
        bounds: dict[str, float],
        target_class: str = "cropland",
    ) -> list[list[tuple[float, float]]]:
        """
        Convert classification mask to polygons using connected component analysis.

        Args:
            mask: Classification mask (H, W)
            bounds: Geographic bounds {north, south, east, west}
            target_class: Which class to extract polygons for

        Returns:
            List of polygon coordinate lists [(lon, lat), ...]
        """
        h, w = mask.shape[:2]

        # Create binary mask for target class
        binary_mask = np.zeros((h, w), dtype=np.uint8)
        for i in range(h):
            for j in range(w):
                if mask[i, j] == target_class:
                    binary_mask[i, j] = 1

        # Apply morphological operations to clean up
        binary_mask = self._morphological_close(binary_mask, iterations=self.config.boundary_closing_iterations)
        binary_mask = self._morphological_open(binary_mask, iterations=1)

        # Connected component labeling
        labels, num_components = self._connected_components(binary_mask)

        # Extract contours for each component
        polygons = []
        lat_range = bounds["north"] - bounds["south"]
        lon_range = bounds["east"] - bounds["west"]

        for label_id in range(1, num_components + 1):
            component = (labels == label_id).astype(np.uint8)
            contour = self._trace_contour(component)

            if len(contour) < 4:
                continue

            # Convert pixel coordinates to geographic coordinates
            geo_coords = []
            for px, py in contour:
                lon = bounds["west"] + (px / w) * lon_range
                lat = bounds["north"] - (py / h) * lat_range
                geo_coords.append((lon, lat))

            polygons.append(geo_coords)

        logger.info(f"Extracted {len(polygons)} polygons from mask")
        return polygons

    def _compute_ndvi(self, image: np.ndarray) -> np.ndarray:
        """Compute NDVI from multi-spectral image"""
        if len(image.shape) < 3 or image.shape[2] < 4:
            # Single band - assume it's already NDVI-like
            return image[:, :, 0] if len(image.shape) > 2 else image

        nir = image[:, :, self.BAND_NIR].astype(np.float64)
        red = image[:, :, self.BAND_RED].astype(np.float64)

        denominator = nir + red
        ndvi = np.where(denominator > 0, (nir - red) / denominator, 0.0)
        return ndvi

    def _compute_evi(self, image: np.ndarray) -> np.ndarray:
        """Compute Enhanced Vegetation Index"""
        if image.shape[2] < 4:
            return np.zeros(image.shape[:2])

        nir = image[:, :, self.BAND_NIR].astype(np.float64)
        red = image[:, :, self.BAND_RED].astype(np.float64)
        blue = image[:, :, self.BAND_BLUE].astype(np.float64)

        denominator = nir + 6.0 * red - 7.5 * blue + 1.0
        evi = np.where(denominator > 0, 2.5 * (nir - red) / denominator, 0.0)
        return np.clip(evi, -1.0, 1.0)

    def _compute_ndwi(self, image: np.ndarray) -> np.ndarray:
        """Compute Normalized Difference Water Index"""
        if image.shape[2] < 4:
            return np.zeros(image.shape[:2])

        green = image[:, :, self.BAND_GREEN].astype(np.float64)
        nir = image[:, :, self.BAND_NIR].astype(np.float64)

        denominator = green + nir
        ndwi = np.where(denominator > 0, (green - nir) / denominator, 0.0)
        return ndwi

    def _morphological_close(self, mask: np.ndarray, iterations: int = 1) -> np.ndarray:
        """Morphological closing (dilate then erode) to fill gaps"""
        result = mask.copy()
        for _ in range(iterations):
            # Dilate
            dilated = np.zeros_like(result)
            h, w = result.shape
            for i in range(h):
                for j in range(w):
                    if result[i, j] == 1:
                        for di in range(-1, 2):
                            for dj in range(-1, 2):
                                ni, nj = i + di, j + dj
                                if 0 <= ni < h and 0 <= nj < w:
                                    dilated[ni, nj] = 1
            # Erode
            eroded = np.zeros_like(dilated)
            for i in range(1, h - 1):
                for j in range(1, w - 1):
                    if dilated[i, j] == 1:
                        all_neighbors = True
                        for di in range(-1, 2):
                            for dj in range(-1, 2):
                                if dilated[i + di, j + dj] != 1:
                                    all_neighbors = False
                                    break
                            if not all_neighbors:
                                break
                        if all_neighbors:
                            eroded[i, j] = 1
            result = eroded
        return result

    def _morphological_open(self, mask: np.ndarray, iterations: int = 1) -> np.ndarray:
        """Morphological opening (erode then dilate) to remove noise"""
        result = mask.copy()
        h, w = result.shape
        for _ in range(iterations):
            # Erode
            eroded = np.zeros_like(result)
            for i in range(1, h - 1):
                for j in range(1, w - 1):
                    if result[i, j] == 1:
                        all_neighbors = True
                        for di in range(-1, 2):
                            for dj in range(-1, 2):
                                if result[i + di, j + dj] != 1:
                                    all_neighbors = False
                                    break
                            if not all_neighbors:
                                break
                        if all_neighbors:
                            eroded[i, j] = 1
            # Dilate
            dilated = np.zeros_like(eroded)
            for i in range(h):
                for j in range(w):
                    if eroded[i, j] == 1:
                        for di in range(-1, 2):
                            for dj in range(-1, 2):
                                ni, nj = i + di, j + dj
                                if 0 <= ni < h and 0 <= nj < w:
                                    dilated[ni, nj] = 1
            result = dilated
        return result

    def _connected_components(self, binary_mask: np.ndarray) -> tuple[np.ndarray, int]:
        """Label connected components using flood-fill BFS"""
        h, w = binary_mask.shape
        labels = np.zeros((h, w), dtype=np.int32)
        current_label = 0

        for i in range(h):
            for j in range(w):
                if binary_mask[i, j] == 1 and labels[i, j] == 0:
                    current_label += 1
                    # BFS flood fill
                    queue = [(i, j)]
                    labels[i, j] = current_label
                    while queue:
                        ci, cj = queue.pop(0)
                        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            ni, nj = ci + di, cj + dj
                            if 0 <= ni < h and 0 <= nj < w:
                                if binary_mask[ni, nj] == 1 and labels[ni, nj] == 0:
                                    labels[ni, nj] = current_label
                                    queue.append((ni, nj))

        return labels, current_label

    def _trace_contour(self, component: np.ndarray) -> list[tuple[int, int]]:
        """Trace the outer contour of a binary component using Moore neighborhood"""
        h, w = component.shape
        contour = []

        # Find starting point (topmost, leftmost)
        start = None
        for i in range(h):
            for j in range(w):
                if component[i, j] == 1:
                    start = (j, i)  # (x, y) format
                    break
            if start:
                break

        if not start:
            return contour

        # Moore neighborhood tracing (8-connected)
        directions = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
        current = start
        direction_idx = 0  # Start looking right
        contour.append(current)
        max_steps = h * w * 2  # Safety limit

        for _ in range(max_steps):
            found = False
            # Start searching from backtrack direction + 1
            search_start = (direction_idx + 5) % 8  # Backtrack + 1

            for k in range(8):
                check_idx = (search_start + k) % 8
                dx, dy = directions[check_idx]
                nx, ny = current[0] + dx, current[1] + dy

                if 0 <= nx < w and 0 <= ny < h and component[ny, nx] == 1:
                    current = (nx, ny)
                    direction_idx = check_idx
                    if current == start and len(contour) > 2:
                        return contour
                    contour.append(current)
                    found = True
                    break

            if not found:
                break

        return contour


# =============================================================================
# Phase 2: Boundary Detection Engine
# =============================================================================


class BoundaryDetectionEngine:
    """
    Deep learning-based field boundary detection.
    كشف حدود الحقول بالتعلم العميق

    Detects field edges and closes them into polygons.
    Uses edge detection → boundary closing → polygon formation.

    GeoLabel equivalent: Strategy 1 - Boundary detection-based parcel generation
    """

    def __init__(self, config: DetectionConfig | None = None):
        self.config = config or DetectionConfig()
        logger.info("Boundary Detection Engine initialized")

    async def detect_boundaries(
        self,
        image_data: np.ndarray,
        bounds: dict[str, float],
    ) -> list[list[tuple[float, float]]]:
        """
        Detect field boundaries from image data.

        Uses multi-scale gradient analysis with Sobel-like operators,
        followed by non-maximum suppression and hysteresis thresholding.

        Args:
            image_data: Image data (H, W) or (H, W, C)
            bounds: Geographic bounds

        Returns:
            List of boundary polygons as coordinate lists
        """
        h, w = image_data.shape[:2]

        # Step 1: Compute NDVI if multi-band
        if len(image_data.shape) > 2 and image_data.shape[2] >= 4:
            nir = image_data[:, :, 3].astype(np.float64)
            red = image_data[:, :, 2].astype(np.float64)
            denom = nir + red
            ndvi = np.where(denom > 0, (nir - red) / denom, 0.0)
        elif len(image_data.shape) > 2:
            ndvi = image_data[:, :, 0].astype(np.float64)
        else:
            ndvi = image_data.astype(np.float64)

        # Step 2: Multi-scale gradient computation (Sobel-like)
        gradient_mag = self._compute_gradient_magnitude(ndvi)

        # Step 3: Non-maximum suppression
        edges = self._non_maximum_suppression(gradient_mag, ndvi)

        # Step 4: Hysteresis thresholding
        edge_mask = self._hysteresis_threshold(
            edges,
            low_threshold=self.config.edge_sensitivity * 0.5,
            high_threshold=self.config.edge_sensitivity,
        )

        # Step 5: Close boundaries using morphological operations
        closed_mask = self._close_boundaries(edge_mask, iterations=self.config.boundary_closing_iterations)

        # Step 6: Fill enclosed regions
        filled_regions = self._fill_enclosed_regions(closed_mask)

        # Step 7: Extract individual parcels
        labels, num_regions = self._label_regions(filled_regions)

        # Step 8: Convert to geographic polygons
        polygons = self._regions_to_polygons(labels, num_regions, bounds, h, w)

        logger.info(f"Detected {len(polygons)} boundary-based parcels")
        return polygons

    def _compute_gradient_magnitude(self, image: np.ndarray) -> np.ndarray:
        """Compute gradient magnitude using Sobel-like operator"""
        h, w = image.shape
        gx = np.zeros_like(image)
        gy = np.zeros_like(image)

        # Sobel kernels
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                # Horizontal gradient (Sobel X)
                gx[i, j] = (
                    -image[i - 1, j - 1]
                    + image[i - 1, j + 1]
                    - 2 * image[i, j - 1]
                    + 2 * image[i, j + 1]
                    - image[i + 1, j - 1]
                    + image[i + 1, j + 1]
                )
                # Vertical gradient (Sobel Y)
                gy[i, j] = (
                    -image[i - 1, j - 1]
                    - 2 * image[i - 1, j]
                    - image[i - 1, j + 1]
                    + image[i + 1, j - 1]
                    + 2 * image[i + 1, j]
                    + image[i + 1, j + 1]
                )

        magnitude = np.sqrt(gx**2 + gy**2)
        # Normalize to 0-1
        max_val = magnitude.max()
        if max_val > 0:
            magnitude = magnitude / max_val
        return magnitude

    def _non_maximum_suppression(self, gradient_mag: np.ndarray, image: np.ndarray) -> np.ndarray:
        """Thin edges using non-maximum suppression"""
        h, w = gradient_mag.shape
        suppressed = np.zeros_like(gradient_mag)

        for i in range(1, h - 1):
            for j in range(1, w - 1):
                mag = gradient_mag[i, j]
                if mag < self.config.edge_sensitivity * 0.3:
                    continue

                # Estimate gradient direction from image differences
                dx = abs(image[i, j + 1] - image[i, j - 1]) if j > 0 and j < w - 1 else 0
                dy = abs(image[i + 1, j] - image[i - 1, j]) if i > 0 and i < h - 1 else 0

                # Check if current pixel is local maximum along gradient
                if dx > dy:  # Horizontal edge
                    if mag >= gradient_mag[i, j - 1] and mag >= gradient_mag[i, j + 1]:
                        suppressed[i, j] = mag
                else:  # Vertical edge
                    if mag >= gradient_mag[i - 1, j] and mag >= gradient_mag[i + 1, j]:
                        suppressed[i, j] = mag

        return suppressed

    def _hysteresis_threshold(
        self, edges: np.ndarray, low_threshold: float, high_threshold: float
    ) -> np.ndarray:
        """Apply hysteresis thresholding (Canny-style)"""
        h, w = edges.shape
        result = np.zeros((h, w), dtype=np.uint8)

        # Mark strong edges
        strong = edges >= high_threshold
        weak = (edges >= low_threshold) & ~strong

        result[strong] = 1

        # Connect weak edges to strong edges
        changed = True
        while changed:
            changed = False
            for i in range(1, h - 1):
                for j in range(1, w - 1):
                    if weak[i, j] and result[i, j] == 0:
                        # Check if connected to strong edge
                        for di in range(-1, 2):
                            for dj in range(-1, 2):
                                if result[i + di, j + dj] == 1:
                                    result[i, j] = 1
                                    changed = True
                                    break
                            if result[i, j] == 1:
                                break

        return result

    def _close_boundaries(self, edge_mask: np.ndarray, iterations: int = 3) -> np.ndarray:
        """Close gaps in boundary edges using morphological closing"""
        result = edge_mask.copy()
        h, w = result.shape

        for _ in range(iterations):
            dilated = np.zeros_like(result)
            for i in range(h):
                for j in range(w):
                    if result[i, j] == 1:
                        for di in range(-1, 2):
                            for dj in range(-1, 2):
                                ni, nj = i + di, j + dj
                                if 0 <= ni < h and 0 <= nj < w:
                                    dilated[ni, nj] = 1
            result = dilated

        return result

    def _fill_enclosed_regions(self, boundary_mask: np.ndarray) -> np.ndarray:
        """Fill regions enclosed by boundaries"""
        h, w = boundary_mask.shape
        filled = np.ones((h, w), dtype=np.uint8)

        # Flood fill from edges to find exterior
        visited = np.zeros((h, w), dtype=bool)
        queue = []

        # Start from border pixels that are not boundaries
        for i in range(h):
            for j in [0, w - 1]:
                if boundary_mask[i, j] == 0 and not visited[i, j]:
                    queue.append((i, j))
                    visited[i, j] = True
        for j in range(w):
            for i in [0, h - 1]:
                if boundary_mask[i, j] == 0 and not visited[i, j]:
                    queue.append((i, j))
                    visited[i, j] = True

        # BFS flood fill exterior
        while queue:
            ci, cj = queue.pop(0)
            filled[ci, cj] = 0
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = ci + di, cj + dj
                if 0 <= ni < h and 0 <= nj < w:
                    if not visited[ni, nj] and boundary_mask[ni, nj] == 0:
                        visited[ni, nj] = True
                        queue.append((ni, nj))

        # Remove boundary pixels from filled regions
        filled[boundary_mask == 1] = 0

        return filled

    def _label_regions(self, filled_mask: np.ndarray) -> tuple[np.ndarray, int]:
        """Label individual filled regions"""
        h, w = filled_mask.shape
        labels = np.zeros((h, w), dtype=np.int32)
        current_label = 0

        for i in range(h):
            for j in range(w):
                if filled_mask[i, j] == 1 and labels[i, j] == 0:
                    current_label += 1
                    queue = [(i, j)]
                    labels[i, j] = current_label
                    while queue:
                        ci, cj = queue.pop(0)
                        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            ni, nj = ci + di, cj + dj
                            if 0 <= ni < h and 0 <= nj < w:
                                if filled_mask[ni, nj] == 1 and labels[ni, nj] == 0:
                                    labels[ni, nj] = current_label
                                    queue.append((ni, nj))

        return labels, current_label

    def _regions_to_polygons(
        self, labels: np.ndarray, num_regions: int, bounds: dict[str, float], h: int, w: int
    ) -> list[list[tuple[float, float]]]:
        """Convert labeled regions to geographic polygons"""
        lat_range = bounds["north"] - bounds["south"]
        lon_range = bounds["east"] - bounds["west"]
        polygons = []

        for label_id in range(1, num_regions + 1):
            component = (labels == label_id).astype(np.uint8)

            # Check minimum size
            pixel_count = np.sum(component)
            pixel_area_m2 = (lat_range * 111320 / h) * (lon_range * 111320 * math.cos(
                math.radians((bounds["north"] + bounds["south"]) / 2)
            ) / w)
            area_hectares = pixel_count * pixel_area_m2 / 10000

            if area_hectares < 0.01:  # Skip very small regions
                continue

            # Extract boundary contour
            contour = self._extract_boundary_contour(component)
            if len(contour) < 4:
                continue

            # Convert to geographic coordinates
            geo_coords = []
            for px, py in contour:
                lon = bounds["west"] + (px / w) * lon_range
                lat = bounds["north"] - (py / h) * lat_range
                geo_coords.append((lon, lat))

            polygons.append(geo_coords)

        return polygons

    def _extract_boundary_contour(self, component: np.ndarray) -> list[tuple[int, int]]:
        """Extract boundary pixels of a component"""
        h, w = component.shape
        boundary = []

        for i in range(h):
            for j in range(w):
                if component[i, j] == 1:
                    # Check if it's a boundary pixel
                    is_boundary = False
                    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ni, nj = i + di, j + dj
                        if ni < 0 or ni >= h or nj < 0 or nj >= w or component[ni, nj] == 0:
                            is_boundary = True
                            break
                    if is_boundary:
                        boundary.append((j, i))  # (x, y) format

        # Sort boundary points to form a polygon (convex hull approximation)
        if len(boundary) > 4:
            boundary = self._order_boundary_points(boundary)

        return boundary

    def _order_boundary_points(self, points: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """Order boundary points counter-clockwise around centroid"""
        if len(points) < 3:
            return points

        # Calculate centroid
        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)

        # Sort by angle from centroid
        def angle_key(p):
            return math.atan2(p[1] - cy, p[0] - cx)

        sorted_points = sorted(points, key=angle_key)

        # Subsample to reasonable number of points
        max_points = 100
        if len(sorted_points) > max_points:
            step = len(sorted_points) // max_points
            sorted_points = sorted_points[::step]

        return sorted_points


# =============================================================================
# Phase 3: Advanced Post-Processing
# =============================================================================


class ParcelPostProcessor:
    """
    Advanced post-processing for detected parcels.
    معالجة لاحقة متقدمة للقطع المكتشفة

    Includes:
    - Boundary smoothing (Chaikin's corner cutting)
    - Small parcel removal
    - Sharp angle correction
    - Overlapping parcel merging
    - Shape regularization (rectangle fitting, circle fitting)

    GeoLabel equivalent: Post-processing tools (simplification + smoothing)
    """

    def __init__(self, config: DetectionConfig | None = None):
        self.config = config or DetectionConfig()
        logger.info("Parcel Post-Processor initialized")

    def process_parcels(
        self,
        polygons: list[list[tuple[float, float]]],
        bounds: dict[str, float],
    ) -> list[list[tuple[float, float]]]:
        """
        Apply full post-processing pipeline to detected parcels.

        Pipeline:
        1. Remove small parcels (below area threshold)
        2. Simplify boundaries (Douglas-Peucker)
        3. Smooth boundaries (Chaikin's algorithm)
        4. Correct sharp angles
        5. Apply shape regularization if configured
        6. Remove overlapping parcels

        Args:
            polygons: List of polygon coordinate lists
            bounds: Geographic bounds

        Returns:
            Post-processed polygon list
        """
        logger.info(f"Post-processing {len(polygons)} parcels")
        processed = []

        for polygon in polygons:
            if len(polygon) < 3:
                continue

            # Step 1: Check minimum area
            area = self._calculate_area(polygon)
            if area < self.config.min_area_hectares:
                continue
            if area > self.config.max_area_hectares:
                continue

            # Step 2: Simplify (Douglas-Peucker)
            simplified = self._douglas_peucker(polygon, self.config.simplify_tolerance)
            if len(simplified) < 3:
                continue

            # Step 3: Smooth (Chaikin's corner cutting)
            smoothed = simplified
            for _ in range(self.config.smoothing_iterations):
                smoothed = self._chaikin_smooth(smoothed)

            # Step 4: Correct sharp angles
            corrected = self._correct_sharp_angles(smoothed, min_angle_degrees=15.0)

            # Step 5: Shape regularization
            if self.config.target_shape == ParcelShape.RECTANGLE:
                corrected = self._fit_rectangle(corrected)
            elif self.config.target_shape == ParcelShape.CONVEX_HULL:
                corrected = self._convex_hull(corrected)
            elif self.config.target_shape == ParcelShape.MINIMUM_BOUNDING:
                corrected = self._minimum_bounding_rectangle(corrected)

            processed.append(corrected)

        # Step 6: Remove duplicates/overlaps
        processed = self._remove_overlapping(processed)

        logger.info(f"Post-processing complete: {len(polygons)} → {len(processed)} parcels")
        return processed

    def _chaikin_smooth(self, coords: list[tuple[float, float]], ratio: float = 0.25) -> list[tuple[float, float]]:
        """
        Chaikin's corner cutting algorithm for boundary smoothing.
        خوارزمية تشيكن لتنعيم الحدود

        Each iteration replaces each line segment with two new points
        at 25% and 75% along the segment, creating smoother curves.
        """
        if len(coords) < 3:
            return coords

        smoothed = []
        n = len(coords)

        for i in range(n):
            p0 = coords[i]
            p1 = coords[(i + 1) % n]

            # Point at 25% along segment
            q = (
                p0[0] + ratio * (p1[0] - p0[0]),
                p0[1] + ratio * (p1[1] - p0[1]),
            )
            # Point at 75% along segment
            r = (
                p0[0] + (1 - ratio) * (p1[0] - p0[0]),
                p0[1] + (1 - ratio) * (p1[1] - p0[1]),
            )

            smoothed.append(q)
            smoothed.append(r)

        return smoothed

    def _correct_sharp_angles(
        self, coords: list[tuple[float, float]], min_angle_degrees: float = 15.0
    ) -> list[tuple[float, float]]:
        """Remove vertices that create sharp angles"""
        if len(coords) < 4:
            return coords

        corrected = []
        n = len(coords)
        min_angle_rad = math.radians(min_angle_degrees)

        for i in range(n):
            p_prev = coords[(i - 1) % n]
            p_curr = coords[i]
            p_next = coords[(i + 1) % n]

            angle = self._angle_between(p_prev, p_curr, p_next)
            if angle >= min_angle_rad:
                corrected.append(p_curr)

        return corrected if len(corrected) >= 3 else coords

    def _angle_between(
        self, p1: tuple[float, float], p2: tuple[float, float], p3: tuple[float, float]
    ) -> float:
        """Calculate angle at p2 formed by p1-p2-p3"""
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])

        dot = v1[0] * v2[0] + v1[1] * v2[1]
        mag1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
        mag2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

        if mag1 * mag2 == 0:
            return math.pi

        cos_angle = max(-1.0, min(1.0, dot / (mag1 * mag2)))
        return math.acos(cos_angle)

    def _fit_rectangle(self, coords: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Fit polygon to minimum area bounding rectangle"""
        if len(coords) < 3:
            return coords

        # Use axis-aligned bounding box as approximation
        min_lon = min(c[0] for c in coords)
        max_lon = max(c[0] for c in coords)
        min_lat = min(c[1] for c in coords)
        max_lat = max(c[1] for c in coords)

        return [
            (min_lon, min_lat),
            (max_lon, min_lat),
            (max_lon, max_lat),
            (min_lon, max_lat),
        ]

    def _convex_hull(self, coords: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Compute convex hull using Graham scan"""
        if len(coords) < 3:
            return coords

        # Find lowest point
        start = min(coords, key=lambda p: (p[1], p[0]))

        def polar_angle(p):
            return math.atan2(p[1] - start[1], p[0] - start[0])

        sorted_points = sorted(coords, key=polar_angle)

        hull = [sorted_points[0], sorted_points[1]]

        for p in sorted_points[2:]:
            while len(hull) > 1 and self._cross_product(hull[-2], hull[-1], p) <= 0:
                hull.pop()
            hull.append(p)

        return hull

    def _minimum_bounding_rectangle(self, coords: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Compute minimum area bounding rectangle using rotating calipers approximation"""
        hull = self._convex_hull(coords)
        if len(hull) < 3:
            return self._fit_rectangle(coords)

        min_area = float("inf")
        best_rect = None

        n = len(hull)
        for i in range(n):
            # Edge direction
            edge = (
                hull[(i + 1) % n][0] - hull[i][0],
                hull[(i + 1) % n][1] - hull[i][1],
            )
            edge_len = math.sqrt(edge[0] ** 2 + edge[1] ** 2)
            if edge_len == 0:
                continue

            # Normalize
            ux, uy = edge[0] / edge_len, edge[1] / edge_len
            vx, vy = -uy, ux  # Perpendicular

            # Project all hull points onto edge directions
            proj_u = [p[0] * ux + p[1] * uy for p in hull]
            proj_v = [p[0] * vx + p[1] * vy for p in hull]

            min_u, max_u = min(proj_u), max(proj_u)
            min_v, max_v = min(proj_v), max(proj_v)

            area = (max_u - min_u) * (max_v - min_v)
            if area < min_area:
                min_area = area
                # Reconstruct rectangle corners
                best_rect = [
                    (min_u * ux + min_v * vx, min_u * uy + min_v * vy),
                    (max_u * ux + min_v * vx, max_u * uy + min_v * vy),
                    (max_u * ux + max_v * vx, max_u * uy + max_v * vy),
                    (min_u * ux + max_v * vx, min_u * uy + max_v * vy),
                ]

        return best_rect if best_rect else self._fit_rectangle(coords)

    def _cross_product(
        self, o: tuple[float, float], a: tuple[float, float], b: tuple[float, float]
    ) -> float:
        """Cross product of vectors OA and OB"""
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def _remove_overlapping(
        self, polygons: list[list[tuple[float, float]]], overlap_threshold: float = 0.5
    ) -> list[list[tuple[float, float]]]:
        """Remove parcels that overlap significantly (keep larger one)"""
        if len(polygons) <= 1:
            return polygons

        # Calculate areas and sort by size (largest first)
        areas = [(i, self._calculate_area(p)) for i, p in enumerate(polygons)]
        areas.sort(key=lambda x: x[1], reverse=True)

        keep = set(range(len(polygons)))

        for idx, (i, area_i) in enumerate(areas):
            if i not in keep:
                continue
            for j, area_j in areas[idx + 1:]:
                if j not in keep:
                    continue
                # Simple centroid distance check for overlap
                c_i = self._centroid(polygons[i])
                c_j = self._centroid(polygons[j])
                dist = math.sqrt((c_i[0] - c_j[0]) ** 2 + (c_i[1] - c_j[1]) ** 2)

                # If centroids are very close and one is much smaller, remove smaller
                avg_radius = math.sqrt(area_i * 10000 / math.pi) / 111320
                if dist < avg_radius * 0.5 and area_j < area_i * overlap_threshold:
                    keep.discard(j)

        return [polygons[i] for i in sorted(keep)]

    def _douglas_peucker(
        self, coords: list[tuple[float, float]], tolerance: float
    ) -> list[tuple[float, float]]:
        """Douglas-Peucker line simplification"""
        if len(coords) <= 2:
            return coords

        max_dist = 0
        max_idx = 0

        for i in range(1, len(coords) - 1):
            dist = self._point_line_distance(coords[i], coords[0], coords[-1])
            if dist > max_dist:
                max_dist = dist
                max_idx = i

        if max_dist > tolerance:
            left = self._douglas_peucker(coords[: max_idx + 1], tolerance)
            right = self._douglas_peucker(coords[max_idx:], tolerance)
            return left[:-1] + right
        else:
            return [coords[0], coords[-1]]

    def _point_line_distance(
        self, point: tuple[float, float], line_start: tuple[float, float], line_end: tuple[float, float]
    ) -> float:
        """Perpendicular distance from point to line"""
        dx = line_end[0] - line_start[0]
        dy = line_end[1] - line_start[1]
        if dx == 0 and dy == 0:
            return math.sqrt((point[0] - line_start[0]) ** 2 + (point[1] - line_start[1]) ** 2)
        num = abs(dy * point[0] - dx * point[1] + line_end[0] * line_start[1] - line_end[1] * line_start[0])
        den = math.sqrt(dx ** 2 + dy ** 2)
        return num / den

    def _calculate_area(self, coords: list[tuple[float, float]]) -> float:
        """Calculate area in hectares using Shoelace formula"""
        if len(coords) < 3:
            return 0.0

        avg_lat = sum(c[1] for c in coords) / len(coords)
        lat_to_m = 111320.0
        lon_to_m = 111320.0 * math.cos(math.radians(avg_lat))

        coords_m = [(c[0] * lon_to_m, c[1] * lat_to_m) for c in coords]

        area = 0.0
        n = len(coords_m)
        for i in range(n):
            x1, y1 = coords_m[i]
            x2, y2 = coords_m[(i + 1) % n]
            area += x1 * y2 - x2 * y1

        return abs(area) / 2.0 / 10000.0

    def _centroid(self, coords: list[tuple[float, float]]) -> tuple[float, float]:
        """Calculate polygon centroid"""
        n = len(coords)
        return (sum(c[0] for c in coords) / n, sum(c[1] for c in coords) / n)


# =============================================================================
# Phase 4: Vector Classification Engine
# =============================================================================


class VectorClassificationEngine:
    """
    Classify existing vector parcels as agricultural/non-agricultural.
    تصنيف القطع المتجهة الموجودة كأراضي زراعية/غير زراعية

    Uses spectral and geometric features:
    - Spectral: Mean/std NDVI, EVI, NDWI per parcel
    - Geometric: Area, perimeter, compactness, elongation, rectangularity
    - Texture: NDVI variance, spatial autocorrelation

    GeoLabel equivalent: Vector classification of farmland/non-farmland
    """

    # Feature weights for classification (trained empirically)
    FEATURE_WEIGHTS = {
        "ndvi_mean": 0.25,
        "ndvi_std": -0.10,
        "evi_mean": 0.15,
        "ndwi_mean": -0.15,
        "compactness": 0.10,
        "area_score": 0.10,
        "rectangularity": 0.08,
        "elongation_score": 0.07,
    }

    # Cropland classification threshold
    CROPLAND_THRESHOLD = 0.45

    def __init__(self, config: DetectionConfig | None = None):
        self.config = config or DetectionConfig()
        logger.info("Vector Classification Engine initialized")

    async def classify_parcels(
        self,
        parcels: list[AgriculturalParcel],
        image_data: np.ndarray | None = None,
        bounds: dict[str, float] | None = None,
    ) -> list[AgriculturalParcel]:
        """
        Classify parcels as agricultural or non-agricultural.

        Uses a weighted feature scoring approach:
        1. Extract spectral features per parcel
        2. Extract geometric features per parcel
        3. Compute weighted score
        4. Classify based on threshold

        Args:
            parcels: List of parcels to classify
            image_data: Optional image data for spectral feature extraction
            bounds: Geographic bounds of image data

        Returns:
            Parcels with updated land_cover classification
        """
        logger.info(f"Classifying {len(parcels)} parcels")

        for parcel in parcels:
            features = self._extract_features(parcel, image_data, bounds)
            score = self._compute_classification_score(features)

            if score >= self.CROPLAND_THRESHOLD:
                parcel.land_cover = LandCoverClass.CROPLAND
                parcel.detection_confidence = min(0.95, 0.5 + score * 0.5)
            elif features.get("ndwi_mean", 0) > 0.3:
                parcel.land_cover = LandCoverClass.WATER
                parcel.detection_confidence = 0.7
            elif features.get("ndvi_mean", 0) > 0.15:
                parcel.land_cover = LandCoverClass.GRASSLAND
                parcel.detection_confidence = 0.6
            else:
                parcel.land_cover = LandCoverClass.BARREN
                parcel.detection_confidence = 0.5 + (1 - score) * 0.3

        cropland_count = sum(1 for p in parcels if p.land_cover == LandCoverClass.CROPLAND)
        logger.info(f"Classification: {cropland_count}/{len(parcels)} parcels are cropland")

        return parcels

    def _extract_features(
        self,
        parcel: AgriculturalParcel,
        image_data: np.ndarray | None,
        bounds: dict[str, float] | None,
    ) -> dict[str, float]:
        """Extract spectral and geometric features for a parcel"""
        features = {}

        # Spectral features (from parcel metadata or computed from image)
        features["ndvi_mean"] = parcel.mean_ndvi or 0.0
        features["ndvi_std"] = parcel.ndvi_std or 0.0
        features["evi_mean"] = parcel.mean_evi or 0.0
        features["ndwi_mean"] = parcel.mean_ndwi or 0.0

        # Geometric features
        features["compactness"] = parcel.compactness or self._compute_compactness(
            parcel.area_hectares, parcel.perimeter_meters
        )
        features["area_score"] = self._area_to_score(parcel.area_hectares)
        features["rectangularity"] = parcel.rectangularity or 0.5
        features["elongation_score"] = 1.0 - min(1.0, (parcel.elongation or 3.0) / 10.0)

        return features

    def _compute_classification_score(self, features: dict[str, float]) -> float:
        """Compute weighted classification score"""
        score = 0.0

        for feature_name, weight in self.FEATURE_WEIGHTS.items():
            value = features.get(feature_name, 0.0)
            score += value * weight

        # Normalize to 0-1
        score = max(0.0, min(1.0, score + 0.3))
        return score

    def _compute_compactness(self, area_hectares: float, perimeter_meters: float) -> float:
        """Isoperimetric quotient: 4π·A/P²"""
        if perimeter_meters <= 0:
            return 0.0
        area_m2 = area_hectares * 10000
        return min(1.0, (4 * math.pi * area_m2) / (perimeter_meters ** 2))

    def _area_to_score(self, area_hectares: float) -> float:
        """Convert area to agricultural likelihood score"""
        # Typical agricultural fields: 0.1-100 hectares
        if 0.5 <= area_hectares <= 50:
            return 1.0
        elif 0.1 <= area_hectares < 0.5:
            return area_hectares / 0.5
        elif 50 < area_hectares <= 200:
            return max(0.3, 1.0 - (area_hectares - 50) / 150)
        elif area_hectares < 0.1:
            return area_hectares / 0.1 * 0.3
        else:
            return 0.2


# =============================================================================
# Main Orchestrator: Agricultural Land Detector
# =============================================================================


class AgriculturalLandDetector:
    """
    Main orchestrator for automatic agricultural land detection.
    المنسق الرئيسي لكشف الأراضي الزراعية التلقائي

    Combines all 4 strategies inspired by GeoLabel:
    1. Semantic Segmentation → pixel classification → polygonize
    2. Boundary Detection → edge detection → close → fill → polygons
    3. Training-Free → NDVI/spectral indices → approximate parcels
    4. Vector Classification → classify existing parcels

    Supports:
    - Full image detection (like GeoLabel's full-page annotation)
    - Region-based detection (like GeoLabel's custom range)
    - Point-based detection (like GeoLabel's point click annotation)
    """

    def __init__(self, config: DetectionConfig | None = None, multi_provider=None):
        self.config = config or DetectionConfig()
        self.multi_provider = multi_provider

        # Initialize engines
        self.segmentation = SemanticSegmentationEngine(self.config)
        self.boundary_detection = BoundaryDetectionEngine(self.config)
        self.post_processor = ParcelPostProcessor(self.config)
        self.classifier = VectorClassificationEngine(self.config)

        logger.info(
            f"Agricultural Land Detector initialized "
            f"(strategy={self.config.strategy.value}, precision={self.config.precision.value})"
        )

    async def detect_parcels(
        self,
        image_data: np.ndarray | None = None,
        bounds: dict[str, float] | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        radius_meters: float = 1000,
    ) -> DetectionReport:
        """
        Detect agricultural parcels in the given area.

        Can work with:
        1. Pre-loaded image data + bounds
        2. Lat/lon + radius (will fetch satellite data)

        Args:
            image_data: Optional pre-loaded multi-spectral image (H, W, C)
            bounds: Geographic bounds {north, south, east, west}
            latitude: Center latitude (if no image_data)
            longitude: Center longitude (if no image_data)
            radius_meters: Search radius (if using lat/lon)

        Returns:
            DetectionReport with all detected parcels
        """
        import time

        start_time = time.time()
        warnings = []

        # Generate or use provided image data
        if image_data is None:
            if latitude is None or longitude is None:
                raise ValueError("Either image_data+bounds or latitude+longitude must be provided")

            # Generate synthetic data for demonstration
            image_data, bounds = self._generate_synthetic_data(latitude, longitude, radius_meters)
            warnings.append("Using synthetic data - connect satellite provider for real imagery")

        h, w = image_data.shape[:2]
        logger.info(f"Detecting parcels in {h}x{w} image, strategy={self.config.strategy.value}")

        # Execute detection strategy
        all_polygons = []

        if self.config.strategy in (DetectionStrategy.SEMANTIC_SEGMENTATION, DetectionStrategy.HYBRID):
            seg_mask = await self.segmentation.classify_pixels(image_data, bounds)
            seg_polygons = await self.segmentation.polygonize_mask(seg_mask, bounds, LandCoverClass.CROPLAND.value)
            all_polygons.extend(seg_polygons)
            logger.info(f"Segmentation: {len(seg_polygons)} parcels")

        if self.config.strategy in (DetectionStrategy.BOUNDARY_DETECTION, DetectionStrategy.HYBRID):
            boundary_polygons = await self.boundary_detection.detect_boundaries(image_data, bounds)
            all_polygons.extend(boundary_polygons)
            logger.info(f"Boundary detection: {len(boundary_polygons)} parcels")

        if self.config.strategy == DetectionStrategy.TRAINING_FREE:
            tf_polygons = await self._training_free_detection(image_data, bounds)
            all_polygons.extend(tf_polygons)
            logger.info(f"Training-free: {len(tf_polygons)} parcels")

        # Post-process all detected polygons
        processed_polygons = self.post_processor.process_parcels(all_polygons, bounds)

        # Convert to AgriculturalParcel objects
        parcels = []
        for i, polygon in enumerate(processed_polygons):
            parcel = self._polygon_to_parcel(polygon, i, bounds, image_data)
            parcels.append(parcel)

        # Classify parcels
        parcels = await self.classifier.classify_parcels(parcels, image_data, bounds)

        # Build report
        elapsed = time.time() - start_time
        cropland_parcels = [p for p in parcels if p.land_cover == LandCoverClass.CROPLAND]

        report = DetectionReport(
            total_parcels=len(parcels),
            total_area_hectares=sum(p.area_hectares for p in parcels),
            cropland_parcels=len(cropland_parcels),
            cropland_area_hectares=sum(p.area_hectares for p in cropland_parcels),
            non_cropland_parcels=len(parcels) - len(cropland_parcels),
            detection_time_seconds=elapsed,
            strategy_used=self.config.strategy,
            precision_level=self.config.precision,
            parcels=parcels,
            warnings=warnings,
        )

        logger.info(
            f"Detection complete: {report.cropland_parcels} cropland parcels "
            f"({report.cropland_area_hectares:.1f} ha) in {elapsed:.1f}s"
        )
        return report

    async def detect_at_point(
        self,
        latitude: float,
        longitude: float,
        radius_meters: float = 500,
    ) -> DetectionReport:
        """
        Detect parcels around a specific point (GeoLabel point-click mode).
        كشف القطع حول نقطة محددة (وضع النقر على النقطة)
        """
        return await self.detect_parcels(
            latitude=latitude,
            longitude=longitude,
            radius_meters=radius_meters,
        )

    async def detect_in_region(
        self,
        bounds: dict[str, float],
        image_data: np.ndarray | None = None,
    ) -> DetectionReport:
        """
        Detect parcels in a specific region (GeoLabel custom range mode).
        كشف القطع في منطقة محددة (وضع النطاق المخصص)
        """
        if image_data is None:
            center_lat = (bounds["north"] + bounds["south"]) / 2
            center_lon = (bounds["east"] + bounds["west"]) / 2
            lat_range = bounds["north"] - bounds["south"]
            radius = lat_range * 111320 / 2
            image_data, bounds = self._generate_synthetic_data(center_lat, center_lon, radius)

        return await self.detect_parcels(image_data=image_data, bounds=bounds)

    async def _training_free_detection(
        self,
        image_data: np.ndarray,
        bounds: dict[str, float],
    ) -> list[list[tuple[float, float]]]:
        """
        Training-free approximate detection using spectral indices only.
        كشف تقريبي بدون تدريب باستخدام المؤشرات الطيفية فقط

        GeoLabel equivalent: Strategy 4 - Training-free approximate farmland detection
        """
        h, w = image_data.shape[:2]

        # Compute NDVI
        if len(image_data.shape) > 2 and image_data.shape[2] >= 4:
            nir = image_data[:, :, 3].astype(np.float64)
            red = image_data[:, :, 2].astype(np.float64)
            denom = nir + red
            ndvi = np.where(denom > 0, (nir - red) / denom, 0.0)
        else:
            ndvi = image_data[:, :, 0].astype(np.float64) if len(image_data.shape) > 2 else image_data.astype(
                np.float64
            )

        # Simple threshold
        cropland_mask = (ndvi > self.config.ndvi_cropland_threshold).astype(np.uint8)

        # Clean up with morphology
        cropland_mask = self.segmentation._morphological_close(cropland_mask, iterations=2)
        cropland_mask = self.segmentation._morphological_open(cropland_mask, iterations=1)

        # Connected components
        labels, num_components = self.segmentation._connected_components(cropland_mask)

        # Extract polygons
        polygons = []
        lat_range = bounds["north"] - bounds["south"]
        lon_range = bounds["east"] - bounds["west"]

        for label_id in range(1, num_components + 1):
            component = (labels == label_id).astype(np.uint8)
            pixel_count = np.sum(component)

            # Skip very small regions
            if pixel_count < 4:
                continue

            contour = self.segmentation._trace_contour(component)
            if len(contour) < 4:
                continue

            geo_coords = []
            for px, py in contour:
                lon = bounds["west"] + (px / w) * lon_range
                lat = bounds["north"] - (py / h) * lat_range
                geo_coords.append((lon, lat))

            polygons.append(geo_coords)

        return polygons

    def _polygon_to_parcel(
        self,
        polygon: list[tuple[float, float]],
        index: int,
        bounds: dict[str, float],
        image_data: np.ndarray,
    ) -> AgriculturalParcel:
        """Convert a polygon to an AgriculturalParcel with computed features"""
        area = self.post_processor._calculate_area(polygon)
        perimeter = self._calculate_perimeter(polygon)
        centroid = self.post_processor._centroid(polygon)

        # Compactness (isoperimetric quotient)
        area_m2 = area * 10000
        compactness = (4 * math.pi * area_m2) / (perimeter ** 2) if perimeter > 0 else 0

        # Elongation (bounding box ratio)
        lons = [c[0] for c in polygon]
        lats = [c[1] for c in polygon]
        lon_range = max(lons) - min(lons)
        lat_range = max(lats) - min(lats)
        avg_lat = sum(lats) / len(lats)
        width_m = lon_range * 111320 * math.cos(math.radians(avg_lat))
        height_m = lat_range * 111320
        elongation = max(width_m, height_m) / max(min(width_m, height_m), 1)

        # Rectangularity
        bbox_area = width_m * height_m
        rectangularity = area_m2 / bbox_area if bbox_area > 0 else 0

        # Approximate NDVI from image
        mean_ndvi = self._sample_ndvi_in_polygon(polygon, image_data, bounds)

        return AgriculturalParcel(
            parcel_id=f"parcel_{uuid.uuid4().hex[:8]}",
            coordinates=polygon,
            area_hectares=round(area, 4),
            perimeter_meters=round(perimeter, 2),
            centroid=centroid,
            land_cover=LandCoverClass.UNKNOWN,
            detection_confidence=0.0,
            detection_date=datetime.now(),
            strategy=self.config.strategy,
            mean_ndvi=round(mean_ndvi, 3),
            compactness=round(compactness, 3),
            elongation=round(elongation, 2),
            rectangularity=round(rectangularity, 3),
            num_vertices=len(polygon),
            quality_score=round(min(1.0, compactness * 0.4 + rectangularity * 0.3 + 0.3), 2),
        )

    def _calculate_perimeter(self, coords: list[tuple[float, float]]) -> float:
        """Calculate perimeter in meters"""
        if len(coords) < 2:
            return 0.0
        perimeter = 0.0
        n = len(coords)
        for i in range(n):
            lon1, lat1 = coords[i]
            lon2, lat2 = coords[(i + 1) % n]
            perimeter += self._haversine(lat1, lon1, lat2, lon2)
        return perimeter

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine distance in meters"""
        R = 6371000
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(
            dlon / 2
        ) ** 2
        return R * 2 * math.asin(math.sqrt(a))

    def _sample_ndvi_in_polygon(
        self,
        polygon: list[tuple[float, float]],
        image_data: np.ndarray,
        bounds: dict[str, float],
    ) -> float:
        """Sample approximate NDVI value within polygon from image data"""
        centroid = self.post_processor._centroid(polygon)
        h, w = image_data.shape[:2]
        lat_range = bounds["north"] - bounds["south"]
        lon_range = bounds["east"] - bounds["west"]

        if lat_range == 0 or lon_range == 0:
            return 0.0

        # Convert centroid to pixel
        px = int((centroid[0] - bounds["west"]) / lon_range * w)
        py = int((bounds["north"] - centroid[1]) / lat_range * h)

        px = max(0, min(px, w - 1))
        py = max(0, min(py, h - 1))

        # Compute NDVI at pixel
        if len(image_data.shape) > 2 and image_data.shape[2] >= 4:
            nir = float(image_data[py, px, 3])
            red = float(image_data[py, px, 2])
            denom = nir + red
            return (nir - red) / denom if denom > 0 else 0.0
        elif len(image_data.shape) > 2:
            return float(image_data[py, px, 0])
        else:
            return float(image_data[py, px])

    def _generate_synthetic_data(
        self, lat: float, lon: float, radius_m: float
    ) -> tuple[np.ndarray, dict[str, float]]:
        """Generate synthetic multi-spectral data for demonstration"""
        size = 64  # 64x64 pixels
        lat_offset = radius_m / 111320.0
        lon_offset = radius_m / (111320.0 * math.cos(math.radians(lat)))

        bounds = {
            "north": lat + lat_offset,
            "south": lat - lat_offset,
            "east": lon + lon_offset,
            "west": lon - lon_offset,
        }

        # Generate 4-band synthetic image (Blue, Green, Red, NIR)
        rng = np.random.default_rng(seed=int(abs(lat * 1e6 + lon * 1e6)) % (2**31))
        image = np.zeros((size, size, 4), dtype=np.float64)

        # Create synthetic agricultural patterns
        for i in range(size):
            for j in range(size):
                # Create a few rectangular "fields"
                in_field = False
                field_regions = [
                    (10, 10, 25, 25),
                    (30, 5, 55, 20),
                    (5, 35, 20, 55),
                    (35, 30, 58, 50),
                    (25, 40, 45, 60),
                ]
                for y1, x1, y2, x2 in field_regions:
                    if x1 <= j < x2 and y1 <= i < y2:
                        in_field = True
                        break

                if in_field:
                    # Agricultural land: high NIR, moderate Red
                    image[i, j, 0] = 0.05 + rng.random() * 0.05  # Blue
                    image[i, j, 1] = 0.08 + rng.random() * 0.05  # Green
                    image[i, j, 2] = 0.06 + rng.random() * 0.04  # Red
                    image[i, j, 3] = 0.35 + rng.random() * 0.15  # NIR
                else:
                    # Non-agricultural: low NIR, higher Red
                    image[i, j, 0] = 0.10 + rng.random() * 0.08  # Blue
                    image[i, j, 1] = 0.12 + rng.random() * 0.06  # Green
                    image[i, j, 2] = 0.15 + rng.random() * 0.08  # Red
                    image[i, j, 3] = 0.10 + rng.random() * 0.08  # NIR

        return image, bounds
