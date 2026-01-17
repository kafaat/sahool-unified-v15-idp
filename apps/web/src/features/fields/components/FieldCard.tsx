"use client";

/**
 * SAHOOL Field Card Component
 * مكون بطاقة الحقل
 *
 * Enhanced with:
 * - ARIA labels for accessibility
 * - Keyboard navigation (Enter/Space)
 * - React.memo for performance optimization
 * - Improved hover and focus states
 * - RTL support
 */

import React from "react";
import { MapPin, Sprout, Maximize2, Calendar } from "lucide-react";
import type { Field } from "../types";

interface FieldCardProps {
  field: Field;
  onClick?: () => void;
}

const FieldCardComponent: React.FC<FieldCardProps> = ({ field, onClick }) => {
  // Handle keyboard navigation for accessibility
  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (onClick && (event.key === "Enter" || event.key === " ")) {
      event.preventDefault();
      onClick();
    }
  };

  // Construct descriptive ARIA label
  const ariaLabel = `${field.nameAr || field.name}, المساحة ${field.area} هكتار${
    field.crop ? `, المحصول ${field.cropAr || field.crop}` : ""
  }`;

  // Check if card is interactive
  const isInteractive = !!onClick;

  return (
    <div
      onClick={onClick}
      onKeyDown={handleKeyDown}
      role={isInteractive ? "button" : undefined}
      tabIndex={isInteractive ? 0 : undefined}
      aria-label={isInteractive ? ariaLabel : undefined}
      dir="auto"
      className={`
        group
        bg-white rounded-xl border-2 border-gray-200 p-5
        transition-all duration-200 ease-in-out
        ${
          isInteractive
            ? `cursor-pointer
               hover:shadow-lg hover:border-blue-300 hover:scale-[1.02]
               focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2
               active:scale-[0.98]`
            : ""
        }
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4 gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-bold text-gray-900 truncate">
            {field.nameAr || field.name}
          </h3>
          <p className="text-sm text-gray-500 truncate">{field.name}</p>
        </div>
        <div
          className="p-2 bg-green-50 rounded-lg flex-shrink-0
                     group-hover:bg-green-100 transition-colors duration-200"
        >
          <MapPin className="w-5 h-5 text-green-600" aria-hidden="true" />
        </div>
      </div>

      {/* Stats */}
      <div className="space-y-3" role="list" aria-label="معلومات الحقل">
        <div className="flex items-center gap-2 text-sm" role="listitem">
          <Maximize2
            className="w-4 h-4 text-gray-400 flex-shrink-0"
            aria-hidden="true"
          />
          <span className="text-gray-600">المساحة:</span>
          <span className="font-semibold text-gray-900">
            {field.area} هكتار
          </span>
        </div>

        {field.crop && (
          <div className="flex items-center gap-2 text-sm" role="listitem">
            <Sprout
              className="w-4 h-4 text-gray-400 flex-shrink-0"
              aria-hidden="true"
            />
            <span className="text-gray-600">المحصول:</span>
            <span className="font-semibold text-gray-900">
              {field.cropAr || field.crop}
            </span>
          </div>
        )}

        {field.createdAt && (
          <div className="flex items-center gap-2 text-sm" role="listitem">
            <Calendar
              className="w-4 h-4 text-gray-400 flex-shrink-0"
              aria-hidden="true"
            />
            <span className="text-gray-600">تاريخ الإضافة:</span>
            <span className="text-gray-500">
              {new Date(field.createdAt).toLocaleDateString("ar-EG")}
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

// Memoize component for performance optimization
// Only re-renders when field or onClick props change
export const FieldCard = React.memo(FieldCardComponent);

export default FieldCard;
