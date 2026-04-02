# Compliance Automation Policy

> سياسة أتمتة الامتثال | Compliance Automation Policy

**Version**: 1.0.0
**Status**: Approved
**Last Updated**: 2026-04-02

## Purpose | الهدف

This policy defines how compliance checks (GlobalGAP IFA v6, pesticide regulations, GDPR) are automated, monitored, and reported across the SAHOOL platform.

تحدد هذه السياسة كيفية أتمتة فحوصات الامتثال (GlobalGAP IFA v6، لوائح المبيدات، GDPR) ومراقبتها والإبلاغ عنها عبر منصة سهول.

---

## Compliance Frameworks | أطر الامتثال

### 1. GlobalGAP IFA v6 (Integrated Farm Assurance)

| Component | Module | Status |
|-----------|--------|--------|
| **Checklist Engine** | `shared/globalgap/ifa_v6_checklist.py` | ✅ Implemented |
| **Compliance Levels** | MAJOR_MUST, MINOR_MUST | ✅ Defined |
| **Evidence Types** | DOCUMENT, OBSERVATION, TEST_RESULT | ✅ Defined |
| **API Endpoints** | `/api/v1/compliance/globalgap/*` | Required |
| **Automated Scoring** | Percentage-based compliance calculation | Required |
| **Evidence Storage** | Linked blob storage for audit documents | Required |
| **Report Generation** | PDF/CSV export for auditors and certifiers | Required |

**Automation Requirements:**
- Compliance checks MUST be triggerable via API for tenant workflows
- Non-compliance MUST emit NATS events: `sahool.compliance.violation`
- Critical violations MUST generate alerts via `alert-service`
- Evidence attachments MUST be stored with versioning and immutability

### 2. Pesticide Compliance

| Component | Module | Status |
|-----------|--------|--------|
| **PHI Checker** | `shared/pesticide_compliance/checker.py` | ✅ Implemented |
| **REI Checker** | `shared/pesticide_compliance/checker.py` | ✅ Implemented |
| **Tank Mix Validation** | `shared/pesticide_compliance/checker.py` | ✅ Implemented |
| **Spray Drift Assessment** | `shared/pesticide_compliance/checker.py` | ✅ Implemented |
| **PPE Requirements** | `shared/pesticide_compliance/database.py` | ✅ Defined |
| **Automated Alerts** | Pre-harvest interval countdown alerts | Required |
| **Application Logging** | Record all pesticide applications with audit trail | Required |

**Automation Requirements:**
- PHI violations MUST block harvest scheduling in `task-service`
- REI violations MUST generate worker safety alerts
- All pesticide applications MUST be logged to audit trail with: product, rate, field, applicator, weather conditions

### 3. GDPR / Data Protection

| Component | Description | Status |
|-----------|-------------|--------|
| **Data Classification** | Public, Internal, Sensitive, Restricted levels | ✅ Defined in `docs/security/DATA_CLASSIFICATION.md` |
| **Consent Management** | `POST /gdpr/consent` endpoint for opt-in/opt-out | Required |
| **Right of Access** | `GET /gdpr/data-export/{user_id}` | Required |
| **Right of Erasure** | `DELETE /gdpr/data/{user_id}` with audit logging | Required |
| **Data Portability** | Export user data in machine-readable format (JSON/CSV) | Required |
| **Breach Notification** | Automated alerting within 72 hours of detected breach | Required |

---

## Audit Trail Requirements | متطلبات سجل التدقيق

All compliance-related actions MUST be logged to `shared/audit_trail/`:

| Event | Required Fields |
|-------|----------------|
| **Compliance Check** | check_type, tenant_id, field_id, result, score, timestamp |
| **Violation Detected** | violation_type, severity, field_id, details, remediation_deadline |
| **Evidence Uploaded** | evidence_type, checklist_item, file_hash, uploaded_by |
| **Report Generated** | report_type, framework, date_range, generated_by |
| **GDPR Request** | request_type, user_id, status, processed_at |

---

## Compliance Reporting | تقارير الامتثال

### Automated Reports

| Report | Frequency | Format | Audience |
|--------|-----------|--------|----------|
| **GlobalGAP Readiness** | Monthly | PDF/CSV | Farm managers, auditors |
| **Pesticide Application Log** | Per-season | PDF | Regulatory authorities |
| **PHI Compliance Status** | Weekly | Dashboard | Field supervisors |
| **GDPR Data Processing Register** | Quarterly | PDF | Data Protection Officer |
| **Security Audit Summary** | Monthly | PDF | CISO, compliance team |

### NATS Events for Compliance

| Event Subject | Trigger |
|---------------|---------|
| `sahool.compliance.check_completed` | Compliance check finished |
| `sahool.compliance.violation` | Violation detected |
| `sahool.compliance.violation_resolved` | Violation remediated |
| `sahool.compliance.report_generated` | Report created |
| `sahool.gdpr.request_received` | GDPR data request |
| `sahool.gdpr.request_completed` | GDPR request processed |

---

## Enforcement | التنفيذ

1. **CI Guard**: `governance-validation.yml` checks compliance module integration
2. **Runtime**: Compliance checks run on schedule via `batch_operations`
3. **Alerts**: Violations trigger notifications via `notification-service`
4. **Dashboard**: Compliance status visible in admin portal

---

## Related | مراجع ذات صلة

- [GlobalGAP Module](../../shared/globalgap/)
- [Pesticide Compliance Module](../../shared/pesticide_compliance/)
- [Audit Trail Module](../../shared/audit_trail/)
- [Security Policies](../../infrastructure/security/security-policies.yaml)
- [Data Classification](../../docs/security/DATA_CLASSIFICATION.md)
