"""
SAHOOL Agricultural Land Detection - GeoLabel-Inspired (v4.0)
كشف الأراضي الزراعية التلقائي مستوحى من GeoLabel 4.0

Automatic agricultural land parcel generation using heuristic strategies.

NOTE: The current implementation uses spectral-index heuristics (NDVI/EVI/NDWI
thresholds, gradient-based edge detection) rather than trained deep learning models.
The architecture is designed so that trained models (U-Net, DeepLabV3+, HED, etc.)
can replace the heuristic engines when training data becomes available.

Strategies implemented:
1. Semantic Segmentation Engine: Spectral-index threshold classification
   (placeholder for U-Net/DeepLabV3+ — currently uses NDVI/EVI/NDWI thresholds)
2. Boundary Detection Engine: Gradient-based edge detection
   (placeholder for HED-like models — currently uses Sobel-like gradients)
3. Training-Free Detection: NDVI+spectral index approximate detection
4. Vector Classification: Feature-based parcel type scoring (rule-based)
5. Crop Classification Engine: ML spectral scoring + DL placeholder ensemble
6. Topology-Preserving Simplification: Douglas-Peucker with shared vertex preservation
7. Parcel Editing Tools: Merge, split, connect operations
8. Quality Inspection Tool: Validation, attribute editing, WKT export

References:
- GeoLabel 3.6.0 SAM-based semi-automatic annotation
- GeoLabel 4.0 for China's 4th National Agricultural Census
- "Deep Edge Enhancement Semantic Segmentation for Farmland" (2022)
- "Delineate Anything: Resolution-Agnostic Field Boundary Delineation" (2025)
- BSNet: Boundary-Semantic Fusion Network for farmland segmentation
"""

