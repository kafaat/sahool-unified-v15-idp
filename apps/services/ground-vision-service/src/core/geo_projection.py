"""
Quaternion-based Georeferencing - تحويل الإحداثيات باستخدام الرباعيات
Based on: Qin et al. (2026) - Quaternion-based georeferencing for tower cameras

This module provides direct pixel-to-geocoordinate transformation using quaternions,
avoiding gimbal lock issues with traditional Euler angles.
"""

import logging
from typing import Optional

import numpy as np
from pydantic import BaseModel
from scipy.spatial.transform import Rotation

logger = logging.getLogger(__name__)


class CameraIntrinsicsMatrix(BaseModel):
    """Camera intrinsic parameters for matrix construction"""

    fx: float  # Focal length x
    fy: float  # Focal length y
    cx: float  # Principal point x
    cy: float  # Principal point y
    k1: float = 0.0  # Radial distortion coefficient 1
    k2: float = 0.0  # Radial distortion coefficient 2
    k3: float = 0.0  # Radial distortion coefficient 3
    p1: float = 0.0  # Tangential distortion coefficient 1
    p2: float = 0.0  # Tangential distortion coefficient 2

    def to_matrix(self) -> np.ndarray:
        """Convert to 3x3 intrinsic matrix K"""
        return np.array([[self.fx, 0, self.cx], [0, self.fy, self.cy], [0, 0, 1]])

    def distortion_coeffs(self) -> np.ndarray:
        """Get distortion coefficients vector"""
        return np.array([self.k1, self.k2, self.p1, self.p2, self.k3])


