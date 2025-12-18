-- SAHOOL Database Initialization Script
-- Creates all required databases and extensions

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create databases for each service
CREATE DATABASE sahool_auth;
CREATE DATABASE sahool_tenant;
CREATE DATABASE sahool_user;
CREATE DATABASE sahool_geo;
CREATE DATABASE sahool_crop;
CREATE DATABASE sahool_weather;
CREATE DATABASE sahool_ndvi;
CREATE DATABASE sahool_soil;
CREATE DATABASE sahool_astro;
CREATE DATABASE sahool_diagnosis;
CREATE DATABASE sahool_disease;
CREATE DATABASE sahool_irrigation;
CREATE DATABASE sahool_advisor;
CREATE DATABASE sahool_market;
CREATE DATABASE sahool_tasks;
CREATE DATABASE sahool_alerts;
CREATE DATABASE sahool_notification;
CREATE DATABASE sahool_equipment;
CREATE DATABASE sahool_process;
CREATE DATABASE sahool_schema;

-- Enable extensions on geo database
\c sahool_geo
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Enable extensions on all databases
\c sahool_auth
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c sahool_tenant
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c sahool_user
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c sahool_crop
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c sahool_weather
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

\c sahool_ndvi
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

\c sahool_soil
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

\c sahool_astro
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c sahool_diagnosis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c sahool_disease
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

\c sahool_irrigation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

\c sahool_advisor
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c sahool_market
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c sahool_tasks
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c sahool_alerts
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c sahool_notification
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c sahool_equipment
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

\c sahool_process
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c sahool_schema
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant privileges
GRANT ALL PRIVILEGES ON ALL DATABASES TO sahool;

-- Log completion
\echo 'SAHOOL databases initialized successfully!'
