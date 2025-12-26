-- SAHOOL Weather History Seed Data
-- 1 year of historical weather data for major Yemen cities

-- Create weather history table if not exists
CREATE TABLE IF NOT EXISTS weather_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_name VARCHAR(100) NOT NULL,
    location_name_ar VARCHAR(100),
    governorate VARCHAR(100),
    latitude DECIMAL(10, 6) NOT NULL,
    longitude DECIMAL(10, 6) NOT NULL,

    obs_date DATE NOT NULL,

    -- Temperature (°C)
    temp_avg_c DECIMAL(5, 2),
    temp_min_c DECIMAL(5, 2),
    temp_max_c DECIMAL(5, 2),

    -- Precipitation (mm)
    precipitation_mm DECIMAL(6, 2) DEFAULT 0,

    -- Humidity (%)
    humidity_avg_pct DECIMAL(5, 2),
    humidity_min_pct DECIMAL(5, 2),
    humidity_max_pct DECIMAL(5, 2),

    -- Wind (km/h)
    wind_speed_kmh DECIMAL(5, 2),
    wind_gust_kmh DECIMAL(5, 2),
    wind_direction_deg INTEGER,

    -- Solar radiation (W/m²)
    solar_radiation_wm2 DECIMAL(7, 2),

    -- Other
    cloud_cover_pct DECIMAL(5, 2),
    pressure_hpa DECIMAL(7, 2),
    dew_point_c DECIMAL(5, 2),

    -- GDD calculation
    gdd_base_10 DECIMAL(6, 2), -- Growing Degree Days with base 10°C

    -- Data source
    data_source VARCHAR(50) DEFAULT 'mock',
    quality_score DECIMAL(3, 2) DEFAULT 1.0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(location_name, obs_date)
);

-- Create index for efficient queries
CREATE INDEX IF NOT EXISTS idx_weather_location_date ON weather_history(location_name, obs_date);
CREATE INDEX IF NOT EXISTS idx_weather_governorate_date ON weather_history(governorate, obs_date);

-- Helper function to generate weather data for a location
-- This generates realistic Yemen weather patterns

-- Function to calculate GDD (Growing Degree Days)
CREATE OR REPLACE FUNCTION calculate_gdd(temp_avg DECIMAL, temp_min DECIMAL, temp_max DECIMAL, base_temp DECIMAL DEFAULT 10)
RETURNS DECIMAL AS $$
DECLARE
    avg_temp DECIMAL;
BEGIN
    avg_temp := (temp_min + temp_max) / 2.0;
    IF avg_temp > base_temp THEN
        RETURN avg_temp - base_temp;
    ELSE
        RETURN 0;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Generate weather data for Sana'a (صنعاء) - Highland climate
-- Altitude: ~2,250m, temperate with two rainy seasons
WITH date_series AS (
    SELECT generate_series(
        CURRENT_DATE - INTERVAL '365 days',
        CURRENT_DATE - INTERVAL '1 day',
        '1 day'::interval
    )::date AS obs_date
)
INSERT INTO weather_history (
    location_name, location_name_ar, governorate,
    latitude, longitude, obs_date,
    temp_avg_c, temp_min_c, temp_max_c,
    precipitation_mm, humidity_avg_pct,
    wind_speed_kmh, solar_radiation_wm2,
    cloud_cover_pct, pressure_hpa,
    gdd_base_10, data_source
)
SELECT
    'Sana''a City', 'صنعاء', 'صنعاء',
    15.3547, 44.2066, obs_date,
    -- Temperature varies by season (highland climate)
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (12, 1, 2) THEN 12.0 + random() * 4 -- Winter: 12-16°C
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 4, 5) THEN 18.0 + random() * 6 -- Spring: 18-24°C
        WHEN EXTRACT(MONTH FROM obs_date) IN (6, 7, 8) THEN 20.0 + random() * 5 -- Summer: 20-25°C
        ELSE 16.0 + random() * 5 -- Fall: 16-21°C
    END,
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (12, 1, 2) THEN 6.0 + random() * 4
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 4, 5) THEN 12.0 + random() * 4
        WHEN EXTRACT(MONTH FROM obs_date) IN (6, 7, 8) THEN 14.0 + random() * 4
        ELSE 10.0 + random() * 4
    END,
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (12, 1, 2) THEN 18.0 + random() * 4
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 4, 5) THEN 24.0 + random() * 5
        WHEN EXTRACT(MONTH FROM obs_date) IN (6, 7, 8) THEN 26.0 + random() * 5
        ELSE 22.0 + random() * 4
    END,
    -- Rainfall peaks in April-May and July-August
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (4, 5, 7, 8) THEN
            CASE WHEN random() < 0.3 THEN random() * 25 ELSE 0 END
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 6, 9) THEN
            CASE WHEN random() < 0.15 THEN random() * 10 ELSE 0 END
        ELSE 0
    END,
    45.0 + random() * 30, -- Humidity 45-75%
    8.0 + random() * 10, -- Wind 8-18 km/h
    220.0 + random() * 80, -- Solar radiation 220-300 W/m²
    30.0 + random() * 40, -- Cloud cover 30-70%
    850.0 + random() * 10, -- Pressure ~850 hPa (high altitude)
    0, -- GDD will be calculated
    'mock_realistic'
