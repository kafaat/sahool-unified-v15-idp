# shared/nlp

Arabic-first natural language processing for the SAHOOL platform.
Provides intent classification, named entity recognition, and sentiment analysis
for agricultural queries in Arabic and English using AraBERT.
Fully functional offline via keyword fallback when model weights are unavailable.

## File Structure

```
shared/nlp/
├── __init__.py      # Module exports
└── arabic_nlp.py   # All NLP components: preprocessor, classifier, extractor, analyser
```

## Key Components

### ArabicTextPreprocessor

Prepares raw text before classification. All methods are static.

| Method | Purpose |
|--------|---------|
| `normalize(text)` | Remove diacritics, normalise Alef/Taa Marbuta variants, collapse whitespace |
| `remove_emojis(text)` | Strip Unicode emoji ranges |
| `is_arabic(text)` | Detect presence of Arabic Unicode block (U+0600–U+06FF) |
| `extract_numbers(text)` | Convert Arabic-Indic numerals and return list of floats |

### IntentClassifier

Keyword-based primary classifier with optional AraBERT model upgrade.

Supported intents (`AgriculturalIntent` enum):
`crop_disease`, `irrigation`, `fertilizer`, `pest`, `weather`, `yield`, `planting`, `harvest`, `market_price`, `general`

- Keyword dictionaries cover both Arabic and English terms.
- When `transformers` is installed and `ARABERT_MODEL` is reachable, `load_model()` loads
  `aubmindlab/bert-base-arabertv2` for sequence classification.
- Falls back gracefully to keyword scoring if the model cannot be loaded (offline-first).

### EntityExtractor

Rule-based NER covering four agricultural entity types:

| EntityType | Examples |
|-----------|---------|
| `CROP` | قمح (wheat), نخيل (date_palm), طماطم (tomato) |
| `DISEASE` | صدأ (rust), لفحة (blight), تعفن (rot) |
| `PEST` | سوسة النخيل (red_palm_weevil), من (aphid) |
| `FERTILIZER` | يوريا (urea), نيتروجين (nitrogen), npk |
| `QUANTITY` | Regex-based: numbers followed by كيلو/طن/هكتار/kg/ton/ha |

### SentimentAnalyzer

Counts positive, negative, and urgency keywords. Returns:
- `sentiment`: `"positive"`, `"neutral"`, or `"negative"` with a 0–1 score.
- `is_urgent`: True when terms like عاجل, طوارئ, urgent, emergency are present.

### ArabicNLPProcessor

Orchestrates all four components. Call `initialize()` once at startup to attempt model loading;
subsequent calls to `process()` are synchronous.

`process(text)` returns a single dict with keys: `original_text`, `normalized_text`,
`is_arabic`, `intent` (`{primary, confidence, all_intents}`), `entities` (list of
`{text, type, value, confidence}`), `sentiment` (`{label, score, is_urgent}`),
`numbers` (extracted numeric values), `language` (`"arabic"` or `"mixed"`).

## Usage Example

```python
from shared.nlp import ArabicNLPProcessor, IntentClassifier, EntityExtractor

# Full pipeline
processor = ArabicNLPProcessor()
await processor.initialize()   # loads AraBERT if available

result = processor.process("القمح يعاني من اصفرار الأوراق")

print(result["is_arabic"])          # True
print(result["intent"]["primary"])  # "crop_disease"
print(result["intent"]["confidence"])  # ~0.85

for entity in result["entities"]:
    print(entity["text"], entity["type"])
# قمح  crop
# اصفرار  disease

print(result["sentiment"]["label"])    # "neutral"
print(result["sentiment"]["is_urgent"])  # False

# Quick intent only
classifier = IntentClassifier()
intent = classifier.classify("متى أسقي القمح؟")
print(intent.intent)      # AgriculturalIntent.IRRIGATION
print(intent.confidence)  # ~0.80

# Entity extraction only
extractor = EntityExtractor()
entities = extractor.extract("apply 50 kg urea per hectare")
# [Entity(text='urea', entity_type=<EntityType.FERTILIZER>, ...),
#  Entity(text='50 kg', entity_type=<EntityType.QUANTITY>, ...)]
```

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `ARABERT_MODEL` | `aubmindlab/bert-base-arabertv2` | HuggingFace model identifier |
| `ARABERT_REVISION` | `main` | Model revision pin (prevents supply-chain attacks) |

The module operates fully offline when `transformers` is not installed or credentials
are unavailable; the keyword fallback is always active.
