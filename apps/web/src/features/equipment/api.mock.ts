/**
 * Equipment Feature - Mock Data (Development Fallback)
 * بيانات وهمية للمعدات
 *
 * Separated from the API layer to reduce client bundle size.
 * This data is used as fallback when the API is unavailable.
 */

import type { Equipment, MaintenanceRecord } from './types';

export const MOCK_EQUIPMENT: Equipment[] = [
  {
    id: '1',
    name: 'John Deere Tractor 5075E',
    nameAr: 'جرار جون ديري 5075E',
    type: 'tractor',
    status: 'active',
    serialNumber: 'JD-5075E-2023-001',
    manufacturer: 'John Deere',
    model: '5075E',
    purchaseDate: '2023-01-15',
    purchasePrice: 45000,
    currentValue: 42000,
    location: {
      latitude: 15.3694,
      longitude: 44.191,
      fieldId: 'field-1',
      fieldName: 'North Field',
    },
    specifications: {
      horsepower: 75,
      fuelCapacity: 68,
      weight: 2500,
    },
    imageUrl: '/images/equipment/tractor-1.jpg',
    assignedTo: {
      userId: 'user-1',
      userName: 'Ahmad Ali',
    },
    lastMaintenanceDate: '2024-12-01',
    nextMaintenanceDate: '2025-02-01',
    totalOperatingHours: 1250,
    fuelType: 'diesel',
    metadata: {},
    createdAt: '2023-01-15T10:00:00Z',
    updatedAt: '2024-12-01T14:30:00Z',
  },
  {
    id: '2',
    name: 'Case IH Harvester Axial-Flow',
    nameAr: 'حصادة كيس IH محوري التدفق',
    type: 'harvester',
    status: 'maintenance',
    serialNumber: 'CIH-AF-2022-005',
    manufacturer: 'Case IH',
    model: 'Axial-Flow 9250',
    purchaseDate: '2022-08-20',
    purchasePrice: 125000,
    currentValue: 110000,
    specifications: {
      capacity: 450,
      grainTankCapacity: 350,
    },
    lastMaintenanceDate: '2025-01-01',
    nextMaintenanceDate: '2025-01-15',
    totalOperatingHours: 850,
    fuelType: 'diesel',
    metadata: {},
    createdAt: '2022-08-20T09:00:00Z',
    updatedAt: '2025-01-01T11:00:00Z',
  },
  {
    id: '3',
    name: 'Valley Pivot Irrigation System',
    nameAr: 'نظام الري المحوري فالي',
    type: 'irrigation_system',
    status: 'active',
    serialNumber: 'VP-8000-2023-012',
    manufacturer: 'Valley',
    model: '8000 Series',
    purchaseDate: '2023-03-10',
    purchasePrice: 85000,
    currentValue: 80000,
    location: {
      latitude: 15.37,
      longitude: 44.192,
      fieldId: 'field-2',
      fieldName: 'South Field',
    },
    specifications: {
      coverage: 50,
      flowRate: 1200,
    },
    lastMaintenanceDate: '2024-11-15',
    nextMaintenanceDate: '2025-05-15',
    totalOperatingHours: 3200,
    metadata: {},
    createdAt: '2023-03-10T08:00:00Z',
    updatedAt: '2024-11-15T16:00:00Z',
  },
];

export const MOCK_MAINTENANCE_RECORDS: MaintenanceRecord[] = [
  {
    id: 'm1',
    equipmentId: '1',
    equipmentName: 'John Deere Tractor 5075E',
    type: 'routine',
    status: 'completed',
    scheduledDate: '2024-12-01',
    completedDate: '2024-12-01',
    description: 'Regular oil change and filter replacement',
    descriptionAr: 'تغيير الزيت العادي واستبدال الفلتر',
    performedBy: 'Ahmad Ali',
    cost: 250,
    parts: [
      { name: 'Oil filter', quantity: 1, cost: 50 },
      { name: 'Engine oil', quantity: 15, cost: 200 },
    ],
    notes: 'All systems working normally',
    createdAt: '2024-11-20T10:00:00Z',
    updatedAt: '2024-12-01T14:30:00Z',
  },
  {
    id: 'm2',
    equipmentId: '2',
    equipmentName: 'Case IH Harvester Axial-Flow',
    type: 'repair',
    status: 'in_progress',
    scheduledDate: '2025-01-01',
    description: 'Belt replacement and hydraulic system check',
    descriptionAr: 'استبدال الحزام وفحص النظام الهيدروليكي',
    performedBy: 'Mohammed Hassan',
    cost: 850,
    parts: [
      { name: 'Drive belt', quantity: 2, cost: 400 },
      { name: 'Hydraulic fluid', quantity: 20, cost: 450 },
    ],
    createdAt: '2024-12-15T09:00:00Z',
    updatedAt: '2025-01-01T11:00:00Z',
  },
  {
    id: 'm3',
    equipmentId: '1',
    equipmentName: 'John Deere Tractor 5075E',
    type: 'routine',
    status: 'scheduled',
    scheduledDate: '2025-02-01',
    description: 'Scheduled maintenance and inspection',
    descriptionAr: 'الصيانة والفحص المجدول',
    cost: 300,
    createdAt: '2025-01-02T08:00:00Z',
    updatedAt: '2025-01-02T08:00:00Z',
  },
];

export const MOCK_STATS = {
  total: 3,
  byType: {
    tractor: 1,
    harvester: 1,
    irrigation_system: 1,
  },
  byStatus: {
    active: 2,
    maintenance: 1,
  },
  maintenanceDue: 1,
};