FROM date_series;

-- Update GDD for Sana'a
UPDATE weather_history
SET gdd_base_10 = calculate_gdd(temp_avg_c, temp_min_c, temp_max_c, 10)
WHERE location_name = 'Sana''a City';

-- Generate weather data for Ta'izz (تعز) - Mountain climate
WITH date_series AS (
    SELECT generate_series(
        CURRENT_DATE - INTERVAL '365 days',
        CURRENT_DATE - INTERVAL '1 day',
        '1 day'::interval
    )::date AS obs_date
)
INSERT INTO weather_history (
    location_name, location_name_ar, governorate,
    latitude, longitude, obs_date,
    temp_avg_c, temp_min_c, temp_max_c,
    precipitation_mm, humidity_avg_pct,
    wind_speed_kmh, solar_radiation_wm2,
    cloud_cover_pct, pressure_hpa,
    gdd_base_10, data_source
)
SELECT
    'Ta''izz City', 'تعز', 'تعز',
    13.5795, 44.0216, obs_date,
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (12, 1, 2) THEN 18.0 + random() * 5
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 4, 5) THEN 22.0 + random() * 6
        WHEN EXTRACT(MONTH FROM obs_date) IN (6, 7, 8) THEN 24.0 + random() * 5
        ELSE 20.0 + random() * 5
    END,
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (12, 1, 2) THEN 12.0 + random() * 4
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 4, 5) THEN 16.0 + random() * 4
        WHEN EXTRACT(MONTH FROM obs_date) IN (6, 7, 8) THEN 18.0 + random() * 4
        ELSE 14.0 + random() * 4
    END,
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (12, 1, 2) THEN 24.0 + random() * 4
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 4, 5) THEN 28.0 + random() * 5
        WHEN EXTRACT(MONTH FROM obs_date) IN (6, 7, 8) THEN 30.0 + random() * 5
        ELSE 26.0 + random() * 4
    END,
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (4, 5, 7, 8, 9) THEN
            CASE WHEN random() < 0.4 THEN random() * 35 ELSE 0 END
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 6, 10) THEN
            CASE WHEN random() < 0.2 THEN random() * 15 ELSE 0 END
        ELSE 0
    END,
    50.0 + random() * 30,
    10.0 + random() * 12,
    240.0 + random() * 80,
    25.0 + random() * 45,
    920.0 + random() * 10,
    calculate_gdd(
        (12.0 + 24.0) / 2.0 + random() * 5,
        12.0 + random() * 4,
        24.0 + random() * 5,
        10
    ),
    'mock_realistic'
FROM date_series;

