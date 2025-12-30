// @ts-nocheck - Temporary fix for types with React 19
'use client';

// Disease Management Page - Sahool Vision AI
// صفحة إدارة الأمراض - سهول فيجن

import { useEffect, useState, useMemo, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Header from '@/components/layout/Header';
import AlertBadge from '@/components/ui/AlertBadge';
import StatusBadge from '@/components/ui/StatusBadge';
import { fetchDiagnoses, updateDiagnosisStatus } from '@/lib/api';
import { formatDate, cn } from '@/lib/utils';
import type { DiagnosisRecord } from '@/types';
import {
  Bug,
  Filter,
  Search,
  Eye,
  Check,
  X,
  Pill,
  MapPin,
  Calendar,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  Download,
  Loader2,
} from 'lucide-react';

const SEVERITY_OPTIONS = [
  { value: '', label: 'كل الخطورات' },
  { value: 'low', label: 'منخفض' },
  { value: 'medium', label: 'متوسط' },
  { value: 'high', label: 'مرتفع' },
  { value: 'critical', label: 'حرج' },
];

const STATUS_OPTIONS = [
  { value: '', label: 'كل الحالات' },
  { value: 'pending', label: 'قيد المراجعة' },
  { value: 'confirmed', label: 'مؤكد' },
  { value: 'rejected', label: 'مرفوض' },
  { value: 'treated', label: 'تم العلاج' },
];

function DiseasesContent() {
  const searchParams = useSearchParams();
  const farmIdParam = searchParams?.get('farmId') || '';

  const [diagnoses, setDiagnoses] = useState<DiagnosisRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedDiagnosis, setSelectedDiagnosis] = useState<DiagnosisRecord | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [farmIdFilter, setFarmIdFilter] = useState(farmIdParam);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;

  useEffect(() => {
    loadDiagnoses();
  }, []);

  async function loadDiagnoses() {
    setIsLoading(true);
    try {
      const data = await fetchDiagnoses();
      setDiagnoses(data);
    } catch (error) {
      console.error('Failed to load diagnoses:', error);
    } finally {
      setIsLoading(false);
    }
  }

  // Filter diagnoses
  const filteredDiagnoses = useMemo(() => {
    return diagnoses.filter((d) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !d.diseaseNameAr.toLowerCase().includes(query) &&
          !d.diseaseName.toLowerCase().includes(query) &&
          !(d.farmName || '').toLowerCase().includes(query)
        ) {
          return false;
        }
      }
      if (severityFilter && d.severity !== severityFilter) return false;
      if (statusFilter && d.status !== statusFilter) return false;
      if (farmIdFilter && d.farmId !== farmIdFilter) return false;
      return true;
    });
  }, [diagnoses, searchQuery, severityFilter, statusFilter, farmIdFilter]);

  // Paginate
  const totalPages = Math.ceil(filteredDiagnoses.length / itemsPerPage);
  const paginatedDiagnoses = filteredDiagnoses.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Stats
  const stats = useMemo(() => {
    return {
      total: diagnoses.length,
      pending: diagnoses.filter((d) => d.status === 'pending').length,
      critical: diagnoses.filter((d) => d.severity === 'critical').length,
      thisWeek: diagnoses.filter((d) => {
        const weekAgo = new Date();
        weekAgo.setDate(weekAgo.getDate() - 7);
        return new Date(d.diagnosedAt) >= weekAgo;
      }).length,
    };
  }, [diagnoses]);

  const handleStatusUpdate = async (id: string, status: 'confirmed' | 'rejected' | 'treated') => {
    setIsUpdating(true);
    try {
      await updateDiagnosisStatus(id, status);
      setDiagnoses((prev) =>
        prev.map((d) => (d.id === id ? { ...d, status } : d))
      );
      if (selectedDiagnosis?.id === id) {
        setSelectedDiagnosis({ ...selectedDiagnosis, status });
      }
    } catch (error) {
      console.error('Failed to update status:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const openModal = (diagnosis: DiagnosisRecord) => {
    setSelectedDiagnosis(diagnosis);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedDiagnosis(null);
  };

  return (
    <div className="p-6">
      <Header
        title="إدارة الأمراض"
        subtitle="تشخيصات سهول فيجن للذكاء الاصطناعي"
      />

      {/* Stats Summary */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
          <p className="text-sm text-gray-500">إجمالي التشخيصات</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <p className="text-2xl font-bold text-amber-600">{stats.pending}</p>
          <p className="text-sm text-gray-500">قيد المراجعة</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <p className="text-2xl font-bold text-red-600">{stats.critical}</p>
          <p className="text-sm text-gray-500">حالات حرجة</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-100">
          <p className="text-2xl font-bold text-blue-600">{stats.thisWeek}</p>
          <p className="text-sm text-gray-500">هذا الأسبوع</p>
        </div>
      </div>

      {/* Filters */}
      <div className="mt-6 bg-white rounded-xl p-4 border border-gray-100">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="بحث بالمرض أو المزرعة..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          {/* Severity Filter */}
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            {SEVERITY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>

          {/* Actions */}
          <button
            onClick={loadDiagnoses}
            className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            title="تحديث"
          >
            <RefreshCw className={cn('w-5 h-5 text-gray-600', isLoading && 'animate-spin')} />
          </button>
          <button
            className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            title="تصدير"
          >
            <Download className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </div>

      {/* Diagnoses Grid */}
      {isLoading ? (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-gray-200 animate-pulse rounded-xl h-64"></div>
          ))}
        </div>
      ) : filteredDiagnoses.length === 0 ? (
        <div className="mt-6 bg-white rounded-xl p-12 text-center border border-gray-100">
          <Bug className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">لا توجد تشخيصات مطابقة للبحث</p>
        </div>
      ) : (
        <>
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {paginatedDiagnoses.map((diagnosis) => (
              <div
                key={diagnosis.id}
                className="bg-white rounded-xl border border-gray-100 overflow-hidden hover:shadow-lg transition-all cursor-pointer"
                onClick={() => openModal(diagnosis)}
              >
                {/* Image Placeholder */}
                <div className="relative h-40 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                  <Bug className="w-16 h-16 text-gray-300" />
                  <div className="absolute top-3 right-3">
                    <AlertBadge severity={diagnosis.severity} />
                  </div>
                  <div className="absolute top-3 left-3">
                    <StatusBadge status={diagnosis.status} />
                  </div>
                  <div className="absolute bottom-3 left-3 bg-black/60 text-white px-2 py-1 rounded text-sm font-bold">
                    {diagnosis.confidence.toFixed(0)}% دقة
                  </div>
                </div>

                {/* Content */}
                <div className="p-4">
                  <h3 className="font-bold text-gray-900 mb-1">{diagnosis.diseaseNameAr}</h3>
                  <p className="text-sm text-gray-500 mb-3">{diagnosis.diseaseName}</p>

                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2 text-gray-600">
                      <MapPin className="w-4 h-4" />
                      <span>{diagnosis.farmName}</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <Calendar className="w-4 h-4" />
                      <span>{formatDate(diagnosis.diagnosedAt)}</span>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  {diagnosis.status === 'pending' && (
                    <div className="mt-4 flex gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleStatusUpdate(diagnosis.id, 'confirmed');
                        }}
                        className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-green-50 text-green-700 rounded-lg text-sm font-medium hover:bg-green-100 transition-colors"
                        disabled={isUpdating}
                      >
                        <Check className="w-4 h-4" />
                        تأكيد
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleStatusUpdate(diagnosis.id, 'rejected');
                        }}
                        className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-red-50 text-red-700 rounded-lg text-sm font-medium hover:bg-red-100 transition-colors"
                        disabled={isUpdating}
                      >
                        <X className="w-4 h-4" />
                        رفض
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-center gap-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
              <span className="px-4 py-2 text-sm">
                صفحة {currentPage} من {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
            </div>
          )}
        </>
      )}

      {/* Detail Modal */}
      {isModalOpen && selectedDiagnosis && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/50"
            onClick={closeModal}
          ></div>

          {/* Modal Content */}
          <div className="relative bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-slide-up">
            {/* Close Button */}
            <button
              onClick={closeModal}
              className="absolute top-4 left-4 p-2 hover:bg-gray-100 rounded-lg transition-colors z-10"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Image */}
            <div className="relative h-64 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
              <Bug className="w-24 h-24 text-gray-300" />
              <div className="absolute bottom-4 right-4 flex gap-2">
                <AlertBadge severity={selectedDiagnosis.severity} />
                <StatusBadge status={selectedDiagnosis.status} />
              </div>
            </div>

            {/* Details */}
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    {selectedDiagnosis.diseaseNameAr}
                  </h2>
                  <p className="text-gray-500">{selectedDiagnosis.diseaseName}</p>
                </div>
                <div className="text-left">
                  <p className="text-3xl font-bold text-sahool-600">
                    {selectedDiagnosis.confidence.toFixed(1)}%
                  </p>
                  <p className="text-sm text-gray-500">دقة التشخيص</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500 mb-1">المزرعة</p>
                  <p className="font-medium">{selectedDiagnosis.farmName}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500 mb-1">نوع المحصول</p>
                  <p className="font-medium">{selectedDiagnosis.cropType}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500 mb-1">الموقع</p>
                  <p className="font-medium text-sm">
                    {selectedDiagnosis.location.lat.toFixed(4)}, {selectedDiagnosis.location.lng.toFixed(4)}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500 mb-1">تاريخ التشخيص</p>
                  <p className="font-medium">{formatDate(selectedDiagnosis.diagnosedAt)}</p>
                </div>
              </div>

              {/* Treatment Recommendation */}
              {(selectedDiagnosis as DiagnosisRecord & { treatment?: { recommendation?: string; recommendationAr?: string } }).treatment && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                  <h3 className="font-bold text-green-800 mb-2 flex items-center gap-2">
                    <Pill className="w-5 h-5" />
                    توصية العلاج
                  </h3>
                  <p className="text-green-700">
                    {(selectedDiagnosis as DiagnosisRecord & { treatment?: { recommendation?: string; recommendationAr?: string } }).treatment?.recommendationAr ||
                      (selectedDiagnosis as DiagnosisRecord & { treatment?: { recommendation?: string; recommendationAr?: string } }).treatment?.recommendation}
                  </p>
                </div>
              )}

              {/* Expert Review */}
              {selectedDiagnosis.expertReview && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <h3 className="font-bold text-blue-800 mb-2">مراجعة الخبير</h3>
                  <p className="text-blue-700 mb-2">{selectedDiagnosis.expertReview.notes}</p>
                  <p className="text-sm text-blue-600">
                    بواسطة: {selectedDiagnosis.expertReview.expertName} •{' '}
                    {formatDate(selectedDiagnosis.expertReview.reviewedAt)}
                  </p>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3">
                {selectedDiagnosis.status === 'pending' && (
                  <>
                    <button
                      onClick={() => handleStatusUpdate(selectedDiagnosis.id, 'confirmed')}
                      disabled={isUpdating}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50"
                    >
                      <Check className="w-5 h-5" />
                      تأكيد التشخيص
                    </button>
                    <button
                      onClick={() => handleStatusUpdate(selectedDiagnosis.id, 'rejected')}
                      disabled={isUpdating}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors disabled:opacity-50"
                    >
                      <X className="w-5 h-5" />
                      رفض
                    </button>
                  </>
                )}
                {selectedDiagnosis.status === 'confirmed' && (
                  <button
                    onClick={() => handleStatusUpdate(selectedDiagnosis.id, 'treated')}
                    disabled={isUpdating}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-sahool-600 text-white rounded-lg font-medium hover:bg-sahool-700 transition-colors disabled:opacity-50"
                  >
                    <Pill className="w-5 h-5" />
                    تم العلاج
                  </button>
                )}
                <button
                  onClick={() => window.open(`https://maps.google.com/?q=${selectedDiagnosis.location.lat},${selectedDiagnosis.location.lng}`, '_blank')}
                  className="px-4 py-3 border border-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                >
                  <MapPin className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function DiseasesPage() {
  return (
    <Suspense fallback={
      <div className="p-6 flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-sahool-600" />
      </div>
    }>
      <DiseasesContent />
    </Suspense>
  );
}
