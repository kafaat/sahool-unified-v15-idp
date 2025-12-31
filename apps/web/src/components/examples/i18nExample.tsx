/**
 * i18n Integration Example Component
 * مثال على دمج الترجمة الدولية
 *
 * This component demonstrates how to use the @sahool/i18n package
 * in your components with next-intl.
 */

'use client';

import React from 'react';
import { useTranslations, useLocale } from 'next-intl';
import { getDirection, getLocaleDisplayName } from '@sahool/i18n';

export function I18nExample() {
  // Get translation functions for different namespaces
  const tCommon = useTranslations('common');
  const tNav = useTranslations('nav');
  const tDashboard = useTranslations('dashboard');

  // Get current locale
  const locale = useLocale();
  const direction = getDirection(locale as any);
  const localeDisplayName = getLocaleDisplayName(locale as any);

  return (
    <div className="p-6 space-y-6 max-w-2xl">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">
          {tCommon('appName')} - i18n Integration Example
        </h2>

        <div className="space-y-4">
          {/* Current Locale Info */}
          <section>
            <h3 className="text-lg font-semibold mb-2">Current Locale Information</h3>
            <ul className="list-disc list-inside space-y-1 text-gray-700">
              <li>Locale Code: <code className="bg-gray-100 px-2 py-1 rounded">{locale}</code></li>
              <li>Display Name: <code className="bg-gray-100 px-2 py-1 rounded">{localeDisplayName}</code></li>
              <li>Direction: <code className="bg-gray-100 px-2 py-1 rounded">{direction}</code></li>
            </ul>
          </section>

          {/* Common Translations */}
          <section>
            <h3 className="text-lg font-semibold mb-2">Common Translations</h3>
            <div className="grid grid-cols-2 gap-2">
              <button className="px-4 py-2 bg-blue-500 text-white rounded">
                {tCommon('save')}
              </button>
              <button className="px-4 py-2 bg-red-500 text-white rounded">
                {tCommon('delete')}
              </button>
              <button className="px-4 py-2 bg-green-500 text-white rounded">
                {tCommon('add')}
              </button>
              <button className="px-4 py-2 bg-yellow-500 text-white rounded">
                {tCommon('edit')}
              </button>
            </div>
          </section>

          {/* Navigation Translations */}
          <section>
            <h3 className="text-lg font-semibold mb-2">Navigation Translations</h3>
            <ul className="space-y-1 text-gray-700">
              <li>{tNav('dashboard')}</li>
              <li>{tNav('fields')}</li>
              <li>{tNav('farms')}</li>
              <li>{tNav('settings')}</li>
            </ul>
          </section>

          {/* Dashboard Translations */}
          <section>
            <h3 className="text-lg font-semibold mb-2">Dashboard Translations</h3>
            <div className="bg-gray-50 p-4 rounded">
              <h4 className="font-semibold">{tDashboard('welcome')}</h4>
              <div className="grid grid-cols-2 gap-4 mt-2 text-sm">
                <div>
                  <div className="text-gray-600">{tDashboard('totalFields')}</div>
                  <div className="text-2xl font-bold">12</div>
                </div>
                <div>
                  <div className="text-gray-600">{tDashboard('totalArea')}</div>
                  <div className="text-2xl font-bold">240 {tDashboard('areaUnit')}</div>
                </div>
              </div>
            </div>
          </section>

          {/* Usage Example */}
          <section>
            <h3 className="text-lg font-semibold mb-2">Usage in Code</h3>
            <pre className="bg-gray-900 text-gray-100 p-4 rounded overflow-x-auto">
{`import { useTranslations } from 'next-intl';

function MyComponent() {
  const t = useTranslations('common');

  return (
    <button>{t('save')}</button>
  );
}`}
            </pre>
          </section>
        </div>
      </div>
    </div>
  );
}
