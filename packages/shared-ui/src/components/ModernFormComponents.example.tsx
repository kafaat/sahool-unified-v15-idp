'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// Modern Form Components Example - أمثلة على مكونات النماذج الحديثة
// Comprehensive examples for all modern form components
// ═══════════════════════════════════════════════════════════════════════════════

import { useState } from 'react';
import { ModernSelect, SelectOption } from './ModernSelect';
import { ModernCheckbox } from './ModernCheckbox';
import { ModernRadio, RadioOption } from './ModernRadio';
import { ModernSwitch } from './ModernSwitch';
import { ModernSlider, SliderMark } from './ModernSlider';
import { DatePicker } from './DatePicker';
import { User, Mail, Globe, Heart, Star, Zap } from 'lucide-react';

/**
 * Example demonstrating all modern form components
 */
export default function ModernFormComponentsExample() {
  // ModernSelect state
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);

  // ModernCheckbox state
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [newsletter, setNewsletter] = useState(false);
  const [notifications, setNotifications] = useState(false);

  // ModernRadio state
  const [subscriptionPlan, setSubscriptionPlan] = useState('basic');
  const [theme, setTheme] = useState('light');

  // ModernSwitch state
  const [darkMode, setDarkMode] = useState(false);
  const [emailNotif, setEmailNotif] = useState(true);
  const [autoSave, setAutoSave] = useState(false);

  // ModernSlider state
  const [volume, setVolume] = useState(50);
  const [brightness, setBrightness] = useState(75);
  const [price, setPrice] = useState(500);

  // DatePicker state
  const [birthDate, setBirthDate] = useState<Date | null>(null);
  const [appointmentDate, setAppointmentDate] = useState<Date | null>(null);

  // Options data
  const countryOptions: SelectOption[] = [
    { value: 'sa', label: 'السعودية - Saudi Arabia', icon: <Globe size={18} /> },
    { value: 'ae', label: 'الإمارات - UAE', icon: <Globe size={18} /> },
    { value: 'eg', label: 'مصر - Egypt', icon: <Globe size={18} /> },
    { value: 'jo', label: 'الأردن - Jordan', icon: <Globe size={18} /> },
    { value: 'kw', label: 'الكويت - Kuwait', icon: <Globe size={18} /> },
  ];

  const skillOptions: SelectOption[] = [
    { value: 'js', label: 'JavaScript', icon: <Zap size={18} /> },
    { value: 'ts', label: 'TypeScript', icon: <Zap size={18} /> },
    { value: 'react', label: 'React', icon: <Zap size={18} /> },
    { value: 'node', label: 'Node.js', icon: <Zap size={18} /> },
    { value: 'python', label: 'Python', icon: <Zap size={18} /> },
  ];

  const planOptions: RadioOption[] = [
    {
      value: 'basic',
      label: 'باسيك - Basic',
      description: '10$/شهر - Perfect for individuals',
      icon: <User size={24} />,
    },
    {
      value: 'pro',
      label: 'برو - Pro',
      description: '25$/شهر - Best for professionals',
      icon: <Star size={24} />,
    },
    {
      value: 'enterprise',
      label: 'مؤسسات - Enterprise',
      description: '99$/شهر - For large teams',
      icon: <Heart size={24} />,
    },
  ];

  const themeOptions: RadioOption[] = [
    { value: 'light', label: 'فاتح - Light' },
    { value: 'dark', label: 'داكن - Dark' },
    { value: 'auto', label: 'تلقائي - Auto' },
  ];

  const priceMarks: SliderMark[] = [
    { value: 0, label: '$0' },
    { value: 500, label: '$500' },
    { value: 1000, label: '$1000' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-sahool-600 to-purple-600 bg-clip-text text-transparent mb-4">
            Modern Form Components
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            مكونات النماذج الحديثة - Advanced form components with animations and accessibility
          </p>
        </div>

        {/* ModernSelect Examples */}
        <section className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
            ModernSelect - القوائم المنسدلة
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ModernSelect
              label="اختر الدولة / Select Country"
              options={countryOptions}
              value={selectedCountry}
              onChange={(val) => setSelectedCountry(val as string)}
              placeholder="اختر دولة / Choose a country"
              searchable
              clearable
              variant="default"
              size="md"
            />

            <ModernSelect
              label="المهارات / Skills (Multi-Select)"
              options={skillOptions}
              value={selectedSkills}
              onChange={(val) => setSelectedSkills(val as string[])}
              placeholder="اختر المهارات / Select skills"
              searchable
              multiple
              clearable
              variant="filled"
              size="md"
            />
          </div>
        </section>

        {/* ModernCheckbox Examples */}
        <section className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
            ModernCheckbox - مربعات الاختيار
          </h2>
          <div className="space-y-4">
            <ModernCheckbox
              label="موافق على الشروط والأحكام / Accept Terms and Conditions"
              description="يجب الموافقة للمتابعة / You must accept to proceed"
              checked={acceptTerms}
              onChange={(e) => setAcceptTerms(e.target.checked)}
              size="md"
              variant="default"
              required
            />

            <ModernCheckbox
              label="اشترك في النشرة الإخبارية / Subscribe to Newsletter"
              description="احصل على أحدث الأخبار / Get the latest updates"
              checked={newsletter}
              onChange={(e) => setNewsletter(e.target.checked)}
              size="md"
              variant="gradient"
            />

            <ModernCheckbox
              label="تفعيل الإشعارات / Enable Notifications"
              checked={notifications}
              onChange={(e) => setNotifications(e.target.checked)}
              size="lg"
              variant="filled"
            />
          </div>
        </section>

        {/* ModernRadio Examples */}
        <section className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
            ModernRadio - أزرار الاختيار
          </h2>
          <div className="space-y-8">
            <ModernRadio
              label="خطة الاشتراك / Subscription Plan"
              name="subscription"
              options={planOptions}
              value={subscriptionPlan}
              onChange={setSubscriptionPlan}
              variant="card"
              size="md"
            />

            <ModernRadio
              label="المظهر / Theme"
              name="theme"
              options={themeOptions}
              value={theme}
              onChange={setTheme}
              variant="button"
              orientation="horizontal"
              size="md"
            />
          </div>
        </section>

        {/* ModernSwitch Examples */}
        <section className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
            ModernSwitch - مفاتيح التبديل
          </h2>
          <div className="space-y-4">
            <ModernSwitch
              label="الوضع الليلي / Dark Mode"
              description="تفعيل المظهر الداكن / Enable dark theme"
              checked={darkMode}
              onChange={(e) => setDarkMode(e.target.checked)}
              variant="default"
              size="md"
            />

            <ModernSwitch
              label="إشعارات البريد / Email Notifications"
              description="استقبال الإشعارات عبر البريد / Receive notifications via email"
              checked={emailNotif}
              onChange={(e) => setEmailNotif(e.target.checked)}
              variant="gradient"
              size="md"
              showIcons
            />

            <ModernSwitch
              label="الحفظ التلقائي / Auto Save"
              checked={autoSave}
              onChange={(e) => setAutoSave(e.target.checked)}
              variant="ios"
              size="lg"
              showIcons
            />
          </div>
        </section>

        {/* ModernSlider Examples */}
        <section className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
            ModernSlider - أشرطة التمرير
          </h2>
          <div className="space-y-8">
            <ModernSlider
              label="مستوى الصوت / Volume"
              value={volume}
              onChange={setVolume}
              min={0}
              max={100}
              unit="%"
              variant="default"
              size="md"
              showValue
              showTooltip
            />

            <ModernSlider
              label="السطوع / Brightness"
              value={brightness}
              onChange={setBrightness}
              min={0}
              max={100}
              unit="%"
              variant="gradient"
              size="md"
              showValue
            />

            <ModernSlider
              label="نطاق السعر / Price Range"
              value={price}
              onChange={setPrice}
              min={0}
              max={1000}
              step={50}
              unit="$"
              variant="default"
              size="lg"
              showValue
              showMarks
              marks={priceMarks}
            />
          </div>
        </section>

        {/* DatePicker Examples */}
        <section className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">
            DatePicker - منتقي التاريخ
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <DatePicker
              label="تاريخ الميلاد / Birth Date"
              value={birthDate}
              onChange={setBirthDate}
              placeholder="اختر تاريخ / Select date"
              variant="default"
              size="md"
              format="dd/mm/yyyy"
              clearable
              max={new Date()}
            />

            <DatePicker
              label="موعد الحجز / Appointment Date"
              value={appointmentDate}
              onChange={setAppointmentDate}
              placeholder="اختر موعد / Select appointment"
              variant="filled"
              size="md"
              format="dd/mm/yyyy"
              clearable
              min={new Date()}
            />
          </div>
        </section>

        {/* Form Summary */}
        <section className="bg-gradient-to-r from-sahool-600 to-purple-600 rounded-2xl p-6 shadow-lg text-white">
          <h2 className="text-2xl font-bold mb-4">ملخص النموذج / Form Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <strong>Country:</strong> {selectedCountry || 'Not selected'}
            </div>
            <div>
              <strong>Skills:</strong> {selectedSkills.join(', ') || 'None'}
            </div>
            <div>
              <strong>Terms Accepted:</strong> {acceptTerms ? 'Yes' : 'No'}
            </div>
            <div>
              <strong>Newsletter:</strong> {newsletter ? 'Subscribed' : 'Not subscribed'}
            </div>
            <div>
              <strong>Plan:</strong> {subscriptionPlan}
            </div>
            <div>
              <strong>Theme:</strong> {theme}
            </div>
            <div>
              <strong>Dark Mode:</strong> {darkMode ? 'Enabled' : 'Disabled'}
            </div>
            <div>
              <strong>Volume:</strong> {volume}%
            </div>
            <div>
              <strong>Birth Date:</strong> {birthDate?.toLocaleDateString() || 'Not selected'}
            </div>
            <div>
              <strong>Appointment:</strong>{' '}
              {appointmentDate?.toLocaleDateString() || 'Not selected'}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
