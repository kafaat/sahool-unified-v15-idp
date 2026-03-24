'use client';

// Cooperative Management Page
// صفحة إدارة التعاونيات

import React, { useState, useMemo } from 'react';
import Header from '@/components/layout/Header';
import StatCard from '@/components/ui/StatCard';
import { cn } from '@/lib/utils';
import {
  Users,
  Layers,
  Package,
  DollarSign,
  MapPin,
  ChevronRight,
  X,
  CheckCircle2,
  Clock,
  XCircle,
  Wheat,
  Droplets,
  ShoppingCart,
  Factory,
  User,
  Shield,
  BookOpen,
  Calendar,
  TrendingUp,
  Box,
} from 'lucide-react';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// أنواع البيانات
// ═══════════════════════════════════════════════════════════════════════════

type CoopType = 'agricultural' | 'irrigation' | 'marketing' | 'processing';
type CoopStatus = 'active' | 'pending' | 'suspended';
type MemberRole = 'Chairman' | 'Treasurer' | 'Secretary' | 'Member';
type ResourceStatus = 'available' | 'booked' | 'maintenance';
type ActiveTab = 'overview' | 'members' | 'resources' | 'revenue';

interface CoopMember {
  id: string;
  nameAr: string;
  role: MemberRole;
  joinedDate: string;
  phone: string;
}

interface CoopResource {
  id: string;
  nameAr: string;
  type: string;
  status: ResourceStatus;
  bookedBy?: string;
  returnDate?: string;
}

interface RevenueEntry {
  month: string;
  monthAr: string;
  amount: number;
  members: number;
}

interface Cooperative {
  id: string;
  name: string;
  nameAr: string;
  region: string;
  type: CoopType;
  memberCount: number;
  sharedResources: number;
  totalRevenue: number;
  status: CoopStatus;
  foundedDate: string;
  chairman: string;
  members: CoopMember[];
  resources: CoopResource[];
  revenueHistory: RevenueEntry[];
}

// ═══════════════════════════════════════════════════════════════════════════
// Mock Data
// بيانات تجريبية
// ═══════════════════════════════════════════════════════════════════════════

