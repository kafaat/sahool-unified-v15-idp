# WASPAS Multi-Criteria Decision Making - Agro-Advisor v15.4

## Overview

WASPAS (Weighted Aggregated Sum Product Assessment) framework for multi-objective optimization in agricultural recommendations.

**Research Basis**: Zavadskas et al. (2012) - "Optimization of Weighted Aggregated Sum Product Assessment"

## What is WASPAS?

WASPAS combines two decision-making approaches:

1. **WSM (Weighted Sum Model)**: Additive aggregation of criteria
2. **WPM (Weighted Product Model)**: Multiplicative aggregation of criteria

**Formula**: Q = λ × WSM + (1-λ) × WPM

Where λ (lambda) balances between the two approaches (default: 0.5)

## Use Cases

### 1. Fertilizer Recommendation

Balance multiple objectives:
- **Yield increase** (maximize)
- **Cost** (minimize)
- **Environmental sustainability** (maximize)

### 2. Irrigation Method Selection

Optimize for:
- **Water efficiency** (maximize)
- **Installation cost** (minimize)
- **Water savings** (maximize)
- **Maintenance effort** (minimize)

### 3. Crop Variety Selection

Consider:
- **Expected yield** (maximize)
- **Disease resistance** (maximize)
- **Seed cost** (minimize)
- **Drought tolerance** (maximize)

### 4. Pesticide Selection

Evaluate:
- **Effectiveness** (maximize)
- **Cost** (minimize)
- **Environmental safety** (maximize)
- **Residual period** (minimize)

## API Usage

### Python API

```python
from ml.waspas import WASPASRecommender, Criterion, Alternative

# Define decision criteria
criteria = [
    Criterion(
        name="yield",
        name_ar="الإنتاجية",
        weight=0.4,          # 40% importance
        is_benefit=True,     # Higher is better
        unit="t/ha",
        unit_ar="طن/هكتار"
    ),
    Criterion(
        name="cost",
        name_ar="التكلفة",
        weight=0.3,          # 30% importance
        is_benefit=False,    # Lower is better
        unit="SAR/ha",
        unit_ar="ريال/هكتار"
    ),
    Criterion(
        name="sustainability",
        name_ar="الاستدامة",
        weight=0.3,          # 30% importance
        is_benefit=True,     # Higher is better
        unit="score",
        unit_ar="درجة"
    ),
]

# Define alternatives
alternatives = [
    Alternative(
        id="urea",
        name="Urea 46%",
        name_ar="يوريا 46%",
        description="Synthetic nitrogen fertilizer, fast-acting",
        description_ar="سماد نيتروجيني صناعي سريع المفعول",
        criteria_values={
            "yield": 4.5,           # t/ha
            "cost": 500,            # SAR/ha
            "sustainability": 0.6   # 0-1 scale
        }
    ),
    Alternative(
        id="organic",
        name="Organic Compost",
        name_ar="سماد عضوي",
        description="Natural organic matter, slow-release",
        description_ar="مواد عضوية طبيعية بطيئة الإطلاق",
        criteria_values={
            "yield": 4.2,
            "cost": 800,
            "sustainability": 0.95
        }
    ),
    Alternative(
        id="npk",
        name="NPK 20-20-20",
        name_ar="NPK 20-20-20",
        description="Balanced compound fertilizer",
        description_ar="سماد مركب متوازن",
        criteria_values={
            "yield": 4.8,
            "cost": 700,
            "sustainability": 0.7
        }
    ),
]

# Run WASPAS analysis
waspas = WASPASRecommender(criteria, lambda_param=0.5)
result = waspas.evaluate(alternatives)

# Get results
print(f"Best option: {result.best_alternative_id}")
print(f"Ranking: {result.ranked_alternatives}")
print(f"\nExplanation (English):\n{result.explanation}")
print(f"\nExplanation (Arabic):\n{result.explanation_ar}")

# Generate report
from ml.waspas import create_waspas_report
report = create_waspas_report(result, alternatives)
```

