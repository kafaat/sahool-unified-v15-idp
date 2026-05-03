'use client';

/**
 * SAHOOL Fields List Component
 * مكون قائمة الحقول
 */

import React, { useEffect, useRef, useState } from 'react';
import { Grid3x3, List, Map as MapIcon, Search, Plus } from 'lucide-react';
import { useFields } from '../hooks/useFields';
import { FieldCard } from './FieldCard';
import type { FieldViewMode, FieldFilters } from '../types';

interface FieldsListProps {
  onFieldClick?: (fieldId: string) => void;
  onCreateClick?: () => void;
  /**
   * If set, the matching field's card is scrolled into view and visually
   * highlighted on first render. Used to restore the user's last-viewed
   * field when they return to the fields list.
   */
  highlightedFieldId?: string | null;
  /**
   * Called once when `highlightedFieldId` is set but no matching field is
   * found in the loaded list (deleted / access denied / stale). Lets the
   * caller clean up persisted state.
   */
  onMissingHighlight?: (fieldId: string) => void;
}

export const FieldsList: React.FC<FieldsListProps> = ({
  onFieldClick,
  onCreateClick,
  highlightedFieldId,
  onMissingHighlight,
}) => {
  const [viewMode, setViewMode] = useState<FieldViewMode>('grid');
  const [filters, setFilters] = useState<FieldFilters>({});
  const { data: fields, isLoading } = useFields(filters);
  const cardRefs = useRef<Map<string, HTMLDivElement | null>>(new Map());
  // Track the id we've already scrolled to / cleaned up so we don't repeat
  // the side-effect on every re-render or filter change.
  const handledHighlightRef = useRef<string | null>(null);

  // When the stored last-viewed field id arrives and the list has loaded,
  // either scroll the card into view or notify the caller it's stale.
  useEffect(() => {
    if (
      !highlightedFieldId ||
      isLoading ||
      !fields ||
      handledHighlightRef.current === highlightedFieldId
    ) {
      return;
    }
    handledHighlightRef.current = highlightedFieldId;
    const match = fields.find((f) => f.id === highlightedFieldId);
    if (!match) {
      onMissingHighlight?.(highlightedFieldId);
      return;
    }
    const node = cardRefs.current.get(highlightedFieldId);
    if (node) {
      // Defer to the next frame so layout has settled after the cards
      // mount; avoids races with smooth-scroll timing in Safari/Firefox.
      const raf =
        typeof window !== 'undefined' && typeof window.requestAnimationFrame === 'function'
          ? window.requestAnimationFrame
          : (cb: FrameRequestCallback) => setTimeout(() => cb(0), 0);
      raf(() => {
        node.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
    }
  }, [highlightedFieldId, fields, isLoading, onMissingHighlight]);

  const handleSearch = (search: string) => {
    setFilters((prev) => ({ ...prev, search }));
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="h-10 w-64 bg-gray-200 rounded-lg animate-pulse" />
          <div className="h-10 w-32 bg-gray-200 rounded-lg animate-pulse" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-48 bg-gray-200 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex-1 w-full sm:w-auto">
          <div className="relative">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="ابحث عن حقل... | Search fields..."
              aria-label="ابحث عن حقل | Search fields"
              className="w-full pr-10 pl-4 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500"
              onChange={(e) => handleSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* View Mode Toggle */}
          <div
            className="flex items-center gap-1 p-1 bg-gray-100 rounded-lg"
            role="group"
            aria-label="وضع العرض | View mode"
          >
            <button
              onClick={() => setViewMode('grid')}
              aria-label="عرض شبكي | Grid view"
              aria-pressed={viewMode === 'grid'}
              className={`p-2 rounded ${viewMode === 'grid' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'}`}
            >
              <Grid3x3 className="w-5 h-5" aria-hidden="true" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              aria-label="عرض قائمة | List view"
              aria-pressed={viewMode === 'list'}
              className={`p-2 rounded ${viewMode === 'list' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'}`}
            >
              <List className="w-5 h-5" aria-hidden="true" />
            </button>
            <button
              onClick={() => setViewMode('map')}
              aria-label="عرض خريطة | Map view"
              aria-pressed={viewMode === 'map'}
              className={`p-2 rounded ${viewMode === 'map' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'}`}
            >
              <MapIcon className="w-5 h-5" aria-hidden="true" />
            </button>
          </div>

          {/* Create Button */}
          {onCreateClick && (
            <button
              onClick={onCreateClick}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-5 h-5" />
              <span>إضافة حقل</span>
            </button>
          )}
        </div>
      </div>

      {/* Fields Grid/List */}
      {!fields || fields.length === 0 ? (
        <div className="text-center py-16">
          <MapIcon className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">لا توجد حقول</h3>
          <p className="text-gray-500 mb-6">ابدأ بإضافة حقلك الأول</p>
          {onCreateClick && (
            <button
              onClick={onCreateClick}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              إضافة حقل جديد
            </button>
          )}
        </div>
      ) : (
        <div
          className={
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
              : 'space-y-4'
          }
        >
          {fields.map((field) => {
            const isHighlighted = field.id === highlightedFieldId;
            return (
              <div
                key={field.id}
                ref={(node) => {
                  if (node) {
                    cardRefs.current.set(field.id, node);
                  } else {
                    cardRefs.current.delete(field.id);
                  }
                }}
                className={
                  isHighlighted
                    ? 'rounded-xl ring-2 ring-blue-500 ring-offset-2 transition-shadow'
                    : undefined
                }
                aria-current={isHighlighted ? 'true' : undefined}
                data-testid={isHighlighted ? 'field-card-highlighted' : undefined}
              >
                <FieldCard field={field} onClick={() => onFieldClick?.(field.id)} />
              </div>
            );
          })}
        </div>
      )}

      {/* Results Count */}
      {fields && fields.length > 0 && (
        <div className="text-center text-sm text-gray-500">
          عرض {fields.length} حقل | Showing {fields.length} fields
        </div>
      )}
    </div>
  );
};

export default FieldsList;
