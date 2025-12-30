"""
Crop Health Tool
أداة صحة المحاصيل

Tool for calling the crop-health-ai service.
أداة لاستدعاء خدمة الذكاء الاصطناعي لصحة المحاصيل.
"""

import httpx
from typing import Dict, Any, Optional
import structlog

from ..config import settings

logger = structlog.get_logger()


class CropHealthTool:
    """
    Tool to interact with crop-health-ai service
    أداة للتفاعل مع خدمة الذكاء الاصطناعي لصحة المحاصيل
    """

    def __init__(self):
        self.base_url = settings.crop_health_ai_url
        self.timeout = 30.0

    async def analyze_image(
        self,
        image_path: str,
        crop_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze crop image for disease detection
        تحليل صورة المحصول لكشف الأمراض

        Args:
            image_path: Path to crop image | مسار صورة المحصول
            crop_type: Type of crop (optional) | نوع المحصول (اختياري)

        Returns:
            Analysis results | نتائج التحليل
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # In real implementation, upload image as multipart/form-data
                # في التنفيذ الحقيقي، قم بتحميل الصورة كـ multipart/form-data
                data = {
                    "image_path": image_path,
                    "crop_type": crop_type,
                }

                response = await client.post(
                    f"{self.base_url}/api/v1/analyze",
                    json=data
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "crop_health_analysis_success",
                    image_path=image_path,
                    detected_issues=len(result.get("detections", []))
                )
                return result

        except httpx.HTTPError as e:
            logger.error(
                "crop_health_analysis_failed",
                error=str(e),
                image_path=image_path
            )
            return {
                "error": str(e),
                "status": "failed"
            }

    async def get_disease_info(
        self,
        disease_name: str,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Get information about a specific disease
        الحصول على معلومات عن مرض معين

        Args:
            disease_name: Name of the disease | اسم المرض
            language: Response language (en/ar) | لغة الاستجابة

        Returns:
            Disease information | معلومات المرض
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/diseases/{disease_name}",
                    params={"language": language}
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "disease_info_retrieved",
                    disease_name=disease_name,
                    language=language
                )
                return result

        except httpx.HTTPError as e:
            logger.error(
                "disease_info_failed",
                error=str(e),
                disease_name=disease_name
            )
            return {
                "error": str(e),
                "status": "failed"
            }

    async def get_treatment_options(
        self,
        disease_name: str,
        crop_type: str,
        severity: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get treatment options for a disease
        الحصول على خيارات العلاج لمرض

        Args:
            disease_name: Name of the disease | اسم المرض
            crop_type: Type of crop | نوع المحصول
            severity: Disease severity level | مستوى خطورة المرض

        Returns:
            Treatment options | خيارات العلاج
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "crop_type": crop_type,
                }
                if severity:
                    params["severity"] = severity

                response = await client.get(
                    f"{self.base_url}/api/v1/diseases/{disease_name}/treatments",
                    params=params
                )
                response.raise_for_status()

                result = response.json()
                logger.info(
                    "treatment_options_retrieved",
                    disease_name=disease_name,
                    crop_type=crop_type
                )
                return result

        except httpx.HTTPError as e:
            logger.error(
                "treatment_options_failed",
                error=str(e),
                disease_name=disease_name
            )
            return {
                "error": str(e),
                "status": "failed"
            }
