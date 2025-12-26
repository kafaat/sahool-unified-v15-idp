# SAHOOL Database Seed Data

Comprehensive seed data for the SAHOOL agricultural platform, featuring realistic Yemen agricultural scenarios with Arabic localization.

## Overview

This seed data package provides sample data for:
- **Users**: Admin, farmers, agronomists, and researchers across Yemen regions
- **Farms**: 10 farms in different governorates (صنعاء، تعز، حضرموت، إب، الحديدة)
- **Fields**: 30+ fields with GeoJSON boundaries and various soil/irrigation types
- **Crops**: 50+ Yemen-specific crops with GDD, seasons, and pricing
- **Weather**: 1 year of historical weather data for major cities
- **Inventory**: Seeds, fertilizers, pesticides, tools, and suppliers
- **Satellite**: NDVI observations and growth monitoring
- **Financial**: Transactions, invoices, and subscriptions

## Files

| File | Description | Records |
|------|-------------|---------|
| `seed_runner.py` | Main Python script to run all seeds | - |
| `01_users.sql` | Sample users (farmers, agronomists, admin) | 10 users |
| `02_farms.sql` | Farms across Yemen governorates | 10 farms |
| `03_fields.sql` | Fields with GeoJSON geometries | 30 fields |
| `04_crops.sql` | Yemen crop catalog with GDD and prices | 50+ crops |
| `05_weather_history.sql` | Historical weather for major cities | ~1,825 records |
| `06_inventory.sql` | Inventory items, suppliers, stock | 35+ items, 6 suppliers |
| `07_satellite_data.sql` | NDVI observations and alerts | 1,000+ observations |
| `08_financial.sql` | Transactions, invoices, subscriptions | 30+ transactions |

## Quick Start

### Prerequisites

- PostgreSQL 12+
- Python 3.8+
- `psycopg2-binary` Python package

```bash
pip install psycopg2-binary
```

### Running Seeds

**Option 1: Using database URL**
```bash
cd database/seeds
python seed_runner.py --db-url postgresql://user:password@localhost:5432/sahool
```

