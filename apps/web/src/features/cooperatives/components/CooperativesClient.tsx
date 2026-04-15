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
  Loader2,
  AlertTriangle,
} from 'lucide-react';
import {
  useCooperatives,
  useCooperativeStats,
  useMembers,
} from '../hooks/useCooperatives';
import type { Cooperative, CooperativeMember } from '../types';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-700',
  forming: 'bg-yellow-100 text-yellow-700',
  suspended: 'bg-red-100 text-red-700',
  dissolved: 'bg-gray-100 text-gray-700',
};

const statusLabels: Record<string, string> = {
  active: 'نشط',
  forming: 'قيد التأسيس',
  suspended: 'موقوف',
  dissolved: 'منحل',
};

const roleLabels: Record<string, string> = {
  chairman: 'رئيس مجلس الإدارة',
  vice_chairman: 'نائب الرئيس',
  treasurer: 'أمين الصندوق',
  secretary: 'أمين السر',
  board_member: 'عضو مجلس إدارة',
  member: 'عضو',
  observer: 'مراقب',
};

// ---------------------------------------------------------------------------
// Members Sub-component
// ---------------------------------------------------------------------------

function CoopMembers({ coopId }: { coopId: string }) {
  const { data: members, isLoading, isError } = useMembers(coopId);

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-gray-500 text-sm py-4">
        <Loader2 className="w-4 h-4 animate-spin" />
        جاري تحميل الأعضاء...
      </div>
    );
  }

  if (isError || !members || members.length === 0) {
    return (
      <p className="text-sm text-gray-500 py-4">لا يوجد أعضاء مسجلون حالياً</p>
    );
  }

  return (
    <table className="w-full text-right">
      <thead>
        <tr className="border-b border-gray-200 text-sm text-gray-500">
          <th className="pb-2 pr-4 font-medium">الاسم</th>
          <th className="pb-2 pr-4 font-medium">الدور</th>
          <th className="pb-2 pr-4 font-medium">الأسهم</th>
          <th className="pb-2 pr-4 font-medium">المساهمة (ر.س)</th>
          <th className="pb-2 font-medium">تاريخ الانضمام</th>
        </tr>
      </thead>
      <tbody>
        {members.map((member: CooperativeMember) => (
          <tr key={member.id} className="border-b border-gray-50 text-sm">
            <td className="py-3 pr-4 font-medium text-gray-900">
              {member.farmerNameAr ?? member.farmerName}
            </td>
            <td className="py-3 pr-4 text-gray-700">
              {roleLabels[member.role] ?? member.role}
            </td>
            <td className="py-3 pr-4 text-gray-700">{member.shareCount}</td>
            <td className="py-3 pr-4 text-gray-700">
              {member.contributionValue?.toLocaleString() ?? '-'}
            </td>
            <td className="py-3 text-gray-500">{member.joinDate}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export default function CooperativesClient() {
  const [expandedCoop, setExpandedCoop] = useState<string | null>(null);

  const { data: cooperatives, isLoading, isError, error, refetch } = useCooperatives();
  const { data: stats } = useCooperativeStats();

  const coops = cooperatives ?? [];

  const summaryStats = stats
    ? {
        totalCoops: stats.totalCooperatives,
        totalMembers: stats.totalMembers,
        totalArea: stats.totalLandAreaHa,
        totalEquipment: stats.totalResources,
      }
    : {
        totalCoops: coops.length,
        totalMembers: coops.reduce((s, c) => s + (c.memberCount ?? 0), 0),
        totalArea: coops.reduce((s, c) => s + (c.totalLandAreaHa ?? 0), 0),
        totalEquipment: coops.reduce((s, c) => s + (c.resourceCount ?? 0), 0),
      };

  // ── Loading State ──────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-3">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin mx-auto" />
          <p className="text-gray-600 text-sm">جاري تحميل التعاونيات...</p>
          <p className="text-gray-400 text-xs">Loading cooperatives...</p>
        </div>
      </div>
    );
  }

  // ── Error State ────────────────────────────────────────────────────
  if (isError) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-3 max-w-md">
          <AlertTriangle className="w-8 h-8 text-red-500 mx-auto" />
          <p className="text-gray-900 font-semibold">تعذر تحميل التعاونيات</p>
          <p className="text-gray-500 text-sm">
            {error instanceof Error ? error.message : 'Failed to load cooperatives'}
          </p>
          <button
            onClick={() => refetch()}
            className="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            إعادة المحاولة
          </button>
        </div>
      </div>
    );
  }

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
          <p className="text-3xl font-bold text-gray-900">{summaryStats.totalCoops}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Users className="w-5 h-5 text-green-600" />
            <p className="text-sm text-gray-600">إجمالي الأعضاء</p>
          </div>
          <p className="text-3xl font-bold text-green-600">{summaryStats.totalMembers}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <MapPin className="w-5 h-5 text-amber-600" />
            <p className="text-sm text-gray-600">المساحة الإجمالية (هـ)</p>
          </div>
          <p className="text-3xl font-bold text-amber-600">{summaryStats.totalArea}</p>
        </div>
        <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-2">
            <Tractor className="w-5 h-5 text-purple-600" />
            <p className="text-sm text-gray-600">معدات مشتركة</p>
          </div>
          <p className="text-3xl font-bold text-purple-600">{summaryStats.totalEquipment}</p>
        </div>
      </div>

      {/* Cooperatives List */}
      {coops.length === 0 ? (
        <div className="bg-white rounded-xl border-2 border-gray-200 p-10 text-center text-gray-500">
          <p className="text-sm">لا توجد تعاونيات مسجلة حالياً</p>
          <p className="text-xs text-gray-400 mt-1">No cooperatives found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {coops.map((coop: Cooperative) => (
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
                    <h3 className="text-lg font-bold text-gray-900">{coop.nameAr ?? coop.name}</h3>
                    <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {coop.address ?? '-'}
                      </span>
                      <span className="flex items-center gap-1">
                        <Users className="w-3 h-3" />
                        {coop.memberCount ?? 0} عضو
                      </span>
                      <span>{coop.totalLandAreaHa ?? 0} هـ</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[coop.status] ?? 'bg-gray-100 text-gray-700'}`}
                  >
                    {statusLabels[coop.status] ?? coop.status}
                  </span>
                  {coop.tags?.map((tag) => (
                    <span key={tag} className="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded text-xs">
                      {tag}
                    </span>
                  ))}
                  {expandedCoop === coop.id ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
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
                  <CoopMembers coopId={coop.id} />
                  <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <Phone className="w-3 h-3" />
                      {coop.contactPhone ?? '-'}
                    </span>
                    <span className="flex items-center gap-1">
                      <HandCoins className="w-3 h-3" />
                      رأس المال: {coop.shareCapital?.toLocaleString() ?? 0} {coop.currency ?? 'ر.س'}
                    </span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
