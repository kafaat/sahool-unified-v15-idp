"""
Satellite Tool
أداة الأقمار الصناعية

Tool for calling the satellite-service.
أداة لاستدعاء خدمة الأقمار الصناعية.
"""

import httpx
from typing import Dict, Any, Optional, List
import structlog

from ..config import settings

logger = structlog.get_logger()


class SatelliteTool:
    """
    Tool to interact with satellite-service
    أداة للتفاعل مع خدمة الأقمار الصناعية
    """

    def __init__(self):
        self.base_url = settings.satellite_service_url
        self.timeout = 60.0  # Satellite processing can take longer

    async def get_ndvi(
        self,
        field_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get NDVI data for a field
        الحصول على بيانات NDVI لحقل

        Args:
            field_id: Field identifier | معرف الحقل
            start_date: Start date (YYYY-MM-DD) | تاريخ البداية
            end_date: End date (YYYY-MM-DD) | تاريخ النهاية

        Returns:
            NDVI data | بيانات NDVI
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {"field_id": field_id}
                if start_date:
                    params["start_date"] = start_date
                if end_date:
                    params["end_date"] = end_date

                response = await client.get(
                    f"{self.base_url}/api/v1/satellite/ndvi", params=params
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "ndvi_data_retrieved",
                    field_id=field_id,
                    data_points=len(result.get("data", [])),
                )
                return result

        except httpx.HTTPError as e:
            logger.error("ndvi_retrieval_failed", error=str(e), field_id=field_id)
            return {"error": str(e), "status": "failed"}

    async def get_field_imagery(
        self,
        field_id: str,
        layer: str = "true_color",
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get satellite imagery for a field
        الحصول على صور الأقمار الصناعية لحقل

        Args:
            field_id: Field identifier | معرف الحقل
            layer: Image layer type (true_color, ndvi, evi, etc.) | نوع طبقة الصورة
            date: Specific date (YYYY-MM-DD) | تاريخ محدد

        Returns:
            Satellite imagery data | بيانات صور الأقمار الصناعية
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "field_id": field_id,
                    "layer": layer,
                }
                if date:
                    params["date"] = date

                response = await client.get(
                    f"{self.base_url}/api/v1/satellite/imagery", params=params
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "satellite_imagery_retrieved",
                    field_id=field_id,
                    layer=layer,
                    date=date or "latest",
                )
                return result

        except httpx.HTTPError as e:
            logger.error("satellite_imagery_failed", error=str(e), field_id=field_id)
            return {"error": str(e), "status": "failed"}

    async def analyze_field_zones(
        self,
        field_id: str,
        analysis_type: str = "variability",
    ) -> Dict[str, Any]:
        """
        Analyze field zones based on satellite data
        تحليل مناطق الحقل بناءً على بيانات الأقمار الصناعية

        Args:
            field_id: Field identifier | معرف الحقل
            analysis_type: Type of analysis (variability, stress, etc.) | نوع التحليل

        Returns:
            Zone analysis results | نتائج تحليل المناطق
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/satellite/analyze-zones",
                    json={
                        "field_id": field_id,
                        "analysis_type": analysis_type,
                    },
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "field_zones_analyzed",
                    field_id=field_id,
                    analysis_type=analysis_type,
                    zones=len(result.get("zones", [])),
                )
                return result

        except httpx.HTTPError as e:
            logger.error("field_zones_analysis_failed", error=str(e), field_id=field_id)
            return {"error": str(e), "status": "failed"}

    async def get_time_series(
        self,
        field_id: str,
        start_date: str,
        end_date: str,
        index: str = "ndvi",
    ) -> Dict[str, Any]:
        """
        Get time series data for vegetation indices
        الحصول على بيانات السلسلة الزمنية لمؤشرات الغطاء النباتي

        Args:
            field_id: Field identifier | معرف الحقل
            index: Vegetation index (ndvi, evi, savi, etc.) | مؤشر الغطاء النباتي
            start_date: Start date (YYYY-MM-DD) | تاريخ البداية
            end_date: End date (YYYY-MM-DD) | تاريخ النهاية

        Returns:
            Time series data | بيانات السلسلة الزمنية
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/satellite/time-series",
                    params={
                        "field_id": field_id,
                        "index": index,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "time_series_retrieved",
                    field_id=field_id,
                    index=index,
                    period=f"{start_date} to {end_date}",
                )
                return result

        except httpx.HTTPError as e:
            logger.error("time_series_failed", error=str(e), field_id=field_id)
            return {"error": str(e), "status": "failed"}

    async def detect_changes(
        self,
        field_id: str,
        baseline_date: str,
        comparison_date: str,
    ) -> Dict[str, Any]:
        """
        Detect changes between two dates
        كشف التغيرات بين تاريخين

        Args:
            field_id: Field identifier | معرف الحقل
            baseline_date: Baseline date (YYYY-MM-DD) | تاريخ الأساس
            comparison_date: Comparison date (YYYY-MM-DD) | تاريخ المقارنة

        Returns:
            Change detection results | نتائج كشف التغيرات
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/satellite/detect-changes",
                    json={
                        "field_id": field_id,
                        "baseline_date": baseline_date,
                        "comparison_date": comparison_date,
                    },
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "change_detection_complete",
                    field_id=field_id,
                    baseline_date=baseline_date,
                    comparison_date=comparison_date,
                )
                return result

        except httpx.HTTPError as e:
            logger.error("change_detection_failed", error=str(e), field_id=field_id)
            return {"error": str(e), "status": "failed"}