**Option 2: Using environment variable**
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/sahool"
python seed_runner.py
```

**Option 3: Using environment name**
```bash
export DATABASE_URL_DEV="postgresql://user:password@localhost:5432/sahool_dev"
python seed_runner.py --env development
```

### Verification Only

To verify the database without running seeds:
```bash
python seed_runner.py --db-url <url> --verify-only
```

### Continue on Error

To continue running remaining seeds even if one fails:
```bash
python seed_runner.py --db-url <url> --continue-on-error
```

## Data Details

### 1. Users (01_users.sql)

**Default Password**: All users have password `admin123` or `farmer123` (hashed with bcrypt)

| Role | Count | Regions |
|------|-------|---------|
| Admin | 1 | System-wide |
| Farmers | 5 | صنعاء، تعز، حضرموت، إب، الحديدة |
| Agronomists | 2 | Advisory services |
| Researchers | 1 | Data analysis |

**Sample Users:**
- `admin@sahool.ye` - System Administrator (مدير النظام)
- `ahmed.alsanani@sahool.ye` - Farmer from Sana'a
- `mohammed.altaizi@sahool.ye` - Farmer from Ta'izz (Coffee)
- `ali.alhadrami@sahool.ye` - Farmer from Hadramout (Dates)
- `dr.khalid@sahool.ye` - Senior Agronomist

### 2. Farms (02_farms.sql)

10 farms distributed across Yemen's major agricultural regions:

| Governorate | Farms | Total Area (ha) |
|-------------|-------|-----------------|
| صنعاء (Sana'a) | 2 | 40.8 |
| تعز (Ta'izz) | 2 | 21.0 |
| حضرموت (Hadramout) | 2 | 75.2 |
| إب (Ibb) | 2 | 29.2 |
| الحديدة (Al-Hudaydah) | 2 | 175.5 |

**Featured Farms:**
- Green Valley Farm (مزرعة الوادي الأخضر) - Highland cereals
- Al-Mawasit Coffee Estate (مزرعة المواسط للبن) - Mountain coffee
- Wadi Hadramout Date Farm (مزرعة وادي حضرموت للنخيل) - Date palms
- Red Sea Agricultural Complex (مجمع البحر الأحمر الزراعي) - Large-scale vegetables

### 3. Fields (03_fields.sql)

30 fields with realistic GeoJSON polygon boundaries:

**Soil Types Distribution:**
- Loamy: 40%
- Sandy: 27%
- Clay: 20%
- Silty: 13%

**Irrigation Types:**
- Drip: 47%
- Sprinkler: 23%
- Flood: 17%
- Rainfed: 13%

**GeoJSON Format:**
```json
{
  "type": "Polygon",
  "coordinates": [[[lon, lat], [lon, lat], ...]]
}
```

### 4. Crops Catalog (04_crops.sql)

50+ Yemen-specific crops with comprehensive data:

**Categories:**
- **Cereals** (الحبوب): Wheat, Barley, Sorghum, Millet, Maize
- **Legumes** (البقوليات): Lentils, Chickpeas, Faba Beans, Cowpea, Peanuts
- **Vegetables** (الخضروات): Tomato, Onion, Potato, Cucumber, Eggplant, Peppers
- **Fruits** (الفواكه): Dates, Mango, Banana, Grapes, Citrus, Melons, Pomegranate
- **Cash Crops** (المحاصيل النقدية): Coffee, Qat, Cotton, Sesame, Tobacco
- **Herbs & Spices**: Coriander, Cumin, Fenugreek, Basil, Mint
- **Forage**: Alfalfa, Clover, Rhodes Grass

**Data Fields:**
- Arabic and English names
- Growing Degree Days (GDD) requirements
- Planting seasons and months
- Price ranges (YER/kg)
- Yield expectations (kg/ha)
- Water requirements
- Drought tolerance
- Suitable Yemen regions
- Optimal altitude ranges

**Example - Coffee (Arabica):**
```sql
name_en: 'Arabica Coffee'
name_ar: 'بن عربي'
gdd_total: NULL (perennial)
growing_days: 1095-1460
price_avg: 8000 YER/kg
yield_avg: 1250 kg/ha
water_req: 'high'
regions: ['تعز', 'إب', 'صنعاء', 'الحديدة']
altitude: 1000-2400m
```

### 5. Weather History (05_weather_history.sql)

1 year of daily weather data for 5 major Yemen cities:

| Location | Climate Type | Avg Temp (°C) | Annual Rainfall (mm) |
|----------|--------------|---------------|----------------------|
| Sana'a | Highland | 16-22 | 400-600 |
| Ta'izz | Mountain | 20-26 | 600-800 |
| Al-Hudaydah | Coastal Hot | 28-38 | 50-150 |
| Hadramout (Shibam) | Desert/Wadi | 26-36 | 80-200 |
| Ibb | Highland Wet | 18-24 | 800-1200 |

**Data Fields:**
- Temperature (avg, min, max)
- Precipitation (mm)
- Humidity (%)
- Wind speed and direction
- Solar radiation (W/m²)
- Cloud cover
- Pressure
- Growing Degree Days (GDD base 10°C)

**Features:**
- Realistic seasonal patterns
- Monsoon seasons for appropriate regions
- Temperature variations by altitude
- Accurate climate zones

### 6. Inventory (06_inventory.sql)

Comprehensive agricultural supply inventory:

**Suppliers:** 6 Yemen-based suppliers
- Yemen Agricultural Supplies Co. (صنعاء)
- Al-Thawra Seeds & Fertilizers (صنعاء)
- Red Sea Agricultural Import/Export (الحديدة)
- Hadramout Farming Solutions (حضرموت)
- Green Yemen Trading (إب)
- International Agro Tech Yemen (صنعاء)

**Inventory Categories:**
- **Seeds**: 10 items (cereals, vegetables, tree crops)
- **Fertilizers**: 6 items (NPK, Urea, DAP, Organic, Micronutrients)
- **Pesticides**: 5 items (Insecticides, Fungicides, Herbicides)
- **Tools**: 4 items (Hand tools, sprayers, pumps)
- **Irrigation Supplies**: 4 items (Drip systems, pipes, emitters)

**Data Fields:**
- SKU, barcode
- Arabic/English names and descriptions
- Categories and subcategories
- Units (KG, LITER, PIECE, BAG, etc.)
- Current quantity, reorder levels
- Costs and selling prices (YER)
- Supplier relationships
- Stock movements

### 7. Satellite Data (07_satellite_data.sql)

NDVI (Normalized Difference Vegetation Index) observations:

**Coverage:**
- 1,000+ observations across 30 fields
- 6-month historical data
- 5-8 day revisit frequency (Sentinel-2)
- Cloud filtering (<50% cloud cover)

**Growth Patterns:**
- Early germination: NDVI 0.15-0.25
- Seedling stage: NDVI 0.30-0.45
- Vegetative growth: NDVI 0.50-0.70
- Peak growth: NDVI 0.65-0.85
- Flowering/fruiting: NDVI 0.55-0.75
- Ripening: NDVI 0.40-0.55
- Harvest/senescence: NDVI 0.25-0.35

**Perennial Crops (Coffee, Dates):**
- Stable NDVI: 0.65-0.80
- Seasonal variations minimal

**NDVI Alerts:**
- Anomaly detection (negative/positive)
- Threshold breaches
- Sudden drops (>15%)
- Growth stage monitoring

**Data Fields:**
- NDVI statistics (mean, min, max, std, percentiles)
- Cloud coverage
- Confidence scores
- Pixel counts
- Source tracking (Sentinel-2)
- Scene IDs

### 8. Financial Data (08_financial.sql)

Comprehensive financial tracking:

**Subscriptions:**
- Basic Plan: 5,000 YER/month
- Premium Plan: 15,000 YER/month
- Enterprise Plan: 150,000 YER/year
- Features: Farms, fields, satellite monitoring, AI advisor

**Transaction Categories:**

**Expenses:**
- Seed purchases
- Fertilizer purchases
- Pesticide purchases
- Labor (planting, harvesting, pruning)
- Equipment purchases
- Irrigation system maintenance
- Water costs

**Income:**
- Harvest sales (crops)
- Government subsidies
- Agricultural support programs

**Invoices:**
- Purchase invoices (to suppliers)
- Sales invoices (to buyers)
- Status tracking (pending, paid, overdue)
- Payment terms
- Line items

**Sample Data:**
- 20+ transactions across different farmers
- Range: 28,000 - 3,500,000 YER
- Purchase and sales invoices
- Active subscriptions for all farmer users

## Data Relationships

```
Users (farmers)
  └── Farms (owned_by)
       └── Fields (farm_id)
            ├── NDVI Observations (field_id)
            │    └── NDVI Alerts (observation_id)
            ├── Crops/Plantings (field_id)
            └── Transactions (field_id)

