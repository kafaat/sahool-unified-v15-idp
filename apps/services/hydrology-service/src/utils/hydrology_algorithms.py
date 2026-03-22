"""
Hydrology Algorithms for Agricultural Analysis
خوارزميات الهيدرولوجيا للتحليل الزراعي

Implements core hydrological calculations:
- Drainage network extraction using D8 flow direction
- Topographic Wetness Index (TWI) calculation
- Depression identification and filling
- Stream order calculation (Strahler method)
- Basin/watershed delineation

Reference:
- O'Callaghan & Mark (1984) - D8 Algorithm
- Beven & Kirkby (1979) - TOPMODEL / TWI
- Strahler (1957) - Stream ordering
"""

import math
import uuid
from dataclasses import dataclass, field
from typing import Any

import numpy as np

# ==============================================================================
# Data Structures
# ==============================================================================


@dataclass
class DEMData:
    """Digital Elevation Model data structure."""

    elevation: np.ndarray  # 2D elevation array
    resolution: float  # Cell resolution in meters
    nodata_value: float = -9999.0
    bounds: tuple[float, float, float, float] | None = None  # min_lon, min_lat, max_lon, max_lat

    @property
    def rows(self) -> int:
        return self.elevation.shape[0]

    @property
    def cols(self) -> int:
        return self.elevation.shape[1]

    @property
    def cell_area(self) -> float:
        """Cell area in square meters."""
        return self.resolution * self.resolution


@dataclass
class FlowData:
    """Flow direction and accumulation data."""

    direction: np.ndarray  # D8 flow direction (1-8, 0=pit)
    accumulation: np.ndarray  # Flow accumulation (cell count)
    slope: np.ndarray  # Slope in degrees


@dataclass
class DrainageSegmentData:
    """Data for a drainage segment."""

    segment_id: str
    cells: list[tuple[int, int]]  # List of (row, col) coordinates
    stream_order: int
    upstream_cells: int


@dataclass
class DepressionData:
    """Data for a depression/sink."""

    depression_id: str
    cells: list[tuple[int, int]]
    depth_m: float
    volume_m3: float
    spill_elevation: float


# ==============================================================================
# D8 Flow Direction Constants
# ==============================================================================

# D8 directions: 1=E, 2=SE, 4=S, 8=SW, 16=W, 32=NW, 64=N, 128=NE
D8_DIRECTIONS = {
    1: (0, 1),  # East
    2: (1, 1),  # Southeast
    4: (1, 0),  # South
    8: (1, -1),  # Southwest
    16: (0, -1),  # West
    32: (-1, -1),  # Northwest
    64: (-1, 0),  # North
    128: (-1, 1),  # Northeast
}

# Diagonal distance factor
SQRT2 = math.sqrt(2)


# ==============================================================================
# Core Algorithms
# ==============================================================================


def calculate_slope(dem: DEMData) -> np.ndarray:
    """
    Calculate slope from DEM using 3x3 neighborhood.
    حساب الميل من نموذج الارتفاع الرقمي

    Returns slope in degrees.
    """
    elev = dem.elevation
    res = dem.resolution

    # Pad array to handle edges
    padded = np.pad(elev, 1, mode="edge")

    # Calculate gradients using Sobel-like operators
    dz_dx = (
        (padded[:-2, 2:] + 2 * padded[1:-1, 2:] + padded[2:, 2:])
        - (padded[:-2, :-2] + 2 * padded[1:-1, :-2] + padded[2:, :-2])
    ) / (8 * res)

    dz_dy = (
        (padded[2:, :-2] + 2 * padded[2:, 1:-1] + padded[2:, 2:])
        - (padded[:-2, :-2] + 2 * padded[:-2, 1:-1] + padded[:-2, 2:])
    ) / (8 * res)

    # Calculate slope in degrees
    slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
    slope_deg = np.degrees(slope_rad)

    return slope_deg


