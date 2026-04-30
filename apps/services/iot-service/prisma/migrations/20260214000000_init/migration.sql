-- CreateEnum
DO $$
BEGIN
    CREATE TYPE "DeviceType" AS ENUM ('SOIL_MOISTURE_SENSOR', 'TEMPERATURE_SENSOR', 'HUMIDITY_SENSOR', 'WATER_FLOW_METER', 'WEATHER_STATION', 'VALVE_CONTROLLER', 'PUMP_CONTROLLER', 'IRRIGATION_CONTROLLER', 'CAMERA', 'GATEWAY', 'CUSTOM');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$
BEGIN
    CREATE TYPE "DeviceStatus" AS ENUM ('ONLINE', 'OFFLINE', 'MAINTENANCE', 'ERROR', 'INACTIVE');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$
BEGIN
    CREATE TYPE "SensorType" AS ENUM ('SOIL_MOISTURE', 'SOIL_TEMPERATURE', 'AIR_TEMPERATURE', 'AIR_HUMIDITY', 'LIGHT_INTENSITY', 'WATER_FLOW', 'WATER_PRESSURE', 'WATER_LEVEL', 'PH_LEVEL', 'EC_LEVEL', 'BATTERY_LEVEL', 'SIGNAL_STRENGTH', 'RAINFALL', 'WIND_SPEED', 'WIND_DIRECTION', 'CUSTOM');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$
BEGIN
    CREATE TYPE "ActuatorType" AS ENUM ('VALVE', 'PUMP', 'MOTOR', 'RELAY', 'SWITCH', 'SERVO', 'CUSTOM');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$
BEGIN
    CREATE TYPE "AlertSeverity" AS ENUM ('INFO', 'WARNING', 'ERROR', 'CRITICAL');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateEnum
DO $$
BEGIN
    CREATE TYPE "CommandStatus" AS ENUM ('PENDING', 'EXECUTING', 'COMPLETED', 'FAILED', 'TIMEOUT', 'CANCELLED');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CreateTable
CREATE TABLE IF NOT EXISTS "devices" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenantId" VARCHAR(100) NOT NULL,
    "deviceId" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "type" "DeviceType" NOT NULL,
    "status" "DeviceStatus" NOT NULL DEFAULT 'OFFLINE',
    "lastSeen" TIMESTAMPTZ,
    "metadata" JSONB,
    "fieldId" VARCHAR(100),
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ NOT NULL,

    CONSTRAINT "devices_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "sensors" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenantId" VARCHAR(100) NOT NULL,
    "deviceId" UUID NOT NULL,
    "sensorType" "SensorType" NOT NULL,
    "unit" VARCHAR(50) NOT NULL,
    "calibrationData" JSONB,
    "lastReading" DOUBLE PRECISION,
    "lastReadingAt" TIMESTAMPTZ,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ NOT NULL,

    CONSTRAINT "sensors_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "sensor_readings" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenantId" VARCHAR(100) NOT NULL,
    "sensorId" UUID NOT NULL,
    "deviceId" UUID NOT NULL,
    "value" DOUBLE PRECISION NOT NULL,
    "unit" VARCHAR(50) NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "quality" DOUBLE PRECISION DEFAULT 1.0,
    "metadata" JSONB,

    CONSTRAINT "sensor_readings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "actuators" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenantId" VARCHAR(100) NOT NULL,
    "deviceId" UUID NOT NULL,
    "actuatorType" "ActuatorType" NOT NULL,
    "name" VARCHAR(255),
    "currentState" JSONB,
    "lastCommand" VARCHAR(255),
    "lastCommandAt" TIMESTAMPTZ,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ NOT NULL,

    CONSTRAINT "actuators_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "actuator_commands" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenantId" VARCHAR(100) NOT NULL,
    "actuatorId" UUID NOT NULL,
    "command" VARCHAR(255) NOT NULL,
    "parameters" JSONB,
    "status" "CommandStatus" NOT NULL DEFAULT 'PENDING',
    "requestedAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "executedAt" TIMESTAMPTZ,
    "completedAt" TIMESTAMPTZ,
    "errorMessage" TEXT,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ NOT NULL,

    CONSTRAINT "actuator_commands_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "device_alerts" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "deviceId" UUID NOT NULL,
    "tenantId" VARCHAR(100) NOT NULL,
    "alertType" VARCHAR(100) NOT NULL,
    "severity" "AlertSeverity" NOT NULL,
    "message" TEXT NOT NULL,
    "acknowledged" BOOLEAN NOT NULL DEFAULT false,
    "acknowledgedBy" VARCHAR(255),
    "acknowledgedAt" TIMESTAMPTZ,
    "resolvedAt" TIMESTAMPTZ,
    "metadata" JSONB,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ NOT NULL,

    CONSTRAINT "device_alerts_pkey" PRIMARY KEY ("id")
);

