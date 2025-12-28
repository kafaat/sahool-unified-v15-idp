# GlobalGAP IFA v6 Checklist
# قائمة التحقق GlobalGAP IFA v6

Complete Integrated Farm Assurance (IFA) version 6 checklist implementation for Fruit & Vegetables certification.

تطبيق كامل لقائمة التحقق من ضمان المزرعة المتكامل (IFA) الإصدار 6 لشهادة الفواكه والخضروات.

## Overview / نظرة عامة

This module provides a comprehensive implementation of the GlobalGAP IFA v6 control points checklist with:

- **52 checklist items** across 13 categories
- **Arabic and English** translations for all content
- **Three compliance levels**: MAJOR_MUST, MINOR_MUST, RECOMMENDATION
- **Evidence types** for each control point
- **Helper functions** for checklist navigation and compliance calculation

## Categories / الفئات

| Code | Name (EN) | Name (AR) | Items |
|------|-----------|-----------|-------|
| `SITE_HISTORY` | Site History and Management | تاريخ الموقع والإدارة | 3 |
| `RECORD_KEEPING` | Record Keeping and Documentation | حفظ السجلات والتوثيق | 4 |
| `WORKERS_HEALTH` | Workers Health, Safety and Welfare | صحة وسلامة ورفاهية العمال | 7 |
| `TRACEABILITY` | Product Traceability and Segregation | تتبع المنتجات والفصل | 4 |
| `PLANT_PROPAGATION` | Plant Propagation Material | مواد التكاثر النباتي | 2 |
| `SOIL_MANAGEMENT` | Soil and Substrate Management | إدارة التربة والركيزة | 3 |
| `FERTILIZER` | Fertilizer Application | تطبيق الأسمدة | 4 |
| `IRRIGATION` | Irrigation and Water Management | الري وإدارة المياه | 4 |
| `IPM` | Integrated Pest Management | الإدارة المتكاملة للآفات | 3 |
| `PLANT_PROTECTION` | Plant Protection Products | منتجات وقاية النباتات | 6 |
| `HARVEST` | Harvesting Procedures | إجراءات الحصاد | 4 |
| `PRODUCE_HANDLING` | Produce Handling and Post-Harvest | معالجة المنتجات وما بعد الحصاد | 4 |
| `ENVIRONMENT` | Environmental Management | الإدارة البيئية | 4 |

## Compliance Levels / مستويات الامتثال

- **MAJOR_MUST** (34 items): 100% compliance required - critical control points
- **MINOR_MUST** (20 items): 95% compliance required - important requirements
- **RECOMMENDATION** (10 items): Best practices - no minimum threshold

## Usage Examples / أمثلة الاستخدام

### 1. Get Checklist Statistics

```python
from shared.globalgap.ifa_v6_checklist import get_statistics

stats = get_statistics()
print(f"Total items: {stats['total_items']}")
print(f"Categories: {stats['total_categories']}")
print(f"Major Must items: {stats['by_compliance_level']['MAJOR_MUST']}")

# Output:
# Total items: 52
# Categories: 13
# Major Must items: 34
```

### 2. Get a Specific Category

```python
from shared.globalgap.ifa_v6_checklist import get_category

category = get_category('WORKERS_HEALTH')
print(f"{category.name_en} / {category.name_ar}")
print(f"Items: {len(category.items)}")

for item in category.items:
    print(f"  {item.id}: {item.title_en}")
    print(f"  Level: {item.compliance_level}")
```

### 3. Get a Specific Checklist Item

```python
from shared.globalgap.ifa_v6_checklist import get_checklist_item

item = get_checklist_item('AF.3.6.1')
print(f"{item.title_en}")
print(f"{item.title_ar}")
print(f"Compliance Level: {item.compliance_level}")
print(f"Evidence Required: {item.evidence_required}")
print(f"Guidance: {item.guidance_en}")
```

### 4. Filter Items by Compliance Level

