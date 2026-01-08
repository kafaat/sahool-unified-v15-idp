#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - WAL-G Initialization Script
# سكريبت تهيئة WAL-G لنظام PostgreSQL
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Purpose: Initialize WAL-G and S3 bucket for PostgreSQL WAL archiving
# Usage: Run once to set up WAL-G infrastructure
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

# Load environment variables from .env if exists
if [ -f .env ]; then
    log_info "Loading configuration from .env file"
    export $(grep -v '^#' .env | xargs)
fi

# WAL-G Configuration
WALG_S3_PREFIX="${WALG_S3_PREFIX:-s3://sahool-wal-archive/pg-primary}"
AWS_ENDPOINT="${AWS_ENDPOINT:-${S3_ENDPOINT:-http://minio:9000}}"
AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-${S3_ACCESS_KEY:-${MINIO_ROOT_USER}}}"
AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-${S3_SECRET_KEY:-${MINIO_ROOT_PASSWORD}}}"
AWS_REGION="${AWS_REGION:-us-east-1}"

# Extract bucket name from WALG_S3_PREFIX
S3_BUCKET=$(echo "${WALG_S3_PREFIX}" | sed 's|s3://||' | cut -d'/' -f1)

log_info "WAL-G Configuration:"
log_info "  S3 Prefix: ${WALG_S3_PREFIX}"
log_info "  S3 Bucket: ${S3_BUCKET}"
log_info "  Endpoint:  ${AWS_ENDPOINT}"
log_info "  Region:    ${AWS_REGION}"

# ═══════════════════════════════════════════════════════════════════════════════
# Validation
# ═══════════════════════════════════════════════════════════════════════════════

log_info "Validating configuration..."

if [ -z "${AWS_ACCESS_KEY_ID}" ] || [ -z "${AWS_SECRET_ACCESS_KEY}" ]; then
    log_error "AWS credentials not set. Please configure:"
    log_error "  - AWS_ACCESS_KEY_ID (or S3_ACCESS_KEY or MINIO_ROOT_USER)"
    log_error "  - AWS_SECRET_ACCESS_KEY (or S3_SECRET_KEY or MINIO_ROOT_PASSWORD)"
    exit 1
fi

# Check if WAL-G is installed
if ! command -v wal-g >/dev/null 2>&1; then
    log_error "WAL-G not found. Please install WAL-G or use the custom Docker image."
    exit 1
fi

log_info "WAL-G version: $(wal-g --version)"

# Check if AWS CLI is installed
if ! command -v aws >/dev/null 2>&1; then
    log_warn "AWS CLI not found. Install it for better S3 management."
else
    log_info "AWS CLI version: $(aws --version)"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# S3 Bucket Creation
# ═══════════════════════════════════════════════════════════════════════════════

log_info "Checking S3 bucket: ${S3_BUCKET}"

if command -v aws >/dev/null 2>&1; then
    # Configure AWS CLI
    export AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY
    export AWS_DEFAULT_REGION="${AWS_REGION}"

    # Check if bucket exists
    if aws s3 ls "s3://${S3_BUCKET}" --endpoint-url "${AWS_ENDPOINT}" >/dev/null 2>&1; then
        log_info "Bucket ${S3_BUCKET} already exists"
    else
        log_info "Creating S3 bucket: ${S3_BUCKET}"
        if aws s3 mb "s3://${S3_BUCKET}" --endpoint-url "${AWS_ENDPOINT}"; then
            log_info "Successfully created bucket ${S3_BUCKET}"

            # Enable versioning (recommended for disaster recovery)
            log_info "Enabling versioning on bucket ${S3_BUCKET}"
            aws s3api put-bucket-versioning \
                --bucket "${S3_BUCKET}" \
                --versioning-configuration Status=Enabled \
                --endpoint-url "${AWS_ENDPOINT}" || log_warn "Could not enable versioning (may not be supported)"
        else
            log_error "Failed to create bucket ${S3_BUCKET}"
            exit 1
        fi
    fi

    # Set bucket lifecycle policy (optional - clean up old WAL files)
    log_info "Setting lifecycle policy for old WAL files (30 days retention)"
    cat > /tmp/lifecycle-policy.json <<EOF
{
    "Rules": [
        {
            "Id": "DeleteOldWAL",
            "Status": "Enabled",
            "Prefix": "wal/",
            "Expiration": {
                "Days": 30
            }
        }
    ]
}
EOF

    aws s3api put-bucket-lifecycle-configuration \
        --bucket "${S3_BUCKET}" \
        --lifecycle-configuration file:///tmp/lifecycle-policy.json \
        --endpoint-url "${AWS_ENDPOINT}" 2>/dev/null || log_warn "Could not set lifecycle policy (may not be supported by MinIO)"

    rm /tmp/lifecycle-policy.json
else
    log_warn "AWS CLI not available. Skipping bucket creation."
    log_warn "Please manually create S3 bucket: ${S3_BUCKET}"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Test WAL-G Connection
# ═══════════════════════════════════════════════════════════════════════════════

log_info "Testing WAL-G connection to S3..."

export WALG_S3_PREFIX
export AWS_ENDPOINT
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export AWS_REGION
export AWS_S3_FORCE_PATH_STYLE=true

# Test by listing backups (should return empty or existing backups)
if wal-g backup-list 2>&1 | grep -q "No backups found\|.*backup.*"; then
    log_info "✓ WAL-G successfully connected to S3"
else
    log_error "✗ WAL-G connection test failed"
    log_error "Please verify your S3 credentials and endpoint"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Create Base Backup (Optional)
# ═══════════════════════════════════════════════════════════════════════════════

log_info ""
log_info "═══════════════════════════════════════════════════════════════"
log_info "WAL-G Initialization Complete!"
log_info "═══════════════════════════════════════════════════════════════"
log_info ""
log_info "Next steps:"
log_info "1. Restart PostgreSQL to enable WAL archiving"
log_info "2. Create a base backup:"
log_info "   docker-compose exec postgres wal-g backup-push /var/lib/postgresql/data"
log_info ""
log_info "3. Verify backup:"
log_info "   docker-compose exec postgres wal-g backup-list"
log_info ""
log_info "4. Monitor WAL archiving:"
log_info "   tail -f /var/log/postgresql/wal-archive.log"
log_info ""
log_info "For disaster recovery documentation, see:"
log_info "   config/postgres/PITR_RECOVERY.md"
log_info "═══════════════════════════════════════════════════════════════"