def calculate_d8_flow_direction(dem: DEMData) -> np.ndarray:
    """
    Calculate D8 flow direction from DEM.
    حساب اتجاه التدفق D8

    Uses steepest descent to assign flow direction to each cell.
    Returns array with D8 direction codes (1, 2, 4, 8, 16, 32, 64, 128).
    """
    elev = dem.elevation
    rows, cols = elev.shape
    res = dem.resolution
    nodata = dem.nodata_value

    # Initialize flow direction array
    flow_dir = np.zeros((rows, cols), dtype=np.uint8)

    # D8 neighbor offsets and direction codes
    neighbors = [
        (0, 1, 1, res),  # E
        (1, 1, 2, res * SQRT2),  # SE
        (1, 0, 4, res),  # S
        (1, -1, 8, res * SQRT2),  # SW
        (0, -1, 16, res),  # W
        (-1, -1, 32, res * SQRT2),  # NW
        (-1, 0, 64, res),  # N
        (-1, 1, 128, res * SQRT2),  # NE
    ]

    for i in range(rows):
        for j in range(cols):
            if elev[i, j] == nodata:
                continue

            max_drop = 0
            max_dir = 0

            for di, dj, direction, dist in neighbors:
                ni, nj = i + di, j + dj

                # Check bounds
                if 0 <= ni < rows and 0 <= nj < cols:
                    if elev[ni, nj] != nodata:
                        drop = (elev[i, j] - elev[ni, nj]) / dist
                        if drop > max_drop:
                            max_drop = drop
                            max_dir = direction

            flow_dir[i, j] = max_dir

    return flow_dir


def calculate_flow_accumulation(dem: DEMData, flow_dir: np.ndarray) -> np.ndarray:
    """
    Calculate flow accumulation from flow direction.
    حساب تراكم التدفق

    Each cell contains the count of upstream cells that flow into it.
    """
    rows, cols = dem.elevation.shape
    accumulation = np.ones((rows, cols), dtype=np.int32)
    nodata = dem.nodata_value

    # Sort cells by elevation (highest first)
    valid_mask = dem.elevation != nodata
    valid_indices = np.argwhere(valid_mask)
    elevations = dem.elevation[valid_mask]
    sorted_indices = valid_indices[np.argsort(-elevations)]

    # Process from highest to lowest
    for idx in sorted_indices:
        i, j = idx[0], idx[1]
        direction = flow_dir[i, j]

        if direction == 0:
            continue

        if direction in D8_DIRECTIONS:
            di, dj = D8_DIRECTIONS[direction]
            ni, nj = i + di, j + dj

            if 0 <= ni < rows and 0 <= nj < cols:
                accumulation[ni, nj] += accumulation[i, j]

    return accumulation


def calculate_topographic_wetness_index(dem: DEMData, flow_accumulation: np.ndarray, slope: np.ndarray) -> np.ndarray:
    """
    Calculate Topographic Wetness Index (TWI).
    حساب مؤشر الرطوبة الطبوغرافي

    TWI = ln(a / tan(β))
    where:
        a = specific catchment area (upstream area per unit contour length)
        β = local slope angle

    Higher TWI values indicate wetter areas.
    """
    # Calculate specific catchment area
    # a = (flow_accumulation * cell_area) / cell_width
    cell_area = dem.cell_area
    sca = (flow_accumulation * cell_area) / dem.resolution

    # Convert slope to radians and prevent division by zero
    slope_rad = np.radians(slope)
    tan_slope = np.tan(slope_rad)
    tan_slope = np.maximum(tan_slope, 0.001)  # Minimum slope

    # Calculate TWI
    twi = np.log(sca / tan_slope)

    # Clip extreme values
    twi = np.clip(twi, -5, 30)

    return twi


