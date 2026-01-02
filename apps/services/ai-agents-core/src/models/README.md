# SAHOOL Disease Detection CNN Model
# نموذج CNN لاكتشاف أمراض المحاصيل في SAHOOL

## Overview / نظرة عامة

This module provides a comprehensive wrapper for disease detection in Yemen crops using Convolutional Neural Networks (CNN).

توفر هذه الوحدة غلاف شامل لاكتشاف الأمراض في المحاصيل اليمنية باستخدام الشبكات العصبية التلافيفية.

## Supported Diseases / الأمراض المدعومة

1. **Tomato Leaf Blight** (لفحة أوراق الطماطم)
2. **Wheat Rust** (صدأ القمح)
3. **Grape Downy Mildew** (البياض الزغبي للعنب)
4. **Date Palm Bayoud** (مرض البيوض في النخيل)
5. **Coffee Leaf Rust** (صدأ أوراق البن)
6. **Banana Fusarium** (فطر الفيوزاريوم في الموز)
7. **Mango Anthracnose** (أنثراكنوز المانجو)
8. **Healthy** (سليم)

## Installation / التثبيت

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start / البدء السريع

### Basic Usage / الاستخدام الأساسي

```python
from models import DiseaseCNNModel

# Initialize model - تهيئة النموذج
model = DiseaseCNNModel(framework="tensorflow", enable_gpu=True)

# Load model - تحميل النموذج
model.load_model("/path/to/model.h5")

# Warm up model for better performance - تسخين النموذج للأداء الأفضل
model.warm_up_model()

# Predict disease from image - التنبؤ بالمرض من الصورة
disease, confidence, bbox = model.predict("/path/to/image.jpg")
print(f"Disease: {disease}, Confidence: {confidence:.2%}")
```

### Get Top-K Predictions / الحصول على أعلى K تنبؤات

```python
# Get top 3 predictions - الحصول على أعلى 3 تنبؤات
predictions = model.get_top_k_predictions("/path/to/image.jpg", k=3)

for pred in predictions:
    print(f"{pred['disease']} ({pred['disease_ar']}): {pred['confidence']:.2%}")
    print(f"Treatment: {pred['treatment_ar']}")
```

### Batch Processing / المعالجة الدفعية

```python
# Process multiple images - معالجة صور متعددة
images = ["image1.jpg", "image2.jpg", "image3.jpg"]
results = model.predict_batch(images, batch_size=8)

for img, (disease, confidence, bbox) in zip(images, results):
    print(f"{img}: {disease} ({confidence:.2%})")
```

### Field Analysis / تحليل الحقل

```python
import asyncio

async def analyze_field():
    # Process all images from a field - معالجة جميع الصور من حقل
    field_images = ["field_1.jpg", "field_2.jpg", "field_3.jpg"]

    report = await model.process_field_images(
        field_id="FIELD-001",
        images=field_images,
        min_confidence=0.5
    )

    print(f"Field Status: {report['field_status_ar']}")
    print(f"Health Percentage: {report['health_percentage']:.1f}%")
    print(f"Diseased Images: {report['total_diseased']}/{report['total_images']}")

    # Print recommendations - طباعة التوصيات
    for rec in report['recommendations']:
        print(f"\nDisease: {rec['disease_ar']}")
        print(f"Treatment: {rec['treatment_ar']}")

# Run analysis - تشغيل التحليل
asyncio.run(analyze_field())
```

### Visualization / التصور

```python
# Visualize predictions on image - تصور التنبؤات على الصورة
image = "/path/to/image.jpg"
predictions = model.get_top_k_predictions(image, k=3)

visualized = model.visualize_predictions(
    image,
    predictions,
    output_path="/path/to/output.jpg"
)
```

### Model Management / إدارة النماذج

```python
import asyncio

async def download_and_load_model():
    # Download latest model - تحميل أحدث نموذج
    model_path = await model.download_model(version="latest")

    # Load the downloaded model - تحميل النموذج المحمل
    model.load_model(model_path)

    # Get model info - الحصول على معلومات النموذج
    print(f"Model Version: {model.get_model_version()}")

    # Get performance metrics - الحصول على مقاييس الأداء
    metrics = model.get_metrics()
    print(f"Total Predictions: {metrics['total_predictions']}")
    print(f"Avg Inference Time: {metrics['avg_inference_time_ms']:.2f}ms")

asyncio.run(download_and_load_model())
```

