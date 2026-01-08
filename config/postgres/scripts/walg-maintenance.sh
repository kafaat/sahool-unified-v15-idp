#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - WAL-G Maintenance Script
# سكريبت صيانة WAL-G
# ═══════════════════════════════════════════════════════════════════════════════
# Version: 1.0.0
# Purpose: Automated maintenance tasks for WAL-G backups
# Usage: ./walg-maintenance.sh [backup|cleanup|verify|status|help]
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RETAIN_BACKUPS="${WALG_RETAIN_BACKUPS:-7}"
NOTIFICATION_EMAIL="${BACKUP_EMAIL_TO:-admin@sahool.com}"

# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════

log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date +'%Y-%m-%d %H:%M:%S') - $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date +'%Y-%m-%d %H:%M:%S') - $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date +'%Y-%m-%d %H:%M:%S') - $*"
}

send_notification() {
    local SUBJECT="$1"
    local MESSAGE="$2"

    # Try to send email if mail command is available
    if command -v mail >/dev/null 2>&1; then
        echo "$MESSAGE" | mail -s "$SUBJECT" "$NOTIFICATION_EMAIL"
    fi

    # Log the notification
    log_info "Notification: $SUBJECT"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Maintenance Functions
# ═══════════════════════════════════════════════════════════════════════════════

create_backup() {
    log_info "Creating PostgreSQL base backup..."

    # Check if PostgreSQL is running
    if ! docker-compose exec -T postgres pg_isready -U sahool >/dev/null 2>&1; then
        log_error "PostgreSQL is not ready. Aborting backup."
        send_notification "Backup Failed" "PostgreSQL is not ready"
        return 1
    fi

    # Create backup
    START_TIME=$(date +%s)
    log_info "Backup started at $(date)"

    if docker-compose exec -T postgres wal-g backup-push /var/lib/postgresql/data 2>&1 | tee /tmp/backup.log; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))

        log_info "Backup completed successfully in ${DURATION} seconds"

        # Get backup name
        BACKUP_NAME=$(docker-compose exec -T postgres wal-g backup-list 2>/dev/null | tail -1 | awk '{print $1}')

        send_notification "Backup Successful" "PostgreSQL backup completed successfully.\nBackup: $BACKUP_NAME\nDuration: ${DURATION}s"
        return 0
    else
        log_error "Backup failed"
        send_notification "Backup Failed" "PostgreSQL backup failed. Check logs for details."
        return 1
    fi
}

cleanup_old_backups() {
    log_info "Cleaning up old backups (retaining last $RETAIN_BACKUPS backups)..."

    # List backups before cleanup
    BEFORE_COUNT=$(docker-compose exec -T postgres wal-g backup-list 2>/dev/null | grep -c "^base_" || echo "0")
    log_info "Current backup count: $BEFORE_COUNT"

    if [ "$BEFORE_COUNT" -le "$RETAIN_BACKUPS" ]; then
        log_info "No cleanup needed (backups: $BEFORE_COUNT, retain: $RETAIN_BACKUPS)"
        return 0
    fi

    # Perform cleanup
    if docker-compose exec -T postgres wal-g delete retain "$RETAIN_BACKUPS" --confirm 2>&1 | tee /tmp/cleanup.log; then
        AFTER_COUNT=$(docker-compose exec -T postgres wal-g backup-list 2>/dev/null | grep -c "^base_" || echo "0")
        DELETED=$((BEFORE_COUNT - AFTER_COUNT))

        log_info "Cleanup completed: $DELETED backup(s) deleted, $AFTER_COUNT remaining"
        send_notification "Backup Cleanup" "Cleaned up $DELETED old backup(s). Remaining: $AFTER_COUNT"
        return 0
    else
        log_error "Cleanup failed"
        send_notification "Cleanup Failed" "Failed to clean up old backups"
        return 1
    fi
}

