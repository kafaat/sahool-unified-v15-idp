/**
 * Logistics Page - Mock Data (Development Fallback)
 * بيانات وهمية ثابتة للتطوير - صفحة إدارة اللوجستيات
 *
 * This file is separated from the page component to allow tree-shaking
 * in production builds. Mock data is only loaded as a fallback when the
 * API is unavailable during development.
 */

export interface Shipment {
  id: string;
  trackingNumber: string;
  origin: string;
  originAr: string;
  destination: string;
  destinationAr: string;
  sender: string;
  senderAr: string;
  receiver: string;
  receiverAr: string;
  status: 'pending' | 'in_transit' | 'delivered' | 'delayed' | 'cancelled';
  weight: number;
  items: number;
  estimatedDelivery: string;
  actualDelivery?: string;
  driver?: string;
  driverAr?: string;
  createdAt: string;
}

export const MOCK_SHIPMENTS: Shipment[] = [
  {
    id: '1',
    trackingNumber: 'SHP-2026-001',
    origin: 'Riyadh Warehouse',
    originAr: 'مستودع الرياض',
    destination: 'Al-Rashid Farm',
    destinationAr: 'مزرعة الراشد',
    sender: 'AgriSupplies Co',
    senderAr: 'شركة المستلزمات الزراعية',
    receiver: 'Ahmed Al-Rashid',
    receiverAr: 'أحمد الراشد',
    status: 'in_transit',
    weight: 500,
    items: 10,
    estimatedDelivery: '2026-01-26',
    driver: 'Saleh Mohammed',
    driverAr: 'صالح محمد',
    createdAt: '2026-01-24',
  },
  {
    id: '2',
    trackingNumber: 'SHP-2026-002',
    origin: 'Jeddah Port',
    originAr: 'ميناء جدة',
    destination: 'Green Valley Farm',
    destinationAr: 'مزرعة الوادي الأخضر',
    sender: 'Import Co',
    senderAr: 'شركة الاستيراد',
    receiver: 'Mohammed Saeed',
    receiverAr: 'محمد سعيد',
    status: 'delivered',
    weight: 1200,
    items: 25,
    estimatedDelivery: '2026-01-23',
    actualDelivery: '2026-01-23',
    driver: 'Fahad Ali',
    driverAr: 'فهد علي',
    createdAt: '2026-01-20',
  },
  {
    id: '3',
    trackingNumber: 'SHP-2026-003',
    origin: 'Dammam Warehouse',
    originAr: 'مستودع الدمام',
    destination: 'Desert Oasis',
    destinationAr: 'واحة الصحراء',
    sender: 'Fertilizer Co',
    senderAr: 'شركة الأسمدة',
    receiver: 'Khalid Omar',
    receiverAr: 'خالد عمر',
    status: 'delayed',
    weight: 800,
    items: 15,
    estimatedDelivery: '2026-01-24',
    driver: 'Hassan Ahmed',
    driverAr: 'حسن أحمد',
    createdAt: '2026-01-22',
  },
  {
    id: '4',
    trackingNumber: 'SHP-2026-004',
    origin: 'Local Supplier',
    originAr: 'مورد محلي',
    destination: 'Palm Gardens',
    destinationAr: 'حدائق النخيل',
    sender: 'Seeds Shop',
    senderAr: 'محل البذور',
    receiver: 'Ali Hassan',
    receiverAr: 'علي حسن',
    status: 'pending',
    weight: 150,
    items: 5,
    estimatedDelivery: '2026-01-27',
    createdAt: '2026-01-25',
  },
  {
    id: '5',
    trackingNumber: 'SHP-2026-005',
    origin: 'Equipment Store',
    originAr: 'متجر المعدات',
    destination: 'Old Farms',
    destinationAr: 'المزارع القديمة',
    sender: 'AgriTech',
    senderAr: 'تقنيات زراعية',
    receiver: 'Sami Abdullah',
    receiverAr: 'سامي عبدالله',
    status: 'cancelled',
    weight: 2000,
    items: 2,
    estimatedDelivery: '2026-01-25',
    createdAt: '2026-01-21',
  },
];
