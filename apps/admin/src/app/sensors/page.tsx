'use client';

// IoT Sensors Management Page - Dynamic with Full CRUD
// صفحة إدارة المستشعرات - ديناميكية مع جميع عمليات CRUD

import { useEffect, useState, useMemo, useCallback } from 'react';
import { useToast } from '@/components/ui/Toast';
import Header from '@/components/layout/Header';
import DataTable from '@/components/ui/DataTable';
import { formatDate, cn } from '@/lib/utils';
import {
  Cpu,
  Thermometer,
  Droplets,
  Camera,
  Activity,
  Search,
  Plus,
  RefreshCw,
  Edit,
  Trash2,
  X,
  Save,
  Zap,
  AlertTriangle,
} from 'lucide-react';
import { logger } from '../../lib/logger';
import { iotService, type IoTDevice, type CreateDeviceData, type SensorReading } from '@/lib/api';

export default function SensorsPage() {
  const { toast } = useToast();
  const [devices, setDevices] = useState<IoTDevice[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedDevice, setSelectedDevice] = useState<IoTDevice | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showReadingsModal, setShowReadingsModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [loadingReadings, setLoadingReadings] = useState(false);

  const loadDevices = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await iotService.getAll({
        page,
        limit: 20,
        search: searchQuery || undefined,
        type: typeFilter || undefined,
        status: statusFilter || undefined,
      });

      setDevices(response.data);
      setTotalPages(response.meta.totalPages);
    } catch (error) {
      logger.error('Failed to load IoT devices:', error);
      setDevices([]);
    } finally {
      setIsLoading(false);
    }
  }, [page, typeFilter, statusFilter, searchQuery]);

  useEffect(() => {
    loadDevices();
  }, [loadDevices]);

  async function loadDeviceReadings(deviceId: string) {
    setLoadingReadings(true);
    try {
      const response = await iotService.getReadings(deviceId, {
        // Last 24 hours
        from: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        to: new Date().toISOString(),
      });
      setReadings(response.data);
    } catch (error) {
      logger.error('Failed to load device readings:', error);
      setReadings([]);
    } finally {
      setLoadingReadings(false);
    }
  }

  // CRUD Handlers
  async function handleCreate(data: CreateDeviceData) {
    setIsSubmitting(true);
    try {
      await iotService.create(data);
      await loadDevices();
      setShowCreateModal(false);
      logger.info('IoT device registered successfully');
    } catch (error) {
      logger.error('Failed to register device:', error);
      toast.error('Failed to register device', 'فشل تسجيل الجهاز. يرجى المحاولة مرة أخرى.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleUpdate(
    id: string,
    data: Partial<CreateDeviceData> & { status?: IoTDevice['status'] }
  ) {
    setIsSubmitting(true);
    try {
      await iotService.update(id, data);
      await loadDevices();
      setShowEditModal(false);
      setSelectedDevice(null);
      logger.info('IoT device updated successfully');
    } catch (error) {
      logger.error('Failed to update device:', error);
      toast.error('Failed to update device', 'فشل تحديث الجهاز. يرجى المحاولة مرة أخرى.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete(id: string) {
    setIsSubmitting(true);
    try {
      await iotService.delete(id);
      await loadDevices();
      setShowDeleteModal(false);
      setSelectedDevice(null);
      logger.info('IoT device deleted successfully');
    } catch (error) {
      logger.error('Failed to delete device:', error);
      toast.error('Failed to delete device', 'فشل حذف الجهاز. يرجى المحاولة مرة أخرى.');
    } finally {
      setIsSubmitting(false);
    }
  }

  const stats = useMemo(
    () => ({
      total: devices.length,
      online: devices.filter((d) => d.status === 'online').length,
      offline: devices.filter((d) => d.status === 'offline').length,
      error: devices.filter((d) => d.status === 'error').length,
    }),
    [devices]
  );

  const getDeviceIcon = (type: IoTDevice['type']) => {
    const icons = {
      soil_moisture: Droplets,
      weather_station: Activity,
      camera: Camera,
      flow_meter: Thermometer,
      other: Cpu,
    };
    return icons[type] || Cpu;
  };

  const getDeviceTypeLabel = (type: IoTDevice['type']) => {
    const labels = {
      soil_moisture: 'رطوبة التربة',
      weather_station: 'محطة طقس',
      camera: 'كاميرا',
      flow_meter: 'عداد التدفق',
      other: 'أخرى',
    };
    return labels[type] || type;
  };

  const getStatusColor = (status: IoTDevice['status']) => {
    const colors = {
      online: 'bg-green-100 text-green-800',
      offline: 'bg-gray-100 text-gray-800',
      error: 'bg-red-100 text-red-800',
      maintenance: 'bg-yellow-100 text-yellow-800',
    };
    return colors[status];
  };

  const getStatusLabel = (status: IoTDevice['status']) => {
    const labels = {
      online: 'متصل',
      offline: 'غير متصل',
      error: 'خطأ',
      maintenance: 'صيانة',
    };
    return labels[status];
  };

  const columns = [
    {
      key: 'name',
      header: 'الجهاز',
      render: (device: IoTDevice) => {
        const Icon = getDeviceIcon(device.type);
        return (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sahool-100 rounded-full flex items-center justify-center">
              <Icon className="w-5 h-5 text-sahool-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900 dark:text-gray-100">{device.name}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {getDeviceTypeLabel(device.type)}
              </p>
            </div>
          </div>
        );
      },
    },
    {
      key: 'serialNumber',
      header: 'الرقم التسلسلي',
      render: (device: IoTDevice) => (
        <span className="text-gray-700 dark:text-gray-300 text-sm font-mono" dir="ltr">
          {device.serialNumber}
        </span>
      ),
    },
    {
      key: 'fieldName',
      header: 'الحقل',
      render: (device: IoTDevice) => (
        <span className="text-gray-700 dark:text-gray-300">{device.fieldName || 'غير محدد'}</span>
      ),
    },
    {
      key: 'status',
      header: 'الحالة',
      render: (device: IoTDevice) => (
        <span
          className={cn(
            'px-2 py-1 rounded-full text-xs font-medium',
            getStatusColor(device.status)
          )}
        >
          {getStatusLabel(device.status)}
        </span>
      ),
    },
    {
      key: 'lastReading',
      header: 'آخر قراءة',
      render: (device: IoTDevice) => (
        <div>
          {device.lastReading ? (
            <>
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                {device.lastReadingValue} {device.unit}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {formatDate(device.lastReading)}
              </p>
            </>
          ) : (
            <span className="text-gray-400 text-sm">لا توجد قراءات</span>
          )}
        </div>
      ),
    },
    {
      key: 'battery',
      header: 'البطارية',
      render: (device: IoTDevice) => (
        <div className="flex items-center gap-2">
          {device.batteryLevel !== undefined ? (
            <>
              <Zap
                className={cn(
                  'w-4 h-4',
                  device.batteryLevel > 20 ? 'text-green-500' : 'text-red-500'
                )}
              />
              <span
                className={cn(
                  'text-sm',
                  device.batteryLevel > 20 ? 'text-gray-700 dark:text-gray-300' : 'text-red-600'
                )}
              >
                {device.batteryLevel}%
              </span>
            </>
          ) : (
            <span className="text-gray-400 text-sm">-</span>
          )}
        </div>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (device: IoTDevice) => (
        <div className="flex items-center gap-1">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedDevice(device);
              loadDeviceReadings(device.id);
              setShowReadingsModal(true);
            }}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="عرض القراءات"
          >
            <Activity className="w-4 h-4 text-gray-500 dark:text-gray-400" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedDevice(device);
              setShowEditModal(true);
            }}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="تعديل"
          >
            <Edit className="w-4 h-4 text-blue-500" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSelectedDevice(device);
              setShowDeleteModal(true);
            }}
            className="p-2 hover:bg-red-50 rounded-lg transition-colors"
            title="حذف"
          >
            <Trash2 className="w-4 h-4 text-red-500" />
          </button>
        </div>
      ),
      className: 'w-32',
    },
  ];

  return (
    <div className="p-6">
      <Header title="إدارة المستشعرات وأجهزة IoT" subtitle={`${devices.length} جهاز مسجل`} />

      {/* Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Cpu className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.total}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">إجمالي الأجهزة</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.online}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">متصل</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.offline}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">غير متصل</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.error}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">خطأ</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-100 dark:border-gray-700">
        <div className="flex flex-wrap items-center gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="بحث بالاسم أو الرقم التسلسلي..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الأنواع</option>
            <option value="soil_moisture">رطوبة التربة</option>
            <option value="weather_station">محطة طقس</option>
            <option value="camera">كاميرا</option>
            <option value="flow_meter">عداد التدفق</option>
            <option value="other">أخرى</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الحالات</option>
            <option value="online">متصل</option>
            <option value="offline">غير متصل</option>
            <option value="error">خطأ</option>
            <option value="maintenance">صيانة</option>
          </select>

          <button
            onClick={loadDevices}
            className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            title="تحديث"
          >
            <RefreshCw
              className={cn(
                'w-5 h-5 text-gray-600 dark:text-gray-400',
                isLoading && 'animate-spin'
              )}
            />
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            تسجيل جهاز
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="mt-6">
        {isLoading ? (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-8">
            <div className="animate-pulse space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
              ))}
            </div>
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={devices}
            keyExtractor={(device) => device.id}
            emptyMessage="لا يوجد أجهزة مطابقة للبحث"
          />
        )}
      </div>

      {/* Create Device Modal */}
      {showCreateModal && (
        <DeviceFormModal
          title="تسجيل جهاز جديد"
          onClose={() => setShowCreateModal(false)}
          onSubmit={(data) => handleCreate(data as CreateDeviceData)}
          isSubmitting={isSubmitting}
        />
      )}

      {/* Edit Device Modal */}
      {showEditModal && selectedDevice && (
        <DeviceFormModal
          title="تعديل الجهاز"
          device={selectedDevice}
          onClose={() => {
            setShowEditModal(false);
            setSelectedDevice(null);
          }}
          onSubmit={(data) => handleUpdate(selectedDevice.id, data)}
          isSubmitting={isSubmitting}
        />
      )}

      {/* Device Readings Modal */}
      {showReadingsModal && selectedDevice && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                قراءات الجهاز: {selectedDevice.name}
              </h3>
              <button
                onClick={() => {
                  setShowReadingsModal(false);
                  setSelectedDevice(null);
                }}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {loadingReadings ? (
              <div className="text-center py-8">
                <RefreshCw className="w-8 h-8 animate-spin text-sahool-600 mx-auto mb-2" />
                <p className="text-gray-500">جاري تحميل القراءات...</p>
              </div>
            ) : readings.length > 0 ? (
              <div className="space-y-3">
                {readings.map((reading) => (
                  <div
                    key={reading.id}
                    className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-gray-100">
                          {reading.metric}
                        </p>
                        <p className="text-2xl font-bold text-sahool-600">
                          {reading.value} {reading.unit}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {formatDate(reading.timestamp)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">لا توجد قراءات متاحة</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && selectedDevice && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full">
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">تأكيد الحذف</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              هل أنت متأكد من حذف الجهاز <strong>{selectedDevice.name}</strong>؟ هذا الإجراء لا يمكن
              التراجع عنه.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setSelectedDevice(null);
                }}
                disabled={isSubmitting}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
              >
                إلغاء
              </button>
              <button
                onClick={() => handleDelete(selectedDevice.id)}
                disabled={isSubmitting}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                {isSubmitting ? 'جاري الحذف...' : 'حذف'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            السابق
          </button>
          <span className="px-4 py-2 text-gray-600 dark:text-gray-400">
            صفحة {page} من {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            التالي
          </button>
        </div>
      )}
    </div>
  );
}

// Device Form Modal Component
function DeviceFormModal({
  title,
  device,
  onClose,
  onSubmit,
  isSubmitting,
}: {
  title: string;
  device?: IoTDevice;
  onClose: () => void;
  onSubmit: (
    data: CreateDeviceData | (Partial<CreateDeviceData> & { status?: IoTDevice['status'] })
  ) => void;
  isSubmitting: boolean;
}) {
  const [formData, setFormData] = useState({
    name: device?.name || '',
    type: device?.type || ('soil_moisture' as IoTDevice['type']),
    fieldId: device?.fieldId || '',
    serialNumber: device?.serialNumber || '',
    status: device?.status || ('online' as IoTDevice['status']),
    config: device?.config || {},
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!device) {
      // Create mode
      const createData: CreateDeviceData = {
        name: formData.name,
        type: formData.type,
        fieldId: formData.fieldId,
        serialNumber: formData.serialNumber,
        config: formData.config,
      };
      onSubmit(createData);
    } else {
      // Edit mode
      const updateData = {
        name: formData.name,
        type: formData.type,
        fieldId: formData.fieldId,
        serialNumber: formData.serialNumber,
        status: formData.status,
        config: formData.config,
      };
      onSubmit(updateData);
    }
  };

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{title}</h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              اسم الجهاز
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              نوع الجهاز
            </label>
            <select
              value={formData.type}
              onChange={(e) =>
                setFormData({ ...formData, type: e.target.value as IoTDevice['type'] })
              }
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
            >
              <option value="soil_moisture">رطوبة التربة</option>
              <option value="weather_station">محطة طقس</option>
              <option value="camera">كاميرا</option>
              <option value="flow_meter">عداد التدفق</option>
              <option value="other">أخرى</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              الرقم التسلسلي
            </label>
            <input
              type="text"
              required
              value={formData.serialNumber}
              onChange={(e) => setFormData({ ...formData, serialNumber: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              معرف الحقل
            </label>
            <input
              type="text"
              required
              value={formData.fieldId}
              onChange={(e) => setFormData({ ...formData, fieldId: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
              placeholder="field-123"
            />
          </div>

          {device && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                الحالة
              </label>
              <select
                value={formData.status}
                onChange={(e) =>
                  setFormData({ ...formData, status: e.target.value as IoTDevice['status'] })
                }
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-sahool-500 focus:border-transparent"
              >
                <option value="online">متصل</option>
                <option value="offline">غير متصل</option>
                <option value="error">خطأ</option>
                <option value="maintenance">صيانة</option>
              </select>
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
            >
              إلغاء
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Save className="w-4 h-4" />
              {isSubmitting ? 'جاري الحفظ...' : device ? 'تحديث' : 'تسجيل'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
