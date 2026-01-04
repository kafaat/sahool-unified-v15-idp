"""
خدمة التقويم الزراعي - SAHOOL Crop Calendar Service
=====================================================
نظام شامل لإدارة التقويمات الزراعية للمحاصيل اليمنية

Comprehensive crop calendar management system for Yemen crops
Supports 18+ crops with regional adaptations
"""

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass

# Try to import from models, but make it optional for standalone usage
try:
    from ..models.irrigation import CropType, GrowthStage
except (ImportError, ValueError):
    # Fallback definitions for standalone usage
    from enum import Enum

    class CropType(str, Enum):
        """Crop types - fallback definition"""

        WHEAT = "wheat"
        SORGHUM = "sorghum"
        TOMATO = "tomato"
        COFFEE = "coffee"
        QAT = "qat"
        DATES = "dates"
        MANGO = "mango"
        BANANA = "banana"
        GRAPES = "grapes"
        POTATO = "potato"
        ONION = "onion"
        CUCUMBER = "cucumber"
        EGGPLANT = "eggplant"
        PEPPER = "pepper"
        BEANS = "beans"
        CHICKPEAS = "chickpeas"
        LENTILS = "lentils"

    class GrowthStage(str, Enum):
        """Growth stages - fallback definition"""

        INITIAL = "initial"
        DEVELOPMENT = "development"
        MID_SEASON = "mid_season"
        LATE_SEASON = "late_season"


# ============== التعدادات الإضافية - Additional Enumerations ==============


class DetailedGrowthStage(str, Enum):
    """
    مراحل النمو التفصيلية
    Detailed growth stages (6-stage model)
    """

    GERMINATION = "germination"  # إنبات
    VEGETATIVE = "vegetative"  # نمو خضري
    FLOWERING = "flowering"  # إزهار
    FRUITING = "fruiting"  # إثمار
    MATURITY = "maturity"  # نضج
    HARVEST = "harvest"  # حصاد


class YemenRegion(str, Enum):
    """
    مناطق اليمن الزراعية
    Yemen agricultural regions
    """

    TIHAMA = "tihama"  # تهامة - الساحل
    HIGHLANDS = "highlands"  # المرتفعات الجبلية
    HADHRAMAUT = "hadhramaut"  # حضرموت - الشرق


class Season(str, Enum):
    """
    الفصول
    Seasons
    """

    SPRING = "spring"  # ربيع
    SUMMER = "summer"  # صيف
    AUTUMN = "autumn"  # خريف
    WINTER = "winter"  # شتاء


# ============== نماذج البيانات - Data Models ==============


@dataclass
class CropCalendar:
    """
    تقويم محصول
    Crop calendar information
    """

    crop_type: str
    name_en: str
    name_ar: str
    crop_category: str
    planting_windows: Dict[str, Any]
    growth_stages: Dict[str, Any]
    total_cycle_days: Optional[int]
    is_perennial: bool = False
    harvest_season: Optional[Dict[str, Any]] = None
    productive_years: Optional[int] = None


@dataclass
class GrowthStageInfo:
    """
    معلومات مرحلة النمو
    Growth stage information
    """

    stage_name: str
    name_ar: str
    duration_days: int
    order: int
    water_requirement: str
    critical_tasks: List[str]
    start_day: int
    end_day: int


@dataclass
class PlantingWindow:
    """
    نافذة الزراعة
    Planting window information
    """

    region: str
    start_month: int
    end_month: int
    window_type: str  # main, secondary, best
    description: str


@dataclass
class Task:
    """
    مهمة زراعية
    Agricultural task
    """

    task_id: str
    field_id: str
    crop_type: str
    task_type: str  # irrigation, fertilization, pest_monitoring, etc.
    task_name_en: str
    task_name_ar: str
    scheduled_date: date
    growth_stage: str
    priority: int  # 1=critical, 2=high, 3=medium, 4=low
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None


# ============== فئة خدمة التقويم الزراعي - Crop Calendar Service Class ==============


