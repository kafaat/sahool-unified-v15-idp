'use client';

/**
 * SAHOOL Weather Page
 * صفحة الطقس
 */

import React, { useState } from 'react';
import { WeatherDashboard } from '@/features/weather';
import { MapPin } from 'lucide-react';

export default function WeatherPage() {
  const [location, setLocation] = useState<string>('صنعاء، اليمن');

  const locations = [
    { value: 'صنعاء، اليمن', label: 'صنعاء، اليمن', labelEn: 'Sana\'a, Yemen' },
    { value: 'عدن، اليمن', label: 'عدن، اليمن', labelEn: 'Aden, Yemen' },
    { value: 'تعز، اليمن', label: 'تعز، اليمن', labelEn: 'Taiz, Yemen' },
    { value: 'الحديدة، اليمن', label: 'الحديدة، اليمن', labelEn: 'Hodeidah, Yemen' },
    { value: 'إب، اليمن', label: 'إب، اليمن', labelEn: 'Ibb, Yemen' },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header with Location Selector */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">الطقس</h1>
            <p className="text-gray-600">Weather Dashboard</p>
          </div>
          <div className="flex items-center gap-3">
            <MapPin className="w-5 h-5 text-gray-600" />
            <select
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 bg-white text-gray-900 font-medium"
            >
              {locations.map((loc) => (
                <option key={loc.value} value={loc.value}>
                  {loc.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Weather Dashboard */}
      <WeatherDashboard location={location} />
    </div>
  );
}
