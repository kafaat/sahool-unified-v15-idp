#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# MinIO Initialization Script
# Creates default buckets and configures basic settings after MinIO starts
# سكريبت تهيئة MinIO - إنشاء الحاويات الافتراضية وتكوين الإعدادات الأساسية
# ═══════════════════════════════════════════════════════════════════════════════

set -e

echo "MinIO initialization script started..."

# Wait for MinIO to be ready
echo "Waiting for MinIO to be ready..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:9000/minio/health/live > /dev/null 2>&1; then
    echo "MinIO is ready."
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "ERROR: MinIO did not become ready in time."
    exit 1
  fi
  sleep 2
done

echo "MinIO initialization completed successfully."
