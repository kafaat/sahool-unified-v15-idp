# SAHOOL Frontend Governance Rules

# قواعد حوكمة الواجهات الأمامية

> Version: 16.0.0
> Last Updated: 2024-12-19

---

## 1. App Boundaries - حدود التطبيقات

### المسموح ✅

```
apps/web/       → المنتج الرئيسي (المزارعين + المستخدمين)
apps/admin/     → لوحة الإدارة (المشرفين + الدعم الفني)
apps/mobile/    → تطبيق الجوال
```

### الممنوع ❌

```
❌ إنشاء مجلد واجهة جديد في الجذر (frontend/, web_admin/, dashboard/)
❌ إنشاء app جديد بدون موافقة معمارية
❌ نسخ components بين web و admin
```

---

## 2. Import Rules - قواعد الاستيراد

### المسموح ✅

```typescript
// apps/web can import:
import { Button } from "@sahool/shared-ui";
import { useAuth } from "@sahool/shared-hooks";
import { api } from "@sahool/api-client";
import { tokens } from "@sahool/design-system";

// apps/admin can import:
import { Button } from "@sahool/shared-ui";
import { useAuth } from "@sahool/shared-hooks";
import { api } from "@sahool/api-client";
```

### الممنوع ❌

```typescript
// ❌ Cross-app imports
import { Component } from "../../../apps/admin/src/components";
import { hook } from "../../web/src/hooks";

// ❌ Direct service imports
import { calculateNDVI } from "../../../apps/services/satellite-service";

// ❌ Relative imports outside feature
import { util } from "../../../../shared/utils";
```

---

## 3. Package Responsibilities - مسؤوليات الحزم

| Package                 | المسؤولية                            | الممنوع              |
| ----------------------- | ------------------------------------ | -------------------- |
| `@sahool/design-system` | tokens, theme, colors, spacing, RTL  | components, hooks    |
| `@sahool/shared-ui`     | Button, Card, Modal, Table, MapShell | business logic       |
| `@sahool/shared-hooks`  | useAuth, useTenant, useMap, useQuery | API calls, decisions |
| `@sahool/api-client`    | HTTP client, interceptors, types     | UI code, React       |

### قاعدة ذهبية 🏆

```
shared-hooks = hooks تقنية فقط
لا قرارات زراعية، لا حسابات NDVI، لا منطق أعمال
```

---

## 4. Feature Folder Structure - بنية المجلدات

### البنية المطلوبة ✅

```
apps/web/src/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Auth group
│   ├── (dashboard)/       # Dashboard group
│   └── layout.tsx
├── features/              # Feature modules
│   ├── field-map/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api.ts
│   │   └── index.ts
│   ├── ndvi/
│   ├── advisor/
│   ├── reports/
│   └── alerts/
├── components/            # Shared app components
│   ├── layout/
│   └── common/
└── lib/                   # Utilities
```

### الممنوع ❌

```
❌ apps/web/src/components/NDVICalculator.tsx  (business logic in UI)
❌ apps/web/src/utils/yieldFormula.ts          (domain logic in frontend)
❌ apps/web/src/pages/                         (use app/ instead)
```

---

## 5. State Management - إدارة الحالة

### المعيار المعتمد

| نوع الحالة   | الأداة                 | الاستخدام                 |
| ------------ | ---------------------- | ------------------------- |
| Server State | TanStack Query         | API data, caching         |
| UI State     | Zustand                | modals, sidebars, filters |
| Form State   | React Hook Form        | forms, validation         |
| URL State    | nuqs / useSearchParams | filters, pagination       |

### الممنوع ❌

```typescript
// ❌ useState for server data
const [fields, setFields] = useState([]);
useEffect(() => {
  fetchFields().then(setFields);
}, []);

// ✅ Use TanStack Query
const { data: fields } = useQuery({
  queryKey: ["fields"],
  queryFn: fetchFields,
});
```

---

## 6. API Layer Rules - قواعد طبقة API

### المطلوب ✅

