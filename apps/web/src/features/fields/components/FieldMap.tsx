'use client';

/**
 * SAHOOL Field Map Component
 * مكون خريطة الحقل
 */

import React from 'react';
import { MapPin } from 'lucide-react';
import type { Field } from '../types';

interface FieldMapProps {
  field?: Field;
  fields?: Field[];
  height?: string;
  onFieldClick?: (fieldId: string) => void;
}

export const FieldMap: React.FC<FieldMapProps> = ({
  field,
  fields,
  height = '400px',

}) => {
  // TODO: Implement actual map with Leaflet
  // For now, showing a placeholder

  const displayFields = field ? [field] : fields || [];

  return (
    <div
      className="bg-gray-100 rounded-xl border-2 border-gray-200 overflow-hidden relative"
      style={{ height }}
    >
      {/* Map Placeholder */}
      <div className="w-full h-full flex flex-col items-center justify-center">
        <MapPin className="w-16 h-16 text-gray-400 mb-4" />
        <p className="text-gray-600 font-medium">خريطة الحقول</p>
        <p className="text-sm text-gray-500">سيتم تفعيل الخريطة التفاعلية قريباً</p>

        {displayFields.length > 0 && (
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600">
              عرض {displayFields.length} حقل على الخريطة
            </p>
          </div>
        )}
      </div>

      {/* Map Controls Placeholder */}
      <div className="absolute top-4 left-4 bg-white rounded-lg shadow-md p-2 space-y-2">
        <button className="w-8 h-8 flex items-center justify-center hover:bg-gray-100 rounded">
          +
        </button>
        <button className="w-8 h-8 flex items-center justify-center hover:bg-gray-100 rounded">
          -
        </button>
      </div>
    </div>
  );
};

export default FieldMap;
