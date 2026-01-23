# @sahool/i18n

Comprehensive internationalization package for the SAHOOL Agricultural Intelligence Platform, providing full Arabic and English bilingual support with regional customization for the Middle East.

## Features

- **Bilingual Support**: Arabic (ar) and English (en) translations
- **RTL/LTR Support**: Full right-to-left layout utilities
- **Arabic Pluralization**: 6 plural forms (zero, one, two, few, many, other) following CLDR rules
- **Islamic Calendar**: Hijri date formatting with Umm al-Qura calendar
- **Regional Configuration**: Pre-configured settings for Yemen, Saudi Arabia, and UAE
- **Agricultural Domain**: Specialized formatting for crops, yields, irrigation, and weather
- **Number Formatting**: Arabic-Indic numerals support, currency, and units
- **Type-Safe**: Full TypeScript support with type-safe translation keys
- **Next.js Integration**: Built-in support for next-intl

## Installation

```bash
# Add to your app's package.json dependencies
"@sahool/i18n": "*"
```

## Quick Start

### Basic Usage

```typescript
import {
  messages,
  getDirection,
  formatNumber,
  formatDate,
  formatPlural,
  isRTL,
} from "@sahool/i18n";

// Get translation messages
const arMessages = messages.ar;
console.log(arMessages.common.appName); // "سهول"

// Check RTL
console.log(isRTL("ar")); // true
console.log(getDirection("ar")); // "rtl"

// Format numbers
console.log(formatNumber(1234.56, "ar")); // "١٬٢٣٤٫٥٦"
console.log(formatNumber(1234.56, "en")); // "1,234.56"

// Format dates
const date = new Date("2024-01-15");
console.log(formatDate(date, "ar")); // "١٥ يناير ٢٠٢٤"
console.log(formatHijriDate(date, "ar")); // "٣ رجب ١٤٤٥"
```

### Next.js App Router Integration

#### 1. Configure i18n

Create `src/i18n.ts`:

```typescript
import { getRequestConfig } from "next-intl/server";
import { locales, defaultLocale, messages, type Locale } from "@sahool/i18n";

export default getRequestConfig(async ({ locale }) => {
  const validLocale = (
    locales.includes(locale as Locale) ? locale : defaultLocale
  ) as Locale;

  return {
    messages: messages[validLocale],
    timeZone: "Asia/Aden",
    now: new Date(),
  };
});
```

#### 2. Update next.config.js

```javascript
const createNextIntlPlugin = require("next-intl/plugin");
const withNextIntl = createNextIntlPlugin("./src/i18n.ts");

module.exports = withNextIntl({
  // your config
});
```

#### 3. Root Layout with RTL Support

```typescript
import { NextIntlClientProvider } from "next-intl";
import { getMessages } from "next-intl/server";
import { getHtmlAttributes } from "@sahool/i18n";

export default async function RootLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { locale?: string };
}) {
  const locale = (params.locale || "ar") as "ar" | "en";
  const messages = await getMessages();
  const { lang, dir } = getHtmlAttributes(locale);

  return (
    <html lang={lang} dir={dir}>
      <body>
        <NextIntlClientProvider messages={messages} locale={locale}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

#### 4. Use Translations in Components

```typescript
"use client";
import { useTranslations } from "next-intl";
import { formatCurrency, formatArea } from "@sahool/i18n";

