"use client";

import { useEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";
import type { BBoxArray } from "@/lib/bbox";
import type { CurrentWeather, ForecastDay } from "@/lib/weather";
import { formatDate } from "@/lib/utils";

const FieldMap = dynamic(() => import("@/components/FieldMap"), { ssr: false });

type SentinelIndex = "NDVI" | "EVI" | "NDWI" | "TRUE_COLOR" | "FALSE_COLOR";

interface Field {
  id: string;
  name: string;
  description: string | null;
  bbox: BBoxArray;
  centerLng: number | null;
  centerLat: number | null;
  areaSqKm: number | null;
  createdAt: string;
}

interface WeatherData {
  current: CurrentWeather;
  forecast: ForecastDay[];
  historical: { mocked: true; days: Array<{ date: string; tempAvg: number; precipitation: number }> };
  agro: { mocked: true; message: string };
}

const INDICES: { value: SentinelIndex; label: string }[] = [
  { value: "NDVI", label: "NDVI" },
  { value: "EVI", label: "EVI" },
  { value: "NDWI", label: "NDWI" },
  { value: "TRUE_COLOR", label: "True Color" },
  { value: "FALSE_COLOR", label: "False Color" },
];

// Default date range: last 30 days
const today = new Date().toISOString().slice(0, 10);
const thirtyDaysAgo = new Date(Date.now() - 30 * 86400_000).toISOString().slice(0, 10);

export default function FieldDetailClient({ field }: { field: Field }) {
  const [activeIndex, setActiveIndex] = useState<SentinelIndex>("NDVI");
  const [dateFrom, setDateFrom] = useState(thirtyDaysAgo);
  const [dateTo, setDateTo] = useState(today);
  const [sentinelUrl, setSentinelUrl] = useState<string | null>(null);
  const [sentinelLoading, setSentinelLoading] = useState(false);
  const [sentinelError, setSentinelError] = useState("");
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [weatherLoading, setWeatherLoading] = useState(true);
  const abortRef = useRef<AbortController | null>(null);

  // Fetch weather once on mount
  useEffect(() => {
    fetch(`/api/weather?fieldId=${field.id}`)
      .then((r) => r.json())
      .then(setWeather)
      .catch(() => {})
      .finally(() => setWeatherLoading(false));
  }, [field.id]);

  // Fetch Sentinel layer when index or dates change
  useEffect(() => {
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    setSentinelLoading(true);
    setSentinelError("");

    fetch(
      `/api/sentinel/${activeIndex}?fieldId=${field.id}&from=${dateFrom}&to=${dateTo}`,
      { signal: ctrl.signal }
    )
      .then(async (res) => {
        if (!res.ok) {
          const d = await res.json();
          throw new Error(d.error ?? "Sentinel Hub error");
        }
        const blob = await res.blob();
        setSentinelUrl(URL.createObjectURL(blob));
      })
      .catch((err) => {
        if (err.name !== "AbortError") setSentinelError(err.message);
      })
      .finally(() => setSentinelLoading(false));
  }, [activeIndex, dateFrom, dateTo, field.id]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{field.name}</h1>
          {field.description && (
            <p className="text-sm text-muted-foreground mt-1">{field.description}</p>
          )}
          <p className="text-xs text-muted-foreground mt-1">
            {field.areaSqKm?.toFixed(2)} km² · Created {formatDate(field.createdAt)}
          </p>
        </div>
      </div>

      {/* Layer controls */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex gap-1 bg-muted p-1 rounded-lg">
          {INDICES.map((idx) => (
            <button
              key={idx.value}
              onClick={() => setActiveIndex(idx.value)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                activeIndex === idx.value
                  ? "bg-card shadow text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {idx.label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2 text-sm">
          <input
            type="date"
            value={dateFrom}
            max={dateTo}
            onChange={(e) => setDateFrom(e.target.value)}
            className="border rounded-md px-2 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
          />
          <span className="text-muted-foreground">—</span>
          <input
            type="date"
            value={dateTo}
            min={dateFrom}
            max={today}
            onChange={(e) => setDateTo(e.target.value)}
            className="border rounded-md px-2 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
      </div>

      {/* Map */}
      <div className="relative h-[460px] rounded-xl overflow-hidden border bg-muted">
        <FieldMap
          bbox={field.bbox}
          sentinelImageUrl={sentinelUrl}
        />
        {sentinelLoading && (
          <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
            <div className="bg-card rounded-lg px-4 py-2 text-sm font-medium shadow">
              Loading {activeIndex}…
            </div>
          </div>
        )}
        {sentinelError && (
          <div className="absolute bottom-3 left-3 right-3 bg-destructive/90 text-destructive-foreground text-xs rounded-lg px-4 py-2">
            {sentinelError}
          </div>
        )}
      </div>

      {/* Weather KPIs */}
      {weatherLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      ) : weather ? (
        <WeatherKPICards weather={weather} />
      ) : null}
    </div>
  );
}

function WeatherKPICards({ weather }: { weather: WeatherData }) {
  const { current, forecast } = weather;
  const cards = [
    { label: "Temperature", value: `${current.temp}°C`, sub: `Feels like ${current.feelsLike}°C` },
    { label: "Humidity", value: `${current.humidity}%`, sub: current.description },
    { label: "Wind", value: `${current.windSpeed} km/h`, sub: `${current.pressure} hPa` },
    { label: "Visibility", value: `${current.visibility} km`, sub: `Pressure ${current.pressure} hPa` },
  ];

  return (
    <div className="space-y-4">
      <h2 className="font-semibold">Current Weather</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {cards.map((c) => (
          <div key={c.label} className="bg-card border rounded-xl p-4 space-y-1">
            <p className="text-xs text-muted-foreground">{c.label}</p>
            <p className="text-2xl font-bold">{c.value}</p>
            <p className="text-xs text-muted-foreground capitalize">{c.sub}</p>
          </div>
        ))}
      </div>

      {forecast.length > 0 && (
        <div>
          <h3 className="font-medium text-sm mb-2">5-day Forecast</h3>
          <div className="grid grid-cols-5 gap-2">
            {forecast.map((day) => (
              <div key={day.dt} className="bg-card border rounded-lg p-3 text-center space-y-1">
                <p className="text-xs font-medium">{day.dateLabel.split(",")[0]}</p>
                <img
                  src={`https://openweathermap.org/img/wn/${day.icon}.png`}
                  alt={day.description}
                  className="w-8 h-8 mx-auto"
                />
                <p className="text-xs">
                  <span className="font-medium">{day.tempMax}°</span>
                  <span className="text-muted-foreground"> / {day.tempMin}°</span>
                </p>
                <p className="text-xs text-blue-500">{day.pop}%</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
