'use client';

import React, { useState, useMemo } from 'react';
import {
  FileText,
  Plus,
  Search,
  AlertTriangle,
  Download,
  Trash2,
  Shield,
  FileCheck,
  File,
  Clock,
  X,
} from 'lucide-react';
import {
  useDocuments,
  useDocumentStats,
  useUploadDocument,
  useDeleteDocument,
  documentsApi,
} from '@/features/documents';
import type { DocumentCategory, DocumentStatus } from '@/features/documents';

// File upload validation constants
const MAX_UPLOAD_SIZE_BYTES = 20 * 1024 * 1024; // 20 MB
const ALLOWED_MIME_TYPES = new Set<string>([
  'application/pdf',
  'image/jpeg',
  'image/png',
  'image/webp',
  'image/gif',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
  'application/msword', // .doc
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
  'application/vnd.ms-excel', // .xls
  'text/csv',
  'text/plain',
]);
const ALLOWED_EXTENSIONS = new Set<string>([
  'pdf', 'jpg', 'jpeg', 'png', 'webp', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'txt',
]);
const MAX_TITLE_LENGTH = 200;

/** Strip control chars and common XSS-prone characters from user-supplied titles. */
function sanitizeTitle(input: string): string {
  // Remove control characters (0x00-0x1F, 0x7F), zero-width chars, and trim
  // eslint-disable-next-line no-control-regex
  return input.replace(/[\u0000-\u001F\u007F\u200B-\u200F\u2028-\u202F]/g, '').trim().slice(0, MAX_TITLE_LENGTH);
}

/** Validate file extension, MIME, and size. Returns error message (Arabic) or null if valid. */
function validateUploadFile(file: File | null): string | null {
  if (!file) return 'يرجى اختيار ملف';
  if (file.size === 0) return 'الملف فارغ';
  if (file.size > MAX_UPLOAD_SIZE_BYTES) {
    return `حجم الملف يتجاوز الحد المسموح (${MAX_UPLOAD_SIZE_BYTES / (1024 * 1024)} MB)`;
  }
  const ext = file.name.split('.').pop()?.toLowerCase() ?? '';
  if (!ALLOWED_EXTENSIONS.has(ext)) {
    return `امتداد الملف غير مسموح (.${ext})`;
  }
  // MIME type check — some browsers leave it empty; allow empty only if extension matches
  if (file.type && !ALLOWED_MIME_TYPES.has(file.type)) {
    return `نوع الملف غير مسموح (${file.type})`;
  }
  return null;
}

const categoryConfig: Record<
  DocumentCategory,
  { labelAr: string; icon: React.ElementType; color: string }
> = {
  compliance: { labelAr: 'امتثال', icon: Shield, color: 'text-blue-600' },
  permits: { labelAr: 'تصاريح', icon: FileCheck, color: 'text-green-600' },
  contracts: { labelAr: 'عقود', icon: FileText, color: 'text-purple-600' },
  reports: { labelAr: 'تقارير', icon: File, color: 'text-orange-600' },
  certificates: { labelAr: 'شهادات', icon: FileCheck, color: 'text-yellow-600' },
  maps: { labelAr: 'خرائط', icon: File, color: 'text-cyan-600' },
  invoices: { labelAr: 'فواتير', icon: File, color: 'text-pink-600' },
  other: { labelAr: 'أخرى', icon: File, color: 'text-gray-600' },
};

const statusConfig: Record<DocumentStatus, { color: string; labelAr: string }> = {
  draft: { color: 'bg-gray-100 text-gray-800', labelAr: 'مسودة' },
  active: { color: 'bg-green-100 text-green-800', labelAr: 'نشط' },
  expired: { color: 'bg-red-100 text-red-800', labelAr: 'منتهي' },
  archived: { color: 'bg-yellow-100 text-yellow-800', labelAr: 'مؤرشف' },
};

const categoryOptions: Array<{ value: DocumentCategory | 'all'; labelAr: string }> = [
  { value: 'all', labelAr: 'جميع الفئات' },
  { value: 'compliance', labelAr: 'امتثال' },
  { value: 'permits', labelAr: 'تصاريح' },
  { value: 'contracts', labelAr: 'عقود' },
  { value: 'reports', labelAr: 'تقارير' },
  { value: 'certificates', labelAr: 'شهادات' },
  { value: 'maps', labelAr: 'خرائط' },
  { value: 'invoices', labelAr: 'فواتير' },
];