```python
from shared.globalgap.ifa_v6_checklist import get_items_by_compliance_level
from shared.globalgap.constants import ComplianceLevel

# Get all MAJOR_MUST items
major_items = get_items_by_compliance_level(ComplianceLevel.MAJOR_MUST)
print(f"Total MAJOR_MUST items: {len(major_items)}")

# Get MINOR_MUST items for a specific category
minor_items = get_items_by_compliance_level(
    ComplianceLevel.MINOR_MUST,
    category_code='IRRIGATION'
)
```

### 5. Get All Items in Order

```python
from shared.globalgap.ifa_v6_checklist import get_all_items

all_items = get_all_items()
for item in all_items:
    print(f"{item.id}: {item.title_en} ({item.compliance_level})")
```

### 6. Calculate Compliance Score from Audit Findings

```python
from shared.globalgap.ifa_v6_checklist import calculate_compliance_score

# Sample audit findings
findings = [
    {"checklist_item_id": "AF.1.1.1", "is_compliant": True, "is_not_applicable": False},
    {"checklist_item_id": "AF.1.1.2", "is_compliant": False, "is_not_applicable": False},
    {"checklist_item_id": "AF.3.1.1", "is_compliant": True, "is_not_applicable": False},
    {"checklist_item_id": "AF.3.2.1", "is_compliant": True, "is_not_applicable": False},
    # ... more findings
]

result = calculate_compliance_score(findings)

print(f"Overall Pass: {result['overall_pass']}")
print(f"Recommendation: {result['certification_recommendation']}")

# Breakdown by compliance level
for level, stats in result['by_level'].items():
    print(f"\n{level}:")
    print(f"  Total: {stats['total_items']}")
    print(f"  Compliant: {stats['compliant']}")
    print(f"  Compliance %: {stats['compliance_percentage']}")
    print(f"  Passes: {stats['passes']}")
```

### 7. Working with the Complete Checklist Dictionary

```python
from shared.globalgap.ifa_v6_checklist import IFA_V6_CHECKLIST

# Iterate through all categories
for code, category in IFA_V6_CHECKLIST.items():
    print(f"{code}: {category.name_en}")
    print(f"  Items: {len(category.items)}")

    # Count compliance levels in this category
    major = category.count_by_compliance_level(ComplianceLevel.MAJOR_MUST)
    minor = category.count_by_compliance_level(ComplianceLevel.MINOR_MUST)
    print(f"  Major Must: {major}, Minor Must: {minor}")
```

## Data Model / نموذج البيانات

### ChecklistItem

Each checklist item includes:

```python
{
    "id": str,                      # Control point ID (e.g., "AF.1.1.1")
    "category_code": str,           # Category code
    "subcategory": str,             # Subcategory name
    "title_en": str,                # Title in English
    "title_ar": str,                # Title in Arabic
    "description_en": str,          # Description in English
    "description_ar": str,          # Description in Arabic
    "compliance_level": str,        # MAJOR_MUST, MINOR_MUST, or RECOMMENDATION
    "evidence_required": List[str], # Evidence types: DOCUMENT, OBSERVATION, etc.
    "guidance_en": str,             # Implementation guidance in English
    "guidance_ar": str,             # Implementation guidance in Arabic
    "applicable_to": List[str],     # Scopes: FV, CROPS_BASE, etc.
    "not_applicable_allowed": bool, # Whether N/A is acceptable
    "order": int                    # Display order
}
```

### ChecklistCategory

Each category includes:

```python
{
    "code": str,           # Category code
    "name_en": str,        # Name in English
    "name_ar": str,        # Name in Arabic
    "description_en": str, # Description in English
    "description_ar": str, # Description in Arabic
    "items": List[ChecklistItem],
    "order": int          # Display order
}
```

## Evidence Types / أنواع الأدلة

- **DOCUMENT**: Procedures, records, certificates
- **OBSERVATION**: Physical inspection, site visit
- **INTERVIEW**: Staff interviews, management review
- **TEST_RESULT**: Lab analysis, quality tests
- **PHOTO**: Photographic evidence

