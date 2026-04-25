-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add WeatherProviderSource enum and migrate source/provider columns
-- إضافة نوع WeatherProviderSource وترحيل أعمدة source/provider من TEXT إلى enum
--
-- Context: The Prisma schema now uses a typed enum for the provider/source
-- columns in weather_observations and weather_forecasts. This migration:
--   1. Creates the WeatherProviderSource PostgreSQL enum type using the exact
--      @map values defined in schema.prisma.
--   2. Normalises any legacy free-text values to a known enum member (MOCK)
--      so the USING cast cannot fail on existing rows.
--   3. Alters both columns from TEXT to the new enum type.
--
-- Rollback:
--   ALTER TABLE "weather_observations" ALTER COLUMN "source" TYPE TEXT
--     USING "source"::TEXT;
--   ALTER TABLE "weather_forecasts" ALTER COLUMN "provider" TYPE TEXT
--     USING "provider"::TEXT;
--   DROP TYPE "WeatherProviderSource";
-- ═══════════════════════════════════════════════════════════════════════════════

-- Step 1: Create the enum type.
-- The labels match the @map values in schema.prisma so Prisma Client maps
-- them transparently without any further translation layer.
CREATE TYPE "WeatherProviderSource" AS ENUM (
    'open-meteo',
    'openweathermap',
    'weatherapi',
    'mock'
);

-- Step 2: Normalise unknown legacy values in weather_observations.source.
-- Any row whose source text is not a known enum label is coerced to 'mock'
-- to guarantee the subsequent USING cast succeeds on every existing row.
UPDATE "weather_observations"
SET    "source" = 'mock'
WHERE  "source" NOT IN ('open-meteo', 'openweathermap', 'weatherapi', 'mock');

-- Step 3: Alter weather_observations.source from TEXT to the enum type.
ALTER TABLE "weather_observations"
    ALTER COLUMN "source" TYPE "WeatherProviderSource"
    USING "source"::"WeatherProviderSource";

-- Step 4: Normalise unknown legacy values in weather_forecasts.provider.
UPDATE "weather_forecasts"
SET    "provider" = 'mock'
WHERE  "provider" NOT IN ('open-meteo', 'openweathermap', 'weatherapi', 'mock');

-- Step 5: Alter weather_forecasts.provider from TEXT to the enum type.
ALTER TABLE "weather_forecasts"
    ALTER COLUMN "provider" TYPE "WeatherProviderSource"
    USING "provider"::"WeatherProviderSource";
