"""
Sahool Vision - AI Prediction Service
خدمة التنبؤ بالذكاء الاصطناعي

هذه الخدمة مسؤولة عن:
- تحميل نموذج TensorFlow
- معالجة الصور
- تشغيل الاستدلال
"""

import os
import io
import logging
from typing import Tuple, List, Dict, Any, Optional

import numpy as np

from services.disease_service import disease_service

logger = logging.getLogger("sahool-vision")


class PredictionService:
    """
    خدمة التنبؤ بالذكاء الاصطناعي
    AI Prediction Service
    """

    # PlantVillage dataset class names (38 classes)
    PLANTVILLAGE_CLASSES = [
        "Apple___Apple_scab",
        "Apple___Black_rot",
        "Apple___Cedar_apple_rust",
        "Apple___healthy",
        "Blueberry___healthy",
        "Cherry___Powdery_mildew",
        "Cherry___healthy",
        "Corn___Cercospora_leaf_spot",
        "Corn___Common_rust",
        "Corn___Northern_Leaf_Blight",
        "Corn___healthy",
        "Grape___Black_rot",
        "Grape___Esca",
        "Grape___Leaf_blight",
        "Grape___healthy",
        "Orange___Citrus_greening",
        "Peach___Bacterial_spot",
        "Peach___healthy",
        "Pepper___Bacterial_spot",
        "Pepper___healthy",
        "Potato___Early_blight",
        "Potato___Late_blight",
        "Potato___healthy",
        "Raspberry___healthy",
        "Soybean___healthy",
        "Squash___Powdery_mildew",
        "Strawberry___Leaf_scorch",
        "Strawberry___healthy",
        "Tomato___Bacterial_spot",
        "Tomato___Early_blight",
        "Tomato___Late_blight",
        "Tomato___Leaf_Mold",
        "Tomato___Septoria_leaf_spot",
        "Tomato___Spider_mites",
        "Tomato___Target_Spot",
        "Tomato___Yellow_Leaf_Curl_Virus",
        "Tomato___mosaic_virus",
        "Tomato___healthy",
    ]

    # Map PlantVillage classes to Yemen-focused disease database
    CLASS_TO_DISEASE = {
        "Tomato___Late_blight": "tomato_late_blight",
        "Tomato___Early_blight": "tomato_late_blight",
        "Tomato___Bacterial_spot": "tomato_late_blight",
        "Tomato___Leaf_Mold": "tomato_late_blight",
        "Tomato___healthy": "healthy",
        "Potato___Late_blight": "tomato_late_blight",
        "Potato___Early_blight": "tomato_late_blight",
        "Potato___healthy": "healthy",
        "Corn___Common_rust": "wheat_leaf_rust",
        "Corn___healthy": "healthy",
        "Grape___Black_rot": "mango_anthracnose",
        "Grape___healthy": "healthy",
        "Apple___Apple_scab": "wheat_leaf_rust",
        "Apple___healthy": "healthy",
        "Orange___Citrus_greening": "coffee_leaf_rust",
        "Peach___healthy": "healthy",
        "Pepper___healthy": "healthy",
        "Cherry___healthy": "healthy",
    }

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.getenv(
            "MODEL_PATH", "models/plant_disease_model.tflite"
        )
        self.model = None
        self.is_loaded = False
        self.is_real_model = False
        self.model_type: Optional[str] = None
        self.class_names = disease_service.get_disease_names()
        self.input_shape = (224, 224)

    def load_model(self) -> bool:
        """
        تحميل نموذج TensorFlow مع التراجع التلقائي لوضع المحاكاة
        Load TensorFlow model with automatic fallback to mock mode
        """
        if self.model_path and os.path.exists(self.model_path):
            try:
                logger.info(f"⏳ Loading AI model from {self.model_path}...")

                if self.model_path.endswith(".tflite"):
                    import tensorflow as tf

                    self.model = tf.lite.Interpreter(model_path=self.model_path)
                    self.model.allocate_tensors()
                    self.model_type = "tflite"
                    self.is_real_model = True
                    logger.info("✅ TFLite model loaded successfully!")

                elif self.model_path.endswith(".h5") or self.model_path.endswith(
                    ".keras"
                ):
                    import tensorflow as tf

                    self.model = tf.keras.models.load_model(self.model_path)
                    self.model_type = "keras"
                    self.is_real_model = True
                    logger.info("✅ Keras model loaded successfully!")

                elif os.path.isdir(self.model_path):
                    import tensorflow as tf

                    self.model = tf.keras.models.load_model(self.model_path)
                    self.model_type = "savedmodel"
                    self.is_real_model = True
                    logger.info("✅ SavedModel loaded successfully!")

                self.is_loaded = True
                return True

            except ImportError as e:
                logger.warning(f"⚠️ TensorFlow not available: {e}")
                logger.info("📦 Install with: pip install tensorflow-cpu")
            except Exception as e:
                logger.error(f"❌ Failed to load model: {e}")
        else:
            logger.info(f"ℹ️ Model not found at: {self.model_path}")

        # Fallback to mock mode
        logger.info("🧪 Running in MOCK mode (simulated AI predictions)")
        self.is_loaded = True
        self.is_real_model = False
        return True

    def preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        """
        معالجة الصورة للاستدلال
        Preprocess image for model inference
        """
        try:
            from PIL import Image

            image = Image.open(io.BytesIO(image_bytes))
            image = image.resize(self.input_shape, Image.Resampling.LANCZOS)

            if image.mode != "RGB":
                image = image.convert("RGB")

            img_array = np.array(image, dtype=np.float32) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            return img_array

        except ImportError:
            logger.warning("PIL not available, using random tensor")
            return np.random.rand(1, 224, 224, 3).astype(np.float32)
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise ValueError(f"صورة غير صالحة: {str(e)}")

    def _run_real_inference(self, img_array: np.ndarray) -> np.ndarray:
        """تشغيل استدلال حقيقي باستخدام TensorFlow"""
        try:
            import tensorflow as tf

            if self.model_type == "tflite":
                input_details = self.model.get_input_details()
                output_details = self.model.get_output_details()
                self.model.set_tensor(input_details[0]["index"], img_array)
                self.model.invoke()
                predictions = self.model.get_tensor(output_details[0]["index"])[0]
            else:
                predictions = self.model.predict(img_array, verbose=0)[0]

            if np.max(predictions) > 1.0 or np.min(predictions) < 0.0:
                predictions = tf.nn.softmax(predictions).numpy()

            return predictions

        except Exception as e:
            logger.error(f"Real inference failed: {e}, falling back to mock")
            return self._run_mock_inference(None)

    def _run_mock_inference(self, image_bytes: Optional[bytes]) -> np.ndarray:
        """
        تشغيل استدلال محاكاة للتطوير
        Run simulated inference for development
        """
        if image_bytes:
            seed = hash(image_bytes[:100]) % (2**32)
        else:
            seed = np.random.randint(0, 2**32)
        np.random.seed(seed)

        weights = np.ones(len(self.class_names))
        if "healthy" in self.class_names:
            weights[self.class_names.index("healthy")] = 0.3
        if "tomato_late_blight" in self.class_names:
            weights[self.class_names.index("tomato_late_blight")] = 2.5
        if "wheat_leaf_rust" in self.class_names:
            weights[self.class_names.index("wheat_leaf_rust")] = 2.0
        if "mango_anthracnose" in self.class_names:
            weights[self.class_names.index("mango_anthracnose")] = 1.5

        predictions = np.random.dirichlet(weights)
        return predictions

    def _map_plantvillage_to_disease(self, pv_class: str) -> str:
        """تحويل فئة PlantVillage لمفتاح قاعدة البيانات"""
        if pv_class in self.CLASS_TO_DISEASE:
            return self.CLASS_TO_DISEASE[pv_class]
        if "healthy" in pv_class.lower():
            return "healthy"
        return "healthy"

    def predict(self, image_bytes: bytes) -> Tuple[str, float, List[Dict[str, Any]]]:
        """
        تشغيل استدلال الذكاء الاصطناعي على صورة النبات
        Run AI inference on plant image

        Returns:
            tuple: (disease_key, confidence, all_predictions)
        """
        img_array = self.preprocess_image(image_bytes)

        if self.is_real_model and self.model is not None:
            predictions = self._run_real_inference(img_array)
            top_idx = np.argmax(predictions)
            confidence = float(predictions[top_idx])

            if top_idx < len(self.PLANTVILLAGE_CLASSES):
                pv_class = self.PLANTVILLAGE_CLASSES[top_idx]
                disease_key = self._map_plantvillage_to_disease(pv_class)

                sorted_indices = np.argsort(predictions)[::-1][:5]
                all_predictions = []
                for idx in sorted_indices:
                    if idx < len(self.PLANTVILLAGE_CLASSES):
                        pv = self.PLANTVILLAGE_CLASSES[idx]
                        all_predictions.append(
                            {
                                "disease": pv,
                                "mapped_to": self._map_plantvillage_to_disease(pv),
                                "confidence": float(predictions[idx]),
                            }
                        )
            else:
                disease_key = "healthy"
                all_predictions = [{"disease": "unknown", "confidence": confidence}]

            logger.info(f"🤖 Real AI: {pv_class} -> {disease_key} ({confidence:.1%})")

        else:
            predictions = self._run_mock_inference(image_bytes)
            top_idx = np.argmax(predictions)
            confidence = float(predictions[top_idx])
            disease_key = self.class_names[top_idx]

            all_predictions = [
                {"disease": self.class_names[i], "confidence": float(predictions[i])}
                for i in np.argsort(predictions)[::-1][:5]
            ]

            logger.info(f"🧪 Mock AI: {disease_key} ({confidence:.1%})")

        return disease_key, confidence, all_predictions


# Singleton instance
prediction_service = PredictionService()
