'use client';

/**
 * SAHOOL Crop Insurance Client
 * التأمين الزراعي
 */

import React, { useState } from 'react';
import {
  Shield,
  AlertTriangle,
  FileText,
  Plus,
  CheckCircle,
  Clock,
  XCircle,
  DollarSign,
  Wheat,
  CloudRain,
  Thermometer,
  Bug,
} from 'lucide-react';

interface InsurancePolicy {
  id: string;
  policyNumber: string;
  fieldName: string;
  fieldNameAr: string;
  crop: string;
  cropAr: string;
  area: number;
  coverageType: string;
  coverageTypeAr: string;
  premiumAmount: number;
  coverageAmount: number;
  startDate: string;
  endDate: string;
  status: 'active' | 'expired' | 'pending' | 'claimed';
  statusAr: string;
  riskLevel: 'low' | 'medium' | 'high';
  riskLevelAr: string;
}

interface Claim {
  id: string;
  policyNumber: string;
  type: string;
  typeAr: string;
  description: string;
  descriptionAr: string;
  amount: number;
  filedDate: string;
  status: 'pending' | 'approved' | 'rejected' | 'under-review';
  statusAr: string;
}

const MOCK_POLICIES: InsurancePolicy[] = [
  { id: 'IP-001', policyNumber: 'SAH-INS-2026-001', fieldName: 'North Wheat Field', fieldNameAr: 'حقل القمح الشمالي', crop: 'Wheat', cropAr: 'قمح', area: 25, coverageType: 'Multi-Peril', coverageTypeAr: 'تغطية شاملة', premiumAmount: 4500, coverageAmount: 185000, startDate: '2025-10-01', endDate: '2026-06-30', status: 'active', statusAr: 'نشط', riskLevel: 'medium', riskLevelAr: 'متوسط' },
  { id: 'IP-002', policyNumber: 'SAH-INS-2026-002', fieldName: 'Date Palm Grove', fieldNameAr: 'بستان النخيل', crop: 'Dates', cropAr: 'تمور', area: 15, coverageType: 'Named Peril', coverageTypeAr: 'مخاطر محددة', premiumAmount: 3200, coverageAmount: 520000, startDate: '2026-01-01', endDate: '2026-12-31', status: 'active', statusAr: 'نشط', riskLevel: 'low', riskLevelAr: 'منخفض' },
  { id: 'IP-003', policyNumber: 'SAH-INS-2026-003', fieldName: 'Greenhouse GH-05', fieldNameAr: 'بيت محمي GH-05', crop: 'Tomato', cropAr: 'طماطم', area: 3, coverageType: 'Revenue Protection', coverageTypeAr: 'حماية الإيرادات', premiumAmount: 1800, coverageAmount: 95000, startDate: '2026-02-01', endDate: '2026-08-31', status: 'active', statusAr: 'نشط', riskLevel: 'high', riskLevelAr: 'عالي' },
  { id: 'IP-004', policyNumber: 'SAH-INS-2025-015', fieldName: 'South Barley Field', fieldNameAr: 'حقل الشعير الجنوبي', crop: 'Barley', cropAr: 'شعير', area: 18, coverageType: 'Multi-Peril', coverageTypeAr: 'تغطية شاملة', premiumAmount: 3100, coverageAmount: 120000, startDate: '2025-09-01', endDate: '2026-03-31', status: 'expired', statusAr: 'منتهي', riskLevel: 'low', riskLevelAr: 'منخفض' },
  { id: 'IP-005', policyNumber: 'SAH-INS-2026-004', fieldName: 'Alfalfa Field F-012', fieldNameAr: 'حقل البرسيم F-012', crop: 'Alfalfa', cropAr: 'برسيم', area: 10, coverageType: 'Crop-Hail', coverageTypeAr: 'تغطية البرد', premiumAmount: 1500, coverageAmount: 65000, startDate: '2026-03-01', endDate: '2026-09-30', status: 'pending', statusAr: 'قيد المراجعة', riskLevel: 'medium', riskLevelAr: 'متوسط' },
];

