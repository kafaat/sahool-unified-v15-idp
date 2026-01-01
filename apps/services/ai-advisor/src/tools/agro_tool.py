"""
Agro Tool
أداة الاستشارات الزراعية

Tool for calling the agro-advisor service.
أداة لاستدعاء خدمة المستشار الزراعي.
"""

import httpx
from typing import Dict, Any, Optional, List
import structlog

from ..config import settings

logger = structlog.get_logger()


class AgroTool:
    """
    Tool to interact with agro-advisor service
    أداة للتفاعل مع خدمة المستشار الزراعي
    """

    def __init__(self):
        self.base_url = settings.agro_advisor_url
        self.timeout = 30.0

    async def get_crop_info(
        self,
        crop_type: str,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Get information about a crop
        الحصول على معلومات عن محصول

        Args:
            crop_type: Type of crop | نوع المحصول
            language: Response language (en/ar) | لغة الاستجابة

        Returns:
            Crop information | معلومات المحصول
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/crops/{crop_type}",
                    params={"language": language},
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "crop_info_retrieved", crop_type=crop_type, language=language
                )
                return result

        except httpx.HTTPError as e:
            logger.error("crop_info_failed", error=str(e), crop_type=crop_type)
            return {"error": str(e), "status": "failed"}

    async def get_growth_stage_info(
        self,
        crop_type: str,
        growth_stage: str,
    ) -> Dict[str, Any]:
        """
        Get information about a specific growth stage
        الحصول على معلومات عن مرحلة نمو معينة

        Args:
            crop_type: Type of crop | نوع المحصول
            growth_stage: Growth stage name | اسم مرحلة النمو

        Returns:
            Growth stage information | معلومات مرحلة النمو
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/crops/{crop_type}/stages/{growth_stage}"
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "growth_stage_info_retrieved",
                    crop_type=crop_type,
                    growth_stage=growth_stage,
                )
                return result

        except httpx.HTTPError as e:
            logger.error(
                "growth_stage_info_failed",
                error=str(e),
                crop_type=crop_type,
                growth_stage=growth_stage,
            )
            return {"error": str(e), "status": "failed"}

    async def get_fertilizer_recommendation(
        self,
        crop_type: str,
        growth_stage: str,
        soil_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Get fertilizer recommendations
        الحصول على توصيات التسميد

        Args:
            crop_type: Type of crop | نوع المحصول
            growth_stage: Current growth stage | مرحلة النمو الحالية
            soil_analysis: Soil test results | نتائج تحليل التربة

        Returns:
            Fertilizer recommendations | توصيات التسميد
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/fertilizer/recommend",
                    json={
                        "crop_type": crop_type,
                        "growth_stage": growth_stage,
                        "soil_analysis": soil_analysis,
                    },
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "fertilizer_recommendation_generated",
                    crop_type=crop_type,
                    growth_stage=growth_stage,
                )
                return result

        except httpx.HTTPError as e:
            logger.error(
                "fertilizer_recommendation_failed", error=str(e), crop_type=crop_type
            )
            return {"error": str(e), "status": "failed"}

    async def get_pest_control_advice(
        self,
        crop_type: str,
        pest_type: str,
        infestation_level: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get pest control advice
        الحصول على نصائح مكافحة الآفات

        Args:
            crop_type: Type of crop | نوع المحصول
            pest_type: Type of pest | نوع الآفة
            infestation_level: Level of infestation | مستوى الإصابة

        Returns:
            Pest control recommendations | توصيات مكافحة الآفات
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                data = {
                    "crop_type": crop_type,
                    "pest_type": pest_type,
                }
                if infestation_level:
                    data["infestation_level"] = infestation_level

                response = await client.post(
                    f"{self.base_url}/api/v1/pest-control/advise", json=data
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "pest_control_advice_generated",
                    crop_type=crop_type,
                    pest_type=pest_type,
                )
                return result

        except httpx.HTTPError as e:
            logger.error(
                "pest_control_advice_failed",
                error=str(e),
                crop_type=crop_type,
                pest_type=pest_type,
            )
            return {"error": str(e), "status": "failed"}

    async def get_best_practices(
        self,
        crop_type: str,
        region: Optional[str] = None,
        season: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get best agricultural practices
        الحصول على أفضل الممارسات الزراعية

        Args:
            crop_type: Type of crop | نوع المحصول
            region: Geographic region | المنطقة الجغرافية
            season: Growing season | الموسم الزراعي

        Returns:
            Best practices | أفضل الممارسات
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {"crop_type": crop_type}
                if region:
                    params["region"] = region
                if season:
                    params["season"] = season

                response = await client.get(
                    f"{self.base_url}/api/v1/best-practices", params=params
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "best_practices_retrieved",
                    crop_type=crop_type,
                    region=region,
                    season=season,
                )
                return result

        except httpx.HTTPError as e:
            logger.error("best_practices_failed", error=str(e), crop_type=crop_type)
            return {"error": str(e), "status": "failed"}

    async def get_market_prices(
        self,
        crop_type: str,
        region: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get market price information
        الحصول على معلومات أسعار السوق

        Args:
            crop_type: Type of crop | نوع المحصول
            region: Market region | منطقة السوق

        Returns:
            Market price data | بيانات أسعار السوق
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {"crop_type": crop_type}
                if region:
                    params["region"] = region

                response = await client.get(
                    f"{self.base_url}/api/v1/market/prices", params=params
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "market_prices_retrieved", crop_type=crop_type, region=region
                )
                return result

        except httpx.HTTPError as e:
            logger.error("market_prices_failed", error=str(e), crop_type=crop_type)
            return {"error": str(e), "status": "failed"}
