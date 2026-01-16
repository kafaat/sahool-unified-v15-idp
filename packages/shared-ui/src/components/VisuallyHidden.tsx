"use client";

import React from "react";

export interface VisuallyHiddenProps {
  children: React.ReactNode;
  as?: "span" | "div" | "p" | "h1" | "h2" | "h3" | "h4" | "h5" | "h6";
}

/**
 * Visually Hidden Component for Screen Readers
 * مكون مخفي بصرياً لقارئات الشاشة
 */
export function VisuallyHidden({
  children,
  as: Component = "span",
}: VisuallyHiddenProps) {
  return <Component className="sr-only">{children}</Component>;
}

export default VisuallyHidden;
