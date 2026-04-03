# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
AgML Integration for Agricultural Machine Learning
تكامل AgML للتعلم الآلي الزراعي

Uses AgML (https://github.com/Project-AgML/AgML) for:
- Agricultural benchmark datasets
- Crop disease detection models
- Yield prediction
- Plant phenotyping

AgML provides standardized access to 30+ agricultural ML datasets.
"""

# ⚠️ INTEGRATION STATUS: STATIC CATALOG ONLY
# The `agml` package is not installed in any active service's requirements.txt.
# All functions return hardcoded dataset metadata and disease class dictionaries.
# No actual ML dataset loading or model inference occurs.
# To enable real AgML integration, add `agml>=0.4.0` to requirements.

import os
import tempfile
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()


class DatasetType(StrEnum):
    """Types of agricultural datasets."""

    CROP_DISEASE = "crop_disease"  # أمراض المحاصيل
    PLANT_PHENOTYPING = "plant_phenotyping"  # نمط النبات
    YIELD_PREDICTION = "yield_prediction"  # تنبؤ الإنتاجية
    WEED_DETECTION = "weed_detection"  # كشف الأعشاب
    FRUIT_DETECTION = "fruit_detection"  # كشف الفاكهة
    SEMANTIC_SEGMENTATION = "semantic_segmentation"  # التجزئة الدلالية


class CropType(StrEnum):
    """Supported crop types."""

    WHEAT = "wheat"  # قمح
    BARLEY = "barley"  # شعير
    CORN = "corn"  # ذرة
    RICE = "rice"  # أرز
    TOMATO = "tomato"  # طماطم
    POTATO = "potato"  # بطاطس
    DATE_PALM = "date_palm"  # نخيل
    APPLE = "apple"  # تفاح
    GRAPE = "grape"  # عنب
    CITRUS = "citrus"  # حمضيات
    GENERAL = "general"  # عام


@dataclass
class CropDataset:
    """Crop-specific dataset information."""

    name: str
    name_ar: str
    dataset_type: DatasetType
    crop_type: CropType
    num_classes: int
    num_images: int
    source: str
    license: str
    description: str
    description_ar: str
    download_url: str | None = None


@dataclass
class DiseaseDataset:
    """Disease detection dataset."""

    name: str
    crop: CropType
    diseases: list[str]
    diseases_ar: list[str]
    num_images: int
    accuracy_benchmark: float


@dataclass
class YieldDataset:
    """Yield prediction dataset."""

    name: str
    crop: CropType
    features: list[str]
    target: str
    num_samples: int
    rmse_benchmark: float


@dataclass
class ModelInfo:
    """Pre-trained model information."""

    name: str
    task: DatasetType
    architecture: str
    accuracy: float
    input_size: tuple[int, int]
    download_url: str


class AgMLDatasetManager:
    """
    AgML Dataset Manager for SAHOOL.
    مدير مجموعات بيانات AgML لسهول

    Provides access to agricultural ML datasets and pre-trained models.
    """

    # SECURITY: Allowed base directories for cache_dir to prevent path traversal
    _ALLOWED_CACHE_PREFIXES = (tempfile.gettempdir(), "/var/cache/")

    def __init__(self, cache_dir: str | None = None):
        raw_path = cache_dir or os.getenv("AGML_CACHE_DIR", os.path.join(tempfile.gettempdir(), "agml"))
        resolved = str(Path(raw_path).resolve())

        # SECURITY: Validate cache_dir is under an allowed prefix
        if not any(resolved.startswith(prefix) for prefix in self._ALLOWED_CACHE_PREFIXES):
            raise ValueError(
                f"cache_dir must be under {self._ALLOWED_CACHE_PREFIXES}, "
                f"got '{resolved}'. Path traversal is not allowed."
            )

        self.cache_dir = Path(resolved)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._agml = None
        self._initialized = False

        # Available datasets catalog
        self._datasets_catalog = self._build_catalog()

    def _build_catalog(self) -> dict[str, CropDataset]:
        """Build the datasets catalog."""
        return {
            # Plant Village - Most comprehensive disease dataset
            "plant_village": CropDataset(
                name="PlantVillage",
                name_ar="قرية النبات",
                dataset_type=DatasetType.CROP_DISEASE,
                crop_type=CropType.GENERAL,
                num_classes=38,
                num_images=54306,
                source="PlantVillage",
                license="CC0",
                description="38 classes of healthy and diseased crop leaves",
                description_ar="38 فئة من أوراق المحاصيل الصحية والمريضة",
                download_url="https://github.com/spMohanty/PlantVillage-Dataset",
            ),
            # Wheat disease datasets
            "wheat_rust": CropDataset(
                name="Wheat Rust Detection",
                name_ar="كشف صدأ القمح",
                dataset_type=DatasetType.CROP_DISEASE,
                crop_type=CropType.WHEAT,
                num_classes=4,
                num_images=1400,
                source="CGIAR",
                license="CC-BY-4.0",
                description="Wheat leaf rust, stem rust, yellow rust detection",
                description_ar="كشف صدأ الأوراق والساق والصدأ الأصفر في القمح",
            ),
            # Rice disease
            "rice_disease": CropDataset(
                name="Rice Disease Detection",
                name_ar="كشف أمراض الأرز",
                dataset_type=DatasetType.CROP_DISEASE,
                crop_type=CropType.RICE,
                num_classes=5,
                num_images=3355,
                source="Mendeley",
                license="CC-BY-4.0",
                description="Rice blast, brown spot, tungro detection",
                description_ar="كشف لفحة الأرز، البقع البنية، التنغرو",
            ),
            # Tomato disease
            "tomato_disease": CropDataset(
                name="Tomato Disease Detection",
                name_ar="كشف أمراض الطماطم",
                dataset_type=DatasetType.CROP_DISEASE,
                crop_type=CropType.TOMATO,
                num_classes=10,
                num_images=18160,
                source="PlantVillage",
                license="CC0",
                description="10 tomato diseases including blight, mosaic, leaf mold",
                description_ar="10 أمراض طماطم تشمل اللفحة، الفسيفساء، عفن الأوراق",
            ),
            # Corn/Maize
            "corn_disease": CropDataset(
                name="Corn Disease Detection",
                name_ar="كشف أمراض الذرة",
                dataset_type=DatasetType.CROP_DISEASE,
                crop_type=CropType.CORN,
                num_classes=4,
                num_images=4188,
                source="PlantVillage",
                license="CC0",
                description="Gray leaf spot, common rust, northern leaf blight",
                description_ar="بقعة الورقة الرمادية، الصدأ الشائع، لفحة الأوراق الشمالية",
            ),
            # Grape disease
            "grape_disease": CropDataset(
                name="Grape Disease Detection",
                name_ar="كشف أمراض العنب",
                dataset_type=DatasetType.CROP_DISEASE,
                crop_type=CropType.GRAPE,
                num_classes=4,
                num_images=4062,
                source="PlantVillage",
                license="CC0",
                description="Black rot, esca, leaf blight detection",
                description_ar="كشف العفن الأسود، إسكا، لفحة الأوراق",
            ),
            # Potato disease
            "potato_disease": CropDataset(
                name="Potato Disease Detection",
                name_ar="كشف أمراض البطاطس",
                dataset_type=DatasetType.CROP_DISEASE,
                crop_type=CropType.POTATO,
                num_classes=3,
                num_images=2152,
                source="PlantVillage",
                license="CC0",
                description="Early blight, late blight detection",
                description_ar="كشف اللفحة المبكرة واللفحة المتأخرة",
            ),
            # Apple disease
            "apple_disease": CropDataset(
                name="Apple Disease Detection",
                name_ar="كشف أمراض التفاح",
                dataset_type=DatasetType.CROP_DISEASE,
                crop_type=CropType.APPLE,
                num_classes=4,
                num_images=3171,
                source="PlantVillage",
                license="CC0",
                description="Apple scab, black rot, cedar apple rust",
                description_ar="جرب التفاح، العفن الأسود، صدأ تفاح الأرز",
            ),
            # Weed detection
            "deepweeds": CropDataset(
                name="DeepWeeds",
                name_ar="الأعشاب العميقة",
                dataset_type=DatasetType.WEED_DETECTION,
                crop_type=CropType.GENERAL,
                num_classes=9,
                num_images=17509,
                source="Queensland University",
                license="CC-BY-4.0",
                description="8 weed species + negative class",
                description_ar="8 أنواع من الأعشاب + فئة سلبية",
            ),
            # Yield prediction
            "crop_yield_prediction": CropDataset(
                name="Crop Yield Prediction",
                name_ar="تنبؤ إنتاجية المحاصيل",
                dataset_type=DatasetType.YIELD_PREDICTION,
                crop_type=CropType.GENERAL,
                num_classes=0,
                num_images=0,  # Tabular data
                source="USDA/FAO",
                license="Public Domain",
                description="Historical yield data with weather and soil features",
                description_ar="بيانات الإنتاجية التاريخية مع ميزات الطقس والتربة",
            ),
        }

    async def initialize(self) -> bool:
        """Initialize AgML library."""
        if self._initialized:
            return True

        try:
            import agml

            self._agml = agml
            self._initialized = True
            logger.info("AgML initialized successfully")
            return True

        except ImportError:
            logger.warning(
                "AgML not installed. Install with: pip install agml",
                fallback="Using built-in dataset catalog",
            )
            return False

    def list_datasets(
        self,
        dataset_type: DatasetType | None = None,
        crop_type: CropType | None = None,
    ) -> list[CropDataset]:
        """
        List available datasets.
        عرض مجموعات البيانات المتاحة
        """
        datasets = list(self._datasets_catalog.values())

        if dataset_type:
            datasets = [d for d in datasets if d.dataset_type == dataset_type]

        if crop_type:
            datasets = [d for d in datasets if d.crop_type == crop_type or d.crop_type == CropType.GENERAL]

        return datasets

    def get_dataset_info(self, name: str) -> CropDataset | None:
        """Get information about a specific dataset."""
        return self._datasets_catalog.get(name)

    async def load_dataset(
        self,
        name: str,
        split: str = "train",
        download: bool = True,
    ) -> Any:
        """
        Load a dataset for training.
        تحميل مجموعة بيانات للتدريب
        """
        if not self._initialized:
            if not await self.initialize():
                logger.warning("AgML not available, returning dataset info only")
                return self._datasets_catalog.get(name)

        try:
            loader = self._agml.data.AgMLDataLoader(name)
            if download:
                loader.download()
            return loader.load_split(split)

        except Exception as e:
            logger.error("Failed to load dataset", name=name, error=str(e))
            return None

    def get_disease_classes(self, crop: CropType) -> list[dict[str, str]]:
        """
        Get disease classes for a crop type.
        الحصول على فئات الأمراض لنوع محصول
        """
        disease_classes = {
            CropType.WHEAT: [
                {"en": "Healthy", "ar": "صحي"},
                {"en": "Leaf Rust", "ar": "صدأ الأوراق"},
                {"en": "Stem Rust", "ar": "صدأ الساق"},
                {"en": "Yellow Rust", "ar": "الصدأ الأصفر"},
                {"en": "Septoria", "ar": "سبتوريا"},
            ],
            CropType.TOMATO: [
                {"en": "Healthy", "ar": "صحي"},
                {"en": "Early Blight", "ar": "اللفحة المبكرة"},
                {"en": "Late Blight", "ar": "اللفحة المتأخرة"},
                {"en": "Leaf Mold", "ar": "عفن الأوراق"},
                {"en": "Septoria Leaf Spot", "ar": "بقعة أوراق السبتوريا"},
                {"en": "Spider Mites", "ar": "العنكبوت الأحمر"},
                {"en": "Target Spot", "ar": "البقعة المستهدفة"},
                {"en": "Mosaic Virus", "ar": "فيروس الفسيفساء"},
                {"en": "Yellow Leaf Curl", "ar": "تجعد الأوراق الأصفر"},
                {"en": "Bacterial Spot", "ar": "البقعة البكتيرية"},
            ],
            CropType.POTATO: [
                {"en": "Healthy", "ar": "صحي"},
                {"en": "Early Blight", "ar": "اللفحة المبكرة"},
                {"en": "Late Blight", "ar": "اللفحة المتأخرة"},
            ],
            CropType.CORN: [
                {"en": "Healthy", "ar": "صحي"},
                {"en": "Gray Leaf Spot", "ar": "بقعة الورقة الرمادية"},
                {"en": "Common Rust", "ar": "الصدأ الشائع"},
                {"en": "Northern Leaf Blight", "ar": "لفحة الأوراق الشمالية"},
            ],
            CropType.GRAPE: [
                {"en": "Healthy", "ar": "صحي"},
                {"en": "Black Rot", "ar": "العفن الأسود"},
                {"en": "Esca (Black Measles)", "ar": "إسكا (الحصبة السوداء)"},
                {"en": "Leaf Blight", "ar": "لفحة الأوراق"},
            ],
            CropType.APPLE: [
                {"en": "Healthy", "ar": "صحي"},
                {"en": "Apple Scab", "ar": "جرب التفاح"},
                {"en": "Black Rot", "ar": "العفن الأسود"},
                {"en": "Cedar Apple Rust", "ar": "صدأ تفاح الأرز"},
            ],
            CropType.DATE_PALM: [
                {"en": "Healthy", "ar": "صحي"},
                {"en": "Red Palm Weevil", "ar": "سوسة النخيل الحمراء"},
                {"en": "Bayoud Disease", "ar": "مرض البيوض"},
                {"en": "Black Scorch", "ar": "اللفحة السوداء"},
                {"en": "Leaf Spot", "ar": "تبقع الأوراق"},
            ],
        }

        return disease_classes.get(crop, [{"en": "Unknown", "ar": "غير معروف"}])

    def get_yield_features(self) -> list[dict[str, str]]:
        """
        Get features used for yield prediction.
        الحصول على الميزات المستخدمة للتنبؤ بالإنتاجية
        """
        return [
            {"en": "Temperature (mean)", "ar": "درجة الحرارة (متوسط)", "unit": "°C"},
            {"en": "Precipitation", "ar": "الهطول", "unit": "mm"},
            {"en": "Solar Radiation", "ar": "الإشعاع الشمسي", "unit": "MJ/m²"},
            {"en": "Soil Moisture", "ar": "رطوبة التربة", "unit": "%"},
            {"en": "NDVI (vegetation index)", "ar": "مؤشر الغطاء النباتي", "unit": ""},
            {"en": "Growing Degree Days", "ar": "أيام النمو الحرارية", "unit": "GDD"},
            {"en": "Nitrogen Applied", "ar": "النيتروجين المطبق", "unit": "kg/ha"},
            {"en": "Phosphorus Applied", "ar": "الفوسفور المطبق", "unit": "kg/ha"},
            {"en": "Potassium Applied", "ar": "البوتاسيوم المطبق", "unit": "kg/ha"},
            {"en": "Planting Date", "ar": "تاريخ الزراعة", "unit": "DOY"},
            {"en": "Soil Type", "ar": "نوع التربة", "unit": "category"},
            {"en": "Irrigation Amount", "ar": "كمية الري", "unit": "mm"},
        ]

    async def get_pretrained_model(
        self,
        task: DatasetType,
        crop: CropType | None = None,
    ) -> ModelInfo | None:
        """
        Get information about pre-trained models.
        الحصول على معلومات حول النماذج المدربة مسبقاً
        """
        models = {
            DatasetType.CROP_DISEASE: ModelInfo(
                name="plant_disease_resnet50",
                task=DatasetType.CROP_DISEASE,
                architecture="ResNet50",
                accuracy=0.987,
                input_size=(224, 224),
                download_url="https://github.com/imskr/Plant_Disease_Detection",
            ),
            DatasetType.WEED_DETECTION: ModelInfo(
                name="deepweeds_resnet50",
                task=DatasetType.WEED_DETECTION,
                architecture="ResNet50",
                accuracy=0.956,
                input_size=(224, 224),
                download_url="https://github.com/AlexOlsen/DeepWeeds",
            ),
            DatasetType.FRUIT_DETECTION: ModelInfo(
                name="fruit_detector_yolov5",
                task=DatasetType.FRUIT_DETECTION,
                architecture="YOLOv5",
                accuracy=0.92,
                input_size=(640, 640),
                download_url="https://github.com/ultralytics/yolov5",
            ),
        }

        return models.get(task)

    def get_recommended_datasets(self, region: str = "middle_east") -> list[str]:
        """
        Get recommended datasets for a region.
        الحصول على مجموعات البيانات الموصى بها لمنطقة
        """
        if region == "middle_east":
            return [
                "wheat_rust",  # Common in Saudi Arabia
                "date_palm_disease",  # Native crop
                "tomato_disease",  # Major vegetable crop
                "deepweeds",  # For field management
                "crop_yield_prediction",  # For advisory
            ]
        return list(self._datasets_catalog.keys())
