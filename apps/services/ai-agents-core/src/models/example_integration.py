"""
Example Integration of Disease CNN Model with SAHOOL AI Agents
مثال على دمج نموذج CNN للأمراض مع وكلاء SAHOOL الذكيين

This script demonstrates how to integrate the DiseaseCNNModel with the existing
AI agents system and FastAPI endpoints.

يوضح هذا النص كيفية دمج DiseaseCNNModel مع نظام الوكلاء الذكيين الحالي
ونقاط نهاية FastAPI.
"""

import asyncio
import logging
from typing import Any

import numpy as np
from disease_cnn import DiseaseCNNModel

# Configure logging - تكوين السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiseaseDetectionAgent:
    """
    Disease Detection Agent using CNN Model
    وكيل اكتشاف الأمراض باستخدام نموذج CNN

    This agent wraps the DiseaseCNNModel and provides high-level
    disease detection capabilities for the SAHOOL system.

    يغلف هذا الوكيل DiseaseCNNModel ويوفر إمكانيات اكتشاف
    الأمراض عالية المستوى لنظام SAHOOL.
    """

    def __init__(self, model_path: str = None, enable_gpu: bool = True):
        """
        Initialize Disease Detection Agent
        تهيئة وكيل اكتشاف الأمراض

        Args:
            model_path: Path to pre-trained model - مسار النموذج المدرب مسبقاً
            enable_gpu: Enable GPU acceleration - تفعيل تسريع GPU
        """
        self.model = DiseaseCNNModel(
            model_path=model_path, framework="tensorflow", enable_gpu=enable_gpu
        )

        if model_path:
            self.model.load_model(model_path)
            self.model.warm_up_model()

        logger.info("Disease Detection Agent initialized")

    async def analyze_plant_health(
        self, image: Any, field_id: str = None, crop_type: str = None
    ) -> dict[str, Any]:
        """
        Analyze plant health from image
        تحليل صحة النبات من الصورة

        Args:
            image: Plant image - صورة النبات
            field_id: Field identifier - معرف الحقل
            crop_type: Type of crop - نوع المحصول

        Returns:
            Analysis results - نتائج التحليل
        """
        try:
            # Get top-k predictions - الحصول على أعلى k تنبؤات
            predictions = self.model.get_top_k_predictions(image, k=3)

            # Primary diagnosis - التشخيص الأساسي
            primary = predictions[0]

            # Determine action required - تحديد الإجراء المطلوب
            action_required = primary["severity"] in ["high", "critical"]

            result = {
                "field_id": field_id,
                "crop_type": crop_type,
                "diagnosis": {
                    "disease": primary["disease"],
                    "disease_ar": primary["disease_ar"],
                    "confidence": primary["confidence"],
                    "severity": primary["severity"],
                },
                "alternative_diagnoses": predictions[1:],
                "action_required": action_required,
                "recommended_treatment": primary["treatment_ar"],
                "all_predictions": predictions,
            }

            # Add alerts for critical conditions - إضافة تنبيهات للظروف الحرجة
            if primary["severity"] == "critical":
                result["alert"] = {
                    "level": "urgent",
                    "message": f"كشف مرض خطير: {primary['disease_ar']}",
                    "action": "اتخاذ إجراء فوري مطلوب",
                }

            return result

        except Exception as e:
            logger.error(f"Error analyzing plant health: {e}")
            raise

    async def analyze_field_batch(
        self, field_id: str, images: list[Any], crop_type: str = None
    ) -> dict[str, Any]:
        """
        Analyze entire field from multiple images
        تحليل الحقل بالكامل من صور متعددة

        Args:
            field_id: Field identifier - معرف الحقل
            images: List of field images - قائمة صور الحقل
            crop_type: Type of crop - نوع المحصول

        Returns:
            Field analysis report - تقرير تحليل الحقل
        """
        try:
            logger.info(f"Analyzing field {field_id} with {len(images)} images")

            # Process field images - معالجة صور الحقل
            report = await self.model.process_field_images(
                field_id=field_id, images=images, min_confidence=0.6
            )

            # Add crop-specific information - إضافة معلومات خاصة بالمحصول
            if crop_type:
                report["crop_type"] = crop_type
                report["crop_type_ar"] = self._get_crop_name_ar(crop_type)

            # Generate action plan - إنشاء خطة العمل
            action_plan = self._generate_action_plan(report)
            report["action_plan"] = action_plan

            return report

        except Exception as e:
            logger.error(f"Error analyzing field batch: {e}")
            raise

    def _get_crop_name_ar(self, crop_type: str) -> str:
        """
        Get Arabic name for crop type
        الحصول على الاسم العربي لنوع المحصول
        """
        crop_names = {
            "tomato": "طماطم",
            "wheat": "قمح",
            "grape": "عنب",
            "date_palm": "نخيل",
            "coffee": "بن",
            "banana": "موز",
            "mango": "مانجو",
        }
        return crop_names.get(crop_type, crop_type)

    def _generate_action_plan(self, report: dict[str, Any]) -> dict[str, Any]:
        """
        Generate actionable plan based on field analysis
        إنشاء خطة عملية بناءً على تحليل الحقل
        """
        health_percentage = report.get("health_percentage", 0)
        recommendations = report.get("recommendations", [])

        action_plan = {
            "immediate_actions": [],
            "short_term_actions": [],
            "monitoring_schedule": {},
            "estimated_cost": 0.0,
        }

        # Immediate actions for critical diseases - إجراءات فورية للأمراض الحرجة
        critical_diseases = [rec for rec in recommendations if rec["severity"] == "critical"]

        if critical_diseases:
            for disease in critical_diseases:
                action_plan["immediate_actions"].append(
                    {
                        "action": f"معالجة {disease['disease_ar']}",
                        "treatment": disease["treatment_ar"],
                        "affected_areas": disease["affected_count"],
                        "priority": "urgent",
                    }
                )

        # Short-term actions - إجراءات قصيرة المدى
        if health_percentage < 70:
            action_plan["short_term_actions"].append(
                {"action": "زيادة مراقبة الحقل", "frequency": "يومي", "duration": "أسبوعين"}
            )

        # Monitoring schedule - جدول المراقبة
        if health_percentage < 80:
            action_plan["monitoring_schedule"] = {
                "frequency": "يومي",
                "duration_weeks": 2,
                "focus_areas": ["المناطق المصابة", "النباتات المجاورة"],
            }
        else:
            action_plan["monitoring_schedule"] = {
                "frequency": "أسبوعي",
                "duration_weeks": 4,
                "focus_areas": ["الفحص العام"],
            }

        return action_plan

    def get_agent_status(self) -> dict[str, Any]:
        """
        Get agent status and metrics
        الحصول على حالة الوكيل والمقاييس
        """
        return {
            "agent_type": "disease_detection",
            "model_status": "active" if self.model.model else "not_loaded",
            "model_version": self.model.get_model_version(),
            "is_warmed_up": self.model.is_warmed_up,
            "metrics": self.model.get_metrics(),
        }