const MOCK_CLAIMS: Claim[] = [
  { id: 'CL-001', policyNumber: 'SAH-INS-2026-001', type: 'Frost Damage', typeAr: 'أضرار الصقيع', description: 'Late frost damaged 30% of wheat crop', descriptionAr: 'صقيع متأخر أضر بـ 30% من محصول القمح', amount: 55000, filedDate: '2026-03-15', status: 'approved', statusAr: 'تمت الموافقة' },
  { id: 'CL-002', policyNumber: 'SAH-INS-2026-003', type: 'Pest Damage', typeAr: 'أضرار آفات', description: 'Whitefly infestation in greenhouse', descriptionAr: 'إصابة بالذبابة البيضاء في البيت المحمي', amount: 28000, filedDate: '2026-03-28', status: 'under-review', statusAr: 'قيد الدراسة' },
  { id: 'CL-003', policyNumber: 'SAH-INS-2025-015', type: 'Drought', typeAr: 'جفاف', description: 'Water shortage reduced yield by 40%', descriptionAr: 'نقص المياه خفض الإنتاج بنسبة 40%', amount: 48000, filedDate: '2026-02-10', status: 'rejected', statusAr: 'مرفوض' },
];

const policyStatusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-700',
  expired: 'bg-gray-100 text-gray-600',
  pending: 'bg-yellow-100 text-yellow-700',
  claimed: 'bg-blue-100 text-blue-700',
};

const riskColors: Record<string, string> = {
  low: 'bg-green-100 text-green-700',
  medium: 'bg-yellow-100 text-yellow-700',
  high: 'bg-red-100 text-red-700',
};

const claimStatusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-700',
  approved: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
  'under-review': 'bg-blue-100 text-blue-700',
};

const claimStatusIcons: Record<string, React.ReactNode> = {
  pending: <Clock className="w-4 h-4" />,
  approved: <CheckCircle className="w-4 h-4" />,
  rejected: <XCircle className="w-4 h-4" />,
  'under-review': <FileText className="w-4 h-4" />,
};

