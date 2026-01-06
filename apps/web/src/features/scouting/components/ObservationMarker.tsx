'use client';

/**
 * Observation Marker Component
 * مكون علامة الملاحظة
 *
 * Custom Leaflet marker for field observations with:
 * - Color-coded by category
 * - Popup with observation details
 * - Edit/delete actions
 */

import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import { useLocale } from 'next-intl';
import L from 'leaflet';
import {
  Edit2,
  Trash2,
  CheckCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { Observation } from '../types/scouting';
import { CATEGORY_OPTIONS, SEVERITY_LABELS } from '../types/scouting';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

interface ObservationMarkerProps {
  observation: Observation;
  onEdit?: (observation: Observation) => void;
  onDelete?: (observationId: string) => void;
  editable?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create custom marker icon based on category and severity
 */
function createMarkerIcon(category: string, severity: number): L.DivIcon {
  const categoryOption = CATEGORY_OPTIONS.find((opt) => opt.value === category);
  const color = categoryOption?.color || '#64748b';
  const severityColor = SEVERITY_LABELS[severity as 1 | 2 | 3 | 4 | 5]?.color || color;

  const html = `
    <div style="
      width: 36px;
      height: 36px;
      background: ${severityColor};
      border: 3px solid white;
      border-radius: 50% 50% 50% 0;
      transform: rotate(-45deg);
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      justify-content: center;
    ">
      <div style="
        width: 24px;
        height: 24px;
        background: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        transform: rotate(45deg);
        font-weight: bold;
        font-size: 14px;
        color: ${severityColor};
      ">
        ${severity}
      </div>
    </div>
  `;

  return L.divIcon({
    html,
    className: 'custom-observation-marker',
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -36],
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Component
// ═══════════════════════════════════════════════════════════════════════════

export const ObservationMarker: React.FC<ObservationMarkerProps> = ({
  observation,
  onEdit,
  onDelete,
  editable = true,
}) => {
  const locale = useLocale();
  const isArabic = locale === 'ar';

  const position: [number, number] = [
    observation.location.coordinates[1],
    observation.location.coordinates[0],
  ];

  const categoryOption = CATEGORY_OPTIONS.find((opt) => opt.value === observation.category);
  const severityInfo = SEVERITY_LABELS[observation.severity];

  // Cast to any due to incompatible Leaflet types between leaflet and react-leaflet packages
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const markerIcon: any = createMarkerIcon(observation.category, observation.severity);

  return (
    <Marker position={position} icon={markerIcon} {...({} as any)}>
      <Popup maxWidth={300} className="observation-popup" {...({} as any)}>
        <div className="p-2 min-w-[280px]">
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-2">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center"
                style={{ backgroundColor: `${categoryOption?.color}20` }}
              >
                {/* Category icon would go here */}
                <div
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: categoryOption?.color }}
                />
              </div>
              <div>
                <p className="font-semibold text-gray-900">
                  {isArabic ? categoryOption?.labelAr : categoryOption?.label}
                </p>
                {observation.subcategory && (
                  <p className="text-xs text-gray-600">
                    {isArabic ? observation.subcategoryAr : observation.subcategory}
                  </p>
                )}
              </div>
            </div>
            <Badge
              variant="default"
              style={{
                backgroundColor: `${severityInfo.color}20`,
                color: severityInfo.color,
                borderColor: severityInfo.color,
              }}
            >
              {isArabic ? severityInfo.ar : severityInfo.en}
            </Badge>
          </div>

          {/* Notes */}
          <div className="mb-3">
            <p className="text-sm text-gray-700 line-clamp-3">
              {isArabic ? observation.notesAr : observation.notes}
            </p>
          </div>

          {/* Photos */}
          {observation.photos && observation.photos.length > 0 && (
            <div className="mb-3">
              <div className="flex gap-2 overflow-x-auto">
                {observation.photos.slice(0, 3).map((photo, index) => (
                  <img
                    key={photo.id}
                    src={photo.thumbnailUrl || photo.url}
                    alt={`Observation ${index + 1}`}
                    className="w-16 h-16 object-cover rounded border border-gray-200"
                  />
                ))}
                {observation.photos.length > 3 && (
                  <div className="w-16 h-16 bg-gray-100 rounded border border-gray-200 flex items-center justify-center text-xs text-gray-600">
                    +{observation.photos.length - 3}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Task Status */}
          {observation.taskCreated && (
            <div className="mb-3 flex items-center gap-2 text-xs text-green-600">
              <CheckCircle className="w-4 h-4" />
              <span>{isArabic ? 'تم إنشاء مهمة' : 'Task created'}</span>
            </div>
          )}

          {/* Metadata */}
          <div className="text-xs text-gray-500 mb-3">
            <p>
              {isArabic ? 'تم التسجيل:' : 'Recorded:'}{' '}
              {new Date(observation.createdAt).toLocaleDateString(locale, {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </p>
            {observation.observedBy && (
              <p>
                {isArabic ? 'بواسطة:' : 'By:'} {observation.observedBy}
              </p>
            )}
          </div>

          {/* Actions */}
          {editable && (onEdit || onDelete) && (
            <div className="flex gap-2 pt-2 border-t border-gray-200">
              {onEdit && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onEdit(observation)}
                  className="flex-1"
                >
                  <Edit2 className="w-4 h-4 mr-2" />
                  {isArabic ? 'تعديل' : 'Edit'}
                </Button>
              )}
              {onDelete && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onDelete(observation.id)}
                  className="flex-1 text-red-600 hover:bg-red-50 hover:border-red-300"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  {isArabic ? 'حذف' : 'Delete'}
                </Button>
              )}
            </div>
          )}
        </div>
      </Popup>
    </Marker>
  );
};

export default ObservationMarker;
