# shared/ml - Agricultural Machine Learning Module

وحدة التعلم الآلي الزراعي

Provides standardized access to agricultural ML datasets and pre-trained models using the AgML framework. Covers crop disease detection, yield prediction, weed detection, and plant phenotyping across 10 crop types with bilingual (Arabic/English) class definitions.

## File Structure

```
shared/ml/
├── __init__.py           # Package exports
└── agml_integration.py   # AgMLDatasetManager, dataset catalog, disease classes
```

## Key Components

### Enums

| Enum | Values |
|------|--------|
| `DatasetType` | crop_disease, plant_phenotyping, yield_prediction, weed_detection, fruit_detection, semantic_segmentation |
| `CropType` | wheat, barley, corn, rice, tomato, potato, date_palm, apple, grape, citrus, general |

### Data Models

| Model | Description |
|-------|-------------|
| `CropDataset` | Dataset metadata: name (bilingual), type, crop, image count, class count, license, source URL |
| `DiseaseDataset` | Disease-specific: class names in EN/AR, image count, accuracy benchmark |
| `YieldDataset` | Yield prediction: feature list, target variable, sample count, RMSE benchmark |
| `ModelInfo` | Pre-trained model: architecture, accuracy, input size, download URL |

### AgMLDatasetManager

Main class providing the dataset catalog and AgML library integration.

**Methods:**
- `initialize()` - Load AgML library (optional; falls back to catalog-only mode if not installed)
- `list_datasets(dataset_type, crop_type)` - Filter catalog by type and/or crop
- `get_dataset_info(name)` - Fetch metadata for a named dataset
- `load_dataset(name, split, download)` - Download and load dataset via AgML
- `get_disease_classes(crop)` - Bilingual disease class list for a crop
- `get_yield_features()` - Standard features used for yield prediction
- `get_pretrained_model(task, crop)` - Lookup pre-trained model info by task
- `get_recommended_datasets(region)` - Region-appropriate dataset list

## Built-in Dataset Catalog

| Key | Name | Crop | Classes | Images | License |
|-----|------|------|---------|--------|---------|
| `plant_village` | PlantVillage | General | 38 | 54,306 | CC0 |
| `wheat_rust` | Wheat Rust Detection | Wheat | 4 | 1,400 | CC-BY-4.0 |
| `rice_disease` | Rice Disease Detection | Rice | 5 | 3,355 | CC-BY-4.0 |
| `tomato_disease` | Tomato Disease Detection | Tomato | 10 | 18,160 | CC0 |
| `corn_disease` | Corn Disease Detection | Corn | 4 | 4,188 | CC0 |
| `grape_disease` | Grape Disease Detection | Grape | 4 | 4,062 | CC0 |
| `potato_disease` | Potato Disease Detection | Potato | 3 | 2,152 | CC0 |
| `apple_disease` | Apple Disease Detection | Apple | 4 | 3,171 | CC0 |
| `deepweeds` | DeepWeeds | General | 9 | 17,509 | CC-BY-4.0 |
| `crop_yield_prediction` | Crop Yield Prediction | General | - | tabular | Public Domain |

## Usage Example

```python
from shared.ml import AgMLDatasetManager, DatasetType
from shared.ml.agml_integration import CropType

manager = AgMLDatasetManager(cache_dir="/data/agml_cache")
await manager.initialize()

# List wheat datasets
wheat_datasets = manager.list_datasets(crop_type=CropType.WHEAT)

# Get bilingual disease classes
classes = manager.get_disease_classes(CropType.WHEAT)
# [{"en": "Healthy", "ar": "صحي"}, {"en": "Leaf Rust", "ar": "صدأ الأوراق"}, ...]

# Get recommended datasets for Middle East deployments
recommended = manager.get_recommended_datasets(region="middle_east")
# ["wheat_rust", "date_palm_disease", "tomato_disease", "deepweeds", "crop_yield_prediction"]

# Load dataset for training (requires agml package)
train_data = await manager.load_dataset("wheat_rust", split="train", download=True)

# Get pre-trained model info
model = await manager.get_pretrained_model(DatasetType.CROP_DISEASE)
# ModelInfo(name="plant_disease_resnet50", architecture="ResNet50", accuracy=0.987, ...)
```

## Environment Variables

```bash
AGML_CACHE_DIR=/tmp/agml   # Dataset cache directory (default: /tmp/agml)
```

## Dependencies

- `agml` (optional): Install with `pip install agml`. The manager works in catalog-only mode without it.
- `structlog`: Logging.

## Notes

- All disease class definitions include Arabic translations for farmer-facing UI.
- The `date_palm` crop class includes Red Palm Weevil (سوسة النخيل الحمراء) and Bayoud Disease (مرض البيوض) relevant to the Middle East region.
- Yield prediction features cover temperature, precipitation, NDVI, soil moisture, NPK, and irrigation amount.
- This module feeds data to `shared/ai/crop_vision.py` and the YOLO26 vision service training pipelines.