```typescript
// features/field-map/api.ts
import { api } from "@sahool/api-client";

export const fieldMapApi = {
  getFields: () => api.get("/v1/fields"),
  getFieldById: (id: string) => api.get(`/v1/fields/${id}`),
  updateField: (id: string, data: FieldUpdate) =>
    api.patch(`/v1/fields/${id}`, data),
};
```

### الممنوع ❌

```typescript
// ❌ Direct fetch in components
const Component = () => {
  const [data, setData] = useState();
  useEffect(() => {
    fetch("/api/fields")
      .then((r) => r.json())
      .then(setData);
  }, []);
};

// ❌ Axios in components
import axios from "axios";
const response = await axios.get("/api/fields");
```

---

## 7. Security Rules - قواعد الأمان

### المطلوب ✅

```typescript
// ✅ Use httpOnly cookies for auth tokens
// ✅ Never expose API keys in frontend
// ✅ Use environment variables for URLs
const apiUrl = process.env.NEXT_PUBLIC_API_URL;

// ✅ Validate all user inputs
import { z } from "zod";
const schema = z.object({ name: z.string().min(1) });
```

### الممنوع ❌

```typescript
// ❌ Hardcoded secrets
const API_KEY = "sk-1234567890";

// ❌ localStorage for tokens
localStorage.setItem("token", accessToken);

// ❌ Exposed internal URLs
const dbUrl = "postgresql://user:pass@localhost:5432/db";
```

---

## 8. RTL & i18n Rules - قواعد التعريب

### المطلوب ✅

```typescript
// ✅ Use logical properties
className="ms-4 me-2"  // margin-inline-start, margin-inline-end
className="ps-4 pe-2"  // padding-inline-start, padding-inline-end
className="start-0"    // inset-inline-start

// ✅ Use next-intl for translations
import { useTranslations } from 'next-intl';
const t = useTranslations('FieldMap');
return <h1>{t('title')}</h1>;
```

### الممنوع ❌

```typescript
// ❌ Physical properties for RTL-sensitive layouts
className="ml-4 mr-2"  // Use ms-4 me-2
className="left-0"     // Use start-0
className="text-left"  // Use text-start

// ❌ Hardcoded strings
return <h1>Field Map</h1>;  // Use translations
```

---

## 9. Performance Rules - قواعد الأداء

### المطلوب ✅

```typescript
// ✅ Lazy load features
const FieldMap = dynamic(() => import("@/features/field-map"), { ssr: false });

// ✅ Memoize expensive components
const MemoizedMap = memo(MapComponent);

// ✅ Use virtual lists for large data
import { useVirtualizer } from "@tanstack/react-virtual";
```

### الممنوع ❌

```typescript
// ❌ Import entire libraries
import * as L from 'leaflet';

// ❌ Render large lists without virtualization
{items.map(item => <Row key={item.id} />)}  // for 1000+ items
```

---

## 10. CI Enforcement - فرض القواعد

### Checks المطلوبة في CI

```yaml
frontend-guard:
  - lint: eslint apps/ packages/
  - typecheck: tsc --noEmit
  - build: next build
  - no-cross-imports: Check no apps/web → apps/admin
  - no-legacy-paths: Check no frontend/, web_admin/
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│                 SAHOOL Frontend Rules                    │
├─────────────────────────────────────────────────────────┤
│ ✅ Import from @sahool/* packages                       │
│ ✅ Feature folders with api.ts                          │
│ ✅ TanStack Query for server state                      │
│ ✅ RTL-safe CSS (ms-, me-, start-, end-)                │
│ ✅ Translations via next-intl                           │
├─────────────────────────────────────────────────────────┤
│ ❌ Cross-app imports                                     │
│ ❌ Business logic in components                          │
│ ❌ Direct fetch/axios in components                      │
│ ❌ localStorage for tokens                               │
│ ❌ Hardcoded strings                                     │
└─────────────────────────────────────────────────────────┘
```

---

## Governance Contacts

- **Architecture Owner**: Platform Team
- **Review Required For**: New apps, new packages, cross-app changes
- **Enforcement**: CI Pipeline + Code Review