-- Generate weather data for Al-Hudaydah (الحديدة) - Coastal hot climate
WITH date_series AS (
    SELECT generate_series(
        CURRENT_DATE - INTERVAL '365 days',
        CURRENT_DATE - INTERVAL '1 day',
        '1 day'::interval
    )::date AS obs_date
)
INSERT INTO weather_history (
    location_name, location_name_ar, governorate,
    latitude, longitude, obs_date,
    temp_avg_c, temp_min_c, temp_max_c,
    precipitation_mm, humidity_avg_pct,
    wind_speed_kmh, solar_radiation_wm2,
    cloud_cover_pct, pressure_hpa,
    gdd_base_10, data_source
)
SELECT
    'Al-Hudaydah City', 'الحديدة', 'الحديدة',
    14.7978, 42.9545, obs_date,
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (12, 1, 2) THEN 25.0 + random() * 5
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 4, 5) THEN 30.0 + random() * 5
        WHEN EXTRACT(MONTH FROM obs_date) IN (6, 7, 8) THEN 35.0 + random() * 5
        ELSE 28.0 + random() * 5
    END,
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (12, 1, 2) THEN 20.0 + random() * 3
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 4, 5) THEN 24.0 + random() * 4
        WHEN EXTRACT(MONTH FROM obs_date) IN (6, 7, 8) THEN 28.0 + random() * 4
        ELSE 22.0 + random() * 4
    END,
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (12, 1, 2) THEN 30.0 + random() * 4
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 4, 5) THEN 36.0 + random() * 5
        WHEN EXTRACT(MONTH FROM obs_date) IN (6, 7, 8) THEN 42.0 + random() * 5
        ELSE 34.0 + random() * 5
    END,
    -- Very little rainfall, mostly in summer
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (7, 8) THEN
            CASE WHEN random() < 0.15 THEN random() * 15 ELSE 0 END
        ELSE
            CASE WHEN random() < 0.05 THEN random() * 5 ELSE 0 END
    END,
    70.0 + random() * 20, -- High humidity (coastal)
    12.0 + random() * 15,
    280.0 + random() * 100,
    20.0 + random() * 30,
    1010.0 + random() * 10, -- Sea level pressure
    calculate_gdd(
        (28.0 + 42.0) / 2.0 + random() * 5,
        24.0 + random() * 4,
        36.0 + random() * 5,
        10
    ),
    'mock_realistic'
FROM date_series;

-- Generate weather data for Hadramout (حضرموت) - Wadi/Desert climate
WITH date_series AS (
    SELECT generate_series(
        CURRENT_DATE - INTERVAL '365 days',
        CURRENT_DATE - INTERVAL '1 day',
        '1 day'::interval
    )::date AS obs_date
)
INSERT INTO weather_history (
    location_name, location_name_ar, governorate,
    latitude, longitude, obs_date,
    temp_avg_c, temp_min_c, temp_max_c,
    precipitation_mm, humidity_avg_pct,
    wind_speed_kmh, solar_radiation_wm2,
    cloud_cover_pct, pressure_hpa,
    gdd_base_10, data_source
)
SELECT
    'Shibam (Wadi Hadramout)', 'شبام (وادي حضرموت)', 'حضرموت',
    15.9288, 48.7825, obs_date,
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (12, 1, 2) THEN 20.0 + random() * 6
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 4, 5) THEN 28.0 + random() * 7
        WHEN EXTRACT(MONTH FROM obs_date) IN (6, 7, 8) THEN 34.0 + random() * 8
        ELSE 26.0 + random() * 6
    END,
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (12, 1, 2) THEN 14.0 + random() * 4
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 4, 5) THEN 20.0 + random() * 5
        WHEN EXTRACT(MONTH FROM obs_date) IN (6, 7, 8) THEN 26.0 + random() * 5
        ELSE 18.0 + random() * 5
    END,
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (12, 1, 2) THEN 26.0 + random() * 5
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 4, 5) THEN 36.0 + random() * 6
        WHEN EXTRACT(MONTH FROM obs_date) IN (6, 7, 8) THEN 42.0 + random() * 6
        ELSE 34.0 + random() * 6
    END,
    -- Very arid, occasional rain
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (4, 5, 10, 11) THEN
            CASE WHEN random() < 0.1 THEN random() * 20 ELSE 0 END
        ELSE
            CASE WHEN random() < 0.03 THEN random() * 5 ELSE 0 END
    END,
    30.0 + random() * 25, -- Low humidity (desert)
    10.0 + random() * 12,
    300.0 + random() * 120,
    10.0 + random() * 25,
    980.0 + random() * 15,
    calculate_gdd(
        (26.0 + 42.0) / 2.0 + random() * 6,
        20.0 + random() * 5,
        36.0 + random() * 6,
        10
    ),
    'mock_realistic'