const MOCK_COOPERATIVES: Cooperative[] = [
  {
    id: 'COOP-001',
    name: 'Wadi Dhubhan Cooperative',
    nameAr: 'تعاونية وادي ذبحان',
    region: 'صنعاء',
    type: 'agricultural',
    memberCount: 45,
    sharedResources: 12,
    totalRevenue: 250000,
    status: 'active',
    foundedDate: '2019-03-15',
    chairman: 'أحمد محمد الحداد',
    members: [
      {
        id: 'm001',
        nameAr: 'أحمد محمد الحداد',
        role: 'Chairman',
        joinedDate: '2019-03-15',
        phone: '+967 71 234 5678',
      },
      {
        id: 'm002',
        nameAr: 'سعيد علي الزبيدي',
        role: 'Treasurer',
        joinedDate: '2019-03-15',
        phone: '+967 71 345 6789',
      },
      {
        id: 'm003',
        nameAr: 'فاطمة حسن الشرعبي',
        role: 'Secretary',
        joinedDate: '2019-04-01',
        phone: '+967 71 456 7890',
      },
      {
        id: 'm004',
        nameAr: 'محمد عبدالله القاضي',
        role: 'Member',
        joinedDate: '2019-05-10',
        phone: '+967 71 567 8901',
      },
      {
        id: 'm005',
        nameAr: 'عبدالرحمن يحيى المقطري',
        role: 'Member',
        joinedDate: '2020-01-20',
        phone: '+967 71 678 9012',
      },
    ],
    resources: [
      { id: 'r001', nameAr: 'جرار زراعي كبير', type: 'معدات', status: 'available' },
      {
        id: 'r002',
        nameAr: 'مضخة ري رئيسية',
        type: 'ري',
        status: 'booked',
        bookedBy: 'محمد عبدالله القاضي',
        returnDate: '2026-03-25',
      },
      { id: 'r003', nameAr: 'مستودع تبريد', type: 'تخزين', status: 'available' },
      { id: 'r004', nameAr: 'آلة حصاد', type: 'معدات', status: 'maintenance' },
      { id: 'r005', nameAr: 'شاحنة نقل', type: 'نقل', status: 'available' },
    ],
    revenueHistory: [
      { month: 'October 2025', monthAr: 'أكتوبر 2025', amount: 38000, members: 45 },
      { month: 'November 2025', monthAr: 'نوفمبر 2025', amount: 42000, members: 45 },
      { month: 'December 2025', monthAr: 'ديسمبر 2025', amount: 55000, members: 45 },
      { month: 'January 2026', monthAr: 'يناير 2026', amount: 48000, members: 45 },
      { month: 'February 2026', monthAr: 'فبراير 2026', amount: 39000, members: 45 },
      { month: 'March 2026', monthAr: 'مارس 2026', amount: 28000, members: 45 },
    ],
  },
  {
    id: 'COOP-002',
    name: 'Tihama Farmers Cooperative',
    nameAr: 'تعاونية مزارعي تهامة',
    region: 'الحديدة',
    type: 'irrigation',
    memberCount: 32,
    sharedResources: 8,
    totalRevenue: 180000,
    status: 'active',
    foundedDate: '2020-06-01',
    chairman: 'عبدالكريم سالم البيضاني',
    members: [
      {
        id: 'm101',
        nameAr: 'عبدالكريم سالم البيضاني',
        role: 'Chairman',
        joinedDate: '2020-06-01',
        phone: '+967 71 111 2222',
      },
      {
        id: 'm102',
        nameAr: 'نجيب عمر الأغبري',
        role: 'Treasurer',
        joinedDate: '2020-06-01',
        phone: '+967 71 222 3333',
      },
      {
        id: 'm103',
        nameAr: 'هدى أحمد الحميري',
        role: 'Secretary',
        joinedDate: '2020-07-15',
        phone: '+967 71 333 4444',
      },
      {
        id: 'm104',
        nameAr: 'وليد محمد المتوكل',
        role: 'Member',
        joinedDate: '2020-08-01',
        phone: '+967 71 444 5555',
      },
    ],
    resources: [
      { id: 'r101', nameAr: 'نظام ري بالتنقيط', type: 'ري', status: 'available' },
      {
        id: 'r102',
        nameAr: 'خزان مياه رئيسي',
        type: 'مياه',
        status: 'booked',
        bookedBy: 'وليد محمد المتوكل',
        returnDate: '2026-03-22',
      },
      { id: 'r103', nameAr: 'مضخة مياه جوفية', type: 'ري', status: 'available' },
      { id: 'r104', nameAr: 'محطة تحلية صغيرة', type: 'مياه', status: 'maintenance' },
    ],
    revenueHistory: [
      { month: 'October 2025', monthAr: 'أكتوبر 2025', amount: 25000, members: 32 },
      { month: 'November 2025', monthAr: 'نوفمبر 2025', amount: 31000, members: 32 },
      { month: 'December 2025', monthAr: 'ديسمبر 2025', amount: 38000, members: 32 },
      { month: 'January 2026', monthAr: 'يناير 2026', amount: 35000, members: 32 },
      { month: 'February 2026', monthAr: 'فبراير 2026', amount: 29000, members: 32 },
      { month: 'March 2026', monthAr: 'مارس 2026', amount: 22000, members: 32 },
    ],
  },
  {
    id: 'COOP-003',
    name: 'Coffee Marketing Cooperative',
    nameAr: 'تعاونية تسويق البن',
    region: 'إب',
    type: 'marketing',
    memberCount: 28,
    sharedResources: 5,
    totalRevenue: 420000,
    status: 'active',
    foundedDate: '2018-09-10',
    chairman: 'محمد صالح الإرياني',
    members: [
      {
        id: 'm201',
        nameAr: 'محمد صالح الإرياني',
        role: 'Chairman',
        joinedDate: '2018-09-10',
        phone: '+967 71 555 6666',
      },
      {
        id: 'm202',
        nameAr: 'رشيدة أحمد الوريث',
        role: 'Treasurer',
        joinedDate: '2018-09-10',
        phone: '+967 71 666 7777',
      },
      {
        id: 'm203',
        nameAr: 'عادل حسين الدعيس',
        role: 'Secretary',
        joinedDate: '2018-10-05',
        phone: '+967 71 777 8888',
      },
      {
        id: 'm204',
        nameAr: 'سمر علي اليوسفي',
        role: 'Member',
        joinedDate: '2019-02-14',
        phone: '+967 71 888 9999',
      },
      {
        id: 'm205',
        nameAr: 'طارق محمد الرداعي',
        role: 'Member',
        joinedDate: '2019-06-01',
        phone: '+967 71 999 0000',
      },
    ],
    resources: [
      { id: 'r201', nameAr: 'منصة التسويق الإلكتروني', type: 'تسويق', status: 'available' },
      { id: 'r202', nameAr: 'مستودع تخزين البن', type: 'تخزين', status: 'available' },
      {
        id: 'r203',
        nameAr: 'آلة تقشير البن',
        type: 'معدات',
        status: 'booked',
        bookedBy: 'طارق محمد الرداعي',
        returnDate: '2026-03-30',
      },
    ],
    revenueHistory: [
      { month: 'October 2025', monthAr: 'أكتوبر 2025', amount: 65000, members: 28 },
      { month: 'November 2025', monthAr: 'نوفمبر 2025', amount: 72000, members: 28 },
      { month: 'December 2025', monthAr: 'ديسمبر 2025', amount: 88000, members: 28 },
      { month: 'January 2026', monthAr: 'يناير 2026', amount: 78000, members: 28 },
      { month: 'February 2026', monthAr: 'فبراير 2026', amount: 69000, members: 28 },
      { month: 'March 2026', monthAr: 'مارس 2026', amount: 48000, members: 28 },
    ],
  },
  {
    id: 'COOP-004',
    name: 'Palm Cooperative',
    nameAr: 'تعاونية النخيل',
    region: 'حضرموت',
    type: 'processing',
    memberCount: 20,
    sharedResources: 6,
    totalRevenue: 150000,
    status: 'active',
    foundedDate: '2021-01-20',
    chairman: 'سلطان عوض الكثيري',
    members: [
      {
        id: 'm301',
        nameAr: 'سلطان عوض الكثيري',
        role: 'Chairman',
        joinedDate: '2021-01-20',
        phone: '+967 73 111 2222',
      },
      {
        id: 'm302',
        nameAr: 'بدر محمد الحامد',
        role: 'Treasurer',
        joinedDate: '2021-01-20',
        phone: '+967 73 222 3333',
      },
      {
        id: 'm303',
        nameAr: 'منيرة سالم العمودي',
        role: 'Secretary',
        joinedDate: '2021-02-10',
        phone: '+967 73 333 4444',
      },
      {
        id: 'm304',
        nameAr: 'عمر خالد السقاف',
        role: 'Member',
        joinedDate: '2021-03-01',
        phone: '+967 73 444 5555',
      },
    ],
    resources: [
      { id: 'r301', nameAr: 'مصنع تعبئة التمر', type: 'تصنيع', status: 'available' },
      { id: 'r302', nameAr: 'مستودع مبرد للتمور', type: 'تخزين', status: 'available' },
      {
        id: 'r303',
        nameAr: 'آلة فرز وتدريج',
        type: 'معدات',
        status: 'booked',
        bookedBy: 'عمر خالد السقاف',
        returnDate: '2026-03-28',
      },
      { id: 'r304', nameAr: 'سيارة توزيع مبردة', type: 'نقل', status: 'available' },
    ],
    revenueHistory: [
      { month: 'October 2025', monthAr: 'أكتوبر 2025', amount: 20000, members: 20 },
      { month: 'November 2025', monthAr: 'نوفمبر 2025', amount: 28000, members: 20 },
      { month: 'December 2025', monthAr: 'ديسمبر 2025', amount: 35000, members: 20 },
      { month: 'January 2026', monthAr: 'يناير 2026', amount: 32000, members: 20 },
      { month: 'February 2026', monthAr: 'فبراير 2026', amount: 22000, members: 20 },
      { month: 'March 2026', monthAr: 'مارس 2026', amount: 13000, members: 20 },
    ],
  },
  {
    id: 'COOP-005',
    name: 'Northern Grain Cooperative',
    nameAr: 'تعاونية الحبوب الشمالية',
    region: 'صعدة',
    type: 'agricultural',
    memberCount: 38,
    sharedResources: 10,
    totalRevenue: 200000,
    status: 'pending',
    foundedDate: '2025-11-05',
    chairman: 'يحيى حسين العمري',
    members: [
      {
        id: 'm401',
        nameAr: 'يحيى حسين العمري',
        role: 'Chairman',
        joinedDate: '2025-11-05',
        phone: '+967 77 111 2222',
      },
      {
        id: 'm402',
        nameAr: 'حمد أحمد المؤيد',
        role: 'Treasurer',
        joinedDate: '2025-11-05',
        phone: '+967 77 222 3333',
      },
      {
        id: 'm403',
        nameAr: 'أم كلثوم علي الوشلي',
        role: 'Secretary',
        joinedDate: '2025-11-15',
        phone: '+967 77 333 4444',
      },
      {
        id: 'm404',
        nameAr: 'قاسم محمد الحوثي',
        role: 'Member',
        joinedDate: '2025-12-01',
        phone: '+967 77 444 5555',
      },
    ],
    resources: [
      { id: 'r401', nameAr: 'جرار زراعي متوسط', type: 'معدات', status: 'available' },
      { id: 'r402', nameAr: 'حصادة حبوب', type: 'معدات', status: 'available' },
      { id: 'r403', nameAr: 'صوامع تخزين الحبوب', type: 'تخزين', status: 'maintenance' },
      { id: 'r404', nameAr: 'مختبر تحليل التربة', type: 'علمي', status: 'available' },
    ],
    revenueHistory: [
      { month: 'November 2025', monthAr: 'نوفمبر 2025', amount: 32000, members: 38 },
      { month: 'December 2025', monthAr: 'ديسمبر 2025', amount: 55000, members: 38 },
      { month: 'January 2026', monthAr: 'يناير 2026', amount: 48000, members: 38 },
      { month: 'February 2026', monthAr: 'فبراير 2026', amount: 41000, members: 38 },
      { month: 'March 2026', monthAr: 'مارس 2026', amount: 24000, members: 38 },
    ],
  },
  {
    id: 'COOP-006',
    name: 'Aden Vegetable Cooperative',
    nameAr: 'تعاونية خضار عدن',
    region: 'عدن',
    type: 'marketing',
    memberCount: 25,
    sharedResources: 7,
    totalRevenue: 310000,
    status: 'active',
    foundedDate: '2020-02-28',
    chairman: 'نادية محمد الصبيحي',
    members: [
      {
        id: 'm501',
        nameAr: 'نادية محمد الصبيحي',
        role: 'Chairman',
        joinedDate: '2020-02-28',
        phone: '+967 72 111 2222',
      },
      {
        id: 'm502',
        nameAr: 'إبراهيم علي الجفري',
        role: 'Treasurer',
        joinedDate: '2020-02-28',
        phone: '+967 72 222 3333',
      },
      {
        id: 'm503',
        nameAr: 'ليلى أحمد البحري',
        role: 'Secretary',
        joinedDate: '2020-03-15',
        phone: '+967 72 333 4444',
      },
      {
        id: 'm504',
        nameAr: 'كريم حسن العولقي',
        role: 'Member',
        joinedDate: '2020-05-01',
        phone: '+967 72 444 5555',
      },
      {
        id: 'm505',
        nameAr: 'زينب سعيد الأمين',
        role: 'Member',
        joinedDate: '2021-01-10',
        phone: '+967 72 555 6666',
      },
    ],
    resources: [
      { id: 'r501', nameAr: 'سوق المزارعين المركزي', type: 'تسويق', status: 'available' },
      {
        id: 'r502',
        nameAr: 'ثلاجة جماعية كبيرة',
        type: 'تخزين',
        status: 'booked',
        bookedBy: 'كريم حسن العولقي',
        returnDate: '2026-03-20',
      },
      { id: 'r503', nameAr: 'حافلة توزيع يومية', type: 'نقل', status: 'available' },
      { id: 'r504', nameAr: 'منصة بيع إلكتروني', type: 'تسويق', status: 'available' },
    ],
    revenueHistory: [
      { month: 'October 2025', monthAr: 'أكتوبر 2025', amount: 48000, members: 25 },
      { month: 'November 2025', monthAr: 'نوفمبر 2025', amount: 54000, members: 25 },
      { month: 'December 2025', monthAr: 'ديسمبر 2025', amount: 62000, members: 25 },
      { month: 'January 2026', monthAr: 'يناير 2026', amount: 58000, members: 25 },
      { month: 'February 2026', monthAr: 'فبراير 2026', amount: 51000, members: 25 },
      { month: 'March 2026', monthAr: 'مارس 2026', amount: 37000, members: 25 },
    ],
  },
];

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// دوال مساعدة
// ═══════════════════════════════════════════════════════════════════════════

