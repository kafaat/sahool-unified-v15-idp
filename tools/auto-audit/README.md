# SAHOOL Auto Audit Tools

مجموعة شاملة من أدوات التدقيق التلقائي لمنصة SAHOOL الزراعية الذكية.

## نظرة عامة

تتضمن هذه المجموعة أدوات متقدمة لـ:

1. **تحليل سجلات التدقيق** (Audit Log Analyzer) - تحليل إحصائي واكتشاف الأنماط
2. **التحقق من سلسلة التجزئة** (Hash Chain Validator) - التحقق من سلامة البيانات
3. **إنشاء تقارير الامتثال** (Compliance Reporter) - تقارير GDPR, SOC2, ISO27001
4. **كشف الأنماط الشاذة** (Anomaly Detector) - كشف التهديدات والسلوك المشبوه
5. **تصدير بيانات التدقيق** (Audit Data Exporter) - تصدير لأنظمة SIEM المختلفة

## التثبيت

الأدوات مدمجة مع مشروع SAHOOL ولا تحتاج تثبيت منفصل.

```bash
# التأكد من وجود التبعيات
pip install -e ".[base,observability]"
```

## الاستخدام

### واجهة سطر الأوامر (CLI)

```bash
# تشغيل تحليل كامل
python -m tools.auto-audit full-audit -i logs.json -t tenant-123 -o reports/

# تحليل سجلات التدقيق
python -m tools.auto-audit analyze -i logs.json -t tenant-123

# التحقق من سلسلة التجزئة
python -m tools.auto-audit validate -i logs.json --recovery

# إنشاء تقرير امتثال GDPR
python -m tools.auto-audit compliance -i logs.json -t tenant-123 -f gdpr

# كشف الأنماط الشاذة
python -m tools.auto-audit detect -i logs.json -t tenant-123 -w 48

# تصدير للتكامل مع SIEM
python -m tools.auto-audit export -i logs.json -f splunk -o audit.splunk
```

### الاستخدام البرمجي

```python
from tools.auto_audit import (
    AuditLogAnalyzer,
    HashChainValidator,
    ComplianceReporter,
    AuditAnomalyDetector,
    AuditDataExporter,
)

# تحليل السجلات
analyzer = AuditLogAnalyzer()
analyzer.load_from_file("logs.json")
report = analyzer.analyze(tenant_id="tenant-123")
print(f"Risk indicators: {len(report.risk_indicators)}")

# التحقق من السلامة
validator = HashChainValidator()
validator.load_from_file("logs.json")
validation = validator.validate()
print(f"Chain integrity: {validation.chain_integrity}%")

# تقرير الامتثال
reporter = ComplianceReporter()
reporter.load_from_file("logs.json")
compliance = reporter.generate_report(
    framework=ComplianceFramework.GDPR,
    tenant_id="tenant-123"
)
print(f"Compliance score: {compliance.overall_score}%")

# كشف الأنماط الشاذة
detector = AuditAnomalyDetector()
detector.load_from_file("logs.json")
anomalies = detector.detect(tenant_id="tenant-123")
print(f"Threat score: {anomalies.threat_score}/100")
```

## الأدوات المتاحة

### 1. Audit Log Analyzer (محلل سجلات التدقيق)

تحليل شامل لسجلات التدقيق يتضمن:

- **التحليل الإحصائي**: توزيع الأحداث، النشاط الزمني
- **اكتشاف الأنماط**: تحديد السلوكيات المتكررة
- **تحليل الفاعلين**: تصنيف المستخدمين حسب النشاط
- **مؤشرات المخاطر**: تحديد الإجراءات الحساسة
- **تقارير مفصلة**: Markdown أو JSON

**الميزات:**

- تحليل توزيع الإجراءات
- رسم بياني للنشاط الزمني
- أفضل 20 فاعل/إجراء/مورد
- كشف النشاط خارج ساعات العمل
- تصنيف مستوى النشاط

### 2. Hash Chain Validator (محقق سلسلة التجزئة)

التحقق من سلامة البيانات وعدم التلاعب:

- **التحقق من التجزئة**: مقارنة SHA-256
- **كشف الكسور**: تحديد نقاط انقطاع السلسلة
- **التحقق المتوازي**: للمجموعات الكبيرة
- **تقرير الاستعادة**: اقتراحات للإصلاح
- **تحليل الفجوات الزمنية**: كشف الثغرات

**الميزات:**

- التحقق من prev_hash و entry_hash
- كشف التلاعب المحتمل
- نقاط استعادة آمنة
- تقرير جنائي رقمي

### 3. Compliance Reporter (مولد تقارير الامتثال)

تقييم الامتثال للمعايير الدولية:

- **GDPR**: المواد 5, 6, 15, 17, 20, 25, 30, 32, 33
- **SOC 2 Type II**: معايير CC1-CC9
- **ISO 27001:2022**: ملحق A (A.5 - A.18)

**الميزات:**

- نقاط امتثال لكل إطار
- جمع الأدلة التلقائي
- تحديد الثغرات
- توصيات الإصلاح
- ملخص تنفيذي

### 4. Anomaly Detector (كاشف الأنماط الشاذة)

كشف التهديدات باستخدام خوارزميات متقدمة:

**أنواع الكشف:**

