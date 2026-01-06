/**
 * InteractiveFieldMap Usage Examples
 * أمثلة استخدام مكون خريطة الحقول التفاعلية
 *
 * This file demonstrates various use cases for the InteractiveFieldMap component
 * يوضح هذا الملف حالات الاستخدام المختلفة لمكون خريطة الحقول التفاعلية
 */

import React from 'react';
import { InteractiveFieldMap } from './InteractiveFieldMap.dynamic';
import type {
  Field,
  GeoPolygon,
  GeoPoint,
} from '../types';
import type { MapTask, HealthZone } from './InteractiveFieldMap';
import type { WeatherData } from '@sahool/api-client';

// ═══════════════════════════════════════════════════════════════════════════
// Example 1: Basic Map with Single Field
// المثال 1: خريطة أساسية مع حقل واحد
// ═══════════════════════════════════════════════════════════════════════════

export const BasicFieldMap: React.FC = () => {
  const sampleField: Field = {
    id: 'field-1',
    name: 'North Field',
    nameAr: 'الحقل الشمالي',
    area: 5.2,
    crop: 'Wheat',
    cropAr: 'قمح',
    polygon: {
      type: 'Polygon',
      coordinates: [
        [
          [44.2, 15.3],
          [44.21, 15.3],
          [44.21, 15.31],
          [44.2, 15.31],
          [44.2, 15.3],
        ],
      ],
    } as GeoPolygon,
    ndviValue: 0.65,
    healthScore: 85,
    status: 'active',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  return (
    <InteractiveFieldMap
      field={sampleField}
      height="500px"
      zoom={14}
      onFieldClick={(field) => {
        console.log('Field clicked:', field.name);
      }}
    />
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// Example 2: Multiple Fields with NDVI Layer
// المثال 2: حقول متعددة مع طبقة NDVI
// ═══════════════════════════════════════════════════════════════════════════

export const MultipleFieldsMap: React.FC = () => {
  const sampleFields: Field[] = [
    {
      id: 'field-1',
      name: 'Field A',
      nameAr: 'الحقل أ',
      area: 3.5,
      polygon: {
        type: 'Polygon',
        coordinates: [
          [
            [44.2, 15.3],
            [44.205, 15.3],
            [44.205, 15.305],
            [44.2, 15.305],
            [44.2, 15.3],
          ],
        ],
      } as GeoPolygon,
      ndviValue: 0.72,
      healthScore: 90,
      status: 'active',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: 'field-2',
      name: 'Field B',
      nameAr: 'الحقل ب',
      area: 4.2,
      polygon: {
        type: 'Polygon',
        coordinates: [
          [
            [44.21, 15.3],
            [44.215, 15.3],
            [44.215, 15.305],
            [44.21, 15.305],
            [44.21, 15.3],
          ],
        ],
      } as GeoPolygon,
      ndviValue: 0.35,
      healthScore: 55,
      status: 'active',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  ];

  return (
    <InteractiveFieldMap
      fields={sampleFields}
      height="600px"
      onFieldClick={(field) => {
        alert(`Selected: ${field.nameAr || field.name}`);
      }}
    />
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// Example 3: Map with Tasks and Health Zones
// المثال 3: خريطة مع المهام ومناطق الصحة
// ═══════════════════════════════════════════════════════════════════════════

export const FieldMapWithTasksAndZones: React.FC = () => {
  const field: Field = {
    id: 'field-1',
    name: 'Main Field',
    nameAr: 'الحقل الرئيسي',
    area: 8.5,
    polygon: {
      type: 'Polygon',
      coordinates: [
        [
          [44.2, 15.3],
          [44.22, 15.3],
          [44.22, 15.32],
          [44.2, 15.32],
          [44.2, 15.3],
        ],
      ],
    } as GeoPolygon,
    ndviValue: 0.58,
    healthScore: 72,
    status: 'active',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  const tasks: MapTask[] = [
    {
      id: 'task-1',
      tenant_id: 'tenant-1',
      field_id: 'field-1',
      title: 'Check irrigation system',
      title_ar: 'فحص نظام الري',
      description: 'Inspect all drip lines',
      status: 'open',
      priority: 'high',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      location: {
        type: 'Point',
        coordinates: [44.21, 15.31],
      } as GeoPoint,
    },
    {
      id: 'task-2',
      tenant_id: 'tenant-1',
      field_id: 'field-1',
      title: 'Fertilizer application',
      title_ar: 'تطبيق الأسمدة',
      status: 'completed',
      priority: 'medium',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      location: {
        type: 'Point',
        coordinates: [44.205, 15.305],
      } as GeoPoint,
    },
  ];

  const healthZones: HealthZone[] = [
    {
      id: 'zone-1',
      fieldId: 'field-1',
      center: {
        type: 'Point',
        coordinates: [44.208, 15.315],
      } as GeoPoint,
      radius: 50,
      healthScore: 45,
      ndviValue: 0.28,
      status: 'stressed',
      color: '#f97316',
    },
    {
      id: 'zone-2',
      fieldId: 'field-1',
      center: {
        type: 'Point',
        coordinates: [44.215, 15.308],
      } as GeoPoint,
      radius: 40,
      healthScore: 88,
      ndviValue: 0.71,
      status: 'healthy',
      color: '#22c55e',
    },
  ];

  return (
    <InteractiveFieldMap
      field={field}
      tasks={tasks}
      healthZones={healthZones}
      height="700px"
      onTaskClick={(task) => {
        console.log('Task clicked:', task.title_ar || task.title);
      }}
      onHealthZoneClick={(zone) => {
        console.log('Health zone clicked:', zone.status, zone.healthScore);
      }}
    />
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// Example 4: Full-Featured Map with Weather Overlay
// المثال 4: خريطة كاملة المميزات مع طبقة الطقس
// ═══════════════════════════════════════════════════════════════════════════

export const FullFeaturedMap: React.FC = () => {
  const fields: Field[] = [
    {
      id: 'field-1',
      name: 'Field 1',
      nameAr: 'الحقل 1',
      area: 6.3,
      crop: 'Tomatoes',
      cropAr: 'طماطم',
      polygon: {
        type: 'Polygon',
        coordinates: [
          [
            [44.2, 15.3],
            [44.21, 15.3],
            [44.21, 15.31],
            [44.2, 15.31],
            [44.2, 15.3],
          ],
        ],
      } as GeoPolygon,
      ndviValue: 0.68,
      healthScore: 82,
      status: 'active',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  ];

  const weather: WeatherData = {
    location_id: 'loc-1',
    temperature_c: 28,
    humidity_percent: 65,
    wind_speed_kmh: 12,
    condition: 'Partly Cloudy',
    condition_ar: 'غائم جزئياً',
    timestamp: new Date().toISOString(),
  };

  const tasks: MapTask[] = [
    {
      id: 'task-urgent',
      tenant_id: 'tenant-1',
      field_id: 'field-1',
      title: 'Pest control urgently needed',
      title_ar: 'مكافحة الآفات مطلوبة بشكل عاجل',
      status: 'open',
      priority: 'urgent',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      location: {
        type: 'Point',
        coordinates: [44.205, 15.305],
      } as GeoPoint,
    },
  ];

  const healthZones: HealthZone[] = [
    {
      id: 'zone-critical',
      fieldId: 'field-1',
      center: {
        type: 'Point',
        coordinates: [44.205, 15.305],
      } as GeoPoint,
      radius: 30,
      healthScore: 35,
      ndviValue: 0.18,
      status: 'critical',
      color: '#ef4444',
    },
  ];

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          خريطة الحقول التفاعلية الكاملة
        </h2>
        <p className="text-gray-600 mb-4">
          خريطة تفاعلية مع جميع الطبقات: حدود الحقول، NDVI، مناطق الصحة، المهام، والطقس
        </p>

        <InteractiveFieldMap
          fields={fields}
          tasks={tasks}
          healthZones={healthZones}
          weather={weather}
          height="800px"
          zoom={15}
          enableLayerControl={true}
          onFieldClick={(field) => {
            console.log('Field:', field);
          }}
          onTaskClick={(task) => {
            console.log('Task:', task);
          }}
          onHealthZoneClick={(zone) => {
            console.log('Health Zone:', zone);
          }}
          onMapClick={(lat, lng) => {
            console.log('Map clicked at:', lat, lng);
          }}
        />
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// Example 5: Integration with State Management
// المثال 5: التكامل مع إدارة الحالة
// ═══════════════════════════════════════════════════════════════════════════

export const StatefulFieldMap: React.FC = () => {
  const [selectedField, setSelectedField] = React.useState<Field | null>(null);
  const [selectedTask, setSelectedTask] = React.useState<MapTask | null>(null);

  const fields: Field[] = [
    {
      id: 'field-1',
      name: 'Interactive Field',
      nameAr: 'حقل تفاعلي',
      area: 5.0,
      polygon: {
        type: 'Polygon',
        coordinates: [
          [
            [44.2, 15.3],
            [44.21, 15.3],
            [44.21, 15.31],
            [44.2, 15.31],
            [44.2, 15.3],
          ],
        ],
      } as GeoPolygon,
      ndviValue: 0.62,
      healthScore: 78,
      status: 'active',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      {/* Map */}
      <div className="lg:col-span-2">
        <InteractiveFieldMap
          fields={fields}
          height="600px"
          onFieldClick={setSelectedField}
          onTaskClick={setSelectedTask}
        />
      </div>

      {/* Details Panel */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">التفاصيل</h3>

        {selectedField ? (
          <div className="space-y-3">
            <h4 className="font-semibold text-gray-800">حقل محدد:</h4>
            <div className="space-y-2 text-sm">
              <p>
                <span className="text-gray-600">الاسم:</span>{' '}
                <span className="font-semibold">{selectedField.nameAr}</span>
              </p>
              <p>
                <span className="text-gray-600">المساحة:</span>{' '}
                <span className="font-semibold">{selectedField.area} هكتار</span>
              </p>
              <p>
                <span className="text-gray-600">الصحة:</span>{' '}
                <span className="font-semibold">{selectedField.healthScore}%</span>
              </p>
            </div>
          </div>
        ) : selectedTask ? (
          <div className="space-y-3">
            <h4 className="font-semibold text-gray-800">مهمة محددة:</h4>
            <div className="space-y-2 text-sm">
              <p>
                <span className="text-gray-600">العنوان:</span>{' '}
                <span className="font-semibold">{selectedTask.title_ar}</span>
              </p>
              <p>
                <span className="text-gray-600">الحالة:</span>{' '}
                <span className="font-semibold">{selectedTask.status}</span>
              </p>
              <p>
                <span className="text-gray-600">الأولوية:</span>{' '}
                <span className="font-semibold">{selectedTask.priority}</span>
              </p>
            </div>
          </div>
        ) : (
          <p className="text-gray-500 text-sm">
            انقر على حقل أو مهمة على الخريطة لعرض التفاصيل
          </p>
        )}
      </div>
    </div>
  );
};

export default {
  BasicFieldMap,
  MultipleFieldsMap,
  FieldMapWithTasksAndZones,
  FullFeaturedMap,
  StatefulFieldMap,
};
