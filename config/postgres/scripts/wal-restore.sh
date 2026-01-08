#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - WAL Restore Script with WAL-G
# سكريبت استعادة WAL لنظام PostgreSQL مع WAL-G
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 2.0.0
# Purpose: Restores PostgreSQL WAL files from S3/MinIO using WAL-G
# Usage: Called by PostgreSQL restore_command during Point-in-Time Recovery
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
WAL_FILE="$1"
WAL_DEST="$2"

# Configuration
LOCAL_ARCHIVE_DIR="${LOCAL_ARCHIVE_DIR:-/var/lib/postgresql/wal_archive}"
LOG_FILE="${WAL_RESTORE_LOG:-/var/log/postgresql/wal-restore.log}"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}" >&2
}

# Create log directory if it doesn't exist
mkdir -p "$(dirname "${LOG_FILE}")"

log "INFO: Starting WAL restore for ${WAL_FILE}"

# ─────────────────────────────────────────────────────────────────────────────
# Strategy 1: Local archive (Fastest - check first)
# ─────────────────────────────────────────────────────────────────────────────
if [ -f "${LOCAL_ARCHIVE_DIR}/${WAL_FILE}" ]; then
    log "INFO: Found ${WAL_FILE} in local archive"

    if cp "${LOCAL_ARCHIVE_DIR}/${WAL_FILE}" "${WAL_DEST}"; then
        log "SUCCESS: Restored ${WAL_FILE} from local archive"
        exit 0
    else
        log "WARNING: Failed to copy from local archive, trying S3"
    fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# Strategy 2: WAL-G from S3/MinIO (Primary remote method)
# ─────────────────────────────────────────────────────────────────────────────
if command -v wal-g >/dev/null 2>&1; then
    log "INFO: Using WAL-G to restore from S3/MinIO"

    if [ -z "${WALG_S3_PREFIX:-}" ]; then
        log "WARNING: WALG_S3_PREFIX not set, skipping WAL-G restore"
    else
        if wal-g wal-fetch "${WAL_FILE}" "${WAL_DEST}" 2>&1 | tee -a "${LOG_FILE}"; then
            log "SUCCESS: Restored ${WAL_FILE} from S3 via WAL-G"

            # Save to local archive for future quick access
            mkdir -p "${LOCAL_ARCHIVE_DIR}"
            if cp "${WAL_DEST}" "${LOCAL_ARCHIVE_DIR}/${WAL_FILE}"; then
                log "INFO: Cached ${WAL_FILE} to local archive"
            fi

            exit 0
        else
            log "WARNING: WAL-G restore failed for ${WAL_FILE}, trying AWS CLI"
        fi
    fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# Strategy 3: AWS CLI from S3/MinIO (Fallback remote method)
# ─────────────────────────────────────────────────────────────────────────────
if command -v aws >/dev/null 2>&1; then
    log "INFO: Using AWS CLI to restore from S3/MinIO"

    # Extract bucket and prefix from WALG_S3_PREFIX if available
    if [ -n "${WALG_S3_PREFIX:-}" ]; then
        S3_BUCKET=$(echo "${WALG_S3_PREFIX}" | sed 's|s3://||' | cut -d'/' -f1)
        S3_PREFIX=$(echo "${WALG_S3_PREFIX}" | sed 's|s3://||' | cut -d'/' -f2-)

        # Try multiple potential paths
        S3_PATHS=(
            "s3://${S3_BUCKET}/${S3_PREFIX}/wal/${WAL_FILE}"
            "s3://${S3_BUCKET}/${S3_PREFIX}/${WAL_FILE}"
        )
    else
        S3_BUCKET="${S3_BUCKET:-sahool-backups}"
        S3_PATHS=(
            "s3://${S3_BUCKET}/postgres-wal/$(hostname)/${WAL_FILE}"
            "s3://${S3_BUCKET}/wal-archive/${WAL_FILE}"
        )
    fi

    AWS_ENDPOINT_PARAM=""
    if [ -n "${AWS_ENDPOINT:-}" ]; then
        AWS_ENDPOINT_PARAM="--endpoint-url ${AWS_ENDPOINT}"
    fi

    # Try each potential S3 path
    for S3_PATH in "${S3_PATHS[@]}"; do
        log "INFO: Trying to restore from ${S3_PATH}"

        if aws s3 cp "${S3_PATH}" "${WAL_DEST}" ${AWS_ENDPOINT_PARAM} 2>&1 | tee -a "${LOG_FILE}"; then
            log "SUCCESS: Restored ${WAL_FILE} from S3 via AWS CLI"

            # Save to local archive for future quick access
            mkdir -p "${LOCAL_ARCHIVE_DIR}"
            if cp "${WAL_DEST}" "${LOCAL_ARCHIVE_DIR}/${WAL_FILE}"; then
                log "INFO: Cached ${WAL_FILE} to local archive"
            fi

            exit 0
        fi
    done

    log "WARNING: Could not find ${WAL_FILE} in any S3 paths"
fi

# ─────────────────────────────────────────────────────────────────────────────
# All strategies failed
# ─────────────────────────────────────────────────────────────────────────────
log "ERROR: Failed to restore ${WAL_FILE} - not found in local or S3 archives"
exit 1
