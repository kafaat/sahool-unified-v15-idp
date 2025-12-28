# VRA Quick Reference Card
# بطاقة مرجع سريع لنظام التطبيق المتغير

## 🚀 Quick Start (3 Steps)

### 1. Start Service
```bash
cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service
python3 -m src.main
```

### 2. Generate Prescription
```bash
curl -X POST http://localhost:8090/v1/vra/generate \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "my_field",
    "latitude": 15.5,
    "longitude": 44.2,
    "vra_type": "fertilizer",
    "target_rate": 100,
    "unit": "kg/ha",
    "num_zones": 3
  }'
```

### 3. Export to GeoJSON
```bash
curl "http://localhost:8090/v1/vra/export/PRESCRIPTION_ID?format=geojson" > map.geojson
```

---

## 📋 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/v1/vra/generate` | Create prescription |
| GET | `/v1/vra/zones/{field_id}` | Preview zones |
| GET | `/v1/vra/prescriptions/{field_id}` | Get history |
| GET | `/v1/vra/prescription/{id}` | Get details |
| GET | `/v1/vra/export/{id}` | Export |
| DELETE | `/v1/vra/prescription/{id}` | Delete |
| GET | `/v1/vra/info` | Get info |

---

## 🎯 VRA Types

| Type | Arabic | Use Case |
|------|--------|----------|
| `fertilizer` | تسميد | Variable nitrogen/fertilizer |
| `seed` | بذار | Variable seeding rates |
| `lime` | جير | pH correction |
| `pesticide` | مبيدات | Targeted pest control |
| `irrigation` | ري | Variable water application |

---

## 📊 Zone Options

**3-Zone System (Simple):**
- Low (منخفض)
- Medium (متوسط)
- High (عالي)

**5-Zone System (Detailed):**
- Very Low (منخفض جداً)
- Low (منخفض)
- Medium (متوسط)
- High (عالي)
- Very High (عالي جداً)

---

## 💾 Export Formats

| Format | Use For |
|--------|---------|
| `geojson` | Web maps, GIS apps |
| `shapefile` | Farm equipment, GIS software |
| `isoxml` | ISOBUS equipment |

---

## 📝 Example Requests

### Fertilizer (Wheat)
```json
{
  "field_id": "wheat_001",
  "latitude": 15.5,
  "longitude": 44.2,
  "vra_type": "fertilizer",
  "target_rate": 120,
  "unit": "kg/ha",
  "num_zones": 3,
  "product_price_per_unit": 2.8
}
```

### Seeds (Sorghum)
```json
{
  "field_id": "sorghum_001",
  "latitude": 14.8,
  "longitude": 43.5,
  "vra_type": "seed",
  "target_rate": 50000,
  "unit": "seeds/ha",
  "num_zones": 5,
  "min_rate": 40000,
  "max_rate": 60000
}
```

### Irrigation
```json
{
  "field_id": "field_001",
  "latitude": 15.0,
  "longitude": 44.0,
  "vra_type": "irrigation",
  "target_rate": 25,
  "unit": "mm/ha",
  "num_zones": 3
}
```

---

## 🧪 Testing

### Run Tests
```bash
cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service
python3 tests/test_vra_generator.py
```

### Run Examples
```bash
python3 examples/vra_example.py
```

---

## 📁 File Locations

```
satellite-service/
├── src/
│   ├── vra_generator.py         # Core logic (764 lines)
│   ├── vra_endpoints.py         # API endpoints (574 lines)
│   └── main.py                  # Service (updated)
├── tests/
│   └── test_vra_generator.py    # Tests (305 lines)
├── examples/
│   └── vra_example.py           # Examples (392 lines)
├── VRA_README.md                # Full documentation
├── VRA_IMPLEMENTATION_SUMMARY.md # Implementation details
└── VRA_QUICK_REFERENCE.md       # This file
```

---

## ⚡ Common Commands

```bash
# Start service
python3 -m src.main

# Run tests
python3 tests/test_vra_generator.py

# Run examples
python3 examples/vra_example.py

# Check syntax
python3 -m py_compile src/vra_generator.py
python3 -m py_compile src/vra_endpoints.py

# View API docs
curl http://localhost:8090/docs

# Get VRA info
curl http://localhost:8090/v1/vra/info
```

---

## 💡 Tips

1. **Start Simple:** Use 3-zone system first
2. **Set Price:** Include `product_price_per_unit` for cost savings
3. **Set Limits:** Use `min_rate` and `max_rate` to constrain rates
4. **Export Early:** Export to GeoJSON to visualize zones
5. **Test First:** Run tests before deploying

---

## 🔧 Troubleshooting

**Service won't start?**
```bash
# Check if port is in use
lsof -i :8090

# Check imports
python3 -c "from src.vra_generator import VRAGenerator"
```

**Import errors?**
```bash
# Install dependencies
pip install fastapi uvicorn pydantic httpx numpy
```

**Tests failing?**
```bash
# Check Python version (requires 3.11+)
python3 --version

# Run individual test
python3 -m pytest tests/test_vra_generator.py::test_generate_fertilizer_prescription -v
```

---

## 📚 Documentation

- **Full Docs:** `VRA_README.md`
- **Implementation:** `VRA_IMPLEMENTATION_SUMMARY.md`
- **This Card:** `VRA_QUICK_REFERENCE.md`
- **Code Examples:** `examples/vra_example.py`
- **Tests:** `tests/test_vra_generator.py`

---

## ✅ Status

- **Version:** 1.0
- **Status:** Production Ready ✅
- **Tests:** All Passing ✅
- **Documentation:** Complete ✅
- **Examples:** Working ✅

---

**Need Help?** See `VRA_README.md` for detailed documentation.