def fill_depressions(dem: DEMData, max_depth: float = 2.0) -> tuple[np.ndarray, list[DepressionData]]:
    """
    Fill depressions/sinks in DEM.
    ملء المنخفضات في نموذج الارتفاع

    Returns filled DEM and list of identified depressions.
    Uses a simplified breach/fill algorithm.
    """
    filled = dem.elevation.copy()
    rows, cols = filled.shape
    nodata = dem.nodata_value
    cell_area = dem.cell_area

    depressions = []

    # Find local minima (potential depressions)
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            if filled[i, j] == nodata:
                continue

            # Get neighborhood
            neighborhood = filled[i - 1 : i + 2, j - 1 : j + 2].copy()
            center_val = neighborhood[1, 1]
            neighborhood[1, 1] = nodata  # Exclude center from neighbor calculation
            valid_neighbors = neighborhood[neighborhood != nodata]
            neighborhood[1, 1] = center_val  # Restore

            if len(valid_neighbors) == 0:
                continue

            center_elev = filled[i, j]
            min_neighbor = np.min(valid_neighbors)

            # Check if this is a depression (lower than all neighbors)
            if center_elev < min_neighbor:
                depth = min_neighbor - center_elev

                if depth <= max_depth:
                    # Fill the depression
                    filled[i, j] = min_neighbor

                    # Record the depression
                    volume = depth * cell_area
                    depressions.append(
                        DepressionData(
                            depression_id=str(uuid.uuid4())[:8],
                            cells=[(i, j)],
                            depth_m=depth,
                            volume_m3=volume,
                            spill_elevation=min_neighbor,
                        )
                    )

    return filled, depressions


def calculate_stream_order(flow_accumulation: np.ndarray, flow_dir: np.ndarray, threshold: int = 100) -> np.ndarray:
    """
    Calculate Strahler stream order.
    حساب رتبة المجرى (طريقة ستراهلر)

    Rules:
    - A stream with no tributaries is order 1
    - When two streams of same order join, order increases by 1
    - When two streams of different order join, higher order continues
    """
    rows, cols = flow_accumulation.shape
    order = np.zeros((rows, cols), dtype=np.int8)

    # Create stream mask
    stream_mask = flow_accumulation >= threshold

    # Find stream cells
    stream_cells = np.argwhere(stream_mask)

    if len(stream_cells) == 0:
        return order

    # Sort by flow accumulation (lowest first - headwaters)
    accumulations = flow_accumulation[stream_mask]
    sorted_indices = stream_cells[np.argsort(accumulations)]

    # Initialize headwaters as order 1
    for idx in sorted_indices:
        i, j = idx[0], idx[1]
        if order[i, j] == 0:
            order[i, j] = 1

    # Build upstream connectivity for Strahler calculation
    # Process from headwaters downstream
    for idx in sorted_indices:
        i, j = idx[0], idx[1]

        if not stream_mask[i, j]:
            continue

        direction = flow_dir[i, j]
        if direction == 0 or direction not in D8_DIRECTIONS:
            continue

        di, dj = D8_DIRECTIONS[direction]
        ni, nj = i + di, j + dj

        if 0 <= ni < rows and 0 <= nj < cols and stream_mask[ni, nj]:
            current_order = order[i, j]
            downstream_order = order[ni, nj]

            if current_order == downstream_order:
                order[ni, nj] = current_order + 1
            elif current_order > downstream_order:
                order[ni, nj] = current_order

    return order


