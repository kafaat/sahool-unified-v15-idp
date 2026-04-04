'use client';

import React, { useState, useMemo } from 'react';
import {
  Search,
  Activity,
  Gauge,
  Zap,
  Settings,
  AlertTriangle,
  CheckCircle,
  Clock,
  Calculator,
} from 'lucide-react';

type AlgorithmType = 'regression' | 'kalman_filter' | 'neural_network' | 'physics_model' | 'ensemble';
type SensorAccuracy = 'high' | 'medium' | 'low';
type CalibrationStatus = 'calibrated' | 'needs_calibration' | 'auto_calibrating';

interface VirtualSensor {
  id: string;
  name: string;
  nameAr: string;
  parameter: string;
  parameterAr: string;
  algorithm: AlgorithmType;
  accuracy: SensorAccuracy;
  calibrationStatus: CalibrationStatus;
  currentValue: number;
  unit: string;
  inputSensors: string[];
  fieldName: string;
  lastComputed: string;
  confidenceInterval: number;
}

const mockVirtualSensors: VirtualSensor[] = [
  {
    id: 'vs-001',
    name: 'ET Estimation',
    nameAr: 'تقدير التبخر-نتح',
    parameter: 'Evapotranspiration',
    parameterAr: 'التبخر-نتح',
    algorithm: 'physics_model',
    accuracy: 'high',
    calibrationStatus: 'calibrated',
    currentValue: 5.2,
    unit: 'mm/day',
    inputSensors: ['حرارة', 'رطوبة', 'رياح', 'إشعاع'],
    fieldName: 'الحقل الشمالي',
    lastComputed: '2026-04-04T08:00:00Z',
    confidenceInterval: 95,
  },
  {
    id: 'vs-002',
    name: 'Soil Nitrogen Estimate',
    nameAr: 'تقدير نيتروجين التربة',
    parameter: 'Nitrogen',
    parameterAr: 'النيتروجين',
    algorithm: 'neural_network',
    accuracy: 'medium',
    calibrationStatus: 'auto_calibrating',
    currentValue: 22.5,
    unit: 'ppm',
    inputSensors: ['NDVI', 'رطوبة التربة', 'درجة الحرارة'],
    fieldName: 'حقل القمح',
    lastComputed: '2026-04-04T07:45:00Z',
    confidenceInterval: 82,
  },
  {
    id: 'vs-003',
    name: 'Crop Water Stress Index',
    nameAr: 'مؤشر إجهاد المحصول المائي',
    parameter: 'CWSI',
    parameterAr: 'م.إ.م.م',
    algorithm: 'ensemble',
    accuracy: 'high',
    calibrationStatus: 'calibrated',
    currentValue: 0.35,
    unit: '',
    inputSensors: ['حرارة الغطاء', 'حرارة الهواء', 'رطوبة نسبية'],
    fieldName: 'الحقل الجنوبي',
    lastComputed: '2026-04-04T08:10:00Z',
    confidenceInterval: 91,
  },
  {
    id: 'vs-004',
    name: 'LAI Estimation',
    nameAr: 'تقدير مؤشر مساحة الورقة',
    parameter: 'Leaf Area Index',
    parameterAr: 'مؤشر مساحة الورقة',
    algorithm: 'regression',
    accuracy: 'medium',
    calibrationStatus: 'needs_calibration',
    currentValue: 3.8,
    unit: 'm2/m2',
    inputSensors: ['NDVI', 'إشعاع شمسي'],
    fieldName: 'بستان النخيل',
    lastComputed: '2026-04-04T06:30:00Z',
    confidenceInterval: 75,
  },
  {
    id: 'vs-005',
    name: 'Soil Salinity Predictor',
    nameAr: 'مؤشر ملوحة التربة',
    parameter: 'EC',
    parameterAr: 'التوصيلية الكهربائية',
    algorithm: 'kalman_filter',
    accuracy: 'high',
    calibrationStatus: 'calibrated',
    currentValue: 2.1,
    unit: 'dS/m',
    inputSensors: ['رطوبة التربة', 'حرارة التربة', 'EC سابقة'],
    fieldName: 'الصوب الزراعية',
    lastComputed: '2026-04-04T08:05:00Z',
    confidenceInterval: 88,
  },
  {
    id: 'vs-006',
    name: 'Disease Risk Score',
    nameAr: 'درجة خطر الأمراض',
    parameter: 'Risk Score',
    parameterAr: 'درجة الخطر',
    algorithm: 'ensemble',
    accuracy: 'low',
    calibrationStatus: 'needs_calibration',
    currentValue: 62,
    unit: '%',
    inputSensors: ['رطوبة', 'حرارة', 'مدة البلل', 'NDVI'],
    fieldName: 'حقل القمح',
    lastComputed: '2026-04-04T07:00:00Z',
    confidenceInterval: 68,
  },
];

const algorithmLabels: Record<AlgorithmType, string> = {
  regression: 'انحدار خطي',
  kalman_filter: 'مرشح كالمان',
  neural_network: 'شبكة عصبية',
  physics_model: 'نموذج فيزيائي',
  ensemble: 'نموذج مجمع',
};

