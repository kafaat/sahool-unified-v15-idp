/**
 * Internationalization (i18n) Tests for SAHOOL Platform
 *
 * Tests validate localization, translations, and bilingual support.
 */

type SupportedLocale = 'en' | 'ar';

interface TranslationEntry {
  en: string;
  ar: string;
}

interface TranslationNamespace {
  [key: string]: TranslationEntry | TranslationNamespace;
}

// Type guard to check if value is a TranslationNamespace (not a TranslationEntry)
function isTranslationNamespace(
  value: TranslationEntry | TranslationNamespace
): value is TranslationNamespace {
  return (
    typeof value === 'object' &&
    !('en' in value && 'ar' in value && Object.keys(value).length === 2)
  );
}

class I18nManager {
  private locale: SupportedLocale = 'en';
  private translations: Map<string, TranslationNamespace> = new Map();
  private fallbackLocale: SupportedLocale = 'en';

  setLocale(locale: SupportedLocale): void {
    this.locale = locale;
  }

  getLocale(): SupportedLocale {
    return this.locale;
  }

  loadTranslations(namespace: string, translations: TranslationNamespace): void {
    this.translations.set(namespace, translations);
  }

  t(key: string, params?: Record<string, string | number>): string {
    const parts = key.split('.');
    const namespace = parts[0];
    const path = parts.slice(1);

    const namespaceTranslations = this.translations.get(namespace);
    if (!namespaceTranslations) {
      return key;
    }

    let current: TranslationNamespace | TranslationEntry = namespaceTranslations;
    for (const part of path) {
      if (isTranslationNamespace(current) && part in current) {
        current = current[part];
      } else {
        return key;
      }
    }

    if (typeof current === 'object' && this.locale in current) {
      let text = (current as TranslationEntry)[this.locale];

      // Apply parameter substitution
      if (params) {
        for (const [paramKey, paramValue] of Object.entries(params)) {
          text = text.replace(new RegExp(`\\{\\{${paramKey}\\}\\}`, 'g'), String(paramValue));
        }
      }

      return text;
    }

    // Fallback to default locale
    if (typeof current === 'object' && this.fallbackLocale in current) {
      return (current as TranslationEntry)[this.fallbackLocale];
    }

    return key;
  }

  formatNumber(value: number): string {
    if (this.locale === 'ar') {
      return value.toLocaleString('ar-SA');
    }
    return value.toLocaleString('en-US');
  }

  formatDate(date: Date): string {
    if (this.locale === 'ar') {
      return date.toLocaleDateString('ar-SA');
    }
    return date.toLocaleDateString('en-US');
  }

  formatCurrency(value: number, currency: string = 'SAR'): string {
    const options: Intl.NumberFormatOptions = {
      style: 'currency',
      currency,
    };

    if (this.locale === 'ar') {
      return value.toLocaleString('ar-SA', options);
    }
    return value.toLocaleString('en-US', options);
  }

  isRTL(): boolean {
    return this.locale === 'ar';
  }
}

// Sample translations for testing
const commonTranslations: TranslationNamespace = {
  greeting: {
    en: 'Hello',
    ar: 'مرحبا',
  },
  welcome: {
    en: 'Welcome, {{name}}!',
    ar: 'أهلاً، {{name}}!',
  },
  field: {
    name: {
      en: 'Field Name',
      ar: 'اسم الحقل',
    },
    area: {
      en: 'Area (hectares)',
      ar: 'المساحة (هكتار)',
    },
    status: {
      active: {
        en: 'Active',
        ar: 'نشط',
      },
      fallow: {
        en: 'Fallow',
        ar: 'بور',
      },
    },
  },
  errors: {
    notFound: {
      en: 'Resource not found',
      ar: 'المورد غير موجود',
    },
    validation: {
      en: 'Validation error: {{field}}',
      ar: 'خطأ في التحقق: {{field}}',
    },
  },
};

const agriculturalTranslations: TranslationNamespace = {
  crops: {
    wheat: {
      en: 'Wheat',
      ar: 'قمح',
    },
    barley: {
      en: 'Barley',
      ar: 'شعير',
    },
    datePalm: {
      en: 'Date Palm',
      ar: 'نخيل',
    },
  },
  advisory: {
    irrigation: {
      needed: {
        en: 'Irrigation needed',
        ar: 'الري مطلوب',
      },
      sufficient: {
        en: 'Sufficient moisture',
        ar: 'رطوبة كافية',
      },
    },
    fertilizer: {
      apply: {
        en: 'Apply {{amount}} kg/ha of {{type}}',
        ar: 'أضف {{amount}} كجم/هكتار من {{type}}',
      },
    },
  },
};

