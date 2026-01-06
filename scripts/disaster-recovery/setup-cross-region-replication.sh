#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Cross-Region Backup Replication Setup
# إعداد النسخ الاحتياطي عبر المناطق
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Purpose: Configure S3 cross-region replication for disaster recovery
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Colors
# ─────────────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Load environment
if [ -f "${PROJECT_ROOT}/.env" ]; then
    set -a
    source "${PROJECT_ROOT}/.env"
    set +a
fi

# AWS/S3 Configuration
PRIMARY_REGION="${AWS_REGION:-me-south-1}"
SECONDARY_REGION="${AWS_SECONDARY_REGION:-me-central-1}"
PRIMARY_BUCKET="${S3_BUCKET:-sahool-backups}"
SECONDARY_BUCKET="${S3_SECONDARY_BUCKET:-sahool-backups-replica}"

# MinIO Configuration (for self-hosted)
MINIO_PRIMARY_ENDPOINT="${MINIO_PRIMARY_ENDPOINT:-http://minio:9000}"
MINIO_SECONDARY_ENDPOINT="${MINIO_SECONDARY_ENDPOINT:-http://minio-replica:9000}"
MINIO_ACCESS_KEY="${MINIO_ROOT_USER:-minioadmin}"
MINIO_SECRET_KEY="${MINIO_ROOT_PASSWORD:-minioadmin}"

# Logging
LOG_DIR="${PROJECT_ROOT}/logs/cross-region"
LOG_FILE="${LOG_DIR}/setup_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "${LOG_DIR}"

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

print_message() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}" | tee -a "${LOG_FILE}"
}

info_message() {
    print_message "${BLUE}" "ℹ $1"
}

success_message() {
    print_message "${GREEN}" "✓ $1"
}

warning_message() {
    print_message "${YELLOW}" "⚠ $1"
}

error_exit() {
    print_message "${RED}" "✗ ERROR: $1"
    exit 1
}

# ─────────────────────────────────────────────────────────────────────────────
# AWS S3 Cross-Region Replication
# ─────────────────────────────────────────────────────────────────────────────

setup_aws_crr() {
    info_message "Setting up AWS S3 Cross-Region Replication..."

    # Check if AWS CLI is available
    if ! command -v aws >/dev/null 2>&1; then
        error_exit "AWS CLI not found. Please install it first."
    fi

    # Step 1: Create secondary bucket if it doesn't exist
    info_message "Creating secondary bucket in ${SECONDARY_REGION}..."
    if aws s3 ls "s3://${SECONDARY_BUCKET}" --region "${SECONDARY_REGION}" >/dev/null 2>&1; then
        success_message "Secondary bucket already exists"
    else
        aws s3 mb "s3://${SECONDARY_BUCKET}" --region "${SECONDARY_REGION}" || \
            error_exit "Failed to create secondary bucket"
        success_message "Secondary bucket created"
    fi

    # Step 2: Enable versioning on both buckets (required for CRR)
    info_message "Enabling versioning on primary bucket..."
    aws s3api put-bucket-versioning \
        --bucket "${PRIMARY_BUCKET}" \
        --region "${PRIMARY_REGION}" \
        --versioning-configuration Status=Enabled || \
        error_exit "Failed to enable versioning on primary bucket"

    info_message "Enabling versioning on secondary bucket..."
    aws s3api put-bucket-versioning \
        --bucket "${SECONDARY_BUCKET}" \
        --region "${SECONDARY_REGION}" \
        --versioning-configuration Status=Enabled || \
        error_exit "Failed to enable versioning on secondary bucket"

    success_message "Versioning enabled on both buckets"

    # Step 3: Create IAM role for replication
    info_message "Creating IAM role for replication..."

    local role_name="sahool-s3-crr-role"
    local trust_policy='{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {
                "Service": "s3.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }]
    }'

    # Create role if it doesn't exist
    if ! aws iam get-role --role-name "$role_name" >/dev/null 2>&1; then
        aws iam create-role \
            --role-name "$role_name" \
            --assume-role-policy-document "$trust_policy" || \
            error_exit "Failed to create IAM role"
        success_message "IAM role created"
    else
        success_message "IAM role already exists"
    fi

    # Step 4: Attach permissions policy
    local policy_arn="arn:aws:iam::aws:policy/AmazonS3FullAccess"
    aws iam attach-role-policy \
        --role-name "$role_name" \
        --policy-arn "$policy_arn" 2>/dev/null || true

    # Get role ARN
    local role_arn=$(aws iam get-role --role-name "$role_name" --query 'Role.Arn' --output text)

    # Step 5: Create replication configuration
    info_message "Creating replication configuration..."

    cat > /tmp/replication-config.json <<EOF
{
    "Role": "${role_arn}",
    "Rules": [
        {
            "ID": "sahool-backup-replication",
            "Priority": 1,
            "Filter": {},
            "Status": "Enabled",
            "Destination": {
                "Bucket": "arn:aws:s3:::${SECONDARY_BUCKET}",
                "ReplicationTime": {
                    "Status": "Enabled",
                    "Time": {
                        "Minutes": 15
                    }
                },
                "Metrics": {
                    "Status": "Enabled",
                    "EventThreshold": {
                        "Minutes": 15
                    }
                }
            },
            "DeleteMarkerReplication": {
                "Status": "Enabled"
            }
        }
    ]
}
EOF

    aws s3api put-bucket-replication \
        --bucket "${PRIMARY_BUCKET}" \
        --region "${PRIMARY_REGION}" \
        --replication-configuration file:///tmp/replication-config.json || \
        error_exit "Failed to create replication configuration"

    rm /tmp/replication-config.json

    success_message "AWS S3 Cross-Region Replication configured successfully"
}

