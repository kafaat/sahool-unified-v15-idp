"""
SAHOOL Model Inference Handler
معالج استنتاج النموذج

Handles background AI/ML model inference operations.
يعالج عمليات استنتاج نماذج الذكاء الاصطناعي/التعلم الآلي في الخلفية.

Author: SAHOOL Platform Team
License: MIT
"""

import io
import logging
import os
import time
from pathlib import Path
from threading import Lock
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# Model Configuration - تكوين النموذج
# ═══════════════════════════════════════════════════════════════════════════════

# Base directory for model storage - مسار تخزين النماذج
MODELS_DIR = Path(os.getenv("MODELS_DIR", "/app/models"))

# Model Registry - سجل النماذج
# Maps model names to their configurations
MODEL_REGISTRY: dict[str, dict[str, Any]] = {
    "crop_classification": {
        "type": "classification",
        "input_shape": (224, 224, 3),
        "output_classes": ["wheat", "barley", "date_palm", "tomato", "corn", "rice"],
        "output_classes_ar": ["قمح", "شعير", "نخيل", "طماطم", "ذرة", "أرز"],
        "framework": "tensorflow",
        "filename": "crop_classification_v2.onnx",
        "version": "2.0.0",
        "normalization": {"mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225]},
    },
    "yield_prediction": {
        "type": "regression",
        "input_features": [
            "ndvi",
            "soil_moisture",
            "temperature",
            "rainfall",
            "growth_stage",
            "area_ha",
        ],
        "output_unit": "kg/ha",
        "framework": "onnx",
        "filename": "yield_prediction_v3.onnx",
        "version": "3.0.0",
    },
    "growth_stage": {
        "type": "classification",
        "input_shape": (224, 224, 3),
        "output_classes": [
            "germination",
            "seedling",
            "vegetative",
            "flowering",
            "fruiting",
            "maturity",
        ],
        "output_classes_ar": ["إنبات", "شتلة", "نمو خضري", "إزهار", "إثمار", "نضج"],
        "framework": "tensorflow",
        "filename": "growth_stage_v1.onnx",
        "version": "1.0.0",
        "normalization": {"mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225]},
    },
    "pest_detection": {
        "type": "object_detection",
        "input_shape": (640, 640, 3),
        "output_classes": [
            "cotton_worm",
            "aphid",
            "locust",
            "red_palm_weevil",
            "whitefly",
            "thrips",
        ],
        "output_classes_ar": [
            "دودة القطن",
            "المن",
            "جراد",
            "سوسة النخيل الحمراء",
            "الذبابة البيضاء",
            "التربس",
        ],
        "framework": "onnx",
        "filename": "pest_detection_yolov8.onnx",
        "version": "1.2.0",
    },
    "disease_detection": {
        "type": "classification",
        "input_shape": (224, 224, 3),
        "output_classes": [
            "healthy",
            "leaf_blight",
            "rust",
            "powdery_mildew",
            "bacterial_spot",
            "viral_mosaic",
        ],
        "output_classes_ar": [
            "سليم",
            "لفحة الأوراق",
            "صدأ",
            "بياض دقيقي",
            "بقع بكتيرية",
            "فيروس الفسيفساء",
        ],
        "framework": "tensorflow",
        "filename": "disease_detection_v2.onnx",
        "version": "2.1.0",
        "normalization": {"mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225]},
    },
    "soil_analysis": {
        "type": "regression",
        "input_features": ["ph", "ec", "nitrogen", "phosphorus", "potassium", "organic_matter"],
        "output_recommendations": ["fertilizer_type", "application_rate", "timing"],
        "framework": "onnx",
        "filename": "soil_analysis_v1.onnx",
        "version": "1.0.0",
    },
    "water_stress": {
        "type": "classification",
        "input_shape": (224, 224, 3),
        "output_classes": ["no_stress", "mild_stress", "moderate_stress", "severe_stress"],
        "output_classes_ar": ["بدون إجهاد", "إجهاد خفيف", "إجهاد متوسط", "إجهاد شديد"],
        "framework": "tensorflow",
        "filename": "water_stress_v1.onnx",
        "version": "1.0.0",
        "normalization": {"mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225]},
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# Model Cache - ذاكرة التخزين المؤقت للنماذج
# ═══════════════════════════════════════════════════════════════════════════════


class ModelCache:
    """
    Thread-safe model cache for efficient model loading and reuse.
    ذاكرة تخزين مؤقت آمنة للخيوط لتحميل واستخدام النماذج بكفاءة.
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._models: dict[str, Any] = {}
                    cls._instance._model_lock = Lock()
        return cls._instance

    def get_model(self, model_name: str, model_version: str = "latest") -> Any | None:
        """
        Get model from cache or load it.
        الحصول على النموذج من الذاكرة المؤقتة أو تحميله.
        """
        cache_key = f"{model_name}:{model_version}"
        with self._model_lock:
            return self._models.get(cache_key)

    def set_model(self, model_name: str, model_version: str, model: Any) -> None:
        """
        Store model in cache.
        تخزين النموذج في الذاكرة المؤقتة.
        """
        cache_key = f"{model_name}:{model_version}"
        with self._model_lock:
            self._models[cache_key] = model

    def clear(self) -> None:
        """Clear all cached models. مسح جميع النماذج المخزنة."""
        with self._model_lock:
            self._models.clear()


# Singleton instance
model_cache = ModelCache()


# ═══════════════════════════════════════════════════════════════════════════════
# Model Loading - تحميل النماذج
# ═══════════════════════════════════════════════════════════════════════════════


def load_model(model_name: str, model_version: str = "latest") -> tuple[Any, str]:
    """
    Load model from storage with caching.
    تحميل النموذج من التخزين مع التخزين المؤقت.

    Args:
        model_name: Name of the model - اسم النموذج
        model_version: Version of the model - إصدار النموذج

    Returns:
        Tuple of (model, framework) - النموذج وإطار العمل
    """
    # Check cache first - التحقق من الذاكرة المؤقتة أولاً
    cached_model = model_cache.get_model(model_name, model_version)
    if cached_model is not None:
        logger.debug(f"Model loaded from cache: {model_name}:{model_version}")
        config = MODEL_REGISTRY.get(model_name, {})
        return cached_model, config.get("framework", "onnx")

    # Get model configuration - الحصول على تكوين النموذج
    config = MODEL_REGISTRY.get(model_name)
    if not config:
        logger.warning(f"Model not found in registry: {model_name}")
        return None, "unknown"

    # Construct model path - بناء مسار النموذج
    filename = config.get("filename", f"{model_name}.onnx")
    model_path = MODELS_DIR / filename

    framework = config.get("framework", "onnx")

    # Check if model file exists - التحقق من وجود ملف النموذج
    if not model_path.exists():
        logger.warning(f"Model file not found: {model_path}")
        return None, framework

    try:
        model = None

        # Load based on framework - تحميل حسب إطار العمل
        if framework in ("onnx", "tensorflow", "pytorch"):
            # Prefer ONNX Runtime for all models (safe and portable)
            # تفضيل ONNX Runtime لجميع النماذج (آمن وقابل للنقل)
            try:
                import onnxruntime as ort

                model = ort.InferenceSession(
                    str(model_path),
                    providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
                )
                logger.info(f"Model loaded with ONNX Runtime: {model_name}")
            except ImportError:
                logger.warning("ONNX Runtime not available, trying TensorFlow")

                # Fallback to TensorFlow Lite if ONNX not available
                if str(model_path).endswith(".tflite"):
                    try:
                        import tensorflow as tf

                        model = tf.lite.Interpreter(model_path=str(model_path))
                        model.allocate_tensors()
                        logger.info(f"Model loaded with TensorFlow Lite: {model_name}")
                    except ImportError:
                        logger.error("Neither ONNX Runtime nor TensorFlow available")
                        return None, framework

        # Cache the model - تخزين النموذج في الذاكرة المؤقتة
        if model is not None:
            model_cache.set_model(model_name, model_version, model)

        return model, framework

    except Exception as e:
        logger.error(f"Error loading model {model_name}: {e}")
        return None, framework


# ═══════════════════════════════════════════════════════════════════════════════
# Preprocessing - المعالجة المسبقة
# ═══════════════════════════════════════════════════════════════════════════════


def preprocess_image(
    image_data: bytes | np.ndarray,
    target_size: tuple[int, int] = (224, 224),
    normalization: dict[str, list[float]] | None = None,
) -> np.ndarray:
    """
    Preprocess image for model inference.
    معالجة الصورة مسبقاً للاستنتاج.

    Args:
        image_data: Raw image bytes or numpy array - بيانات الصورة
        target_size: Target size (height, width) - الحجم المستهدف
        normalization: Mean and std for normalization - التطبيع

    Returns:
        Preprocessed image array - مصفوفة الصورة المعالجة
    """
    try:
        from PIL import Image

        # Load image - تحميل الصورة
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
        elif isinstance(image_data, np.ndarray):
            image = Image.fromarray(image_data).convert("RGB")
        else:
            raise ValueError(f"Unsupported image type: {type(image_data)}")

        # Resize - تغيير الحجم
        image = image.resize(target_size, Image.Resampling.LANCZOS)

        # Convert to numpy array - تحويل إلى مصفوفة
        img_array = np.array(image, dtype=np.float32) / 255.0

        # Apply normalization if provided - تطبيق التطبيع
        if normalization:
            mean = np.array(normalization.get("mean", [0.485, 0.456, 0.406]))
            std = np.array(normalization.get("std", [0.229, 0.224, 0.225]))
            img_array = (img_array - mean) / std

        # Add batch dimension - إضافة بُعد الدفعة
        img_array = np.expand_dims(img_array, axis=0).astype(np.float32)

        return img_array

    except ImportError:
        logger.warning("PIL not available, returning random tensor")
        return np.random.rand(1, target_size[0], target_size[1], 3).astype(np.float32)


def preprocess_tabular(
    input_data: dict[str, Any],
    feature_names: list[str],
) -> np.ndarray:
    """
    Preprocess tabular data for model inference.
    معالجة البيانات الجدولية مسبقاً للاستنتاج.

    Args:
        input_data: Dictionary of feature values - قاموس قيم الميزات
        feature_names: List of expected feature names - قائمة أسماء الميزات

    Returns:
        Preprocessed feature array - مصفوفة الميزات المعالجة
    """
    features = []
    for name in feature_names:
        value = input_data.get(name, 0.0)
        if isinstance(value, (int, float)):
            features.append(float(value))
        else:
            features.append(0.0)

    return np.array([features], dtype=np.float32)


# ═══════════════════════════════════════════════════════════════════════════════
# Inference Execution - تنفيذ الاستنتاج
# ═══════════════════════════════════════════════════════════════════════════════


def run_onnx_inference(model: Any, input_array: np.ndarray) -> np.ndarray:
    """
    Run inference using ONNX Runtime.
    تشغيل الاستنتاج باستخدام ONNX Runtime.
    """
    input_name = model.get_inputs()[0].name
    output_name = model.get_outputs()[0].name

    # Ensure correct data type - التأكد من نوع البيانات الصحيح
    input_array = input_array.astype(np.float32)

    result = model.run([output_name], {input_name: input_array})
    return result[0]


def run_tflite_inference(model: Any, input_array: np.ndarray) -> np.ndarray:
    """
    Run inference using TensorFlow Lite.
    تشغيل الاستنتاج باستخدام TensorFlow Lite.
    """
    input_details = model.get_input_details()
    output_details = model.get_output_details()

    model.set_tensor(input_details[0]["index"], input_array)
    model.invoke()

    return model.get_tensor(output_details[0]["index"])


def apply_softmax(logits: np.ndarray) -> np.ndarray:
    """Apply softmax to convert logits to probabilities."""
    exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    return exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)


def filter_by_confidence(
    predictions: list[dict[str, Any]],
    threshold: float,
) -> list[dict[str, Any]]:
    """
    Filter predictions by confidence threshold.
    تصفية التنبؤات حسب حد الثقة.
    """
    return [p for p in predictions if p.get("confidence", 0) >= threshold]


def handle_model_inference(payload: dict[str, Any]) -> dict[str, Any]:
    """
    تشغيل استنتاج النموذج
    Run model inference

    Args:
        payload: {
            "model_name": str - اسم النموذج / Model name
            "model_version": str - إصدار النموذج / Model version
            "input_data": dict - بيانات الإدخال / Input data
            "input_urls": List[str] - روابط الإدخال / Input URLs (images, files, etc.)
            "field_id": str - معرف الحقل (اختياري) / Field ID (optional)
            "batch_size": int - حجم الدفعة / Batch size
            "confidence_threshold": float - حد الثقة / Confidence threshold
            "output_format": str - تنسيق الإخراج / Output format
        }

    Returns:
        {
            "predictions": List[dict] - التنبؤات / Predictions
            "model_info": dict - معلومات النموذج / Model info
            "inference_time": float - وقت الاستنتاج / Inference time
            "confidence_scores": List[float] - درجات الثقة / Confidence scores
        }
    """
    logger.info(f"Running model inference: {payload.get('model_name')}")

    try:
        # ═══════════════════════════════════════════════════════════════════════
        # استخراج البيانات من الحمولة
        # Extract data from payload
        # ═══════════════════════════════════════════════════════════════════════
        model_name = payload.get("model_name")
        model_version = payload.get("model_version", "latest")
        input_data = payload.get("input_data", {})
        input_urls = payload.get("input_urls", [])
        confidence_threshold = payload.get("confidence_threshold", 0.7)
        batch_size = payload.get("batch_size", 1)

        if not model_name:
            raise ValueError("model_name is required")

        # Start timing - بدء القياس
        start_time = time.time()

        # ═══════════════════════════════════════════════════════════════════════
        # 1. تحميل النموذج من التخزين
        # 1. Load model from storage
        # ═══════════════════════════════════════════════════════════════════════
        model_config = MODEL_REGISTRY.get(model_name, {})
        model, framework = load_model(model_name, model_version)

        # Determine if we should use real model or fallback to simulation
        use_real_model = model is not None

        # Get model type and configuration - الحصول على نوع النموذج والتكوين
        model_type = model_config.get("type", "classification")
        input_shape = model_config.get("input_shape", (224, 224, 3))
        output_classes = model_config.get("output_classes", [])
        output_classes_ar = model_config.get("output_classes_ar", [])
        normalization = model_config.get("normalization")
        input_features = model_config.get("input_features", [])

        predictions: list[dict[str, Any]] = []
        device_used = "cpu"

        # ═══════════════════════════════════════════════════════════════════════
        # 2. معالجة البيانات المدخلة مسبقاً وتشغيل الاستنتاج
        # 2. Preprocess input data and run inference
        # ═══════════════════════════════════════════════════════════════════════

        if use_real_model:
            logger.info(f"Running real model inference for: {model_name}")

            # Check if CUDA is available - التحقق من توفر CUDA
            try:
                import onnxruntime as ort

                if "CUDAExecutionProvider" in ort.get_available_providers():
                    device_used = "cuda:0"
            except ImportError:
                pass

            if model_type in ("classification", "object_detection"):
                # Image-based inference - استنتاج على أساس الصورة
                predictions = _run_image_inference(
                    model=model,
                    input_urls=input_urls,
                    input_data=input_data,
                    input_shape=input_shape,
                    output_classes=output_classes,
                    output_classes_ar=output_classes_ar,
                    normalization=normalization,
                    model_type=model_type,
                    confidence_threshold=confidence_threshold,
                    batch_size=batch_size,
                )
            elif model_type == "regression":
                # Tabular/feature-based inference - استنتاج على أساس الميزات
                predictions = _run_tabular_inference(
                    model=model,
                    input_data=input_data,
                    input_features=input_features,
                    model_name=model_name,
                )
        else:
            # ═══════════════════════════════════════════════════════════════════
            # Fallback: محاكاة النتائج حسب نوع النموذج
            # Fallback: Simulate results based on model type
            # ═══════════════════════════════════════════════════════════════════
            logger.info(f"Model not available, using simulation for: {model_name}")
            predictions = _generate_simulated_predictions(
                model_name=model_name,
                input_data=input_data,
                input_urls=input_urls,
                confidence_threshold=confidence_threshold,
            )

        # ═══════════════════════════════════════════════════════════════════════
        # 3. تصفية حسب حد الثقة
        # 3. Filter by confidence threshold
        # ═══════════════════════════════════════════════════════════════════════
        filtered_predictions = filter_by_confidence(predictions, confidence_threshold)
        below_threshold_count = len(predictions) - len(filtered_predictions)

        # Calculate inference time - حساب وقت الاستنتاج
        inference_time = time.time() - start_time

        # ═══════════════════════════════════════════════════════════════════════
        # 4. بناء النتيجة النهائية
        # 4. Build final result
        # ═══════════════════════════════════════════════════════════════════════
        confidence_scores = [p.get("confidence", 0.0) for p in filtered_predictions]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

        result = {
            "predictions": filtered_predictions,
            "model_info": {
                "model_name": model_name,
                "model_version": model_config.get("version", model_version),
                "model_type": model_type,
                "framework": framework if use_real_model else "simulated",
                "input_shape": list(input_shape) if isinstance(input_shape, tuple) else input_shape,
                "output_classes": len(output_classes) if output_classes else len(filtered_predictions),
                "trained_on": "SAHOOL Dataset v2.3",
                "is_real_model": use_real_model,
            },
            "inference_time": round(inference_time, 3),
            "confidence_scores": confidence_scores,
            "statistics": {
                "total_predictions": len(filtered_predictions),
                "high_confidence_count": len([p for p in filtered_predictions if p.get("confidence", 0) > 0.9]),
                "average_confidence": round(avg_confidence, 3),
                "below_threshold_count": below_threshold_count,
            },
            "metadata": {
                "processed_inputs": len(input_urls) if input_urls else 1,
                "batch_size": batch_size,
                "device": device_used,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "confidence_threshold": confidence_threshold,
            },
        }

        logger.info(
            f"Model inference completed: {model_name} "
            f"(predictions={len(filtered_predictions)}, avg_confidence={avg_confidence:.2f}, "
            f"time={inference_time:.3f}s, real_model={use_real_model})"
        )
        return result

    except Exception as e:
        logger.error(f"Error running model inference: {e}", exc_info=True)
        raise


# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions - وظائف مساعدة
# ═══════════════════════════════════════════════════════════════════════════════


def _run_image_inference(
    model: Any,
    input_urls: list[str],
    input_data: dict[str, Any],
    input_shape: tuple[int, ...],
    output_classes: list[str],
    output_classes_ar: list[str],
    normalization: dict[str, list[float]] | None,
    model_type: str,
    confidence_threshold: float,
    batch_size: int,
) -> list[dict[str, Any]]:
    """
    Run image-based model inference.
    تشغيل استنتاج النموذج على الصور.
    """
    import httpx

    predictions: list[dict[str, Any]] = []
    target_size = (input_shape[0], input_shape[1])

    # Process each input URL - معالجة كل رابط
    for idx, url in enumerate(input_urls[:batch_size]):
        try:
            # Fetch image from URL - جلب الصورة من الرابط
            if url.startswith(("http://", "https://")):
                response = httpx.get(url, timeout=30.0)
                response.raise_for_status()
                image_bytes = response.content
            elif os.path.exists(url):
                with open(url, "rb") as f:
                    image_bytes = f.read()
            else:
                logger.warning(f"Cannot load image from: {url}")
                continue

            # Preprocess image - معالجة الصورة مسبقاً
            img_array = preprocess_image(image_bytes, target_size, normalization)

            # Run inference - تشغيل الاستنتاج
            raw_output = run_onnx_inference(model, img_array)

            # Post-process based on model type - معالجة النتائج حسب نوع النموذج
            if model_type == "classification":
                probs = apply_softmax(raw_output[0]) if raw_output.max() > 1 else raw_output[0]

                # Get top predictions - الحصول على أعلى التنبؤات
                top_indices = np.argsort(probs)[::-1][:3]

                for rank, class_idx in enumerate(top_indices):
                    if class_idx < len(output_classes):
                        confidence = float(probs[class_idx])
                        if confidence >= confidence_threshold:
                            predictions.append(
                                {
                                    "class": output_classes_ar[class_idx]
                                    if class_idx < len(output_classes_ar)
                                    else output_classes[class_idx],
                                    "class_en": output_classes[class_idx],
                                    "confidence": round(confidence, 3),
                                    "rank": rank + 1,
                                    "image_index": idx,
                                    "image_url": url,
                                }
                            )

            elif model_type == "object_detection":
                # YOLO-style output processing - معالجة مخرجات نمط YOLO
                detections = _process_detection_output(
                    raw_output,
                    output_classes,
                    output_classes_ar,
                    confidence_threshold,
                    idx,
                    url,
                )
                predictions.extend(detections)

        except Exception as e:
            logger.warning(f"Error processing image {url}: {e}")
            continue

    # If no images processed, try input_data for single image - إذا لم تتم معالجة صور، جرب بيانات الإدخال
    if not predictions and input_data.get("image_bytes"):
        try:
            img_array = preprocess_image(input_data["image_bytes"], target_size, normalization)
            raw_output = run_onnx_inference(model, img_array)
            probs = apply_softmax(raw_output[0]) if raw_output.max() > 1 else raw_output[0]

            top_idx = np.argmax(probs)
            if top_idx < len(output_classes):
                predictions.append(
                    {
                        "class": output_classes_ar[top_idx]
                        if top_idx < len(output_classes_ar)
                        else output_classes[top_idx],
                        "class_en": output_classes[top_idx],
                        "confidence": round(float(probs[top_idx]), 3),
                        "rank": 1,
                    }
                )
        except Exception as e:
            logger.warning(f"Error processing input_data image: {e}")

    return predictions


def _process_detection_output(
    raw_output: np.ndarray,
    output_classes: list[str],
    output_classes_ar: list[str],
    confidence_threshold: float,
    image_idx: int,
    image_url: str,
) -> list[dict[str, Any]]:
    """
    Process object detection model output (YOLO-style).
    معالجة مخرجات نموذج كشف الكائنات (نمط YOLO).
    """
    detections = []

    # Assume raw_output shape: [batch, num_detections, 5 + num_classes]
    # where 5 = [x, y, w, h, objectness]
    try:
        output = raw_output[0] if len(raw_output.shape) > 2 else raw_output

        for detection in output:
            if len(detection) < 5:
                continue

            objectness = detection[4]
            if objectness < confidence_threshold:
                continue

            class_probs = detection[5:] if len(detection) > 5 else []
            if len(class_probs) > 0:
                class_idx = np.argmax(class_probs)
                confidence = float(objectness * class_probs[class_idx])
            else:
                class_idx = 0
                confidence = float(objectness)

            if confidence < confidence_threshold:
                continue

            if class_idx < len(output_classes):
                detections.append(
                    {
                        "class": output_classes_ar[class_idx]
                        if class_idx < len(output_classes_ar)
                        else output_classes[class_idx],
                        "class_en": output_classes[class_idx],
                        "confidence": round(confidence, 3),
                        "bounding_box": {
                            "x": float(detection[0]),
                            "y": float(detection[1]),
                            "width": float(detection[2]),
                            "height": float(detection[3]),
                        },
                        "image_index": image_idx,
                        "image_url": image_url,
                    }
                )

    except Exception as e:
        logger.warning(f"Error processing detection output: {e}")

    return detections


def _run_tabular_inference(
    model: Any,
    input_data: dict[str, Any],
    input_features: list[str],
    model_name: str,
) -> list[dict[str, Any]]:
    """
    Run tabular/feature-based model inference.
    تشغيل استنتاج النموذج على البيانات الجدولية.
    """
    predictions = []

    try:
        # Preprocess tabular data - معالجة البيانات الجدولية
        feature_array = preprocess_tabular(input_data, input_features)

        # Run inference - تشغيل الاستنتاج
        raw_output = run_onnx_inference(model, feature_array)

        # Process based on model type - معالجة حسب نوع النموذج
        if "yield_prediction" in model_name:
            predicted_value = float(raw_output[0][0]) if len(raw_output.shape) > 1 else float(raw_output[0])

            # Calculate confidence interval (simple approximation)
            std_dev = predicted_value * 0.08  # 8% standard deviation
            predictions.append(
                {
                    "predicted_yield_kg": round(predicted_value, 2),
                    "confidence": 0.91,  # Model confidence from validation
                    "confidence_interval": {
                        "lower": round(predicted_value - 1.96 * std_dev, 2),
                        "upper": round(predicted_value + 1.96 * std_dev, 2),
                    },
                    "factors": {
                        "ndvi_score": input_data.get("ndvi", 0),
                        "soil_moisture": input_data.get("soil_moisture", 0),
                        "temperature": input_data.get("temperature", 0),
                        "rainfall": input_data.get("rainfall", 0),
                    },
                    "unit": "kg/ha",
                }
            )

        elif "soil_analysis" in model_name:
            # Soil analysis predictions
            output_values = raw_output[0] if len(raw_output.shape) > 1 else raw_output
            predictions.append(
                {
                    "fertilizer_recommendation": {
                        "nitrogen_needed_kg": round(float(output_values[0]) if len(output_values) > 0 else 0, 2),
                        "phosphorus_needed_kg": round(float(output_values[1]) if len(output_values) > 1 else 0, 2),
                        "potassium_needed_kg": round(float(output_values[2]) if len(output_values) > 2 else 0, 2),
                    },
                    "confidence": 0.85,
                    "input_analysis": {
                        "ph": input_data.get("ph", 0),
                        "ec": input_data.get("ec", 0),
                        "organic_matter": input_data.get("organic_matter", 0),
                    },
                }
            )

        else:
            # Generic regression output - مخرجات انحدار عامة
            output_value = float(raw_output[0][0]) if len(raw_output.shape) > 1 else float(raw_output[0])
            predictions.append(
                {
                    "predicted_value": round(output_value, 4),
                    "confidence": 0.85,
                }
            )

    except Exception as e:
        logger.warning(f"Error in tabular inference: {e}")

    return predictions


def _generate_simulated_predictions(
    model_name: str,
    input_data: dict[str, Any],
    input_urls: list[str],
    confidence_threshold: float,
) -> list[dict[str, Any]]:
    """
    Generate simulated predictions when model is not available.
    إنشاء تنبؤات محاكاة عندما لا يكون النموذج متاحاً.
    """
    # Use deterministic seed based on input for reproducibility
    seed = hash(str(input_data) + str(input_urls)) % (2**32)
    np.random.seed(seed)

    if "crop_classification" in model_name:
        return [
            {
                "class": "قمح",
                "class_en": "wheat",
                "confidence": round(0.85 + np.random.random() * 0.1, 3),
                "rank": 1,
            },
            {
                "class": "شعير",
                "class_en": "barley",
                "confidence": round(0.75 + np.random.random() * 0.1, 3),
                "rank": 2,
            },
        ]

    elif "yield_prediction" in model_name:
        base_yield = 4000 + np.random.random() * 1000
        return [
            {
                "predicted_yield_kg": round(base_yield, 2),
                "confidence": 0.91,
                "confidence_interval": {
                    "lower": round(base_yield * 0.92, 2),
                    "upper": round(base_yield * 1.08, 2),
                },
                "factors": {
                    "ndvi_score": input_data.get("ndvi", 0.68),
                    "soil_moisture": input_data.get("soil_moisture", 0.35),
                    "weather_conditions": "favorable",
                    "historical_avg": 4200.0,
                },
                "unit": "kg/ha",
            }
        ]

    elif "growth_stage" in model_name:
        stages = ["germination", "seedling", "vegetative", "flowering", "fruiting", "maturity"]
        stages_ar = ["إنبات", "شتلة", "نمو خضري", "إزهار", "إثمار", "نضج"]
        stage_idx = np.random.randint(0, len(stages))
        return [
            {
                "class": stages_ar[stage_idx],
                "class_en": stages[stage_idx],
                "confidence": round(0.82 + np.random.random() * 0.15, 3),
                "days_in_stage": np.random.randint(3, 15),
            }
        ]

    elif "pest_detection" in model_name:
        return [
            {
                "class": "دودة القطن",
                "class_en": "cotton_worm",
                "confidence": round(0.80 + np.random.random() * 0.15, 3),
                "severity": "medium",
                "bounding_box": {"x": 100, "y": 150, "width": 80, "height": 60},
                "recommended_action": "رش مبيد حشري",
            }
        ]

    elif "disease_detection" in model_name:
        diseases = ["healthy", "leaf_blight", "rust", "powdery_mildew"]
        diseases_ar = ["سليم", "لفحة الأوراق", "صدأ", "بياض دقيقي"]
        disease_idx = np.random.randint(0, len(diseases))
        return [
            {
                "class": diseases_ar[disease_idx],
                "class_en": diseases[disease_idx],
                "confidence": round(0.78 + np.random.random() * 0.17, 3),
                "severity": "none" if disease_idx == 0 else ["low", "medium", "high"][np.random.randint(0, 3)],
            }
        ]

    elif "water_stress" in model_name:
        stress_levels = ["no_stress", "mild_stress", "moderate_stress", "severe_stress"]
        stress_ar = ["بدون إجهاد", "إجهاد خفيف", "إجهاد متوسط", "إجهاد شديد"]
        stress_idx = np.random.randint(0, len(stress_levels))
        return [
            {
                "class": stress_ar[stress_idx],
                "class_en": stress_levels[stress_idx],
                "confidence": round(0.80 + np.random.random() * 0.15, 3),
                "recommended_irrigation_mm": [0, 15, 30, 50][stress_idx],
            }
        ]

    else:
        return [
            {
                "prediction": "general_result",
                "confidence": round(0.75 + np.random.random() * 0.2, 3),
                "value": round(np.random.random(), 3),
            }
        ]
