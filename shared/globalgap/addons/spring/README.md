# SPRING - Sustainable Program for Irrigation and Groundwater

## البرنامج المستدام للري والمياه الجوفية

GlobalGAP add-on module for responsible water management in agriculture, with special focus on Yemen's water scarcity context.

وحدة إضافية لـ GlobalGAP لإدارة المياه المسؤولة في الزراعة، مع التركيز الخاص على سياق ندرة المياه في اليمن.

---

## 📋 Overview / نظرة عامة

The SPRING module provides comprehensive water management capabilities for agricultural operations, including:

- **Water Sources Assessment** - Identify and track all water sources with legal compliance
- **Water Use Efficiency** - Monitor and optimize irrigation efficiency
- **Irrigation Systems** - Evaluate system suitability and maintenance
- **Water Quality** - Regular monitoring and compliance with safety standards
- **Legal Compliance** - Track permits and water rights
- **Monitoring & Records** - Comprehensive documentation and digital integration

### Yemen Context / السياق اليمني

Yemen faces severe water scarcity with groundwater levels declining 6-7 meters annually. This module includes:

- Groundwater depletion tracking and alerts
- Qat vs. food crops water usage analysis
- Rainwater harvesting maximization
- Seasonal pattern analysis for monsoon optimization

---

## 🚀 Quick Start

```python
from shared.globalgap.addons.spring import (
    # Checklist
    SPRING_CHECKLIST,
    calculate_spring_compliance,

    # Metrics
    WaterUsageMetric,
    WaterEfficiencyScore,
    IrrigationEfficiency,

    # Report Generation
    SpringReportGenerator,
    generate_spring_report,

    # Integration
    SpringIntegration,
    calculate_water_footprint,
    generate_usage_alerts,
)
```

---

## 📊 Components

### 1. **spring_checklist.py** - SPRING Requirements Checklist

Contains 20+ checklist items across 6 categories:

#### Categories:

- **WS** - Water Sources Assessment (4 items)
- **WE** - Water Use Efficiency (6 items)
- **IS** - Irrigation System Requirements (5 items)
- **WQ** - Water Quality Monitoring (4 items)
- **LC** - Legal Compliance for Water Rights (4 items)
- **MR** - Monitoring and Record Keeping (5 items)

#### Example Usage:

```python
from shared.globalgap.addons.spring import calculate_spring_compliance

# List of compliant item IDs
compliant_items = [
    "WS.01", "WS.02", "WE.01", "WE.02", "IS.01",
    "WQ.01", "LC.01", "MR.01"
]

# Calculate compliance
compliance = calculate_spring_compliance(compliant_items)

print(f"Overall Compliance: {compliance['overall_compliance_percentage']}%")
print(f"Compliant Items: {compliance['compliant_items']}/{compliance['total_items']}")
```

---

### 2. **water_metrics.py** - Pydantic Data Models

#### Key Models:

**WaterUsageMetric** - Track water usage records

```python
from datetime import date
from shared.globalgap.addons.spring import WaterUsageMetric

usage = WaterUsageMetric(
    usage_id="WU-2024-001",
    source_id="WELL-001",
    field_id="FIELD-N1",
    crop_type="Tomatoes",
    measurement_date=date(2024, 12, 15),
    volume_cubic_meters=125.5,
    crop_area_hectares=2.5,
    irrigation_method="DRIP",
    duration_hours=6.0,
)

print(f"Flow rate: {usage.flow_rate_m3_per_hour} m³/h")
```

**IrrigationEfficiency** - Calculate irrigation efficiency

```python
from shared.globalgap.addons.spring import IrrigationEfficiency

efficiency = IrrigationEfficiency(
    efficiency_id="IE-2024-Q4",
    field_id="FIELD-N1",
    measurement_period_start=date(2024, 10, 1),
    measurement_period_end=date(2024, 12, 31),
    irrigation_method="DRIP",
    water_applied_m3=5000,
    water_stored_in_root_zone_m3=4250,
    application_efficiency_percent=85.0,
    distribution_uniformity_percent=92.0,
)
```

**WaterSource** - Define water sources

```python
from shared.globalgap.addons.spring import WaterSource

source = WaterSource(
    source_id="WELL-001",
    source_type="WELL",
    name_en="North Field Well",
    name_ar="بئر الحقل الشمالي",
    depth_meters=120.0,
    capacity_cubic_meters=50000.0,
    legal_permit_number="YE-WR-2024-1234",
    max_daily_extraction_m3=500.0,
)
```

**WaterQualityTest** - Record water quality

```python
from shared.globalgap.addons.spring import WaterQualityTest

quality_test = WaterQualityTest(
    test_id="WQ-2024-001",
    source_id="WELL-001",
    test_date=date(2024, 12, 15),
    ph_level=7.2,
    ec_ds_per_m=1.5,
    tds_ppm=960,
    salinity_ppm=450,
    quality_status="GOOD",
    meets_irrigation_standards=True,
)
```