Suppliers
  └── Inventory Items (supplier_id)
       └── Stock Movements (item_id)
            └── Transactions (reference_id)

Users
  └── Subscriptions (user_id)
  └── Transactions (user_id)
       └── Invoices (reference_id)

Weather History (location-based, no foreign keys)
Crop Catalog (reference data, no foreign keys)
```

## Yemen Agricultural Context

### Governorates Covered

1. **صنعاء (Sana'a)** - Highland agriculture, cereals, qat
   - Altitude: 1,500-2,500m
   - Climate: Temperate, two rainy seasons
   - Main crops: Wheat, barley, qat, vegetables

2. **تعز (Ta'izz)** - Mountain agriculture, coffee
   - Altitude: 1,000-2,400m
   - Climate: Mountain, good rainfall
   - Main crops: Coffee, fruits, vegetables

3. **حضرموت (Hadramout)** - Desert/wadi agriculture, dates
   - Altitude: 0-1,200m
   - Climate: Arid, wadi irrigation
   - Main crops: Dates, honey production

4. **إب (Ibb)** - "Green Province", high rainfall
   - Altitude: 1,000-2,400m
   - Climate: Wet highland, highest rainfall
   - Main crops: Qat, coffee, cereals, vegetables

5. **الحديدة (Al-Hudaydah)** - Coastal agriculture
   - Altitude: 0-500m
   - Climate: Hot coastal, Tihama plains
   - Main crops: Cotton, sesame, vegetables, fruits

### Currency

All financial data is in **Yemeni Rial (YER)**

Approximate exchange rates (for reference):
- 1 USD ≈ 250 YER (official)
- Prices are realistic for Yemen agricultural context

### Localization

- All names have Arabic translations (name_ar)
- Descriptions in both English and Arabic
- Region names in Arabic
- Culturally appropriate data (qat, coffee specific to Yemen)

## Database Schema Notes

### Required Tables

The seed data assumes the following tables exist:

- `users` (id, tenant_id, email, name, name_ar, phone, roles, ...)
- `farms` (id, tenant_id, name, name_ar, owner_id, latitude, longitude, ...)
- `fields` (id, tenant_id, farm_id, name, name_ar, boundary_geojson, ...)
- `ndvi_observations` (id, tenant_id, field_id, obs_date, ndvi_mean, ...)
- `ndvi_alerts` (id, tenant_id, field_id, alert_type, severity, ...)

### Created Tables

Some files create tables if they don't exist:

- `crop_catalog` (04_crops.sql)
- `weather_history` (05_weather_history.sql)
- `suppliers`, `inventory_items`, `stock_movements` (06_inventory.sql)
- `transactions`, `invoices`, `subscriptions` (08_financial.sql)

### Data Types

- IDs: UUID
- Dates: DATE or TIMESTAMP (with timezone)
- Coordinates: DECIMAL(10, 6)
- Money: DECIMAL(15, 2)
- GeoJSON: TEXT or JSONB

## Customization

### Modifying Data

1. **Adjust quantities**: Edit the INSERT statements
2. **Add more records**: Copy and modify existing INSERT blocks
3. **Change regions**: Update governorate names and coordinates
4. **Modify prices**: Update YER amounts based on current rates
5. **Extend date ranges**: Modify the date_series CTEs

### Disabling Cleanup

By default, TRUNCATE statements are commented out:
```sql
-- TRUNCATE TABLE users CASCADE;
```

Uncomment to clear existing data before seeding.

### Adding Custom Crops

Follow this template in `04_crops.sql`:
```sql
INSERT INTO crop_catalog (
    crop_code, name_en, name_ar, scientific_name,
    category, subcategory,
    gdd_base_temp_c, gdd_total_required,
    growing_days_min, growing_days_max,
    planting_season, planting_months,
    price_yer_per_kg_min, price_yer_per_kg_max, price_yer_per_kg_avg,
    yield_kg_per_ha_min, yield_kg_per_ha_max, yield_kg_per_ha_avg,
    water_requirement, drought_tolerance,
    suitable_regions, optimal_altitude_min_m, optimal_altitude_max_m
) VALUES (
    'YOUR-CODE', 'English Name', 'الاسم العربي', 'Scientific name',
    'category', 'subcategory',
    10, 1500, 90, 120,
    'Season', ARRAY[3,4,5],
    100, 500, 300,
    1000, 5000, 3000,
    'medium', 'medium',
    ARRAY['صنعاء', 'تعز'], 1000, 2000
);
```

## Verification Queries

Each seed file includes verification queries at the end. Run them to check data:

```sql
-- Count records by type
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM farms;
SELECT COUNT(*) FROM fields;
SELECT COUNT(*) FROM crop_catalog;
SELECT COUNT(*) FROM weather_history;
SELECT COUNT(*) FROM inventory_items;
SELECT COUNT(*) FROM ndvi_observations;
SELECT COUNT(*) FROM transactions;

