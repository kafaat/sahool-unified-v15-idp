#!/bin/bash
# ============================================================================
# Konga Database Initialization Script
# سكريبت تهيئة قاعدة بيانات Konga
# ============================================================================
# This script creates the Konga database if it doesn't exist
# يقوم هذا السكريبت بإنشاء قاعدة بيانات Konga إذا لم تكن موجودة
# ============================================================================

set -e

# Wait for PostgreSQL to be ready
until pg_isready -U "${KONG_PG_USER:-kong}" -d "${KONG_PG_DATABASE:-kong}"; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

echo "PostgreSQL is ready!"

# Create Konga database if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "${KONG_PG_USER:-kong}" --dbname "${KONG_PG_DATABASE:-kong}" <<-EOSQL
    SELECT 'CREATE DATABASE konga'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'konga')\gexec
EOSQL

echo "Konga database initialized successfully!"
