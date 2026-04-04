'use client';

/**
 * SAHOOL Cooperatives Management Client
 * إدارة التعاونيات
 */

import React, { useState } from 'react';
import {
  Users,
  Building2,
  Tractor,
  HandCoins,
  Plus,
  UserPlus,
  MapPin,
  Phone,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

interface Cooperative {
  id: string;
  name: string;
  nameAr: string;
  region: string;
  regionAr: string;
  members: number;
  totalArea: number;
  sharedEquipment: number;
  status: 'active' | 'pending' | 'suspended';
  statusAr: string;
  established: string;
  contact: string;
  crops: string[];
  cropsAr: string[];
  monthlyRevenue: number;
}

interface Member {
  id: string;
  name: string;
  nameAr: string;
  role: string;
  roleAr: string;
  farmArea: number;
  joinDate: string;
  contribution: number;
}

const MOCK_COOPERATIVES: Cooperative[] = [
  { id: 'CO-001', name: 'Al-Rashid Agricultural Cooperative', nameAr: 'تعاونية الراشد الزراعية', region: 'Riyadh', regionAr: 'الرياض', members: 45, totalArea: 320, sharedEquipment: 12, status: 'active', statusAr: 'نشط', established: '2023-06-15', contact: '0501234567', crops: ['Wheat', 'Barley'], cropsAr: ['قمح', 'شعير'], monthlyRevenue: 285000 },
  { id: 'CO-002', name: 'Al-Qassim Date Producers', nameAr: 'منتجي تمور القصيم', region: 'Al-Qassim', regionAr: 'القصيم', members: 78, totalArea: 540, sharedEquipment: 8, status: 'active', statusAr: 'نشط', established: '2022-01-10', contact: '0509876543', crops: ['Dates'], cropsAr: ['تمور'], monthlyRevenue: 520000 },
  { id: 'CO-003', name: 'Tabuk Greenhouse Union', nameAr: 'اتحاد بيوت تبوك المحمية', region: 'Tabuk', regionAr: 'تبوك', members: 23, totalArea: 85, sharedEquipment: 5, status: 'active', statusAr: 'نشط', established: '2024-03-22', contact: '0551112233', crops: ['Tomato', 'Cucumber'], cropsAr: ['طماطم', 'خيار'], monthlyRevenue: 145000 },
  { id: 'CO-004', name: 'Jazan Coffee Growers', nameAr: 'مزارعي بن جازان', region: 'Jazan', regionAr: 'جازان', members: 15, totalArea: 42, sharedEquipment: 3, status: 'pending', statusAr: 'قيد المراجعة', established: '2025-11-01', contact: '0567778899', crops: ['Coffee'], cropsAr: ['بن'], monthlyRevenue: 0 },
  { id: 'CO-005', name: 'Hail Wheat Alliance', nameAr: 'تحالف قمح حائل', region: 'Hail', regionAr: 'حائل', members: 34, totalArea: 410, sharedEquipment: 15, status: 'active', statusAr: 'نشط', established: '2021-09-05', contact: '0543332211', crops: ['Wheat', 'Alfalfa'], cropsAr: ['قمح', 'برسيم'], monthlyRevenue: 310000 },
];

const MOCK_MEMBERS: Member[] = [
  { id: 'M-001', name: 'Ahmed Al-Rashid', nameAr: 'أحمد الراشد', role: 'Chairman', roleAr: 'رئيس مجلس الإدارة', farmArea: 25, joinDate: '2023-06-15', contribution: 50000 },
  { id: 'M-002', name: 'Khalid Al-Otaibi', nameAr: 'خالد العتيبي', role: 'Vice Chairman', roleAr: 'نائب الرئيس', farmArea: 18, joinDate: '2023-06-15', contribution: 40000 },
  { id: 'M-003', name: 'Mohammed Al-Harbi', nameAr: 'محمد الحربي', role: 'Member', roleAr: 'عضو', farmArea: 12, joinDate: '2023-08-20', contribution: 25000 },
  { id: 'M-004', name: 'Faisal Al-Dosari', nameAr: 'فيصل الدوسري', role: 'Treasurer', roleAr: 'أمين الصندوق', farmArea: 8, joinDate: '2023-07-01', contribution: 30000 },
  { id: 'M-005', name: 'Sultan Al-Qahtani', nameAr: 'سلطان القحطاني', role: 'Member', roleAr: 'عضو', farmArea: 15, joinDate: '2024-01-10', contribution: 25000 },
];

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-700',
  pending: 'bg-yellow-100 text-yellow-700',
  suspended: 'bg-red-100 text-red-700',
};

