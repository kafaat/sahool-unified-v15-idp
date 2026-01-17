# Crop Profitability Analysis - Quick Start Guide

# دليل البدء السريع - تحليل ربحية المحاصيل

## Overview | نظرة عامة

This guide helps you get started with the SAHOOL Crop Profitability Analysis feature, inspired by LiteFarm. It allows farmers to analyze which crops are most profitable, compare different crops, and make data-driven decisions.

هذا الدليل يساعدك على البدء مع ميزة تحليل ربحية المحاصيل في SAHOOL، المستوحاة من LiteFarm. يسمح للمزارعين بتحليل أي المحاصيل أكثر ربحية، مقارنة المحاصيل المختلفة، واتخاذ قرارات مبنية على البيانات.

---

## Quick Start | البدء السريع

### 1. Install Dependencies | تثبيت المتطلبات

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/field-core
pip install -r requirements.txt
```

### 2. Run the Service | تشغيل الخدمة

```bash
# Development mode
python src/main.py

# Or with uvicorn directly
uvicorn src.main:app --host 0.0.0.0 --port 8090 --reload
```

The service will start on port **8090**.

### 3. Test the API | اختبار الـ API

```bash
# Health check
curl http://localhost:8090/healthz

# List available crops
curl http://localhost:8090/v1/crops/list

# Get profitability for wheat (2.5 hectares)
curl "http://localhost:8090/v1/profitability/crop/season-2025-1?field_id=field-001&crop_code=wheat&area_ha=2.5"
```

---

## Use Cases | حالات الاستخدام

### 1. Analyze Single Crop | تحليل محصول واحد

**Scenario:** A farmer wants to know if their wheat crop was profitable.

**الحالة:** مزارع يريد معرفة ما إذا كان محصول القمح مربحًا.

```bash
curl -X POST "http://localhost:8090/v1/profitability/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "field-001",
    "crop_season_id": "2025-wheat-001",
    "crop_code": "wheat",
    "area_ha": 2.5,
    "costs": [
      {"category": "seeds", "description": "Premium seeds", "amount": 187500},
      {"category": "fertilizer", "description": "NPK + Urea", "amount": 300000},
      {"category": "pesticides", "description": "Herbicide", "amount": 112500},
      {"category": "irrigation", "description": "Water costs", "amount": 200000},
      {"category": "labor", "description": "Farm workers", "amount": 375000},
      {"category": "machinery", "description": "Tractor rental", "amount": 250000}
    ],
    "revenues": [
      {"description": "Wheat harvest", "quantity": 7500, "unit": "kg", "unit_price": 550}
    ]
  }'
```

**Result:**

- Total costs: 1,425,000 YER
- Total revenue: 4,125,000 YER
- Net profit: 2,700,000 YER
- ROI: 189%
- Recommendations in Arabic and English

### 2. Compare Multiple Crops | مقارنة محاصيل متعددة

**Scenario:** A farmer wants to decide which crop to plant next season.

**الحالة:** مزارع يريد أن يقرر أي محصول يزرع في الموسم القادم.

```bash
curl "http://localhost:8090/v1/profitability/compare?crops=wheat,tomato,potato,coffee&area_ha=2.5&region=sanaa"
```

**Result:** Crops ranked by profitability per hectare.

**النتيجة:** المحاصيل مرتبة حسب الربحية لكل هكتار.

### 3. Season Summary | ملخص الموسم

**Scenario:** A farmer wants to see overall performance for the entire season.

**الحالة:** مزارع يريد رؤية الأداء العام للموسم بأكمله.

```bash
curl -X POST "http://localhost:8090/v1/profitability/season" \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "farmer-001",
    "season_year": "2025",
    "crops": [
      {"field_id": "field-001", "crop_code": "wheat", "area_ha": 2.5},
      {"field_id": "field-002", "crop_code": "tomato", "area_ha": 1.0},
      {"field_id": "field-003", "crop_code": "potato", "area_ha": 1.5},
      {"field_id": "field-004", "crop_code": "onion", "area_ha": 1.0}
    ]
  }'
