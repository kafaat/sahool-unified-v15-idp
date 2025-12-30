# ComplianceAgent Guide
# دليل وكيل الامتثال

## Overview | نظرة عامة

The ComplianceAgent is a specialized AI agent for agricultural certification compliance in the SAHOOL system. It helps farms maintain compliance with GlobalGAP, organic certifications (EU, USDA), Saudi GAP, and ISO 22000 standards.

وكيل الامتثال هو وكيل ذكاء اصطناعي متخصص للامتثال للشهادات الزراعية في نظام SAHOOL. يساعد المزارع على الحفاظ على الامتثال لمعايير GlobalGAP والشهادات العضوية (EU، USDA) و Saudi GAP و ISO 22000.

## Supported Certifications | الشهادات المدعومة

1. **GLOBALGAP_IFA_V6** - GlobalGAP Integrated Farm Assurance v6
2. **ORGANIC_EU** - EU Organic Regulation (EC) 834/2007 & 889/2008
3. **ORGANIC_USDA** - USDA National Organic Program (NOP)
4. **SAUDI_GAP** - Saudi GAP Standards
5. **ISO_22000** - Food Safety Management System

## Control Point Categories | فئات نقاط المراقبة

- **SITE_MANAGEMENT** - إدارة الموقع
- **RECORD_KEEPING** - حفظ السجلات
- **TRACEABILITY** - التتبع
- **IPM** - الإدارة المتكاملة للآفات
- **FERTILIZER_USE** - استخدام الأسمدة
- **IRRIGATION** - الري
- **HARVEST** - الحصاد
- **POST_HARVEST** - ما بعد الحصاد
- **WORKER_SAFETY** - سلامة العمال
- **ENVIRONMENT** - البيئة
- **WASTE_MANAGEMENT** - إدارة النفايات

## Core Methods | الوظائف الأساسية

### 1. check_compliance()
Check if a farm action complies with certification requirements.

**Use Case:** Before applying pesticide, fertilizer, or any farm operation.

```python
result = await agent.check_compliance(
    action={
        "type": "pesticide_application",
        "description": "Apply neem oil for aphid control",
        "product": "Neem oil 1%",
    },
    certification=CertificationStandard.ORGANIC_EU,
    context={"crop": "Tomato", "stage": "Flowering"}
)
```

**Returns:**
- Compliance status (compliant/non-compliant/needs verification)
- Relevant control point references
- Risk level and concerns
- Corrective actions or alternatives

### 2. get_control_points()
Get detailed control points for a certification standard.

**Use Case:** Understanding certification requirements for specific categories.

```python
result = await agent.get_control_points(
    certification=CertificationStandard.GLOBALGAP_IFA_V6,
    category=ControlPointCategory.IPM
)
```

**Returns:**
- Control point codes and descriptions
- Compliance levels (mandatory/recommended)
- Evidence requirements
- Best practices

### 3. audit_readiness()
Assess farm's readiness for certification audit.

**Use Case:** Pre-audit assessment and gap analysis.

```python
result = await agent.audit_readiness(
    farm_id="SA-FARM-001",
    certification=CertificationStandard.GLOBALGAP_IFA_V6,
    farm_data={
        "crops": ["Tomato", "Cucumber"],
        "records_available": [...],
        "missing_documents": [...]
    }
)
```

**Returns:**
- Overall readiness score (0-100)
- Documentation completeness percentage
- Critical gaps requiring immediate attention
- Prioritized action plan
- Estimated time to audit-ready

### 4. generate_checklist()
Generate customized audit preparation checklist.

**Use Case:** Systematic audit preparation.

```python
result = await agent.generate_checklist(
    certification=CertificationStandard.ORGANIC_USDA,
    farm_data={
        "crops": ["Dates", "Wheat"],
        "size_hectares": 50
    }
)
```

**Returns:**
- Comprehensive checklist organized by category
- Task priorities (critical/high/medium/low)
- Timeline for each task
- Documentation requirements
- Verification methods

### 5. track_documentation()
Track required documentation status.

**Use Case:** Document management and tracking.

```python
result = await agent.track_documentation(
    farm_id="SA-FARM-001",
    certification=CertificationStandard.GLOBALGAP_IFA_V6,
    current_docs=[
        "Harvest records 2023-2024",
        "IPM monitoring logs",
        "Worker training records"
    ]
)
```

**Returns:**
- Complete list of required documents
- Current vs. required status
- Missing critical documents
- Retention period compliance
- Templates needed

### 6. validate_input()
Validate if inputs (pesticides, fertilizers) are compliant.

**Use Case:** Before purchasing or applying farm inputs.

```python
result = await agent.validate_input(
    input_type="pesticide",
    product="Bacillus thuringiensis (Bt)",
    certification=CertificationStandard.ORGANIC_EU,
    additional_info={
        "concentration": "32,000 IU/mg",
        "target_pest": "Caterpillars"
    }
)
```

**Returns:**
- Approval status (approved/prohibited/restricted)
- Usage conditions and restrictions
- Pre-harvest interval (PHI)
- Maximum residue limits (MRL)
- Compliant alternatives if prohibited

### 7. calculate_waiting_period()
Calculate organic conversion waiting period.

**Use Case:** Planning transition to organic certification.

```python
from datetime import datetime

result = await agent.calculate_waiting_period(
    product="Synthetic NPK fertilizer",
    application_date=datetime(2022, 6, 15),
    certification=CertificationStandard.ORGANIC_USDA,
    crop_type="perennial_crops"
)
```

**Returns:**
- Calculated waiting period (days)
- Eligibility date for organic status
- Days remaining
- Requirements during conversion
- Allowed and prohibited practices

