/**
 * Crop Health Page
 * صفحة صحة المحصول والتشخيص
 */

import { Metadata } from "next";
import CropHealthClient from "./CropHealthClient";

export const metadata: Metadata = {
  title: "Crop Health & Diagnosis | SAHOOL",
  description:
    "صحة المحصول والتشخيص - Monitor crop health, diagnose diseases, and get AI-powered recommendations",
  keywords: [
    "crop health",
    "صحة المحصول",
    "plant diagnosis",
    "disease detection",
    "sahool",
  ],
  openGraph: {
    title: "Crop Health | SAHOOL",
    description: "AI-powered crop health monitoring and disease diagnosis",
    type: "website",
  },
};

export default function CropHealthPage() {
  return <CropHealthClient />;
}
