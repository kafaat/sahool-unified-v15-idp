# Weather Feature - SAHOOL Web App

**ميزة الطقس - تطبيق سهول الويب**

## Overview | نظرة عامة

This feature provides real-time weather data, forecasts, and alerts for agricultural decision-making. It integrates with the SAHOOL weather-core service running on port 8108.

توفر هذه الميزة بيانات الطقس في الوقت الفعلي والتنبؤات والتنبيهات لاتخاذ القرارات الزراعية. تتكامل مع خدمة weather-core في منصة سهول التي تعمل على المنفذ 8108.

## Features | الميزات

### Current Weather | الطقس الحالي

- Real-time temperature, humidity, wind speed
- UV index and atmospheric pressure
- Weather conditions in Arabic and English
- Automatic fallback to mock data if API fails

### Weather Forecast | توقعات الطقس

- 7-day forecast (configurable)
- Daily temperature, precipitation, wind speed
- Condition descriptions in both languages
- Graceful degradation to mock data

### Weather Alerts | تنبيهات الطقس

- Agricultural weather alerts
- Severity levels (low, medium, high, critical)
- Affected areas with Arabic names
- Active/inactive alert status

## API Integration | تكامل الواجهة البرمجية

### Endpoints

The feature calls the following weather-core endpoints:

```
GET /api/v1/weather/current?lat={lat}&lon={lon}
GET /api/v1/weather/forecast?lat={lat}&lon={lon}&days=7
GET /api/v1/weather/alerts?lat={lat}&lon={lon}
```

### Service Configuration

- **Service**: weather-core
- **Port**: 8108 (via Kong gateway)
- **Base URL**: `${NEXT_PUBLIC_API_URL}/api/v1/weather`
- **Default Location**: Sana'a, Yemen (15.3694, 44.191)

### Error Handling

The feature implements robust error handling:

1. **Network Errors**: Falls back to mock data
2. **API Errors**: Logs warning in Arabic and uses fallback
3. **Data Transformation**: Handles various API response formats
4. **Retry Logic**: Retries failed requests 2 times with 1s delay

## Usage Examples | أمثلة الاستخدام

### Basic Usage

```typescript
import { useCurrentWeather, useWeatherForecast, useWeatherAlerts } from '@/features/weather';

function WeatherWidget() {
  // Use default coordinates (Sana'a)
  const { data: weather, isLoading, error } = useCurrentWeather();

  // Custom coordinates
  const { data: forecast } = useWeatherForecast({
    lat: 15.5527,
    lon: 48.5164,
    days: 5,
  });

  // Weather alerts
  const { data: alerts } = useWeatherAlerts({
    lat: 15.3694,
    lon: 44.191,
  });

  if (isLoading) return <div>جاري التحميل...</div>;
  if (error) return <div>فشل تحميل بيانات الطقس</div>;

  return (
    <div>
      <h2>{weather.location}</h2>
      <p>Temperature: {weather.temperature}°C</p>
      <p>Condition: {weather.conditionAr}</p>
    </div>
  );
}
```

### Advanced Usage with Conditional Fetching

```typescript
function FieldWeather({ field }) {
  const { data: weather } = useCurrentWeather({
    lat: field.coordinates.lat,
    lon: field.coordinates.lon,
    enabled: !!field.coordinates, // Only fetch if coordinates exist
  });

  return (
    <div>
      {weather && (
        <>
          <div>درجة الحرارة: {weather.temperature}°C</div>
          <div>الرطوبة: {weather.humidity}%</div>
          <div>سرعة الرياح: {weather.windSpeed} كم/س</div>
        </>
      )}
    </div>
  );
}
```

## Data Structures | هياكل البيانات

### WeatherData

```typescript
interface WeatherData {
  temperature: number; // درجة الحرارة (°C)
  humidity: number; // الرطوبة (%)
  windSpeed: number; // سرعة الرياح (km/h)
  windDirection: string; // اتجاه الرياح (N, NE, E, etc.)
  pressure: number; // الضغط الجوي (hPa)
  visibility: number; // الرؤية (km)
  uvIndex: number; // مؤشر الأشعة فوق البنفسجية
  condition: string; // الحالة (English)
  conditionAr: string; // الحالة (العربية)
  location: string; // الموقع
  timestamp: string; // وقت القراءة (ISO 8601)
}
```

### ForecastDataPoint

```typescript
interface ForecastDataPoint {
  date: string; // تاريخ التنبؤ (ISO 8601)
  temperature: number; // متوسط درجة الحرارة (°C)
  humidity: number; // الرطوبة (%)
  precipitation: number; // الأمطار (mm)
  windSpeed: number; // سرعة الرياح (km/h)
  condition: string; // الحالة (English)
  conditionAr: string; // الحالة (العربية)
}
```