export default function CropInsuranceClient() {
  const [activeTab, setActiveTab] = useState<'policies' | 'claims'>('policies');

  const stats = {
    activePolicies: MOCK_POLICIES.filter(p => p.status === 'active').length,
    totalCoverage: MOCK_POLICIES.filter(p => p.status === 'active').reduce((s, p) => s + p.coverageAmount, 0),
    pendingClaims: MOCK_CLAIMS.filter(c => c.status === 'pending' || c.status === 'under-review').length,
    totalPremiums: MOCK_POLICIES.filter(p => p.status === 'active').reduce((s, p) => s + p.premiumAmount, 0),
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">التأمين الزراعي</h1>
            <p className="text-gray-600 mt-1">Crop Insurance</p>
          </div>
          <div className="flex gap-3">
            <button className="flex items-center gap-2 px-5 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors font-semibold">
              <AlertTriangle className="w-5 h-5" />
              <span>تقديم مطالبة</span>
            </button>
            <button className="flex items-center gap-2 px-5 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold">
              <Plus className="w-5 h-5" />
              <span>وثيقة جديدة</span>
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Shield className="w-5 h-5 text-blue-600" />
            <p className="text-sm text-gray-600">وثائق نشطة</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.activePolicies}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <DollarSign className="w-5 h-5 text-green-600" />
            <p className="text-sm text-gray-600">إجمالي التغطية (ر.س)</p>
          </div>
          <p className="text-3xl font-bold text-green-600">{(stats.totalCoverage / 1000).toFixed(0)}K</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <FileText className="w-5 h-5 text-orange-600" />
            <p className="text-sm text-gray-600">مطالبات معلقة</p>
          </div>
          <p className="text-3xl font-bold text-orange-600">{stats.pendingClaims}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Wheat className="w-5 h-5 text-amber-600" />
            <p className="text-sm text-gray-600">أقساط سنوية (ر.س)</p>
          </div>
          <p className="text-3xl font-bold text-amber-600">{stats.totalPremiums.toLocaleString()}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl border-2 border-gray-200">
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('policies')}
            className={`px-6 py-4 font-semibold text-sm transition-colors ${activeTab === 'policies' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            الوثائق
          </button>
          <button
            onClick={() => setActiveTab('claims')}
            className={`px-6 py-4 font-semibold text-sm transition-colors ${activeTab === 'claims' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            المطالبات
          </button>
        </div>

        <div className="p-6 overflow-x-auto">
          {activeTab === 'policies' ? (
            <table className="w-full text-right">
              <thead>
                <tr className="border-b border-gray-200 text-sm text-gray-500">
                  <th className="pb-3 pr-4 font-medium">رقم الوثيقة</th>
                  <th className="pb-3 pr-4 font-medium">الحقل</th>
                  <th className="pb-3 pr-4 font-medium">المحصول</th>
                  <th className="pb-3 pr-4 font-medium">التغطية</th>
                  <th className="pb-3 pr-4 font-medium">القسط (ر.س)</th>
                  <th className="pb-3 pr-4 font-medium">مبلغ التغطية</th>
                  <th className="pb-3 pr-4 font-medium">المخاطر</th>
                  <th className="pb-3 pr-4 font-medium">الحالة</th>
                  <th className="pb-3 font-medium">الصلاحية</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_POLICIES.map(policy => (
                  <tr key={policy.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 pr-4 text-sm font-mono font-semibold text-gray-900">{policy.policyNumber}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{policy.fieldNameAr}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{policy.cropAr}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{policy.coverageTypeAr}</td>
                    <td className="py-4 pr-4 text-sm font-medium text-gray-900">{policy.premiumAmount.toLocaleString()}</td>
                    <td className="py-4 pr-4 text-sm font-medium text-gray-900">{policy.coverageAmount.toLocaleString()}</td>
                    <td className="py-4 pr-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${riskColors[policy.riskLevel]}`}>
                        {policy.riskLevelAr}
                      </span>
                    </td>
                    <td className="py-4 pr-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${policyStatusColors[policy.status]}`}>
                        {policy.statusAr}
                      </span>
                    </td>
                    <td className="py-4 text-xs text-gray-500">{policy.startDate} - {policy.endDate}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <table className="w-full text-right">
              <thead>
                <tr className="border-b border-gray-200 text-sm text-gray-500">
                  <th className="pb-3 pr-4 font-medium">المطالبة</th>
                  <th className="pb-3 pr-4 font-medium">رقم الوثيقة</th>
                  <th className="pb-3 pr-4 font-medium">النوع</th>
                  <th className="pb-3 pr-4 font-medium">الوصف</th>
                  <th className="pb-3 pr-4 font-medium">المبلغ (ر.س)</th>
                  <th className="pb-3 pr-4 font-medium">الحالة</th>
                  <th className="pb-3 font-medium">التاريخ</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_CLAIMS.map(claim => (
                  <tr key={claim.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 pr-4 text-sm font-semibold text-gray-900">{claim.id}</td>
                    <td className="py-4 pr-4 text-sm font-mono text-gray-700">{claim.policyNumber}</td>
                    <td className="py-4 pr-4 text-sm text-gray-700">{claim.typeAr}</td>
                    <td className="py-4 pr-4 text-sm text-gray-600 max-w-[250px] truncate">{claim.descriptionAr}</td>
                    <td className="py-4 pr-4 text-sm font-bold text-gray-900">{claim.amount.toLocaleString()}</td>
                    <td className="py-4 pr-4">
                      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${claimStatusColors[claim.status]}`}>
                        {claimStatusIcons[claim.status]}
                        {claim.statusAr}
                      </span>
                    </td>
                    <td className="py-4 text-sm text-gray-500">{claim.filedDate}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