function getTypeLabel(type: CoopType): string {
  const labels: Record<CoopType, string> = {
    agricultural: 'زراعية',
    irrigation: 'ري',
    marketing: 'تسويقية',
    processing: 'تصنيعية',
  };
  return labels[type];
}

function getTypeIcon(type: CoopType) {
  switch (type) {
    case 'agricultural':
      return <Wheat className="w-4 h-4" />;
    case 'irrigation':
      return <Droplets className="w-4 h-4" />;
    case 'marketing':
      return <ShoppingCart className="w-4 h-4" />;
    case 'processing':
      return <Factory className="w-4 h-4" />;
  }
}

function getTypeColors(type: CoopType): string {
  const colors: Record<CoopType, string> = {
    agricultural: 'bg-green-100 text-green-700',
    irrigation: 'bg-blue-100 text-blue-700',
    marketing: 'bg-amber-100 text-amber-700',
    processing: 'bg-purple-100 text-purple-700',
  };
  return colors[type];
}

function getStatusConfig(status: CoopStatus) {
  const configs: Record<CoopStatus, { label: string; color: string; icon: React.ReactNode }> = {
    active: {
      label: 'نشطة',
      color: 'bg-green-100 text-green-700',
      icon: <CheckCircle2 className="w-3.5 h-3.5" />,
    },
    pending: {
      label: 'قيد الاعتماد',
      color: 'bg-yellow-100 text-yellow-700',
      icon: <Clock className="w-3.5 h-3.5" />,
    },
    suspended: {
      label: 'موقوفة',
      color: 'bg-red-100 text-red-700',
      icon: <XCircle className="w-3.5 h-3.5" />,
    },
  };
  return configs[status];
}

