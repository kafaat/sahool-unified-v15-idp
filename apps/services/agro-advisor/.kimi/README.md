# Agro Advisor - Kimi EC Repair Agent
# وكيل إصلاح EC للمستشار الزراعي

## Overview | نظرة عامة

This specialized agent detects and helps fix a critical issue in agricultural advisory code: the misuse of EC (Electrical Conductivity) as a nutrient indicator.

هذا الوكيل المتخصص يكتشف ويساعد في إصلاح مشكلة حرجة في كود الاستشارات الزراعية: سوء استخدام التوصيل الكهربائي (EC) كمؤشر للمغذيات.

## Research Background | الخلفية البحثية

**Research Paper 2**: EC ≠ NPK Correlation Study

### Key Findings
- **EC (Electrical Conductivity)** measures soil **salinity**, not nutrient content
- EC cannot be used to accurately determine NPK (Nitrogen, Phosphorus, Potassium) levels
- **Common mistake**: Using EC values in fertilizer recommendation calculations
- **Correct approach**: Use actual laboratory nutrient analysis (mg/kg or ppm)

### النتائج الرئيسية
- **EC (التوصيل الكهربائي)** يقيس **ملوحة التربة**، وليس محتوى المغذيات
- لا يمكن استخدام EC لتحديد مستويات NPK بدقة
- **الخطأ الشائع**: استخدام قيم EC في حسابات توصيات الأسمدة
- **النهج الصحيح**: استخدام التحليل المختبري الفعلي للمغذيات (mg/kg أو ppm)

## Usage | الاستخدام

### Scan for EC Misuse

```bash
# From project root
python apps/services/agro-advisor/.kimi/ec_repair_agent.py --scan

# Export results to JSON
python apps/services/agro-advisor/.kimi/ec_repair_agent.py --scan --export-json /tmp/ec-issues.json
```

### Integration with Kimi Repair Workflow

This agent is automatically invoked when the main Kimi repair workflow detects changes in the agro-advisor service:

```yaml
# In .kimi-agents/repair-agent-config.yaml
monitored_projects:
  - path: "apps/services/agro-advisor"
    priority: "high"
    specialized_agent: "agro_advisor_agent"
```

## Detected Patterns | الأنماط المكتشفة

### CRITICAL Issues

1. **Direct EC to Nutrient Calculation**
   ```python
   # ❌ WRONG
   ec_value * nutrient_factor
   ```

2. **EC for Fertilizer Calculation**
   ```python
   # ❌ WRONG
   def calculate_fertilizer(ec):
       if ec < 0.5:
           return {"N": 100}
   ```

3. **Soil EC for NPK Determination**
   ```python
   # ❌ WRONG
   if soil_ec > 2.0:
       nitrogen = "high"
   ```

### HIGH Issues

1. **EC in Nutrient Function Names**
   ```python
   # ⚠️ SUSPICIOUS
   def calculate_nutrient_from_ec(ec_value):
       ...
   ```

## Correct Implementation | التنفيذ الصحيح

### ✅ Use Lab Nutrient Results

```python
def calculate_fertilizer(lab_results: dict):
    """
    Calculate fertilizer based on actual lab nutrient analysis.
    
    Args:
        lab_results: Dictionary with nutrient levels in mg/kg or ppm
            Required keys: 
            - nitrogen_mg_kg
            - phosphorus_mg_kg
            - potassium_mg_kg
    
    Returns:
        Dictionary with fertilizer recommendations (kg/ha)
    """
    # Nitrogen recommendation
    if lab_results.get('nitrogen_mg_kg', 0) < 60:
        n_rec = 100  # kg/ha
    elif lab_results.get('nitrogen_mg_kg', 0) < 90:
        n_rec = 75
    else:
        n_rec = 50
    
    # Phosphorus recommendation
    if lab_results.get('phosphorus_mg_kg', 0) < 15:
        p_rec = 50
    elif lab_results.get('phosphorus_mg_kg', 0) < 25:
        p_rec = 30
    else:
        p_rec = 20
    
    # Potassium recommendation
    if lab_results.get('potassium_mg_kg', 0) < 150:
        k_rec = 80
    elif lab_results.get('potassium_mg_kg', 0) < 250:
        k_rec = 60
    else:
        k_rec = 40
    
    return {
        "N": n_rec,
        "P": p_rec,
        "K": k_rec,
        "unit": "kg/ha"
    }
```

