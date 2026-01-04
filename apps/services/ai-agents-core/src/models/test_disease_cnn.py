"""
Test Suite for Disease CNN Model
مجموعة اختبارات لنموذج CNN الأمراض

This module provides unit tests for the DiseaseCNNModel class.
توفر هذه الوحدة اختبارات الوحدة لفئة DiseaseCNNModel.
"""

import os
import tempfile
import unittest

import numpy as np
from disease_cnn import DiseaseCNNModel, DiseaseConfig
from PIL import Image


class TestDiseaseCNNModel(unittest.TestCase):
    """
    Unit tests for DiseaseCNNModel
    اختبارات الوحدة لـ DiseaseCNNModel
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up test fixtures
        إعداد تركيبات الاختبار
        """
        cls.model = DiseaseCNNModel(framework="tensorflow", enable_gpu=False)
        cls.test_image_path = None

    def setUp(self):
        """Create test image - إنشاء صورة اختبار"""
        # Create a dummy RGB image - إنشاء صورة RGB وهمية
        self.test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        self.pil_image = Image.fromarray(self.test_image)

        # Save to temporary file - حفظ في ملف مؤقت
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        self.pil_image.save(self.temp_file.name)
        self.temp_file.close()

    def tearDown(self):
        """Clean up test files - تنظيف ملفات الاختبار"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_initialization(self):
        """
        Test model initialization
        اختبار تهيئة النموذج
        """
        model = DiseaseCNNModel(framework="tensorflow", enable_gpu=False)
        self.assertIsNotNone(model)
        self.assertEqual(model.framework, "tensorflow")
        self.assertEqual(model.device, "cpu")

    def test_config(self):
        """
        Test disease configuration
        اختبار إعدادات الأمراض
        """
        config = DiseaseConfig()

        # Test supported diseases - اختبار الأمراض المدعومة
        self.assertIn("tomato_leaf_blight", config.SUPPORTED_DISEASES)
        self.assertIn("wheat_rust", config.SUPPORTED_DISEASES)
        self.assertIn("date_palm_bayoud", config.SUPPORTED_DISEASES)

        # Test disease properties - اختبار خصائص الأمراض
        wheat_rust = config.SUPPORTED_DISEASES["wheat_rust"]
        self.assertEqual(wheat_rust["severity"], "critical")
        self.assertIn("name_ar", wheat_rust)
        self.assertIn("treatment", wheat_rust)

    def test_preprocess_image_from_path(self):
        """
        Test image preprocessing from file path
        اختبار المعالجة المسبقة للصورة من مسار الملف
        """
        processed = self.model.preprocess_image(self.temp_file.name)

        # Check shape - التحقق من الشكل
        self.assertEqual(processed.shape, (224, 224, 3))

        # Check normalization - التحقق من التطبيع
        self.assertTrue(np.all(processed >= -5))  # Reasonable range after normalization
        self.assertTrue(np.all(processed <= 5))

    def test_preprocess_image_from_array(self):
        """
        Test image preprocessing from numpy array
        اختبار المعالجة المسبقة للصورة من مصفوفة numpy
        """
        processed = self.model.preprocess_image(self.test_image)

        # Check shape - التحقق من الشكل
        self.assertEqual(processed.shape, (224, 224, 3))

    def test_preprocess_image_from_pil(self):
        """
        Test image preprocessing from PIL Image
        اختبار المعالجة المسبقة للصورة من PIL
        """
        processed = self.model.preprocess_image(self.pil_image)

        # Check shape - التحقق من الشكل
        self.assertEqual(processed.shape, (224, 224, 3))

    def test_resize_to_input_size(self):
        """
        Test image resizing
        اختبار تغيير حجم الصورة
        """
        # Test with different sizes - اختبار بأحجام مختلفة
        for size in [128, 224, 256]:
            resized = self.model.resize_to_input_size(self.pil_image, size)
            self.assertEqual(resized.size, (size, size))

    def test_normalize_pixels(self):
        """
        Test pixel normalization
        اختبار تطبيع البكسل
        """
        # Create test image - إنشاء صورة اختبار
        test_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)

        # Normalize - تطبيع
        normalized = self.model.normalize_pixels(test_img)

        # Check shape preserved - التحقق من الحفاظ على الشكل
        self.assertEqual(normalized.shape, test_img.shape)

        # Check dtype - التحقق من نوع البيانات
        self.assertEqual(normalized.dtype, np.float32)

    def test_augment_for_inference(self):
        """
        Test Test-Time Augmentation
        اختبار التعزيز في وقت الاختبار
        """
        # Prepare normalized image - تحضير الصورة المطبعة
        normalized = self.test_image.astype(np.float32) / 255.0

        # Get augmentations - الحصول على التعزيزات
        augmented = self.model.augment_for_inference(normalized, n_augmentations=5)

        # Check count - التحقق من العدد
        self.assertEqual(len(augmented), 5)

        # Check shapes - التحقق من الأشكال
        for aug_img in augmented:
            self.assertEqual(aug_img.shape, normalized.shape)

    def test_metrics_initialization(self):
        """
        Test metrics are properly initialized
        اختبار تهيئة المقاييس بشكل صحيح
        """
        metrics = self.model.get_metrics()

        self.assertIn("total_predictions", metrics)
        self.assertIn("avg_inference_time_ms", metrics)
        self.assertIn("framework", metrics)
        self.assertIn("device", metrics)
        self.assertEqual(metrics["total_predictions"], 0)

    def test_model_version(self):
        """
        Test model version retrieval
        اختبار استرجاع إصدار النموذج
        """
        version = self.model.get_model_version()
        self.assertIsNotNone(version)
        self.assertIsInstance(version, str)

    def test_disease_config_completeness(self):
        """
        Test that all diseases have required fields
        اختبار أن جميع الأمراض لها الحقول المطلوبة
        """
        config = DiseaseConfig()

        required_fields = ["name_ar", "severity", "treatment", "treatment_ar"]

        for disease_name, disease_info in config.SUPPORTED_DISEASES.items():
            for field in required_fields:
                self.assertIn(
                    field,
                    disease_info,
                    f"Disease '{disease_name}' missing field '{field}'"
                )

    def test_batch_preprocessing(self):
        """
        Test batch image preprocessing
        اختبار المعالجة المسبقة للدفعة
        """
        # Create multiple test images - إنشاء صور اختبار متعددة
        images = [
            np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            for _ in range(5)
        ]

        # Preprocess all - معالجة الكل مسبقاً
        processed_images = [self.model.preprocess_image(img) for img in images]

        # Check all processed - التحقق من معالجة الكل
        self.assertEqual(len(processed_images), 5)
        for proc_img in processed_images:
            self.assertEqual(proc_img.shape, (224, 224, 3))

    def test_supported_diseases_count(self):
        """
        Test correct number of supported diseases
        اختبار العدد الصحيح للأمراض المدعومة
        """
        config = DiseaseConfig()

        # Should have exactly 8 disease categories (7 diseases + healthy)
        # يجب أن يكون هناك بالضبط 8 فئات من الأمراض (7 أمراض + سليم)
        self.assertEqual(len(config.SUPPORTED_DISEASES), 8)

        # Verify specific diseases - التحقق من أمراض محددة
        expected_diseases = [
            "tomato_leaf_blight",
            "wheat_rust",
            "grape_downy_mildew",
            "date_palm_bayoud",
            "coffee_leaf_rust",
            "banana_fusarium",
            "mango_anthracnose",
            "healthy"
        ]

        for disease in expected_diseases:
            self.assertIn(disease, config.SUPPORTED_DISEASES)

    def test_severity_levels(self):
        """
        Test disease severity levels are valid
        اختبار صحة مستويات خطورة الأمراض
        """
        config = DiseaseConfig()
        valid_severities = ["none", "low", "medium", "high", "critical"]

        for disease_name, disease_info in config.SUPPORTED_DISEASES.items():
            severity = disease_info["severity"]
            self.assertIn(
                severity,
                valid_severities,
                f"Invalid severity '{severity}' for disease '{disease_name}'"
            )


class TestDiseaseRecommendations(unittest.TestCase):
    """
    Test disease recommendations generation
    اختبار إنشاء توصيات الأمراض
    """

    def setUp(self):
        """Set up test model - إعداد نموذج الاختبار"""
        self.model = DiseaseCNNModel(framework="tensorflow", enable_gpu=False)

    def test_generate_recommendations(self):
        """
        Test recommendation generation
        اختبار إنشاء التوصيات
        """
        disease_counts = {
            "wheat_rust": 5,
            "tomato_leaf_blight": 3,
            "healthy": 10
        }

        recommendations = self.model._generate_recommendations(disease_counts)

        # Should have recommendations for diseased plants only
        # يجب أن تكون هناك توصيات للنباتات المريضة فقط
        self.assertEqual(len(recommendations), 2)

        # Check recommendation structure - التحقق من بنية التوصية
        for rec in recommendations:
            self.assertIn("disease", rec)
            self.assertIn("disease_ar", rec)
            self.assertIn("affected_count", rec)
            self.assertIn("severity", rec)
            self.assertIn("treatment", rec)
            self.assertIn("treatment_ar", rec)
            self.assertIn("priority", rec)

        # Wheat rust should be first (higher count) - صدأ القمح يجب أن يكون أولاً
        self.assertEqual(recommendations[0]["disease"], "wheat_rust")
        self.assertEqual(recommendations[0]["affected_count"], 5)


class TestImageFormats(unittest.TestCase):
    """
    Test support for different image formats
    اختبار دعم تنسيقات الصور المختلفة
    """

    def setUp(self):
        """Set up test model - إعداد نموذج الاختبار"""
        self.model = DiseaseCNNModel(framework="tensorflow", enable_gpu=False)

    def test_rgb_image(self):
        """Test RGB image processing - اختبار معالجة صورة RGB"""
        rgb_image = np.random.randint(0, 255, (300, 400, 3), dtype=np.uint8)
        processed = self.model.preprocess_image(rgb_image)
        self.assertEqual(processed.shape, (224, 224, 3))

    def test_different_dimensions(self):
        """Test images with different dimensions - اختبار الصور بأبعاد مختلفة"""
        sizes = [(100, 100), (500, 500), (1024, 768), (640, 480)]

        for h, w in sizes:
            test_img = np.random.randint(0, 255, (h, w, 3), dtype=np.uint8)
            processed = self.model.preprocess_image(test_img)
            self.assertEqual(processed.shape, (224, 224, 3))


def run_tests():
    """
    Run all tests
    تشغيل جميع الاختبارات
    """
    # Create test suite - إنشاء مجموعة الاختبار
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes - إضافة جميع فئات الاختبار
    suite.addTests(loader.loadTestsFromTestCase(TestDiseaseCNNModel))
    suite.addTests(loader.loadTestsFromTestCase(TestDiseaseRecommendations))
    suite.addTests(loader.loadTestsFromTestCase(TestImageFormats))

    # Run tests - تشغيل الاختبارات
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success status - إرجاع حالة النجاح
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run tests when script is executed directly
    # تشغيل الاختبارات عند تنفيذ النص مباشرة
    success = run_tests()
    exit(0 if success else 1)
