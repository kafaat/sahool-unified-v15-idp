"""
Terrain Indicator Calculator
حاسبة مؤشرات التضاريس

Calculates 7 key terrain indicators for agricultural analysis:
1. Slope (Horn's method) - الميل
2. Aspect - الجانب/الاتجاه
3. Flow Direction (D8 algorithm) - اتجاه التدفق
4. Flow Accumulation - تراكم التدفق
5. TWI (Topographic Wetness Index) - مؤشر الرطوبة الطبوغرافية
6. Curvature (plan and profile) - الانحناء
7. Contour Generation - إنشاء خطوط الكنتور
"""

from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import Any, Optional

import numpy as np
import structlog
from numpy.typing import NDArray

try:
    from scipy import ndimage
    from scipy.interpolate import interp2d

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from skimage import measure

    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False

from .dem_processor import DEMBounds, DEMData

logger = structlog.get_logger()


class SlopeUnit(StrEnum):
    """Slope measurement units | وحدات قياس الميل"""

    DEGREES = "degrees"
    PERCENT = "percent"
    RADIANS = "radians"


class FlowMethod(StrEnum):
    """Flow direction methods | طرق اتجاه التدفق"""

    D8 = "d8"
    DINF = "dinf"
    MFD = "mfd"


class CurvatureType(StrEnum):
    """Curvature types | أنواع الانحناء"""

    PLAN = "plan"
    PROFILE = "profile"
    TOTAL = "total"


@dataclass
class SlopeResult:
    """Slope calculation result | نتيجة حساب الميل"""

    data: NDArray[np.float32]
    unit: SlopeUnit
    min_value: float
    max_value: float
    mean_value: float
    std_value: float
    classification: dict[str, float]  # Percentage in each class


@dataclass
class AspectResult:
    """Aspect calculation result | نتيجة حساب الجانب"""

    data: NDArray[np.float32]  # In degrees, 0=North, clockwise
    dominant_direction: str
    distribution: dict[str, float]  # Percentage in each direction
    mean_aspect: float


@dataclass
class FlowDirectionResult:
    """Flow direction result | نتيجة اتجاه التدفق"""

    data: NDArray[np.int32]  # D8 coded: 1,2,4,8,16,32,64,128
    method: FlowMethod
    dominant_direction: str
    direction_distribution: dict[str, float]


@dataclass
class FlowAccumulationResult:
    """Flow accumulation result | نتيجة تراكم التدفق"""

    data: NDArray[np.float32]
    max_accumulation: int
    mean_accumulation: float
    drainage_density: float
    channel_pixels: int
    threshold: int
    streams: list[dict] | None  # GeoJSON features


@dataclass
class TWIResult:
    """Topographic Wetness Index result | نتيجة مؤشر الرطوبة الطبوغرافية"""

    data: NDArray[np.float32]
    min_twi: float
    max_twi: float
    mean_twi: float
    std_twi: float
    high_moisture_pct: float  # Percentage above threshold


@dataclass
class CurvatureResult:
    """Curvature calculation result | نتيجة حساب الانحناء"""

    data: NDArray[np.float32]
    curvature_type: CurvatureType
    min_value: float
    max_value: float
    mean_value: float
    convex_pct: float  # Positive curvature percentage
    concave_pct: float  # Negative curvature percentage
    flat_pct: float  # Near-zero curvature percentage


@dataclass
class ContourResult:
    """Contour generation result | نتيجة إنشاء خطوط الكنتور"""

    contours: list[dict]  # List of GeoJSON LineString features
    interval_m: float
    min_elevation: float
    max_elevation: float
    total_contours: int
    major_interval_m: float


