#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - WAL Archive Script with WAL-G
# سكريبت أرشفة WAL لنظام PostgreSQL مع WAL-G
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 2.0.0
# Purpose: Archives PostgreSQL WAL files to S3/MinIO using WAL-G
# Usage: Called by PostgreSQL archive_command
# Environment Variables:
#   - WALG_S3_PREFIX: S3 path (e.g., s3://sahool-wal-archive/pg-primary)
#   - AWS_ENDPOINT: S3 endpoint URL (for MinIO compatibility)
#   - AWS_ACCESS_KEY_ID: S3 access key
#   - AWS_SECRET_ACCESS_KEY: S3 secret key
#   - AWS_REGION: S3 region (default: us-east-1)
#   - AWS_S3_FORCE_PATH_STYLE: Set to 'true' for MinIO compatibility
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Arguments from PostgreSQL
WAL_PATH="$1"
WAL_FILE="$2"

# Configuration
LOCAL_ARCHIVE_DIR="${LOCAL_ARCHIVE_DIR:-/var/lib/postgresql/wal_archive}"
LOG_FILE="${WAL_ARCHIVE_LOG:-/var/log/postgresql/wal-archive.log}"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}" >&2
}

# Ensure local archive directory exists (for fallback/quick recovery)
mkdir -p "${LOCAL_ARCHIVE_DIR}"

# Create log directory if it doesn't exist
mkdir -p "$(dirname "${LOG_FILE}")"

log "INFO: Starting WAL archive for ${WAL_FILE}"

# ─────────────────────────────────────────────────────────────────────────────
# Strategy 1: WAL-G to S3/MinIO (Primary method)
# ─────────────────────────────────────────────────────────────────────────────
if command -v wal-g >/dev/null 2>&1; then
    log "INFO: Using WAL-G for archiving to S3/MinIO"

    # Verify required environment variables
    if [ -z "${WALG_S3_PREFIX:-}" ]; then
        log "ERROR: WALG_S3_PREFIX not set. Cannot archive to S3."
    else
        # Archive using WAL-G
        if wal-g wal-push "${WAL_PATH}" 2>&1 | tee -a "${LOG_FILE}"; then
            log "SUCCESS: WAL file ${WAL_FILE} archived to S3 via WAL-G"

            # Also keep local copy for quick recovery
            if cp "${WAL_PATH}" "${LOCAL_ARCHIVE_DIR}/${WAL_FILE}"; then
                log "INFO: Local copy saved to ${LOCAL_ARCHIVE_DIR}/${WAL_FILE}"
            fi

            exit 0
        else
            log "WARNING: WAL-G archiving failed for ${WAL_FILE}, trying fallback method"
        fi
    fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# Strategy 2: AWS CLI to S3/MinIO (Fallback method)
# ─────────────────────────────────────────────────────────────────────────────
if command -v aws >/dev/null 2>&1; then
    log "INFO: Using AWS CLI for archiving to S3/MinIO"

    # Extract bucket and prefix from WALG_S3_PREFIX if available
    if [ -n "${WALG_S3_PREFIX:-}" ]; then
        S3_BUCKET=$(echo "${WALG_S3_PREFIX}" | sed 's|s3://||' | cut -d'/' -f1)
        S3_PREFIX=$(echo "${WALG_S3_PREFIX}" | sed 's|s3://||' | cut -d'/' -f2-)
        S3_PATH="s3://${S3_BUCKET}/${S3_PREFIX}/wal/${WAL_FILE}"
    else
        S3_BUCKET="${S3_BUCKET:-sahool-backups}"
        S3_PREFIX="postgres-wal/$(hostname)"
        S3_PATH="s3://${S3_BUCKET}/${S3_PREFIX}/${WAL_FILE}"
    fi

    AWS_ENDPOINT_PARAM=""
    if [ -n "${AWS_ENDPOINT:-}" ]; then
        AWS_ENDPOINT_PARAM="--endpoint-url ${AWS_ENDPOINT}"
    fi

    # Upload to S3
    if aws s3 cp "${WAL_PATH}" "${S3_PATH}" ${AWS_ENDPOINT_PARAM} 2>&1 | tee -a "${LOG_FILE}"; then
        log "SUCCESS: WAL file ${WAL_FILE} archived to S3 via AWS CLI"

        # Also keep local copy
        if cp "${WAL_PATH}" "${LOCAL_ARCHIVE_DIR}/${WAL_FILE}"; then
            log "INFO: Local copy saved to ${LOCAL_ARCHIVE_DIR}/${WAL_FILE}"
        fi

        exit 0
    else
        log "WARNING: AWS CLI archiving failed for ${WAL_FILE}, trying local-only method"
    fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# Strategy 3: Local filesystem only (Emergency fallback)
# ─────────────────────────────────────────────────────────────────────────────
log "WARNING: S3 archiving not available, using local filesystem only"

if cp "${WAL_PATH}" "${LOCAL_ARCHIVE_DIR}/${WAL_FILE}"; then
    log "SUCCESS: WAL file ${WAL_FILE} archived locally (no S3 backup)"
    exit 0
else
    log "ERROR: Failed to archive ${WAL_FILE} - all methods failed"
    exit 1
fi