function getRoleLabel(role: MemberRole): string {
  const labels: Record<MemberRole, string> = {
    Chairman: 'رئيس',
    Treasurer: 'أمين الصندوق',
    Secretary: 'أمين السر',
    Member: 'عضو',
  };
  return labels[role];
}

function getRoleIcon(role: MemberRole) {
  switch (role) {
    case 'Chairman':
      return <Shield className="w-3.5 h-3.5 text-sahool-600" />;
    case 'Treasurer':
      return <DollarSign className="w-3.5 h-3.5 text-amber-600" />;
    case 'Secretary':
      return <BookOpen className="w-3.5 h-3.5 text-blue-600" />;
    default:
      return <User className="w-3.5 h-3.5 text-gray-400" />;
  }
}

function getResourceStatusConfig(status: ResourceStatus) {
  const configs: Record<ResourceStatus, { label: string; color: string }> = {
    available: { label: 'متاح', color: 'bg-green-100 text-green-700' },
    booked: { label: 'محجوز', color: 'bg-blue-100 text-blue-700' },
    maintenance: { label: 'صيانة', color: 'bg-yellow-100 text-yellow-700' },
  };
  return configs[status];
}

function formatRevenue(amount: number): string {
  if (amount >= 1000) {
    return `${(amount / 1000).toFixed(0)}K`;
  }
  return amount.toString();
}