def extract_drainage_network(
    dem: DEMData, flow_dir: np.ndarray, flow_accumulation: np.ndarray, threshold: int = 100
) -> list[DrainageSegmentData]:
    """
    Extract drainage network as line segments.
    استخراج شبكة التصريف كخطوط

    Returns list of drainage segments with their properties.
    """
    rows, cols = flow_accumulation.shape
    stream_mask = flow_accumulation >= threshold
    stream_order = calculate_stream_order(flow_accumulation, flow_dir, threshold)

    segments = []
    visited = np.zeros((rows, cols), dtype=bool)

    # Find headwaters (stream cells with no upstream stream cells)
    for i in range(rows):
        for j in range(cols):
            if not stream_mask[i, j] or visited[i, j]:
                continue

            # Check if this is a headwater
            is_headwater = True
            for direction, (di, dj) in D8_DIRECTIONS.items():
                ni, nj = i - di, j - dj  # Check upstream
                if 0 <= ni < rows and 0 <= nj < cols:
                    if stream_mask[ni, nj]:
                        upstream_dir = flow_dir[ni, nj]
                        if upstream_dir == direction:
                            is_headwater = False
                            break

            if not is_headwater:
                continue

            # Trace downstream from headwater
            cells = []
            ci, cj = i, j
            segment_order = stream_order[i, j]

            while 0 <= ci < rows and 0 <= cj < cols:
                if not stream_mask[ci, cj] or visited[ci, cj]:
                    break

                cells.append((ci, cj))
                visited[ci, cj] = True

                direction = flow_dir[ci, cj]
                if direction == 0 or direction not in D8_DIRECTIONS:
                    break

                di, dj = D8_DIRECTIONS[direction]
                ni, nj = ci + di, cj + dj

                # Check for order change (confluence)
                if 0 <= ni < rows and 0 <= nj < cols:
                    if stream_order[ni, nj] > segment_order:
                        break

                ci, cj = ni, nj

            if len(cells) > 1:
                segments.append(
                    DrainageSegmentData(
                        segment_id=str(uuid.uuid4())[:8],
                        cells=cells,
                        stream_order=segment_order,
                        upstream_cells=int(flow_accumulation[cells[0][0], cells[0][1]]),
                    )
                )

    return segments


def classify_drainage_pattern(dem: DEMData, flow_dir: np.ndarray, slope: np.ndarray) -> str:
    """
    Classify drainage pattern based on flow directions and terrain.
    تصنيف نمط التصريف

    Returns one of: dendritic, parallel, trellis, rectangular, radial, centripetal, deranged
    """
    rows, cols = flow_dir.shape

    # Count flow directions
    direction_counts = {}
    for d in D8_DIRECTIONS:
        direction_counts[d] = np.sum(flow_dir == d)

    total_cells = np.sum(flow_dir > 0)
    if total_cells == 0:
        return "unknown"

    # Calculate direction uniformity
    max_dir_count = max(direction_counts.values())
    uniformity = max_dir_count / total_cells

    # Calculate slope statistics
    mean_slope = np.mean(slope[slope > 0])

    # Simple classification rules
    if uniformity > 0.5:
        return "parallel"  # Dominant single direction
    elif mean_slope < 2:
        return "deranged"  # Flat terrain, irregular pattern
    elif uniformity > 0.3:
        return "trellis"  # Moderate uniformity with variation
    else:
        return "dendritic"  # Tree-like branching pattern


def delineate_basins(
    dem: DEMData, flow_dir: np.ndarray, flow_accumulation: np.ndarray, min_area_cells: int = 100
) -> list[dict[str, Any]]:
    """
    Delineate drainage basins/watersheds.
    تحديد أحواض التصريف

    Returns list of basin dictionaries with properties.
    """
    rows, cols = flow_dir.shape
    nodata = dem.nodata_value

    # Find outlets (cells that flow out of the domain or into nodata)
    outlets = []
    for i in range(rows):
        for j in range(cols):
            if dem.elevation[i, j] == nodata:
                continue

            direction = flow_dir[i, j]
            if direction == 0:
                outlets.append((i, j))
                continue

            if direction in D8_DIRECTIONS:
                di, dj = D8_DIRECTIONS[direction]
                ni, nj = i + di, j + dj

                # Check if flows outside domain or to nodata
                if ni < 0 or ni >= rows or nj < 0 or nj >= cols or dem.elevation[ni, nj] == nodata:
                    outlets.append((i, j))

    # For each outlet with sufficient accumulation, delineate watershed
    basins = []
    basin_id = 0

    for oi, oj in outlets:
        if flow_accumulation[oi, oj] < min_area_cells:
            continue

        # Trace upstream to find all contributing cells
        basin_cells = set()
        to_process = [(oi, oj)]

        while to_process:
            ci, cj = to_process.pop()
            if (ci, cj) in basin_cells:
                continue
            basin_cells.add((ci, cj))

            # Find all cells that flow into this cell
            for direction, (di, dj) in D8_DIRECTIONS.items():
                ni, nj = ci - di, cj - dj
                if 0 <= ni < rows and 0 <= nj < cols:
                    if flow_dir[ni, nj] == direction:
                        if (ni, nj) not in basin_cells:
                            to_process.append((ni, nj))

        if len(basin_cells) < min_area_cells:
            continue

        # Calculate basin properties
        cells_list = list(basin_cells)
        elevations = [dem.elevation[c[0], c[1]] for c in cells_list]

        basin_id += 1
        basins.append(
            {
                "basin_id": f"basin_{basin_id:03d}",
                "outlet": (oi, oj),
                "cells": cells_list,
                "cell_count": len(basin_cells),
                "area_ha": len(basin_cells) * dem.cell_area / 10000,
                "mean_elevation": np.mean(elevations),
                "min_elevation": np.min(elevations),
                "max_elevation": np.max(elevations),
            }
        )

    return basins