### Example Output

```json
{
  "best_alternative": {
    "id": "npk",
    "name": "NPK 20-20-20",
    "name_ar": "NPK 20-20-20",
    "score": 0.867
  },
  "ranking": [
    {
      "rank": 1,
      "id": "npk",
      "name": "NPK 20-20-20",
      "score": 0.867,
      "wsm_score": 0.875,
      "wpm_score": 0.859
    },
    {
      "rank": 2,
      "id": "urea",
      "name": "Urea 46%",
      "score": 0.842,
      "wsm_score": 0.850,
      "wpm_score": 0.834
    },
    {
      "rank": 3,
      "id": "organic",
      "name": "Organic Compost",
      "score": 0.785,
      "wsm_score": 0.780,
      "wpm_score": 0.790
    }
  ],
  "parameters": {
    "lambda": 0.5,
    "n_alternatives": 3
  },
  "explanation": {
    "english": "WASPAS Multi-Criteria Analysis Results:\n\nTop 3 Alternatives:\n1. NPK 20-20-20 - Score: 0.867\n   Balanced compound fertilizer\n\n2. Urea 46% - Score: 0.842\n   Synthetic nitrogen fertilizer, fast-acting\n\n3. Organic Compost - Score: 0.785\n   Natural organic matter, slow-release\n\nCriteria Used:\n- yield: 40% weight\n- cost: 30% weight\n- sustainability: 30% weight",
    "arabic": "نتائج التحليل متعدد المعايير (WASPAS):\n\nأفضل 3 بدائل:\n1. NPK 20-20-20 - النتيجة: 0.867\n   سماد مركب متوازن\n\n2. يوريا 46% - النتيجة: 0.842\n   سماد نيتروجيني صناعي سريع المفعول\n\n3. سماد عضوي - النتيجة: 0.785\n   مواد عضوية طبيعية بطيئة الإطلاق\n\nالمعايير المستخدمة:\n- الإنتاجية: وزن 40%\n- التكلفة: وزن 30%\n- الاستدامة: وزن 30%"
  }
}
```

## Real-World Examples

### Example 1: Irrigation System Selection

```python
criteria = [
    Criterion("efficiency", "الكفاءة", 0.35, True, "%", "%"),
    Criterion("cost", "التكلفة", 0.35, False, "SAR", "ريال"),
    Criterion("water_saving", "توفير الماء", 0.30, True, "%", "%"),
]

alternatives = [
    Alternative(
        "drip",
        "Drip Irrigation",
        "ري بالتنقيط",
        "High efficiency micro-irrigation",
        "ري دقيق عالي الكفاءة",
        {"efficiency": 95, "cost": 5000, "water_saving": 60}
    ),
    Alternative(
        "sprinkler",
        "Sprinkler System",
        "ري بالرش",
        "Overhead sprinkler irrigation",
        "ري علوي بالرش",
        {"efficiency": 75, "cost": 3000, "water_saving": 30}
    ),
    Alternative(
        "flood",
        "Flood Irrigation",
        "ري بالغمر",
        "Traditional surface irrigation",
        "ري سطحي تقليدي",
        {"efficiency": 50, "cost": 500, "water_saving": 0}
    ),
]

waspas = WASPASRecommender(criteria)
result = waspas.evaluate(alternatives)

# Result: Drip irrigation ranks first
# - Highest efficiency (95%)
# - Best water savings (60%)
# - Worth the higher cost
```

### Example 2: Wheat Variety Selection