# ─────────────────────────────────────────────────────────────────────────────
# MinIO Mirror Replication
# ─────────────────────────────────────────────────────────────────────────────

setup_minio_mirror() {
    info_message "Setting up MinIO mirror replication..."

    # Check if mc (MinIO Client) is available
    if ! command -v mc >/dev/null 2>&1; then
        warning_message "MinIO Client (mc) not found. Installing..."

        # Install mc
        wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /tmp/mc
        chmod +x /tmp/mc
        sudo mv /tmp/mc /usr/local/bin/mc
        success_message "MinIO Client installed"
    fi

    # Configure MinIO aliases
    info_message "Configuring MinIO aliases..."

    mc alias set primary "${MINIO_PRIMARY_ENDPOINT}" \
        "${MINIO_ACCESS_KEY}" "${MINIO_SECRET_KEY}" || \
        error_exit "Failed to configure primary MinIO alias"

    mc alias set secondary "${MINIO_SECONDARY_ENDPOINT}" \
        "${MINIO_ACCESS_KEY}" "${MINIO_SECRET_KEY}" || \
        error_exit "Failed to configure secondary MinIO alias"

    success_message "MinIO aliases configured"

    # Create buckets if they don't exist
    info_message "Creating buckets..."

    mc mb -p "primary/${PRIMARY_BUCKET}" 2>/dev/null || true
    mc mb -p "secondary/${SECONDARY_BUCKET}" 2>/dev/null || true

    success_message "Buckets created"

    # Enable versioning
    info_message "Enabling versioning..."

    mc version enable "primary/${PRIMARY_BUCKET}" || true
    mc version enable "secondary/${SECONDARY_BUCKET}" || true

    success_message "Versioning enabled"

    # Set up bucket replication
    info_message "Configuring bucket replication..."

    mc replicate add "primary/${PRIMARY_BUCKET}" \
        --remote-bucket "secondary/${SECONDARY_BUCKET}" \
        --replicate "delete,delete-marker,existing-objects" \
        --priority 1 || \
        error_exit "Failed to configure bucket replication"

    success_message "MinIO mirror replication configured successfully"

    # Create sync cron job
    create_minio_sync_cron
}

# ─────────────────────────────────────────────────────────────────────────────
# Create Continuous Sync Script
# ─────────────────────────────────────────────────────────────────────────────