---

### 3. **spring_report_generator.py** - Bilingual Report Generation

Generate comprehensive PDF-ready reports in both Arabic and English.

#### Example:

```python
from datetime import date
from shared.globalgap.addons.spring import (
    SpringReportGenerator,
    WaterBalanceCalculation,
)

# Initialize generator
generator = SpringReportGenerator(
    farm_id="FARM-YE-001",
    farm_name_en="Al-Khair Agricultural Farm",
    farm_name_ar="مزرعة الخير الزراعية",
)

# Create water balance
water_balance = WaterBalanceCalculation(
    period_start=date(2024, 10, 1),
    period_end=date(2024, 12, 31),
    farm_id="FARM-YE-001",
    irrigation_water_m3=14500,
    rainfall_m3=450,
    recycled_water_m3=50,
    total_input_m3=15000,
    crop_evapotranspiration_m3=12500,
    runoff_m3=300,
    deep_percolation_m3=1800,
    evaporation_m3=400,
    total_output_m3=15000,
    storage_change_m3=0,
    balance_error_percent=0.5,
    beneficial_use_efficiency_percent=83.3,
)

# Generate report
report = generator.generate_report(
    period_start=date(2024, 10, 1),
    period_end=date(2024, 12, 31),
    water_balance=water_balance,
    efficiency_score=efficiency_score,
    compliant_items=compliant_items,
    water_sources=water_sources,
    usage_records=usage_records,
    quality_tests=quality_tests,
    efficiency_records=efficiency_records,
    include_yemen_context=True,
)

# Export to text
from shared.globalgap.addons.spring.spring_report_generator import export_report_to_text

text_report = export_report_to_text(report, language="both")
print(text_report)
```

---

### 4. **spring_integration.py** - Service Integration & Analytics

#### Calculate Water Footprint:

```python
from shared.globalgap.addons.spring import calculate_water_footprint

footprint = calculate_water_footprint(
    crop_type="Tomatoes",
    production_kg=50000,
    irrigation_water_m3=7500,
    rainfall_water_m3=2500,
    fertilizer_use_kg=500,
)

print(f"Total footprint: {footprint.total_water_footprint_m3_per_kg} m³/kg")
print(f"Blue water: {footprint.blue_water_m3_per_kg} m³/kg")
print(f"Green water: {footprint.green_water_m3_per_kg} m³/kg")
print(f"Performance: {footprint.performance_vs_benchmark}")
```

#### Generate Usage Alerts:

```python
from shared.globalgap.addons.spring import generate_usage_alerts

alerts = generate_usage_alerts(
    farm_id="FARM-YE-001",
    usage_records=usage_records,
    water_sources=water_sources,
    current_month_usage_m3=15000,
    previous_month_usage_m3=11000,
    groundwater_level_change_m=-2.5,  # Declined 2.5 meters
)

for alert in alerts:
    print(f"[{alert.severity}] {alert.title_en}")
    print(f"   {alert.message_en}")
    print(f"   Action: {alert.recommended_action_en}")
```

#### Track Seasonal Patterns:

```python
from shared.globalgap.addons.spring import track_seasonal_patterns

patterns = track_seasonal_patterns(
    farm_id="FARM-YE-001",
    usage_records=usage_records,
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31),
)

for pattern in patterns:
    print(f"Season: {pattern.season}")
    print(f"  Total use: {pattern.total_water_use_m3} m³")
    print(f"  Avg daily: {pattern.average_daily_use_m3} m³/day")
    print(f"  Dominant crops: {', '.join(pattern.dominant_crops)}")
```

#### Pull Data from Irrigation-Smart Service:

```python
from shared.globalgap.addons.spring import SpringIntegration

integration = SpringIntegration(
    farm_id="FARM-YE-001",
    irrigation_service_url="http://irrigation-smart:8080/api/v1",
    api_key="your-api-key",
)

# Pull irrigation data
data = integration.pull_irrigation_data(
    start_date=date(2024, 12, 1),
    end_date=date(2024, 12, 31),
    include_sensor_data=True,
)
```

---

## 🇾🇪 Yemen-Specific Features

### 1. **Groundwater Depletion Tracking**

Monitors groundwater level changes and generates critical alerts when depletion exceeds 1 meter/year.

```python
alerts = generate_usage_alerts(
    # ... other params
    groundwater_level_change_m=-6.5,  # Critical: 6.5m decline
)
# Will generate CRITICAL alert for groundwater depletion
```

### 2. **Qat vs Food Crops Analysis**

Tracks water usage for qat cultivation vs. food crops and recommends transitioning to food production.

```python
# System automatically detects qat water usage
# and generates alerts if >30% of water goes to qat
```

### 3. **Monsoon Season Optimization**

