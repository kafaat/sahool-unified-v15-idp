"use client";

/**
 * Mobile Sidebar Drawer (overlay + close button)
 * درج القائمة الجانبية للهاتف المحمول
 *
 * Lazy-loaded: Only rendered on mobile viewports when the hamburger menu is tapped.
 * Handles the backdrop overlay and the close button inside the sidebar panel.
 */

import { useEffect } from "react";
import { X } from "lucide-react";

interface MobileSidebarDrawerProps {
  onClose: () => void;
}

export default function MobileSidebarDrawer({ onClose }: MobileSidebarDrawerProps) {
  // Close on Escape key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  return (
    <>
      {/* Background overlay */}
      <div
        className="fixed inset-0 bg-black/50 z-40 lg:hidden"
        onClick={onClose}
        aria-hidden="true"
      />
      {/* Close button rendered inside the sidebar via a portal-like pattern isn't possible here,
          but the close button is still in the main Sidebar component since it's part of the <aside>.
          This component provides only the overlay. */}
    </>
  );
}

/**
 * Close button for the mobile sidebar panel.
 * Exported separately for use inside the sidebar <aside> element.
 */
export function MobileSidebarCloseButton({ onClose }: { onClose: () => void }) {
  return (
    <button
      type="button"
      onClick={onClose}
      className="absolute top-4 left-4 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 lg:hidden"
      aria-label="إغلاق القائمة"
    >
      <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
    </button>
  );
}