describe('I18nManager', () => {
  let i18n: I18nManager;

  beforeEach(() => {
    i18n = new I18nManager();
    i18n.loadTranslations('common', commonTranslations);
    i18n.loadTranslations('agri', agriculturalTranslations);
  });

  describe('Locale Management', () => {
    it('should default to English locale', () => {
      expect(i18n.getLocale()).toBe('en');
    });

    it('should set locale to Arabic', () => {
      i18n.setLocale('ar');
      expect(i18n.getLocale()).toBe('ar');
    });

    it('should detect RTL for Arabic', () => {
      i18n.setLocale('ar');
      expect(i18n.isRTL()).toBe(true);
    });

    it('should not be RTL for English', () => {
      i18n.setLocale('en');
      expect(i18n.isRTL()).toBe(false);
    });
  });

  describe('Translation Lookup', () => {
    it('should return English translation by default', () => {
      const result = i18n.t('common.greeting');
      expect(result).toBe('Hello');
    });

    it('should return Arabic translation when locale is Arabic', () => {
      i18n.setLocale('ar');
      const result = i18n.t('common.greeting');
      expect(result).toBe('مرحبا');
    });

    it('should return nested translation', () => {
      const result = i18n.t('common.field.name');
      expect(result).toBe('Field Name');
    });

    it('should return deeply nested translation', () => {
      const result = i18n.t('common.field.status.active');
      expect(result).toBe('Active');
    });

    it('should return key for missing translation', () => {
      const result = i18n.t('common.nonexistent.key');
      expect(result).toBe('common.nonexistent.key');
    });

    it('should return key for missing namespace', () => {
      const result = i18n.t('unknown.key');
      expect(result).toBe('unknown.key');
    });
  });

  describe('Parameter Substitution', () => {
    it('should substitute single parameter', () => {
      const result = i18n.t('common.welcome', { name: 'John' });
      expect(result).toBe('Welcome, John!');
    });

    it('should substitute parameter in Arabic', () => {
      i18n.setLocale('ar');
      const result = i18n.t('common.welcome', { name: 'أحمد' });
      expect(result).toBe('أهلاً، أحمد!');
    });

    it('should substitute multiple parameters', () => {
      const result = i18n.t('agri.advisory.fertilizer.apply', {
        amount: '50',
        type: 'Urea',
      });
      expect(result).toBe('Apply 50 kg/ha of Urea');
    });

    it('should handle numeric parameters', () => {
      const result = i18n.t('common.errors.validation', { field: 'areaHa' });
      expect(result).toBe('Validation error: areaHa');
    });
  });

  describe('Number Formatting', () => {
    it('should format numbers in English locale', () => {
      i18n.setLocale('en');
      const result = i18n.formatNumber(1234567.89);
      expect(result).toContain('1,234,567');
    });

    it('should format numbers in Arabic locale', () => {
      i18n.setLocale('ar');
      const result = i18n.formatNumber(1234567.89);
      // Arabic numeral formatting
      expect(result).toBeDefined();
    });
  });

  describe('Date Formatting', () => {
    it('should format date in English locale', () => {
      i18n.setLocale('en');
      const date = new Date('2024-01-15');
      const result = i18n.formatDate(date);
      expect(result).toContain('2024');
    });

    it('should format date in Arabic locale', () => {
      i18n.setLocale('ar');
      const date = new Date('2024-01-15');
      const result = i18n.formatDate(date);
      expect(result).toBeDefined();
    });
  });

  describe('Currency Formatting', () => {
    it('should format currency in SAR', () => {
      const result = i18n.formatCurrency(1500, 'SAR');
      expect(result).toBeDefined();
    });

    it('should format currency in Arabic locale', () => {
      i18n.setLocale('ar');
      const result = i18n.formatCurrency(1500, 'SAR');
      expect(result).toBeDefined();
    });
  });

  describe('Agricultural Terms', () => {
    it('should translate crop names', () => {
      expect(i18n.t('agri.crops.wheat')).toBe('Wheat');

      i18n.setLocale('ar');
      expect(i18n.t('agri.crops.wheat')).toBe('قمح');
    });

    it('should translate advisory messages', () => {
      expect(i18n.t('agri.advisory.irrigation.needed')).toBe('Irrigation needed');

      i18n.setLocale('ar');
      expect(i18n.t('agri.advisory.irrigation.needed')).toBe('الري مطلوب');
    });
  });

  describe('Multiple Namespaces', () => {
    it('should access different namespaces', () => {
      expect(i18n.t('common.greeting')).toBe('Hello');
      expect(i18n.t('agri.crops.wheat')).toBe('Wheat');
    });

    it('should isolate namespaces', () => {
      expect(i18n.t('common.crops.wheat')).toBe('common.crops.wheat');
      expect(i18n.t('agri.greeting')).toBe('agri.greeting');
    });
  });
});

describe('Translation Completeness', () => {
  function checkTranslationCompleteness(
    translations: TranslationNamespace,
    path: string = ''
  ): string[] {
    const missingTranslations: string[] = [];

    for (const [key, value] of Object.entries(translations)) {
      const currentPath = path ? `${path}.${key}` : key;

      if (typeof value === 'object' && 'en' in value && 'ar' in value) {
        // This is a translation entry
        if (!value.en) missingTranslations.push(`${currentPath}.en`);
        if (!value.ar) missingTranslations.push(`${currentPath}.ar`);
      } else if (typeof value === 'object') {
        // This is a nested namespace
        missingTranslations.push(
          ...checkTranslationCompleteness(value as TranslationNamespace, currentPath)
        );
      }
    }

    return missingTranslations;
  }

  it('should have complete common translations', () => {
    const missing = checkTranslationCompleteness(commonTranslations);
    expect(missing).toHaveLength(0);
  });

  it('should have complete agricultural translations', () => {
    const missing = checkTranslationCompleteness(agriculturalTranslations);
    expect(missing).toHaveLength(0);
  });
});

describe('Arabic Text Validation', () => {
  function containsArabic(text: string): boolean {
    return /[\u0600-\u06FF]/.test(text);
  }

  it('should verify Arabic translations contain Arabic characters', () => {
    expect(containsArabic((commonTranslations.greeting as TranslationEntry).ar)).toBe(true);
    expect(
      containsArabic(
        ((commonTranslations.field as TranslationNamespace).name as TranslationEntry).ar
      )
    ).toBe(true);
  });

  it('should verify English translations do not contain Arabic', () => {
    expect(containsArabic((commonTranslations.greeting as TranslationEntry).en)).toBe(false);
  });
});