FROM date_series;

-- Generate weather data for Ibb (إب) - Highland with high rainfall
WITH date_series AS (
    SELECT generate_series(
        CURRENT_DATE - INTERVAL '365 days',
        CURRENT_DATE - INTERVAL '1 day',
        '1 day'::interval
    )::date AS obs_date
)
INSERT INTO weather_history (
    location_name, location_name_ar, governorate,
    latitude, longitude, obs_date,
    temp_avg_c, temp_min_c, temp_max_c,
    precipitation_mm, humidity_avg_pct,
    wind_speed_kmh, solar_radiation_wm2,
    cloud_cover_pct, pressure_hpa,
    gdd_base_10, data_source
)
SELECT
    'Ibb City', 'إب', 'إب',
    13.9667, 44.1667, obs_date,
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (12, 1, 2) THEN 16.0 + random() * 4
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 4, 5) THEN 20.0 + random() * 5
        WHEN EXTRACT(MONTH FROM obs_date) IN (6, 7, 8) THEN 22.0 + random() * 5
        ELSE 18.0 + random() * 5
    END,
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (12, 1, 2) THEN 10.0 + random() * 4
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 4, 5) THEN 14.0 + random() * 4
        WHEN EXTRACT(MONTH FROM obs_date) IN (6, 7, 8) THEN 16.0 + random() * 4
        ELSE 12.0 + random() * 4
    END,
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (12, 1, 2) THEN 22.0 + random() * 4
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 4, 5) THEN 26.0 + random() * 5
        WHEN EXTRACT(MONTH FROM obs_date) IN (6, 7, 8) THEN 28.0 + random() * 5
        ELSE 24.0 + random() * 4
    END,
    -- High rainfall, especially in summer
    CASE
        WHEN EXTRACT(MONTH FROM obs_date) IN (4, 5, 7, 8, 9) THEN
            CASE WHEN random() < 0.5 THEN random() * 40 ELSE 0 END
        WHEN EXTRACT(MONTH FROM obs_date) IN (3, 6, 10) THEN
            CASE WHEN random() < 0.3 THEN random() * 20 ELSE 0 END
        ELSE
            CASE WHEN random() < 0.1 THEN random() * 10 ELSE 0 END
    END,
    60.0 + random() * 25, -- Higher humidity
    9.0 + random() * 11,
    210.0 + random() * 75,
    40.0 + random() * 40, -- Often cloudy
    900.0 + random() * 10,
    calculate_gdd(
        (16.0 + 26.0) / 2.0 + random() * 5,
        14.0 + random() * 4,
        26.0 + random() * 5,
        10
    ),
    'mock_realistic'
FROM date_series;

-- Verification queries
SELECT
    location_name,
    location_name_ar,
    COUNT(*) as days,
    ROUND(AVG(temp_avg_c)::numeric, 2) as avg_temp,
    ROUND(AVG(precipitation_mm)::numeric, 2) as avg_rainfall,
    ROUND(SUM(precipitation_mm)::numeric, 2) as total_rainfall_mm,
    ROUND(AVG(humidity_avg_pct)::numeric, 2) as avg_humidity,
    ROUND(AVG(gdd_base_10)::numeric, 2) as avg_daily_gdd,
    ROUND(SUM(gdd_base_10)::numeric, 0) as total_annual_gdd
FROM weather_history
WHERE obs_date >= CURRENT_DATE - INTERVAL '365 days'
GROUP BY location_name, location_name_ar
ORDER BY location_name;

-- Monthly averages for Sana'a (example)
SELECT
    EXTRACT(MONTH FROM obs_date) as month,
    ROUND(AVG(temp_avg_c)::numeric, 2) as avg_temp,
    ROUND(SUM(precipitation_mm)::numeric, 2) as total_rainfall,
    ROUND(AVG(humidity_avg_pct)::numeric, 2) as avg_humidity
FROM weather_history
WHERE location_name = 'Sana''a City'
    AND obs_date >= CURRENT_DATE - INTERVAL '365 days'
GROUP BY EXTRACT(MONTH FROM obs_date)
ORDER BY month;
