/**
 * Sensor Readings Component with Chart
 * مكون قراءات المستشعر مع الرسم البياني
 */

'use client';

import { useState } from 'react';
import { useSensorReadings } from '../hooks/useSensors';
import type { SensorReadingsQuery } from '../types';
import {
  DynamicLineChart as LineChart,
  DynamicLine as Line,
  DynamicXAxis as XAxis,
  DynamicYAxis as YAxis,
  DynamicCartesianGrid as CartesianGrid,
  DynamicTooltip as Tooltip,
  DynamicLegend as Legend,
  DynamicResponsiveContainer as ResponsiveContainer,
} from '@/components/charts/LazyRecharts.dynamic';
import { Calendar, Loader2 } from 'lucide-react';

interface SensorReadingsProps {
  sensorId: string;
  sensorName?: string;
  unit?: string;
  limit?: number;
}

export function SensorReadings({ sensorId, sensorName, unit, limit }: SensorReadingsProps) {
  const [timeInterval, setTimeInterval] = useState<'1h' | '1d' | '1w' | '1m'>('1d');

  const query: SensorReadingsQuery = {
    sensorId,
    interval: timeInterval,
    startDate: getStartDate(timeInterval),
    endDate: new Date().toISOString(),
    limit,
  };

  const { data: readings, isLoading, error } = useSensorReadings(query);

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 h-96 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-green-600" />
        <span className="ms-3 text-gray-600">جاري التحميل...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        حدث خطأ أثناء تحميل القراءات
      </div>
    );
  }

  const chartData =
    readings?.map((reading) => ({
      timestamp: new Date(reading.timestamp).toLocaleString('ar-YE', {
        month: 'short',
        day: 'numeric',
        hour: timeInterval === '1h' ? '2-digit' : undefined,
        minute: timeInterval === '1h' ? '2-digit' : undefined,
      }),
      value: reading.value,
    })) || [];

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <Calendar className="w-5 h-5 ml-2 text-green-600" />
            قراءات {sensorName || 'المستشعر'}
          </h2>

          {/* Interval Selector */}
          <div className="flex gap-2" role="group" aria-label="الفترة الزمنية | Time interval">
            <button
              onClick={() => setTimeInterval('1h')}
              aria-pressed={timeInterval === '1h'}
              className={`px-3 py-1 rounded-lg text-sm ${
                timeInterval === '1h'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              ساعة
            </button>
            <button
              onClick={() => setTimeInterval('1d')}
              aria-pressed={timeInterval === '1d'}
              className={`px-3 py-1 rounded-lg text-sm ${
                timeInterval === '1d'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              يوم
            </button>
            <button
              onClick={() => setTimeInterval('1w')}
              aria-pressed={timeInterval === '1w'}
              className={`px-3 py-1 rounded-lg text-sm ${
                timeInterval === '1w'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              أسبوع
            </button>
            <button
              onClick={() => setTimeInterval('1m')}
              aria-pressed={timeInterval === '1m'}
              className={`px-3 py-1 rounded-lg text-sm ${
                timeInterval === '1m'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              شهر
            </button>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="p-6">
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" style={{ fontSize: '12px' }} />
              <YAxis
                style={{ fontSize: '12px' }}
                label={{
                  value: unit || '',
                  angle: -90,
                  position: 'insideLeft',
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #ccc',
                  borderRadius: '8px',
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="value"
                name={`القيمة${unit ? ` (${unit})` : ''}`}
                stroke="#16a34a"
                strokeWidth={2}
                dot={{ fill: '#16a34a', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500">لا توجد قراءات متاحة</p>
          </div>
        )}
      </div>

      {/* Stats */}
      {readings && readings.length > 0 && (
        <div className="p-6 bg-gray-50 border-t border-gray-200">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">المتوسط</p>
              <p className="text-2xl font-bold text-gray-900">
                {(readings.reduce((sum, r) => sum + r.value, 0) / readings.length).toFixed(2)}{' '}
                {unit || ''}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">الحد الأدنى</p>
              <p className="text-2xl font-bold text-blue-600">
                {Math.min(...readings.map((r) => r.value)).toFixed(2)} {unit || ''}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">الحد الأقصى</p>
              <p className="text-2xl font-bold text-red-600">
                {Math.max(...readings.map((r) => r.value)).toFixed(2)} {unit || ''}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function getStartDate(interval: '1h' | '1d' | '1w' | '1m'): string {
  const now = new Date();
  switch (interval) {
    case '1h':
      now.setHours(now.getHours() - 1);
      break;
    case '1d':
      now.setDate(now.getDate() - 1);
      break;
    case '1w':
      now.setDate(now.getDate() - 7);
      break;
    case '1m':
      now.setMonth(now.getMonth() - 1);
      break;
  }
  return now.toISOString();
}