## Integration with FastAPI / التكامل مع FastAPI

```python
from fastapi import FastAPI, UploadFile, File
from models import DiseaseCNNModel
from PIL import Image
import io

app = FastAPI()

# Initialize model globally - تهيئة النموذج عالمياً
disease_model = DiseaseCNNModel()
disease_model.load_model("/path/to/model.h5")
disease_model.warm_up_model()

@app.post("/api/v1/detect-disease")
async def detect_disease(file: UploadFile = File(...)):
    """
    Detect disease from uploaded image
    كشف المرض من الصورة المرفوعة
    """
    # Read image - قراءة الصورة
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))

    # Get predictions - الحصول على التنبؤات
    predictions = disease_model.get_top_k_predictions(image, k=3)

    return {
        "success": True,
        "predictions": predictions,
        "model_version": disease_model.get_model_version()
    }

@app.post("/api/v1/analyze-field")
async def analyze_field(field_id: str, files: List[UploadFile] = File(...)):
    """
    Analyze entire field from multiple images
    تحليل الحقل بالكامل من صور متعددة
    """
    # Load all images - تحميل جميع الصور
    images = []
    for file in files:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        images.append(image)

    # Process field - معالجة الحقل
    report = await disease_model.process_field_images(
        field_id=field_id,
        images=images,
        min_confidence=0.6
    )

    return {
        "success": True,
        "report": report
    }
```

## Configuration / الإعدادات

### Environment Variables / متغيرات البيئة

```bash
# Model storage directory - مجلد تخزين النماذج
DISEASE_MODEL_DIR=/app/models/disease_detection

# Enable GPU acceleration - تفعيل تسريع GPU
ENABLE_GPU=true

# Default batch size - حجم الدفعة الافتراضي
BATCH_SIZE=8

# Model download URL - رابط تحميل النموذج
MODEL_DOWNLOAD_URL=https://models.sahool.com/disease-detection/
```

### Custom Configuration / التكوين المخصص

```python
from models import DiseaseCNNModel, DiseaseConfig

# Customize configuration - تخصيص التكوين
config = DiseaseConfig()
config.DEFAULT_INPUT_SIZE = 256
config.TTA_ENABLED = False  # Disable test-time augmentation

# Initialize with custom config - تهيئة بالتكوين المخصص
model = DiseaseCNNModel()
model.config = config
```

## Performance / الأداء

- **Inference Time**: ~50-100ms per image on GPU (وقت الاستدلال: ~50-100 مللي ثانية لكل صورة على GPU)
- **Batch Processing**: 8-16 images per batch for optimal performance (المعالجة الدفعية: 8-16 صورة لكل دفعة للأداء الأمثل)
- **Memory Usage**: ~2GB GPU memory for TensorFlow model (استخدام الذاكرة: ~2 جيجابايت ذاكرة GPU لنموذج TensorFlow)

## Model Training / تدريب النموذج

For model training and fine-tuning, refer to the separate training repository:
لتدريب النموذج والضبط الدقيق، راجع مستودع التدريب المنفصل:

```
https://github.com/sahool/disease-model-training
```

## Troubleshooting / استكشاف الأخطاء

### Common Issues / المشاكل الشائعة

1. **Out of Memory Error** (خطأ نفاد الذاكرة)
   - Reduce batch size - قلل حجم الدفعة
   - Disable GPU or use CPU - عطل GPU أو استخدم CPU

2. **Model Not Found** (النموذج غير موجود)
   - Check model path - تحقق من مسار النموذج
   - Download model using `download_model()` - حمل النموذج باستخدام `download_model()`

3. **Slow Inference** (استدلال بطيء)
   - Warm up model - سخن النموذج
   - Enable GPU - فعل GPU
   - Use batch processing - استخدم المعالجة الدفعية

## License / الترخيص

Copyright © 2024 SAHOOL. All rights reserved.

## Support / الدعم

For questions and support:
للأسئلة والدعم:
- Email: support@sahool.com
- Documentation: https://docs.sahool.com
