# i18n Quick Start Guide for SAHOOL Web App

## TL;DR

The @sahool/i18n package is now integrated. Use `useTranslations()` hook to get translations in your components.

```typescript
'use client';
import { useTranslations } from 'next-intl';

export function MyComponent() {
  const t = useTranslations('common');
  return <button>{t('save')}</button>;
}
```

## Available Namespaces

```typescript
const tCommon = useTranslations('common');      // Buttons, labels, general UI
const tAuth = useTranslations('auth');          // Login, logout, authentication
const tNav = useTranslations('nav');            // Navigation items
const tDashboard = useTranslations('dashboard'); // Dashboard specific
const tFields = useTranslations('fields');       // Field management
const tAlerts = useTranslations('alerts');       // Alert messages
const tErrors = useTranslations('errors');       // Error messages
```

## Common Translation Keys

### Buttons & Actions (`common`)
```typescript
t('save')       // "حفظ" / "Save"
t('delete')     // "حذف" / "Delete"
t('edit')       // "تعديل" / "Edit"
t('add')        // "إضافة" / "Add"
t('cancel')     // "إلغاء" / "Cancel"
t('confirm')    // "تأكيد" / "Confirm"
t('submit')     // "إرسال" / "Submit"
t('search')     // "بحث" / "Search"
```

### Navigation (`nav`)
```typescript
t('dashboard')  // "لوحة التحكم" / "Dashboard"
t('fields')     // "الحقول" / "Fields"
t('farms')      // "المزارع" / "Farms"
t('settings')   // "الإعدادات" / "Settings"
t('users')      // "المستخدمين" / "Users"
```

### States (`common`)
```typescript
t('loading')    // "جاري التحميل..." / "Loading..."
t('error')      // "حدث خطأ" / "An error occurred"
t('noData')     // "لا توجد بيانات" / "No data available"
```

## Locale Detection & Switching

### Get Current Locale
```typescript
import { useLocale } from 'next-intl';

const locale = useLocale(); // 'ar' or 'en'
```

### Add Locale Switcher
```typescript
import { LocaleSwitcher } from '@/components/common/LocaleSwitcher';

<header>
  <LocaleSwitcher />
</header>
```

## RTL/LTR Support

```typescript
import { getDirection } from '@sahool/i18n';

const direction = getDirection(locale); // 'rtl' or 'ltr'
```

## Adding New Translations

1. Edit `/packages/i18n/src/locales/ar.json`
2. Edit `/packages/i18n/src/locales/en.json`
3. Use the same structure in both files

Example:
```json
// ar.json
{
  "myFeature": {
    "title": "عنوان",
    "subtitle": "عنوان فرعي"
  }
}

// en.json
{
  "myFeature": {
    "title": "Title",
    "subtitle": "Subtitle"
  }
}
```

Then use in component:
```typescript
const t = useTranslations('myFeature');
<h1>{t('title')}</h1>
<h2>{t('subtitle')}</h2>
```

## Dynamic Values

```typescript
// In locale file:
{
  "welcome": "مرحباً {name}"
}

// In component:
t('welcome', { name: userName }) // "مرحباً أحمد"
```

## Pluralization

```typescript
// In locale file:
{
  "itemCount": "{count, plural, =0 {لا توجد عناصر} one {عنصر واحد} other {# عناصر}}"
}

// In component:
t('itemCount', { count: 5 }) // "5 عناصر"
```

## Server Components

For server components, await the translation function:

```typescript
import { getTranslations } from 'next-intl/server';

export default async function Page() {
  const t = await getTranslations('common');
  return <h1>{t('appName')}</h1>;
}
```

## Default Locale

Arabic (ar) is the default locale:
- URLs: `/` = Arabic, `/en` = English
- New users see Arabic by default
- RTL is the default layout direction

## Troubleshooting

### Translations not working?
1. Check you're using `'use client'` directive for client components
2. Verify the translation key exists in the locale files
3. Make sure you're using the correct namespace

### Wrong locale detected?
1. Clear browser cookies
2. Check middleware configuration in `/src/middleware.ts`
3. Verify locale is in the URL correctly

### TypeScript errors?
1. Restart TypeScript server (VSCode: Cmd+Shift+P > "Restart TS Server")
2. Run `npm install` to ensure dependencies are installed
3. Check tsconfig.json includes the i18n package

## Examples

See `/apps/web/src/components/examples/i18nExample.tsx` for a complete working example.

## Documentation

Full documentation: `/packages/i18n/README.md`
