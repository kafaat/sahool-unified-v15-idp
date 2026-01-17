/**
 * SAHOOL Weather Page
 * صفحة الطقس
 */

import { Metadata } from "next";
import WeatherClient from "./WeatherClient";

export const metadata: Metadata = {
  title: "Weather Forecast | SAHOOL",
  description:
    "الطقس - Real-time weather forecasts, alerts, and agricultural weather insights for Yemen",
  keywords: [
    "weather",
    "الطقس",
    "forecast",
    "climate",
    "agriculture weather",
    "yemen",
    "sahool",
  ],
  openGraph: {
    title: "Weather Forecast | SAHOOL",
    description: "Agricultural weather forecasts and insights",
    type: "website",
  },
};

export default function WeatherPage() {
  return <WeatherClient />;
}
