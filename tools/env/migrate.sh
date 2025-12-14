#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Database Migration Runner
# Idempotent migrations for all services
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load environment
if [[ -f "$PROJECT_ROOT/.env" ]]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# ─────────────────────────────────────────────────────────────────────────────
# Colors
# ─────────────────────────────────────────────────────────────────────────────

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-sahool}"
DB_USER="${POSTGRES_USER:-sahool}"
DB_PASSWORD="${POSTGRES_PASSWORD:-sahool}"

PGPASSWORD="$DB_PASSWORD"
export PGPASSWORD

# ─────────────────────────────────────────────────────────────────────────────
# Functions
# ─────────────────────────────────────────────────────────────────────────────

wait_for_postgres() {
    log_info "Waiting for PostgreSQL..."

    local max_attempts=30
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; then
            log_success "PostgreSQL is ready"
            return 0
        fi

        echo -n "."
        sleep 1
        ((attempt++))
    done

    log_error "PostgreSQL not available after $max_attempts seconds"
    return 1
}

run_sql() {
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "$1"
}

run_sql_file() {
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$1"
}

create_migrations_table() {
    log_info "Ensuring migrations table exists..."

    run_sql "
        CREATE TABLE IF NOT EXISTS _migrations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    " > /dev/null 2>&1

    log_success "Migrations table ready"
}

is_migration_applied() {
    local name="$1"
    local result

    result=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc \
        "SELECT COUNT(*) FROM _migrations WHERE name = '$name';" 2>/dev/null)

    [[ "$result" == "1" ]]
}

record_migration() {
    local name="$1"
    run_sql "INSERT INTO _migrations (name) VALUES ('$name');" > /dev/null 2>&1
}

# ─────────────────────────────────────────────────────────────────────────────
# Migrations
# ─────────────────────────────────────────────────────────────────────────────