function formatFileSize(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes < 0) return '0 B';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * Strip bidi overrides, zero-width chars, and control characters from strings
 * shown in the document table to prevent filename/title spoofing attacks.
 * React already escapes HTML — this guards against visual deception, not XSS.
 */
function sanitizeDisplay(input: string | undefined | null): string {
  if (!input) return '';
  // eslint-disable-next-line no-control-regex
  return input.replace(/[\u0000-\u001F\u007F\u200B-\u200F\u202A-\u202E\u2066-\u2069]/g, '').slice(0, 300);
}

export default function DocumentsClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<DocumentCategory | 'all'>('all');
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadTitleAr, setUploadTitleAr] = useState('');
  const [uploadCategory, setUploadCategory] = useState<DocumentCategory>('reports');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const uploadDocument = useUploadDocument();
  const deleteDocument = useDeleteDocument();

  const handleFileChange = (file: File | null) => {
    setUploadFile(file);
    const err = file ? validateUploadFile(file) : null;
    setUploadError(err);
  };

  const handleUpload = () => {
    const cleanTitleAr = sanitizeTitle(uploadTitleAr);
    const cleanTitle = sanitizeTitle(uploadTitle);
    if (!uploadFile || !cleanTitleAr) {
      setUploadError('يرجى إكمال الحقول المطلوبة');
      return;
    }
    const fileError = validateUploadFile(uploadFile);
    if (fileError) {
      setUploadError(fileError);
      return;
    }
    const formData = new FormData();
    formData.append('title', cleanTitle);
    formData.append('titleAr', cleanTitleAr);
    formData.append('category', uploadCategory);
    formData.append('file', uploadFile);
    uploadDocument.mutate(formData, {
      onSuccess: () => {
        setShowUploadDialog(false);
        setUploadTitle('');
        setUploadTitleAr('');
        setUploadCategory('reports');
        setUploadFile(null);
        setUploadError(null);
      },
      onError: (err) => {
        setUploadError(err instanceof Error ? err.message : 'فشل في رفع الملف');
      },
    });
  };

  const handleDownload = async (id: string, fileName: string) => {
    try {
      const blob = await documentsApi.downloadDocument(id);
      // Sanitize filename before using in href/download to avoid injection
      const safeName = fileName.replace(/[\u0000-\u001F\u007F<>:"/\\|?*]/g, '_').slice(0, 200);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = safeName || 'document';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      // Swallowed; the hook/query layer surfaces errors globally
    }
  };

  const handleDelete = (id: string) => {
    if (typeof window !== 'undefined' && !window.confirm('هل أنت متأكد من حذف هذه الوثيقة؟')) {
      return;
    }
    deleteDocument.mutate(id);
  };

  const {
    data: documents = [],
    isLoading,
    error,
  } = useDocuments(selectedCategory !== 'all' ? { category: selectedCategory } : undefined);
  const { data: stats } = useDocumentStats();

  const filteredDocs = useMemo(() => {
    if (!searchTerm) return documents;
    const term = searchTerm.toLowerCase();
    return documents.filter(
      (d) =>
        d.title.toLowerCase().includes(term) ||
        d.titleAr.includes(searchTerm) ||
        d.tags.some((t) => t.toLowerCase().includes(term))
    );
  }, [documents, searchTerm]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sahool-green-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-600">فشل في تحميل الوثائق</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Upload Dialog */}
      {showUploadDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6 relative">
            <button onClick={() => setShowUploadDialog(false)} className="absolute top-3 left-3 text-gray-400 hover:text-gray-600">
              <X className="w-5 h-5" />
            </button>
            <h2 className="text-lg font-bold text-gray-900 mb-1">رفع وثيقة جديدة</h2>
            <p className="text-sm text-gray-500 mb-4">Upload New Document</p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">عنوان الوثيقة (عربي)</label>
                <input type="text" value={uploadTitleAr} onChange={(e) => setUploadTitleAr(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" placeholder="أدخل العنوان بالعربية" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">عنوان الوثيقة (إنجليزي)</label>
                <input type="text" value={uploadTitle} onChange={(e) => setUploadTitle(e.target.value)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500" placeholder="Enter title in English" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الفئة</label>
                <select value={uploadCategory} onChange={(e) => setUploadCategory(e.target.value as DocumentCategory)} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500">
                  <option value="compliance">امتثال</option>
                  <option value="permits">تصاريح</option>
                  <option value="contracts">عقود</option>
                  <option value="reports">تقارير</option>
                  <option value="certificates">شهادات</option>
                  <option value="maps">خرائط</option>
                  <option value="invoices">فواتير</option>
                  <option value="other">أخرى</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الملف</label>
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png,.webp,.gif,.doc,.docx,.xls,.xlsx,.csv,.txt,application/pdf,image/*"
                  onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 text-sm"
                />
                <p className="text-xs text-gray-500 mt-1">الحد الأقصى: 20 ميجابايت | PDF, JPG, PNG, DOCX, XLSX, CSV</p>
              </div>
              {uploadError && (
                <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
                  {uploadError}
                </div>
              )}
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button onClick={() => { setShowUploadDialog(false); setUploadError(null); }} className="px-4 py-2 text-sm text-gray-600 border rounded-lg hover:bg-gray-50">إلغاء</button>
              <button onClick={handleUpload} disabled={uploadDocument.isPending || !uploadFile || !uploadTitleAr || !!uploadError} className="px-4 py-2 text-sm text-white bg-sahool-green-600 rounded-lg hover:bg-sahool-green-700 disabled:opacity-50">
                {uploadDocument.isPending ? 'جاري الرفع...' : 'رفع'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">الوثائق</h1>
          <p className="text-gray-500 mt-1">Documents & Records</p>
        </div>
        <button
          onClick={() => setShowUploadDialog(true)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-sahool-green-600 text-white rounded-lg hover:bg-sahool-green-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>رفع وثيقة</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">إجمالي الوثائق</div>
          <div className="text-2xl font-bold text-gray-900">
            {stats?.totalDocuments ?? documents.length}
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">نشطة</div>
          <div className="text-2xl font-bold text-green-600">{stats?.activeDocuments ?? 0}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <Clock className="w-3.5 h-3.5" /> تنتهي قريباً
          </div>
          <div className="text-2xl font-bold text-yellow-600">{stats?.expiringDocuments ?? 0}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">الحجم الكلي</div>
          <div className="text-2xl font-bold text-blue-600">{stats?.totalSizeMb ?? 0} MB</div>
        </div>
      </div>

      {/* Expiry Alert */}
      {(stats?.expiringDocuments ?? 0) > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
            <span className="font-medium text-amber-800">
              تنبيه: {stats?.expiringDocuments} وثيقة تنتهي صلاحيتها خلال 30 يوم
            </span>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث في الوثائق..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500 focus:border-sahool-green-500"
          />
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value as DocumentCategory | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          {categoryOptions.map((c) => (
            <option key={c.value} value={c.value}>
              {c.labelAr}
            </option>
          ))}
        </select>
      </div>

      {/* Document List */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الوثيقة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الفئة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">المزرعة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحجم</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">الحالة</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">
                  تاريخ الانتهاء
                </th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">
                  الإجراءات
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredDocs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                    لا توجد وثائق
                  </td>
                </tr>
              ) : (
                filteredDocs.map((doc) => {
                  const cat = categoryConfig[doc.category];
                  const st = statusConfig[doc.status];
                  const CatIcon = cat.icon;
                  return (
                    <tr key={doc.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <CatIcon className={`w-5 h-5 ${cat.color}`} />
                          <div>
                            <div className="font-medium text-gray-900" title={sanitizeDisplay(doc.titleAr)}>
                              {sanitizeDisplay(doc.titleAr)}
                            </div>
                            <div className="text-xs text-gray-500 truncate max-w-[260px]" title={sanitizeDisplay(doc.fileName)}>
                              {sanitizeDisplay(doc.fileName)}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">{cat.labelAr}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{doc.farmNameAr || '—'}</td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {formatFileSize(doc.fileSize)}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${st.color}`}>
                          {st.labelAr}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {doc.expiryDate
                          ? new Date(doc.expiryDate).toLocaleDateString('ar-SA')
                          : '—'}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            aria-label="تنزيل الوثيقة"
                            onClick={() => handleDownload(doc.id, doc.fileName)}
                            className="p-1.5 text-sahool-green-600 hover:bg-sahool-green-50 rounded disabled:opacity-50"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                          <button
                            type="button"
                            aria-label="حذف الوثيقة"
                            onClick={() => handleDelete(doc.id)}
                            disabled={deleteDocument.isPending}
                            className="p-1.5 text-red-500 hover:bg-red-50 rounded disabled:opacity-50"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
