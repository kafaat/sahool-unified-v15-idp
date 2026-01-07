"""
SAHOOL Disease Detection CNN Model Wrapper
نموذج الشبكة العصبية التلافيفية لاكتشاف أمراض المحاصيل

This module provides a comprehensive wrapper for disease detection in Yemen crops.
يوفر هذا الوحدة غلاف شامل لاكتشاف الأمراض في المحاصيل اليمنية.
"""

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image

# ML Framework imports (support both TensorFlow and PyTorch)
try:
    import tensorflow as tf

    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

try:
    import torch
    import torchvision.transforms as transforms

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Configure logging - تكوين السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiseaseConfig:
    """
    Configuration for disease detection model
    إعدادات نموذج اكتشاف الأمراض
    """

    # Supported diseases for Yemen crops - الأمراض المدعومة للمحاصيل اليمنية
    SUPPORTED_DISEASES = {
        "tomato_leaf_blight": {
            "name_ar": "لفحة أوراق الطماطم",
            "severity": "high",
            "treatment": "Apply copper-based fungicide",
            "treatment_ar": "استخدام مبيد فطري نحاسي",
        },
        "wheat_rust": {
            "name_ar": "صدأ القمح",
            "severity": "critical",
            "treatment": "Apply triazole fungicides",
            "treatment_ar": "استخدام مبيدات الفطريات ترايازول",
        },
        "grape_downy_mildew": {
            "name_ar": "البياض الزغبي للعنب",
            "severity": "high",
            "treatment": "Apply mancozeb or copper fungicides",
            "treatment_ar": "استخدام مانكوزيب أو مبيدات نحاسية",
        },
        "date_palm_bayoud": {
            "name_ar": "مرض البيوض في النخيل",
            "severity": "critical",
            "treatment": "Remove infected trees, soil treatment",
            "treatment_ar": "إزالة الأشجار المصابة، معالجة التربة",
        },
        "coffee_leaf_rust": {
            "name_ar": "صدأ أوراق البن",
            "severity": "high",
            "treatment": "Apply copper-based fungicides, improve air circulation",
            "treatment_ar": "استخدام مبيدات نحاسية، تحسين دوران الهواء",
        },
        "banana_fusarium": {
            "name_ar": "فطر الفيوزاريوم في الموز",
            "severity": "critical",
            "treatment": "Use resistant varieties, soil fumigation",
            "treatment_ar": "استخدام أصناف مقاومة، تبخير التربة",
        },
        "mango_anthracnose": {
            "name_ar": "أنثراكنوز المانجو",
            "severity": "medium",
            "treatment": "Apply copper fungicides, improve drainage",
            "treatment_ar": "استخدام مبيدات نحاسية، تحسين الصرف",
        },
        "healthy": {
            "name_ar": "سليم",
            "severity": "none",
            "treatment": "No treatment needed",
            "treatment_ar": "لا حاجة للعلاج",
        },
    }

    # Model configuration - إعدادات النموذج
    DEFAULT_INPUT_SIZE = 224
    DEFAULT_MODEL_VERSION = "v1.0.0"
    MODEL_DOWNLOAD_URL = "https://models.sahool.com/disease-detection/"
    MODELS_DIR = Path("/app/models/disease_detection")
    CACHE_DIR = Path("/tmp/sahool_model_cache")

    # Preprocessing configuration - إعدادات المعالجة المسبقة
    NORMALIZATION_MEAN = [0.485, 0.456, 0.406]  # ImageNet mean
    NORMALIZATION_STD = [0.229, 0.224, 0.225]  # ImageNet std

    # TTA (Test Time Augmentation) configuration
    TTA_ENABLED = True
    TTA_AUGMENTATIONS = 5


