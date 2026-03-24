/**
 * Irrigation Feature - Mock Data
 * بيانات احتياطية لميزة الري
 */

import type { IrrigationSchedule, IrrigationMethod } from './types';

export const MOCK_IRRIGATION_SCHEDULES: IrrigationSchedule[] = [
  {
    id: '1',
    fieldId: 'field-1',
    fieldName: 'الحقل الشمالي',
    type: 'drip',
    status: 'scheduled',
    scheduledAt: new Date(Date.now() + 3600000).toISOString(),
    duration: 120,
    waterAmount: 500,
  },
  {
    id: '2',
    fieldId: 'field-2',
    fieldName: 'الحقل الجنوبي',
    type: 'pivot',
    status: 'in_progress',
    scheduledAt: new Date(Date.now() - 7200000).toISOString(),
    duration: 180,
    waterAmount: 1200,
    progress: 65,
  },
  {
    id: '3',
    fieldId: 'field-3',
    fieldName: 'حقل القمح',
    type: 'sprinkler',
    status: 'completed',
    scheduledAt: new Date(Date.now() - 86400000).toISOString(),
    duration: 90,
    waterAmount: 800,
    completedAt: new Date(Date.now() - 80000000).toISOString(),
  },
  {
    id: '4',
    fieldId: 'field-4',
    fieldName: 'بستان النخيل',
    type: 'flood',
    status: 'overdue',
    scheduledAt: new Date(Date.now() - 172800000).toISOString(),
    duration: 240,
    waterAmount: 2000,
  },
  {
    id: '5',
    fieldId: 'field-5',
    fieldName: 'الصوب الزراعية',
    type: 'drip',
    status: 'scheduled',
    scheduledAt: new Date(Date.now() + 36000000).toISOString(),
    duration: 60,
    waterAmount: 200,
  },
];

export const MOCK_IRRIGATION_METHODS: IrrigationMethod[] = [
  { id: 'drip', name: 'Drip', nameAr: 'تنقيط', efficiency: 90 },
  { id: 'sprinkler', name: 'Sprinkler', nameAr: 'رشاشات', efficiency: 75 },
  { id: 'pivot', name: 'Pivot', nameAr: 'محوري', efficiency: 80 },
  { id: 'flood', name: 'Flood', nameAr: 'غمر', efficiency: 50 },
  { id: 'manual', name: 'Manual', nameAr: 'يدوي', efficiency: 45 },
];