class DEMService:
    """
    Digital Elevation Model service for terrain-ray intersection.
    Simplified implementation - in production, use rasterio with actual DEM tiles.
    """

    def __init__(self, default_elevation: float = 0.0):
        """
        Initialize DEM service.

        Args:
            default_elevation: Default terrain elevation (meters above WGS84 ellipsoid)
        """
        self.default_elevation = default_elevation
        self._dem_cache: dict[str, np.ndarray] = {}

    async def get_elevation(self, lat: float, lon: float) -> float:
        """
        Get terrain elevation at a geographic point.

        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees

        Returns:
            Elevation in meters above WGS84 ellipsoid
        """
        # TODO: Implement actual DEM lookup using rasterio
        # For now, return default elevation (flat terrain assumption)
        return self.default_elevation

    def get_elevation_grid(
        self, bounds: tuple[float, float, float, float], resolution: float = 10.0
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Get elevation grid for a bounding box.

        Args:
            bounds: (min_lon, min_lat, max_lon, max_lat)
            resolution: Grid resolution in meters

        Returns:
            Tuple of (lon_grid, lat_grid, elevation_grid)
        """
        min_lon, min_lat, max_lon, max_lat = bounds

        # Create coordinate grids (simplified, assumes small area)
        n_lon = int((max_lon - min_lon) * 111000 / resolution) + 1
        n_lat = int((max_lat - min_lat) * 111000 / resolution) + 1

        lon_grid = np.linspace(min_lon, max_lon, n_lon)
        lat_grid = np.linspace(min_lat, max_lat, n_lat)

        # For now, flat terrain
        elevation_grid = np.full((n_lat, n_lon), self.default_elevation)

        return lon_grid, lat_grid, elevation_grid


class QuaternionGeoProjector:
    """
    Direct pixel-to-geocoordinate transformation using quaternions.
    Avoids gimbal lock issues with traditional Euler angles.

    Based on: Qin et al. (2026) - Quaternion-based georeferencing for tower cameras
    """

    # WGS84 ellipsoid parameters
    WGS84_A = 6378137.0  # Semi-major axis (meters)
    WGS84_B = 6356752.314245  # Semi-minor axis (meters)
    WGS84_E2 = 1 - (WGS84_B**2) / (WGS84_A**2)  # First eccentricity squared

    def __init__(
        self,
        camera_intrinsics: CameraIntrinsicsMatrix,
        camera_position_enu: np.ndarray,  # [e, n, u] in local ENU frame
        camera_quaternion: np.ndarray,  # [w, x, y, z] rotation from camera to ENU
        origin_lat: float,  # Origin latitude for ENU frame
        origin_lon: float,  # Origin longitude for ENU frame
        origin_alt: float = 0.0,  # Origin altitude
        dem_service: DEMService | None = None,
    ):
        """
        Initialize the geo-projector.

        Args:
            camera_intrinsics: Camera intrinsic parameters
            camera_position_enu: Camera position in local ENU coordinates [e, n, u]
            camera_quaternion: Quaternion [w, x, y, z] for camera orientation
            origin_lat: Latitude of ENU frame origin
            origin_lon: Longitude of ENU frame origin
            origin_alt: Altitude of ENU frame origin
            dem_service: Optional DEM service for terrain intersection
        """
        self.K = camera_intrinsics.to_matrix()
        self.K_inv = np.linalg.inv(self.K)
        self.distortion = camera_intrinsics.distortion_coeffs()

        self.position = np.array(camera_position_enu)

        # Scipy uses [x, y, z, w] format, but we receive [w, x, y, z]
        quat_scipy = np.array(
            [
                camera_quaternion[1],  # x
                camera_quaternion[2],  # y
                camera_quaternion[3],  # z
                camera_quaternion[0],  # w
            ]
        )
        self.rotation = Rotation.from_quat(quat_scipy)

        self.origin_lat = origin_lat
        self.origin_lon = origin_lon
        self.origin_alt = origin_alt

        self.dem = dem_service or DEMService(default_elevation=origin_alt)

        logger.info(f"QuaternionGeoProjector initialized at origin ({origin_lat}, {origin_lon})")

    def pixel_to_geo(self, u: float, v: float, terrain_elevation: float | None = None) -> tuple[float, float]:
        """
        Transform image pixel (u, v) to geographic coordinates (lon, lat).

        Algorithm:
        1. Undistort pixel coordinates
        2. Convert pixel to normalized camera coordinates
        3. Apply inverse rotation using quaternion
        4. Compute ray-terrain intersection
        5. Convert local ENU to WGS84

        Args:
            u: Pixel x coordinate
            v: Pixel y coordinate
            terrain_elevation: Optional terrain elevation override

        Returns:
            Tuple of (longitude, latitude) in degrees
        """
        # Step 1: Undistort pixel (simplified - assumes low distortion)
        u_undist, v_undist = self._undistort_point(u, v)

        # Step 2: Pixel to normalized camera coords
        pixel = np.array([u_undist, v_undist, 1.0])
        ray_camera = self.K_inv @ pixel
        ray_camera = ray_camera / np.linalg.norm(ray_camera)

        # Step 3: Camera to world frame using quaternion rotation
        ray_world = self.rotation.apply(ray_camera)

        # Step 4: Ray-terrain intersection
        target_elevation = terrain_elevation or self.dem.default_elevation
        intersection_enu = self._intersect_ray_plane(self.position, ray_world, target_elevation)

        if intersection_enu is None:
            # Ray doesn't intersect terrain (looking at sky)
            logger.warning(f"Pixel ({u}, {v}) does not intersect terrain")
            return (self.origin_lon, self.origin_lat)

        # Step 5: ENU to WGS84
        lon, lat = self._enu_to_wgs84(intersection_enu)

        return (lon, lat)

    def geo_to_pixel(self, lon: float, lat: float) -> tuple[float, float]:
        """
        Transform geographic coordinates to image pixel.

        Args:
            lon: Longitude in degrees
            lat: Latitude in degrees

        Returns:
            Tuple of (u, v) pixel coordinates
        """
        # WGS84 to ENU
        point_enu = self._wgs84_to_enu(lon, lat)

        # ENU to camera frame
        point_camera = self._enu_to_camera(point_enu)

        if point_camera[2] <= 0:
            # Point is behind camera
            logger.warning(f"Point ({lon}, {lat}) is behind camera")
            return (-1, -1)

        # Project to image plane
        point_normalized = point_camera / point_camera[2]
        pixel_homogeneous = self.K @ point_normalized

        u = pixel_homogeneous[0]
        v = pixel_homogeneous[1]

        return (u, v)

    def generate_footprint_polygon(
        self, image_width: int, image_height: int, terrain_elevation: float | None = None
    ) -> list[tuple[float, float]]:
        """
        Generate the ground footprint polygon for the camera's field of view.

        Args:
            image_width: Image width in pixels
            image_height: Image height in pixels
            terrain_elevation: Optional terrain elevation

        Returns:
            List of (lon, lat) tuples forming the footprint polygon
        """
        # Image corner pixels
        corners_pixel = [
            (0, 0),  # Top-left
            (image_width, 0),  # Top-right
            (image_width, image_height),  # Bottom-right
            (0, image_height),  # Bottom-left
        ]

        # Project each corner to geographic coordinates
        corners_geo = []
        for u, v in corners_pixel:
            lon, lat = self.pixel_to_geo(u, v, terrain_elevation)
            corners_geo.append((lon, lat))

        return corners_geo

    def _undistort_point(self, u: float, v: float) -> tuple[float, float]:
        """
        Undistort a single pixel coordinate.
        Simplified implementation using first-order correction.
        """
        # Normalize coordinates
        cx, cy = self.K[0, 2], self.K[1, 2]
        fx, fy = self.K[0, 0], self.K[1, 1]

        x = (u - cx) / fx
        y = (v - cy) / fy

        # Radial distance
        r2 = x * x + y * y

        # Radial distortion correction
        k1, k2, _, _, k3 = self.distortion
        radial = 1 + k1 * r2 + k2 * r2 * r2 + k3 * r2 * r2 * r2

        x_corrected = x * radial
        y_corrected = y * radial

        # Back to pixel coordinates
        u_corrected = x_corrected * fx + cx
        v_corrected = y_corrected * fy + cy

        return (u_corrected, v_corrected)

    def _intersect_ray_plane(
        self, origin: np.ndarray, direction: np.ndarray, plane_elevation: float
    ) -> np.ndarray | None:
        """
        Intersect a ray with a horizontal plane at given elevation.

        Args:
            origin: Ray origin in ENU coordinates
            direction: Ray direction (unit vector)
            plane_elevation: Elevation of the plane (U coordinate)

        Returns:
            Intersection point in ENU coordinates, or None if no intersection
        """
        # Plane normal is [0, 0, 1] (pointing up)
        # Plane equation: z = plane_elevation

        # Ray: P = origin + t * direction
        # At intersection: origin[2] + t * direction[2] = plane_elevation

        if abs(direction[2]) < 1e-10:
            # Ray is parallel to plane
            return None

        t = (plane_elevation - origin[2]) / direction[2]

        if t < 0:
            # Intersection is behind the camera
            return None

        intersection = origin + t * direction
        return intersection

    def _enu_to_wgs84(self, enu: np.ndarray) -> tuple[float, float]:
        """
        Convert ENU coordinates to WGS84 (lon, lat).

        Args:
            enu: Coordinates in ENU frame [e, n, u]

        Returns:
            Tuple of (longitude, latitude) in degrees
        """
        e, n, _ = enu

        # Approximate conversion for small areas
        # 1 degree latitude ~ 111,111 meters
        # 1 degree longitude ~ 111,111 * cos(lat) meters
        lat_rad = np.radians(self.origin_lat)

        delta_lat = n / 111111.0
        delta_lon = e / (111111.0 * np.cos(lat_rad))

        lat = self.origin_lat + delta_lat
        lon = self.origin_lon + delta_lon

        return (lon, lat)

    def _wgs84_to_enu(self, lon: float, lat: float, alt: float | None = None) -> np.ndarray:
        """
        Convert WGS84 (lon, lat) to ENU coordinates.

        Args:
            lon: Longitude in degrees
            lat: Latitude in degrees
            alt: Altitude (defaults to origin altitude)

        Returns:
            Coordinates in ENU frame [e, n, u]
        """
        if alt is None:
            alt = self.origin_alt

        # Approximate conversion for small areas
        lat_rad = np.radians(self.origin_lat)

        delta_lat = lat - self.origin_lat
        delta_lon = lon - self.origin_lon

        n = delta_lat * 111111.0
        e = delta_lon * 111111.0 * np.cos(lat_rad)
        u = alt - self.origin_alt

        return np.array([e, n, u])

    def _enu_to_camera(self, point_enu: np.ndarray) -> np.ndarray:
        """
        Transform a point from ENU frame to camera frame.

        Args:
            point_enu: Point in ENU coordinates

        Returns:
            Point in camera frame
        """
        # Translate to camera origin
        point_camera_origin = point_enu - self.position

        # Rotate by inverse of camera orientation
        point_camera = self.rotation.inv().apply(point_camera_origin)

        return point_camera


class OrthoRectifier:
    """
    Generate orthorectified images from tower camera frames.
    """

    def __init__(self, projector: QuaternionGeoProjector, output_resolution_m: float = 0.5):
        """
        Initialize orthorectifier.

        Args:
            projector: QuaternionGeoProjector instance
            output_resolution_m: Output resolution in meters per pixel
        """
        self.projector = projector
        self.resolution = output_resolution_m

    def compute_output_bounds(self, image_width: int, image_height: int) -> tuple[float, float, float, float]:
        """
        Compute the geographic bounds of the output ortho image.

        Returns:
            Tuple of (min_lon, min_lat, max_lon, max_lat)
        """
        footprint = self.projector.generate_footprint_polygon(image_width, image_height)

        lons = [p[0] for p in footprint]
        lats = [p[1] for p in footprint]

        return (min(lons), min(lats), max(lons), max(lats))

    def compute_output_size(self, bounds: tuple[float, float, float, float]) -> tuple[int, int]:
        """
        Compute the output image size in pixels.

        Args:
            bounds: (min_lon, min_lat, max_lon, max_lat)

        Returns:
            Tuple of (width, height) in pixels
        """
        min_lon, min_lat, max_lon, max_lat = bounds

        # Approximate width/height in meters
        lat_rad = np.radians((min_lat + max_lat) / 2)
        width_m = (max_lon - min_lon) * 111111.0 * np.cos(lat_rad)
        height_m = (max_lat - min_lat) * 111111.0

        width_px = int(width_m / self.resolution) + 1
        height_px = int(height_m / self.resolution) + 1

        return (width_px, height_px)

    async def orthorectify(
        self, image: np.ndarray, bounds: tuple[float, float, float, float] | None = None
    ) -> tuple[np.ndarray, dict]:
        """
        Generate orthorectified image.

        Args:
            image: Input image as numpy array (H, W, C)
            bounds: Optional output bounds, auto-computed if None

        Returns:
            Tuple of (ortho_image, geotransform_dict)
        """
        h, w = image.shape[:2]

        if bounds is None:
            bounds = self.compute_output_bounds(w, h)

        out_w, out_h = self.compute_output_size(bounds)
        min_lon, min_lat, max_lon, max_lat = bounds

        # Create output image
        if len(image.shape) == 3:
            ortho = np.zeros((out_h, out_w, image.shape[2]), dtype=image.dtype)
        else:
            ortho = np.zeros((out_h, out_w), dtype=image.dtype)

        # Compute coordinate grids
        lon_step = (max_lon - min_lon) / out_w
        lat_step = (max_lat - min_lat) / out_h

        # For each output pixel, find corresponding input pixel
        for oy in range(out_h):
            for ox in range(out_w):
                # Output pixel geographic coordinates
                lon = min_lon + ox * lon_step
                lat = max_lat - oy * lat_step  # Y axis is flipped

                # Project to input image
                ix, iy = self.projector.geo_to_pixel(lon, lat)

                # Bilinear interpolation
                if 0 <= ix < w - 1 and 0 <= iy < h - 1:
                    ix_int = int(ix)
                    iy_int = int(iy)
                    dx = ix - ix_int
                    dy = iy - iy_int

                    if len(image.shape) == 3:
                        ortho[oy, ox] = (
                            (1 - dx) * (1 - dy) * image[iy_int, ix_int]
                            + dx * (1 - dy) * image[iy_int, ix_int + 1]
                            + (1 - dx) * dy * image[iy_int + 1, ix_int]
                            + dx * dy * image[iy_int + 1, ix_int + 1]
                        )
                    else:
                        ortho[oy, ox] = (
                            (1 - dx) * (1 - dy) * image[iy_int, ix_int]
                            + dx * (1 - dy) * image[iy_int, ix_int + 1]
                            + (1 - dx) * dy * image[iy_int + 1, ix_int]
                            + dx * dy * image[iy_int + 1, ix_int + 1]
                        )

        # Geotransform (GDAL-style)
        geotransform = {
            "origin_lon": min_lon,
            "origin_lat": max_lat,
            "pixel_width": lon_step,
            "pixel_height": -lat_step,
            "crs": "EPSG:4326",
            "bounds": bounds,
            "resolution_m": self.resolution,
        }

        return ortho, geotransform
