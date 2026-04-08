/**
 * OpenWeather API client — server-side only.
 * Historical (One Call 3.0) is mocked since it requires a paid subscription.
 */

const OW_BASE = "https://api.openweathermap.org";
const KEY = () => process.env.OPENWEATHERMAP_API_KEY!;

export interface CurrentWeather {
  temp: number;
  feelsLike: number;
  humidity: number;
  windSpeed: number;
  windDeg: number;
  description: string;
  icon: string;
  pressure: number;
  visibility: number;
}

export interface ForecastDay {
  dt: number;
  dateLabel: string;
  tempMin: number;
  tempMax: number;
  humidity: number;
  description: string;
  icon: string;
  pop: number; // probability of precipitation
}

export interface HistoricalWeather {
  mocked: true;
  message: string;
  days: Array<{ date: string; tempAvg: number; precipitation: number }>;
}

export interface AgroData {
  mocked: true;
  message: string;
}

export async function getCurrentWeather(lat: number, lon: number): Promise<CurrentWeather> {
  const url = `${OW_BASE}/data/2.5/weather?lat=${lat}&lon=${lon}&units=metric&appid=${KEY()}`;
  const res = await fetch(url, { next: { revalidate: 600 } });
  if (!res.ok) throw new Error(`OW current weather failed: ${res.status}`);
  const d = await res.json();
  return {
    temp: Math.round(d.main.temp),
    feelsLike: Math.round(d.main.feels_like),
    humidity: d.main.humidity,
    windSpeed: Math.round(d.wind.speed * 3.6), // m/s → km/h
    windDeg: d.wind.deg,
    description: d.weather[0].description,
    icon: d.weather[0].icon,
    pressure: d.main.pressure,
    visibility: Math.round((d.visibility ?? 10000) / 1000),
  };
}

export async function getForecast(lat: number, lon: number): Promise<ForecastDay[]> {
  const url = `${OW_BASE}/data/2.5/forecast?lat=${lat}&lon=${lon}&units=metric&cnt=40&appid=${KEY()}`;
  const res = await fetch(url, { next: { revalidate: 3600 } });
  if (!res.ok) throw new Error(`OW forecast failed: ${res.status}`);
  const d = await res.json();

  // Group 3-hourly slots into daily summaries (pick noon slot or first of day)
  const byDay = new Map<string, typeof d.list[0]>();
  for (const item of d.list) {
    const date = item.dt_txt.slice(0, 10);
    if (!byDay.has(date) || item.dt_txt.includes("12:00:00")) {
      byDay.set(date, item);
    }
  }

  return Array.from(byDay.entries()).slice(0, 5).map(([date, item]) => ({
    dt: item.dt,
    dateLabel: new Date(date).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" }),
    tempMin: Math.round(item.main.temp_min),
    tempMax: Math.round(item.main.temp_max),
    humidity: item.main.humidity,
    description: item.weather[0].description,
    icon: item.weather[0].icon,
    pop: Math.round((item.pop ?? 0) * 100),
  }));
}

// Mocked — One Call 3.0 requires paid subscription
export async function getHistorical(_lat: number, _lon: number): Promise<HistoricalWeather> {
  return {
    mocked: true,
    message: "Historical weather requires OpenWeather One Call 3.0 (paid). Enable by setting OPENWEATHER_PAID=true.",
    days: Array.from({ length: 7 }, (_, i) => {
      const d = new Date();
      d.setDate(d.getDate() - (7 - i));
      return {
        date: d.toISOString().slice(0, 10),
        tempAvg: 18 + Math.round(Math.random() * 10),
        precipitation: Math.round(Math.random() * 5),
      };
    }),
  };
}

// Mocked — requires separate agromonitoring.com subscription
export async function getAgroMonitoring(_lat: number, _lon: number): Promise<AgroData> {
  return {
    mocked: true,
    message: "Agro Monitoring requires a separate agromonitoring.com API key (AGRO_MONITORING_API_KEY).",
  };
}
