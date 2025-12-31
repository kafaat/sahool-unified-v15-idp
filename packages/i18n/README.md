# @sahool/i18n

Internationalization package for the SAHOOL platform, providing translations and utilities for multi-language support.

## Features

- Arabic (ar) and English (en) translations
- Next.js App Router integration via next-intl
- RTL/LTR support utilities
- Type-safe translation keys
- Default locale: Arabic (ar)

## Installation

This package is already part of the SAHOOL monorepo. To use it in your app:

```bash
# Add to your app's package.json dependencies
"@sahool/i18n": "*"
```

## Usage

### In Next.js App (apps/web)

#### 1. Configure i18n in your app

Create `src/i18n.ts`:

```typescript
import { getRequestConfig } from 'next-intl/server';
import { locales, defaultLocale, messages, type Locale } from '@sahool/i18n';

export default getRequestConfig(async ({ locale }) => {
  const validLocale = (locales.includes(locale as Locale) ? locale : defaultLocale) as Locale;

  return {
    messages: messages[validLocale],
    timeZone: 'Asia/Aden',
    now: new Date(),
  };
});
```

#### 2. Update next.config.js

```javascript
const createNextIntlPlugin = require('next-intl/plugin');
const withNextIntl = createNextIntlPlugin('./src/i18n.ts');

const nextConfig = {
  // your config here
};

module.exports = withNextIntl(nextConfig);
```

#### 3. Update your root layout

```typescript
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { locales, getDirection } from '@sahool/i18n';

export default async function RootLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { locale?: string };
}) {
  const locale = params.locale || 'ar';
  const messages = await getMessages();
  const direction = getDirection(locale as any);

  return (
    <html lang={locale} dir={direction}>
      <body>
        <NextIntlClientProvider messages={messages} locale={locale}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

#### 4. Use translations in your components

```typescript
'use client';
import { useTranslations } from 'next-intl';

export function MyComponent() {
  const t = useTranslations('common');

  return (
    <div>
      <h1>{t('appName')}</h1>
      <p>{t('tagline')}</p>
      <button>{t('save')}</button>
    </div>
  );
}
```

### Available Translation Namespaces

- `common` - Common UI elements (buttons, labels, etc.)
- `auth` - Authentication related text
- `nav` - Navigation labels
- `dashboard` - Dashboard specific content
- `fields` - Field management
- `alerts` - Alert messages
- `errors` - Error messages

## Locale Switcher Component

Use the provided LocaleSwitcher component to allow users to switch languages:

```typescript
import { LocaleSwitcher } from '@/components/common/LocaleSwitcher';

export function Header() {
  return (
    <header>
      <LocaleSwitcher />
    </header>
  );
}
```

## Utility Functions

```typescript
import {
  locales,              // ['ar', 'en']
  defaultLocale,        // 'ar'
  getMessages,          // Get messages for a locale
  getLocaleDisplayName, // Get locale name (e.g., 'العربية', 'English')
  isRTL,               // Check if locale is RTL
  getDirection,        // Get 'rtl' or 'ltr'
} from '@sahool/i18n';
```

## Adding New Translations

1. Add keys to both `src/locales/ar.json` and `src/locales/en.json`
2. Keep the structure consistent between both files
3. Use nested objects for organization
4. Follow the existing naming conventions

Example:

```json
// ar.json
{
  "myFeature": {
    "title": "عنوان الميزة",
    "description": "وصف الميزة"
  }
}

// en.json
{
  "myFeature": {
    "title": "Feature Title",
    "description": "Feature Description"
  }
}
```

## Default Locale

The default locale is set to Arabic (ar). This means:
- URLs without a locale prefix will use Arabic
- The app will default to Arabic for new users
- RTL layout is the default

To change the default locale, update the `defaultLocale` constant in `src/index.ts`.

## License

Copyright (c) 2024 SAHOOL Platform
