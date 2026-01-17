# خطة المرحلة D - ترقية Next.js 16 و Tailwind CSS 4

# Phase D Plan - Next.js 16 & Tailwind CSS 4 Upgrades

**التاريخ:** 20 ديسمبر 2025
**المنصة:** SAHOOL Unified v15-IDP
**الحالة:** 📋 مخطط

---

## ⚠️ تحذير هام | Important Warning

هذه الترقيات تعتبر **عالية المخاطر** وتتطلب:

- اختبارًا شاملًا قبل الدمج
- مراجعة جميع الميزات المتأثرة
- تخصيص وقت كافٍ للتعامل مع المشاكل غير المتوقعة

---

## 1. نظرة عامة | Overview

### الترقيات المخططة

| الحزمة             | الحالي | المستهدف | مستوى المخاطر |
| ------------------ | ------ | -------- | ------------- |
| Next.js            | 15.1.2 | 16.x     | 🔴 مرتفع      |
| Tailwind CSS       | 3.4.17 | 4.x      | 🔴 مرتفع      |
| eslint-config-next | 15.1.2 | 16.x     | 🟡 متوسط      |

---

## 2. Next.js 16 - تفاصيل الترقية

### 2.1 المتطلبات الأساسية

```
✅ Node.js 20.9.0+ (لدينا: 22.21.1) - متوافق
✅ React 19.0.0 (لدينا: 19.0.0) - متوافق
```

### 2.2 الميزات الجديدة

| الميزة                      | الوصف                                               |
| --------------------------- | --------------------------------------------------- |
| **Cache Components**        | تخزين مؤقت صريح باستخدام "use cache" directive      |
| **Turbopack (Stable)**      | أسرع 10x في Fast Refresh، 2-5x في Production builds |
| **Next.js DevTools MCP**    | تكامل AI لتشخيص المشاكل                             |
| **proxy.ts**                | بديل middleware.ts مع Node.js runtime               |
| **Incremental Prefetching** | تحسين prefetch للروابط                              |

### 2.3 التغييرات الكسرية (Breaking Changes)

#### 2.3.1 middleware.ts → proxy.ts

**الملفات المتأثرة:**

- `apps/admin/src/middleware.ts`

**التغييرات المطلوبة:**

```typescript
// قبل (Next.js 15)
// apps/admin/src/middleware.ts
export function middleware(request: NextRequest) { ... }

// بعد (Next.js 16)
// apps/admin/src/proxy.ts
export function proxy(request: NextRequest) { ... }
```

**خطة الترحيل:**

1. إعادة تسمية الملف: `middleware.ts` → `proxy.ts`
2. تغيير اسم الدالة: `middleware` → `proxy`
3. تحديث أي imports أو references

#### 2.3.2 async params & searchParams

**الملفات المتأثرة:** جميع صفحات Server Components التي تستخدم params

**التغييرات المطلوبة:**

```typescript
// قبل
export default function Page({ params }: { params: { id: string } }) {
  return <div>{params.id}</div>
}

// بعد
export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <div>{id}</div>
}
```

**تحليل الحالة الحالية:**

- `apps/admin/src/app/diseases/page.tsx` - ✅ يستخدم `useSearchParams()` (client-side hook) - لا يحتاج تغيير
- `apps/admin/src/app/login/page.tsx` - ✅ يستخدم `useSearchParams()` (client-side hook) - لا يحتاج تغيير

**الفحص المطلوب:** البحث عن صفحات تستخدم `params` أو `searchParams` كـ props

#### 2.3.3 إزالة دعم AMP

**الحالة:** ✅ لا نستخدم AMP في المشروع

### 2.4 خطوات الترقية

```bash
# الخطوة 1: تحديث الحزم
npm install next@16 eslint-config-next@16

# الخطوة 2: تشغيل codemod (اختياري)
npx @next/codemod@latest upgrade

# الخطوة 3: إعادة تسمية middleware → proxy
mv apps/admin/src/middleware.ts apps/admin/src/proxy.ts

# الخطوة 4: تحديث الدالة
# تغيير export function middleware → export function proxy

# الخطوة 5: اختبار البناء
npm run build
```

---

## 3. Tailwind CSS 4 - تفاصيل الترقية

### 3.1 المتطلبات الأساسية

```
✅ Node.js 20+ (لدينا: 22.21.1) - متوافق
⚠️ متصفحات حديثة فقط: Safari 16.4+, Chrome 111+, Firefox 128+
```

### 3.2 الميزات الجديدة

| الميزة                     | الوصف                                        |
| -------------------------- | -------------------------------------------- |
| **Oxide Engine (Rust)**    | أسرع 5x في full builds، 100x+ في incremental |
| **CSS-First Config**       | إعدادات CSS بدلاً من JavaScript              |
| **Modern CSS**             | cascade layers, @property, color-mix()       |
| **Auto Content Detection** | لا حاجة لتحديد مسارات content                |

### 3.3 التغييرات الكسرية (Breaking Changes)

#### 3.3.1 Import Syntax

**الملفات المتأثرة:**

- `apps/web/src/app/globals.css`
- `apps/admin/src/app/globals.css`

**التغييرات المطلوبة:**

```css
/* قبل (Tailwind 3) */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* بعد (Tailwind 4) */
@import "tailwindcss";
```

#### 3.3.2 Configuration Migration

**الملفات المتأثرة:**

- `packages/tailwind-config/index.js` (shared config)
- `apps/web/tailwind.config.ts`
- `apps/admin/tailwind.config.ts`