# ==============================================================================
# Helper Functions
# ==============================================================================


def cells_to_coordinates(cells: list[tuple[int, int]], dem: DEMData) -> list[list[float]]:
    """Convert cell indices to geographic coordinates."""
    if dem.bounds is None:
        # Return pixel coordinates if no bounds
        return [[c[1], c[0]] for c in cells]

    min_lon, min_lat, max_lon, max_lat = dem.bounds
    lon_res = (max_lon - min_lon) / dem.cols
    lat_res = (max_lat - min_lat) / dem.rows

    coordinates = []
    for row, col in cells:
        lon = min_lon + (col + 0.5) * lon_res
        lat = max_lat - (row + 0.5) * lat_res  # Flip lat (row 0 is top)
        coordinates.append([lon, lat])

    return coordinates


def generate_mock_dem(
    rows: int = 100,
    cols: int = 100,
    resolution: float = 30.0,
    base_elevation: float = 100.0,
    relief: float = 50.0,
    bounds: tuple[float, float, float, float] | None = None,
) -> DEMData:
    """
    Generate a synthetic DEM for testing.
    توليد نموذج ارتفاع رقمي اصطناعي للاختبار
    """
    # Create terrain with a valley pattern
    x = np.linspace(0, 4 * np.pi, cols)
    y = np.linspace(0, 4 * np.pi, rows)
    X, Y = np.meshgrid(x, y)

    # Base terrain: tilted plane with sine variation
    elevation = base_elevation + relief * (
        0.5 * (Y / Y.max())  # Slope from north to south
        + 0.3 * np.sin(X) * np.cos(Y)  # Hills
        + 0.2 * np.random.random((rows, cols))  # Noise
    )

    return DEMData(
        elevation=elevation.astype(np.float32),
        resolution=resolution,
        bounds=bounds,
    )


# ==============================================================================
# High-Level Analysis Class
# ==============================================================================


