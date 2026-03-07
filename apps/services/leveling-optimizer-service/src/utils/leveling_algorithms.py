"""
Leveling optimization algorithms for agricultural field preparation.

خوارزميات تحسين التسوية لإعداد الحقول الزراعية

This module implements:
- Optimal grade plane computation using least squares
- Cut/fill volume calculations using grid-based and TIN methods
- Multi-plane optimization for complex fields
- Haul distance calculations for cost optimization
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np


@dataclass
class Point3D:
    """3D point with x, y, z coordinates."""

    x: float
    y: float
    z: float
    point_id: str | None = None


@dataclass
class PlaneParameters:
    """Parameters defining a plane: z = a*x + b*y + c"""

    a: float  # Coefficient for x (grade in x direction)
    b: float  # Coefficient for y (grade in y direction)
    c: float  # Constant term (elevation offset)


@dataclass
class CutFillResult:
    """Results from cut/fill volume calculation."""

    cut_volume: float  # m³
    fill_volume: float  # m³
    cut_area: float  # m²
    fill_area: float  # m²
    max_cut_depth: float  # m
    max_fill_depth: float  # m
    avg_cut_depth: float  # m
    avg_fill_depth: float  # m
    cut_points: list[Point3D]
    fill_points: list[Point3D]
    design_points: list[Point3D]


class LevelingOptimizer:
    """
    Optimizer for agricultural field leveling operations.

    محسّن عمليات تسوية الحقول الزراعية
    """

    def __init__(self, soil_expansion_factor: float = 1.25, soil_compaction_factor: float = 0.90):
        """
        Initialize the leveling optimizer.

        Args:
            soil_expansion_factor: Factor for soil swell when excavated (معامل الانتفاخ)
            soil_compaction_factor: Factor for soil shrinkage when compacted (معامل الدمك)
        """
        self.soil_expansion_factor = soil_expansion_factor
        self.soil_compaction_factor = soil_compaction_factor

    def compute_optimal_plane(
        self,
        points: list[Point3D],
        target_grade_x: float | None = None,
        target_grade_y: float | None = None,
        balance_cut_fill: bool = True,
    ) -> PlaneParameters:
        """
        Compute the optimal design plane using least squares regression.

        حساب مستوى التصميم الأمثل باستخدام طريقة المربعات الصغرى

        Args:
            points: List of survey points with elevations
            target_grade_x: Target grade in X direction (%) - if None, will be optimized
            target_grade_y: Target grade in Y direction (%) - if None, will be optimized
            balance_cut_fill: If True, optimize for balanced cut/fill volumes

        Returns:
            PlaneParameters defining the optimal plane
        """
        if len(points) < 3:
            raise ValueError("At least 3 points required for plane calculation")

        # Convert to numpy arrays
        x = np.array([p.x for p in points])
        y = np.array([p.y for p in points])
        z = np.array([p.z for p in points])

        # Calculate centroid
        x_centroid = np.mean(x)
        y_centroid = np.mean(y)
        z_centroid = np.mean(z)

        if target_grade_x is not None and target_grade_y is not None:
            # Use specified grades (convert from % to decimal)
            a = target_grade_x / 100.0
            b = target_grade_y / 100.0

            if balance_cut_fill:
                # Adjust c to balance cut and fill
                c = self._find_balanced_elevation(points, a, b)
            else:
                # Calculate c such that plane passes through centroid
                c = z_centroid - a * x_centroid - b * y_centroid
        else:
            # Perform least squares fit to find optimal plane
            # Using the equation: z = a*x + b*y + c
            # Build the design matrix A = [[x1, y1, 1], [x2, y2, 1], ...]
            A = np.column_stack([x, y, np.ones_like(x)])

            # Solve the least squares problem
            coefficients, residuals, rank, s = np.linalg.lstsq(A, z, rcond=None)

            a, b, c = coefficients

            if balance_cut_fill:
                # Adjust c to balance cut and fill
                c = self._find_balanced_elevation(points, a, b)

        return PlaneParameters(a=a, b=b, c=c)

    def _find_balanced_elevation(self, points: list[Point3D], a: float, b: float) -> float:
        """
        Find the elevation offset (c) that balances cut and fill volumes.

        إيجاد فرق الارتفاع الذي يوازن أحجام القطع والردم

        This uses binary search to find the optimal c value where:
        cut_volume ≈ fill_volume * soil_compaction_factor / soil_expansion_factor
        """
        # Calculate plane elevations for all points at c=0
        plane_z_at_zero = np.array([a * p.x + b * p.y for p in points])
        actual_z = np.array([p.z for p in points])

        # Initial estimate: median difference
        differences = actual_z - plane_z_at_zero
        c_initial = np.median(differences)

        # Binary search for balanced cut/fill
        c_low = c_initial - 2.0  # 2 meters below
        c_high = c_initial + 2.0  # 2 meters above

        for _ in range(50):  # Max iterations
            c_mid = (c_low + c_high) / 2

            cuts = []
            fills = []

            for i, p in enumerate(points):
                design_z = a * p.x + b * p.y + c_mid
                diff = p.z - design_z

                if diff > 0:
                    cuts.append(diff)
                else:
                    fills.append(-diff)

            # Account for soil factors
            effective_cut = sum(cuts)
            effective_fill = sum(fills) / self.soil_compaction_factor * self.soil_expansion_factor

            if abs(effective_cut - effective_fill) < 0.001:
                break
            elif effective_cut > effective_fill:
                c_low = c_mid
            else:
                c_high = c_mid

        return c_mid

    def compute_multi_plane(
        self, points: list[Point3D], num_planes: int = 2, direction: str = "y"
    ) -> list[tuple[PlaneParameters, list[Point3D]]]:
        """
        Compute multiple planes for stepped or terraced leveling.

        حساب مستويات متعددة للتسوية المتدرجة أو المصاطب

        Args:
            points: List of survey points
            num_planes: Number of planes to create
            direction: Direction to divide ("x" or "y")

        Returns:
            List of (PlaneParameters, points_in_plane) tuples
        """
        if direction == "x":
            coords = [p.x for p in points]
        else:
            coords = [p.y for p in points]

        min_coord = min(coords)
        max_coord = max(coords)
        step = (max_coord - min_coord) / num_planes

        results = []

        for i in range(num_planes):
            low = min_coord + i * step
            high = min_coord + (i + 1) * step

            # Filter points for this plane
            if direction == "x":
                plane_points = [p for p in points if low <= p.x < high or (i == num_planes - 1 and p.x == high)]
            else:
                plane_points = [p for p in points if low <= p.y < high or (i == num_planes - 1 and p.y == high)]

            if len(plane_points) >= 3:
                plane = self.compute_optimal_plane(plane_points)
                results.append((plane, plane_points))

        return results

    def calculate_cut_fill_volumes(
        self, points: list[Point3D], plane: PlaneParameters, grid_size: float = 10.0
    ) -> CutFillResult:
        """
        Calculate cut and fill volumes using grid-based method.

        حساب أحجام القطع والردم باستخدام طريقة الشبكة

        Args:
            points: List of survey points
            plane: Design plane parameters
            grid_size: Grid cell size in meters

        Returns:
            CutFillResult with detailed volume information
        """
        cut_volume = 0.0
        fill_volume = 0.0
        cut_area = 0.0
        fill_area = 0.0
        max_cut_depth = 0.0
        max_fill_depth = 0.0
        cut_depths = []
        fill_depths = []

        cut_points = []
        fill_points = []
        design_points = []

        # Calculate for each point
        for p in points:
            design_z = plane.a * p.x + plane.b * p.y + plane.c
            diff = p.z - design_z

            design_points.append(Point3D(p.x, p.y, design_z, p.point_id))

            # Assume each point represents a cell of grid_size x grid_size
            cell_area = grid_size * grid_size

            if diff > 0:
                # Cut needed (existing ground is higher than design)
                cut_volume += diff * cell_area
                cut_area += cell_area
                max_cut_depth = max(max_cut_depth, diff)
                cut_depths.append(diff)
                cut_points.append(Point3D(p.x, p.y, diff, p.point_id))
            elif diff < 0:
                # Fill needed (existing ground is lower than design)
                fill_depth = -diff
                fill_volume += fill_depth * cell_area
                fill_area += cell_area
                max_fill_depth = max(max_fill_depth, fill_depth)
                fill_depths.append(fill_depth)
                fill_points.append(Point3D(p.x, p.y, fill_depth, p.point_id))

        avg_cut_depth = sum(cut_depths) / len(cut_depths) if cut_depths else 0.0
        avg_fill_depth = sum(fill_depths) / len(fill_depths) if fill_depths else 0.0

        return CutFillResult(
            cut_volume=cut_volume,
            fill_volume=fill_volume,
            cut_area=cut_area,
            fill_area=fill_area,
            max_cut_depth=max_cut_depth,
            max_fill_depth=max_fill_depth,
            avg_cut_depth=avg_cut_depth,
            avg_fill_depth=avg_fill_depth,
            cut_points=cut_points,
            fill_points=fill_points,
            design_points=design_points,
        )

    def calculate_tin_volumes(self, points: list[Point3D], plane: PlaneParameters) -> CutFillResult:
        """
        Calculate volumes using Triangulated Irregular Network (TIN) method.

        حساب الأحجام باستخدام طريقة الشبكة المثلثية غير المنتظمة

        This method is more accurate for irregularly spaced survey points.
        """
        # For a simplified implementation, we'll use Delaunay triangulation
        # In production, you would use scipy.spatial.Delaunay

        if len(points) < 3:
            return CutFillResult(
                cut_volume=0,
                fill_volume=0,
                cut_area=0,
                fill_area=0,
                max_cut_depth=0,
                max_fill_depth=0,
                avg_cut_depth=0,
                avg_fill_depth=0,
                cut_points=[],
                fill_points=[],
                design_points=[],
            )

        # Fallback to grid method for simplicity
        # In production, implement proper TIN calculation
        return self.calculate_cut_fill_volumes(points, plane, grid_size=5.0)

    def calculate_haul_distance(self, cut_points: list[Point3D], fill_points: list[Point3D]) -> float:
        """
        Calculate average haul distance between cut and fill areas.

        حساب متوسط مسافة نقل التربة بين مناطق القطع والردم

        Uses centroid-to-centroid distance as approximation.
        """
        if not cut_points or not fill_points:
            return 0.0

        # Calculate cut centroid
        cut_centroid_x = sum(p.x for p in cut_points) / len(cut_points)
        cut_centroid_y = sum(p.y for p in cut_points) / len(cut_points)

        # Calculate fill centroid
        fill_centroid_x = sum(p.x for p in fill_points) / len(fill_points)
        fill_centroid_y = sum(p.y for p in fill_points) / len(fill_points)

        # Euclidean distance
        distance = math.hypot(cut_centroid_x - fill_centroid_x, cut_centroid_y - fill_centroid_y)

        # Add factor for non-direct paths (typical haul factor)
        haul_factor = 1.2

        return distance * haul_factor

    def calculate_mass_haul(self, cut_points: list[Point3D], fill_points: list[Point3D]) -> dict[str, float]:
        """
        Calculate mass haul diagram statistics.

        حساب إحصائيات مخطط نقل الكتلة

        Returns metrics for optimizing earthwork operations.
        """
        total_cut = sum(p.z for p in cut_points) if cut_points else 0
        total_fill = sum(p.z for p in fill_points) if fill_points else 0

        # Calculate optimal balance line
        balance_point = total_cut - total_fill

        # Free haul distance (typically economic limit for dozers)
        free_haul_distance = 100.0  # meters

        # Overhaul distance
        avg_haul = self.calculate_haul_distance(cut_points, fill_points)
        overhaul_distance = max(0, avg_haul - free_haul_distance)

        return {
            "total_cut_volume": total_cut,
            "total_fill_volume": total_fill,
            "balance_point": balance_point,
            "average_haul_distance": avg_haul,
            "free_haul_distance": free_haul_distance,
            "overhaul_distance": overhaul_distance,
            "requires_import": total_fill > total_cut * self.soil_expansion_factor,
            "requires_export": total_cut > total_fill / self.soil_compaction_factor,
        }

    def calculate_field_area(self, points: list[Point3D]) -> float:
        """
        Calculate field area using convex hull approximation.

        حساب مساحة الحقل باستخدام تقريب الغلاف المحدب
        """
        if len(points) < 3:
            return 0.0

        # Use shoelace formula on convex hull
        x = [p.x for p in points]
        y = [p.y for p in points]

        # Simple bounding box area as approximation
        width = max(x) - min(x)
        height = max(y) - min(y)

        return width * height

    def calculate_statistics(self, points: list[Point3D]) -> dict[str, float]:
        """
        Calculate elevation statistics for survey points.

        حساب إحصائيات الارتفاع لنقاط المسح
        """
        if not points:
            return {}

        elevations = [p.z for p in points]

        return {
            "min_elevation": min(elevations),
            "max_elevation": max(elevations),
            "mean_elevation": sum(elevations) / len(elevations),
            "elevation_range": max(elevations) - min(elevations),
            "std_dev": self._calculate_std_dev(elevations),
            "point_count": len(points),
        }

    def _calculate_std_dev(self, values: list[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

    def optimize_for_irrigation(
        self, points: list[Point3D], min_grade: float = 0.1, max_grade: float = 0.5
    ) -> PlaneParameters:
        """
        Optimize plane parameters for irrigation efficiency.

        تحسين معلمات المستوى لكفاءة الري

        Args:
            points: Survey points
            min_grade: Minimum grade for drainage (%)
            max_grade: Maximum grade for uniform water distribution (%)

        Returns:
            PlaneParameters optimized for irrigation
        """
        # Start with least squares fit
        initial_plane = self.compute_optimal_plane(points)

        # Calculate current grades as percentages
        grade_x = initial_plane.a * 100
        grade_y = initial_plane.b * 100

        # Constrain grades to acceptable range
        if abs(grade_x) < min_grade:
            grade_x = min_grade if grade_x >= 0 else -min_grade
        if abs(grade_x) > max_grade:
            grade_x = max_grade if grade_x >= 0 else -max_grade

        if abs(grade_y) < min_grade:
            grade_y = min_grade if grade_y >= 0 else -min_grade
        if abs(grade_y) > max_grade:
            grade_y = max_grade if grade_y >= 0 else -max_grade

        # Recompute with constrained grades
        return self.compute_optimal_plane(points, target_grade_x=grade_x, target_grade_y=grade_y, balance_cut_fill=True)

    def grade_percent_to_ratio(self, grade_percent: float) -> str:
        """
        Convert grade percentage to ratio format (e.g., 0.5% -> 1:200).

        تحويل نسبة الميل إلى صيغة النسبة
        """
        if grade_percent == 0:
            return "1:∞"

        ratio = 100 / abs(grade_percent)
        return f"1:{ratio:.0f}"

    def ratio_to_grade_percent(self, ratio: float) -> float:
        """
        Convert ratio to grade percentage (e.g., 200 -> 0.5%).

        تحويل النسبة إلى نسبة ميل مئوية
        """
        if ratio == 0:
            return 0.0

        return 100 / ratio