### 8. certification_roadmap()
Create step-by-step path to certification.

**Use Case:** Strategic planning for certification achievement.

```python
result = await agent.certification_roadmap(
    farm_data={
        "farm_name": "Green Valley Farm",
        "crops": ["Dates", "Wheat"],
        "size_hectares": 50,
        "current_practices": {
            "uses_synthetic_pesticides": True,
            "ipm_implemented": False
        }
    },
    target_certification=CertificationStandard.ORGANIC_USDA
)
```

**Returns:**
- Current compliance assessment
- Phased implementation plan (12+ months)
- Required investments and costs
- Training needs
- Timeline to certification
- Success metrics and KPIs

### 9. non_compliance_report()
Generate detailed non-compliance report with corrective actions.

**Use Case:** Documenting and addressing audit findings.

```python
result = await agent.non_compliance_report(
    farm_id="SA-FARM-001",
    issues=[
        {
            "category": "IPM",
            "control_point": "CB.5.1.1",
            "description": "IPM plan not documented",
            "severity": "critical"
        }
    ],
    certification=CertificationStandard.GLOBALGAP_IFA_V6
)
```

**Returns:**
- Non-conformity classification (critical/major/minor)
- Control point references
- Root cause analysis
- Corrective action requirements
- Deadlines and priorities
- Verification methods

### 10. compare_certifications()
Compare multiple certification standards.

**Use Case:** Deciding which certification(s) to pursue.

```python
result = await agent.compare_certifications(
    certifications=[
        CertificationStandard.GLOBALGAP_IFA_V6,
        CertificationStandard.ORGANIC_EU,
        CertificationStandard.SAUDI_GAP
    ],
    farm_context={
        "target_markets": ["EU", "GCC"],
        "crops": ["Tomatoes", "Cucumbers"],
        "budget": "Moderate"
    }
)
```

**Returns:**
- Requirements comparison
- Market advantages and pricing
- Cost comparison (certification + implementation)
- Timeline comparison
- Compatibility analysis
- Recommendations for farm context

## GlobalGAP Control Points Reference | مرجع نقاط المراقبة GlobalGAP

The agent includes comprehensive GlobalGAP IFA v6 control points:

### Site Management (AF.1.x.x)
- Site history and risk assessment
- Soil maps and management plans
- Previous land use documentation
- Conservation of natural vegetation

### Record Keeping (AF.3.x.x)
- Minimum 2-year record retention
- Traceability system implementation
- Internal self-assessment records
- Complaint handling procedures

### IPM (CB.5.x.x)
- IPM plan documentation
- Pest monitoring records
- Economic threshold levels
- Beneficial organism promotion
- Pesticide use as last resort

### Worker Safety (WH.x.x.x)
- Risk assessments for all activities
- PPE provision and use
- Worker training records
- First aid facilities
- No child labor policy

*See full list in the ComplianceAgent class definition.*

## Organic Certification Features | ميزات الشهادة العضوية

### Prohibited Inputs Database
The agent maintains lists of prohibited substances for organic farming:
- Synthetic chemical pesticides
- Synthetic nitrogen fertilizers
- GMO-derived products
- Synthetic growth regulators

### Approved Inputs Database
Pre-approved organic inputs:
- Neem oil, pyrethrum, Bt
- Compost, manure, green manure
- Rock phosphate, bone meal
- Beneficial insects

### Waiting Periods
- **EU Organic:** 2 years (annual), 3 years (perennial)
- **USDA Organic:** 3 years (all crops)

## Integration with SAHOOL System | التكامل مع نظام SAHOOL

The ComplianceAgent integrates with:
- **Farm Management System** - Real-time compliance checking for operations
- **Input Management** - Validate inputs before purchase/application
- **Document Management** - Track certification documentation
- **Audit Module** - Preparation and readiness assessment
- **Knowledge Base (RAG)** - Access to certification standards and regulations

## Best Practices | أفضل الممارسات

1. **Proactive Compliance Checking**
   - Check compliance BEFORE performing farm operations
   - Validate all inputs before purchase
   - Regular audit readiness assessments

2. **Documentation Management**
   - Use track_documentation() monthly
   - Maintain 2+ years of records
   - Organize by control point category

3. **Certification Planning**
   - Start with certification_roadmap()
   - Plan 12-18 months ahead
   - Budget for implementation costs

4. **Continuous Improvement**
   - Conduct internal audits quarterly
   - Address non-conformities immediately
   - Train workers regularly

## API Response Format | تنسيق استجابة API

All methods return a standardized response:

```python
{
    "agent": "compliance_agent",
    "role": "Certification Compliance Specialist",
    "response": "Detailed analysis and recommendations...",
    "confidence": 0.85
}
```

## Error Handling | معالجة الأخطاء

The agent handles:
- Missing or incomplete data
- Unknown certifications
- Invalid input types
- Database connectivity issues

## Performance | الأداء

- **Average response time:** 2-5 seconds
- **RAG retrieval:** Accesses certification standards knowledge base
- **Caching:** Reuses context for similar queries

## Future Enhancements | التحسينات المستقبلية

Planned features:
- Integration with certification body APIs
- Automated audit scheduling
- Real-time regulation updates
- Multi-language support (Arabic, English, Spanish)
- Blockchain-based certification tracking

## Support | الدعم

For questions or issues with the ComplianceAgent:
- Review this documentation
- Check compliance_agent_example.py for code examples
- Consult SAHOOL technical support

---

**File Location:** `/home/user/sahool-unified-v15-idp/apps/services/ai-advisor/src/agents/compliance_agent.py`

**Created:** December 29, 2025

**Version:** 1.0.0
