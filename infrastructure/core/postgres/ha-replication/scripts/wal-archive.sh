#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - WAL Archive Script
# سكريبت أرشفة WAL لنظام PostgreSQL
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Purpose: Archives PostgreSQL WAL files to S3/MinIO for Point-in-Time Recovery
# Usage: Called by PostgreSQL archive_command
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

WAL_PATH="$1"
WAL_FILE="$2"

# Configuration
S3_ENDPOINT="${S3_ENDPOINT:-http://minio:9000}"
S3_BUCKET="${S3_BUCKET:-sahool-backups}"
S3_PREFIX="wal-archive/$(hostname)"
LOCAL_ARCHIVE_DIR="${LOCAL_ARCHIVE_DIR:-/var/lib/postgresql/wal-archive}"

# Ensure local archive directory exists
mkdir -p "${LOCAL_ARCHIVE_DIR}"

# Copy to local archive first (fast, reliable)
if cp "${WAL_PATH}" "${LOCAL_ARCHIVE_DIR}/${WAL_FILE}"; then
    # Upload to S3 in background for durability
    if command -v aws >/dev/null 2>&1; then
        aws s3 cp "${LOCAL_ARCHIVE_DIR}/${WAL_FILE}" \
            "s3://${S3_BUCKET}/${S3_PREFIX}/${WAL_FILE}" \
            --endpoint-url "${S3_ENDPOINT}" \
            >/dev/null 2>&1 &
    elif command -v wal-g >/dev/null 2>&1; then
        wal-g wal-push "${LOCAL_ARCHIVE_DIR}/${WAL_FILE}" \
            >/dev/null 2>&1 &
    fi

    # Success - WAL archived locally
    exit 0
else
    # Failed to archive locally
    exit 1
fi