### EC Can Still Be Used For Salinity

```python
def assess_soil_salinity(ec_value: float) -> dict:
    """
    Assess soil salinity based on EC.
    
    This is the CORRECT use of EC - for salinity, not nutrients.
    
    Args:
        ec_value: EC value in dS/m
    
    Returns:
        Salinity assessment
    """
    if ec_value < 2.0:
        return {
            "level": "low",
            "level_ar": "منخفض",
            "impact": "No salinity problems"
        }
    elif ec_value < 4.0:
        return {
            "level": "medium",
            "level_ar": "متوسط",
            "impact": "Yields of salt-sensitive crops may be reduced"
        }
    elif ec_value < 8.0:
        return {
            "level": "high",
            "level_ar": "عالي",
            "impact": "Only salt-tolerant crops yield satisfactorily"
        }
    else:
        return {
            "level": "very_high",
            "level_ar": "عالي جداً",
            "impact": "Only very salt-tolerant crops yield satisfactorily"
        }
```

## Output Format | تنسيق الإخراج

### Console Output

```
🔍 Scanning apps/services/agro-advisor for EC misuse...
   فحص apps/services/agro-advisor لسوء استخدام EC...

✅ Scan complete. Found 3 issues.
   اكتمل الفحص. تم العثور على 3 مشكلة.

================================================================================
🔍 EC Misuse Detection Report | تقرير اكتشاف سوء استخدام EC
================================================================================

CRITICAL: 2 issue(s)

  1. apps/services/agro-advisor/src/fertilizer.py:45
     Using EC for fertilizer calculation
     استخدام EC لحساب الأسمدة
     Pattern: ec fertilizer calculat

     Code:
       def calculate_fertilizer(ec_value):
           if ec_value < 0.5:
               return {"N": 100, "P": 50}

HIGH: 1 issue(s)

  1. apps/services/agro-advisor/src/nutrient.py:12
     EC parameter in calculation function
     معامل EC في دالة الحساب
     Pattern: def calculate_npk(ec

     Code:
       def calculate_npk(ec, crop_type):
           # ...

================================================================================
Total: 3 issues found
================================================================================
```

### JSON Output

```json
{
  "agent": "AgroAdvisorECRepairAgent",
  "version": "16.0.0",
  "service": "apps/services/agro-advisor",
  "total_issues": 3,
  "issues": [
    {
      "file": "apps/services/agro-advisor/src/fertilizer.py",
      "line": 45,
      "severity": "CRITICAL",
      "type": "ec_as_nutrient",
      "message": "Using EC for fertilizer calculation",
      "message_ar": "استخدام EC لحساب الأسمدة",
      "pattern": "ec fertilizer calculat",
      "snippet": "def calculate_fertilizer(ec_value):\n    if ec_value < 0.5:\n        return {\"N\": 100, \"P\": 50}"
    }
  ]
}
```

## Integration with Main Workflow | التكامل مع سير العمل الرئيسي

This agent is part of the Kimi Repair Agent ecosystem and integrates with:

1. **Main Scan Script**: `scripts/kimi-repair-scan.sh`
2. **GitHub Actions**: `.github/workflows/kimi-repair.yml`
3. **Kimi Configuration**: `.kimi-agents/repair-agent-config.yaml`

---

**Version**: 16.0.0  
**Research**: Based on Research Paper 2 - EC ≠ NPK Correlation Study  
**Maintainer**: SAHOOL Platform Team
