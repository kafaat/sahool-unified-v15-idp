"""
SAHOOL Field Boundary Detection Endpoints
نقاط نهاية كشف حدود الحقول

API endpoints for automatic field boundary detection, refinement, and change detection.
"""

import json
import logging
from datetime import datetime

from fastapi import HTTPException, Query

from .field_boundary_detector import BoundaryChange

logger = logging.getLogger(__name__)


def register_boundary_endpoints(app, boundary_detector):
    """
    Register field boundary detection endpoints with the FastAPI app.

    Args:
        app: FastAPI application instance
        boundary_detector: FieldBoundaryDetector instance
    """

    @app.post("/v1/boundaries/detect", response_model=dict)
    async def detect_boundaries(
        lat: float = Query(..., description="Latitude of center point"),
        lon: float = Query(..., description="Longitude of center point"),
        radius_m: float = Query(500, description="Search radius in meters"),
        date: str | None = Query(None, description="Date for imagery (ISO format)"),
    ):
        """
        Detect field boundaries around a point using NDVI edge detection.

        Automatically identifies field boundaries from satellite imagery using:
        - NDVI-based edge detection
        - Gradient analysis to find field edges
        - Contour tracing to extract polygons
        - Area and quality filtering

        Returns GeoJSON FeatureCollection of detected fields.

        Example:
            POST /v1/boundaries/detect?lat=15.5&lon=44.2&radius_m=500

        Response:
            {
                "type": "FeatureCollection",
                "features": [...],
                "metadata": {
                    "fields_detected": 3,
                    "total_area_hectares": 12.5
                }
            }
        """
        if not boundary_detector:
            raise HTTPException(status_code=503, detail="Field boundary detector not initialized")

        try:
            # Parse date if provided
            detection_date = None
            if date:
                try:
                    detection_date = datetime.fromisoformat(date.replace("Z", "+00:00"))
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid date format. Use ISO format (YYYY-MM-DD)",
                    )

            # Detect boundaries
            boundaries = await boundary_detector.detect_boundary(
                latitude=lat, longitude=lon, radius_meters=radius_m, date=detection_date
            )

            # Convert to GeoJSON FeatureCollection
            features = [boundary.to_geojson() for boundary in boundaries]

            return {
                "type": "FeatureCollection",
                "features": features,
                "metadata": {
                    "center": {"lat": lat, "lon": lon},
                    "radius_meters": radius_m,
                    "detection_date": (detection_date or datetime.now()).isoformat(),
                    "fields_detected": len(boundaries),
                    "total_area_hectares": round(sum(b.area_hectares for b in boundaries), 2),
                    "method": "ndvi_edge_detection",
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Boundary detection failed: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    @app.post("/v1/boundaries/refine", response_model=dict)
    async def refine_boundary(
        coords: list[list[float]] = Query(
            ..., description="Initial boundary coordinates [[lon, lat], ...]"
        ),
        buffer_m: float = Query(50, description="Refinement buffer in meters"),
    ):
        """
        Refine a rough field boundary by snapping to NDVI edges.

        Takes an approximate boundary (e.g., hand-drawn on a map) and refines it
        to match the actual field edges visible in satellite imagery.

        Input coordinates should be [[lon, lat], ...] format.
        Returns refined GeoJSON Feature.

        Example:
            POST /v1/boundaries/refine
            Body: {
                "coords": [[44.2, 15.5], [44.21, 15.5], [44.21, 15.51], [44.2, 15.51]],
                "buffer_m": 50
            }

        Response:
            {
                "refined_boundary": {...},
                "refinement_stats": {
                    "area_hectares": 2.5,
                    "confidence": 0.85
                }
            }
        """
        if not boundary_detector:
            raise HTTPException(status_code=503, detail="Field boundary detector not initialized")

        try:
            # Convert to tuple format
            coord_tuples = list(coords)

            if len(coord_tuples) < 3:
                raise HTTPException(
                    status_code=400,
                    detail="Need at least 3 coordinates to form a polygon",
                )

            # Refine boundary
            refined = await boundary_detector.refine_boundary(
                initial_coords=coord_tuples, buffer_meters=buffer_m
            )

            return {
                "refined_boundary": refined.to_geojson(),
                "refinement_stats": {
                    "initial_points": len(coord_tuples),
                    "refined_points": len(refined.coordinates),
                    "area_hectares": refined.area_hectares,
                    "perimeter_meters": refined.perimeter_meters,
                    "confidence": refined.detection_confidence,
                    "quality_score": refined.quality_score,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Boundary refinement failed: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    @app.get("/v1/boundaries/{field_id}/changes", response_model=dict)
    async def get_boundary_changes(
        field_id: str,
        since_date: str = Query(..., description="Compare to this date (ISO format)"),
        previous_coords: str = Query(..., description="Previous boundary coordinates (JSON array)"),
    ):
        """
        Detect changes in field boundary over time.

        Compares a previous boundary with current satellite imagery to detect:
        - Field expansion (clearing of new land)
        - Field contraction (abandonment, erosion)
        - Boundary shifts

        previous_coords should be JSON array: [[lon, lat], ...]

        Example:
            GET /v1/boundaries/field_123/changes?since_date=2024-01-01&previous_coords=[[44.2,15.5],[44.21,15.5]]

        Response:
            {
                "field_id": "field_123",
                "change_analysis": {
                    "change_type": "expansion",
                    "change_percent": 15.2,
                    "area_change_hectares": 1.2
                }
            }
        """
        if not boundary_detector:
            raise HTTPException(status_code=503, detail="Field boundary detector not initialized")

        try:
            # Parse previous coordinates
            try:
                coord_list = json.loads(previous_coords)
                coord_tuples = list(coord_list)
            except (json.JSONDecodeError, ValueError):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid previous_coords format. Expected JSON array [[lon, lat], ...]",
                )

            # Parse date
            try:
                current_date = datetime.fromisoformat(since_date.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format")

            # Detect changes
            change = await boundary_detector.detect_boundary_change(
                field_id=field_id,
                previous_coords=coord_tuples,
                current_date=current_date,
            )

            # Create response
            return {
                "field_id": field_id,
                "change_analysis": {
                    "change_type": change.change_type,
                    "change_percent": round(change.change_percent, 2),
                    "previous_area_hectares": round(change.previous_area, 2),
                    "current_area_hectares": round(change.current_area, 2),
                    "area_change_hectares": (
                        round(change.area_change_hectares, 2) if change.area_change_hectares else 0
                    ),
                    "boundary_shift_meters": (
                        round(change.boundary_shift_meters, 2)
                        if change.boundary_shift_meters
                        else 0
                    ),
                    "confidence": change.change_confidence,
                },
                "affected_area": (
                    {
                        "type": "MultiPoint",
                        "coordinates": [[lon, lat] for lon, lat in change.affected_coordinates],
                    }
                    if change.affected_coordinates
                    else None
                ),
                "interpretation": {
                    "en": _interpret_boundary_change(change),
                    "ar": _interpret_boundary_change_ar(change),
                },
                "detection_date": change.detection_date.isoformat(),
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Change detection failed: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    logger.info("Field boundary detection endpoints registered")


def _interpret_boundary_change(change: BoundaryChange) -> str:
    """Interpret boundary change in English"""
    if change.change_type == "stable":
        return f"Field boundary is stable (±{abs(change.change_percent):.1f}% change)"
    elif change.change_type == "expansion":
        return f"Field has expanded by {abs(change.change_percent):.1f}% ({abs(change.area_change_hectares):.2f} hectares)"
    else:  # contraction
        return f"Field has contracted by {abs(change.change_percent):.1f}% ({abs(change.area_change_hectares):.2f} hectares)"


def _interpret_boundary_change_ar(change: BoundaryChange) -> str:
    """Interpret boundary change in Arabic"""
    if change.change_type == "stable":
        return f"حدود الحقل مستقرة (تغيير ±{abs(change.change_percent):.1f}%)"
    elif change.change_type == "expansion":
        return f"توسع الحقل بنسبة {abs(change.change_percent):.1f}% ({abs(change.area_change_hectares):.2f} هكتار)"
    else:  # contraction
        return f"انكمش الحقل بنسبة {abs(change.change_percent):.1f}% ({abs(change.area_change_hectares):.2f} هكتار)"