export default function CooperativesClient() {
  const [expandedCoop, setExpandedCoop] = useState<string | null>(null);

  const stats = {
    totalCoops: MOCK_COOPERATIVES.length,
    totalMembers: MOCK_COOPERATIVES.reduce((s, c) => s + c.members, 0),
    totalArea: MOCK_COOPERATIVES.reduce((s, c) => s + c.totalArea, 0),
    totalEquipment: MOCK_COOPERATIVES.reduce((s, c) => s + c.sharedEquipment, 0),
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">إدارة التعاونيات</h1>
            <p className="text-gray-600 mt-1">Cooperatives Management</p>
          </div>
          <button className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold">
            <Plus className="w-5 h-5" />
            <span>تعاونية جديدة</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Building2 className="w-5 h-5 text-blue-600" />
            <p className="text-sm text-gray-600">التعاونيات</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.totalCoops}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Users className="w-5 h-5 text-green-600" />
            <p className="text-sm text-gray-600">إجمالي الأعضاء</p>
          </div>
          <p className="text-3xl font-bold text-green-600">{stats.totalMembers}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <MapPin className="w-5 h-5 text-amber-600" />
            <p className="text-sm text-gray-600">المساحة الإجمالية (هـ)</p>
          </div>
          <p className="text-3xl font-bold text-amber-600">{stats.totalArea}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Tractor className="w-5 h-5 text-purple-600" />
            <p className="text-sm text-gray-600">معدات مشتركة</p>
          </div>
          <p className="text-3xl font-bold text-purple-600">{stats.totalEquipment}</p>
        </div>
      </div>

      {/* Cooperatives List */}
      <div className="space-y-4">
        {MOCK_COOPERATIVES.map(coop => (
          <div key={coop.id} className="bg-white rounded-xl border-2 border-gray-200">
            <div
              className="p-6 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => setExpandedCoop(expandedCoop === coop.id ? null : coop.id)}
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{coop.nameAr}</h3>
                  <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                    <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{coop.regionAr}</span>
                    <span className="flex items-center gap-1"><Users className="w-3 h-3" />{coop.members} عضو</span>
                    <span>{coop.totalArea} هـ</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[coop.status]}`}>
                  {coop.statusAr}
                </span>
                <div className="flex flex-wrap gap-1">
                  {coop.cropsAr.map(crop => (
                    <span key={crop} className="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded text-xs">{crop}</span>
                  ))}
                </div>
                {expandedCoop === coop.id ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
              </div>
            </div>

            {expandedCoop === coop.id && (
              <div className="px-6 pb-6 border-t border-gray-100 pt-4">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-semibold text-gray-800">أعضاء التعاونية</h4>
                  <button className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 font-medium">
                    <UserPlus className="w-4 h-4" />
                    إضافة عضو
                  </button>
                </div>
                <table className="w-full text-right">
                  <thead>
                    <tr className="border-b border-gray-200 text-sm text-gray-500">
                      <th className="pb-2 pr-4 font-medium">الاسم</th>
                      <th className="pb-2 pr-4 font-medium">الدور</th>
                      <th className="pb-2 pr-4 font-medium">المساحة (هـ)</th>
                      <th className="pb-2 pr-4 font-medium">المساهمة (ر.س)</th>
                      <th className="pb-2 font-medium">تاريخ الانضمام</th>
                    </tr>
                  </thead>
                  <tbody>
                    {MOCK_MEMBERS.map(member => (
                      <tr key={member.id} className="border-b border-gray-50 text-sm">
                        <td className="py-3 pr-4 font-medium text-gray-900">{member.nameAr}</td>
                        <td className="py-3 pr-4 text-gray-700">{member.roleAr}</td>
                        <td className="py-3 pr-4 text-gray-700">{member.farmArea}</td>
                        <td className="py-3 pr-4 text-gray-700">{member.contribution.toLocaleString()}</td>
                        <td className="py-3 text-gray-500">{member.joinDate}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
                  <span className="flex items-center gap-1"><Phone className="w-3 h-3" />{coop.contact}</span>
                  <span className="flex items-center gap-1"><HandCoins className="w-3 h-3" />الإيراد الشهري: {coop.monthlyRevenue.toLocaleString()} ر.س</span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
