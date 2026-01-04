"""
SAHOOL Satellite Service - VRA Endpoints
نقاط نهاية خدمة التطبيق المتغير المعدل

API endpoints for Variable Rate Application prescription maps.
"""

import logging

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from .vra_generator import (
    VRAGenerator,
    VRAType,
    ZoneMethod,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Request/Response Models
# =============================================================================


class VRARequest(BaseModel):
    """Request for VRA prescription map generation"""

    field_id: str = Field(..., description="معرف الحقل")
    latitude: float = Field(..., ge=-90, le=90, description="خط العرض")
    longitude: float = Field(..., ge=-180, le=180, description="خط الطول")
    vra_type: str = Field(
        ..., description="نوع التطبيق (fertilizer, seed, lime, pesticide, irrigation)"
    )
    target_rate: float = Field(..., gt=0, description="المعدل المستهدف")
    unit: str = Field(..., description="وحدة القياس (kg/ha, seeds/ha, L/ha, mm/ha)")
    num_zones: int = Field(
        default=3, ge=3, le=5, description="عدد مناطق الإدارة (3 أو 5)"
    )
    zone_method: str = Field(default="ndvi", description="طريقة تصنيف المناطق")
    min_rate: float | None = Field(None, gt=0, description="الحد الأدنى للمعدل")
    max_rate: float | None = Field(None, gt=0, description="الحد الأقصى للمعدل")
    product_price_per_unit: float | None = Field(
        None, description="سعر الوحدة للمنتج"
    )
    notes: str | None = Field(None, description="ملاحظات (إنجليزي)")
    notes_ar: str | None = Field(None, description="ملاحظات (عربي)")


class ManagementZoneResponse(BaseModel):
    """Management zone in prescription map"""

    zone_id: int
    zone_name: str
    zone_name_ar: str
    zone_level: str
    ndvi_min: float
    ndvi_max: float
    area_ha: float
    percentage: float
    centroid: list[float]  # [lon, lat]
    recommended_rate: float
    unit: str
    total_product: float
    color: str


class PrescriptionMapResponse(BaseModel):
    """VRA prescription map response"""

    id: str
    field_id: str
    vra_type: str
    created_at: str
    target_rate: float
    min_rate: float
    max_rate: float
    unit: str
    num_zones: int
    zone_method: str
    zones: list[ManagementZoneResponse]
    total_area_ha: float
    total_product_needed: float
    flat_rate_product: float
    savings_percent: float
    savings_amount: float
    cost_savings: float | None
    notes: str | None
    notes_ar: str | None
    geojson_url: str | None
    shapefile_url: str | None
    isoxml_url: str | None


# =============================================================================
# Endpoint Registration
# =============================================================================


def register_vra_endpoints(app: FastAPI, vra_generator: VRAGenerator):
    """
    Register VRA endpoints to the FastAPI app

    Args:
        app: FastAPI application instance
        vra_generator: Initialized VRAGenerator instance
    """

    @app.post("/v1/vra/generate", response_model=PrescriptionMapResponse)
    async def generate_vra_prescription(request: VRARequest):
        """
        توليد خريطة وصفة التطبيق المتغير | Generate VRA Prescription Map

        Create a variable rate application prescription map based on NDVI zones.
        Similar to OneSoil VRA capabilities.

        Supported VRA types:
        - fertilizer: Variable nitrogen/fertilizer application
        - seed: Variable seeding rates
        - lime: Variable lime application
        - pesticide: Variable pesticide application
        - irrigation: Variable irrigation rates

        Example:
            POST /v1/vra/generate
            {
                "field_id": "field_123",
                "latitude": 15.5,
                "longitude": 44.2,
                "vra_type": "fertilizer",
                "target_rate": 100,
                "unit": "kg/ha",
                "num_zones": 3,
                "product_price_per_unit": 2.5
            }
        """
        try:
            # Parse VRA type
            try:
                vra_type = VRAType(request.vra_type.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid VRA type. Must be one of: {', '.join([t.value for t in VRAType])}",
                )

            # Parse zone method
            try:
                zone_method = ZoneMethod(request.zone_method.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid zone method. Must be one of: {', '.join([m.value for m in ZoneMethod])}",
                )

            # Generate prescription map
            prescription = await vra_generator.generate_prescription(
                field_id=request.field_id,
                latitude=request.latitude,
                longitude=request.longitude,
                vra_type=vra_type,
                target_rate=request.target_rate,
                unit=request.unit,
                num_zones=request.num_zones,
                zone_method=zone_method,
                min_rate=request.min_rate,
                max_rate=request.max_rate,
                product_price_per_unit=request.product_price_per_unit,
                notes=request.notes,
                notes_ar=request.notes_ar,
            )

            # Convert to response model
            zones_response = [
                ManagementZoneResponse(
                    zone_id=z.zone_id,
                    zone_name=z.zone_name,
                    zone_name_ar=z.zone_name_ar,
                    zone_level=z.zone_level.value,
                    ndvi_min=z.ndvi_range[0],
                    ndvi_max=z.ndvi_range[1],
                    area_ha=z.area_ha,
                    percentage=z.percentage,
                    centroid=list(z.centroid),
                    recommended_rate=z.recommended_rate,
                    unit=z.unit,
                    total_product=z.total_product,
                    color=z.color,
                )
                for z in prescription.zones
            ]

            return PrescriptionMapResponse(
                id=prescription.id,
                field_id=prescription.field_id,
                vra_type=prescription.vra_type.value,
                created_at=prescription.created_at.isoformat(),
                target_rate=prescription.target_rate,
                min_rate=prescription.min_rate,
                max_rate=prescription.max_rate,
                unit=prescription.unit,
                num_zones=prescription.num_zones,
                zone_method=prescription.zone_method.value,
                zones=zones_response,
                total_area_ha=prescription.total_area_ha,
                total_product_needed=prescription.total_product_needed,
                flat_rate_product=prescription.flat_rate_product,
                savings_percent=prescription.savings_percent,
                savings_amount=prescription.savings_amount,
                cost_savings=prescription.cost_savings,
                notes=prescription.notes,
                notes_ar=prescription.notes_ar,
                geojson_url=f"/v1/vra/export/{prescription.id}?format=geojson",
                shapefile_url=f"/v1/vra/export/{prescription.id}?format=shapefile",
                isoxml_url=f"/v1/vra/export/{prescription.id}?format=isoxml",
            )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error generating VRA prescription: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to generate prescription: {str(e)}"
            )

    @app.get("/v1/vra/zones/{field_id}")
    async def get_management_zones(
        field_id: str,
        lat: float = Query(..., description="Field latitude", ge=-90, le=90),
        lon: float = Query(..., description="Field longitude", ge=-180, le=180),
        num_zones: int = Query(3, description="Number of management zones", ge=3, le=5),
    ):
        """
        تحليل مناطق الإدارة | Get Management Zones

        Classify field into management zones based on NDVI without generating
        a full prescription. Useful for previewing zones before creating prescription.

        Example:
            GET /v1/vra/zones/field_123?lat=15.5&lon=44.2&num_zones=3
        """
        try:
            zones_stats = await vra_generator.classify_zones(
                field_id=field_id,
                latitude=lat,
                longitude=lon,
                num_zones=num_zones,
            )

            zones_response = [
                {
                    "zone_id": z.zone_id,
                    "zone_name": z.zone_name,
                    "zone_name_ar": z.zone_name_ar,
                    "zone_level": z.zone_level.value,
                    "ndvi_min": z.ndvi_range[0],
                    "ndvi_max": z.ndvi_range[1],
                    "area_ha": z.area_ha,
                    "percentage": z.percentage,
                    "centroid": list(z.centroid),
                    "color": z.color,
                }
                for z in zones_stats.zones
            ]

            return {
                "field_id": field_id,
                "num_zones": zones_stats.num_zones,
                "total_area_ha": zones_stats.total_area_ha,
                "zones": zones_response,
                "ndvi_statistics": {
                    "mean": zones_stats.ndvi_mean,
                    "std": zones_stats.ndvi_std,
                    "min": zones_stats.ndvi_min,
                    "max": zones_stats.ndvi_max,
                },
            }

        except Exception as e:
            logger.error(f"Error classifying zones: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to classify zones: {str(e)}"
            )

    @app.get("/v1/vra/prescriptions/{field_id}")
    async def get_field_prescriptions(
        field_id: str,
        limit: int = Query(
            10, description="Maximum number of prescriptions to return", ge=1, le=50
        ),
    ):
        """
        سجل الوصفات | Get Prescription History

        Get all VRA prescriptions for a field, sorted by creation date (newest first).

        Example:
            GET /v1/vra/prescriptions/field_123?limit=10
        """
        try:
            prescriptions = await vra_generator.get_field_prescriptions(
                field_id=field_id,
                limit=limit,
            )

            return {
                "field_id": field_id,
                "count": len(prescriptions),
                "prescriptions": [
                    {
                        "id": p.id,
                        "vra_type": p.vra_type.value,
                        "created_at": p.created_at.isoformat(),
                        "target_rate": p.target_rate,
                        "unit": p.unit,
                        "num_zones": p.num_zones,
                        "total_area_ha": p.total_area_ha,
                        "total_product_needed": p.total_product_needed,
                        "savings_percent": p.savings_percent,
                        "savings_amount": p.savings_amount,
                        "cost_savings": p.cost_savings,
                        "notes": p.notes,
                        "notes_ar": p.notes_ar,
                    }
                    for p in prescriptions
                ],
            }

        except Exception as e:
            logger.error(f"Error fetching prescriptions: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch prescriptions: {str(e)}"
            )

    @app.get("/v1/vra/prescription/{prescription_id}")
    async def get_prescription_details(prescription_id: str):
        """
        تفاصيل الوصفة | Get Prescription Details

        Get detailed information about a specific prescription, including all zones.

        Example:
            GET /v1/vra/prescription/abc-123-def
        """
        try:
            prescription = await vra_generator.get_prescription(prescription_id)

            if not prescription:
                raise HTTPException(status_code=404, detail="Prescription not found")

            # Convert to response model
            zones_response = [
                ManagementZoneResponse(
                    zone_id=z.zone_id,
                    zone_name=z.zone_name,
                    zone_name_ar=z.zone_name_ar,
                    zone_level=z.zone_level.value,
                    ndvi_min=z.ndvi_range[0],
                    ndvi_max=z.ndvi_range[1],
                    area_ha=z.area_ha,
                    percentage=z.percentage,
                    centroid=list(z.centroid),
                    recommended_rate=z.recommended_rate,
                    unit=z.unit,
                    total_product=z.total_product,
                    color=z.color,
                )
                for z in prescription.zones
            ]

            return PrescriptionMapResponse(
                id=prescription.id,
                field_id=prescription.field_id,
                vra_type=prescription.vra_type.value,
                created_at=prescription.created_at.isoformat(),
                target_rate=prescription.target_rate,
                min_rate=prescription.min_rate,
                max_rate=prescription.max_rate,
                unit=prescription.unit,
                num_zones=prescription.num_zones,
                zone_method=prescription.zone_method.value,
                zones=zones_response,
                total_area_ha=prescription.total_area_ha,
                total_product_needed=prescription.total_product_needed,
                flat_rate_product=prescription.flat_rate_product,
                savings_percent=prescription.savings_percent,
                savings_amount=prescription.savings_amount,
                cost_savings=prescription.cost_savings,
                notes=prescription.notes,
                notes_ar=prescription.notes_ar,
                geojson_url=f"/v1/vra/export/{prescription.id}?format=geojson",
                shapefile_url=f"/v1/vra/export/{prescription.id}?format=shapefile",
                isoxml_url=f"/v1/vra/export/{prescription.id}?format=isoxml",
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching prescription: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch prescription: {str(e)}"
            )

    @app.get("/v1/vra/export/{prescription_id}")
    async def export_prescription(
        prescription_id: str,
        format: str = Query(
            "geojson", description="Export format (geojson, shapefile, isoxml)"
        ),
    ):
        """
        تصدير الوصفة | Export Prescription

        Export prescription in various formats for equipment compatibility:
        - geojson: For web display and GIS applications
        - shapefile: For farm equipment and GIS software
        - isoxml: For ISOBUS-compatible equipment

        Example:
            GET /v1/vra/export/abc-123-def?format=geojson
        """
        try:
            prescription = await vra_generator.get_prescription(prescription_id)

            if not prescription:
                raise HTTPException(status_code=404, detail="Prescription not found")

            format_lower = format.lower()

            if format_lower == "geojson":
                geojson = vra_generator.to_geojson(prescription)
                return geojson

            elif format_lower == "shapefile":
                shapefile_data = vra_generator.to_shapefile_data(prescription)
                return shapefile_data

            elif format_lower == "isoxml":
                isoxml = vra_generator.to_isoxml(prescription)
                return {
                    "format": "ISO-XML",
                    "prescription_id": prescription_id,
                    "xml": isoxml,
                }

            else:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid format. Must be one of: geojson, shapefile, isoxml",
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error exporting prescription: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to export prescription: {str(e)}"
            )

    @app.delete("/v1/vra/prescription/{prescription_id}")
    async def delete_prescription(prescription_id: str):
        """
        حذف الوصفة | Delete Prescription

        Delete a prescription from the system.

        Example:
            DELETE /v1/vra/prescription/abc-123-def
        """
        try:
            deleted = await vra_generator.delete_prescription(prescription_id)

            if not deleted:
                raise HTTPException(status_code=404, detail="Prescription not found")

            return {
                "success": True,
                "message": "Prescription deleted successfully",
                "message_ar": "تم حذف الوصفة بنجاح",
                "prescription_id": prescription_id,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting prescription: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to delete prescription: {str(e)}"
            )

    @app.get("/v1/vra/info")
    async def get_vra_info():
        """
        معلومات VRA | VRA Information

        Get information about supported VRA types, rate adjustments, and capabilities.

        Example:
            GET /v1/vra/info
        """
        return {
            "service": "Variable Rate Application (VRA) Prescription Maps",
            "service_ar": "خرائط وصفات التطبيق المتغير المعدل",
            "version": "1.0",
            "capabilities": {
                "vra_types": [
                    {
                        "type": "fertilizer",
                        "name": "Fertilizer",
                        "name_ar": "تسميد",
                        "description": "Variable nitrogen/fertilizer application based on crop vigor",
                        "description_ar": "تطبيق النيتروجين/الأسمدة المتغير بناءً على قوة المحصول",
                        "strategy": "More to low-vigor areas, less to high-vigor areas",
                    },
                    {
                        "type": "seed",
                        "name": "Seed",
                        "name_ar": "بذار",
                        "description": "Variable seeding rates based on field potential",
                        "description_ar": "معدلات البذر المتغيرة بناءً على إمكانات الحقل",
                        "strategy": "More seeds to high-potential areas",
                    },
                    {
                        "type": "lime",
                        "name": "Lime",
                        "name_ar": "جير",
                        "description": "Variable lime application for pH correction",
                        "description_ar": "تطبيق الجير المتغير لتصحيح الحموضة",
                        "strategy": "More lime to acidic (low NDVI) areas",
                    },
                    {
                        "type": "pesticide",
                        "name": "Pesticide",
                        "name_ar": "مبيدات",
                        "description": "Variable pesticide application targeting problem areas",
                        "description_ar": "تطبيق المبيدات المتغير لاستهداف المناطق المشكلة",
                        "strategy": "Target high-vigor areas where pests thrive",
                    },
                    {
                        "type": "irrigation",
                        "name": "Irrigation",
                        "name_ar": "ري",
                        "description": "Variable water application based on stress indicators",
                        "description_ar": "تطبيق الماء المتغير بناءً على مؤشرات الإجهاد",
                        "strategy": "More water to stressed (low NDVI) areas",
                    },
                ],
                "zone_methods": [
                    {
                        "method": "ndvi",
                        "name": "NDVI-Based",
                        "name_ar": "بناءً على NDVI",
                        "description": "Zones based on vegetation index",
                    },
                    {
                        "method": "yield",
                        "name": "Yield-Based",
                        "name_ar": "بناءً على الإنتاج",
                        "description": "Zones based on historical yield data",
                    },
                    {
                        "method": "soil",
                        "name": "Soil-Based",
                        "name_ar": "بناءً على التربة",
                        "description": "Zones based on soil analysis",
                    },
                    {
                        "method": "combined",
                        "name": "Combined",
                        "name_ar": "مجمع",
                        "description": "Multi-factor zone classification",
                    },
                ],
                "supported_zones": [3, 5],
                "export_formats": ["geojson", "shapefile", "isoxml"],
            },
            "benefits": {
                "en": [
                    "Optimize input use and reduce costs",
                    "Improve crop yield and quality",
                    "Reduce environmental impact",
                    "Equipment-compatible prescriptions",
                    "Data-driven precision agriculture",
                ],
                "ar": [
                    "تحسين استخدام المدخلات وتقليل التكاليف",
                    "تحسين إنتاجية المحاصيل وجودتها",
                    "تقليل الأثر البيئي",
                    "وصفات متوافقة مع المعدات",
                    "زراعة دقيقة قائمة على البيانات",
                ],
            },
        }

    logger.info("VRA endpoints registered successfully")