verify_backups() {
    log_info "Verifying backup integrity..."

    # List all backups
    log_info "Available backups:"
    docker-compose exec -T postgres wal-g backup-list 2>/dev/null || {
        log_error "Failed to list backups"
        return 1
    }

    # Get latest backup
    LATEST_BACKUP=$(docker-compose exec -T postgres wal-g backup-list 2>/dev/null | tail -1 | awk '{print $1}')

    if [ -z "$LATEST_BACKUP" ]; then
        log_error "No backups found"
        send_notification "Backup Verification Failed" "No backups available"
        return 1
    fi

    log_info "Latest backup: $LATEST_BACKUP"

    # Show backup details
    log_info "Backup details:"
    docker-compose exec -T postgres wal-g backup-show "$LATEST_BACKUP" 2>/dev/null || {
        log_error "Failed to show backup details"
        return 1
    }

    # Check backup age
    BACKUP_TIME=$(docker-compose exec -T postgres wal-g backup-list 2>/dev/null | tail -1 | awk '{print $2}')
    BACKUP_TIMESTAMP=$(date -d "$BACKUP_TIME" +%s 2>/dev/null || echo "0")
    CURRENT_TIMESTAMP=$(date +%s)
    BACKUP_AGE=$((CURRENT_TIMESTAMP - BACKUP_TIMESTAMP))
    BACKUP_AGE_HOURS=$((BACKUP_AGE / 3600))

    if [ "$BACKUP_AGE_HOURS" -gt 26 ]; then
        log_warn "Latest backup is $BACKUP_AGE_HOURS hours old (threshold: 26 hours)"
        send_notification "Old Backup Warning" "Latest backup is $BACKUP_AGE_HOURS hours old"
    else
        log_info "Latest backup age: $BACKUP_AGE_HOURS hours (OK)"
    fi

    log_info "Backup verification completed"
    return 0
}

show_status() {
    log_info "WAL-G Status Report"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "PostgreSQL WAL Archiving Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Check PostgreSQL status
    if docker-compose exec -T postgres pg_isready -U sahool >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} PostgreSQL: Running"
    else
        echo -e "${RED}✗${NC} PostgreSQL: Not running"
    fi

    # Check archiving status
    echo ""
    echo "Archive Statistics:"
    docker-compose exec -T postgres psql -U sahool -c "
        SELECT
            'Archived:' as metric,
            archived_count as value
        FROM pg_stat_archiver
        UNION ALL
        SELECT
            'Failed:' as metric,
            COALESCE(failed_count, 0) as value
        FROM pg_stat_archiver
        UNION ALL
        SELECT
            'Last Archive:' as metric,
            EXTRACT(EPOCH FROM (NOW() - last_archived_time))::INTEGER as value
        FROM pg_stat_archiver;
    " 2>/dev/null | tail -n +3

    # List backups
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Available Backups"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    docker-compose exec -T postgres wal-g backup-list 2>/dev/null || echo "Failed to list backups"

    # Storage usage
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Storage Usage"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "S3 Storage:"
    docker-compose exec -T postgres aws s3 ls s3://sahool-wal-archive/ \
        --endpoint-url "${AWS_ENDPOINT:-http://minio:9000}" \
        --recursive --summarize --human-readable 2>/dev/null | tail -2 || echo "Failed to get S3 storage info"

    echo ""
    echo "Local WAL Archive:"
    docker-compose exec -T postgres du -sh /var/lib/postgresql/wal_archive 2>/dev/null || echo "N/A"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

show_help() {
    cat <<EOF
SAHOOL WAL-G Maintenance Script

Usage: $0 [command]

Commands:
    backup      Create a new base backup
    cleanup     Remove old backups (keep last $RETAIN_BACKUPS)
    verify      Verify backup integrity and status
    status      Show detailed WAL-G status
    help        Show this help message

Examples:
    $0 backup          # Create a new backup
    $0 cleanup         # Clean up old backups
    $0 verify          # Verify backups
    $0 status          # Show status

Environment Variables:
    WALG_RETAIN_BACKUPS    Number of backups to retain (default: 7)
    BACKUP_EMAIL_TO        Email address for notifications

For more information, see: config/postgres/PITR_RECOVERY.md
EOF
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main Function
# ═══════════════════════════════════════════════════════════════════════════════

main() {
    local COMMAND="${1:-help}"

    case "$COMMAND" in
        backup)
            create_backup
            ;;
        cleanup)
            cleanup_old_backups
            ;;
        verify)
            verify_backups
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