-- Data quality checks
SELECT governorate, COUNT(*) FROM farms GROUP BY governorate;
SELECT category, COUNT(*) FROM crop_catalog GROUP BY category;
SELECT location_name, COUNT(*) FROM weather_history GROUP BY location_name;
SELECT category, SUM(current_quantity * unit_cost) as value FROM inventory_items GROUP BY category;
```

## Troubleshooting

### Common Issues

**1. Connection Error**
```
Error: psycopg2.OperationalError: could not connect to server
```
**Solution**: Check database URL, ensure PostgreSQL is running

**2. Table Does Not Exist**
```
Error: relation "users" does not exist
```
**Solution**: Run database migrations first, or create required tables

**3. Foreign Key Violation**
```
Error: insert or update violates foreign key constraint
```
**Solution**: Run seed files in order (01, 02, 03, ...)

**4. UUID Generation Error**
```
Error: function gen_random_uuid() does not exist
```
**Solution**: Enable extension: `CREATE EXTENSION IF NOT EXISTS "pgcrypto";`

**5. Duplicate Key Error**
```
Error: duplicate key value violates unique constraint
```
**Solution**: Run with cleanup enabled (uncomment TRUNCATE statements)

### Debug Mode

Add `--continue-on-error` to see all errors:
```bash
python seed_runner.py --db-url <url> --continue-on-error
```

## Production Considerations

### Before Production Use

1. **Review all data** for appropriateness
2. **Change default passwords** immediately
3. **Adjust prices** to current market rates
4. **Update coordinates** to actual locations if needed
5. **Remove test/demo users** if not needed
6. **Verify currency rates** and update amounts

### Security

- All passwords are hashed with bcrypt
- Default password: `admin123` / `farmer123`
- **CHANGE THESE IMMEDIATELY** in production
- Consider removing demo user accounts

### Performance

- Seed data includes ~3,000+ total records
- Expected runtime: 30-60 seconds
- Indexes are created where needed
- For large datasets, consider batching inserts

## Contributing

To add more seed data:

1. Follow existing patterns
2. Maintain Arabic translations
3. Include verification queries
4. Update this README
5. Test with fresh database

## License

This seed data is part of the SAHOOL platform.

## Support

For issues or questions:
- Check verification queries in each SQL file
- Review troubleshooting section
- Ensure all prerequisites are met
- Run with `--verify-only` to check database state

---

**Last Updated**: 2024
**Version**: 1.0
**Records**: ~3,000+ across all tables