Seasonal tracking identifies monsoon periods (April-September) for maximizing rainwater harvesting.

### 4. **Water Scarcity Context**

All reports include Yemen-specific water scarcity context and recommendations.

---

## 📈 Compliance Levels

- **MANDATORY** (إلزامي) - Must comply 100%
- **RECOMMENDED** (موصى به) - Best practices

### Minimum Compliance Requirements:

- All MANDATORY items must be compliant
- Water quality tests: Minimum quarterly
- Legal permits: Must be current and valid
- Irrigation efficiency: Minimum 70% (85% for drip)
- Water use benchmarks: Within 20% of crop-specific standards

---

## 🔧 Integration with SAHOOL Platform

The SPRING module integrates with SAHOOL services:

1. **irrigation-smart** - Real-time irrigation monitoring
2. **weather-service** - Weather-based irrigation scheduling
3. **farm-management** - Farm and field data
4. **document-storage** - Store reports and certificates

---

## 📚 Checklist Item Examples

### Mandatory Items:

**WS.01 - Water Source Identification**

```
Requirement: All water sources used for irrigation must be identified
and documented, including type, location, and capacity.

Verification: Water source register, maps, technical specifications
```

**WE.01 - Water Use Measurement**

```
Requirement: All water used for irrigation must be measured using
flow meters or other reliable measurement devices.

Verification: Water meters, usage records, calibration certificates
```

**WQ.01 - Water Quality Testing - Frequency**

```
Requirement: Conduct water quality testing at least annually for all
irrigation water sources. Quarterly for groundwater and recycled water.

Verification: Laboratory test reports, testing schedule
```

**LC.01 - Water Extraction Permits**

```
Requirement: Valid permits/licenses must be held for all water
extraction (wells, boreholes, surface water abstraction).

Yemen Context: Permits from National Water Resources Authority (NWRA)
or local water authorities.
```

### Recommended Items:

**WE.04 - Soil Moisture Monitoring**

```
Recommendation: Use soil moisture sensors or other monitoring tools
to guide irrigation scheduling.

Benefits: Reduces water waste, improves crop yield
```

**IS.04 - Drip Irrigation Adoption**

```
Recommendation: Prioritize drip irrigation for high-value crops
(vegetables, fruits, orchards).

Benefits: 30-60% water savings vs. surface irrigation
```

---

## 📊 Reporting Outputs

### Report Sections:

1. **Executive Summary** - Overall compliance and efficiency
2. **Water Sources Assessment** - Source inventory and legal status
3. **Water Usage Analysis** - Consumption patterns and trends
4. **Water Quality Monitoring** - Test results and compliance
5. **Irrigation Efficiency** - Performance metrics
6. **Rainwater Harvesting** - Collection and storage
7. **Compliance Summary** - Category-by-category compliance
8. **Recommendations** - Improvement opportunities
9. **Yemen Context** - Water scarcity insights

### Export Formats:

- **Text** - Plain text bilingual report
- **JSON** - Structured data for integration
- **PDF** - (Future) PDF generation with charts

---

## 🎯 Best Practices

### For Yemen Farms:

1. **Prioritize Drip Irrigation** - Target >70% coverage for vegetables and fruits
2. **Monitor Groundwater** - Check water levels quarterly
3. **Maximize Rainwater Harvesting** - During monsoon season (April-September)
4. **Transition from Qat** - Gradually shift water to food crops
5. **Use Soil Moisture Sensors** - Optimize irrigation timing
6. **Regular Quality Testing** - Quarterly for groundwater sources
7. **Maintain Legal Permits** - Keep all water rights current
8. **Digital Record Keeping** - Use SAHOOL irrigation-smart service

---

## 🔍 Troubleshooting

### Common Issues:

**Import Errors:**

```python
# Ensure parent package is in path
import sys
sys.path.append('/home/user/sahool-unified-v15-idp')

from shared.globalgap.addons.spring import *
```

**Missing Dependencies:**

```bash
pip install pydantic
```

**Data Validation Errors:**

- Check that all required fields are provided
- Ensure dates are in correct format (YYYY-MM-DD)
- Verify numeric values are within valid ranges

---

## 📞 Support

For questions or issues:

- Technical Support: SAHOOL Platform Team
- SPRING Methodology: GlobalGAP IFA v6 Documentation
- Yemen Water Context: National Water Resources Authority (NWRA)

---

## 📄 License

Part of the SAHOOL Unified Platform for agricultural management in Yemen.

---

## 🌱 Contributing

To add new features or improve existing functionality:

1. Follow existing code patterns
2. Include bilingual documentation (English/Arabic)
3. Add Yemen-specific context where relevant
4. Write comprehensive examples
5. Test with real farm data

---

**Version:** 1.0.0
**Last Updated:** December 2024
**Maintained by:** SAHOOL Development Team