```python
criteria = [
    Criterion("yield", "الإنتاجية", 0.35, True, "t/ha", "طن/هكتار"),
    Criterion("disease_resistance", "مقاومة الأمراض", 0.25, True, "score", "درجة"),
    Criterion("seed_cost", "تكلفة البذور", 0.20, False, "SAR/ha", "ريال/هكتار"),
    Criterion("drought_tolerance", "تحمل الجفاف", 0.20, True, "score", "درجة"),
]

alternatives = [
    Alternative("sakha95", "Sakha 95", "سخا 95", ...,
                {"yield": 4.5, "disease_resistance": 0.75, "seed_cost": 400, "drought_tolerance": 0.60}),
    Alternative("misr1", "Misr 1", "مصر 1", ...,
                {"yield": 4.2, "disease_resistance": 0.90, "seed_cost": 350, "drought_tolerance": 0.70}),
    Alternative("local", "Local Landrace", "صنف محلي", ...,
                {"yield": 3.5, "disease_resistance": 0.65, "seed_cost": 200, "drought_tolerance": 0.95}),
]

waspas = WASPASRecommender(criteria)
result = waspas.evaluate(alternatives)

# Result balances all factors:
# - Sakha 95: Highest yield
# - Misr 1: Best disease resistance
# - Local: Most drought-tolerant and cheapest
```

## Customizing Lambda Parameter

The λ (lambda) parameter controls the balance between WSM and WPM:

- **λ = 1.0**: Pure WSM (additive, compensatory)
- **λ = 0.0**: Pure WPM (multiplicative, non-compensatory)
- **λ = 0.5**: Balanced (default, recommended)

```python
# Conservative (prefer balanced solutions)
waspas_conservative = WASPASRecommender(criteria, lambda_param=0.7)

# Aggressive (tolerate weakness in one criterion if strong in others)
waspas_aggressive = WASPASRecommender(criteria, lambda_param=0.3)
```

## Integration with Advisory Service

```python
# In agro-advisor/src/engine/recommender.py

from ml.waspas import WASPASRecommender, Criterion, Alternative

class FertilizerRecommender:
    def recommend(self, field_data, farmer_preferences):
        # Define criteria based on farmer preferences
        criteria = [
            Criterion("yield", "الإنتاجية", 
                     farmer_preferences.get("yield_weight", 0.4), True, "t/ha", "طن/هكتار"),
            Criterion("cost", "التكلفة", 
                     farmer_preferences.get("cost_weight", 0.3), False, "SAR", "ريال"),
            Criterion("sustainability", "الاستدامة", 
                     farmer_preferences.get("sustainability_weight", 0.3), True, "score", "درجة"),
        ]
        
        # Get available fertilizer options
        alternatives = self._get_fertilizer_options(field_data)
        
        # Run WASPAS
        waspas = WASPASRecommender(criteria)
        result = waspas.evaluate(alternatives)
        
        return {
            "recommended_fertilizer": result.best_alternative_id,
            "alternatives": result.ranked_alternatives,
            "explanation": result.explanation,
            "explanation_ar": result.explanation_ar,
        }
```

## Testing

```bash
# Run WASPAS tests
pytest tests/test_waspas.py -v

# Run specific test
pytest tests/test_waspas.py::TestWASPASRecommender::test_waspas_fertilizer_recommendation -v

# Run with coverage
pytest tests/test_waspas.py --cov=ml.waspas --cov-report=html
```

## Performance

- **Time complexity**: O(m × n) where m = alternatives, n = criteria
- **Typical execution**: < 1ms for 10 alternatives × 5 criteria
- **Memory**: Minimal, suitable for embedded systems

## Research Citation

```bibtex
@article{zavadskas2012waspas,
  title={Optimization of weighted aggregated sum product assessment},
  author={Zavadskas, Edmundas Kazimieras and Turskis, Zenonas and Antucheviciene, Jurgita and Zakarevicius, Algimantas},
  journal={Elektronika ir Elektrotechnika},
  volume={122},
  number={6},
  pages={3--6},
  year={2012}
}
```

## Future Enhancements

- [ ] Fuzzy WASPAS for uncertain criteria
- [ ] Group decision making (multiple farmers)
- [ ] Sensitivity analysis
- [ ] Integration with real-time market prices
- [ ] Machine learning weights optimization

---

**Version**: 15.4.0  
**Last Updated**: January 2026  
**Author**: SAHOOL Platform Team
