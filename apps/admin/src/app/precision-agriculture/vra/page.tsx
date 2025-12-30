'use client';

// VRA (Variable Rate Application) Management
// إدارة التطبيق المتغير

import { useEffect, useState } from 'react';
import Header from '@/components/layout/Header';
import StatCard from '@/components/ui/StatCard';
import StatusBadge from '@/components/ui/StatusBadge';
import DataTable from '@/components/ui/DataTable';
import { fetchVRAPrescriptions, approvePrescription, rejectPrescription } from '@/lib/api/precision';
import {
  MapPin,
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  Calendar,
  Filter,
  Download
} from 'lucide-react';
import Link from 'next/link';
import { formatDate } from '@/lib/utils';

interface VRAPrescription {
  id: string;
  farmId: string;
  farmName: string;
  fieldName: string;
  cropType: string;
  prescriptionType: 'fertilizer' | 'pesticide' | 'irrigation';
  status: 'pending' | 'approved' | 'rejected' | 'applied';
  createdAt: string;
  createdBy: string;
  approvedBy?: string;
  appliedAt?: string;
  area: number;
  zones: number;
  totalCost: number;
}

export default function VRAPage() {
  const [prescriptions, setPrescriptions] = useState<VRAPrescription[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedFarm, setSelectedFarm] = useState<string>('all');

  useEffect(() => {
    loadPrescriptions();
  }, [selectedStatus, selectedType, selectedFarm]);

  async function loadPrescriptions() {
    setIsLoading(true);
    try {
      const data = await fetchVRAPrescriptions({
        status: selectedStatus !== 'all' ? selectedStatus : undefined,
        type: selectedType !== 'all' ? selectedType : undefined,
        farmId: selectedFarm !== 'all' ? selectedFarm : undefined,
      });
      setPrescriptions(data);
    } catch (error) {
      console.error('Failed to load VRA prescriptions:', error);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleApprove(id: string) {
    try {
      await approvePrescription(id);
      loadPrescriptions();
    } catch (error) {
      console.error('Failed to approve prescription:', error);
    }
  }

  async function handleReject(id: string) {
    try {
      await rejectPrescription(id);
      loadPrescriptions();
    } catch (error) {
      console.error('Failed to reject prescription:', error);
    }
  }

  const stats = {
    total: prescriptions.length,
    pending: prescriptions.filter(p => p.status === 'pending').length,
    approved: prescriptions.filter(p => p.status === 'approved').length,
    applied: prescriptions.filter(p => p.status === 'applied').length,
  };

  const getPrescriptionTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      fertilizer: 'سماد',
      pesticide: 'مبيد',
      irrigation: 'ري'
    };
    return labels[type] || type;
  };

  return (
    <div className="p-6">
      <Header
        title="إدارة التطبيق المتغير (VRA)"
        subtitle="Variable Rate Application Management - إدارة الوصفات الزراعية الدقيقة"
      />

      {/* Statistics Cards */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="إجمالي الوصفات"
          value={stats.total}
          icon={FileText}
          iconColor="text-blue-600"
        />
        <StatCard
          title="قيد المراجعة"
          value={stats.pending}
          icon={Clock}
          iconColor="text-yellow-600"
        />
        <StatCard
          title="تمت الموافقة"
          value={stats.approved}
          icon={CheckCircle}
          iconColor="text-green-600"
        />
        <StatCard
          title="تم التطبيق"
          value={stats.applied}
          icon={TrendingUp}
          iconColor="text-purple-600"
        />
      </div>

      {/* Filters */}
      <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <span className="text-sm font-medium text-gray-700">تصفية:</span>
          </div>

          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="all">جميع الحالات</option>
            <option value="pending">قيد المراجعة</option>
            <option value="approved">تمت الموافقة</option>
            <option value="rejected">مرفوضة</option>
            <option value="applied">تم التطبيق</option>
          </select>

          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="all">جميع الأنواع</option>
            <option value="fertilizer">سماد</option>
            <option value="pesticide">مبيد</option>
            <option value="irrigation">ري</option>
          </select>

          <button className="mr-auto px-4 py-2 bg-sahool-600 text-white rounded-lg text-sm font-medium hover:bg-sahool-700 transition-colors flex items-center gap-2">
            <Download className="w-4 h-4" />
            تصدير التقرير
          </button>
        </div>
      </div>

      {/* Prescriptions Table */}
      <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">المزرعة / الحقل</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">النوع</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">المساحة</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">المناطق</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">التكلفة</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الحالة</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">التاريخ</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">إجراءات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center">
                    <div className="flex items-center justify-center">
                      <div className="w-8 h-8 border-4 border-sahool-600 border-t-transparent rounded-full animate-spin"></div>
                    </div>
                  </td>
                </tr>
              ) : prescriptions.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-gray-500">
                    لا توجد وصفات متاحة
                  </td>
                </tr>
              ) : (
                prescriptions.map((prescription) => (
                  <tr key={prescription.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-gray-900">{prescription.farmName}</p>
                        <p className="text-sm text-gray-500">{prescription.fieldName}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-gray-900">
                        {getPrescriptionTypeLabel(prescription.prescriptionType)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {prescription.area.toFixed(1)} هكتار
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {prescription.zones}
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      ${prescription.totalCost.toFixed(2)}
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={prescription.status} />
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {formatDate(prescription.createdAt)}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {prescription.status === 'pending' && (
                          <>
                            <button
                              onClick={() => handleApprove(prescription.id)}
                              className="p-1 text-green-600 hover:bg-green-50 rounded transition-colors"
                              title="موافقة"
                            >
                              <CheckCircle className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => handleReject(prescription.id)}
                              className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                              title="رفض"
                            >
                              <XCircle className="w-5 h-5" />
                            </button>
                          </>
                        )}
                        <Link
                          href={`/precision-agriculture/vra/${prescription.id}`}
                          className="p-1 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                          title="عرض التفاصيل"
                        >
                          <FileText className="w-5 h-5" />
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
