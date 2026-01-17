"use client";

import React from "react";

export interface SkipLinkProps {
  href?: string;
  children?: React.ReactNode;
}

/**
 * Skip Link Component for Accessibility
 * مكون تخطي الروابط لإمكانية الوصول
 */
export function SkipLink({
  href = "#main-content",
  children = "تخطي إلى المحتوى الرئيسي",
}: SkipLinkProps) {
  return (
    <a
      href={href}
      className="
        sr-only focus:not-sr-only
        focus:absolute focus:top-4 focus:left-4 focus:z-50
        focus:px-4 focus:py-2 focus:rounded-md
        focus:bg-green-600 focus:text-white
        focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2
      "
    >
      {children}
    </a>
  );
}

export default SkipLink;