class TerrainIndicatorCalculator:
    """
    Calculator for terrain morphometric indicators
    حاسبة مؤشرات التضاريس المورفومترية

    Implements standard terrain analysis algorithms for agricultural applications.
    """

    # D8 flow direction encoding (ArcGIS convention)
    # Direction: E=1, SE=2, S=4, SW=8, W=16, NW=32, N=64, NE=128
    D8_DIRECTIONS = {"E": 1, "SE": 2, "S": 4, "SW": 8, "W": 16, "NW": 32, "N": 64, "NE": 128}

    # D8 direction names in Arabic
    D8_DIRECTIONS_AR = {
        "E": "شرق",
        "SE": "جنوب شرق",
        "S": "جنوب",
        "SW": "جنوب غرب",
        "W": "غرب",
        "NW": "شمال غرب",
        "N": "شمال",
        "NE": "شمال شرق",
    }

    # Row/col offsets for 8 directions (E, SE, S, SW, W, NW, N, NE)
    D8_OFFSETS = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

    # Aspect direction classifications
    ASPECT_CLASSES = {
        "flat": (-1, -1),
        "N": (337.5, 22.5),
        "NE": (22.5, 67.5),
        "E": (67.5, 112.5),
        "SE": (112.5, 157.5),
        "S": (157.5, 202.5),
        "SW": (202.5, 247.5),
        "W": (247.5, 292.5),
        "NW": (292.5, 337.5),
    }

    # Slope classification thresholds (percent)
    SLOPE_CLASSES = {
        "flat": (0, 2),  # مسطح
        "gentle": (2, 5),  # لطيف
        "moderate": (5, 10),  # معتدل
        "steep": (10, 20),  # حاد
        "very_steep": (20, 100),  # حاد جداً
    }

    def __init__(
        self,
        cell_size_m: float = 30.0,
        nodata_value: float = -9999.0,
    ):
        """
        Initialize terrain calculator | تهيئة حاسبة التضاريس

        Args:
            cell_size_m: DEM cell size in meters | حجم الخلية بالأمتار
            nodata_value: NoData value | قيمة عدم وجود بيانات
        """
        self.cell_size_m = cell_size_m
        self.nodata_value = nodata_value

        logger.info(
            "Terrain indicator calculator initialized",
            cell_size_m=cell_size_m,
        )

    def calculate_slope(
        self,
        dem_data: DEMData,
        unit: SlopeUnit = SlopeUnit.DEGREES,
    ) -> SlopeResult:
        """
        Calculate slope using Horn's method (3x3 window)
        حساب الميل باستخدام طريقة هورن

        Horn's method provides better results than simple gradient calculation
        by using a weighted 3x3 kernel.

        Args:
            dem_data: Input DEM data | بيانات الارتفاعات المدخلة
            unit: Output slope unit | وحدة الميل الناتجة

        Returns:
            SlopeResult with slope array and statistics
        """
        logger.info("Calculating slope", unit=unit.value)

        elevation = dem_data.data.astype(np.float64)
        cell_size = dem_data.metadata.resolution_m or self.cell_size_m

        # Pad array for edge handling
        padded = np.pad(elevation, 1, mode="edge")

        # Extract 3x3 neighbors
        z1 = padded[:-2, :-2]  # NW
        z2 = padded[:-2, 1:-1]  # N
        z3 = padded[:-2, 2:]  # NE
        z4 = padded[1:-1, :-2]  # W
        # z5 = padded[1:-1, 1:-1]  # Center (not used)
        z6 = padded[1:-1, 2:]  # E
        z7 = padded[2:, :-2]  # SW
        z8 = padded[2:, 1:-1]  # S
        z9 = padded[2:, 2:]  # SE

        # Horn's method: weighted gradient
        dz_dx = ((z3 + 2 * z6 + z9) - (z1 + 2 * z4 + z7)) / (8 * cell_size)
        dz_dy = ((z7 + 2 * z8 + z9) - (z1 + 2 * z2 + z3)) / (8 * cell_size)

        # Calculate slope
        slope_radians = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))

        # Convert to requested unit
        if unit == SlopeUnit.DEGREES:
            slope = np.degrees(slope_radians)
        elif unit == SlopeUnit.PERCENT:
            slope = np.tan(slope_radians) * 100
        else:  # RADIANS
            slope = slope_radians

        slope = slope.astype(np.float32)

        # Mask nodata
        slope[dem_data.nodata_mask] = self.nodata_value

        # Calculate statistics (excluding nodata)
        valid_slope = slope[~dem_data.nodata_mask]
        min_slope = float(np.min(valid_slope))
        max_slope = float(np.max(valid_slope))
        mean_slope = float(np.mean(valid_slope))
        std_slope = float(np.std(valid_slope))

        # Calculate classification (using percent)
        if unit == SlopeUnit.DEGREES:
            slope_pct = np.tan(np.radians(valid_slope)) * 100
        elif unit == SlopeUnit.PERCENT:
            slope_pct = valid_slope
        else:
            slope_pct = np.tan(valid_slope) * 100

        classification = {}
        total_valid = len(slope_pct)
        for class_name, (low, high) in self.SLOPE_CLASSES.items():
            count = np.sum((slope_pct >= low) & (slope_pct < high))
            classification[class_name] = float(count / total_valid * 100)

        return SlopeResult(
            data=slope,
            unit=unit,
            min_value=min_slope,
            max_value=max_slope,
            mean_value=mean_slope,
            std_value=std_slope,
            classification=classification,
        )

    def calculate_aspect(
        self,
        dem_data: DEMData,
    ) -> AspectResult:
        """
        Calculate aspect (slope direction)
        حساب الجانب (اتجاه الميل)

        Args:
            dem_data: Input DEM data | بيانات الارتفاعات المدخلة

        Returns:
            AspectResult with aspect array in degrees (0=North, clockwise)
        """
        logger.info("Calculating aspect")

        elevation = dem_data.data.astype(np.float64)
        cell_size = dem_data.metadata.resolution_m or self.cell_size_m

        # Pad array for edge handling
        padded = np.pad(elevation, 1, mode="edge")

        # Extract neighbors
        z1 = padded[:-2, :-2]
        z2 = padded[:-2, 1:-1]
        z3 = padded[:-2, 2:]
        z4 = padded[1:-1, :-2]
        z6 = padded[1:-1, 2:]
        z7 = padded[2:, :-2]
        z8 = padded[2:, 1:-1]
        z9 = padded[2:, 2:]

        # Calculate gradients
        dz_dx = ((z3 + 2 * z6 + z9) - (z1 + 2 * z4 + z7)) / (8 * cell_size)
        dz_dy = ((z7 + 2 * z8 + z9) - (z1 + 2 * z2 + z3)) / (8 * cell_size)

        # Calculate aspect (in degrees, 0=North, clockwise)
        aspect = np.degrees(np.arctan2(dz_dy, -dz_dx))

        # Convert to 0-360 range (0=North)
        aspect = (90.0 - aspect) % 360.0

        # Mark flat areas (where slope is essentially zero)
        flat_mask = (np.abs(dz_dx) < 1e-10) & (np.abs(dz_dy) < 1e-10)
        aspect[flat_mask] = -1  # Convention for flat areas

        aspect = aspect.astype(np.float32)

        # Mask nodata
        aspect[dem_data.nodata_mask] = self.nodata_value

        # Calculate statistics
        valid_aspect = aspect[(~dem_data.nodata_mask) & (aspect >= 0)]
        mean_aspect = float(np.mean(valid_aspect)) if len(valid_aspect) > 0 else 0

        # Calculate direction distribution
        distribution = {"flat": 0.0}
        for direction in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]:
            distribution[direction] = 0.0

        total_valid = np.sum(~dem_data.nodata_mask)
        if total_valid > 0:
            # Flat areas
            distribution["flat"] = float(np.sum(flat_mask & ~dem_data.nodata_mask) / total_valid * 100)

            # Directional distribution
            for direction, (low, high) in self.ASPECT_CLASSES.items():
                if direction == "flat":
                    continue
                if direction == "N":
                    # North wraps around 360
                    count = np.sum((valid_aspect >= low) | (valid_aspect < high))
                else:
                    count = np.sum((valid_aspect >= low) & (valid_aspect < high))
                distribution[direction] = float(count / len(valid_aspect) * 100) if len(valid_aspect) > 0 else 0

        # Find dominant direction
        dominant = max(distribution.items(), key=lambda x: x[1])[0]

        return AspectResult(
            data=aspect,
            dominant_direction=dominant,
            distribution=distribution,
            mean_aspect=mean_aspect,
        )

    def calculate_flow_direction(
        self,
        dem_data: DEMData,
        method: FlowMethod = FlowMethod.D8,
    ) -> FlowDirectionResult:
        """
        Calculate flow direction using D8 algorithm
        حساب اتجاه التدفق باستخدام خوارزمية D8

        D8 assigns flow to one of 8 neighbors based on steepest descent.

        Args:
            dem_data: Input DEM data | بيانات الارتفاعات المدخلة
            method: Flow direction method | طريقة اتجاه التدفق

        Returns:
            FlowDirectionResult with coded direction array
        """
        logger.info("Calculating flow direction", method=method.value)

        elevation = dem_data.data.astype(np.float64)
        rows, cols = elevation.shape
        cell_size = dem_data.metadata.resolution_m or self.cell_size_m

        # D8 direction codes
        direction_codes = [1, 2, 4, 8, 16, 32, 64, 128]
        direction_names = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]

        # Distance weights for diagonal vs cardinal
        distances = [
            cell_size,
            cell_size * np.sqrt(2),
            cell_size,
            cell_size * np.sqrt(2),
            cell_size,
            cell_size * np.sqrt(2),
            cell_size,
            cell_size * np.sqrt(2),
        ]

        # Initialize flow direction array
        flow_dir = np.zeros((rows, cols), dtype=np.int32)

        # Pad elevation for neighbor access
        padded = np.pad(elevation, 1, mode="constant", constant_values=np.inf)

        # Calculate flow direction for each cell
        for i in range(rows):
            for j in range(cols):
                if dem_data.nodata_mask[i, j]:
                    flow_dir[i, j] = 0
                    continue

                center_elev = padded[i + 1, j + 1]
                max_drop = 0
                max_dir = 0

                for k, (di, dj) in enumerate(self.D8_OFFSETS):
                    neighbor_elev = padded[i + 1 + di, j + 1 + dj]
                    drop = (center_elev - neighbor_elev) / distances[k]

                    if drop > max_drop:
                        max_drop = drop
                        max_dir = direction_codes[k]

                flow_dir[i, j] = max_dir if max_dir > 0 else 0

        # Calculate direction distribution
        distribution = {}
        total_valid = np.sum(flow_dir > 0)

        for code, name in zip(direction_codes, direction_names):
            count = np.sum(flow_dir == code)
            distribution[name] = float(count / total_valid * 100) if total_valid > 0 else 0

        # Find dominant direction
        dominant = max(distribution.items(), key=lambda x: x[1])[0]

        return FlowDirectionResult(
            data=flow_dir,
            method=method,
            dominant_direction=dominant,
            direction_distribution=distribution,
        )

    def calculate_flow_accumulation(
        self,
        dem_data: DEMData,
        flow_direction: FlowDirectionResult,
        threshold: int = 100,
    ) -> FlowAccumulationResult:
        """
        Calculate flow accumulation (contributing area)
        حساب تراكم التدفق (المنطقة المساهمة)

        Args:
            dem_data: Input DEM data | بيانات الارتفاعات المدخلة
            flow_direction: Flow direction result | نتيجة اتجاه التدفق
            threshold: Threshold for channel extraction | عتبة استخراج القنوات

        Returns:
            FlowAccumulationResult with accumulation array
        """
        logger.info("Calculating flow accumulation", threshold=threshold)

        rows, cols = dem_data.data.shape
        flow_dir = flow_direction.data

        # Initialize accumulation (each cell starts with 1)
        accumulation = np.ones((rows, cols), dtype=np.float32)
        accumulation[dem_data.nodata_mask] = 0

        # Create processing order based on elevation (highest first)
        elevation = dem_data.data.copy()
        elevation[dem_data.nodata_mask] = -np.inf

        # Get sorted indices (highest elevation first)
        flat_indices = np.argsort(elevation.ravel())[::-1]

        # D8 direction to offset mapping
        dir_to_offset = {
            1: (0, 1),
            2: (1, 1),
            4: (1, 0),
            8: (1, -1),
            16: (0, -1),
            32: (-1, -1),
            64: (-1, 0),
            128: (-1, 1),
        }

        # Accumulate flow
        for flat_idx in flat_indices:
            i, j = divmod(flat_idx, cols)

            if dem_data.nodata_mask[i, j]:
                continue

            direction = flow_dir[i, j]
            if direction == 0:
                continue

            offset = dir_to_offset.get(direction)
            if offset:
                ni, nj = i + offset[0], j + offset[1]
                if 0 <= ni < rows and 0 <= nj < cols:
                    accumulation[ni, nj] += accumulation[i, j]

        # Mask nodata
        accumulation[dem_data.nodata_mask] = self.nodata_value

        # Calculate statistics
        valid_acc = accumulation[~dem_data.nodata_mask]
        max_acc = int(np.max(valid_acc))
        mean_acc = float(np.mean(valid_acc))

        # Channel pixels (above threshold)
        channel_mask = accumulation >= threshold
        channel_pixels = int(np.sum(channel_mask & ~dem_data.nodata_mask))

        # Drainage density (channel length / area)
        cell_area_km2 = (dem_data.metadata.resolution_m**2) / 1e6
        total_area_km2 = np.sum(~dem_data.nodata_mask) * cell_area_km2
        channel_length_km = channel_pixels * dem_data.metadata.resolution_m / 1000
        drainage_density = channel_length_km / total_area_km2 if total_area_km2 > 0 else 0

        # Extract stream network as GeoJSON (simplified)
        streams = self._extract_streams(accumulation, channel_mask, dem_data.metadata, dem_data.transform)

        return FlowAccumulationResult(
            data=accumulation,
            max_accumulation=max_acc,
            mean_accumulation=mean_acc,
            drainage_density=drainage_density,
            channel_pixels=channel_pixels,
            threshold=threshold,
            streams=streams,
        )

    def _extract_streams(
        self,
        accumulation: NDArray,
        channel_mask: NDArray,
        metadata,
        transform,
    ) -> list[dict]:
        """Extract stream network as GeoJSON features | استخراج شبكة المجاري"""
        # Simplified stream extraction - returns centroid points of high accumulation
        streams = []

        if not SCIPY_AVAILABLE:
            return streams

        # Label connected channel regions
        labeled, num_features = ndimage.label(channel_mask)

        for region_id in range(1, min(num_features + 1, 20)):  # Limit to 20 streams
            region_mask = labeled == region_id
            if np.sum(region_mask) < 10:  # Minimum stream length
                continue

            # Get coordinates of stream pixels
            y_coords, x_coords = np.where(region_mask)

            if len(x_coords) < 2:
                continue

            # Sort by accumulation (approximate flow line)
            acc_values = accumulation[y_coords, x_coords]
            sorted_idx = np.argsort(acc_values)
            x_coords = x_coords[sorted_idx]
            y_coords = y_coords[sorted_idx]

            # Convert pixel coordinates to geographic (simplified)
            if transform is not None:
                coords = [
                    [float(transform.c + x * transform.a), float(transform.f + y * transform.e)]
                    for x, y in zip(x_coords[::5], y_coords[::5])  # Sample every 5th point
                ]
            else:
                coords = [[float(x), float(y)] for x, y in zip(x_coords[::5], y_coords[::5])]

            if len(coords) >= 2:
                streams.append(
                    {
                        "type": "Feature",
                        "properties": {
                            "stream_id": region_id,
                            "length_pixels": len(x_coords),
                            "max_accumulation": float(np.max(acc_values)),
                        },
                        "geometry": {
                            "type": "LineString",
                            "coordinates": coords,
                        },
                    }
                )

        return streams

    def calculate_twi(
        self,
        dem_data: DEMData,
        slope_result: SlopeResult | None = None,
        flow_accumulation: FlowAccumulationResult | None = None,
    ) -> TWIResult:
        """
        Calculate Topographic Wetness Index (TWI)
        حساب مؤشر الرطوبة الطبوغرافية

        TWI = ln(a / tan(β))
        where a = specific catchment area, β = slope

        Higher TWI values indicate wetter conditions.

        Args:
            dem_data: Input DEM data | بيانات الارتفاعات المدخلة
            slope_result: Pre-calculated slope (optional) | الميل المحسوب مسبقاً
            flow_accumulation: Pre-calculated flow accumulation (optional)

        Returns:
            TWIResult with TWI array
        """
        logger.info("Calculating Topographic Wetness Index")

        # Calculate slope if not provided
        if slope_result is None:
            slope_result = self.calculate_slope(dem_data, unit=SlopeUnit.RADIANS)

        # Calculate flow accumulation if not provided
        if flow_accumulation is None:
            flow_dir = self.calculate_flow_direction(dem_data)
            flow_accumulation = self.calculate_flow_accumulation(dem_data, flow_dir)

        # Get slope in radians
        if slope_result.unit == SlopeUnit.DEGREES:
            slope_rad = np.radians(slope_result.data)
        elif slope_result.unit == SlopeUnit.PERCENT:
            slope_rad = np.arctan(slope_result.data / 100)
        else:
            slope_rad = slope_result.data

        # Calculate specific catchment area (contributing area per unit contour length)
        cell_size = dem_data.metadata.resolution_m or self.cell_size_m
        specific_area = flow_accumulation.data * cell_size

        # Calculate TWI
        # Avoid division by zero - use minimum slope
        min_slope = 0.001  # About 0.06 degrees
        tan_slope = np.maximum(np.tan(slope_rad), min_slope)

        twi = np.log(specific_area / tan_slope)

        # Handle infinities and NaN
        twi = np.clip(twi, -10, 30)  # Reasonable TWI range
        twi = twi.astype(np.float32)

        # Mask nodata
        twi[dem_data.nodata_mask] = self.nodata_value

        # Calculate statistics
        valid_twi = twi[~dem_data.nodata_mask]
        min_twi = float(np.min(valid_twi))
        max_twi = float(np.max(valid_twi))
        mean_twi = float(np.mean(valid_twi))
        std_twi = float(np.std(valid_twi))

        # High moisture areas (TWI > mean + std)
        high_threshold = mean_twi + std_twi
        high_moisture_pct = float(np.sum(valid_twi > high_threshold) / len(valid_twi) * 100)

        return TWIResult(
            data=twi,
            min_twi=min_twi,
            max_twi=max_twi,
            mean_twi=mean_twi,
            std_twi=std_twi,
            high_moisture_pct=high_moisture_pct,
        )

    def calculate_curvature(
        self,
        dem_data: DEMData,
        curvature_type: CurvatureType = CurvatureType.TOTAL,
    ) -> CurvatureResult:
        """
        Calculate terrain curvature
        حساب انحناء التضاريس

        Plan curvature: perpendicular to slope direction (affects flow convergence)
        Profile curvature: parallel to slope direction (affects flow acceleration)

        Args:
            dem_data: Input DEM data | بيانات الارتفاعات المدخلة
            curvature_type: Type of curvature to calculate | نوع الانحناء

        Returns:
            CurvatureResult with curvature array
        """
        logger.info("Calculating curvature", type=curvature_type.value)

        elevation = dem_data.data.astype(np.float64)
        cell_size = dem_data.metadata.resolution_m or self.cell_size_m

        # Pad for neighbor access
        padded = np.pad(elevation, 1, mode="edge")

        # Extract 3x3 neighbors
        z1 = padded[:-2, :-2]
        z2 = padded[:-2, 1:-1]
        z3 = padded[:-2, 2:]
        z4 = padded[1:-1, :-2]
        z5 = padded[1:-1, 1:-1]
        z6 = padded[1:-1, 2:]
        z7 = padded[2:, :-2]
        z8 = padded[2:, 1:-1]
        z9 = padded[2:, 2:]

        # Calculate second derivatives
        L = cell_size

        # dz/dx, dz/dy
        p = (z6 - z4) / (2 * L)
        q = (z2 - z8) / (2 * L)

        # d²z/dx², d²z/dy², d²z/dxdy
        r = (z6 - 2 * z5 + z4) / (L**2)
        t = (z2 - 2 * z5 + z8) / (L**2)
        s = (z3 - z1 - z9 + z7) / (4 * L**2)

        # Calculate curvature
        if curvature_type == CurvatureType.PLAN:
            # Plan curvature (horizontal)
            denominator = (p**2 + q**2) * np.sqrt(1 + p**2 + q**2)
            denominator = np.where(denominator < 1e-10, 1e-10, denominator)
            curvature = -(q**2 * r - 2 * p * q * s + p**2 * t) / denominator
        elif curvature_type == CurvatureType.PROFILE:
            # Profile curvature (vertical)
            denominator = (p**2 + q**2) * (1 + p**2 + q**2) ** 1.5
            denominator = np.where(denominator < 1e-10, 1e-10, denominator)
            curvature = -(p**2 * r + 2 * p * q * s + q**2 * t) / denominator
        else:  # TOTAL
            # Total/mean curvature
            curvature = -((r + t) / 2)

        curvature = curvature.astype(np.float32)

        # Mask nodata
        curvature[dem_data.nodata_mask] = self.nodata_value

        # Calculate statistics
        valid_curv = curvature[~dem_data.nodata_mask]
        min_curv = float(np.min(valid_curv))
        max_curv = float(np.max(valid_curv))
        mean_curv = float(np.mean(valid_curv))

        # Classification
        flat_threshold = 0.001
        convex_pct = float(np.sum(valid_curv > flat_threshold) / len(valid_curv) * 100)
        concave_pct = float(np.sum(valid_curv < -flat_threshold) / len(valid_curv) * 100)
        flat_pct = 100 - convex_pct - concave_pct

        return CurvatureResult(
            data=curvature,
            curvature_type=curvature_type,
            min_value=min_curv,
            max_value=max_curv,
            mean_value=mean_curv,
            convex_pct=convex_pct,
            concave_pct=concave_pct,
            flat_pct=flat_pct,
        )

    def generate_contours(
        self,
        dem_data: DEMData,
        interval_m: float = 5.0,
        min_elevation: float | None = None,
        max_elevation: float | None = None,
        simplify_tolerance: float = 1.0,
    ) -> ContourResult:
        """
        Generate contour lines from DEM
        إنشاء خطوط الكنتور من بيانات الارتفاعات

        Args:
            dem_data: Input DEM data | بيانات الارتفاعات المدخلة
            interval_m: Contour interval in meters | فترة الكنتور بالأمتار
            min_elevation: Minimum elevation for contours | أدنى ارتفاع
            max_elevation: Maximum elevation for contours | أقصى ارتفاع
            simplify_tolerance: Line simplification tolerance | تسامح التبسيط

        Returns:
            ContourResult with contour GeoJSON features
        """
        logger.info("Generating contours", interval_m=interval_m)

        elevation = dem_data.data.copy()
        elevation[dem_data.nodata_mask] = np.nan

        # Determine elevation range
        valid_elev = elevation[~np.isnan(elevation)]
        if min_elevation is None:
            min_elevation = float(np.floor(np.min(valid_elev) / interval_m) * interval_m)
        if max_elevation is None:
            max_elevation = float(np.ceil(np.max(valid_elev) / interval_m) * interval_m)

        # Generate contour levels
        levels = np.arange(min_elevation, max_elevation + interval_m, interval_m)

        # Major contour interval (every 5th contour)
        major_interval = interval_m * 5

        contours = []

        if SKIMAGE_AVAILABLE:
            for level in levels:
                # Find contours at this level
                try:
                    contour_coords = measure.find_contours(elevation, level)
                except Exception:
                    continue

                for coords in contour_coords:
                    if len(coords) < 3:
                        continue

                    # Convert pixel coordinates to geographic
                    if dem_data.transform is not None:
                        geo_coords = [
                            [
                                float(dem_data.transform.c + x * dem_data.transform.a),
                                float(dem_data.transform.f + y * dem_data.transform.e),
                            ]
                            for y, x in coords
                        ]
                    else:
                        geo_coords = [[float(x), float(y)] for y, x in coords]

                    # Simplify if requested
                    if simplify_tolerance > 0 and len(geo_coords) > 10:
                        geo_coords = geo_coords[:: int(simplify_tolerance * 2 + 1)]

                    if len(geo_coords) < 2:
                        continue

                    # Calculate length
                    length_m = 0
                    for i in range(len(geo_coords) - 1):
                        dx = geo_coords[i + 1][0] - geo_coords[i][0]
                        dy = geo_coords[i + 1][1] - geo_coords[i][1]
                        length_m += np.sqrt(dx**2 + dy**2) * 111320  # Approximate

                    is_major = (level % major_interval) < 0.01

                    contours.append(
                        {
                            "type": "Feature",
                            "properties": {
                                "elevation_m": float(level),
                                "length_m": float(length_m),
                                "is_major": is_major,
                            },
                            "geometry": {
                                "type": "LineString",
                                "coordinates": geo_coords,
                            },
                        }
                    )
        else:
            logger.warning("scikit-image not available, contour generation limited")

        return ContourResult(
            contours=contours,
            interval_m=interval_m,
            min_elevation=min_elevation,
            max_elevation=max_elevation,
            total_contours=len(contours),
            major_interval_m=major_interval,
        )

    def calculate_all_indicators(
        self,
        dem_data: DEMData,
        contour_interval_m: float = 5.0,
        flow_threshold: int = 100,
    ) -> dict[str, Any]:
        """
        Calculate all terrain indicators
        حساب جميع مؤشرات التضاريس

        Args:
            dem_data: Input DEM data | بيانات الارتفاعات المدخلة
            contour_interval_m: Contour interval | فترة الكنتور
            flow_threshold: Flow accumulation threshold | عتبة تراكم التدفق

        Returns:
            Dictionary with all indicator results
        """
        logger.info("Calculating all terrain indicators")

        results = {}

        # 1. Slope
        results["slope"] = self.calculate_slope(dem_data, SlopeUnit.DEGREES)

        # 2. Aspect
        results["aspect"] = self.calculate_aspect(dem_data)

        # 3. Flow Direction
        results["flow_direction"] = self.calculate_flow_direction(dem_data)

        # 4. Flow Accumulation
        results["flow_accumulation"] = self.calculate_flow_accumulation(
            dem_data, results["flow_direction"], threshold=flow_threshold
        )

        # 5. TWI
        slope_rad = self.calculate_slope(dem_data, SlopeUnit.RADIANS)
        results["twi"] = self.calculate_twi(dem_data, slope_rad, results["flow_accumulation"])

        # 6. Curvature (plan and profile)
        results["plan_curvature"] = self.calculate_curvature(dem_data, CurvatureType.PLAN)
        results["profile_curvature"] = self.calculate_curvature(dem_data, CurvatureType.PROFILE)

        # 7. Contours
        results["contours"] = self.generate_contours(dem_data, interval_m=contour_interval_m)

        return results
