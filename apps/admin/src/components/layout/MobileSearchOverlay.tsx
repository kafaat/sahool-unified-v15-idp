"use client";

/**
 * Mobile Search Overlay
 * بحث الهاتف المحمول
 *
 * Lazy-loaded: Only rendered on mobile when the user taps the search icon.
 */

import { Search, X } from "lucide-react";

interface MobileSearchOverlayProps {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  onClose: () => void;
}

export default function MobileSearchOverlay({
  searchQuery,
  onSearchChange,
  onClose,
}: MobileSearchOverlayProps) {
  return (
    <div className="fixed inset-0 z-50 bg-black/50 md:hidden">
      <div className="bg-white dark:bg-gray-900 p-4">
        <div className="flex items-center gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="بحث..."
              autoFocus
              className="w-full pl-10 pr-4 py-3 text-base border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-sahool-500 focus:border-transparent bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            />
            <Search
              className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
              aria-hidden="true"
            />
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>
  );
}
