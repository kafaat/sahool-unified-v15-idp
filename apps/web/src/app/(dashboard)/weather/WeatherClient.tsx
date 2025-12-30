'use client';

/**
 * SAHOOL Weather Page Client Component
 * صفحة الطقس
 */

import React, { useState, useMemo } from 'react';
import { WeatherDashboard } from '@/features/weather';
import { MapPin } from 'lucide-react';

// Yemen city coordinates
const LOCATIONS = [
  { id: 'sanaa', label: 'صنعاء، اليمن', labelEn: 'Sana\'a, Yemen', lat: 15.3694, lon: 44.1910 },
  { id: 'aden', label: 'عدن، اليمن', labelEn: 'Aden, Yemen', lat: 12.7855, lon: 45.0187 },
  { id: 'taiz', label: 'تعز، اليمن', labelEn: 'Taiz, Yemen', lat: 13.5789, lon: 44.0219 },
  { id: 'hodeidah', label: 'الحديدة، اليمن', labelEn: 'Hodeidah, Yemen', lat: 14.7980, lon: 42.9536 },
  { id: 'ibb', label: 'إب، اليمن', labelEn: 'Ibb, Yemen', lat: 13.9667, lon: 44.1667 },
];

export default function WeatherClient() {
  const [locationId, setLocationId] = useState<string>('sanaa');

  const selectedLocation = useMemo(() =>
    LOCATIONS.find(loc => loc.id === locationId) || LOCATIONS[0],
    [locationId]
  );

  return (
    <div className="space-y-6" data-testid="weather-page">
      {/* Page Header with Location Selector */}
      <div className="bg-white rounded-xl border-2 border-gray-200 p-6" data-testid="weather-header">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2" data-testid="weather-title">الطقس</h1>
            <p className="text-gray-600" data-testid="weather-subtitle">Weather Dashboard</p>
          </div>
          <div className="flex items-center gap-3" data-testid="location-selector-container">
            <MapPin className="w-5 h-5 text-gray-600" data-testid="location-icon" />
            <select
              value={locationId}
              onChange={(e) => setLocationId(e.target.value)}
              className="px-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 bg-white text-gray-900 font-medium"
              data-testid="location-selector"
              aria-label="اختر المدينة"
            >
              {LOCATIONS.map((loc) => (
                <option key={loc.id} value={loc.id}>
                  {loc.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Weather Dashboard */}
      <WeatherDashboard lat={selectedLocation!.lat} lon={selectedLocation!.lon} enabled={true} />
    </div>
  );
}