```

**Result:**

- Total area: 6.0 hectares
- Overall profitability
- Best performing crop
- Worst performing crop
- Recommendations for improvement

### 4. Break-even Analysis | تحليل التعادل

**Scenario:** A farmer wants to know the minimum yield needed to break even.

**الحالة:** مزارع يريد معرفة الحد الأدنى من الإنتاج المطلوب للتعادل.

```bash
curl "http://localhost:8090/v1/profitability/break-even?crop_code=wheat&area_ha=2.5&total_costs=670000&expected_price=550"
```

**Result:**

- Break-even yield: 1,218 kg (487 kg/ha)
- Regional average: 2,800 kg/ha
- Safety margin: 81%

### 5. Regional Benchmarks | المعايير الإقليمية

**Scenario:** A farmer wants to compare their costs with regional averages.

**الحالة:** مزارع يريد مقارنة تكاليفه مع المتوسطات الإقليمية.

```bash
curl "http://localhost:8090/v1/profitability/benchmarks/coffee?region=sanaa"
```

**Result:**

- Regional average costs per category
- Expected yields
- Market prices
- Expected profitability

---

## Supported Crops | المحاصيل المدعومة

### Grains | الحبوب

- **Wheat (قمح)** - Staple grain, 2,800 kg/ha, 550 YER/kg
- **Barley (شعير)** - Feed grain, 2,500 kg/ha, 480 YER/kg
- **Sorghum (ذرة رفيعة)** - Drought-tolerant, 2,200 kg/ha, 400 YER/kg
- **Maize (ذرة شامية)** - Corn, 3,200 kg/ha, 520 YER/kg

### Vegetables | الخضروات

- **Tomato (طماطم)** - High value, 25,000 kg/ha, 280 YER/kg
- **Potato (بطاطس)** - Root crop, 18,000 kg/ha, 350 YER/kg
- **Onion (بصل)** - Storage crop, 22,000 kg/ha, 300 YER/kg
- **Cucumber (خيار)** - Fresh vegetable, 20,000 kg/ha, 250 YER/kg
- **Watermelon (بطيخ)** - Fruit crop, 30,000 kg/ha, 180 YER/kg

### Cash Crops | المحاصيل النقدية

- **Coffee (بن)** - Premium Yemen coffee, 800 kg/ha, 8,500 YER/kg
- **Qat (قات)** - High value, 3,500 kg/ha, 3,500 YER/kg
- **Mango (مانجو)** - Tree crop, 12,000 kg/ha, 800 YER/kg

---

## API Reference | مرجع الـ API

### GET `/v1/crops/list`

List all available crops with regional data.

### POST `/v1/profitability/analyze`

Analyze single crop with custom costs and revenues.

### POST `/v1/profitability/season`

Analyze entire season with multiple crops.

### GET `/v1/profitability/compare`

Compare multiple crops for planning.

### GET `/v1/profitability/break-even`

Calculate break-even yield and price.

### GET `/v1/profitability/benchmarks/{crop_code}`

Get regional benchmarks for a crop.

### GET `/v1/profitability/cost-breakdown/{crop_code}`

Get detailed cost breakdown by category.

### GET `/v1/profitability/history/{field_id}/{crop_code}`

Get historical profitability trends.

---

## Understanding the Metrics | فهم المقاييس

### Gross Profit | إجمالي الربح

Revenue minus direct costs (seeds, fertilizer, labor, etc.)

الإيرادات ناقص التكاليف المباشرة

### Gross Margin % | هامش الربح الإجمالي %

Gross profit as a percentage of revenue. Higher is better.

- < 20%: Low profitability
- 20-40%: Moderate profitability
- > 40%: High profitability

### ROI (Return on Investment) | العائد على الاستثمار

Net profit as a percentage of total costs invested.

- < 30%: Low return
- 30-70%: Good return
- > 70%: Excellent return

### Break-even Yield | إنتاجية التعادل

Minimum yield (kg/ha) needed to cover all costs at expected price.

الحد الأدنى من الإنتاج المطلوب لتغطية جميع التكاليف

### Profit per Hectare | الربح لكل هكتار

Net profit divided by area - useful for comparing crops.

صافي الربح مقسوماً على المساحة

---

## Running with Docker | التشغيل مع Docker

### Build and Run

```bash
# Build
docker build -f Dockerfile.python -t sahool-profitability .

# Run
docker run -p 8090:8090 sahool-profitability
```

### Docker Compose

```bash
# Start all services (field-core + profitability)
docker-compose -f docker-compose.profitability.yml up -d

# View logs
docker-compose -f docker-compose.profitability.yml logs -f field-profitability

# Stop services
docker-compose -f docker-compose.profitability.yml down
```

---

## Testing | الاختبار

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/test_profitability.py tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Manual Testing

```bash
# Start service
python src/main.py

# In another terminal, test endpoints
curl http://localhost:8090/healthz
curl http://localhost:8090/v1/crops/list
```

---

## Integration Examples | أمثلة التكامل

### Python

```python
import httpx

async def analyze_wheat_crop():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8090/v1/profitability/crop/season-001",
            params={
                "field_id": "field-001",
                "crop_code": "wheat",
                "area_ha": 2.5
            }
        )
        data = response.json()
        print(f"Net Profit: {data['net_profit']:,.0f} YER")
        print(f"ROI: {data['return_on_investment']:.1f}%")
```

### JavaScript/TypeScript

```javascript
const response = await fetch(
  "http://localhost:8090/v1/profitability/compare?crops=wheat,tomato,coffee&area_ha=2.5",
);
const data = await response.json();
console.log(`Best crop: ${data.best_crop.crop_name_en}`);
```

### cURL

```bash
#!/bin/bash
# Analyze all fields
for field in field-001 field-002 field-003; do
  curl -s "http://localhost:8090/v1/profitability/crop/season-2025?field_id=$field&crop_code=wheat&area_ha=2.5" | jq '.net_profit'
done
```

---

## Troubleshooting | استكشاف الأخطاء

### Service won't start

```bash
# Check if port 8090 is available
lsof -i :8090

# Check Python version (requires 3.12+)
python --version

# Check dependencies
pip list | grep fastapi
```

### Database connection issues

```bash
# Verify DATABASE_URL environment variable
echo $DATABASE_URL

# Test PostgreSQL connection
psql $DATABASE_URL -c "SELECT 1"
```

### API returns errors

```bash
# Check service logs
tail -f logs/field-core.log

# Test with verbose output
curl -v http://localhost:8090/healthz
```

---

## Next Steps | الخطوات التالية

1. **Customize Regional Data**: Update `REGIONAL_COSTS`, `REGIONAL_YIELDS`, and `REGIONAL_PRICES` in `profitability_analyzer.py` with your local market data.

2. **Add More Crops**: Extend the crop dictionaries to include crops specific to your region.

3. **Database Integration**: Connect to your actual field and crop database for real-time analysis.

4. **Export Reports**: Implement PDF/Excel export functionality for farmer reports.

5. **Mobile Integration**: Build mobile UI components to display profitability data.

---

## Support | الدعم

For questions or issues, contact the SAHOOL development team.

للأسئلة أو المشاكل، اتصل بفريق تطوير SAHOOL.

---

**Version:** 15.3.3
**Last Updated:** December 2025
**License:** Proprietary - KAFAAT
