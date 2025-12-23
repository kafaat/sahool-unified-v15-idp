'use client';

/**
 * SAHOOL Field Card Component
 * مكون بطاقة الحقل
 */

import React from 'react';
import { MapPin, Sprout, Maximize2, Calendar } from 'lucide-react';
import type { Field } from '../types';

interface FieldCardProps {
  field: Field;
  onClick?: () => void;
}

export const FieldCard: React.FC<FieldCardProps> = ({ field, onClick }) => {
  return (
    <div
      onClick={onClick}
      className="bg-white rounded-xl border-2 border-gray-200 p-5 hover:shadow-lg hover:border-blue-300 transition-all cursor-pointer"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-gray-900">{field.nameAr || field.name}</h3>
          <p className="text-sm text-gray-500">{field.name}</p>
        </div>
        <div className="p-2 bg-green-50 rounded-lg">
          <MapPin className="w-5 h-5 text-green-600" />
        </div>
      </div>

      {/* Stats */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-sm">
          <Maximize2 className="w-4 h-4 text-gray-400" />
          <span className="text-gray-600">المساحة:</span>
          <span className="font-semibold text-gray-900">{field.area} هكتار</span>
        </div>

        {field.crop && (
          <div className="flex items-center gap-2 text-sm">
            <Sprout className="w-4 h-4 text-gray-400" />
            <span className="text-gray-600">المحصول:</span>
            <span className="font-semibold text-gray-900">{field.cropAr || field.crop}</span>
          </div>
        )}

        {field.createdAt && (
          <div className="flex items-center gap-2 text-sm">
            <Calendar className="w-4 h-4 text-gray-400" />
            <span className="text-gray-600">تاريخ الإضافة:</span>
            <span className="text-gray-500">
              {new Date(field.createdAt).toLocaleDateString('ar-EG')}
            </span>
          </div>
        )}
      </div>

      {/* Footer */}
      {field.description && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <p className="text-sm text-gray-600 line-clamp-2">
            {field.descriptionAr || field.description}
          </p>
        </div>
      )}
    </div>
  );
};

export default FieldCard;