# Example usage with FastAPI integration
# مثال على الاستخدام مع تكامل FastAPI


async def example_single_image_analysis():
    """
    Example: Analyze single plant image
    مثال: تحليل صورة نبات واحدة
    """
    print("=" * 60)
    print("Example 1: Single Image Analysis")
    print("مثال 1: تحليل صورة واحدة")
    print("=" * 60)

    # Initialize agent - تهيئة الوكيل
    DiseaseDetectionAgent(enable_gpu=False)

    # Note: In production, load actual model
    # ملاحظة: في الإنتاج، قم بتحميل النموذج الفعلي
    # agent.model.load_model("/path/to/model.h5")

    # Create dummy image for demonstration - إنشاء صورة وهمية للعرض
    np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)

    # Analyze - تحليل
    # result = await agent.analyze_plant_health(
    #     image=dummy_image,
    #     field_id="FIELD-001",
    #     crop_type="tomato"
    # )

    print("\nAnalysis would return:")
    print("- Disease diagnosis (primary and alternatives)")
    print("- Confidence scores")
    print("- Recommended treatments")
    print("- Action required flag")
    print("\nالتحليل سيعيد:")
    print("- تشخيص المرض (الأساسي والبدائل)")
    print("- درجات الثقة")
    print("- العلاجات الموصى بها")
    print("- علامة الإجراء المطلوب")


