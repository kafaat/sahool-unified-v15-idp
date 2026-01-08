#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - WAL Restore Script
# سكريبت استعادة WAL لنظام PostgreSQL
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Purpose: Restores PostgreSQL WAL files from S3/MinIO for Point-in-Time Recovery
# Usage: Called by PostgreSQL restore_command
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

WAL_FILE="$1"
WAL_DEST="$2"

# Configuration
S3_ENDPOINT="${S3_ENDPOINT:-http://minio:9000}"
S3_BUCKET="${S3_BUCKET:-sahool-backups}"
S3_PREFIX="wal-archive"
LOCAL_ARCHIVE_DIR="${LOCAL_ARCHIVE_DIR:-/var/lib/postgresql/wal-archive}"

# Try local archive first (fastest)
if [ -f "${LOCAL_ARCHIVE_DIR}/${WAL_FILE}" ]; then
    cp "${LOCAL_ARCHIVE_DIR}/${WAL_FILE}" "${WAL_DEST}"
    exit 0
fi

# Try S3/MinIO
if command -v aws >/dev/null 2>&1; then
    # Try to find WAL file in any of the archived hosts
    for host_dir in $(aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/" --endpoint-url "${S3_ENDPOINT}" 2>/dev/null | awk '{print $2}' | tr -d '/'); do
        if aws s3 cp "s3://${S3_BUCKET}/${S3_PREFIX}/${host_dir}/${WAL_FILE}" \
            "${WAL_DEST}" \
            --endpoint-url "${S3_ENDPOINT}" \
            >/dev/null 2>&1; then
            exit 0
        fi
    done
elif command -v wal-g >/dev/null 2>&1; then
    if wal-g wal-fetch "${WAL_FILE}" "${WAL_DEST}" >/dev/null 2>&1; then
        exit 0
    fi
fi

# WAL file not found
exit 1