-- CreateIndex: devices
CREATE UNIQUE INDEX IF NOT EXISTS "devices_tenantId_deviceId_key" ON "devices"("tenantId", "deviceId");
CREATE INDEX IF NOT EXISTS "idx_devices_tenant" ON "devices"("tenantId");
CREATE INDEX IF NOT EXISTS "idx_devices_device_id" ON "devices"("deviceId");
CREATE INDEX IF NOT EXISTS "idx_devices_status" ON "devices"("status");
CREATE INDEX IF NOT EXISTS "idx_devices_field" ON "devices"("fieldId");
CREATE INDEX IF NOT EXISTS "idx_devices_last_seen" ON "devices"("lastSeen");
CREATE INDEX IF NOT EXISTS "idx_devices_tenant_status" ON "devices"("tenantId", "status");
CREATE INDEX IF NOT EXISTS "idx_devices_tenant_field" ON "devices"("tenantId", "fieldId");

-- CreateIndex: sensors
CREATE INDEX IF NOT EXISTS "idx_sensors_tenant" ON "sensors"("tenantId");
CREATE INDEX IF NOT EXISTS "idx_sensors_device" ON "sensors"("deviceId");
CREATE INDEX IF NOT EXISTS "idx_sensors_type" ON "sensors"("sensorType");
CREATE INDEX IF NOT EXISTS "idx_sensors_device_type" ON "sensors"("deviceId", "sensorType");

-- CreateIndex: sensor_readings
CREATE INDEX IF NOT EXISTS "idx_readings_tenant" ON "sensor_readings"("tenantId");
CREATE INDEX IF NOT EXISTS "idx_readings_sensor" ON "sensor_readings"("sensorId");
CREATE INDEX IF NOT EXISTS "idx_readings_device" ON "sensor_readings"("deviceId");
CREATE INDEX IF NOT EXISTS "idx_readings_timestamp" ON "sensor_readings"("timestamp");
CREATE INDEX IF NOT EXISTS "idx_readings_sensor_time" ON "sensor_readings"("sensorId", "timestamp");
CREATE INDEX IF NOT EXISTS "idx_readings_device_time" ON "sensor_readings"("deviceId", "timestamp");
CREATE INDEX IF NOT EXISTS "idx_readings_device_sensor_time" ON "sensor_readings"("deviceId", "sensorId", "timestamp");

-- CreateIndex: actuators
CREATE INDEX IF NOT EXISTS "idx_actuators_tenant" ON "actuators"("tenantId");
CREATE INDEX IF NOT EXISTS "idx_actuators_device" ON "actuators"("deviceId");
CREATE INDEX IF NOT EXISTS "idx_actuators_type" ON "actuators"("actuatorType");
CREATE INDEX IF NOT EXISTS "idx_actuators_device_type" ON "actuators"("deviceId", "actuatorType");

-- CreateIndex: actuator_commands
CREATE INDEX IF NOT EXISTS "idx_commands_tenant" ON "actuator_commands"("tenantId");
CREATE INDEX IF NOT EXISTS "idx_commands_actuator" ON "actuator_commands"("actuatorId");
CREATE INDEX IF NOT EXISTS "idx_commands_status" ON "actuator_commands"("status");
CREATE INDEX IF NOT EXISTS "idx_commands_requested" ON "actuator_commands"("requestedAt");
CREATE INDEX IF NOT EXISTS "idx_commands_actuator_status" ON "actuator_commands"("actuatorId", "status");
CREATE INDEX IF NOT EXISTS "idx_commands_actuator_requested" ON "actuator_commands"("actuatorId", "requestedAt");

-- CreateIndex: device_alerts
CREATE INDEX IF NOT EXISTS "idx_alerts_device" ON "device_alerts"("deviceId");
CREATE INDEX IF NOT EXISTS "idx_alerts_tenant" ON "device_alerts"("tenantId");
CREATE INDEX IF NOT EXISTS "idx_alerts_severity" ON "device_alerts"("severity");
CREATE INDEX IF NOT EXISTS "idx_alerts_acknowledged" ON "device_alerts"("acknowledged");
CREATE INDEX IF NOT EXISTS "idx_alerts_created" ON "device_alerts"("createdAt");
CREATE INDEX IF NOT EXISTS "idx_alerts_tenant_ack" ON "device_alerts"("tenantId", "acknowledged");
CREATE INDEX IF NOT EXISTS "idx_alerts_tenant_severity" ON "device_alerts"("tenantId", "severity");
CREATE INDEX IF NOT EXISTS "idx_alerts_device_ack" ON "device_alerts"("deviceId", "acknowledged");

-- AddForeignKey
ALTER TABLE "sensors" ADD CONSTRAINT "sensors_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "devices"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sensor_readings" ADD CONSTRAINT "sensor_readings_sensorId_fkey" FOREIGN KEY ("sensorId") REFERENCES "sensors"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sensor_readings" ADD CONSTRAINT "sensor_readings_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "devices"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "actuators" ADD CONSTRAINT "actuators_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "devices"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "actuator_commands" ADD CONSTRAINT "actuator_commands_actuatorId_fkey" FOREIGN KEY ("actuatorId") REFERENCES "actuators"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "device_alerts" ADD CONSTRAINT "device_alerts_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "devices"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- Partition hint for sensor_readings (future optimization):
-- Consider partitioning sensor_readings by timestamp for high-volume time-series data
-- CREATE TABLE sensor_readings_partitioned (...) PARTITION BY RANGE (timestamp);