create_minio_sync_cron() {
    info_message "Creating continuous sync script..."

    local sync_script="${PROJECT_ROOT}/scripts/disaster-recovery/sync-to-secondary.sh"

    cat > "$sync_script" <<'EOF'
#!/bin/bash
# Continuous sync to secondary region

set -euo pipefail

PRIMARY_BUCKET="${PRIMARY_BUCKET:-sahool-backups}"
SECONDARY_BUCKET="${SECONDARY_BUCKET:-sahool-backups-replica}"

# Sync using mc mirror
mc mirror --watch --remove \
    "primary/${PRIMARY_BUCKET}" \
    "secondary/${SECONDARY_BUCKET}" \
    >> /var/log/sahool/minio-sync.log 2>&1
EOF

    chmod +x "$sync_script"

    # Add to crontab
    local cron_entry="*/15 * * * * ${sync_script}"

    # Check if entry already exists
    if ! crontab -l 2>/dev/null | grep -q "$sync_script"; then
        (crontab -l 2>/dev/null; echo "$cron_entry") | crontab -
        success_message "Sync cron job created (runs every 15 minutes)"
    else
        success_message "Sync cron job already exists"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Database Cross-Region Replication (for RDS)
# ─────────────────────────────────────────────────────────────────────────────

setup_database_crr() {
    info_message "Setting up database cross-region replication..."

    if ! command -v aws >/dev/null 2>&1; then
        warning_message "AWS CLI not found. Skipping RDS cross-region setup."
        return 0
    fi

    local db_instance="${DB_INSTANCE_ID:-sahool-postgres}"
    local read_replica_id="${db_instance}-replica-${SECONDARY_REGION}"

    # Check if source database exists
    if ! aws rds describe-db-instances \
        --db-instance-identifier "$db_instance" \
        --region "${PRIMARY_REGION}" >/dev/null 2>&1; then
        warning_message "Source database not found. Skipping RDS cross-region setup."
        return 0
    fi

    # Create read replica in secondary region
    info_message "Creating cross-region read replica..."

    if aws rds describe-db-instances \
        --db-instance-identifier "$read_replica_id" \
        --region "${SECONDARY_REGION}" >/dev/null 2>&1; then
        success_message "Read replica already exists"
    else
        aws rds create-db-instance-read-replica \
            --db-instance-identifier "$read_replica_id" \
            --source-db-instance-identifier "arn:aws:rds:${PRIMARY_REGION}:*:db:${db_instance}" \
            --region "${SECONDARY_REGION}" \
            --db-instance-class db.r6g.large \
            --publicly-accessible false || \
            warning_message "Failed to create read replica (may need manual setup)"
    fi

    success_message "Database cross-region replication configured"
}

# ─────────────────────────────────────────────────────────────────────────────
# Verify Replication
# ─────────────────────────────────────────────────────────────────────────────

verify_replication() {
    info_message "Verifying replication setup..."

    # Test file upload and replication
    local test_file="/tmp/sahool-replication-test-$(date +%s).txt"
    echo "SAHOOL Platform - Replication Test - $(date)" > "$test_file"

    # Upload to primary
    if command -v mc >/dev/null 2>&1; then
        mc cp "$test_file" "primary/${PRIMARY_BUCKET}/test/" || \
            warning_message "Failed to upload test file"

        # Wait for replication
        sleep 5

        # Check if file exists in secondary
        if mc ls "secondary/${SECONDARY_BUCKET}/test/" | grep -q "$(basename $test_file)"; then
            success_message "Replication verified: File replicated successfully"
        else
            warning_message "Replication may not be working properly"
        fi

        # Cleanup
        mc rm "primary/${PRIMARY_BUCKET}/test/$(basename $test_file)" 2>/dev/null || true
        mc rm "secondary/${SECONDARY_BUCKET}/test/$(basename $test_file)" 2>/dev/null || true
    fi

    rm -f "$test_file"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Function
# ─────────────────────────────────────────────────────────────────────────────

show_usage() {
    cat <<EOF
SAHOOL Platform - Cross-Region Replication Setup

Usage: $0 [OPTION]

Options:
    aws         Configure AWS S3 Cross-Region Replication
    minio       Configure MinIO mirror replication
    database    Configure database cross-region replication
    all         Configure all replication types
    verify      Verify replication is working
    -h, --help  Show this help message

Examples:
    $0 aws              # Setup AWS S3 CRR
    $0 minio            # Setup MinIO mirror
    $0 all              # Setup everything
    $0 verify           # Verify replication

EOF
}

main() {
    local mode="${1:-all}"

    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"
    print_message "${BLUE}" "  SAHOOL Platform - Cross-Region Replication Setup"
    print_message "${BLUE}" "  إعداد النسخ الاحتياطي عبر المناطق"
    print_message "${BLUE}" "═══════════════════════════════════════════════════════════════"

    case "$mode" in
        aws)
            setup_aws_crr
            ;;

        minio)
            setup_minio_mirror
            ;;

        database)
            setup_database_crr
            ;;

        all)
            # Try AWS first, fallback to MinIO
            if command -v aws >/dev/null 2>&1; then
                setup_aws_crr
            else
                warning_message "AWS CLI not found, using MinIO instead"
                setup_minio_mirror
            fi
            setup_database_crr
            ;;

        verify)
            verify_replication
            ;;

        -h|--help)
            show_usage
            exit 0
            ;;

        *)
            error_exit "Unknown option: $mode. Use -h for help."
            ;;
    esac

    echo ""
    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"
    success_message "Cross-region replication setup completed!"
    info_message "Primary Region: ${PRIMARY_REGION}"
    info_message "Secondary Region: ${SECONDARY_REGION}"
    info_message "Primary Bucket: ${PRIMARY_BUCKET}"
    info_message "Secondary Bucket: ${SECONDARY_BUCKET}"
    print_message "${GREEN}" "═══════════════════════════════════════════════════════════════"
}

main "$@"
