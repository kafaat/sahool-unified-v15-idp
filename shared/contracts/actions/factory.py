"""
SAHOOL Action Template Factory
مصنع قوالب الإجراءات

يوفر طرق سهلة لإنشاء ActionTemplates من خدمات التحليل المختلفة
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

from .types import ActionType, UrgencyLevel, ResourceType
from .template import ActionTemplate, ActionStep, Resource, TimeWindow


class ActionTemplateFactory:
    """
    مصنع لإنشاء قوالب الإجراءات

    يوفر طرق مساعدة لتسهيل إنشاء ActionTemplates من الخدمات المختلفة
    """

    @staticmethod
    def create_irrigation_action(
        field_id: str,
        water_amount_liters: float,
        duration_minutes: int,
        urgency: UrgencyLevel,
        confidence: float,
        soil_moisture_percent: Optional[float] = None,
        source_analysis_id: Optional[str] = None,
        method: str = "drip",
        deadline: Optional[datetime] = None,
    ) -> ActionTemplate:
        """إنشاء إجراء ري"""

        method_ar = {
            "drip": "تنقيط",
            "sprinkler": "رش",
            "flood": "غمر",
            "furrow": "أخاديد",
        }.get(method, method)

        reasoning_ar = (
            f"رطوبة التربة: {soil_moisture_percent}%"
            if soil_moisture_percent
            else "بناءً على تحليل احتياجات المحصول"
        )

        steps = [
            ActionStep(
                step_number=1,
                title_ar="فحص نظام الري",
                title_en="Check irrigation system",
                description_ar="تأكد من عمل المضخة والأنابيب بشكل صحيح",
                description_en="Ensure pump and pipes are working correctly",
                duration_minutes=10,
            ),
            ActionStep(
                step_number=2,
                title_ar="تشغيل الري",
                title_en="Start irrigation",
                description_ar=f"شغّل نظام الري بطريقة {method_ar} لمدة {duration_minutes} دقيقة",
                description_en=f"Run {method} irrigation for {duration_minutes} minutes",
                duration_minutes=duration_minutes,
                requires_confirmation=True,
            ),
            ActionStep(
                step_number=3,
                title_ar="التحقق من التغطية",
                title_en="Verify coverage",
                description_ar="تأكد من وصول المياه لجميع أجزاء الحقل",
                description_en="Ensure water reaches all field areas",
                duration_minutes=15,
                requires_photo=True,
            ),
        ]

        resources = [
            Resource(
                resource_type=ResourceType.WATER,
                name_ar="مياه",
                name_en="Water",
                quantity=water_amount_liters,
                unit="liters",
                unit_ar="لتر",
            )
        ]

        return ActionTemplate(
            action_type=ActionType.IRRIGATION,
            title_ar=f"ري الحقل - {urgency.label_ar}",
            title_en=f"Field Irrigation - {urgency.value.capitalize()}",
            description_ar=f"يُنصح بري الحقل بكمية {water_amount_liters:,.0f} لتر باستخدام نظام {method_ar}",
            description_en=f"Irrigate field with {water_amount_liters:,.0f} liters using {method} system",
            summary_ar=f"ري {water_amount_liters:,.0f} لتر - {urgency.label_ar}",
            source_service="irrigation-smart",
            source_analysis_id=source_analysis_id,
            source_analysis_type="irrigation_recommendation",
            confidence=confidence,
            reasoning_ar=reasoning_ar,
            reasoning_en=(
                f"Soil moisture: {soil_moisture_percent}%"
                if soil_moisture_percent
                else "Based on crop water needs analysis"
            ),
            urgency=urgency,
            deadline=deadline
            or datetime.utcnow() + timedelta(hours=urgency.max_delay_hours),
            field_id=field_id,
            steps=steps,
            resources_needed=resources,
            estimated_duration_minutes=duration_minutes + 25,
            offline_executable=True,
            fallback_instructions_ar=f"في حال عدم توفر البيانات: قم بري الحقل لمدة {duration_minutes} دقيقة في الصباح الباكر (قبل الساعة 8)",
            fallback_instructions_en=f"If data unavailable: Irrigate field for {duration_minutes} minutes in early morning (before 8 AM)",
            tags=["irrigation", method, urgency.value],
        )

    @staticmethod
    def create_fertilization_action(
        field_id: str,
        fertilizer_type: str,
        quantity_kg: float,
        urgency: UrgencyLevel,
        confidence: float,
        application_method: str = "broadcast",
        npk_ratio: Optional[str] = None,
        source_analysis_id: Optional[str] = None,
        deadline: Optional[datetime] = None,
    ) -> ActionTemplate:
        """إنشاء إجراء تسميد"""

        fertilizer_names = {
            "urea": ("يوريا", "Urea"),
            "dap": ("داب", "DAP"),
            "npk_15_15_15": ("NPK متوازن", "Balanced NPK"),
            "npk_20_20_20": ("NPK مركز", "Concentrated NPK"),
            "potassium_sulfate": ("سلفات البوتاسيوم", "Potassium Sulfate"),
            "organic_compost": ("سماد عضوي", "Organic Compost"),
        }

        method_names = {
            "broadcast": ("نثر", "Broadcast"),
            "side_dressing": ("جانبي", "Side Dressing"),
            "fertigation": ("مع الري", "Fertigation"),
            "foliar": ("رش ورقي", "Foliar Spray"),
        }

        fert_ar, fert_en = fertilizer_names.get(
            fertilizer_type, (fertilizer_type, fertilizer_type)
        )
        method_ar, method_en = method_names.get(
            application_method, (application_method, application_method)
        )

        steps = [
            ActionStep(
                step_number=1,
                title_ar="تحضير السماد",
                title_en="Prepare fertilizer",
                description_ar=f"قم بوزن {quantity_kg:.1f} كجم من {fert_ar}",
                description_en=f"Weigh {quantity_kg:.1f} kg of {fert_en}",
                duration_minutes=10,
            ),
            ActionStep(
                step_number=2,
                title_ar="تطبيق السماد",
                title_en="Apply fertilizer",
                description_ar=f"وزّع السماد بطريقة {method_ar} على الحقل",
                description_en=f"Distribute fertilizer using {method_en} method",
                duration_minutes=45,
                safety_notes_ar="ارتدِ قفازات وكمامة أثناء التطبيق",
                safety_notes_en="Wear gloves and mask during application",
            ),
            ActionStep(
                step_number=3,
                title_ar="الري بعد التسميد",
                title_en="Post-fertilization irrigation",
                description_ar="قم بري خفيف لمساعدة امتصاص السماد",
                description_en="Light irrigation to help fertilizer absorption",
                duration_minutes=30,
                requires_confirmation=True,
            ),
        ]

        resource_type = {
            "urea": ResourceType.FERTILIZER_UREA,
            "dap": ResourceType.FERTILIZER_DAP,
            "organic_compost": ResourceType.FERTILIZER_ORGANIC,
        }.get(fertilizer_type, ResourceType.FERTILIZER_NPK)

        resources = [
            Resource(
                resource_type=resource_type,
                name_ar=fert_ar,
                name_en=fert_en,
                quantity=quantity_kg,
                unit="kg",
                unit_ar="كجم",
            )
        ]

        return ActionTemplate(
            action_type=ActionType.FERTILIZATION,
            title_ar=f"تسميد الحقل - {fert_ar}",
            title_en=f"Field Fertilization - {fert_en}",
            description_ar=f"يُنصح بإضافة {quantity_kg:.1f} كجم من {fert_ar} بطريقة {method_ar}",
            description_en=f"Apply {quantity_kg:.1f} kg of {fert_en} using {method_en} method",
            summary_ar=f"تسميد {quantity_kg:.1f} كجم {fert_ar}",
            source_service="fertilizer-advisor",
            source_analysis_id=source_analysis_id,
            source_analysis_type="npk_recommendation",
            confidence=confidence,
            reasoning_ar=(
                f"نسبة NPK الموصى بها: {npk_ratio}"
                if npk_ratio
                else "بناءً على تحليل التربة"
            ),
            reasoning_en=(
                f"Recommended NPK ratio: {npk_ratio}"
                if npk_ratio
                else "Based on soil analysis"
            ),
            urgency=urgency,
            deadline=deadline
            or datetime.utcnow() + timedelta(hours=urgency.max_delay_hours),
            field_id=field_id,
            steps=steps,
            resources_needed=resources,
            estimated_duration_minutes=85,
            offline_executable=True,
            fallback_instructions_ar=f"في حال عدم توفر البيانات: أضف {quantity_kg:.1f} كجم من {fert_ar} في الصباح الباكر، ثم اروِ الحقل",
            fallback_instructions_en=f"If data unavailable: Apply {quantity_kg:.1f} kg of {fert_en} in early morning, then irrigate",
            tags=["fertilization", fertilizer_type, application_method],
        )

    @staticmethod
    def create_disease_inspection_action(
        field_id: str,
        disease_name_ar: str,
        disease_name_en: str,
        confidence: float,
        affected_area_percent: float,
        urgency: UrgencyLevel = UrgencyLevel.HIGH,
        zone_ids: Optional[List[str]] = None,
        source_analysis_id: Optional[str] = None,
        recommended_treatment: Optional[str] = None,
    ) -> ActionTemplate:
        """إنشاء إجراء فحص مرض"""

        steps = [
            ActionStep(
                step_number=1,
                title_ar="الفحص البصري",
                title_en="Visual inspection",
                description_ar=f"افحص النباتات في المنطقة المحددة بحثاً عن أعراض {disease_name_ar}",
                description_en=f"Inspect plants in the affected area for {disease_name_en} symptoms",
                duration_minutes=30,
                requires_photo=True,
            ),
            ActionStep(
                step_number=2,
                title_ar="تحديد نطاق الإصابة",
                title_en="Assess infection scope",
                description_ar="حدد المناطق المصابة وقدّر نسبة الإصابة",
                description_en="Mark infected areas and estimate infection percentage",
                duration_minutes=20,
                requires_confirmation=True,
            ),
            ActionStep(
                step_number=3,
                title_ar="جمع عينات",
                title_en="Collect samples",
                description_ar="اجمع عينات من الأوراق/الثمار المصابة للتحليل",
                description_en="Collect samples of infected leaves/fruits for analysis",
                duration_minutes=15,
                requires_photo=True,
            ),
        ]

        return ActionTemplate(
            action_type=ActionType.INSPECTION_DISEASE,
            title_ar=f"فحص مرض - {disease_name_ar}",
            title_en=f"Disease Inspection - {disease_name_en}",
            description_ar=f"تم اكتشاف احتمال إصابة بـ{disease_name_ar} بنسبة ثقة {confidence*100:.0f}%، المنطقة المتأثرة: {affected_area_percent:.1f}%",
            description_en=f"Possible {disease_name_en} infection detected with {confidence*100:.0f}% confidence, affected area: {affected_area_percent:.1f}%",
            summary_ar=f"اشتباه {disease_name_ar} - {affected_area_percent:.0f}% من الحقل",
            source_service="crop-health-ai",
            source_analysis_id=source_analysis_id,
            source_analysis_type="disease_detection",
            confidence=confidence,
            reasoning_ar=f"تحليل الصور الفضائية كشف أنماط مشابهة لأعراض {disease_name_ar}",
            reasoning_en=f"Satellite image analysis detected patterns similar to {disease_name_en} symptoms",
            urgency=urgency,
            deadline=datetime.utcnow() + timedelta(hours=24),
            field_id=field_id,
            zone_ids=zone_ids or [],
            steps=steps,
            resources_needed=[],
            estimated_duration_minutes=65,
            offline_executable=True,
            fallback_instructions_ar=f"افحص الحقل يدوياً بحثاً عن: بقع على الأوراق، ذبول، تغير اللون. التقط صوراً للنباتات المشتبه بإصابتها",
            fallback_instructions_en=f"Manually inspect field for: leaf spots, wilting, discoloration. Take photos of suspected infected plants",
            tags=["inspection", "disease", disease_name_en.lower().replace(" ", "_")],
            metadata={
                "disease_name": disease_name_en,
                "affected_area_percent": affected_area_percent,
                "recommended_treatment": recommended_treatment,
            },
        )

    @staticmethod
    def create_spray_action(
        field_id: str,
        pesticide_type: str,
        pesticide_name_ar: str,
        pesticide_name_en: str,
        concentration: str,
        area_hectares: float,
        urgency: UrgencyLevel,
        confidence: float,
        target_pest_ar: Optional[str] = None,
        target_pest_en: Optional[str] = None,
        source_analysis_id: Optional[str] = None,
    ) -> ActionTemplate:
        """إنشاء إجراء رش مبيد"""

        action_type = {
            "fungicide": ActionType.SPRAY_FUNGICIDE,
            "insecticide": ActionType.SPRAY_INSECTICIDE,
            "herbicide": ActionType.SPRAY_HERBICIDE,
        }.get(pesticide_type, ActionType.SPRAY)

        resource_type = {
            "fungicide": ResourceType.PESTICIDE_FUNGICIDE,
            "insecticide": ResourceType.PESTICIDE_INSECTICIDE,
            "herbicide": ResourceType.PESTICIDE_HERBICIDE,
        }.get(pesticide_type, ResourceType.OTHER)

        steps = [
            ActionStep(
                step_number=1,
                title_ar="تحضير المحلول",
                title_en="Prepare solution",
                description_ar=f"اخلط {pesticide_name_ar} بتركيز {concentration} مع الماء",
                description_en=f"Mix {pesticide_name_en} at {concentration} concentration with water",
                duration_minutes=15,
                safety_notes_ar="ارتدِ ملابس واقية وقفازات ونظارات وكمامة",
                safety_notes_en="Wear protective clothing, gloves, goggles, and mask",
            ),
            ActionStep(
                step_number=2,
                title_ar="الرش",
                title_en="Spray application",
                description_ar=f"رش المحلول على مساحة {area_hectares:.2f} هكتار",
                description_en=f"Spray solution over {area_hectares:.2f} hectares",
                duration_minutes=int(area_hectares * 60),
                requires_confirmation=True,
            ),
            ActionStep(
                step_number=3,
                title_ar="التنظيف",
                title_en="Cleanup",
                description_ar="نظّف المعدات واغسل الملابس الواقية",
                description_en="Clean equipment and wash protective clothing",
                duration_minutes=20,
            ),
        ]

        resources = [
            Resource(
                resource_type=resource_type,
                name_ar=pesticide_name_ar,
                name_en=pesticide_name_en,
                quantity=area_hectares * 2,  # Approximate liters per hectare
                unit="liters",
                unit_ar="لتر",
            ),
            Resource(
                resource_type=ResourceType.EQUIPMENT_SPRAYER,
                name_ar="مرشة",
                name_en="Sprayer",
                quantity=1,
                unit="unit",
                unit_ar="وحدة",
            ),
        ]

        return ActionTemplate(
            action_type=action_type,
            title_ar=f"رش {pesticide_name_ar}"
            + (f" ضد {target_pest_ar}" if target_pest_ar else ""),
            title_en=f"Spray {pesticide_name_en}"
            + (f" against {target_pest_en}" if target_pest_en else ""),
            description_ar=f"رش {pesticide_name_ar} بتركيز {concentration} على مساحة {area_hectares:.2f} هكتار",
            description_en=f"Apply {pesticide_name_en} at {concentration} over {area_hectares:.2f} hectares",
            summary_ar=f"رش {pesticide_name_ar} - {area_hectares:.1f} هكتار",
            source_service="crop-health-ai",
            source_analysis_id=source_analysis_id,
            source_analysis_type="treatment_recommendation",
            confidence=confidence,
            urgency=urgency,
            deadline=datetime.utcnow() + timedelta(hours=urgency.max_delay_hours),
            field_id=field_id,
            steps=steps,
            resources_needed=resources,
            estimated_duration_minutes=35 + int(area_hectares * 60),
            offline_executable=True,
            fallback_instructions_ar=f"في حال عدم توفر البيانات: رش {pesticide_name_ar} بتركيز {concentration} في الصباح الباكر أو المساء، تجنب الرش في الرياح القوية",
            fallback_instructions_en=f"If data unavailable: Spray {pesticide_name_en} at {concentration} in early morning or evening, avoid spraying in strong winds",
            tags=["spray", pesticide_type, urgency.value],
        )