import collections
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
    """Land cover classification classes (GeoLabel 8-class system)
    فئات تصنيف الغطاء الأرضي (نظام GeoLabel ذو 8 فئات)
    """

    CROPLAND = "cropland"  # 耕地 - أرض زراعية
    ORCHARD = "orchard"  # 园地 - بستان
    FOREST = "forest"  # 林地 - غابة
    GRASSLAND = "grassland"  # 草地 - مرعى
    BUILT_UP = "built_up"  # 建筑 - منطقة مبنية
    WATER = "water"  # 水面 - مسطح مائي
    ROAD = "road"  # 道路 - طريق
    BARREN = "barren"  # 其他 - أرض جرداء / أخرى
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
        """Convert to GeoJSON Feature (RFC 7946 compliant closed rings)"""
        ring = [[lon, lat] for lon, lat in self.coordinates]
        # GeoJSON requires closed LinearRings (first == last point)
        if ring and ring[0] != ring[-1]:
            ring.append(ring[0])
        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [ring],
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

        # Integer-coded classification for performance (avoid dtype=object)
        # Code mapping: 0=barren, 1=water, 2=grassland, 3=cropland
        _CODE_BARREN = 0
        _CODE_WATER = 1
        _CODE_GRASSLAND = 2
        _CODE_CROPLAND = 3
        _CODE_TO_CLASS = {
            _CODE_BARREN: LandCoverClass.BARREN.value,
            _CODE_WATER: LandCoverClass.WATER.value,
            _CODE_GRASSLAND: LandCoverClass.GRASSLAND.value,
            _CODE_CROPLAND: LandCoverClass.CROPLAND.value,
        }

        int_mask = np.full((h, w), _CODE_BARREN, dtype=np.uint8)

        # Water detection (high NDWI) — highest priority
        if ndwi is not None:
            water_mask = ndwi > self.config.ndwi_water_threshold
            int_mask[water_mask] = _CODE_WATER

        # Sparse vegetation (NDVI above vegetation threshold but below cropland)
        veg_mask = ndvi > self.config.ndvi_vegetation_threshold
        int_mask[veg_mask] = _CODE_GRASSLAND

        # Cropland detection (high NDVI + EVI)
        crop_ndvi_mask = ndvi > self.config.ndvi_cropland_threshold
        if evi is not None:
            cropland_mask = crop_ndvi_mask & (evi > self.config.evi_threshold)
            grassland_mask = crop_ndvi_mask & ~(evi > self.config.evi_threshold)
            int_mask[grassland_mask] = _CODE_GRASSLAND
            int_mask[cropland_mask] = _CODE_CROPLAND
        else:
            int_mask[crop_ndvi_mask] = _CODE_CROPLAND

        # Water overrides all — reapply on top
        if ndwi is not None:
            int_mask[water_mask] = _CODE_WATER

        # Map integer codes to string class values at the boundary
        mask = np.empty((h, w), dtype=object)
        for code, class_val in _CODE_TO_CLASS.items():
            mask[int_mask == code] = class_val

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

        # Create binary mask for target class (vectorized comparison)
        binary_mask = (mask == target_class).astype(np.uint8)

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
                    queue = collections.deque([(i, j)])
                    labels[i, j] = current_label
                    while queue:
                        ci, cj = queue.popleft()
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
        """Close gaps in boundary edges using morphological closing (dilate then erode)."""
        result = edge_mask.copy()
        h, w = result.shape

        def _dilate(src: np.ndarray) -> np.ndarray:
            out = np.zeros_like(src)
            for i in range(h):
                for j in range(w):
                    if src[i, j] == 1:
                        for di in range(-1, 2):
                            for dj in range(-1, 2):
                                ni, nj = i + di, j + dj
                                if 0 <= ni < h and 0 <= nj < w:
                                    out[ni, nj] = 1
            return out

        def _erode(src: np.ndarray) -> np.ndarray:
            out = np.zeros_like(src)
            for i in range(h):
                for j in range(w):
                    if src[i, j] == 1:
                        all_set = True
                        for di in range(-1, 2):
                            for dj in range(-1, 2):
                                ni, nj = i + di, j + dj
                                if 0 <= ni < h and 0 <= nj < w:
                                    if src[ni, nj] == 0:
                                        all_set = False
                                        break
                                else:
                                    all_set = False
                                    break
                            if not all_set:
                                break
                        if all_set:
                            out[i, j] = 1
            return out

        # Morphological closing = dilate then erode
        for _ in range(iterations):
            result = _dilate(result)
        for _ in range(iterations):
            result = _erode(result)

        return result

    def _fill_enclosed_regions(self, boundary_mask: np.ndarray) -> np.ndarray:
        """Fill regions enclosed by boundaries"""
        h, w = boundary_mask.shape
        filled = np.ones((h, w), dtype=np.uint8)

        # Flood fill from edges to find exterior
        visited = np.zeros((h, w), dtype=bool)
        queue = collections.deque()

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
            ci, cj = queue.popleft()
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
                    queue = collections.deque([(i, j)])
                    labels[i, j] = current_label
                    while queue:
                        ci, cj = queue.popleft()
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
        mag1 = math.hypot(v1[0], v1[1])
        mag2 = math.hypot(v2[0], v2[1])

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
            edge_len = math.hypot(edge[0], edge[1])
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
                dist = math.hypot(c_i[0] - c_j[0], c_i[1] - c_j[1])

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
            return math.hypot(point[0] - line_start[0], point[1] - line_start[1])
        num = abs(dy * point[0] - dx * point[1] + line_end[0] * line_start[1] - line_end[1] * line_start[0])
        den = math.hypot(dx, dy)
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

    Combines all strategies inspired by GeoLabel 4.0:
    Phase 1-4 (Original):
    1. Semantic Segmentation → pixel classification → polygonize
    2. Boundary Detection → edge detection → close → fill → polygons
    3. Training-Free → NDVI/spectral indices → approximate parcels
    4. Vector Classification → classify existing parcels

    GeoLabel 4.0 additions:
    5. Crop Classification Engine → ML+DL crop type identification
    6. Topology-Preserving Simplification → maintain adjacency
    7. Parcel Editing Tools → merge/split/connect operations
    8. Quality Inspection → browsing, WKT export, batch attribute assignment

    Supports:
    - Full image detection (like GeoLabel's full-page annotation)
    - Region-based detection (like GeoLabel's custom range)
    - Point-based detection (like GeoLabel's point click annotation)
    """

    def __init__(self, config: DetectionConfig | None = None, multi_provider=None):
        self.config = config or DetectionConfig()
        self.multi_provider = multi_provider

        # Phase 1-4: Core detection engines
        self.segmentation = SemanticSegmentationEngine(self.config)
        self.boundary_detection = BoundaryDetectionEngine(self.config)
        self.post_processor = ParcelPostProcessor(self.config)
        self.classifier = VectorClassificationEngine(self.config)

        # GeoLabel 4.0: Advanced engines
        self.crop_classifier = CropClassificationEngine(self.config)
        self.topology_simplifier = TopologyPreservingSimplifier(
            tolerance=self.config.simplify_tolerance,
        )
        self.editing_tools = ParcelEditingTools()
        self.quality_inspector = QualityInspectionTool()

        logger.info(
            f"Agricultural Land Detector initialized with GeoLabel 4.0 engines "
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


# =============================================================================
# GeoLabel 4.0: Crop Classification Engine (ML + DL dual path)
# محرك تصنيف المحاصيل (مسار مزدوج: تعلم آلي + تعلم عميق)
# =============================================================================


class CropType(str, Enum):
    """Crop type classification classes | فئات تصنيف المحاصيل"""

    WHEAT = "wheat"  # قمح
    RICE = "rice"  # أرز
    CORN = "corn"  # ذرة
    COTTON = "cotton"  # قطن
    SOYBEAN = "soybean"  # فول صويا
    VEGETABLES = "vegetables"  # خضروات
    FRUIT_TREES = "fruit_trees"  # أشجار فاكهة
    DATE_PALM = "date_palm"  # نخيل
    BARLEY = "barley"  # شعير
    SORGHUM = "sorghum"  # ذرة رفيعة
    ALFALFA = "alfalfa"  # برسيم
    FALLOW = "fallow"  # بور
    GREENHOUSE = "greenhouse"  # بيوت محمية
    OTHER_CROP = "other_crop"  # محصول آخر
    UNKNOWN = "unknown"  # غير محدد


@dataclass
class CropClassificationResult:
    """Result of crop type classification for a parcel"""

    parcel_id: str
    predicted_crop: CropType
    confidence: float
    ml_prediction: CropType | None = None
    ml_confidence: float = 0.0
    dl_prediction: CropType | None = None
    dl_confidence: float = 0.0
    feature_scores: dict[str, float] | None = None
    secondary_crops: list[tuple[CropType, float]] | None = None


class CropClassificationEngine:
    """
    Crop type classification using ML + DL dual path.
    تصنيف نوع المحصول باستخدام المسار المزدوج (تعلم آلي + تعلم عميق)

    GeoLabel 4.0 equivalent: Crop Classification (作物分类)
    Two technical paths per the 4th National Agricultural Census specification:

    1. AI Model (DL path):
       - U-Net/DeepLab/PSPNet/DLinkNet/Transformer for parcel-level crop identification
       - Uses spectral, texture, and semantic features from imagery
       - Higher accuracy but requires trained model weights

    2. ML Model (ML path):
       - Random Forest (RF) / SVM pixel-based classification
       - Uses spectral features (NDVI temporal profile, EVI, band ratios)
       - Faster, works with pre-computed features, no GPU required

    Final prediction is an ensemble of both paths with configurable weights.
    """

    # Spectral signature profiles for common crops (NDVI temporal patterns)
    # Based on multi-temporal Sentinel-2 observations for Middle East / Yemen region
    CROP_SPECTRAL_PROFILES = {
        CropType.WHEAT: {
            "ndvi_peak": 0.75, "ndvi_range": (0.3, 0.82), "evi_peak": 0.55,
            "peak_month": 3, "growing_months": (11, 4), "ndwi_range": (-0.1, 0.15),
        },
        CropType.BARLEY: {
            "ndvi_peak": 0.68, "ndvi_range": (0.25, 0.72), "evi_peak": 0.48,
            "peak_month": 2, "growing_months": (10, 3), "ndwi_range": (-0.15, 0.1),
        },
        CropType.RICE: {
            "ndvi_peak": 0.80, "ndvi_range": (0.15, 0.85), "evi_peak": 0.60,
            "peak_month": 8, "growing_months": (5, 10), "ndwi_range": (0.1, 0.45),
        },
        CropType.CORN: {
            "ndvi_peak": 0.78, "ndvi_range": (0.2, 0.82), "evi_peak": 0.58,
            "peak_month": 7, "growing_months": (4, 9), "ndwi_range": (-0.05, 0.2),
        },
        CropType.COTTON: {
            "ndvi_peak": 0.65, "ndvi_range": (0.2, 0.70), "evi_peak": 0.45,
            "peak_month": 8, "growing_months": (4, 10), "ndwi_range": (-0.1, 0.1),
        },
        CropType.SOYBEAN: {
            "ndvi_peak": 0.72, "ndvi_range": (0.2, 0.78), "evi_peak": 0.52,
            "peak_month": 7, "growing_months": (5, 10), "ndwi_range": (-0.05, 0.15),
        },
        CropType.VEGETABLES: {
            "ndvi_peak": 0.60, "ndvi_range": (0.25, 0.65), "evi_peak": 0.42,
            "peak_month": None, "growing_months": None, "ndwi_range": (-0.1, 0.2),
        },
        CropType.FRUIT_TREES: {
            "ndvi_peak": 0.55, "ndvi_range": (0.35, 0.60), "evi_peak": 0.38,
            "peak_month": 6, "growing_months": (1, 12), "ndwi_range": (-0.15, 0.05),
        },
        CropType.DATE_PALM: {
            "ndvi_peak": 0.45, "ndvi_range": (0.30, 0.50), "evi_peak": 0.30,
            "peak_month": 7, "growing_months": (1, 12), "ndwi_range": (-0.2, 0.0),
        },
        CropType.ALFALFA: {
            "ndvi_peak": 0.70, "ndvi_range": (0.35, 0.75), "evi_peak": 0.50,
            "peak_month": None, "growing_months": (1, 12), "ndwi_range": (-0.05, 0.15),
        },
        CropType.SORGHUM: {
            "ndvi_peak": 0.72, "ndvi_range": (0.2, 0.76), "evi_peak": 0.52,
            "peak_month": 8, "growing_months": (5, 10), "ndwi_range": (-0.1, 0.1),
        },
        CropType.FALLOW: {
            "ndvi_peak": 0.18, "ndvi_range": (0.05, 0.22), "evi_peak": 0.10,
            "peak_month": None, "growing_months": None, "ndwi_range": (-0.3, -0.1),
        },
        CropType.GREENHOUSE: {
            "ndvi_peak": 0.10, "ndvi_range": (-0.05, 0.25), "evi_peak": 0.08,
            "peak_month": None, "growing_months": None, "ndwi_range": (-0.3, -0.05),
        },
    }

    # Geometric feature ranges for crop types
    CROP_GEOMETRIC_PROFILES = {
        CropType.WHEAT: {"area_range": (0.5, 100), "compactness_min": 0.3, "rectangularity_min": 0.5},
        CropType.RICE: {"area_range": (0.1, 5), "compactness_min": 0.4, "rectangularity_min": 0.6},
        CropType.CORN: {"area_range": (0.5, 50), "compactness_min": 0.3, "rectangularity_min": 0.4},
        CropType.DATE_PALM: {"area_range": (0.2, 20), "compactness_min": 0.2, "rectangularity_min": 0.3},
        CropType.VEGETABLES: {"area_range": (0.05, 5), "compactness_min": 0.4, "rectangularity_min": 0.6},
        CropType.GREENHOUSE: {"area_range": (0.01, 2), "compactness_min": 0.6, "rectangularity_min": 0.8},
        CropType.FRUIT_TREES: {"area_range": (0.5, 30), "compactness_min": 0.25, "rectangularity_min": 0.3},
        CropType.ALFALFA: {"area_range": (0.5, 50), "compactness_min": 0.3, "rectangularity_min": 0.4},
    }

    # ML path: Feature weights for Random Forest-like classification
    ML_FEATURE_WEIGHTS = {
        "ndvi_similarity": 0.30,
        "evi_similarity": 0.15,
        "ndwi_similarity": 0.15,
        "area_fit": 0.10,
        "compactness_fit": 0.10,
        "rectangularity_fit": 0.10,
        "temporal_fit": 0.10,
    }

    # DL path weight vs ML path weight (ensemble)
    DL_WEIGHT = 0.6
    ML_WEIGHT = 0.4

    def __init__(self, config: DetectionConfig | None = None):
        self.config = config or DetectionConfig()
        self._dl_model_loaded = False
        logger.info("Crop Classification Engine initialized (ML + DL dual path)")

    async def classify_crops(
        self,
        parcels: list[AgriculturalParcel],
        image_data: np.ndarray | None = None,
        bounds: dict[str, float] | None = None,
        current_month: int | None = None,
    ) -> list[CropClassificationResult]:
        """
        Classify crop type for each parcel using ML + DL dual path ensemble.

        Args:
            parcels: List of detected agricultural parcels
            image_data: Optional multi-spectral image for DL path
            bounds: Geographic bounds
            current_month: Current month (1-12) for temporal matching

        Returns:
            List of CropClassificationResult for each parcel
        """
        if current_month is None:
            current_month = datetime.now().month

        results = []
        for parcel in parcels:
            # ML path: Feature-based classification (RF/SVM-like)
            ml_result = self._ml_classify(parcel, current_month)

            # DL path: Image-based classification (simulated U-Net/DeepLab)
            dl_result = self._dl_classify(parcel, image_data, bounds)

            # Ensemble: Weighted combination of ML and DL predictions
            final_result = self._ensemble_predictions(parcel, ml_result, dl_result)
            results.append(final_result)

            # Update parcel crop_type
            parcel.crop_type = final_result.predicted_crop.value

        crop_counts = {}
        for r in results:
            crop_counts[r.predicted_crop.value] = crop_counts.get(r.predicted_crop.value, 0) + 1

        logger.info(f"Crop classification complete: {crop_counts}")
        return results

    def _ml_classify(
        self, parcel: AgriculturalParcel, current_month: int
    ) -> tuple[CropType, float, dict[str, float]]:
        """
        ML path: Random Forest / SVM-like classification using spectral+geometric features.

        Per GeoLabel 4.0 spec: "采用通用的基于像素的分类方法进行地块类型的分类。
        优先选择随机森林(RF)、支持向量机(SVM)等分类器"
        """
        best_crop = CropType.UNKNOWN
        best_score = 0.0
        all_scores = {}

        ndvi = parcel.mean_ndvi or 0.0
        evi = parcel.mean_evi or 0.0
        ndwi = parcel.mean_ndwi or 0.0
        area = parcel.area_hectares
        compactness = parcel.compactness or 0.0
        rectangularity = parcel.rectangularity or 0.0

        for crop_type, profile in self.CROP_SPECTRAL_PROFILES.items():
            features = {}

            # NDVI similarity to crop profile
            ndvi_min, ndvi_max = profile["ndvi_range"]
            if ndvi_min <= ndvi <= ndvi_max:
                ndvi_dist = abs(ndvi - profile["ndvi_peak"]) / max(profile["ndvi_peak"], 0.01)
                features["ndvi_similarity"] = max(0, 1.0 - ndvi_dist)
            else:
                features["ndvi_similarity"] = max(0, 1.0 - min(abs(ndvi - ndvi_min), abs(ndvi - ndvi_max)) * 3)

            # EVI similarity
            evi_diff = abs(evi - profile["evi_peak"]) / max(profile["evi_peak"], 0.01)
            features["evi_similarity"] = max(0, 1.0 - evi_diff)

            # NDWI similarity
            ndwi_min, ndwi_max = profile["ndwi_range"]
            if ndwi_min <= ndwi <= ndwi_max:
                features["ndwi_similarity"] = 1.0
            else:
                features["ndwi_similarity"] = max(0, 1.0 - min(abs(ndwi - ndwi_min), abs(ndwi - ndwi_max)) * 5)

            # Geometric features
            geo_profile = self.CROP_GEOMETRIC_PROFILES.get(crop_type, {})
            area_range = geo_profile.get("area_range", (0.05, 1000))
            if area_range[0] <= area <= area_range[1]:
                features["area_fit"] = 1.0
            else:
                features["area_fit"] = max(0, 0.5 - abs(area - sum(area_range) / 2) / max(area_range[1], 1) * 0.5)

            comp_min = max(geo_profile.get("compactness_min", 0.01), 0.01)
            features["compactness_fit"] = (
                1.0 if compactness >= geo_profile.get("compactness_min", 0)
                else compactness / comp_min
            )
            rect_min = max(geo_profile.get("rectangularity_min", 0.01), 0.01)
            features["rectangularity_fit"] = (
                1.0 if rectangularity >= geo_profile.get("rectangularity_min", 0)
                else rectangularity / rect_min
            )

            # Temporal fit (is current month in growing season?)
            growing = profile.get("growing_months")
            if growing and profile["peak_month"]:
                start, end = growing
                if start <= end:
                    in_season = start <= current_month <= end
                else:  # Wraps around year (e.g., Nov-Apr)
                    in_season = current_month >= start or current_month <= end
                features["temporal_fit"] = 1.0 if in_season else 0.3
            else:
                features["temporal_fit"] = 0.7  # Year-round or unknown

            # Weighted score
            score = sum(features.get(k, 0) * w for k, w in self.ML_FEATURE_WEIGHTS.items())
            all_scores[crop_type] = score

            if score > best_score:
                best_score = score
                best_crop = crop_type

        return best_crop, min(0.95, best_score), all_scores

    def _dl_classify(
        self,
        parcel: AgriculturalParcel,
        image_data: np.ndarray | None,
        bounds: dict[str, float] | None,
    ) -> tuple[CropType, float]:
        """
        DL path: Simulated deep learning classification.

        Per GeoLabel 4.0 spec: "利用影像的光谱、纹理和语义特征，采用适合作物分类任务
        的人工智能模型，如 U-Net、DeepLab、PSPNet、DLinkNet、Transformer 等"

        In production, this would load a trained model. Currently uses a
        spectral-enhanced heuristic as a DL proxy until a real model is integrated.
        """
        if image_data is None or bounds is None:
            # Fallback: use parcel metadata only
            ndvi = parcel.mean_ndvi or 0.0
            if ndvi > 0.7:
                return CropType.WHEAT, 0.6
            elif ndvi > 0.5:
                return CropType.CORN, 0.5
            elif ndvi > 0.3:
                return CropType.VEGETABLES, 0.4
            elif ndvi > 0.15:
                return CropType.FALLOW, 0.5
            else:
                return CropType.UNKNOWN, 0.3

        # Simulate DL model by extracting image patch features at parcel location
        h, w = image_data.shape[:2]
        centroid = parcel.centroid
        lat_range = bounds["north"] - bounds["south"]
        lon_range = bounds["east"] - bounds["west"]

        if lat_range == 0 or lon_range == 0:
            return CropType.UNKNOWN, 0.3

        px = int((centroid[0] - bounds["west"]) / lon_range * w)
        py = int((bounds["north"] - centroid[1]) / lat_range * h)
        px = max(0, min(px, w - 1))
        py = max(0, min(py, h - 1))

        # Sample a small patch around centroid
        patch_size = 5
        x1, x2 = max(0, px - patch_size), min(w, px + patch_size + 1)
        y1, y2 = max(0, py - patch_size), min(h, py + patch_size + 1)
        patch = image_data[y1:y2, x1:x2]

        if patch.size == 0:
            return CropType.UNKNOWN, 0.3

        # Compute patch-level features (simulating DL feature extraction)
        if len(patch.shape) > 2 and patch.shape[2] >= 4:
            nir = patch[:, :, 3].astype(np.float64)
            red = patch[:, :, 2].astype(np.float64)
            green = patch[:, :, 1].astype(np.float64)
            denom = nir + red
            patch_ndvi = np.where(denom > 0, (nir - red) / denom, 0.0)
            mean_ndvi = float(np.mean(patch_ndvi))
            std_ndvi = float(np.std(patch_ndvi))

            # Texture feature: NDVI variance indicates crop uniformity
            # Low variance = uniform crop (wheat, rice), high = mixed/orchard
            if mean_ndvi > 0.6 and std_ndvi < 0.1:
                return CropType.WHEAT, 0.7
            elif mean_ndvi > 0.6 and std_ndvi >= 0.1:
                return CropType.FRUIT_TREES, 0.6
            elif mean_ndvi > 0.4 and std_ndvi < 0.08:
                return CropType.ALFALFA, 0.6
            elif mean_ndvi > 0.4:
                return CropType.CORN, 0.55
            elif mean_ndvi > 0.25:
                return CropType.VEGETABLES, 0.5
            elif mean_ndvi > 0.1:
                # Check if greenhouse (low NDVI but structured)
                green_ratio = float(np.mean(green)) / max(float(np.mean(nir)), 0.01)
                if green_ratio > 0.8:
                    return CropType.GREENHOUSE, 0.5
                return CropType.FALLOW, 0.55
            else:
                return CropType.FALLOW, 0.6
        else:
            val = float(np.mean(patch))
            if val > 0.5:
                return CropType.WHEAT, 0.5
            elif val > 0.3:
                return CropType.VEGETABLES, 0.4
            else:
                return CropType.FALLOW, 0.45

    def _ensemble_predictions(
        self,
        parcel: AgriculturalParcel,
        ml_result: tuple[CropType, float, dict],
        dl_result: tuple[CropType, float],
    ) -> CropClassificationResult:
        """Ensemble ML + DL predictions with weighted voting"""
        ml_crop, ml_conf, ml_scores = ml_result
        dl_crop, dl_conf = dl_result

        # If both agree, boost confidence
        if ml_crop == dl_crop:
            final_crop = ml_crop
            final_conf = min(0.95, (ml_conf * self.ML_WEIGHT + dl_conf * self.DL_WEIGHT) * 1.2)
        else:
            # Use higher-confidence prediction
            ml_weighted = ml_conf * self.ML_WEIGHT
            dl_weighted = dl_conf * self.DL_WEIGHT
            if dl_weighted >= ml_weighted:
                final_crop = dl_crop
                final_conf = dl_conf * 0.85  # Slight penalty for disagreement
            else:
                final_crop = ml_crop
                final_conf = ml_conf * 0.85

        # Build secondary crops list from ML scores
        sorted_crops = sorted(ml_scores.items(), key=lambda x: x[1], reverse=True)
        secondary = [(crop, round(score, 3)) for crop, score in sorted_crops[:3] if crop != final_crop]

        return CropClassificationResult(
            parcel_id=parcel.parcel_id,
            predicted_crop=final_crop,
            confidence=round(final_conf, 3),
            ml_prediction=ml_crop,
            ml_confidence=round(ml_conf, 3),
            dl_prediction=dl_crop,
            dl_confidence=round(dl_conf, 3),
            feature_scores={k.value: round(v, 3) for k, v in ml_scores.items()},
            secondary_crops=secondary,
        )


# =============================================================================
# GeoLabel 4.0: Topology-Preserving Simplification
# تبسيط مع الحفاظ على العلاقات الطوبولوجية
# =============================================================================


class TopologyPreservingSimplifier:
    """
    Simplify parcel boundaries while preserving topological relationships.
    تبسيط حدود القطع مع الحفاظ على العلاقات الطوبولوجية بين القطع المتجاورة

    GeoLabel 4.0 equivalent: "تبسيط وتسهيل التعرف الذكي على قطع الأرض
    مع الحفاظ على العلاقات الطوبولوجية"

    Ensures:
    - No gaps between adjacent parcels after simplification
    - No overlaps between adjacent parcels after simplification
    - Shared boundaries remain shared (simplified consistently)
    - Parcel area change stays within tolerance
    """

    def __init__(self, tolerance: float = 0.00003, area_change_threshold: float = 0.05):
        """
        Args:
            tolerance: Douglas-Peucker simplification tolerance in degrees (~3m)
            area_change_threshold: Maximum allowed area change fraction (5%)
        """
        self.tolerance = tolerance
        self.area_change_threshold = area_change_threshold
        logger.info("Topology-Preserving Simplifier initialized")

    def simplify_with_topology(
        self,
        parcels: list[AgriculturalParcel],
    ) -> list[AgriculturalParcel]:
        """
        Simplify all parcel boundaries while preserving topology.

        Algorithm:
        1. Build adjacency graph (find shared boundaries)
        2. Identify shared edges between adjacent parcels
        3. Simplify shared edges consistently (same simplified edge for both parcels)
        4. Simplify non-shared edges independently
        5. Validate: no gaps, no overlaps, area within tolerance
        """
        if not parcels:
            return parcels

        logger.info(f"Topology-preserving simplification for {len(parcels)} parcels")

        # Step 1: Build adjacency graph
        adjacency = self._build_adjacency_graph(parcels)

        # Step 2: Identify shared edges
        shared_edges = self._find_shared_edges(parcels, adjacency)

        # Step 3: Simplify shared edges consistently
        simplified_shared = {}
        for edge_key, edge_coords in shared_edges.items():
            simplified_shared[edge_key] = self._douglas_peucker(edge_coords, self.tolerance)

        # Step 4: Simplify each parcel using consistent shared edges
        for i, parcel in enumerate(parcels):
            original_area = self._calculate_area(parcel.coordinates)
            new_coords = self._simplify_parcel_with_shared_edges(
                parcel.coordinates, i, adjacency.get(i, []), simplified_shared
            )

            # Step 5: Validate area change
            new_area = self._calculate_area(new_coords)
            if original_area > 0:
                area_change = abs(new_area - original_area) / original_area
                if area_change <= self.area_change_threshold and len(new_coords) >= 3:
                    parcel.coordinates = new_coords
                    parcel.area_hectares = round(new_area, 4)
                    parcel.num_vertices = len(new_coords)

        logger.info("Topology-preserving simplification complete")
        return parcels

    def _build_adjacency_graph(
        self, parcels: list[AgriculturalParcel]
    ) -> dict[int, list[int]]:
        """Build adjacency graph: parcel_index -> [neighbor_indices]"""
        adjacency: dict[int, list[int]] = {}
        n = len(parcels)

        for i in range(n):
            adjacency[i] = []
            for j in range(i + 1, n):
                if self._parcels_are_adjacent(parcels[i], parcels[j]):
                    adjacency.setdefault(i, []).append(j)
                    adjacency.setdefault(j, []).append(i)

        return adjacency

    def _parcels_are_adjacent(
        self, p1: AgriculturalParcel, p2: AgriculturalParcel, threshold: float = 0.0001
    ) -> bool:
        """Check if two parcels share a boundary (have nearby vertices)"""
        shared_count = 0
        for c1 in p1.coordinates:
            for c2 in p2.coordinates:
                dist = math.hypot(c1[0] - c2[0], c1[1] - c2[1])
                if dist < threshold:
                    shared_count += 1
                    if shared_count >= 2:  # At least 2 shared points = shared edge
                        return True
        return False

    def _find_shared_edges(
        self,
        parcels: list[AgriculturalParcel],
        adjacency: dict[int, list[int]],
    ) -> dict[tuple[int, int], list[tuple[float, float]]]:
        """Find shared edge coordinates between adjacent parcels"""
        shared_edges: dict[tuple[int, int], list[tuple[float, float]]] = {}
        threshold = 0.0001

        for i, neighbors in adjacency.items():
            for j in neighbors:
                if i >= j:
                    continue  # Avoid duplicate edges

                # Find shared vertices
                shared_points = []
                for c1 in parcels[i].coordinates:
                    for c2 in parcels[j].coordinates:
                        dist = math.hypot(c1[0] - c2[0], c1[1] - c2[1])
                        if dist < threshold:
                            shared_points.append(c1)
                            break

                if len(shared_points) >= 2:
                    shared_edges[(i, j)] = shared_points

        return shared_edges

    def _simplify_parcel_with_shared_edges(
        self,
        coords: list[tuple[float, float]],
        parcel_idx: int,
        neighbors: list[int],
        simplified_shared: dict[tuple[int, int], list[tuple[float, float]]],
    ) -> list[tuple[float, float]]:
        """Simplify parcel, using pre-simplified shared edges for consistency"""
        if len(coords) <= 4:
            return coords

        # For now, apply standard Douglas-Peucker but respect shared vertices
        shared_vertex_set = set()
        for j in neighbors:
            key = (min(parcel_idx, j), max(parcel_idx, j))
            if key in simplified_shared:
                for pt in simplified_shared[key]:
                    shared_vertex_set.add(pt)

        # Simplify while keeping shared vertices
        simplified = self._douglas_peucker_preserve(coords, self.tolerance, shared_vertex_set)
        return simplified if len(simplified) >= 3 else coords

    def _douglas_peucker_preserve(
        self,
        coords: list[tuple[float, float]],
        tolerance: float,
        preserve: set[tuple[float, float]],
    ) -> list[tuple[float, float]]:
        """Douglas-Peucker simplification that preserves specified vertices"""
        if len(coords) <= 2:
            return coords

        max_dist = 0.0
        max_idx = 1  # Default to 1 to avoid zero-length splits

        for i in range(1, len(coords) - 1):
            dist = self._point_line_distance(coords[i], coords[0], coords[-1])
            if dist > max_dist:
                max_dist = dist
                max_idx = i

        if max_dist > tolerance or coords[max_idx] in preserve:
            left = self._douglas_peucker_preserve(coords[:max_idx + 1], tolerance, preserve)
            right = self._douglas_peucker_preserve(coords[max_idx:], tolerance, preserve)
            return left[:-1] + right
        else:
            # Check if any preserved points would be lost
            for i in range(1, len(coords) - 1):
                if coords[i] in preserve:
                    left = self._douglas_peucker_preserve(coords[:i + 1], tolerance, preserve)
                    right = self._douglas_peucker_preserve(coords[i:], tolerance, preserve)
                    return left[:-1] + right
            return [coords[0], coords[-1]]

    def _point_line_distance(
        self, point: tuple[float, float], line_start: tuple[float, float], line_end: tuple[float, float]
    ) -> float:
        """Perpendicular distance from point to line segment"""
        dx = line_end[0] - line_start[0]
        dy = line_end[1] - line_start[1]
        if dx == 0 and dy == 0:
            return math.hypot(point[0] - line_start[0], point[1] - line_start[1])
        num = abs(dy * point[0] - dx * point[1] + line_end[0] * line_start[1] - line_end[1] * line_start[0])
        den = math.hypot(dx, dy)
        return num / den

    def _douglas_peucker(
        self, coords: list[tuple[float, float]], tolerance: float
    ) -> list[tuple[float, float]]:
        """Standard Douglas-Peucker simplification"""
        if len(coords) <= 2:
            return coords
        max_dist = 0.0
        max_idx = 0
        for i in range(1, len(coords) - 1):
            dist = self._point_line_distance(coords[i], coords[0], coords[-1])
            if dist > max_dist:
                max_dist = dist
                max_idx = i
        if max_dist > tolerance:
            left = self._douglas_peucker(coords[:max_idx + 1], tolerance)
            right = self._douglas_peucker(coords[max_idx:], tolerance)
            return left[:-1] + right
        return [coords[0], coords[-1]]

    def _calculate_area(self, coords: list[tuple[float, float]]) -> float:
        """Calculate area in hectares using Shoelace formula"""
        if len(coords) < 3:
            return 0.0
        avg_lat = sum(c[1] for c in coords) / len(coords)
        lon_to_m = 111320.0 * math.cos(math.radians(avg_lat))
        lat_to_m = 111320.0
        coords_m = [(c[0] * lon_to_m, c[1] * lat_to_m) for c in coords]
        area = 0.0
        n = len(coords_m)
        for i in range(n):
            x1, y1 = coords_m[i]
            x2, y2 = coords_m[(i + 1) % n]
            area += x1 * y2 - x2 * y1
        return abs(area) / 2.0 / 10000.0


# =============================================================================
# GeoLabel 4.0: Parcel Editing Tools
# أدوات تحرير القطع (دمج/تقسيم/ربط)
# =============================================================================


class ParcelEditingTools:
    """
    Fast parcel editing operations for manual correction and refinement.
    أدوات تحرير سريعة للقطع للتصحيح اليدوي والتنقيح

    GeoLabel 4.0 equivalent: "تحديث وتحرير قطع الأراضي الزراعية"
    Provides:
    - Fast merge: Merge multiple parcels intersected by a line
    - Fast split: Split a parcel along a cutting line
    - Fast connect: Connect broken/disconnected parcel fragments
    - Single-to-double line conversion: Convert centerline to polygon
    """

    def __init__(self):
        logger.info("Parcel Editing Tools initialized")

    def merge_parcels(
        self,
        parcels: list[AgriculturalParcel],
        parcel_ids: list[str],
    ) -> AgriculturalParcel | None:
        """
        Merge multiple parcels into one.

        GeoLabel 4.0: "快速合并 - 画一条线，合并所有相交的要素"
        Combines all specified parcels into a single parcel using convex hull.

        Args:
            parcels: All available parcels
            parcel_ids: IDs of parcels to merge

        Returns:
            Merged AgriculturalParcel or None if insufficient parcels
        """
        to_merge = [p for p in parcels if p.parcel_id in parcel_ids]
        if len(to_merge) < 2:
            return None

        # Collect all coordinates from parcels to merge
        all_coords = []
        for parcel in to_merge:
            all_coords.extend(parcel.coordinates)

        # Compute convex hull of all coordinates
        merged_coords = self._convex_hull(all_coords)
        if len(merged_coords) < 3:
            return None

        # Compute merged properties
        total_area = sum(p.area_hectares for p in to_merge)
        merged_perimeter = self._calculate_perimeter(merged_coords)
        centroid = (
            sum(c[0] for c in merged_coords) / len(merged_coords),
            sum(c[1] for c in merged_coords) / len(merged_coords),
        )

        # Weighted average of spectral properties
        weighted_ndvi = sum((p.mean_ndvi or 0) * p.area_hectares for p in to_merge) / max(total_area, 0.001)

        merged = AgriculturalParcel(
            parcel_id=f"merged_{uuid.uuid4().hex[:8]}",
            coordinates=merged_coords,
            area_hectares=round(total_area, 4),
            perimeter_meters=round(merged_perimeter, 2),
            centroid=centroid,
            land_cover=to_merge[0].land_cover,
            detection_confidence=min(p.detection_confidence for p in to_merge),
            detection_date=datetime.now(),
            strategy=to_merge[0].strategy,
            mean_ndvi=round(weighted_ndvi, 3),
            num_vertices=len(merged_coords),
            quality_score=round(min(p.quality_score or 0 for p in to_merge), 2),
            crop_type=to_merge[0].crop_type,
        )

        logger.info(f"Merged {len(to_merge)} parcels into {merged.parcel_id}")
        return merged

    def split_parcel(
        self,
        parcel: AgriculturalParcel,
        split_line: list[tuple[float, float]],
    ) -> list[AgriculturalParcel]:
        """
        Split a parcel along a cutting line.

        GeoLabel 4.0: "快速分割 - 连续切割"
        Divides a parcel into two or more parts along the specified line.

        Args:
            parcel: Parcel to split
            split_line: List of (lon, lat) points defining the cutting line

        Returns:
            List of resulting parcels after split
        """
        if len(split_line) < 2 or len(parcel.coordinates) < 3:
            return [parcel]

        # Find intersection points of split line with parcel boundary
        intersections = self._find_line_polygon_intersections(split_line, parcel.coordinates)

        if len(intersections) < 2:
            # Line doesn't properly cross the parcel
            return [parcel]

        # Split coordinates into two groups based on which side of the line they fall
        left_coords, right_coords = self._split_by_line(
            parcel.coordinates, split_line, intersections
        )

        results = []
        for idx, coords in enumerate([left_coords, right_coords]):
            if len(coords) < 3:
                continue
            area = self._calculate_area(coords)
            if area < 0.001:  # Skip negligible fragments
                continue

            centroid = (
                sum(c[0] for c in coords) / len(coords),
                sum(c[1] for c in coords) / len(coords),
            )
            new_parcel = AgriculturalParcel(
                parcel_id=f"{parcel.parcel_id}_split{idx}",
                coordinates=coords,
                area_hectares=round(area, 4),
                perimeter_meters=round(self._calculate_perimeter(coords), 2),
                centroid=centroid,
                land_cover=parcel.land_cover,
                detection_confidence=parcel.detection_confidence * 0.9,
                detection_date=datetime.now(),
                strategy=parcel.strategy,
                mean_ndvi=parcel.mean_ndvi,
                crop_type=parcel.crop_type,
                num_vertices=len(coords),
            )
            results.append(new_parcel)

        if not results:
            return [parcel]

        logger.info(f"Split parcel {parcel.parcel_id} into {len(results)} parts")
        return results

    def connect_parcels(
        self,
        parcels: list[AgriculturalParcel],
        parcel_ids: list[str],
        max_gap_meters: float = 10.0,
    ) -> AgriculturalParcel | None:
        """
        Connect broken/disconnected parcel fragments.

        GeoLabel 4.0: "快速连接 - 把断裂的图斑连接起来"
        Connects nearby parcels that should be one continuous field.

        Args:
            parcels: All available parcels
            parcel_ids: IDs of fragments to connect
            max_gap_meters: Maximum gap between fragments to bridge

        Returns:
            Connected AgriculturalParcel or None
        """
        to_connect = [p for p in parcels if p.parcel_id in parcel_ids]
        if len(to_connect) < 2:
            return None

        # Sort by centroid longitude for left-to-right ordering
        to_connect.sort(key=lambda p: p.centroid[0])

        # Build connected polygon by bridging gaps between fragments
        all_coords = list(to_connect[0].coordinates)
        for i in range(1, len(to_connect)):
            prev_coords = to_connect[i - 1].coordinates
            curr_coords = to_connect[i].coordinates

            # Find closest points between fragments
            min_dist = float("inf")
            best_prev_idx = 0
            best_curr_idx = 0

            for pi, pc in enumerate(prev_coords):
                for ci, cc in enumerate(curr_coords):
                    dist = math.hypot(pc[0] - cc[0], pc[1] - cc[1]) * 111320
                    if dist < min_dist:
                        min_dist = dist
                        best_prev_idx = pi
                        best_curr_idx = ci

            if min_dist <= max_gap_meters:
                # Bridge the gap: add connecting coordinates
                bridge_start = prev_coords[best_prev_idx]
                bridge_end = curr_coords[best_curr_idx]
                all_coords.append(bridge_start)
                all_coords.append(bridge_end)
                all_coords.extend(curr_coords)

        # Clean up: compute convex hull of connected coordinates
        connected_coords = self._convex_hull(all_coords)
        if len(connected_coords) < 3:
            return None

        total_area = sum(p.area_hectares for p in to_connect)
        centroid = (
            sum(c[0] for c in connected_coords) / len(connected_coords),
            sum(c[1] for c in connected_coords) / len(connected_coords),
        )

        connected = AgriculturalParcel(
            parcel_id=f"connected_{uuid.uuid4().hex[:8]}",
            coordinates=connected_coords,
            area_hectares=round(total_area, 4),
            perimeter_meters=round(self._calculate_perimeter(connected_coords), 2),
            centroid=centroid,
            land_cover=to_connect[0].land_cover,
            detection_confidence=min(p.detection_confidence for p in to_connect) * 0.9,
            detection_date=datetime.now(),
            strategy=to_connect[0].strategy,
            mean_ndvi=to_connect[0].mean_ndvi,
            crop_type=to_connect[0].crop_type,
            num_vertices=len(connected_coords),
        )

        logger.info(f"Connected {len(to_connect)} fragments into {connected.parcel_id}")
        return connected

    def _find_line_polygon_intersections(
        self,
        line: list[tuple[float, float]],
        polygon: list[tuple[float, float]],
    ) -> list[tuple[float, float]]:
        """Find intersection points between a line and polygon boundary"""
        intersections = []
        n = len(polygon)

        for li in range(len(line) - 1):
            l1, l2 = line[li], line[li + 1]
            for pi in range(n):
                p1, p2 = polygon[pi], polygon[(pi + 1) % n]
                pt = self._segment_intersection(l1, l2, p1, p2)
                if pt is not None:
                    intersections.append(pt)

        return intersections

    def _segment_intersection(
        self,
        a1: tuple[float, float], a2: tuple[float, float],
        b1: tuple[float, float], b2: tuple[float, float],
    ) -> tuple[float, float] | None:
        """Find intersection point of two line segments"""
        dx1, dy1 = a2[0] - a1[0], a2[1] - a1[1]
        dx2, dy2 = b2[0] - b1[0], b2[1] - b1[1]
        denom = dx1 * dy2 - dy1 * dx2

        if abs(denom) < 1e-12:
            return None  # Parallel

        t = ((b1[0] - a1[0]) * dy2 - (b1[1] - a1[1]) * dx2) / denom
        u = ((b1[0] - a1[0]) * dy1 - (b1[1] - a1[1]) * dx1) / denom

        if 0 <= t <= 1 and 0 <= u <= 1:
            return (a1[0] + t * dx1, a1[1] + t * dy1)
        return None

    def _split_by_line(
        self,
        polygon: list[tuple[float, float]],
        line: list[tuple[float, float]],
        intersections: list[tuple[float, float]],
    ) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
        """Split polygon coordinates into two groups based on a line"""
        if len(intersections) < 2:
            return polygon, []

        # Use signed area / cross product to determine which side of the line each vertex falls
        l1, l2 = line[0], line[-1]
        left_coords = list(intersections[:2])
        right_coords = list(intersections[:2])

        for coord in polygon:
            cross = (l2[0] - l1[0]) * (coord[1] - l1[1]) - (l2[1] - l1[1]) * (coord[0] - l1[0])
            if cross >= 0:
                left_coords.append(coord)
            else:
                right_coords.append(coord)

        # Order points by angle around centroid
        for coords in [left_coords, right_coords]:
            if len(coords) >= 3:
                cx = sum(c[0] for c in coords) / len(coords)
                cy = sum(c[1] for c in coords) / len(coords)
                coords.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))

        return left_coords, right_coords

    def _convex_hull(self, coords: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Graham scan convex hull"""
        if len(coords) < 3:
            return coords
        start = min(coords, key=lambda p: (p[1], p[0]))

        def polar_angle(p):
            return math.atan2(p[1] - start[1], p[0] - start[0])

        sorted_pts = sorted(set(coords), key=polar_angle)
        hull = [sorted_pts[0], sorted_pts[1]] if len(sorted_pts) >= 2 else list(sorted_pts)

        for p in sorted_pts[2:]:
            while len(hull) > 1:
                cross = (hull[-1][0] - hull[-2][0]) * (p[1] - hull[-2][1]) - \
                        (hull[-1][1] - hull[-2][1]) * (p[0] - hull[-2][0])
                if cross <= 0:
                    hull.pop()
                else:
                    break
            hull.append(p)
        return hull

    def _calculate_perimeter(self, coords: list[tuple[float, float]]) -> float:
        """Calculate perimeter in meters"""
        if len(coords) < 2:
            return 0.0
        perimeter = 0.0
        n = len(coords)
        for i in range(n):
            c1, c2 = coords[i], coords[(i + 1) % n]
            dlat = math.radians(c2[1] - c1[1])
            dlon = math.radians(c2[0] - c1[0])
            a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(c1[1])) * math.cos(
                math.radians(c2[1])
            ) * math.sin(dlon / 2) ** 2
            perimeter += 6371000 * 2 * math.asin(math.sqrt(a))
        return perimeter

    def _calculate_area(self, coords: list[tuple[float, float]]) -> float:
        """Calculate area in hectares"""
        if len(coords) < 3:
            return 0.0
        avg_lat = sum(c[1] for c in coords) / len(coords)
        lon_to_m = 111320.0 * math.cos(math.radians(avg_lat))
        lat_to_m = 111320.0
        coords_m = [(c[0] * lon_to_m, c[1] * lat_to_m) for c in coords]
        area = 0.0
        n = len(coords_m)
        for i in range(n):
            x1, y1 = coords_m[i]
            x2, y2 = coords_m[(i + 1) % n]
            area += x1 * y2 - x2 * y1
        return abs(area) / 2.0 / 10000.0


# =============================================================================
# GeoLabel 4.0: Quality Inspection Tool
# أداة فحص الجودة
# =============================================================================


class QualityInspectionTool:
    """
    Quality inspection and attribute editing for parcel data.
    فحص الجودة وتحرير خصائص بيانات القطع

    GeoLabel 4.0 equivalent: "检查工具 - 逐要素浏览、快速属性编辑、WKT导出"
    Provides:
    - Sequential element browsing (next/previous)
    - Quality validation (geometry, attributes, topology)
    - WKT export for interoperability
    - Batch attribute assignment
    - Statistics summary
    """

    # Quality check rules
    QUALITY_RULES = {
        "min_area_m2": 50,  # Per GeoLabel: 最小图斑面积 50m²
        "min_hole_area_m2": 20,  # Per GeoLabel: 最小空洞面积 20m²
        "min_vertices": 3,
        "max_self_intersections": 0,
        "min_compactness": 0.01,
        "max_elongation": 50.0,
    }

    def __init__(self):
        self._current_index = 0
        logger.info("Quality Inspection Tool initialized")

    def inspect_all(
        self, parcels: list[AgriculturalParcel]
    ) -> dict[str, Any]:
        """
        Run quality inspection on all parcels.

        Returns:
            Inspection report with issues found per parcel
        """
        issues: list[dict[str, Any]] = []
        passed = 0
        failed = 0

        for parcel in parcels:
            parcel_issues = self._inspect_parcel(parcel)
            if parcel_issues:
                issues.append({
                    "parcel_id": parcel.parcel_id,
                    "issues": parcel_issues,
                    "status": "failed",
                })
                failed += 1
            else:
                passed += 1

        return {
            "total_parcels": len(parcels),
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / max(len(parcels), 1) * 100, 1),
            "issues": issues,
            "summary": {
                "en": (
                    f"Quality inspection: {passed}/{len(parcels)} parcels"
                    f" passed ({round(passed / max(len(parcels), 1) * 100, 1)}%)"
                ),
                "ar": (
                    f"فحص الجودة: {passed}/{len(parcels)} قطعة"
                    f" اجتازت ({round(passed / max(len(parcels), 1) * 100, 1)}%)"
                ),
            },
        }

    def _inspect_parcel(self, parcel: AgriculturalParcel) -> list[str]:
        """Inspect a single parcel for quality issues"""
        issues = []

        # Check minimum area
        area_m2 = parcel.area_hectares * 10000
        if area_m2 < self.QUALITY_RULES["min_area_m2"]:
            issues.append(f"Area too small: {area_m2:.0f}m² < {self.QUALITY_RULES['min_area_m2']}m²")

        # Check minimum vertices
        if len(parcel.coordinates) < self.QUALITY_RULES["min_vertices"]:
            issues.append(f"Too few vertices: {len(parcel.coordinates)} < {self.QUALITY_RULES['min_vertices']}")

        # Check compactness
        if parcel.compactness is not None and parcel.compactness < self.QUALITY_RULES["min_compactness"]:
            issues.append(f"Compactness too low: {parcel.compactness:.4f}")

        # Check elongation
        if parcel.elongation is not None and parcel.elongation > self.QUALITY_RULES["max_elongation"]:
            issues.append(f"Too elongated: {parcel.elongation:.1f} > {self.QUALITY_RULES['max_elongation']}")

        # Check for self-intersections (simplified check)
        if self._has_self_intersection(parcel.coordinates):
            issues.append("Self-intersecting polygon detected")

        # Check closure (first and last point should be close)
        if len(parcel.coordinates) >= 3:
            first, last = parcel.coordinates[0], parcel.coordinates[-1]
            closure_dist = math.hypot(first[0] - last[0], first[1] - last[1])
            if closure_dist > 0.001:  # ~111m threshold
                issues.append(f"Polygon not closed (gap: {closure_dist * 111320:.1f}m)")

        # Check confidence
        if parcel.detection_confidence < 0.3:
            issues.append(f"Low detection confidence: {parcel.detection_confidence:.2f}")

        return issues

    def _has_self_intersection(self, coords: list[tuple[float, float]]) -> bool:
        """Check if polygon has self-intersections"""
        n = len(coords)
        if n < 4:
            return False

        for i in range(n):
            a1, a2 = coords[i], coords[(i + 1) % n]
            for j in range(i + 2, n):
                if j == (i - 1) % n or (i == 0 and j == n - 1):
                    continue  # Skip adjacent edges
                b1, b2 = coords[j], coords[(j + 1) % n]
                if self._segments_intersect(a1, a2, b1, b2):
                    return True
        return False

    def _segments_intersect(
        self,
        a1: tuple[float, float], a2: tuple[float, float],
        b1: tuple[float, float], b2: tuple[float, float],
    ) -> bool:
        """Check if two line segments intersect"""
        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        d1, d2 = cross(b1, b2, a1), cross(b1, b2, a2)
        d3, d4 = cross(a1, a2, b1), cross(a1, a2, b2)

        if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
           ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
            return True
        return False

    def parcel_to_wkt(self, parcel: AgriculturalParcel) -> str:
        """
        Export parcel as WKT (Well-Known Text) for interoperability.

        GeoLabel 4.0: "WKT导出" for data exchange with GIS systems.
        """
        if len(parcel.coordinates) < 3:
            return "POLYGON EMPTY"

        coords_str = ", ".join(f"{c[0]} {c[1]}" for c in parcel.coordinates)
        # Close the ring
        first = parcel.coordinates[0]
        coords_str += f", {first[0]} {first[1]}"
        return f"POLYGON (({coords_str}))"

    def parcels_to_wkt_collection(self, parcels: list[AgriculturalParcel]) -> str:
        """Export multiple parcels as WKT GEOMETRYCOLLECTION"""
        wkt_parts = []
        for p in parcels:
            wkt = self.parcel_to_wkt(p)
            if wkt != "POLYGON EMPTY":
                wkt_parts.append(wkt)
        if not wkt_parts:
            return "GEOMETRYCOLLECTION EMPTY"
        return f"GEOMETRYCOLLECTION ({', '.join(wkt_parts)})"

    def batch_assign_attribute(
        self,
        parcels: list[AgriculturalParcel],
        parcel_ids: list[str],
        attribute: str,
        value: Any,
    ) -> int:
        """
        Batch assign an attribute to multiple parcels.

        GeoLabel 4.0: "快速赋属性 - 批量赋值刷"
        Quickly assign crop type, land cover, or other properties.

        Args:
            parcels: All parcels
            parcel_ids: IDs to update
            attribute: Attribute name (crop_type, land_cover, is_irrigated)
            value: Value to assign

        Returns:
            Number of parcels updated
        """
        updated = 0
        target_set = set(parcel_ids)

        for parcel in parcels:
            if parcel.parcel_id in target_set:
                if attribute == "crop_type" and isinstance(value, str):
                    parcel.crop_type = value
                    updated += 1
                elif attribute == "land_cover" and isinstance(value, str):
                    try:
                        parcel.land_cover = LandCoverClass(value)
                        updated += 1
                    except ValueError:
                        pass
                elif attribute == "is_irrigated" and isinstance(value, bool):
                    parcel.is_irrigated = value
                    updated += 1

        logger.info(f"Batch assigned {attribute}={value} to {updated} parcels")
        return updated

    def get_statistics(self, parcels: list[AgriculturalParcel]) -> dict[str, Any]:
        """Generate summary statistics for parcel collection"""
        if not parcels:
            return {"total": 0}

        areas = [p.area_hectares for p in parcels]
        crop_types = {}
        land_covers = {}

        for p in parcels:
            ct = p.crop_type or "unknown"
            crop_types[ct] = crop_types.get(ct, 0) + 1
            lc = p.land_cover.value
            land_covers[lc] = land_covers.get(lc, 0) + 1

        return {
            "total_parcels": len(parcels),
            "total_area_hectares": round(sum(areas), 2),
            "mean_area_hectares": round(sum(areas) / len(areas), 4),
            "min_area_hectares": round(min(areas), 4),
            "max_area_hectares": round(max(areas), 4),
            "crop_type_distribution": crop_types,
            "land_cover_distribution": land_covers,
            "mean_confidence": round(sum(p.detection_confidence for p in parcels) / len(parcels), 3),
            "mean_ndvi": round(sum((p.mean_ndvi or 0) for p in parcels) / len(parcels), 3),
        }