// ═══════════════════════════════════════════════════════════════════════════
// Main Component
// المكون الرئيسي
// ═══════════════════════════════════════════════════════════════════════════

export default function CooperativesPage() {
  const [selectedCoop, setSelectedCoop] = useState<Cooperative | null>(null);
  const [activeTab, setActiveTab] = useState<ActiveTab>('overview');

  // ── Stats ──────────────────────────────────────────────────────────────

  const stats = useMemo(() => {
    const totalCoops = MOCK_COOPERATIVES.length;
    const activeMembers = MOCK_COOPERATIVES.reduce((sum, c) => sum + c.memberCount, 0);
    const sharedResources = MOCK_COOPERATIVES.reduce((sum, c) => sum + c.sharedResources, 0);
    const totalRevenue = MOCK_COOPERATIVES.reduce((sum, c) => sum + c.totalRevenue, 0);
    return { totalCoops, activeMembers, sharedResources, totalRevenue };
  }, []);

  // ── Tabs ───────────────────────────────────────────────────────────────

  const tabs: { key: ActiveTab; label: string }[] = [
    { key: 'overview', label: 'نظرة عامة' },
    { key: 'members', label: 'الأعضاء' },
    { key: 'resources', label: 'الموارد' },
    { key: 'revenue', label: 'الإيرادات' },
  ];

  // ── Revenue Distribution ───────────────────────────────────────────────

  function getRevenueShare(coop: Cooperative): number {
    if (coop.memberCount === 0) return 0;
    return Math.round(coop.totalRevenue / coop.memberCount);
  }

  return (
    <div className="p-6" dir="rtl">
      <Header
        title="إدارة التعاونيات"
        subtitle="إدارة ومتابعة التعاونيات الزراعية والأعضاء والموارد المشتركة"
      />

      {/* ── Stats Row ──────────────────────────────────────────────────── */}
      <div className="mt-6 grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="إجمالي التعاونيات"
          value={stats.totalCoops}
          icon={Layers}
          iconColor="text-sahool-600"
          trend={{ value: 12, isPositive: true }}
        />
        <StatCard
          title="الأعضاء النشطون"
          value={stats.activeMembers}
          icon={Users}
          iconColor="text-blue-600"
          trend={{ value: 8, isPositive: true }}
        />
        <StatCard
          title="الموارد المشتركة"
          value={stats.sharedResources}
          icon={Package}
          iconColor="text-purple-600"
          trend={{ value: 5, isPositive: true }}
        />
        <StatCard
          title="إجمالي الإيرادات"
          value={stats.totalRevenue}
          icon={DollarSign}
          iconColor="text-amber-600"
          suffix="ريال"
          trend={{ value: 15, isPositive: true }}
        />
      </div>

      {/* ── Tab Navigation ─────────────────────────────────────────────── */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
        <div className="flex border-b border-gray-100 dark:border-gray-700">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={cn(
                'px-6 py-3 text-sm font-medium transition-colors relative',
                activeTab === tab.key
                  ? 'text-sahool-600 dark:text-sahool-400'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
              )}
            >
              {tab.label}
              {activeTab === tab.key && (
                <span className="absolute bottom-0 right-0 left-0 h-0.5 bg-sahool-600 dark:bg-sahool-400 rounded-t-full" />
              )}
            </button>
          ))}
        </div>

        {/* ── Overview Tab ─────────────────────────────────────────────── */}
        {activeTab === 'overview' && (
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {MOCK_COOPERATIVES.map((coop) => {
                const statusCfg = getStatusConfig(coop.status);
                const typeCfg = getTypeColors(coop.type);
                const isSelected = selectedCoop?.id === coop.id;

                return (
                  <div
                    key={coop.id}
                    onClick={() => setSelectedCoop(isSelected ? null : coop)}
                    className={cn(
                      'bg-gray-50 dark:bg-gray-900 rounded-xl p-5 border-2 cursor-pointer transition-all hover:shadow-md',
                      isSelected
                        ? 'border-sahool-500 dark:border-sahool-400 shadow-md'
                        : 'border-transparent hover:border-gray-200 dark:hover:border-gray-600'
                    )}
                  >
                    {/* Card Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-bold text-gray-900 dark:text-white text-base leading-tight">
                          {coop.nameAr}
                        </h3>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{coop.id}</p>
                      </div>
                      <ChevronRight
                        className={cn(
                          'w-4 h-4 text-gray-400 flex-shrink-0 mr-2 transition-transform',
                          isSelected && 'rotate-90 text-sahool-500'
                        )}
                      />
                    </div>

                    {/* Region */}
                    <div className="flex items-center gap-1.5 mb-3">
                      <MapPin className="w-3.5 h-3.5 text-gray-400" />
                      <span className="text-sm text-gray-600 dark:text-gray-300">
                        {coop.region}
                      </span>
                    </div>

                    {/* Badges */}
                    <div className="flex flex-wrap items-center gap-2 mb-4">
                      <span
                        className={cn(
                          'inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium',
                          typeCfg
                        )}
                      >
                        {getTypeIcon(coop.type)}
                        {getTypeLabel(coop.type)}
                      </span>
                      <span
                        className={cn(
                          'inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium',
                          statusCfg.color
                        )}
                      >
                        {statusCfg.icon}
                        {statusCfg.label}
                      </span>
                    </div>

                    {/* Metrics */}
                    <div className="grid grid-cols-3 gap-2">
                      <div className="text-center bg-white dark:bg-gray-800 rounded-lg p-2">
                        <p className="text-lg font-bold text-gray-900 dark:text-white">
                          {coop.memberCount}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">عضو</p>
                      </div>
                      <div className="text-center bg-white dark:bg-gray-800 rounded-lg p-2">
                        <p className="text-lg font-bold text-gray-900 dark:text-white">
                          {coop.sharedResources}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">مورد</p>
                      </div>
                      <div className="text-center bg-white dark:bg-gray-800 rounded-lg p-2">
                        <p className="text-lg font-bold text-gray-900 dark:text-white">
                          {formatRevenue(coop.totalRevenue)}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">ريال</p>
                      </div>
                    </div>

                    {/* Chairman */}
                    <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-sahool-100 dark:bg-sahool-900 flex items-center justify-center flex-shrink-0">
                        <User className="w-3.5 h-3.5 text-sahool-600 dark:text-sahool-400" />
                      </div>
                      <span className="text-xs text-gray-600 dark:text-gray-300 truncate">
                        {coop.chairman}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ── Members Tab ──────────────────────────────────────────────── */}
        {activeTab === 'members' && (
          <div className="p-6">
            {MOCK_COOPERATIVES.map((coop) => (
              <div key={coop.id} className="mb-6 last:mb-0">
                <div className="flex items-center gap-3 mb-3">
                  <h3 className="font-bold text-gray-900 dark:text-white">{coop.nameAr}</h3>
                  <span className="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full">
                    {coop.memberCount} عضو
                  </span>
                </div>
                <div className="bg-gray-50 dark:bg-gray-900 rounded-xl overflow-hidden border border-gray-100 dark:border-gray-700">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200 dark:border-gray-700">
                        <th className="text-right py-2.5 px-4 font-medium text-gray-500 dark:text-gray-400">
                          الاسم
                        </th>
                        <th className="text-right py-2.5 px-4 font-medium text-gray-500 dark:text-gray-400">
                          الدور
                        </th>
                        <th className="text-right py-2.5 px-4 font-medium text-gray-500 dark:text-gray-400">
                          تاريخ الانضمام
                        </th>
                        <th className="text-right py-2.5 px-4 font-medium text-gray-500 dark:text-gray-400">
                          الهاتف
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {coop.members.map((member, idx) => (
                        <tr
                          key={member.id}
                          className={cn(
                            'border-b border-gray-100 dark:border-gray-800 last:border-0',
                            idx % 2 === 0
                              ? 'bg-white dark:bg-gray-800'
                              : 'bg-gray-50 dark:bg-gray-900'
                          )}
                        >
                          <td className="py-2.5 px-4">
                            <div className="flex items-center gap-2">
                              <div className="w-7 h-7 rounded-full bg-sahool-100 dark:bg-sahool-900 flex items-center justify-center flex-shrink-0">
                                <span className="text-xs font-bold text-sahool-600 dark:text-sahool-400">
                                  {member.nameAr.charAt(0)}
                                </span>
                              </div>
                              <span className="font-medium text-gray-900 dark:text-white">
                                {member.nameAr}
                              </span>
                            </div>
                          </td>
                          <td className="py-2.5 px-4">
                            <span className="inline-flex items-center gap-1.5 text-gray-700 dark:text-gray-300">
                              {getRoleIcon(member.role)}
                              {getRoleLabel(member.role)}
                            </span>
                          </td>
                          <td className="py-2.5 px-4">
                            <span className="flex items-center gap-1 text-gray-500 dark:text-gray-400">
                              <Calendar className="w-3.5 h-3.5" />
                              {new Date(member.joinedDate).toLocaleDateString('ar-YE')}
                            </span>
                          </td>
                          <td className="py-2.5 px-4 text-gray-500 dark:text-gray-400 font-mono text-xs">
                            {member.phone}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ── Resources Tab ────────────────────────────────────────────── */}
        {activeTab === 'resources' && (
          <div className="p-6">
            {MOCK_COOPERATIVES.map((coop) => (
              <div key={coop.id} className="mb-6 last:mb-0">
                <div className="flex items-center gap-3 mb-3">
                  <h3 className="font-bold text-gray-900 dark:text-white">{coop.nameAr}</h3>
                  <span className="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full">
                    {coop.sharedResources} مورد
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {coop.resources.map((resource) => {
                    const statusCfg = getResourceStatusConfig(resource.status);
                    return (
                      <div
                        key={resource.id}
                        className="bg-gray-50 dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-700"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg bg-sahool-100 dark:bg-sahool-900 flex items-center justify-center flex-shrink-0">
                              <Box className="w-4 h-4 text-sahool-600 dark:text-sahool-400" />
                            </div>
                            <div>
                              <p className="font-medium text-gray-900 dark:text-white text-sm leading-tight">
                                {resource.nameAr}
                              </p>
                              <p className="text-xs text-gray-400 dark:text-gray-500">
                                {resource.type}
                              </p>
                            </div>
                          </div>
                        </div>
                        <span
                          className={cn(
                            'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
                            statusCfg.color
                          )}
                        >
                          {statusCfg.label}
                        </span>
                        {resource.status === 'booked' && resource.bookedBy && (
                          <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-500 dark:text-gray-400 space-y-0.5">
                            <p>محجوز بواسطة: {resource.bookedBy}</p>
                            {resource.returnDate && (
                              <p>
                                تاريخ الإعادة:{' '}
                                {new Date(resource.returnDate).toLocaleDateString('ar-YE')}
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ── Revenue Tab ──────────────────────────────────────────────── */}
        {activeTab === 'revenue' && (
          <div className="p-6">
            {MOCK_COOPERATIVES.map((coop) => (
              <div key={coop.id} className="mb-8 last:mb-0">
                <div className="flex items-center gap-3 mb-4">
                  <h3 className="font-bold text-gray-900 dark:text-white">{coop.nameAr}</h3>
                  <span className="text-xs font-medium text-sahool-600 dark:text-sahool-400 bg-sahool-50 dark:bg-sahool-900 px-2.5 py-0.5 rounded-full">
                    إجمالي: {coop.totalRevenue.toLocaleString('ar-YE')} ريال
                  </span>
                </div>

                {/* Revenue Summary Cards */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
                  <div className="bg-sahool-50 dark:bg-sahool-900/30 rounded-xl p-4 border border-sahool-100 dark:border-sahool-800">
                    <div className="flex items-center gap-2 mb-1">
                      <DollarSign className="w-4 h-4 text-sahool-600 dark:text-sahool-400" />
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        إجمالي الإيرادات
                      </span>
                    </div>
                    <p className="text-xl font-bold text-sahool-700 dark:text-sahool-300">
                      {coop.totalRevenue.toLocaleString('ar-YE')}
                      <span className="text-sm font-normal text-gray-500 mr-1">ريال</span>
                    </p>
                  </div>
                  <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 border border-blue-100 dark:border-blue-800">
                    <div className="flex items-center gap-2 mb-1">
                      <Users className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                      <span className="text-xs text-gray-500 dark:text-gray-400">نصيب كل عضو</span>
                    </div>
                    <p className="text-xl font-bold text-blue-700 dark:text-blue-300">
                      {getRevenueShare(coop).toLocaleString('ar-YE')}
                      <span className="text-sm font-normal text-gray-500 mr-1">ريال</span>
                    </p>
                  </div>
                  <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-4 border border-green-100 dark:border-green-800">
                    <div className="flex items-center gap-2 mb-1">
                      <TrendingUp className="w-4 h-4 text-green-600 dark:text-green-400" />
                      <span className="text-xs text-gray-500 dark:text-gray-400">أعلى شهر</span>
                    </div>
                    <p className="text-sm font-bold text-green-700 dark:text-green-300">
                      {coop.revenueHistory.length > 0
                        ? (coop.revenueHistory.reduce<RevenueEntry | undefined>(
                            (max, e) => (max === undefined || e.amount > max.amount ? e : max),
                            undefined
                          )?.monthAr ?? '-')
                        : '-'}
                    </p>
                  </div>
                </div>

                {/* Monthly Breakdown */}
                <div className="bg-gray-50 dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
                  <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                    <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                      التوزيع الشهري
                    </h4>
                  </div>
                  <div className="divide-y divide-gray-100 dark:divide-gray-800">
                    {coop.revenueHistory.map((entry) => {
                      const maxAmount = Math.max(...coop.revenueHistory.map((e) => e.amount));
                      const barWidth = maxAmount > 0 ? (entry.amount / maxAmount) * 100 : 0;
                      return (
                        <div key={entry.month} className="flex items-center gap-4 px-4 py-3">
                          <span className="text-sm text-gray-600 dark:text-gray-300 w-32 flex-shrink-0">
                            {entry.monthAr}
                          </span>
                          <div className="flex-1 flex items-center gap-3">
                            <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-sahool-500 dark:bg-sahool-400 rounded-full transition-all"
                                style={{ width: `${barWidth}%` }}
                              />
                            </div>
                            <span className="text-sm font-semibold text-gray-900 dark:text-white w-28 text-left flex-shrink-0">
                              {entry.amount.toLocaleString('ar-YE')} ريال
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Detail Panel (slides in when a cooperative is selected) ─────── */}
      {selectedCoop && activeTab === 'overview' && (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl border border-sahool-200 dark:border-sahool-700 shadow-lg overflow-hidden">
          {/* Panel Header */}
          <div className="flex items-center justify-between px-6 py-4 bg-sahool-50 dark:bg-sahool-900/30 border-b border-sahool-100 dark:border-sahool-700">
            <div>
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                {selectedCoop.nameAr}
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {selectedCoop.id} &bull; {selectedCoop.region} &bull; تأسست:{' '}
                {new Date(selectedCoop.foundedDate).toLocaleDateString('ar-YE')}
              </p>
            </div>
            <button
              onClick={() => setSelectedCoop(null)}
              className="p-2 hover:bg-sahool-100 dark:hover:bg-sahool-800 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </button>
          </div>

          <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Members List */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                <Users className="w-4 h-4 text-sahool-600 dark:text-sahool-400" />
                قائمة الأعضاء ({selectedCoop.memberCount})
              </h3>
              <div className="space-y-2">
                {selectedCoop.members.map((member) => (
                  <div
                    key={member.id}
                    className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-100 dark:border-gray-700"
                  >
                    <div className="w-8 h-8 rounded-full bg-sahool-100 dark:bg-sahool-800 flex items-center justify-center flex-shrink-0">
                      <span className="text-sm font-bold text-sahool-600 dark:text-sahool-300">
                        {member.nameAr.charAt(0)}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {member.nameAr}
                      </p>
                      <p className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                        {getRoleIcon(member.role)}
                        {getRoleLabel(member.role)}
                      </p>
                    </div>
                  </div>
                ))}
                {selectedCoop.memberCount > selectedCoop.members.length && (
                  <p className="text-xs text-center text-gray-400 dark:text-gray-500 py-1">
                    + {selectedCoop.memberCount - selectedCoop.members.length} أعضاء آخرون
                  </p>
                )}
              </div>
            </div>

            {/* Resources with booking status */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                <Package className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                الموارد المشتركة ({selectedCoop.sharedResources})
              </h3>
              <div className="space-y-2">
                {selectedCoop.resources.map((resource) => {
                  const statusCfg = getResourceStatusConfig(resource.status);
                  return (
                    <div
                      key={resource.id}
                      className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-100 dark:border-gray-700"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {resource.nameAr}
                        </p>
                        <span
                          className={cn(
                            'text-xs px-2 py-0.5 rounded-full font-medium',
                            statusCfg.color
                          )}
                        >
                          {statusCfg.label}
                        </span>
                      </div>
                      <p className="text-xs text-gray-400 dark:text-gray-500">{resource.type}</p>
                      {resource.status === 'booked' && resource.bookedBy && (
                        <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                          محجوز: {resource.bookedBy}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Revenue Distribution Summary */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                ملخص توزيع الإيرادات
              </h3>
              <div className="space-y-3">
                <div className="p-4 bg-sahool-50 dark:bg-sahool-900/30 rounded-xl border border-sahool-100 dark:border-sahool-800">
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">إجمالي الإيرادات</p>
                  <p className="text-2xl font-bold text-sahool-700 dark:text-sahool-300">
                    {selectedCoop.totalRevenue.toLocaleString('ar-YE')}
                    <span className="text-sm font-normal text-gray-500 mr-1">ريال</span>
                  </p>
                </div>
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-100 dark:border-blue-800">
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">نصيب كل عضو</p>
                  <p className="text-2xl font-bold text-blue-700 dark:text-blue-300">
                    {getRevenueShare(selectedCoop).toLocaleString('ar-YE')}
                    <span className="text-sm font-normal text-gray-500 mr-1">ريال</span>
                  </p>
                </div>
                <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-700">
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">آخر 3 أشهر</p>
                  <div className="space-y-2">
                    {selectedCoop.revenueHistory.slice(-3).map((entry) => (
                      <div key={entry.month} className="flex items-center justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-300">{entry.monthAr}</span>
                        <span className="font-semibold text-gray-900 dark:text-white">
                          {entry.amount.toLocaleString('ar-YE')}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
