# SAHOOL Low-Code PoC Spec

## الهدف

تثبيت PoC آمن داخل SAHOOL يحوّل Design Tokens و OpenAPI operations المعتمدة إلى Flutter UI مولّد، بدون إدخال runtime خارجي أو حزم Flutter جديدة.

## المرحلة 1: Design Tokens

- المصدر الوحيد: `governance/design/design-tokens.yaml`.
- entrypoint المطلوب: `scripts/generate_themes.py`.
- المخرجات:
  - `shared/design-system/tokens.json`
  - `apps/mobile/lib/core/theme/generated/sahool_token_theme.dart`
  - `apps/mobile/lib/core/theme/generated_theme.dart` كمسار توافق للـ PoC.
- القيود:
  - لا لون خارج `design-tokens.yaml`.
  - لا خط خارج `typography.fonts`.
  - لا spacing خارج: `0, 4, 8, 12, 16, 24, 32, 48, 64` px (`0` مسموح فقط كقيمة reset).

## المرحلة 2: OpenAPI UI Generation

- entrypoint المطلوب: `scripts/openapi_form_generator.py`.
- لا توليد لأي operation خارج `schema-registry/approved_operations/`.
- POST / PUT / PATCH يولّد Form.
- GET list يولّد Card list أو DataTable.
- DataTable مرفوضة ما لم يعلن الـ spec pagination + filtering + sorting.
- generated widgets لا تنفّذ API calls مباشرة؛ تمرّر payload أو rows عبر parent-owned adapters.

## المرحلة 3: Security Gate

- القواعد المصدرية: `sahool_linter_rules.yaml`.
- كل generated UI file يجب أن يحتوي:
  - `// TENANT_ID_REQUIRED`
  - `// PERMISSION_CHECK_REQUIRED`
- ممنوع داخل generated code:
  - `print(...)`
  - `eval(...)`
  - hardcoded `http://` أو `https://`
  - imports من `package:dio/` أو `package:http/`
  - أي Flutter package جديد خارج Flutter SDK.

## أوامر التحقق

```bash
npm run lowcode:poc
npm run lint:sahool
```

## حدود الـ PoC

- Tenant Context الحالي static guard، والربط الديناميكي مع tenant-service مرحلة لاحقة.
- RBAC الحالي permission input guard، والربط مع Permission Service مرحلة لاحقة.
- unified response handling شرط للتوسع في API adapters، وليس مسموحاً للـ generated UI بتجاوز هذا الشرط عبر direct HTTP.