export function FieldCard({ area, cost }: { area: number; cost: number }) {
  const t = useTranslations("fields");
  const locale = useLocale() as "ar" | "en";

  return (
    <div>
      <h2>{t("title")}</h2>
      <p>
        {t("area")}: {formatArea(area, locale)}
      </p>
      <p>
        {t("cost")}: {formatCurrency(cost, locale, "YER")}
      </p>
    </div>
  );
}
```

## API Reference

### Core Functions

#### `getMessages(locale: Locale): Messages`

Get all translation messages for a locale.

#### `getLocaleDisplayName(locale: Locale): string`

Get the display name of a locale ("العربية" for Arabic, "English" for English).

#### `getLocaleNativeName(locale: Locale): { name: string; nativeName: string }`

Get both English and native names for a locale.

### RTL Support

#### `isRTL(locale: Locale): boolean`

Check if a locale uses right-to-left text direction.

#### `getDirection(locale: Locale): "rtl" | "ltr"`

Get the text direction for a locale.

#### `getLogicalProperties(locale: Locale)`

Get CSS logical property mappings for RTL-aware styling:

```typescript
const props = getLogicalProperties("ar");
// {
//   start: "right",
//   end: "left",
//   marginInlineStart: "marginRight",
//   textAlign: "right",
//   ...
// }
```

#### `getHtmlAttributes(locale: Locale): { lang: string; dir: "rtl" | "ltr" }`

Get HTML attributes for the document root.

### Number Formatting

#### `formatNumber(value: number, locale: Locale, options?: NumberFormatOptions): string`

Format a number with locale-specific formatting.

```typescript
formatNumber(1234567.89, "ar"); // "١٬٢٣٤٬٥٦٧٫٨٩"
formatNumber(1234567.89, "en"); // "1,234,567.89"
formatNumber(123, "ar", { useArabicNumerals: true }); // Arabic-Indic numerals
```

#### `formatCurrency(value: number, locale: Locale, currency?: string): string`

Format a currency value.

```typescript
formatCurrency(1500, "ar", "YER"); // "١٬٥٠٠٫٠٠ ر.ي."
formatCurrency(1500, "en", "SAR"); // "SAR 1,500.00"
```

#### `formatPercent(value: number, locale: Locale, decimals?: number): string`

Format a percentage (value should be 0-100).

```typescript
formatPercent(75.5, "ar", 1); // "٧٥٫٥٪"
formatPercent(75.5, "en", 1); // "75.5%"
```

### Date Formatting

#### `formatDate(date: Date | string | number, locale: Locale, options?: DateFormatOptions): string`

Format a date.

```typescript
formatDate(new Date("2024-01-15"), "ar"); // "١٥ يناير ٢٠٢٤"
formatDate(new Date("2024-01-15"), "en"); // "Jan 15, 2024"
```

#### `formatHijriDate(date: Date | string | number, locale: Locale): string`

Format a date using the Islamic (Hijri) calendar.

```typescript
formatHijriDate(new Date("2024-01-15"), "ar"); // "٣ رجب ١٤٤٥"
```

#### `formatTime(date: Date | string | number, locale: Locale): string`

Format a time.

#### `formatDateTime(date: Date | string | number, locale: Locale): string`

Format both date and time.

#### `formatRelativeTime(date: Date | string | number, locale: Locale): string`

Format a relative time (e.g., "2 hours ago", "in 3 days").

```typescript
formatRelativeTime(new Date(Date.now() - 3600000), "ar"); // "منذ ساعة"
formatRelativeTime(new Date(Date.now() - 3600000), "en"); // "1 hour ago"
```

### Pluralization

Arabic has 6 plural forms following CLDR rules:

| Category | Numbers        | Example (field) |
| -------- | -------------- | --------------- |
| zero     | 0              | لا توجد حقول    |
| one      | 1              | حقل واحد        |
| two      | 2              | حقلان           |
| few      | 3-10           | ٥ حقول          |
| many     | 11-99          | ٢٥ حقلاً        |
| other    | 100+           | ١٠٠ حقل         |

#### `getArabicPluralCategory(n: number): ArabicPluralCategory`

Get the Arabic plural category for a number.

#### `getPluralCategory(n: number, locale: Locale): string`

Get the plural category for any locale.

#### `formatPlural(count: number, forms: PluralForms, locale: Locale): string`

Format a number with its plural form.

```typescript
const fieldForms = {
  zero: "لا توجد حقول",
  one: "حقل واحد",
  two: "حقلان",
  few: "# حقول",
  many: "# حقلاً",
  other: "# حقل",
};