- **Volume Spike/Drop**: ارتفاع/انخفاض غير طبيعي
- **Unusual Time**: نشاط خارج الأوقات المعتادة
- **Behavioral Change**: تغير في نمط السلوك
- **Velocity Anomaly**: سرعة تنفيذ غير طبيعية
- **Privilege Escalation**: محاولات رفع الصلاحيات
- **Data Exfiltration**: تسريب بيانات محتمل
- **Brute Force**: هجمات القوة الغاشمة

**الميزات:**

- تحليل Z-Score و IQR
- بناء خط أساس سلوكي
- نقاط تهديد (0-100)
- تصنيف الخطورة
- توصيات الاستجابة

### 5. Audit Data Exporter (مصدّر بيانات التدقيق)

تصدير البيانات بتنسيقات متعددة:

**التنسيقات المدعومة:**

- **JSON**: تنسيق قياسي
- **JSONL**: سطر واحد لكل سجل
- **CSV**: للجداول والتحليل
- **Splunk HEC**: تكامل Splunk
- **ELK/Elasticsearch**: تنسيق bulk
- **CEF**: Common Event Format
- **Syslog**: RFC 5424

**الميزات:**

- تنقية البيانات الحساسة (PII)
- ضغط GZIP
- تصدير تزايدي
- نقاط تفتيش للاستمرارية
- حساب checksum

## صيغة ملف الإدخال

يجب أن يكون ملف الإدخال بتنسيق JSON يحتوي على مصفوفة من سجلات التدقيق:

```json
[
  {
    "id": "uuid-here",
    "tenant_id": "tenant-uuid",
    "actor_id": "user-uuid",
    "actor_type": "user",
    "action": "field.create",
    "resource_type": "field",
    "resource_id": "field-123",
    "correlation_id": "request-uuid",
    "ip": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "details_json": "{\"name\": \"Field 1\"}",
    "prev_hash": "abc123...",
    "entry_hash": "def456...",
    "created_at": "2025-01-05T10:30:00Z"
  }
]
```

## التكوين

يمكن تكوين الأدوات عبر متغيرات البيئة:

```bash
# قاعدة البيانات
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=sahool
export POSTGRES_USER=sahool
export POSTGRES_PASSWORD=secret

# الأدوات
export SAHOOL_ENV=production
export AUDIT_OUTPUT_DIR=audit_reports
export AUDIT_LOG_LEVEL=INFO
```

أو برمجياً:

```python
from tools.auto_audit.config import AuditToolsConfig, set_config

config = AuditToolsConfig(
    output_dir=Path("/var/log/audit"),
    log_level="DEBUG",
)
set_config(config)
```

## الإخراج

### تقرير التحليل الكامل

عند تشغيل `full-audit`، يتم إنشاء:

```
audit_reports/
├── 00_audit_summary_20250105_103000.md     # ملخص شامل
├── 01_hashchain_validation_20250105_103000.md  # تحقق السلامة
├── 02_analysis_report_20250105_103000.md   # تحليل مفصل
├── 03_compliance_report_20250105_103000.md # تقرير الامتثال
└── 04_anomaly_report_20250105_103000.md    # كشف الأنماط الشاذة
```

## أمثلة الاستخدام

### سيناريو 1: تدقيق يومي

```bash
#!/bin/bash
# daily_audit.sh

DATE=$(date +%Y%m%d)
OUTPUT_DIR="/var/log/sahool/audit/$DATE"

# تشغيل التدقيق الكامل
python -m tools.auto-audit full-audit \
    -i /var/log/sahool/audit_logs.json \
    -t production-tenant \
    -o "$OUTPUT_DIR"

# إرسال التنبيهات إذا وجدت تهديدات
if [ $? -ne 0 ]; then
    # إرسال بريد أو إشعار
    echo "Critical threats detected!"
fi
```

### سيناريو 2: تصدير لـ SIEM

```bash
# تصدير يومي لـ Splunk
python -m tools.auto-audit export \
    -i /var/log/sahool/audit_logs.json \
    -f splunk \
    -o /var/log/splunk/sahool_audit.json \
    --redact standard \
    --compress
```

### سيناريو 3: تحقق الامتثال قبل المراجعة

```bash
# تقرير GDPR قبل مراجعة الامتثال
python -m tools.auto-audit compliance \
    -i audit_logs.json \
    -t tenant-123 \
    -f gdpr \
    -o gdpr_assessment.md
```

## التكامل مع CI/CD

```yaml
# .github/workflows/audit.yml
name: Security Audit

on:
  schedule:
    - cron: "0 2 * * *" # يومياً الساعة 2 صباحاً

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Full Audit
        run: |
          python -m tools.auto-audit full-audit \
            -i ${{ secrets.AUDIT_LOG_PATH }} \
            -t ${{ secrets.TENANT_ID }} \
            -o audit_reports/

      - name: Upload Reports
        uses: actions/upload-artifact@v4
        with:
          name: audit-reports
          path: audit_reports/
```

## المساهمة

1. إنشاء فرع جديد
2. إضافة الميزة/الإصلاح
3. كتابة الاختبارات
4. فتح Pull Request

## الترخيص

ملكية خاصة - KAFAAT Team

---

_تم إنشاء هذه الأدوات كجزء من مشروع SAHOOL للزراعة الذكية_