migrate_001_initial_schema() {
    local name="001_initial_schema"

    if is_migration_applied "$name"; then
        log_info "Migration $name already applied, skipping"
        return 0
    fi

    log_info "Applying migration: $name"

    run_sql "
        -- Extensions
        CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";
        CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";

        -- Tenants
        CREATE TABLE IF NOT EXISTS tenants (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            name VARCHAR(255) NOT NULL,
            slug VARCHAR(64) NOT NULL UNIQUE,
            settings JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Users
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            tenant_id UUID NOT NULL REFERENCES tenants(id),
            email VARCHAR(255) NOT NULL,
            password_hash VARCHAR(255),
            name VARCHAR(255) NOT NULL,
            roles TEXT[] DEFAULT '{}',
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(tenant_id, email)
        );

        CREATE INDEX IF NOT EXISTS idx_users_tenant ON users(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    " > /dev/null

    record_migration "$name"
    log_success "Migration $name applied"
}

migrate_002_field_ops() {
    local name="002_field_ops"

    if is_migration_applied "$name"; then
        log_info "Migration $name already applied, skipping"
        return 0
    fi

    log_info "Applying migration: $name"

    run_sql "
        -- Fields
        CREATE TABLE IF NOT EXISTS fields (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            tenant_id UUID NOT NULL,
            name VARCHAR(255) NOT NULL,
            area_hectares DECIMAL(10,2),
            crop_type VARCHAR(64),
            geometry JSONB,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_fields_tenant ON fields(tenant_id);

        -- Tasks
        CREATE TABLE IF NOT EXISTS tasks (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            tenant_id UUID NOT NULL,
            field_id UUID REFERENCES fields(id),
            title VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(32) DEFAULT 'pending',
            priority VARCHAR(16) DEFAULT 'medium',
            assigned_to UUID,
            due_date DATE,
            completed_at TIMESTAMP WITH TIME ZONE,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_tasks_tenant ON tasks(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        CREATE INDEX IF NOT EXISTS idx_tasks_field ON tasks(field_id);
        CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to);
    " > /dev/null

    record_migration "$name"
    log_success "Migration $name applied"
}

migrate_003_chat() {
    local name="003_chat"

    if is_migration_applied "$name"; then
        log_info "Migration $name already applied, skipping"
        return 0
    fi

    log_info "Applying migration: $name"

    run_sql "
        -- Chat Threads
        CREATE TABLE IF NOT EXISTS chat_threads (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            tenant_id VARCHAR(64) NOT NULL,
            scope_type VARCHAR(16) NOT NULL,
            scope_id VARCHAR(128) NOT NULL,
            created_by VARCHAR(64) NOT NULL,
            title VARCHAR(255),
            is_archived BOOLEAN DEFAULT false,
            message_count INTEGER DEFAULT 0,
            last_message_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(tenant_id, scope_type, scope_id)
        );

        CREATE INDEX IF NOT EXISTS idx_chat_threads_tenant ON chat_threads(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_chat_threads_scope ON chat_threads(scope_type, scope_id);

        -- Chat Messages
        CREATE TABLE IF NOT EXISTS chat_messages (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            tenant_id VARCHAR(64) NOT NULL,
            thread_id UUID NOT NULL REFERENCES chat_threads(id),
            sender_id VARCHAR(64) NOT NULL,
            text TEXT,
            attachments JSONB,
            reply_to_id UUID,
            message_type VARCHAR(32) DEFAULT 'text',
            is_edited BOOLEAN DEFAULT false,
            edited_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_chat_messages_thread ON chat_messages(thread_id);
        CREATE INDEX IF NOT EXISTS idx_chat_messages_sender ON chat_messages(sender_id);

        -- Chat Participants
        CREATE TABLE IF NOT EXISTS chat_participants (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            tenant_id VARCHAR(64) NOT NULL,
            thread_id UUID NOT NULL REFERENCES chat_threads(id),
            user_id VARCHAR(64) NOT NULL,
            last_read_at TIMESTAMP WITH TIME ZONE,
            last_read_message_id UUID,
            unread_count INTEGER DEFAULT 0,
            is_muted BOOLEAN DEFAULT false,
            joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(thread_id, user_id)
        );

        CREATE INDEX IF NOT EXISTS idx_chat_participants_user ON chat_participants(tenant_id, user_id);
    " > /dev/null

    record_migration "$name"
    log_success "Migration $name applied"
}

migrate_004_audit() {
    local name="004_audit"

    if is_migration_applied "$name"; then
        log_info "Migration $name already applied, skipping"
        return 0
    fi

    log_info "Applying migration: $name"

    run_sql "
        -- Security Audit Logs
        CREATE TABLE IF NOT EXISTS security_audit_logs (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            tenant_id VARCHAR(64) NOT NULL,
            user_id VARCHAR(64) NOT NULL,
            action VARCHAR(128) NOT NULL,
            category VARCHAR(32) NOT NULL,
            severity VARCHAR(16) DEFAULT 'info',
            resource_type VARCHAR(64),
            resource_id VARCHAR(128),
            correlation_id VARCHAR(64),
            session_id VARCHAR(64),
            ip_address VARCHAR(64),
            user_agent TEXT,
            request_method VARCHAR(16),
            request_path VARCHAR(512),
            details JSONB,
            old_value JSONB,
            new_value JSONB,
            success BOOLEAN DEFAULT true,
            error_code VARCHAR(64),
            error_message TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_audit_tenant_time ON security_audit_logs(tenant_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_audit_user_time ON security_audit_logs(user_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_audit_action ON security_audit_logs(action);
        CREATE INDEX IF NOT EXISTS idx_audit_category ON security_audit_logs(category);
        CREATE INDEX IF NOT EXISTS idx_audit_correlation ON security_audit_logs(correlation_id);
    " > /dev/null

    record_migration "$name"
    log_success "Migration $name applied"
}

migrate_005_iot() {
    local name="005_iot"

    if is_migration_applied "$name"; then
        log_info "Migration $name already applied, skipping"
        return 0
    fi

    log_info "Applying migration: $name"

    run_sql "
        -- IoT Devices
        CREATE TABLE IF NOT EXISTS iot_devices (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            tenant_id VARCHAR(64) NOT NULL,
            device_id VARCHAR(128) NOT NULL,
            device_type VARCHAR(64) NOT NULL,
            name VARCHAR(255) NOT NULL,
            field_id UUID,
            location JSONB,
            firmware_version VARCHAR(32),
            last_seen_at TIMESTAMP WITH TIME ZONE,
            status VARCHAR(32) DEFAULT 'offline',
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(tenant_id, device_id)
        );

        CREATE INDEX IF NOT EXISTS idx_iot_devices_tenant ON iot_devices(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_iot_devices_type ON iot_devices(device_type);
        CREATE INDEX IF NOT EXISTS idx_iot_devices_field ON iot_devices(field_id);

        -- Sensor Readings
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            tenant_id VARCHAR(64) NOT NULL,
            device_id VARCHAR(128) NOT NULL,
            sensor_type VARCHAR(64) NOT NULL,
            value DECIMAL(12,4) NOT NULL,
            unit VARCHAR(16),
            quality INTEGER DEFAULT 100,
            recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_sensor_readings_device ON sensor_readings(device_id, recorded_at);
        CREATE INDEX IF NOT EXISTS idx_sensor_readings_type ON sensor_readings(sensor_type);
    " > /dev/null

    record_migration "$name"
    log_success "Migration $name applied"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

main() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "           SAHOOL Database Migration Runner"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""

    wait_for_postgres
    create_migrations_table

    echo ""
    log_info "Running migrations..."
    echo ""

    migrate_001_initial_schema
    migrate_002_field_ops
    migrate_003_chat
    migrate_004_audit
    migrate_005_iot

    echo ""
    log_success "All migrations completed!"
    echo ""
}

main "$@"