class CropCalendarService:
    """
    خدمة التقويم الزراعي
    Crop Calendar Service

    الميزات الرئيسية:
    - تقويمات زراعية لـ 18 محصول يمني
    - 6 مراحل نمو تفصيلية
    - تعديلات إقليمية (تهامة، المرتفعات، حضرموت)
    - جدولة تلقائية للمهام (ري، تسميد، مراقبة آفات)
    - اقتراحات نوافذ الزراعة المثلى

    Main features:
    - Crop calendars for 18 Yemen crops
    - 6 detailed growth stages
    - Regional adjustments (Tihama, Highlands, Hadhramaut)
    - Automatic task scheduling (irrigation, fertilization, pest monitoring)
    - Optimal planting window suggestions
    """

    def __init__(self):
        """تهيئة الخدمة - Initialize service"""
        self._load_calendar_data()

    def _load_calendar_data(self):
        """
        تحميل بيانات التقويم من ملف JSON
        Load calendar data from JSON file
        """
        data_path = Path(__file__).parent.parent / "data" / "crop_calendars.json"

        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.crops_data = data.get("crops", {})
        self.regions_data = data.get("regions", {})
        self.task_schedules = data.get("task_schedules", {})

    # ============== 1. الحصول على التقويم - Get Calendar ==============

    def get_calendar(
        self, crop_type: str, region: Optional[str] = None
    ) -> CropCalendar:
        """
        الحصول على تقويم المحصول
        Get crop calendar with regional adjustments

        Args:
            crop_type: نوع المحصول - Crop type (e.g., "sorghum", "wheat")
            region: المنطقة - Region (optional: "tihama", "highlands", "hadhramaut")

        Returns:
            CropCalendar: تقويم المحصول - Crop calendar object

        Example:
            >>> service = CropCalendarService()
            >>> calendar = service.get_calendar("sorghum", "tihama")
            >>> print(calendar.name_ar)  # "ذرة رفيعة"
        """
        # تحويل من CropType enum إذا لزم الأمر
        # Convert from CropType enum if needed
        if isinstance(crop_type, CropType):
            crop_type = crop_type.value

        crop_data = self.crops_data.get(crop_type)
        if not crop_data:
            raise ValueError(f"Crop type '{crop_type}' not found in calendar data")

        # تصفية نوافذ الزراعة حسب المنطقة
        # Filter planting windows by region
        planting_windows = crop_data.get("planting_windows", {})
        if region:
            planting_windows = {region: planting_windows.get(region, {})}

        # تصفية مواسم الحصاد حسب المنطقة
        # Filter harvest seasons by region
        harvest_season = crop_data.get("harvest_season", {})
        if region and harvest_season:
            harvest_season = {region: harvest_season.get(region, {})}

        return CropCalendar(
            crop_type=crop_type,
            name_en=crop_data.get("name_en", ""),
            name_ar=crop_data.get("name_ar", ""),
            crop_category=crop_data.get("type", ""),
            planting_windows=planting_windows,
            growth_stages=crop_data.get("growth_stages", {}),
            total_cycle_days=crop_data.get("total_cycle_days"),
            is_perennial=crop_data.get("perennial", False),
            harvest_season=harvest_season,
            productive_years=crop_data.get("productive_years"),
        )

    # ============== 2. الحصول على المرحلة الحالية - Get Current Stage ==============

    def get_current_stage(
        self, crop_type: str, planting_date: date
    ) -> Tuple[str, GrowthStageInfo]:
        """
        الحصول على مرحلة النمو الحالية
        Get current growth stage based on planting date

        Args:
            crop_type: نوع المحصول - Crop type
            planting_date: تاريخ الزراعة - Planting date

        Returns:
            Tuple[str, GrowthStageInfo]: (اسم المرحلة، معلومات المرحلة)
                                         (stage name, stage info)

        Example:
            >>> service = CropCalendarService()
            >>> stage_name, stage_info = service.get_current_stage("wheat", date(2025, 10, 15))
            >>> print(stage_name)  # "vegetative"
            >>> print(stage_info.name_ar)  # "نمو خضري"
        """
        if isinstance(crop_type, CropType):
            crop_type = crop_type.value

        crop_data = self.crops_data.get(crop_type)
        if not crop_data:
            raise ValueError(f"Crop type '{crop_type}' not found")

        # حساب عدد الأيام منذ الزراعة
        # Calculate days since planting
        today = date.today()
        days_since_planting = (today - planting_date).days

        if days_since_planting < 0:
            raise ValueError("Planting date cannot be in the future")

        # تحليل مراحل النمو
        # Parse growth stages
        growth_stages = crop_data.get("growth_stages", {})
        stages_list = self._parse_growth_stages(growth_stages)

        # إيجاد المرحلة الحالية
        # Find current stage
        current_stage = None
        current_stage_info = None

        for stage_name, stage_info in stages_list:
            if stage_info.start_day <= days_since_planting <= stage_info.end_day:
                current_stage = stage_name
                current_stage_info = stage_info
                break

        # إذا تجاوز المحصول جميع المراحل
        # If crop has passed all stages
        if current_stage is None:
            # إرجاع آخر مرحلة (الحصاد عادة)
            # Return last stage (usually harvest)
            stage_name, stage_info = stages_list[-1]
            return stage_name, stage_info

        return current_stage, current_stage_info

    def _parse_growth_stages(
        self, growth_stages: Dict[str, Any]
    ) -> List[Tuple[str, GrowthStageInfo]]:
        """
        تحليل مراحل النمو وحساب أيام البداية والنهاية
        Parse growth stages and calculate start/end days
        """
        stages_list = []
        cumulative_days = 0

        # ترتيب المراحل حسب الترتيب
        # Sort stages by order
        sorted_stages = sorted(
            growth_stages.items(), key=lambda x: x[1].get("order", 0)
        )

        for stage_name, stage_data in sorted_stages:
            duration = stage_data.get("duration_days", 0)

            stage_info = GrowthStageInfo(
                stage_name=stage_name,
                name_ar=stage_data.get("name_ar", ""),
                duration_days=duration,
                order=stage_data.get("order", 0),
                water_requirement=stage_data.get("water_requirement", "moderate"),
                critical_tasks=stage_data.get("critical_tasks", []),
                start_day=cumulative_days,
                end_day=cumulative_days + duration - 1,
            )

            stages_list.append((stage_name, stage_info))
            cumulative_days += duration

        return stages_list

    # ============== 3. الحصول على المهام القادمة - Get Upcoming Tasks ==============

    def get_upcoming_tasks(
        self,
        field_id: str,
        crop_type: str,
        planting_date: date,
        region: str = "highlands",
        days: int = 14,
    ) -> List[Task]:
        """
        الحصول على المهام القادمة للحقل
        Get upcoming tasks for a field

        Args:
            field_id: معرّف الحقل - Field ID
            crop_type: نوع المحصول - Crop type
            planting_date: تاريخ الزراعة - Planting date
            region: المنطقة - Region
            days: عدد الأيام القادمة - Number of days ahead (default: 14)

        Returns:
            List[Task]: قائمة المهام - List of upcoming tasks

        Example:
            >>> service = CropCalendarService()
            >>> tasks = service.get_upcoming_tasks(
            ...     field_id="field_001",
            ...     crop_type="tomato",
            ...     planting_date=date(2025, 9, 1),
            ...     days=14
            ... )
            >>> for task in tasks:
            ...     print(f"{task.task_name_ar}: {task.scheduled_date}")
        """
        if isinstance(crop_type, CropType):
            crop_type = crop_type.value

        tasks = []
        today = date.today()
        end_date = today + timedelta(days=days)

        # الحصول على المرحلة الحالية
        # Get current stage
        current_stage_name, current_stage_info = self.get_current_stage(
            crop_type, planting_date
        )

        # 1. مهام الري - Irrigation tasks
        irrigation_tasks = self._generate_irrigation_tasks(
            field_id=field_id,
            crop_type=crop_type,
            planting_date=planting_date,
            current_stage=current_stage_name,
            today=today,
            end_date=end_date,
        )
        tasks.extend(irrigation_tasks)

        # 2. مهام التسميد - Fertilization tasks
        fertilization_tasks = self._generate_fertilization_tasks(
            field_id=field_id,
            crop_type=crop_type,
            planting_date=planting_date,
            current_stage=current_stage_name,
            today=today,
            end_date=end_date,
        )
        tasks.extend(fertilization_tasks)

        # 3. مهام مراقبة الآفات - Pest monitoring tasks
        pest_tasks = self._generate_pest_monitoring_tasks(
            field_id=field_id,
            crop_type=crop_type,
            planting_date=planting_date,
            region=region,
            today=today,
            end_date=end_date,
        )
        tasks.extend(pest_tasks)

        # 4. المهام الحرجة من مرحلة النمو - Critical tasks from growth stage
        critical_tasks = self._generate_critical_tasks(
            field_id=field_id,
            crop_type=crop_type,
            current_stage_info=current_stage_info,
            today=today,
        )
        tasks.extend(critical_tasks)

        # ترتيب المهام حسب التاريخ والأولوية
        # Sort tasks by date and priority
        tasks.sort(key=lambda t: (t.scheduled_date, t.priority))

        return tasks

    # ============== 4. اقتراح نافذة الزراعة - Suggest Planting Window ==============

    def suggest_planting_window(
        self, crop_type: str, region: str, reference_date: Optional[date] = None
    ) -> List[PlantingWindow]:
        """
        اقتراح أفضل نوافذ الزراعة
        Suggest optimal planting windows

        Args:
            crop_type: نوع المحصول - Crop type
            region: المنطقة - Region
            reference_date: تاريخ مرجعي - Reference date (default: today)

        Returns:
            List[PlantingWindow]: نوافذ الزراعة الموصى بها - Recommended planting windows

        Example:
            >>> service = CropCalendarService()
            >>> windows = service.suggest_planting_window("sorghum", "tihama")
            >>> for window in windows:
            ...     print(f"{window.description}: شهر {window.start_month}-{window.end_month}")
        """
        if isinstance(crop_type, CropType):
            crop_type = crop_type.value

        if reference_date is None:
            reference_date = date.today()

        crop_data = self.crops_data.get(crop_type)
        if not crop_data:
            raise ValueError(f"Crop type '{crop_type}' not found")

        planting_windows_data = crop_data.get("planting_windows", {})
        region_windows = planting_windows_data.get(region, {})

        if not region_windows:
            raise ValueError(
                f"No planting windows found for crop '{crop_type}' in region '{region}'"
            )

        windows = []

        for window_type, window_data in region_windows.items():
            window = PlantingWindow(
                region=region,
                start_month=window_data.get("start_month"),
                end_month=window_data.get("end_month"),
                window_type=window_type,
                description=window_data.get("description", ""),
            )
            windows.append(window)

        # ترتيب: الأفضل أولاً، ثم الرئيسي، ثم الثانوي
        # Sort: best first, then main, then secondary
        priority_order = {"best": 0, "main": 1, "secondary": 2}
        windows.sort(key=lambda w: priority_order.get(w.window_type, 3))

        return windows

    # ============== جدولة المهام - Task Scheduling ==============

    def irrigation_schedule(
        self, growth_stage: str, region: str = "highlands"
    ) -> Dict[str, Any]:
        """
        جدول الري حسب مرحلة النمو
        Irrigation schedule by growth stage

        Args:
            growth_stage: مرحلة النمو - Growth stage
            region: المنطقة - Region for adjustments

        Returns:
            Dict: معلومات جدول الري - Irrigation schedule information

        Example:
            >>> service = CropCalendarService()
            >>> schedule = service.irrigation_schedule("flowering")
            >>> print(schedule["frequency_days"])  # 2
        """
        irrigation_data = self.task_schedules.get("irrigation", {}).get(
            growth_stage, {}
        )

        if not irrigation_data:
            # قيم افتراضية
            # Default values
            irrigation_data = {
                "frequency_days": 4,
                "description_ar": "ري منتظم",
                "description_en": "Regular irrigation",
            }

        # تعديلات إقليمية - Regional adjustments
        frequency = irrigation_data.get("frequency_days", 4)

        if region == "tihama":
            # تهامة: حار ورطب، يحتاج ري أكثر تواتراً
            # Tihama: hot and humid, needs more frequent irrigation
            frequency = max(1, frequency - 1)
        elif region == "hadhramaut":
            # حضرموت: صحراوي، يحتاج ري أكثر تواتراً
            # Hadhramaut: desert, needs more frequent irrigation
            frequency = max(1, frequency - 1)

        return {
            "frequency_days": frequency,
            "description_ar": irrigation_data.get("description_ar", ""),
            "description_en": irrigation_data.get("description_en", ""),
            "region_adjusted": region,
        }

    def fertilizer_schedule(
        self, crop_type: str, growth_stage: str
    ) -> List[Dict[str, Any]]:
        """
        جدول التسميد حسب المحصول ومرحلة النمو
        Fertilizer schedule by crop and growth stage

        Args:
            crop_type: نوع المحصول - Crop type
            growth_stage: مرحلة النمو - Growth stage

        Returns:
            List[Dict]: جداول التسميد - Fertilization schedules

        Example:
            >>> service = CropCalendarService()
            >>> schedule = service.fertilizer_schedule("tomato", "vegetative")
            >>> for fert in schedule:
            ...     print(f"{fert['type']}: {fert['amount_kg_ha']} kg/ha")
        """
        if isinstance(crop_type, CropType):
            crop_type = crop_type.value

        fertilization_data = self.task_schedules.get("fertilization", {})
        crop_schedule = fertilization_data.get(crop_type, [])

        # تصفية حسب مرحلة النمو
        # Filter by growth stage
        stage_fertilizers = [
            fert for fert in crop_schedule if fert.get("stage") == growth_stage
        ]

        return stage_fertilizers

    def pest_monitoring_schedule(
        self, crop_type: str, season: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        جدول مراقبة الآفات حسب المحصول والموسم
        Pest monitoring schedule by crop and season

        Args:
            crop_type: نوع المحصول - Crop type
            season: الموسم - Season (optional, auto-detected if None)

        Returns:
            Dict: معلومات مراقبة الآفات - Pest monitoring information

        Example:
            >>> service = CropCalendarService()
            >>> schedule = service.pest_monitoring_schedule("tomato", "summer")
            >>> print(schedule["frequency_days"])  # 5
            >>> print(schedule["common_pests_ar"])  # ['العنكبوت الأحمر', ...]
        """
        if season is None:
            season = self._get_current_season()

        pest_data = self.task_schedules.get("pest_monitoring", {}).get(season, {})

        if not pest_data:
            # قيم افتراضية
            # Default values
            pest_data = {
                "frequency_days": 7,
                "common_pests_ar": ["آفات عامة"],
                "common_pests_en": ["general_pests"],
            }

        return pest_data

    # ============== دوال مساعدة خاصة - Private Helper Functions ==============

    def _generate_irrigation_tasks(
        self,
        field_id: str,
        crop_type: str,
        planting_date: date,
        current_stage: str,
        today: date,
        end_date: date,
    ) -> List[Task]:
        """إنشاء مهام الري - Generate irrigation tasks"""
        tasks = []

        irrigation_schedule = self.irrigation_schedule(current_stage)
        frequency = irrigation_schedule.get("frequency_days", 4)

        # حساب تواريخ الري القادمة
        # Calculate upcoming irrigation dates
        current_date = today
        task_counter = 1

        while current_date <= end_date:
            task = Task(
                task_id=f"{field_id}_irrigation_{task_counter}",
                field_id=field_id,
                crop_type=crop_type,
                task_type="irrigation",
                task_name_en=f"Irrigation - {current_stage}",
                task_name_ar=f"ري - {irrigation_schedule.get('description_ar', '')}",
                scheduled_date=current_date,
                growth_stage=current_stage,
                priority=2 if current_stage in ["flowering", "fruiting"] else 3,
                description=irrigation_schedule.get("description_en", ""),
            )
            tasks.append(task)

            current_date += timedelta(days=frequency)
            task_counter += 1

        return tasks

    def _generate_fertilization_tasks(
        self,
        field_id: str,
        crop_type: str,
        planting_date: date,
        current_stage: str,
        today: date,
        end_date: date,
    ) -> List[Task]:
        """إنشاء مهام التسميد - Generate fertilization tasks"""
        tasks = []

        fertilizer_schedule = self.fertilizer_schedule(crop_type, current_stage)

        for fert in fertilizer_schedule:
            # حساب تاريخ التسميد
            # Calculate fertilization date
            stage_day = fert.get("day", 1)

            # الحصول على تاريخ بداية المرحلة
            # Get stage start date
            crop_data = self.crops_data.get(crop_type, {})
            growth_stages = crop_data.get("growth_stages", {})
            stages_list = self._parse_growth_stages(growth_stages)

            for stage_name, stage_info in stages_list:
                if stage_name == current_stage:
                    task_date = planting_date + timedelta(
                        days=stage_info.start_day + stage_day
                    )

                    if today <= task_date <= end_date:
                        task = Task(
                            task_id=f"{field_id}_fertilizer_{fert.get('type')}_{stage_day}",
                            field_id=field_id,
                            crop_type=crop_type,
                            task_type="fertilization",
                            task_name_en=f"Apply {fert.get('type')} fertilizer",
                            task_name_ar=fert.get("description_ar", "تسميد"),
                            scheduled_date=task_date,
                            growth_stage=current_stage,
                            priority=2,
                            description=f"Apply {fert.get('amount_kg_ha')} kg/ha",
                            quantity=fert.get("amount_kg_ha"),
                            unit="kg/ha",
                        )
                        tasks.append(task)
                    break

        return tasks

    def _generate_pest_monitoring_tasks(
        self,
        field_id: str,
        crop_type: str,
        planting_date: date,
        region: str,
        today: date,
        end_date: date,
    ) -> List[Task]:
        """إنشاء مهام مراقبة الآفات - Generate pest monitoring tasks"""
        tasks = []

        season = self._get_current_season()
        pest_schedule = self.pest_monitoring_schedule(crop_type, season)
        frequency = pest_schedule.get("frequency_days", 7)

        current_date = today
        task_counter = 1

        while current_date <= end_date:
            pests_ar = ", ".join(pest_schedule.get("common_pests_ar", []))
            pests_en = ", ".join(pest_schedule.get("common_pests_en", []))

            task = Task(
                task_id=f"{field_id}_pest_monitor_{task_counter}",
                field_id=field_id,
                crop_type=crop_type,
                task_type="pest_monitoring",
                task_name_en=f"Monitor for {pests_en}",
                task_name_ar=f"مراقبة: {pests_ar}",
                scheduled_date=current_date,
                growth_stage="",
                priority=3,
                description=f"Check for common {season} pests",
            )
            tasks.append(task)

            current_date += timedelta(days=frequency)
            task_counter += 1

        return tasks

    def _generate_critical_tasks(
        self,
        field_id: str,
        crop_type: str,
        current_stage_info: GrowthStageInfo,
        today: date,
    ) -> List[Task]:
        """إنشاء المهام الحرجة - Generate critical tasks from growth stage"""
        tasks = []

        for idx, task_name in enumerate(current_stage_info.critical_tasks):
            # ترجمة أسماء المهام
            # Translate task names
            task_translations = {
                "ensure_soil_moisture": ("ضمان رطوبة التربة", "Ensure soil moisture"),
                "weed_control": ("مكافحة الأعشاب", "Weed control"),
                "fertilization": ("تسميد", "Fertilization"),
                "irrigation": ("ري", "Irrigation"),
                "pest_monitoring": ("مراقبة الآفات", "Pest monitoring"),
                "pollination_support": ("دعم التلقيح", "Pollination support"),
                "pest_control": ("مكافحة الآفات", "Pest control"),
                "nutrient_boost": ("تعزيز المغذيات", "Nutrient boost"),
                "bird_protection": ("حماية من الطيور", "Bird protection"),
                "reduce_irrigation": ("تقليل الري", "Reduce irrigation"),
                "harvest_preparation": ("التحضير للحصاد", "Harvest preparation"),
                "timely_harvest": ("حصاد في الوقت المناسب", "Timely harvest"),
                "drying": ("تجفيف", "Drying"),
                "storage": ("تخزين", "Storage"),
                "seed_treatment": ("معالجة البذور", "Seed treatment"),
                "soil_preparation": ("تحضير التربة", "Soil preparation"),
                "transplanting": ("شتل", "Transplanting"),
                "staking": ("دعم بالأوتاد", "Staking"),
                "pruning": ("تقليم", "Pruning"),
                "thinning": ("خف", "Thinning"),
                "quality_check": ("فحص الجودة", "Quality check"),
                "packaging": ("تعبئة", "Packaging"),
            }

            name_ar, name_en = task_translations.get(task_name, (task_name, task_name))

            # جدولة المهمة في منتصف المرحلة تقريباً
            # Schedule task approximately mid-stage
            days_offset = idx * 3  # توزيع المهام

            task = Task(
                task_id=f"{field_id}_critical_{task_name}",
                field_id=field_id,
                crop_type=crop_type,
                task_type="critical",
                task_name_en=name_en,
                task_name_ar=name_ar,
                scheduled_date=today + timedelta(days=days_offset),
                growth_stage=current_stage_info.stage_name,
                priority=1,
                description=f"Critical task for {current_stage_info.name_ar} stage",
            )
            tasks.append(task)

        return tasks

    def _get_current_season(self) -> str:
        """
        الحصول على الموسم الحالي
        Get current season
        """
        month = date.today().month

        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "autumn"
        else:
            return "winter"

    # ============== معلومات إضافية - Additional Information ==============

    def get_regional_climate_info(self, region: str) -> Dict[str, Any]:
        """
        الحصول على معلومات المناخ الإقليمي
        Get regional climate information

        Args:
            region: المنطقة - Region

        Returns:
            Dict: معلومات المناخ - Climate information
        """
        return self.regions_data.get(region, {})

    def list_available_crops(self) -> List[Dict[str, str]]:
        """
        قائمة بجميع المحاصيل المتاحة
        List all available crops

        Returns:
            List[Dict]: قائمة المحاصيل - List of crops with names
        """
        crops = []
        for crop_key, crop_data in self.crops_data.items():
            crops.append(
                {
                    "crop_type": crop_key,
                    "name_en": crop_data.get("name_en", ""),
                    "name_ar": crop_data.get("name_ar", ""),
                    "category": crop_data.get("type", ""),
                    "is_perennial": crop_data.get("perennial", False),
                }
            )

        return crops

    def map_fao_stage_to_detailed(self, fao_stage: GrowthStage) -> str:
        """
        تحويل مرحلة FAO (4 مراحل) إلى مراحل تفصيلية (6 مراحل)
        Map FAO growth stage (4 stages) to detailed stages (6 stages)

        Args:
            fao_stage: مرحلة FAO - FAO growth stage

        Returns:
            str: المرحلة التفصيلية - Detailed stage name
        """
        mapping = {
            GrowthStage.INITIAL: DetailedGrowthStage.GERMINATION,
            GrowthStage.DEVELOPMENT: DetailedGrowthStage.VEGETATIVE,
            GrowthStage.MID_SEASON: DetailedGrowthStage.FLOWERING,
            GrowthStage.LATE_SEASON: DetailedGrowthStage.MATURITY,
        }

        return mapping.get(fao_stage, DetailedGrowthStage.VEGETATIVE).value


# ============== مصدّر الوحدة - Module Exports ==============

__all__ = [
    "CropCalendarService",
    "CropCalendar",
    "GrowthStageInfo",
    "PlantingWindow",
    "Task",
    "DetailedGrowthStage",
    "YemenRegion",
    "Season",
]