@dataclass
class HydrologyAnalyzer:
    """
    High-level hydrology analysis orchestrator.
    محلل الهيدرولوجيا عالي المستوى
    """

    dem: DEMData | None = None
    flow_data: FlowData | None = None
    twi: np.ndarray | None = None
    depressions: list[DepressionData] = field(default_factory=list)
    drainage_segments: list[DrainageSegmentData] = field(default_factory=list)
    basins: list[dict[str, Any]] = field(default_factory=list)

    def load_dem(self, dem_data: DEMData) -> None:
        """Load DEM data for analysis."""
        self.dem = dem_data

    def run_full_analysis(
        self,
        flow_threshold: int = 100,
        depression_max_depth: float = 2.0,
        min_basin_cells: int = 100,
    ) -> dict[str, Any]:
        """
        Run complete hydrology analysis.
        تشغيل تحليل هيدرولوجي كامل
        """
        if self.dem is None:
            raise ValueError("DEM data not loaded")

        # Step 1: Fill depressions
        filled_elev, self.depressions = fill_depressions(self.dem, max_depth=depression_max_depth)
        filled_dem = DEMData(
            elevation=filled_elev,
            resolution=self.dem.resolution,
            bounds=self.dem.bounds,
        )

        # Step 2: Calculate slope
        slope = calculate_slope(filled_dem)

        # Step 3: Calculate flow direction
        flow_dir = calculate_d8_flow_direction(filled_dem)

        # Step 4: Calculate flow accumulation
        flow_acc = calculate_flow_accumulation(filled_dem, flow_dir)

        # Store flow data
        self.flow_data = FlowData(
            direction=flow_dir,
            accumulation=flow_acc,
            slope=slope,
        )

        # Step 5: Calculate TWI
        self.twi = calculate_topographic_wetness_index(filled_dem, flow_acc, slope)

        # Step 6: Extract drainage network
        self.drainage_segments = extract_drainage_network(filled_dem, flow_dir, flow_acc, threshold=flow_threshold)

        # Step 7: Classify drainage pattern
        drainage_pattern = classify_drainage_pattern(filled_dem, flow_dir, slope)

        # Step 8: Delineate basins
        self.basins = delineate_basins(filled_dem, flow_dir, flow_acc, min_area_cells=min_basin_cells)

        # Compile results
        return {
            "dem_stats": {
                "rows": self.dem.rows,
                "cols": self.dem.cols,
                "resolution_m": self.dem.resolution,
                "mean_elevation": float(np.mean(self.dem.elevation[self.dem.elevation != self.dem.nodata_value])),
                "min_elevation": float(np.min(self.dem.elevation[self.dem.elevation != self.dem.nodata_value])),
                "max_elevation": float(np.max(self.dem.elevation[self.dem.elevation != self.dem.nodata_value])),
            },
            "slope_stats": {
                "mean_slope_deg": float(np.mean(slope)),
                "max_slope_deg": float(np.max(slope)),
            },
            "twi_stats": {
                "mean_twi": float(np.mean(self.twi)),
                "min_twi": float(np.min(self.twi)),
                "max_twi": float(np.max(self.twi)),
            },
            "drainage": {
                "pattern": drainage_pattern,
                "segment_count": len(self.drainage_segments),
                "total_length_cells": sum(len(s.cells) for s in self.drainage_segments),
            },
            "depressions": {
                "count": len(self.depressions),
                "total_volume_m3": sum(d.volume_m3 for d in self.depressions),
            },
            "basins": {
                "count": len(self.basins),
                "total_area_ha": sum(b["area_ha"] for b in self.basins),
            },
        }

    def get_wetness_zones(self, thresholds: tuple[float, ...] = (5.0, 8.0, 10.0, 12.0, 15.0)) -> list[dict[str, Any]]:
        """
        Classify wetness zones based on TWI thresholds.
        تصنيف مناطق الرطوبة
        """
        if self.twi is None:
            raise ValueError("TWI not calculated. Run analysis first.")

        zones = []
        labels = ["very_dry", "dry", "moderate", "wet", "very_wet", "waterlogged"]
        labels_ar = ["جاف جداً", "جاف", "معتدل", "رطب", "رطب جداً", "مشبع"]

        all_thresholds = [-float("inf")] + list(thresholds) + [float("inf")]

        total_cells = np.sum(self.twi > -float("inf"))

        for i in range(len(labels)):
            lower = all_thresholds[i]
            upper = all_thresholds[i + 1]

            mask = (self.twi >= lower) & (self.twi < upper)
            cell_count = np.sum(mask)

            if cell_count > 0:
                zones.append(
                    {
                        "level": labels[i],
                        "level_ar": labels_ar[i],
                        "cell_count": int(cell_count),
                        "percentage": float(cell_count / total_cells * 100),
                        "twi_range": (lower, upper),
                        "area_ha": float(cell_count * self.dem.cell_area / 10000) if self.dem else 0,
                    }
                )

        return zones
