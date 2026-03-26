'use client';

import React, { useState } from 'react';
import { Thermometer, TrendingUp, Calendar, Target, Leaf, BarChart3 } from 'lucide-react';

interface GDDRecord {
  id: string;
  fieldId: string;
  fieldName: string;
  cropType: string;
  cropTypeAr: string;
  plantingDate: string;
  currentGDD: number;
  targetGDD: number;
  currentStage: string;
  currentStageAr: string;
  nextStage: string;
  nextStageAr: string;
  gddToNextStage: number;
  estimatedDaysToNextStage: number;
}

const mockGDDRecords: GDDRecord[] = [
  {
    id: '1',
    fieldId: 'field-1',
    fieldName: 'الحقل الشمالي',
    cropType: 'Wheat',
    cropTypeAr: 'قمح',
    plantingDate: '2024-11-15',
    currentGDD: 850,
    targetGDD: 2100,
    currentStage: 'Tillering',
    currentStageAr: 'التفريع',
    nextStage: 'Stem Elongation',
    nextStageAr: 'استطالة الساق',
    gddToNextStage: 250,
    estimatedDaysToNextStage: 18,
  },
  {
    id: '2',
    fieldId: 'field-2',
    fieldName: 'الحقل الجنوبي',
    cropType: 'Barley',
    cropTypeAr: 'شعير',
    plantingDate: '2024-11-20',
    currentGDD: 720,
    targetGDD: 1800,
    currentStage: 'Tillering',
    currentStageAr: 'التفريع',
    nextStage: 'Jointing',
    nextStageAr: 'التعقيل',
    gddToNextStage: 180,
    estimatedDaysToNextStage: 14,
  },
  {
    id: '3',
    fieldId: 'field-3',
    fieldName: 'حقل القمح',
    cropType: 'Wheat',
    cropTypeAr: 'قمح',
    plantingDate: '2024-11-10',
    currentGDD: 920,
    targetGDD: 2100,
    currentStage: 'Stem Elongation',
    currentStageAr: 'استطالة الساق',
    nextStage: 'Heading',
    nextStageAr: 'طرد السنابل',
    gddToNextStage: 380,
    estimatedDaysToNextStage: 28,
  },
  {
    id: '4',
    fieldId: 'field-5',
    fieldName: 'الصوب الزراعية',
    cropType: 'Tomato',
    cropTypeAr: 'طماطم',
    plantingDate: '2024-12-01',
    currentGDD: 580,
    targetGDD: 1500,
    currentStage: 'Flowering',
    currentStageAr: 'الإزهار',
    nextStage: 'Fruiting',
    nextStageAr: 'الإثمار',
    gddToNextStage: 120,
    estimatedDaysToNextStage: 10,
  },
];

export default function GDDClient() {
  const [selectedField, setSelectedField] = useState<string>('all');

  const filteredRecords =
    selectedField === 'all'
      ? mockGDDRecords
      : mockGDDRecords.filter((r) => r.fieldId === selectedField);

  const getProgressPercentage = (current: number, target: number) => {
    return Math.min((current / target) * 100, 100);
  };

  const getProgressColor = (percentage: number) => {
    if (percentage < 33) return 'bg-blue-500';
    if (percentage < 66) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const averageGDD = Math.round(
    mockGDDRecords.reduce((sum, r) => sum + r.currentGDD, 0) / mockGDDRecords.length
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">درجات النمو الحراري</h1>
          <p className="text-gray-500 mt-1">Growing Degree Days (GDD)</p>
        </div>
        <select
          value={selectedField}
          onChange={(e) => setSelectedField(e.target.value)}
          className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sahool-green-500"
        >
          <option value="all">جميع الحقول</option>
          {mockGDDRecords.map((record) => (
            <option key={record.fieldId} value={record.fieldId}>
              {record.fieldName}
            </option>
          ))}
        </select>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <Thermometer className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">متوسط GDD</div>
              <div className="text-xl font-bold text-gray-900">{averageGDD}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Leaf className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">حقول مراقبة</div>
              <div className="text-xl font-bold text-green-600">{mockGDDRecords.length}</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">أقرب مرحلة</div>
              <div className="text-xl font-bold text-blue-600">10 أيام</div>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-sm text-gray-500">معدل التراكم</div>
              <div className="text-xl font-bold text-purple-600">14 GDD/يوم</div>
            </div>
          </div>
        </div>
      </div>

      {/* GDD Chart Placeholder */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">تراكم درجات النمو الحراري</h2>
          <BarChart3 className="w-5 h-5 text-gray-400" />
        </div>
        <div className="h-48 flex items-center justify-center bg-gray-50 rounded-lg">
          <p className="text-gray-500">الرسم البياني للتراكم الحراري</p>
        </div>
      </div>

      {/* Field Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredRecords.map((record) => {
          const progress = getProgressPercentage(record.currentGDD, record.targetGDD);
          return (
            <div key={record.id} className="bg-white rounded-lg border p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-gray-900">{record.fieldName}</h3>
                  <p className="text-sm text-gray-500">{record.cropTypeAr}</p>
                </div>
                <span className="px-3 py-1 bg-sahool-green-100 text-sahool-green-800 rounded-full text-sm font-medium">
                  {record.currentStageAr}
                </span>
              </div>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-500">التقدم</span>
                  <span className="font-medium text-gray-900">
                    {record.currentGDD} / {record.targetGDD} GDD
                  </span>
                </div>
                <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${getProgressColor(progress)} transition-all duration-500`}
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>

              {/* Next Stage Info */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Target className="w-4 h-4 text-sahool-green-600" />
                  <span className="font-medium text-gray-900">المرحلة التالية</span>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">المرحلة:</span>
                    <span className="font-medium text-gray-900 mr-1">{record.nextStageAr}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">المتبقي:</span>
                    <span className="font-medium text-gray-900 mr-1">
                      {record.gddToNextStage} GDD
                    </span>
                  </div>
                  <div className="col-span-2">
                    <span className="text-gray-500">الوقت المتوقع:</span>
                    <span className="font-medium text-sahool-green-600 mr-1">
                      {record.estimatedDaysToNextStage} يوم
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t flex items-center justify-between text-sm">
                <span className="text-gray-500">
                  تاريخ الزراعة: {new Date(record.plantingDate).toLocaleDateString('ar-SA')}
                </span>
                <button className="text-sahool-green-600 hover:text-sahool-green-700 font-medium">
                  التفاصيل
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