formatPlural(0, fieldForms, "ar"); // "لا توجد حقول"
formatPlural(1, fieldForms, "ar"); // "حقل واحد"
formatPlural(2, fieldForms, "ar"); // "حقلان"
formatPlural(5, fieldForms, "ar"); // "٥ حقول"
formatPlural(25, fieldForms, "ar"); // "٢٥ حقلاً"
```

### Text Utilities

#### `containsArabic(text: string): boolean`

Check if text contains Arabic characters.

#### `isPrimarilyArabic(text: string): boolean`

Check if text is primarily Arabic (>50% Arabic characters).

#### `detectTextDirection(text: string): "rtl" | "ltr"`

Detect text direction based on content.

#### `wrapWithDirection(text: string, dir: "rtl" | "ltr"): string`

Wrap text with directional markers (LRM/RLM).

#### `formatBidirectionalText(text: string, baseDirection: "rtl" | "ltr"): string`

Format bidirectional text with Unicode isolate markers.

### Agricultural Formatting

#### `formatArea(value: number, locale: Locale, unit?: "hectare" | "sqm" | "dunam"): string`

```typescript
formatArea(10.5, "ar", "hectare"); // "١٠٫٥ هكتار"
formatArea(10.5, "en", "hectare"); // "10.5 ha"
```

#### `formatWeight(value: number, locale: Locale, unit?: "kg" | "ton" | "gram"): string`

```typescript
formatWeight(500, "ar", "kg"); // "٥٠٠ كجم"
```

#### `formatYield(value: number, locale: Locale, unit?: "kg/ha" | "ton/ha"): string`

```typescript
formatYield(5000, "ar", "kg/ha"); // "٥٬٠٠٠ كجم/هـ"
```

#### `formatWaterVolume(value: number, locale: Locale, unit?: "liter" | "m3"): string`

```typescript
formatWaterVolume(250.5, "ar", "m3"); // "٢٥٠٫٥ م³"
```

#### `formatTemperature(value: number, locale: Locale, unit?: "celsius" | "fahrenheit"): string`

```typescript
formatTemperature(25.5, "ar", "celsius"); // "٢٥٫٥°م"
formatTemperature(25.5, "en", "celsius"); // "25.5°C"
```

#### `formatSoilMoisture(value: number, locale: Locale): string`

Format soil moisture as percentage.

#### `formatNDVI(value: number, locale: Locale): string`

Format NDVI value with 2 decimal places.

### Regional Configuration

#### `getRegionalConfig(region?: string): RegionalConfig`

Get regional settings for a country.

```typescript
const yeConfig = getRegionalConfig("ye");
// {
//   timeZone: "Asia/Aden",
//   currency: "YER",
//   currencySymbol: "ر.ي",
//   dateFormat: "both",
//   weekStartsOn: 0,
//   numberSystem: "arab"
// }

const saConfig = getRegionalConfig("sa");
// {
//   timeZone: "Asia/Riyadh",
//   currency: "SAR",
//   currencySymbol: "ر.س",
//   dateFormat: "hijri",
//   ...
// }
```

## Translation Namespaces

| Namespace         | Description                           |
| ----------------- | ------------------------------------- |
| `common`          | Common UI elements (buttons, labels)  |
| `auth`            | Authentication related text           |
| `nav`             | Navigation labels                     |
| `dashboard`       | Dashboard specific content            |
| `fields`          | Field management                      |
| `farms`           | Farm management                       |
| `crops`           | Crop names and types                  |
| `cropStages`      | Growth stages                         |
| `irrigation`      | Irrigation terminology                |
| `weather`         | Weather terms and conditions          |
| `sensors`         | Sensor types and readings             |
| `advisory`        | Advisory and recommendations          |
| `tasks`           | Task management                       |
| `diseases`        | Disease diagnosis                     |
| `alerts`          | Alert messages                        |
| `analytics`       | Analytics and reports                 |
| `costCategories`  | Cost category names                   |
| `reportSections`  | Report section names                  |
| `units`           | Unit names                            |
| `time`            | Time-related terms (days, months)     |
| `validation`      | Form validation messages              |
| `confirmation`    | Confirmation dialogs                  |
| `success`         | Success messages                      |
| `errors`          | Error messages                        |
| `plurals`         | Plural forms (ICU MessageFormat)      |

## Adding New Translations

1. Add keys to both `src/locales/ar.json` and `src/locales/en.json`
2. Keep the structure consistent between both files
3. Use nested objects for organization
4. For plurals, use ICU MessageFormat syntax

```json
// ar.json
{
  "myFeature": {
    "title": "عنوان الميزة",
    "description": "وصف الميزة",
    "count": "{count, plural, =0 {لا توجد عناصر} =1 {عنصر واحد} =2 {عنصران} few {# عناصر} many {# عنصراً} other {# عنصر}}"
  }
}

// en.json
{
  "myFeature": {
    "title": "Feature Title",
    "description": "Feature Description",
    "count": "{count, plural, =0 {No items} =1 {1 item} other {# items}}"
  }
}
```

## Default Locale

The default locale is Arabic (`ar`), reflecting SAHOOL's primary market in the Middle East:

- URLs without a locale prefix use Arabic
- New users default to Arabic
- RTL layout is the default

To change the default, update `defaultLocale` in `src/index.ts`.

## License

Copyright (c) 2024-2026 SAHOOL Platform (KAFAAT)
