#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform Upgrade Script
# نظام الترقيات والتطوير وفقاً لقواعد حاكمة
# ═══════════════════════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VERSION_FILE="$PROJECT_ROOT/VERSION"
MIGRATIONS_DIR="$SCRIPT_DIR/migrations"
BACKUP_DIR="$PROJECT_ROOT/backups"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ═══════════════════════════════════════════════════════════════════════════════
# Version Management - إدارة الإصدارات
# ═══════════════════════════════════════════════════════════════════════════════

get_current_version() {
    if [ -f "$VERSION_FILE" ]; then
        cat "$VERSION_FILE"
    else
        echo "15.0.0"
    fi
}

set_version() {
    echo "$1" > "$VERSION_FILE"
    log_success "Version updated to $1"
}

compare_versions() {
    # Returns 0 if v1 == v2, 1 if v1 > v2, 2 if v1 < v2
    if [ "$1" = "$2" ]; then return 0; fi
    local IFS=.
    local i ver1=($1) ver2=($2)
    for ((i=0; i<${#ver1[@]}; i++)); do
        if ((10#${ver1[i]:-0} > 10#${ver2[i]:-0})); then return 1; fi
        if ((10#${ver1[i]:-0} < 10#${ver2[i]:-0})); then return 2; fi
    done
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════════
# Pre-Upgrade Checks - فحوصات ما قبل الترقية
# ═══════════════════════════════════════════════════════════════════════════════

pre_upgrade_checks() {
    log_info "Running pre-upgrade checks..."

    # Check Docker is running
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running"
        exit 1
    fi

    # Check disk space (minimum 10GB)
    available_space=$(df -BG "$PROJECT_ROOT" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$available_space" -lt 10 ]; then
        log_error "Insufficient disk space. Need at least 10GB, have ${available_space}GB"
        exit 1
    fi

    # Check required files
    if [ ! -f "$PROJECT_ROOT/docker-compose.yml" ]; then
        log_error "docker-compose.yml not found"
        exit 1
    fi

    log_success "Pre-upgrade checks passed"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Backup - النسخ الاحتياطي
# ═══════════════════════════════════════════════════════════════════════════════

create_backup() {
    local version=$(get_current_version)
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_name="sahool_backup_${version}_${timestamp}"
    local backup_path="$BACKUP_DIR/$backup_name"

    log_info "Creating backup at $backup_path..."
    mkdir -p "$backup_path"

    # Backup database
    if docker ps | grep -q sahool-postgres; then
        log_info "Backing up PostgreSQL database..."
        docker exec sahool-postgres pg_dump -U ${POSTGRES_USER:-sahool} ${POSTGRES_DB:-sahool} \
            > "$backup_path/database.sql" 2>/dev/null || log_warn "Database backup skipped"
    fi

    # Backup Redis
    if docker ps | grep -q sahool-redis; then
        log_info "Backing up Redis..."
        docker exec sahool-redis redis-cli -a "${REDIS_PASSWORD:-}" BGSAVE 2>/dev/null || true
        sleep 2
    fi

    # Backup configuration files
    cp -r "$PROJECT_ROOT/infra" "$backup_path/" 2>/dev/null || true
    cp "$PROJECT_ROOT/docker-compose.yml" "$backup_path/" 2>/dev/null || true
    cp "$PROJECT_ROOT/.env" "$backup_path/" 2>/dev/null || true

    # Compress backup
    tar -czf "$BACKUP_DIR/${backup_name}.tar.gz" -C "$BACKUP_DIR" "$backup_name"
    rm -rf "$backup_path"

    log_success "Backup created: ${backup_name}.tar.gz"
    echo "$BACKUP_DIR/${backup_name}.tar.gz"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Run Migrations - تشغيل الترحيلات
# ═══════════════════════════════════════════════════════════════════════════════

run_migrations() {
    local from_version="$1"
    local to_version="$2"

    log_info "Running migrations from $from_version to $to_version..."

    # Find and run applicable migrations
    for migration in $(ls -1 "$MIGRATIONS_DIR"/*.sh 2>/dev/null | sort -V); do
        local migration_version=$(basename "$migration" | grep -oP '^\d+\.\d+\.\d+' || echo "0.0.0")

        compare_versions "$migration_version" "$from_version"
        local cmp_from=$?

        compare_versions "$migration_version" "$to_version"
        local cmp_to=$?

        # Run migration if: from_version < migration_version <= to_version
        if [ $cmp_from -eq 1 ] && ([ $cmp_to -eq 0 ] || [ $cmp_to -eq 2 ]); then
            log_info "Running migration: $(basename $migration)"
            bash "$migration" || {
                log_error "Migration failed: $(basename $migration)"
                exit 1
            }
        fi
    done

    log_success "Migrations completed"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Docker Operations - عمليات دوكر
# ═══════════════════════════════════════════════════════════════════════════════

pull_images() {
    log_info "Pulling latest images..."
    cd "$PROJECT_ROOT"
    docker compose pull 2>/dev/null || docker-compose pull
    log_success "Images pulled"
}

rebuild_services() {
    log_info "Rebuilding services..."
    cd "$PROJECT_ROOT"
    docker compose build --no-cache 2>/dev/null || docker-compose build --no-cache
    log_success "Services rebuilt"
}

restart_services() {
    log_info "Restarting services..."
    cd "$PROJECT_ROOT"
    docker compose down 2>/dev/null || docker-compose down
    docker compose up -d 2>/dev/null || docker-compose up -d
    log_success "Services restarted"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Health Checks - فحوصات الصحة
# ═══════════════════════════════════════════════════════════════════════════════

wait_for_services() {
    local max_attempts=30
    local attempt=1

    log_info "Waiting for services to be healthy..."

    while [ $attempt -le $max_attempts ]; do
        if docker compose ps 2>/dev/null | grep -q "unhealthy"; then
            log_warn "Some services still unhealthy (attempt $attempt/$max_attempts)"
            sleep 10
            ((attempt++))
        else
            log_success "All services healthy"
            return 0
        fi
    done

    log_error "Services did not become healthy in time"
    return 1
}

run_health_checks() {
    log_info "Running health checks..."

    # Check Kong
    if curl -s http://localhost:8000/healthz > /dev/null 2>&1; then
        log_success "Kong API Gateway: OK"
    else
        log_warn "Kong API Gateway: Not responding"
    fi

    # Check PostgreSQL
    if docker exec sahool-postgres pg_isready -U ${POSTGRES_USER:-sahool} > /dev/null 2>&1; then
        log_success "PostgreSQL: OK"
    else
        log_warn "PostgreSQL: Not responding"
    fi

    # Check NATS
    if curl -s http://localhost:8222/healthz > /dev/null 2>&1; then
        log_success "NATS: OK"
    else
        log_warn "NATS: Not responding"
    fi

    # Check Redis
    if docker exec sahool-redis redis-cli -a "${REDIS_PASSWORD:-}" ping > /dev/null 2>&1; then
        log_success "Redis: OK"
    else
        log_warn "Redis: Not responding"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# Rollback - التراجع
# ═══════════════════════════════════════════════════════════════════════════════

rollback() {
    local backup_file="$1"

    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        exit 1
    fi

    log_warn "Rolling back to backup: $backup_file"

    # Stop services
    cd "$PROJECT_ROOT"
    docker compose down 2>/dev/null || docker-compose down

    # Extract backup
    local backup_name=$(basename "$backup_file" .tar.gz)
    tar -xzf "$backup_file" -C "$BACKUP_DIR"

    # Restore database
    if [ -f "$BACKUP_DIR/$backup_name/database.sql" ]; then
        log_info "Restoring database..."
        docker compose up -d postgres
        sleep 10
        docker exec -i sahool-postgres psql -U ${POSTGRES_USER:-sahool} ${POSTGRES_DB:-sahool} \
            < "$BACKUP_DIR/$backup_name/database.sql"
    fi

    # Restore configuration
    cp "$BACKUP_DIR/$backup_name/docker-compose.yml" "$PROJECT_ROOT/" 2>/dev/null || true
    cp -r "$BACKUP_DIR/$backup_name/infra/"* "$PROJECT_ROOT/infra/" 2>/dev/null || true

    # Restart services
    restart_services

    # Cleanup
    rm -rf "$BACKUP_DIR/$backup_name"

    log_success "Rollback completed"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Main Upgrade Function - وظيفة الترقية الرئيسية
# ═══════════════════════════════════════════════════════════════════════════════

upgrade() {
    local target_version="${1:-}"
    local current_version=$(get_current_version)

    if [ -z "$target_version" ]; then
        # Get latest version from git tags or use incremented version
        target_version=$(git describe --tags --abbrev=0 2>/dev/null || echo "15.6.0")
    fi

    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo "  SAHOOL Platform Upgrade"
    echo "  ترقية منصة سهول"
    echo "═══════════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "  Current Version: $current_version"
    echo "  Target Version:  $target_version"
    echo ""

    compare_versions "$target_version" "$current_version"
    local cmp=$?

    if [ $cmp -eq 0 ]; then
        log_info "Already at version $target_version"
        exit 0
    elif [ $cmp -eq 2 ]; then
        log_error "Cannot downgrade from $current_version to $target_version"
        log_info "Use 'rollback' command for downgrades"
        exit 1
    fi

    # Confirm upgrade
    read -p "Proceed with upgrade? (y/N) " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_info "Upgrade cancelled"
        exit 0
    fi

    # Run upgrade steps
    pre_upgrade_checks

    log_info "Creating backup before upgrade..."
    backup_file=$(create_backup)

    # Pull latest code (if git repo)
    if [ -d "$PROJECT_ROOT/.git" ]; then
        log_info "Pulling latest code..."
        git -C "$PROJECT_ROOT" pull origin $(git -C "$PROJECT_ROOT" branch --show-current) 2>/dev/null || true
    fi

    # Run migrations
    run_migrations "$current_version" "$target_version"

    # Rebuild and restart
    rebuild_services
    restart_services

    # Wait for services
    if ! wait_for_services; then
        log_error "Upgrade failed - services not healthy"
        log_info "Rolling back..."
        rollback "$backup_file"
        exit 1
    fi

    # Update version
    set_version "$target_version"

    # Run health checks
    run_health_checks

    echo ""
    log_success "═══════════════════════════════════════════════════════════════════════════════"
    log_success "  Upgrade to $target_version completed successfully!"
    log_success "  تمت الترقية إلى الإصدار $target_version بنجاح!"
    log_success "═══════════════════════════════════════════════════════════════════════════════"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# Command Line Interface - واجهة سطر الأوامر
# ═══════════════════════════════════════════════════════════════════════════════

show_help() {
    echo "SAHOOL Platform Upgrade System"
    echo "نظام ترقية منصة سهول"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  upgrade [version]   Upgrade to specified version (or latest)"
    echo "  rollback <backup>   Rollback to a backup file"
    echo "  backup              Create a backup"
    echo "  version             Show current version"
    echo "  health              Run health checks"
    echo "  help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 upgrade 15.7.0"
    echo "  $0 rollback /path/to/backup.tar.gz"
    echo "  $0 backup"
}

case "${1:-help}" in
    upgrade)
        upgrade "${2:-}"
        ;;
    rollback)
        rollback "${2:-}"
        ;;
    backup)
        create_backup
        ;;
    version)
        echo "SAHOOL Platform v$(get_current_version)"
        ;;
    health)
        run_health_checks
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