class DiseaseCNNModel:
    """
    Disease Detection CNN Model Wrapper
    غلاف نموذج CNN لاكتشاف الأمراض

    This class provides a comprehensive interface for disease detection in crops.
    توفر هذه الفئة واجهة شاملة لاكتشاف الأمراض في المحاصيل.
    """

    def __init__(
        self,
        model_path: str | None = None,
        framework: str = "auto",
        device: str = "auto",
        enable_gpu: bool = True,
    ):
        """
        Initialize Disease CNN Model
        تهيئة نموذج CNN للأمراض

        Args:
            model_path: Path to the model file - مسار ملف النموذج
            framework: ML framework to use ('tensorflow', 'pytorch', 'auto') - إطار العمل
            device: Device to run on ('cpu', 'cuda', 'auto') - الجهاز المستخدم
            enable_gpu: Enable GPU acceleration - تفعيل تسريع GPU
        """
        self.model_path = model_path
        self.framework = self._detect_framework(framework)
        self.device = self._detect_device(device, enable_gpu)
        self.model = None
        self.config = DiseaseConfig()
        self.model_version = None
        self.is_warmed_up = False

        # Thread pool for batch processing - مجموعة الخيوط للمعالجة الدفعية
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Performance metrics - مقاييس الأداء
        self.metrics = {
            "total_predictions": 0,
            "avg_inference_time_ms": 0,
            "cache_hits": 0,
            "errors": 0,
        }

        # ONNX flag for special handling
        # علم ONNX للمعالجة الخاصة
        self._is_onnx = False

        logger.info(
            f"Initialized DiseaseCNNModel with framework: {self.framework}, device: {self.device}"
        )

    def _detect_framework(self, framework: str) -> str:
        """
        Detect available ML framework
        اكتشاف إطار العمل المتاح
        """
        if framework == "auto":
            if TF_AVAILABLE:
                return "tensorflow"
            elif TORCH_AVAILABLE:
                return "pytorch"
            else:
                raise RuntimeError("No ML framework available. Install TensorFlow or PyTorch.")

        if framework == "tensorflow" and not TF_AVAILABLE:
            raise RuntimeError("TensorFlow not available")
        if framework == "pytorch" and not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch not available")

        return framework

    def _detect_device(self, device: str, enable_gpu: bool) -> str:
        """
        Detect available device for computation
        اكتشاف الجهاز المتاح للحساب
        """
        if device != "auto":
            return device

        if not enable_gpu:
            return "cpu"

        if self.framework == "tensorflow" and TF_AVAILABLE:
            gpus = tf.config.list_physical_devices("GPU")
            return "gpu" if gpus else "cpu"

        if self.framework == "pytorch" and TORCH_AVAILABLE:
            return "cuda" if torch.cuda.is_available() else "cpu"

        return "cpu"

    def load_model(self, model_path: str) -> bool:
        """
        Load disease detection model from file
        تحميل نموذج اكتشاف الأمراض من ملف

        Args:
            model_path: Path to model file - مسار ملف النموذج

        Returns:
            bool: True if successful - صحيح إذا نجح التحميل
        """
        try:
            logger.info(f"Loading model from: {model_path}")

            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")

            self.model_path = model_path

            # Load based on framework - تحميل حسب إطار العمل
            if self.framework == "tensorflow":
                self.model = tf.keras.models.load_model(model_path)
                logger.info("Model loaded successfully with TensorFlow")

            elif self.framework == "pytorch":
                # Security: Only support safe serialization formats (no pickle)
                # الأمان: دعم صيغ التسلسل الآمنة فقط (بدون pickle)
                if model_path.endswith(".onnx"):
                    # ONNX format - safest and recommended option
                    # صيغة ONNX - الخيار الأكثر أماناً والموصى به
                    try:
                        import onnxruntime as ort

                        self.model = ort.InferenceSession(model_path)
                        self._is_onnx = True
                        logger.info("Model loaded successfully with ONNX Runtime")
                    except ImportError:
                        raise RuntimeError(
                            "onnxruntime required for ONNX models: pip install onnxruntime"
                        )
                elif model_path.endswith(".safetensors"):
                    # SafeTensors format - safe alternative to pickle
                    # صيغة SafeTensors - بديل آمن لـ pickle
                    try:
                        from safetensors.torch import load_file
                        from torchvision import models

                        self.model = models.resnet50(weights=None)
                        self.model.fc = torch.nn.Linear(2048, len(self.config.SUPPORTED_DISEASES))
                        state_dict = load_file(model_path)
                        self.model.load_state_dict(state_dict)
                        self.model.to(self.device)
                        self.model.eval()
                        logger.info("Model loaded successfully with SafeTensors")
                    except ImportError:
                        raise RuntimeError("safetensors required: pip install safetensors")
                else:
                    # Unsupported format - recommend conversion to ONNX or SafeTensors
                    # صيغة غير مدعومة - يُنصح بالتحويل إلى ONNX أو SafeTensors
                    supported = [".onnx", ".safetensors"]
                    raise ValueError(
                        f"Unsupported model format. For security, only {supported} are allowed. "
                        f"صيغة غير مدعومة. للأمان، الصيغ المسموحة فقط: {supported}. "
                        f"Convert using: torch.onnx.export() or safetensors.torch.save_file()"
                    )

            # Extract model version from metadata - استخراج إصدار النموذج
            self.model_version = self._extract_model_version(model_path)

            return True

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.metrics["errors"] += 1
            return False

    def _extract_model_version(self, model_path: str) -> str:
        """
        Extract model version from path or metadata
        استخراج إصدار النموذج من المسار أو البيانات الوصفية
        """
        # Try to read version from accompanying metadata file
        metadata_path = Path(model_path).parent / "metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path) as f:
                    metadata = json.load(f)
                    return metadata.get("version", self.config.DEFAULT_MODEL_VERSION)
            except Exception:
                pass

        # Default version
        return self.config.DEFAULT_MODEL_VERSION

    def preprocess_image(
        self, image_data: str | np.ndarray | Image.Image, target_size: int | None = None
    ) -> np.ndarray:
        """
        Preprocess image for model input
        معالجة الصورة مسبقاً لإدخال النموذج

        Args:
            image_data: Image as path, numpy array, or PIL Image - الصورة
            target_size: Target size for resizing - الحجم المستهدف

        Returns:
            Preprocessed image array - مصفوفة الصورة المعالجة
        """
        try:
            # Load image - تحميل الصورة
            if isinstance(image_data, str):
                image = Image.open(image_data).convert("RGB")
            elif isinstance(image_data, np.ndarray):
                image = Image.fromarray(image_data).convert("RGB")
            elif isinstance(image_data, Image.Image):
                image = image_data.convert("RGB")
            else:
                raise ValueError(f"Unsupported image type: {type(image_data)}")

            # Resize - تغيير الحجم
            size = target_size or self.config.DEFAULT_INPUT_SIZE
            image = self.resize_to_input_size(image, size)

            # Convert to array - تحويل إلى مصفوفة
            img_array = np.array(image)

            # Normalize - تطبيع
            img_array = self.normalize_pixels(img_array)

            return img_array

        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise

    def resize_to_input_size(self, image: Image.Image | np.ndarray, size: int = 224) -> Image.Image:
        """
        Resize image to model input size
        تغيير حجم الصورة إلى حجم إدخال النموذج

        Args:
            image: Input image - الصورة المدخلة
            size: Target size - الحجم المستهدف

        Returns:
            Resized PIL Image - صورة PIL بحجم معدل
        """
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # Use high-quality Lanczos resampling - استخدام إعادة العينة عالية الجودة
        return image.resize((size, size), Image.Resampling.LANCZOS)

    def normalize_pixels(self, image: np.ndarray) -> np.ndarray:
        """
        Normalize pixel values using ImageNet statistics
        تطبيع قيم البكسل باستخدام إحصائيات ImageNet

        Args:
            image: Input image array - مصفوفة الصورة المدخلة

        Returns:
            Normalized image array - مصفوفة الصورة المطبعة
        """
        # Scale to [0, 1] - تحجيم إلى [0، 1]
        image = image.astype(np.float32) / 255.0

        # Apply ImageNet normalization - تطبيق تطبيع ImageNet
        mean = np.array(self.config.NORMALIZATION_MEAN)
        std = np.array(self.config.NORMALIZATION_STD)

        image = (image - mean) / std

        return image

    def augment_for_inference(
        self, image: np.ndarray, n_augmentations: int = 5
    ) -> list[np.ndarray]:
        """
        Apply Test Time Augmentation (TTA) for robust predictions
        تطبيق التعزيز في وقت الاختبار للتنبؤات القوية

        Args:
            image: Input image - الصورة المدخلة
            n_augmentations: Number of augmentations - عدد التعزيزات

        Returns:
            List of augmented images - قائمة الصور المعززة
        """
        if not self.config.TTA_ENABLED:
            return [image]

        augmented = [image]  # Original image

        # Horizontal flip - قلب أفقي
        augmented.append(np.fliplr(image))

        # Slight rotations - دورانات طفيفة
        for angle in [-10, 10]:
            pil_img = Image.fromarray((image * 255).astype(np.uint8))
            rotated = pil_img.rotate(angle, fillcolor=(0, 0, 0))
            rotated_array = np.array(rotated).astype(np.float32) / 255.0
            augmented.append(rotated_array)

        # Brightness adjustment - تعديل السطوع
        brightened = np.clip(image * 1.1, 0, 1)
        augmented.append(brightened)

        return augmented[:n_augmentations]

    def predict(
        self, image: str | np.ndarray | Image.Image, return_bbox: bool = True
    ) -> tuple[str, float, dict | None]:
        """
        Predict disease from image
        التنبؤ بالمرض من الصورة

        Args:
            image: Input image - الصورة المدخلة
            return_bbox: Return bounding box if available - إرجاع صندوق الحدود

        Returns:
            Tuple of (disease_name, confidence, bbox_dict) - (اسم المرض، الثقة، صندوق الحدود)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        start_time = datetime.now()

        try:
            # Preprocess - معالجة مسبقة
            img_array = self.preprocess_image(image)

            # Add batch dimension - إضافة بُعد الدفعة
            if self.framework == "tensorflow":
                img_batch = np.expand_dims(img_array, axis=0)
                predictions = self.model.predict(img_batch, verbose=0)[0]

            elif self.framework == "pytorch":
                img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).unsqueeze(0)
                img_tensor = img_tensor.to(self.device)
                with torch.no_grad():
                    predictions = self.model(img_tensor).cpu().numpy()[0]

            # Get top prediction - الحصول على أعلى تنبؤ
            disease_idx = np.argmax(predictions)
            confidence = float(predictions[disease_idx])
            disease_name = list(self.config.SUPPORTED_DISEASES.keys())[disease_idx]

            # Bounding box (placeholder - would need object detection model)
            # صندوق الحدود (نائب - يحتاج نموذج كشف الأشياء)
            bbox = None
            if return_bbox:
                bbox = self._estimate_disease_region(image)

            # Update metrics - تحديث المقاييس
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            self._update_metrics(elapsed)

            logger.info(f"Predicted: {disease_name} with confidence {confidence:.3f}")

            return disease_name, confidence, bbox

        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            self.metrics["errors"] += 1
            raise

    def _estimate_disease_region(self, image: str | np.ndarray | Image.Image) -> dict | None:
        """
        Estimate disease-affected region using simple image processing
        تقدير المنطقة المصابة باستخدام معالجة الصور البسيطة

        This is a placeholder. For production, use proper object detection.
        هذا نائب. للإنتاج، استخدم كشف الأشياء المناسب.
        """
        try:
            # Load image
            if isinstance(image, str):
                img = cv2.imread(image)
            elif isinstance(image, Image.Image):
                img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                img = image

            # Simple color-based segmentation for diseased areas
            # تجزئة بسيطة على أساس اللون للمناطق المصابة
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # Detect brown/yellow discoloration (common in diseases)
            # كشف تغير اللون البني/الأصفر (شائع في الأمراض)
            lower_brown = np.array([10, 50, 50])
            upper_brown = np.array([30, 255, 200])
            mask = cv2.inRange(hsv, lower_brown, upper_brown)

            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                # Get largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)

                return {
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "confidence": 0.7,  # Placeholder confidence
                }

            return None

        except Exception as e:
            logger.warning(f"Could not estimate disease region: {e}")
            return None

    def get_top_k_predictions(
        self, image: str | np.ndarray | Image.Image, k: int = 3
    ) -> list[dict[str, Any]]:
        """
        Get top K disease predictions
        الحصول على أعلى K تنبؤات للأمراض

        Args:
            image: Input image - الصورة المدخلة
            k: Number of top predictions - عدد التنبؤات العليا

        Returns:
            List of prediction dictionaries - قائمة قواميس التنبؤ
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        try:
            # Preprocess - معالجة مسبقة
            img_array = self.preprocess_image(image)

            # Predict - تنبؤ
            if self.framework == "tensorflow":
                img_batch = np.expand_dims(img_array, axis=0)
                predictions = self.model.predict(img_batch, verbose=0)[0]

            elif self.framework == "pytorch":
                img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).unsqueeze(0)
                img_tensor = img_tensor.to(self.device)
                with torch.no_grad():
                    predictions = self.model(img_tensor).cpu().numpy()[0]

            # Get top k indices - الحصول على أعلى k مؤشرات
            top_k_indices = np.argsort(predictions)[-k:][::-1]

            results = []
            disease_names = list(self.config.SUPPORTED_DISEASES.keys())

            for idx in top_k_indices:
                disease_name = disease_names[idx]
                disease_info = self.config.SUPPORTED_DISEASES[disease_name]

                results.append(
                    {
                        "disease": disease_name,
                        "disease_ar": disease_info["name_ar"],
                        "confidence": float(predictions[idx]),
                        "severity": disease_info["severity"],
                        "treatment": disease_info["treatment"],
                        "treatment_ar": disease_info["treatment_ar"],
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Error getting top-k predictions: {e}")
            raise

    def visualize_predictions(
        self,
        image: str | np.ndarray | Image.Image,
        predictions: list[dict[str, Any]],
        output_path: str | None = None,
    ) -> np.ndarray:
        """
        Visualize predictions on image
        تصور التنبؤات على الصورة

        Args:
            image: Input image - الصورة المدخلة
            predictions: List of predictions from get_top_k_predictions - قائمة التنبؤات
            output_path: Optional path to save visualization - مسار اختياري لحفظ التصور

        Returns:
            Visualized image array - مصفوفة الصورة المصورة
        """
        try:
            # Load image
            if isinstance(image, str):
                img = cv2.imread(image)
            elif isinstance(image, Image.Image):
                img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                img = image.copy()

            # Create visualization
            h, w = img.shape[:2]

            # Add semi-transparent overlay for text - إضافة طبقة شفافة للنص
            overlay = img.copy()

            # Draw predictions - رسم التنبؤات
            y_offset = 30
            for i, pred in enumerate(predictions[:3]):  # Top 3
                disease = pred["disease"]
                disease_ar = pred["disease_ar"]
                confidence = pred["confidence"]
                severity = pred["severity"]

                # Color based on severity - اللون بناءً على الخطورة
                if severity == "critical":
                    color = (0, 0, 255)  # Red
                elif severity == "high":
                    color = (0, 165, 255)  # Orange
                elif severity == "medium":
                    color = (0, 255, 255)  # Yellow
                else:
                    color = (0, 255, 0)  # Green

                # Draw text - رسم النص
                text = f"{i + 1}. {disease} ({disease_ar}) - {confidence * 100:.1f}%"
                cv2.putText(overlay, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                y_offset += 30

            # Blend overlay - دمج الطبقة
            alpha = 0.7
            img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

            # Save if path provided - حفظ إذا تم توفير المسار
            if output_path:
                cv2.imwrite(output_path, img)
                logger.info(f"Visualization saved to: {output_path}")

            return img

        except Exception as e:
            logger.error(f"Error visualizing predictions: {e}")
            raise

    async def download_model(self, version: str = "latest") -> str:
        """
        Download model from remote server
        تحميل النموذج من الخادم البعيد

        Args:
            version: Model version to download - إصدار النموذج للتحميل

        Returns:
            Path to downloaded model - مسار النموذج المحمل
        """
        try:
            import aiohttp

            # Create models directory - إنشاء مجلد النماذج
            self.config.MODELS_DIR.mkdir(parents=True, exist_ok=True)

            # Construct download URL - بناء رابط التحميل
            if version == "latest":
                version = self.config.DEFAULT_MODEL_VERSION

            model_filename = f"disease_model_{version}.h5"
            download_url = f"{self.config.MODEL_DOWNLOAD_URL}{model_filename}"
            local_path = self.config.MODELS_DIR / model_filename

            # Download - تحميل
            logger.info(f"Downloading model from: {download_url}")

            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as response:
                    if response.status == 200:
                        with open(local_path, "wb") as f:
                            f.write(await response.read())
                        logger.info(f"Model downloaded successfully to: {local_path}")
                        return str(local_path)
                    else:
                        raise RuntimeError(f"Failed to download model: HTTP {response.status}")

        except Exception as e:
            logger.error(f"Error downloading model: {e}")
            raise

    def get_model_version(self) -> str:
        """
        Get current model version
        الحصول على إصدار النموذج الحالي

        Returns:
            Model version string - سلسلة إصدار النموذج
        """
        return self.model_version or "unknown"

    def warm_up_model(self, num_iterations: int = 5) -> None:
        """
        Warm up model with dummy predictions for optimal performance
        تسخين النموذج بتنبؤات وهمية للأداء الأمثل

        Args:
            num_iterations: Number of warm-up iterations - عدد تكرارات التسخين
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        logger.info(f"Warming up model with {num_iterations} iterations...")

        try:
            # Create dummy image - إنشاء صورة وهمية
            dummy_image = np.random.rand(
                self.config.DEFAULT_INPUT_SIZE, self.config.DEFAULT_INPUT_SIZE, 3
            ).astype(np.float32)

            # Run predictions - تشغيل التنبؤات
            for _i in range(num_iterations):
                if self.framework == "tensorflow":
                    img_batch = np.expand_dims(dummy_image, axis=0)
                    _ = self.model.predict(img_batch, verbose=0)

                elif self.framework == "pytorch":
                    img_tensor = torch.from_numpy(dummy_image).permute(2, 0, 1).unsqueeze(0)
                    img_tensor = img_tensor.to(self.device)
                    with torch.no_grad():
                        _ = self.model(img_tensor)

            self.is_warmed_up = True
            logger.info("Model warm-up completed")

        except Exception as e:
            logger.error(f"Error during warm-up: {e}")
            raise

    def predict_batch(
        self, images: list[str | np.ndarray | Image.Image], batch_size: int = 8
    ) -> list[tuple[str, float, dict | None]]:
        """
        Predict diseases for a batch of images
        التنبؤ بالأمراض لدفعة من الصور

        Args:
            images: List of images - قائمة الصور
            batch_size: Batch size for processing - حجم الدفعة للمعالجة

        Returns:
            List of predictions - قائمة التنبؤات
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        logger.info(f"Processing batch of {len(images)} images")

        try:
            results = []

            # Process in batches - معالجة في دفعات
            for i in range(0, len(images), batch_size):
                batch = images[i : i + batch_size]

                # Preprocess batch - معالجة الدفعة مسبقاً
                batch_arrays = [self.preprocess_image(img) for img in batch]
                batch_array = np.stack(batch_arrays, axis=0)

                # Predict - تنبؤ
                if self.framework == "tensorflow":
                    predictions = self.model.predict(batch_array, verbose=0)

                elif self.framework == "pytorch":
                    batch_tensor = torch.from_numpy(batch_array).permute(0, 3, 1, 2)
                    batch_tensor = batch_tensor.to(self.device)
                    with torch.no_grad():
                        predictions = self.model(batch_tensor).cpu().numpy()

                # Process predictions - معالجة التنبؤات
                disease_names = list(self.config.SUPPORTED_DISEASES.keys())
                for j, pred in enumerate(predictions):
                    disease_idx = np.argmax(pred)
                    disease_name = disease_names[disease_idx]
                    confidence = float(pred[disease_idx])
                    bbox = self._estimate_disease_region(batch[j])

                    results.append((disease_name, confidence, bbox))

            logger.info(f"Batch processing completed: {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Error in batch prediction: {e}")
            raise

    async def process_field_images(
        self,
        field_id: str,
        images: list[str | np.ndarray | Image.Image],
        min_confidence: float = 0.5,
    ) -> dict[str, Any]:
        """
        Process all images from a field and generate comprehensive report
        معالجة جميع الصور من حقل وإنشاء تقرير شامل

        Args:
            field_id: Field identifier - معرف الحقل
            images: List of field images - قائمة صور الحقل
            min_confidence: Minimum confidence threshold - الحد الأدنى للثقة

        Returns:
            Comprehensive field analysis report - تقرير تحليل الحقل الشامل
        """
        logger.info(f"Processing {len(images)} images for field: {field_id}")

        try:
            # Batch predict - تنبؤ دفعي
            predictions = self.predict_batch(images)

            # Analyze results - تحليل النتائج
            disease_counts = {}
            high_confidence_detections = []
            total_diseased = 0

            for i, (disease, confidence, bbox) in enumerate(predictions):
                if confidence >= min_confidence:
                    disease_counts[disease] = disease_counts.get(disease, 0) + 1

                    if disease != "healthy":
                        total_diseased += 1

                        disease_info = self.config.SUPPORTED_DISEASES[disease]
                        high_confidence_detections.append(
                            {
                                "image_index": i,
                                "disease": disease,
                                "disease_ar": disease_info["name_ar"],
                                "confidence": confidence,
                                "severity": disease_info["severity"],
                                "bbox": bbox,
                                "treatment": disease_info["treatment"],
                                "treatment_ar": disease_info["treatment_ar"],
                            }
                        )

            # Calculate statistics - حساب الإحصائيات
            total_images = len(images)
            health_percentage = ((total_images - total_diseased) / total_images) * 100

            # Determine overall field health - تحديد الصحة العامة للحقل
            if health_percentage >= 80:
                field_status = "healthy"
                field_status_ar = "سليم"
            elif health_percentage >= 60:
                field_status = "moderate"
                field_status_ar = "متوسط"
            else:
                field_status = "critical"
                field_status_ar = "حرج"

            # Generate report - إنشاء التقرير
            report = {
                "field_id": field_id,
                "timestamp": datetime.now().isoformat(),
                "total_images": total_images,
                "total_diseased": total_diseased,
                "health_percentage": round(health_percentage, 2),
                "field_status": field_status,
                "field_status_ar": field_status_ar,
                "disease_distribution": disease_counts,
                "detections": high_confidence_detections,
                "recommendations": self._generate_recommendations(disease_counts),
                "model_version": self.get_model_version(),
            }

            logger.info(f"Field analysis completed for {field_id}: {field_status}")

            return report

        except Exception as e:
            logger.error(f"Error processing field images: {e}")
            raise

    def _generate_recommendations(self, disease_counts: dict[str, int]) -> list[dict[str, str]]:
        """
        Generate treatment recommendations based on detected diseases
        إنشاء توصيات العلاج بناءً على الأمراض المكتشفة

        Args:
            disease_counts: Dictionary of disease counts - قاموس أعداد الأمراض

        Returns:
            List of recommendations - قائمة التوصيات
        """
        recommendations = []

        # Sort diseases by count - ترتيب الأمراض حسب العدد
        sorted_diseases = sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)

        for disease, count in sorted_diseases:
            if disease == "healthy":
                continue

            disease_info = self.config.SUPPORTED_DISEASES[disease]

            recommendations.append(
                {
                    "disease": disease,
                    "disease_ar": disease_info["name_ar"],
                    "affected_count": count,
                    "severity": disease_info["severity"],
                    "treatment": disease_info["treatment"],
                    "treatment_ar": disease_info["treatment_ar"],
                    "priority": "high"
                    if disease_info["severity"] in ["critical", "high"]
                    else "medium",
                }
            )

        return recommendations

    def _update_metrics(self, inference_time_ms: float) -> None:
        """
        Update performance metrics
        تحديث مقاييس الأداء
        """
        self.metrics["total_predictions"] += 1

        # Update running average - تحديث المتوسط الجاري
        n = self.metrics["total_predictions"]
        old_avg = self.metrics["avg_inference_time_ms"]
        self.metrics["avg_inference_time_ms"] = (old_avg * (n - 1) + inference_time_ms) / n

    def get_metrics(self) -> dict[str, Any]:
        """
        Get model performance metrics
        الحصول على مقاييس أداء النموذج

        Returns:
            Dictionary of metrics - قاموس المقاييس
        """
        return {
            **self.metrics,
            "model_version": self.get_model_version(),
            "framework": self.framework,
            "device": self.device,
            "is_warmed_up": self.is_warmed_up,
            "supported_diseases": len(self.config.SUPPORTED_DISEASES),
        }

    def __del__(self):
        """Cleanup resources - تنظيف الموارد"""
        try:
            if hasattr(self, "executor"):
                self.executor.shutdown(wait=True)
        except Exception:
            pass