**التغييرات المطلوبة:**

```css
/* قبل: tailwind.config.ts */
module.exports = {
  theme: {
    extend: {
      colors: {
        sahool: {
          500: "#22c55e";
        }
      }
    }
  }
}

/* بعد: في globals.css */
@import "tailwindcss";

@theme {
  --color-sahool-500: #22c55e;
}
```

#### 3.3.3 Breaking Utility Changes

| Utility      | Tailwind 3 | Tailwind 4   |
| ------------ | ---------- | ------------ |
| border color | gray-200   | currentColor |
| ring width   | 3px        | 1px          |
| ring color   | blue-500   | currentColor |
| placeholder  | gray-400   | 50% opacity  |

**التأثير:** يجب مراجعة جميع استخدامات `border`, `ring`, `placeholder` في الكود

#### 3.3.4 حزم منفصلة

```bash
# Tailwind 4 يتطلب تثبيت PostCSS plugin بشكل منفصل
npm install tailwindcss @tailwindcss/postcss

# تحديث postcss.config.js
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
```

### 3.4 ملاحظة مهمة: CSS Preprocessors

⛔ **Tailwind 4 غير متوافق مع Sass/Less/Stylus**

**الحالة الحالية:** ✅ نستخدم CSS عادي - لا توجد مشكلة

### 3.5 خطوات الترقية

```bash
# الخطوة 1: تشغيل أداة الترقية التلقائية
npx @tailwindcss/upgrade

# الخطوة 2: تحديث الحزم يدوياً إذا لزم الأمر
npm install tailwindcss@4 @tailwindcss/postcss

# الخطوة 3: مراجعة التغييرات التلقائية

# الخطوة 4: اختبار البناء
npm run build

# الخطوة 5: مراجعة visual regression للـ UI
```

---

## 4. استراتيجية الترقية المقترحة

### الخيار A: ترقية تدريجية (موصى به) ⭐

```
الأسبوع 1: Next.js 16 فقط
├── ترقية Next.js
├── تحويل middleware → proxy
├── اختبار شامل
└── دمج

الأسبوع 2: Tailwind 4
├── ترقية Tailwind
├── تحويل configs إلى CSS
├── إصلاح visual regressions
└── دمج
```

**المميزات:**

- عزل المشاكل
- rollback أسهل
- اختبار مركز

### الخيار B: ترقية متزامنة

**غير موصى به** بسبب:

- صعوبة تشخيص المشاكل
- rollback معقد
- احتمال تعارضات

---

## 5. قائمة التحقق قبل الترقية

### Next.js 16 Checklist

- [ ] فحص جميع ملفات `middleware.ts`
- [ ] فحص صفحات Server Components التي تستخدم `params`
- [ ] التأكد من عدم استخدام AMP
- [ ] مراجعة استخدامات `next/server` imports
- [ ] إنشاء feature branch للترقية
- [ ] تشغيل test suite قبل الترقية

### Tailwind 4 Checklist

- [ ] إحصاء ملفات CSS التي تستخدم `@tailwind`
- [ ] مراجعة `tailwind.config.*` files
- [ ] فحص استخدامات `border`, `ring`, `placeholder`
- [ ] التأكد من دعم المتصفحات المستهدفة
- [ ] إنشاء feature branch للترقية
- [ ] تحضير visual regression tests

---

## 6. المخاطر والتخفيف

| المخاطر                            | الاحتمال | التأثير | التخفيف                       |
| ---------------------------------- | -------- | ------- | ----------------------------- |
| middleware breakage                | متوسط    | مرتفع   | اختبار auth flow شامل         |
| UI visual regressions              | مرتفع    | متوسط   | مقارنة screenshots            |
| Third-party plugin incompatibility | منخفض    | متوسط   | فحص compatibility قبل الترقية |
| Build failures                     | متوسط    | مرتفع   | feature branch + CI checks    |

---

## 7. التوصيات

### 7.1 توقيت الترقية

🟡 **التوصية:** تأجيل الترقية إلى Q1 2026

**الأسباب:**

1. Next.js 16 صدر حديثاً (أكتوبر 2025) - ينتظر استقرار
2. Tailwind 4 يتطلب تغييرات واسعة في الـ config
3. المشروع في حالة مستقرة حالياً
4. الترقيات الحالية (React 19, ESLint 9) تحتاج اختباراً

### 7.2 إذا كانت الترقية عاجلة

1. ابدأ بـ Next.js 16 فقط
2. انتظر أسبوعًا للاستقرار
3. ثم Tailwind 4 في PR منفصل

### 7.3 البدائل المؤقتة

- **للأمان:** ترقية Next.js إلى 15.2.x (patch) بدلاً من 16
- **للأداء:** تفعيل Turbopack في Next.js 15

---

## 8. المراجع | References

### Next.js 16

- [Next.js 16 Blog](https://nextjs.org/blog/next-16)
- [Next.js 16 Migration](https://nextjs.org/docs/app/building-your-application/upgrading)
- [InfoQ: Next.js 16 Release](https://www.infoq.com/news/2025/12/nextjs-16-release/)

### Tailwind CSS 4

- [Tailwind CSS 4.0 Blog](https://tailwindcss.com/blog/tailwindcss-v4)
- [Official Upgrade Guide](https://tailwindcss.com/docs/upgrade-guide)
- [Migration Guide (DEV Community)](https://dev.to/kasenda/whats-new-and-migration-guide-tailwind-css-v40-3kag)

---

_تم إنشاء هذا التقرير بواسطة Claude في 20 ديسمبر 2025_