## Integration with Audit System / التكامل مع نظام التدقيق

### Creating an Audit with IFA v6 Checklist

```python
from shared.globalgap.ifa_v6_checklist import get_all_items, calculate_compliance_score
from shared.globalgap.models import AuditSession, AuditFinding
from datetime import datetime

# Create audit session
audit = AuditSession(
    audit_number="AUDIT-2024-001",
    farm_id="farm_123",
    ggn="4012345678901",
    audit_type="INITIAL",
    audit_scope=["FV"],
    lead_auditor_id="auditor_001",
    certification_body="CB Name",
    cb_code="CB001",
    scheduled_date=datetime.now().date()
)

# Audit each checklist item
for item in get_all_items():
    # Collect evidence and determine compliance
    finding = AuditFinding(
        audit_id=audit.id,
        checklist_item_id=item.id,
        is_compliant=True,  # or False based on audit
        is_not_applicable=False,
        evidence_collected=["DOCUMENT", "OBSERVATION"],
        notes_en="Complies with requirements",
        notes_ar="يتوافق مع المتطلبات",
        auditor_id="auditor_001",
        audit_date=datetime.now()
    )
    audit.findings.append(finding)

# Calculate compliance score
findings_data = [
    {
        "checklist_item_id": f.checklist_item_id,
        "is_compliant": f.is_compliant,
        "is_not_applicable": f.is_not_applicable
    }
    for f in audit.findings
]

compliance_result = calculate_compliance_score(findings_data)

# Set audit recommendation
audit.recommendation = compliance_result['certification_recommendation']
```

## Compliance Calculation Rules / قواعد حساب الامتثال

### Thresholds / العتبات

- **MAJOR_MUST**: 100% compliance required (no failures allowed)
- **MINOR_MUST**: 95% compliance required (up to 5% failures allowed)
- **RECOMMENDATION**: No minimum threshold

### Certification Decision / قرار الشهادة

A farm is recommended for certification if:
- MAJOR_MUST compliance ≥ 100%
- MINOR_MUST compliance ≥ 95%

Non-applicable (N/A) items are excluded from percentage calculation.

## Sample Control Points / نقاط تحكم نموذجية

### AF.1.1.1 - Site History and Risk Assessment
**تاريخ الموقع وتقييم المخاطر**

- **Level**: MAJOR_MUST
- **Evidence**: DOCUMENT, OBSERVATION
- **Guidance**: Maintain records of previous land use, identify potential contamination sources

### AF.3.6.1 - No Child Labor
**عدم عمالة الأطفال**

- **Level**: MAJOR_MUST
- **Evidence**: DOCUMENT, OBSERVATION, INTERVIEW
- **Guidance**: Verify age through documentation; minimum age 15 years

### AF.10.1.1 - Only Authorized PPP Used
**استخدام منتجات وقاية النباتات المصرح بها فقط**

- **Level**: MAJOR_MUST
- **Evidence**: DOCUMENT, OBSERVATION
- **Guidance**: Verify registration status; check approved crop on label

## Related Modules / الوحدات ذات الصلة

- **models.py**: Pydantic data models for all structures
- **constants.py**: IFA_VERSION, thresholds, GGN patterns
- **validators.py**: Validation functions
- **api_client.py**: GlobalGAP Supply Chain Portal API integration

## Notes / ملاحظات

1. All checklist items are based on actual IFA v6 requirements
2. Control point IDs follow the standard AF.x.x.x numbering scheme
3. Categories align with official GlobalGAP modules including GRASP and SPRING
4. Arabic translations provided for all content
5. Evidence requirements specified for each control point

## Version / الإصدار

- **IFA Version**: 6.0
- **Module Version**: 6.0.0
- **Last Updated**: December 2024

---

For more information about GlobalGAP certification, visit: https://www.globalgap.org
