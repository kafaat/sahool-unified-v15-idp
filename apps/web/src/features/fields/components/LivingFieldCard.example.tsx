/**
 * Living Field Card - Usage Examples
 * أمثلة على استخدام مكون بطاقة الحقل الحي
 */

import React from 'react';
import { LivingFieldCard } from './LivingFieldCard';

/**
 * Example 1: Basic usage with field ID
 */
export function BasicExample() {
  return (
    <div className="max-w-2xl mx-auto p-6">
      <LivingFieldCard fieldId="field-123" />
    </div>
  );
}

/**
 * Example 2: With custom field name
 */
export function WithFieldNameExample() {
  return (
    <div className="max-w-2xl mx-auto p-6">
      <LivingFieldCard
        fieldId="field-456"
        fieldName="North Field"
        fieldNameAr="الحقل الشمالي"
      />
    </div>
  );
}

/**
 * Example 3: Multiple fields in a grid
 */
export function MultipleFieldsExample() {
  const fields = [
    { id: 'field-1', name: 'North Field', nameAr: 'الحقل الشمالي' },
    { id: 'field-2', name: 'South Field', nameAr: 'الحقل الجنوبي' },
    { id: 'field-3', name: 'East Field', nameAr: 'الحقل الشرقي' },
    { id: 'field-4', name: 'West Field', nameAr: 'الحقل الغربي' },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
      {fields.map((field) => (
        <LivingFieldCard
          key={field.id}
          fieldId={field.id}
          fieldName={field.name}
          fieldNameAr={field.nameAr}
        />
      ))}
    </div>
  );
}

/**
 * Example 4: In a field dashboard page
 */
export function FieldDashboardExample() {
  const fieldId = 'field-789';

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          لوحة التحكم - الحقل
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main content - Living Field Card */}
          <div className="lg:col-span-2">
            <LivingFieldCard
              fieldId={fieldId}
              fieldName="Main Wheat Field"
              fieldNameAr="حقل القمح الرئيسي"
            />
          </div>

          {/* Sidebar with other widgets */}
          <div className="space-y-6">
            {/* Other components would go here */}
            <div className="bg-white rounded-lg border-2 border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-2">
                المعلومات الإضافية
              </h3>
              <p className="text-sm text-gray-600">
                Additional field information and controls...
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Example 5: Responsive mobile view
 */
export function MobileViewExample() {
  return (
    <div className="max-w-md mx-auto p-4">
      <LivingFieldCard
        fieldId="field-mobile"
        fieldName="Mobile Field"
        fieldNameAr="الحقل المحمول"
      />
    </div>
  );
}
