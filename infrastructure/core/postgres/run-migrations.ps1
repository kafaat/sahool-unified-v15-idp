# SAHOOL Platform - Database Migration Runner (PowerShell)
# Script to apply all pending migrations to PostgreSQL database

Write-Host "===================================================================" -ForegroundColor Blue
Write-Host "  SAHOOL Database Migration Runner" -ForegroundColor Blue
Write-Host "===================================================================" -ForegroundColor Blue
Write-Host ""

# Database connection details
$DB_HOST = if ($env:POSTGRES_HOST) { $env:POSTGRES_HOST } else { "postgres" }
$DB_PORT = if ($env:POSTGRES_PORT) { $env:POSTGRES_PORT } else { "5432" }
$DB_NAME = if ($env:POSTGRES_DB) { $env:POSTGRES_DB } else { "sahool" }
$DB_USER = if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { "sahool" }

# Migration directory
$MIGRATION_DIR = ".\infrastructure\core\postgres\migrations"

# Check if PostgreSQL container is running
Write-Host "[INFO] Checking database connection..." -ForegroundColor Yellow
$pgCheck = docker exec sahool-postgres pg_isready -U $DB_USER -d $DB_NAME 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Database is accessible" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Cannot connect to database" -ForegroundColor Red
    Write-Host "  Make sure PostgreSQL container is running: docker-compose up -d postgres" -ForegroundColor Yellow
    exit 1
}

# Create migrations tracking table if it doesn't exist
Write-Host "[INFO] Creating migrations tracking table..." -ForegroundColor Yellow
$createTableSQL = @"
CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(255) UNIQUE NOT NULL,
    filename VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    checksum VARCHAR(64)
);
"@
$createTableSQL | docker exec -i sahool-postgres psql -U $DB_USER -d $DB_NAME
Write-Host "[OK] Migrations tracking table ready" -ForegroundColor Green

# Get list of applied migrations
Write-Host "[INFO] Checking applied migrations..." -ForegroundColor Yellow
$appliedMigrations = docker exec sahool-postgres psql -U $DB_USER -d $DB_NAME -t -c "SELECT filename FROM schema_migrations ORDER BY applied_at;" 2>$null
if ($appliedMigrations) {
    $appliedCount = ($appliedMigrations | Where-Object { $_.Trim() -ne "" }).Count
    Write-Host "[OK] Found $appliedCount applied migrations" -ForegroundColor Green
} else {
    Write-Host "[OK] No migrations applied yet" -ForegroundColor Green
}

# Apply pending migrations
Write-Host "[INFO] Applying pending migrations..." -ForegroundColor Yellow
$migrationCount = 0

# Get all SQL files and sort them
$migrationFiles = Get-ChildItem -Path $MIGRATION_DIR -Filter "*.sql" | Sort-Object Name

foreach ($migrationFile in $migrationFiles) {
    $filename = $migrationFile.Name
    
    # Check if migration already applied
    $isApplied = $appliedMigrations -match [regex]::Escape($filename)
    if ($isApplied) {
        Write-Host "  [SKIP] $filename (already applied)" -ForegroundColor Blue
        continue
    }
    
    # Apply migration
    Write-Host "  [RUN] Applying $filename..." -ForegroundColor Yellow
    
    # Read file content and execute
    $migrationContent = Get-Content -Path $migrationFile.FullName -Raw
    $result = $migrationContent | docker exec -i sahool-postgres psql -U $DB_USER -d $DB_NAME 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        # Record migration - escape single quotes in filename
        $escapedFilename = $filename -replace "'", "''"
        $version = if ($filename -match '^(\d+|V\d+)') { $matches[1] } else { 'manual' }
        $recordSQL = "INSERT INTO schema_migrations (filename, version) VALUES ('$escapedFilename', '$version');"
        $recordSQL | docker exec -i sahool-postgres psql -U $DB_USER -d $DB_NAME | Out-Null
        
        Write-Host "  [OK] Applied $filename" -ForegroundColor Green
        $migrationCount++
    } else {
        Write-Host "  [ERROR] Failed to apply $filename" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
        exit 1
    }
}

# Summary
Write-Host ""
Write-Host "===================================================================" -ForegroundColor Blue
if ($migrationCount -eq 0) {
    Write-Host "[OK] All migrations are up to date!" -ForegroundColor Green
} else {
    Write-Host "[OK] Successfully applied $migrationCount migration(s)" -ForegroundColor Green
}
Write-Host "===================================================================" -ForegroundColor Blue

# Show current schema version
Write-Host ""
Write-Host "Current schema migrations:" -ForegroundColor Yellow
docker exec sahool-postgres psql -U $DB_USER -d $DB_NAME -c "SELECT id, filename, version, applied_at FROM schema_migrations ORDER BY applied_at DESC LIMIT 10;"

Write-Host ""
Write-Host "[OK] Migration complete!" -ForegroundColor Green