### WeatherAlert

```typescript
interface WeatherAlert {
  id: string; // معرف التنبيه
  type: string; // نوع التنبيه
  severity: "low" | "medium" | "high" | "critical"; // مستوى الخطورة
  title: string; // العنوان (English)
  titleAr?: string; // العنوان (العربية)
  description: string; // الوصف (English)
  descriptionAr?: string; // الوصف (العربية)
  affectedAreas: string[]; // المناطق المتأثرة
  affectedAreasAr?: string[]; // المناطق المتأثرة (العربية)
  startTime: string; // وقت البداية (ISO 8601)
  endTime?: string; // وقت النهاية (ISO 8601)
  isActive: boolean; // حالة التنبيه
}
```

## Hook Options | خيارات الخطافات

### WeatherHookOptions

```typescript
interface WeatherHookOptions {
  lat?: number; // خط العرض (default: 15.3694)
  lon?: number; // خط الطول (default: 44.191)
  enabled?: boolean; // تمكين الاستعلام (default: true)
}
```

## Cache Configuration | إعدادات التخزين المؤقت

- **Current Weather**: 5 minutes stale time, refetch every 10 minutes
- **Forecast**: 30 minutes stale time
- **Alerts**: 10 minutes stale time, refetch every 15 minutes

## Fallback Behavior | سلوك الاحتياطي

When the API is unavailable or returns an error, the feature automatically falls back to mock data:

- **Mock Weather**: Provides reasonable sample data for Yemen climate
- **Mock Forecast**: Generates 7-day forecast with typical patterns
- **Mock Alerts**: Returns sample temperature alert

This ensures the UI remains functional even when the backend is unavailable.

## Error Messages | رسائل الخطأ

All error messages are in Arabic for better user experience:

- `فشل الحصول على بيانات الطقس` - Failed to get weather data
- `فشل الحصول على توقعات الطقس` - Failed to get weather forecast
- `فشل الحصول على تنبيهات الطقس` - Failed to get weather alerts
- `فشل الاتصال بخدمة الطقس، استخدام البيانات الاحتياطية` - Connection failed, using fallback data

## Components | المكونات

The feature exports the following components:

- `WeatherDashboard` - Full weather dashboard
- `CurrentWeather` - Current weather display
- `ForecastChart` - Weather forecast visualization
- `WeatherAlerts` - Alert notifications

## Development | التطوير

### Testing with Mock Data

Set `USE_MOCK_WEATHER=true` in the weather-core service to use mock data:

```bash
# In weather-core service
export USE_MOCK_WEATHER=true
```

### Testing with Real API

Ensure Kong gateway is running and weather-core is accessible:

```bash
# Check service health
curl http://localhost:8000/api/v1/weather/current?lat=15.3694&lon=44.191

# Check through Kong gateway
curl http://localhost:8001/services
```

### Environment Variables

Required environment variables in `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Migration Notes | ملاحظات الترحيل

### Breaking Changes

The hooks now accept options object instead of location string:

**Before:**

```typescript
const { data } = useCurrentWeather("Sana'a");
```

**After:**

```typescript
const { data } = useCurrentWeather({ lat: 15.3694, lon: 44.191 });
```

### Backward Compatibility

To maintain compatibility, hooks work with no parameters (use default coordinates):

```typescript
const { data } = useCurrentWeather(); // Uses Sana'a coordinates
```

## Troubleshooting | استكشاف الأخطاء

### No Weather Data Showing

1. Check Kong gateway is running: `docker ps | grep kong`
2. Verify weather-core service: `curl http://localhost:8108/healthz`
3. Check browser console for API errors
4. Verify environment variables are set

### Using Mock Data in Production

If you see mock data in production:

- Check `NEXT_PUBLIC_API_URL` is set correctly
- Verify weather-core service is accessible
- Check Kong routing configuration
- Review browser network tab for failed requests

### Arabic Text Not Showing

Ensure your app has proper RTL support and Arabic fonts configured.

## Future Enhancements | التحسينات المستقبلية

- [ ] Historical weather data
- [ ] Weather-based irrigation recommendations
- [ ] Hourly forecast (48 hours)
- [ ] Agricultural risk assessment
- [ ] Crop-specific weather advice
- [ ] Push notifications for critical alerts
- [ ] Offline mode with cached data

## License | الترخيص

Part of SAHOOL Platform - Agricultural Intelligence for Yemen