export default function VirtualSensorsClient() {
  const [searchTerm, setSearchTerm] = useState('');
  const [accuracyFilter, setAccuracyFilter] = useState<SensorAccuracy | 'all'>('all');

  const filteredSensors = useMemo(() => {
    return mockVirtualSensors.filter((sensor) => {
      const matchesSearch =
        !searchTerm ||
        sensor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        sensor.nameAr.includes(searchTerm);
      const matchesAccuracy = accuracyFilter === 'all' || sensor.accuracy === accuracyFilter;
      return matchesSearch && matchesAccuracy;
    });
  }, [searchTerm, accuracyFilter]);

  const getAccuracyBadge = (accuracy: SensorAccuracy) => {
    const styles: Record<SensorAccuracy, string> = {
      high: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-red-100 text-red-800',
    };
    const labels: Record<SensorAccuracy, string> = { high: 'عالية', medium: 'متوسطة', low: 'منخفضة' };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[accuracy]}`}>
        {labels[accuracy]}
      </span>
    );
  };

  const getCalibrationIcon = (status: CalibrationStatus) => {
    if (status === 'calibrated') return <CheckCircle className="w-4 h-4 text-green-500" />;
    if (status === 'auto_calibrating') return <Settings className="w-4 h-4 text-blue-500 animate-spin" />;
    return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
  };

  const getCalibrationLabel = (status: CalibrationStatus) => {
    const labels: Record<CalibrationStatus, string> = {
      calibrated: 'معاير',
      needs_calibration: 'يحتاج معايرة',
      auto_calibrating: 'معايرة تلقائية',
    };
    return labels[status];
  };

  const calibratedCount = mockVirtualSensors.filter((s) => s.calibrationStatus === 'calibrated').length;
  const needsCalibration = mockVirtualSensors.filter((s) => s.calibrationStatus === 'needs_calibration').length;

  return (
    <div className="space-y-6" dir="rtl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">المستشعرات الافتراضية</h1>
          <p className="text-gray-500 mt-1">Virtual Sensors</p>
        </div>
      </div>

      {/* Alerts */}
      {needsCalibration > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-600" />
            <span className="font-medium text-yellow-800">
              {needsCalibration} مستشعر يحتاج إعادة معايرة لتحسين الدقة
            </span>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
              <Calculator className="w-5 h-5 text-indigo-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">إجمالي المستشعرات</div>
              <div className="text-xl font-bold text-gray-900">{mockVirtualSensors.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">معاير</div>
              <div className="text-xl font-bold text-green-600">{calibratedCount}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Gauge className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">يحتاج معايرة</div>
              <div className="text-xl font-bold text-yellow-600">{needsCalibration}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">متوسط الثقة</div>
              <div className="text-xl font-bold text-blue-600">
                {Math.round(mockVirtualSensors.reduce((s, v) => s + v.confidenceInterval, 0) / mockVirtualSensors.length)}%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="بحث عن مستشعر افتراضي..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pr-10 pl-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
          />
        </div>
        <select
          value={accuracyFilter}
          onChange={(e) => setAccuracyFilter(e.target.value as SensorAccuracy | 'all')}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
        >
          <option value="all">جميع مستويات الدقة</option>
          <option value="high">دقة عالية</option>
          <option value="medium">دقة متوسطة</option>
          <option value="low">دقة منخفضة</option>
        </select>
      </div>

      {/* Sensors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredSensors.map((sensor) => (
          <div key={sensor.id} className="bg-white rounded-lg border p-5 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-medium text-gray-900">{sensor.nameAr}</h3>
                <p className="text-sm text-gray-500">{sensor.fieldName}</p>
              </div>
              {getAccuracyBadge(sensor.accuracy)}
            </div>

            <div className="text-center py-4 mb-3 bg-gray-50 rounded-lg">
              <div className="text-3xl font-bold text-gray-900">
                {sensor.currentValue}
                <span className="text-sm font-normal text-gray-500 mr-1">{sensor.unit}</span>
              </div>
              <div className="text-sm text-gray-500 mt-1">{sensor.parameterAr}</div>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-500">الخوارزمية</span>
                <span className="font-medium text-gray-700">{algorithmLabels[sensor.algorithm]}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-500">المعايرة</span>
                <div className="flex items-center gap-1">
                  {getCalibrationIcon(sensor.calibrationStatus)}
                  <span className="text-gray-700">{getCalibrationLabel(sensor.calibrationStatus)}</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-500">فاصل الثقة</span>
                <span className="font-medium text-gray-700">{sensor.confidenceInterval}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-500">المدخلات</span>
                <span className="text-gray-700 text-xs">{sensor.inputSensors.join(' , ')}</span>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t flex justify-between items-center">
              <div className="flex items-center gap-1 text-xs text-gray-400">
                <Clock className="w-3 h-3" />
                <span>{new Date(sensor.lastComputed).toLocaleTimeString('ar-SA')}</span>
              </div>
              <button
                disabled
                title="قريبا - Coming soon"
                className="text-green-600 hover:text-green-700 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                إعدادات
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