async def example_field_batch_analysis():
    """
    Example: Analyze entire field
    مثال: تحليل الحقل بالكامل
    """
    print("\n" + "=" * 60)
    print("Example 2: Field Batch Analysis")
    print("مثال 2: تحليل الحقل الدفعي")
    print("=" * 60)

    # Initialize agent - تهيئة الوكيل
    DiseaseDetectionAgent(enable_gpu=False)

    # Create dummy images - إنشاء صور وهمية
    [np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8) for _ in range(10)]

    # Analyze field - تحليل الحقل
    # report = await agent.analyze_field_batch(
    #     field_id="FIELD-001",
    #     images=field_images,
    #     crop_type="wheat"
    # )

    print("\nField report would include:")
    print("- Total images analyzed")
    print("- Disease distribution")
    print("- Health percentage")
    print("- Field status (healthy/moderate/critical)")
    print("- Detailed recommendations")
    print("- Action plan")
    print("\nتقرير الحقل سيتضمن:")
    print("- إجمالي الصور المحللة")
    print("- توزيع الأمراض")
    print("- نسبة الصحة")
    print("- حالة الحقل (سليم/متوسط/حرج)")
    print("- توصيات مفصلة")
    print("- خطة العمل")


async def example_fastapi_integration():
    """
    Example: FastAPI integration
    مثال: تكامل FastAPI
    """
    print("\n" + "=" * 60)
    print("Example 3: FastAPI Integration")
    print("مثال 3: تكامل FastAPI")
    print("=" * 60)

    print("\nFastAPI endpoint would look like:")
    print("""
    @app.post("/api/v1/detect-disease")
    async def detect_disease(file: UploadFile = File(...)):
        # Read image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # Analyze
        result = await disease_agent.analyze_plant_health(image)

        return {
            "success": True,
            "diagnosis": result
        }
    """)

    print("\nنقطة نهاية FastAPI ستبدو هكذا:")
    print("- قراءة الصورة المرفوعة")
    print("- تحليل صحة النبات")
    print("- إرجاع التشخيص والتوصيات")


async def example_monitoring_integration():
    """
    Example: Integration with monitoring system
    مثال: التكامل مع نظام المراقبة
    """
    print("\n" + "=" * 60)
    print("Example 4: Monitoring System Integration")
    print("مثال 4: التكامل مع نظام المراقبة")
    print("=" * 60)

    agent = DiseaseDetectionAgent(enable_gpu=False)

    # Get agent status - الحصول على حالة الوكيل
    status = agent.get_agent_status()

    print("\nAgent Status:")
    print(f"- Agent Type: {status['agent_type']}")
    print(f"- Model Status: {status['model_status']}")
    print(f"- Model Version: {status['model_version']}")
    print(f"- Warmed Up: {status['is_warmed_up']}")
    print("\nحالة الوكيل:")
    print("- نوع الوكيل، حالة النموذج، إصدار النموذج")
    print("- المقاييس: إجمالي التنبؤات، متوسط الوقت، معدل الأخطاء")


async def main():
    """
    Run all examples
    تشغيل جميع الأمثلة
    """
    print("\n" + "=" * 60)
    print("SAHOOL Disease Detection CNN - Integration Examples")
    print("أمثلة تكامل نموذج CNN لاكتشاف الأمراض في SAHOOL")
    print("=" * 60)

    # Run examples - تشغيل الأمثلة
    await example_single_image_analysis()
    await example_field_batch_analysis()
    await example_fastapi_integration()
    await example_monitoring_integration()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("اكتملت الأمثلة!")
    print("=" * 60)


if __name__ == "__main__":
    # Run examples - تشغيل الأمثلة
    asyncio.run(main())
