# SAHOOL Platform - Windows Commands Guide
# دليل أوامر ويندوز لمنصة سهول

---

## Prerequisites | المتطلبات الأساسية

### 1. Install Required Software | تثبيت البرامج المطلوبة

```powershell
# Install Chocolatey (Run as Administrator)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Docker Desktop
choco install docker-desktop -y

# Install Node.js LTS
choco install nodejs-lts -y

# Install Git
choco install git -y

# Install Python 3.11+
choco install python311 -y

# Install Flutter (for mobile development)
choco install flutter -y
```

### 2. Verify Installations | التحقق من التثبيت

```powershell
docker --version
node --version
npm --version
git --version
python --version
flutter --version
```

---

## Environment Setup | إعداد البيئة

### 1. Clone Repository | استنساخ المستودع

```powershell
git clone https://github.com/kafaat/sahool-unified-v15-idp.git
cd sahool-unified-v15-idp
```

### 2. Create Environment Files | إنشاء ملفات البيئة

```powershell
# Copy environment templates
copy .env.example .env
copy apps\admin\.env.example apps\admin\.env.local
copy apps\web\.env.example apps\web\.env.local
```

### 3. Install Dependencies | تثبيت المكتبات

```powershell
# Install Node.js dependencies
npm install

# Install Python dependencies (optional, for backend services)
pip install -r requirements.txt
```

---

## Docker Commands | أوامر Docker

### Start Infrastructure | تشغيل البنية التحتية

```powershell
# Start all infrastructure services (PostgreSQL, Redis, NATS, Kong)
docker-compose -f docker-compose.infra.yml up -d

# Or use the full stack
docker-compose up -d

# Check running containers
docker ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f postgres
docker-compose logs -f kong
docker-compose logs -f user-service
```

### Stop Infrastructure | إيقاف البنية التحتية

```powershell
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Stop specific service
docker-compose stop postgres
```

### Restart Services | إعادة تشغيل الخدمات

```powershell
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart user-service
docker-compose restart kong
```

---

## Development Commands | أوامر التطوير

### Admin Portal | لوحة الإدارة

```powershell
# Navigate to admin directory
cd apps\admin

# Install dependencies
npm install

# Start development server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Run linting
npm run lint
```

### Web Dashboard | لوحة الويب

```powershell
# Navigate to web directory
cd apps\web

# Install dependencies
npm install

# Start development server (http://localhost:3001)
npm run dev

# Build for production
npm run build

# Run tests
npm run test
```

### Mobile App (Flutter) | تطبيق الهاتف

```powershell
# Navigate to mobile app directory
cd apps\mobile\sahool_field_app

# Get dependencies
flutter pub get

# Run on connected device/emulator
flutter run

# Run on specific device
flutter run -d chrome    # Web
flutter run -d windows   # Windows desktop
flutter run -d <device_id>  # Specific device

# Build APK
flutter build apk

# Build for iOS (requires macOS)
flutter build ios

# Run tests
flutter test

# Analyze code
flutter analyze
```

---

## Database Commands | أوامر قاعدة البيانات

### PostgreSQL Access | الوصول لقاعدة البيانات

```powershell
# Connect to PostgreSQL via Docker
docker exec -it sahool-postgres psql -U sahool -d sahool

# Or using psql if installed locally
$env:PGPASSWORD="your_password"
psql -h localhost -p 5432 -U sahool -d sahool
```

### Database Migrations | ترحيل قاعدة البيانات

```powershell
# Run Prisma migrations (for Node.js services)
cd apps\services\user-service
npx prisma migrate deploy

# Generate Prisma client
npx prisma generate

# Open Prisma Studio (GUI)
npx prisma studio
```

### Database Backup | نسخ احتياطي

```powershell
# Backup database
docker exec sahool-postgres pg_dump -U sahool sahool > backup.sql

# Restore database
Get-Content backup.sql | docker exec -i sahool-postgres psql -U sahool sahool
```

---

## Testing Commands | أوامر الاختبار

### Run All Tests | تشغيل جميع الاختبارات

```powershell
# From project root
npm run test

# With coverage
npm run test:coverage
```

### Run Specific Tests | تشغيل اختبارات محددة

```powershell
# Admin tests
cd apps\admin
npm run test

# Web tests
cd apps\web
npm run test

# Mobile tests
cd apps\mobile\sahool_field_app
flutter test

# Python service tests
cd apps\services\weather-core
pytest -v
```

---

## API Testing | اختبار API

### Health Checks | فحص الصحة

```powershell
# Check Kong Gateway
Invoke-RestMethod -Uri "http://localhost:8000/healthz"

# Check user-service
Invoke-RestMethod -Uri "http://localhost:3001/healthz"

# Check all services health
$services = @("8000", "3001", "8090", "8091", "8092")
foreach ($port in $services) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$port/healthz" -TimeoutSec 5
        Write-Host "Port $port : OK" -ForegroundColor Green
    } catch {
        Write-Host "Port $port : FAILED" -ForegroundColor Red
    }
}
```

### Authentication Testing | اختبار المصادقة

```powershell
# Login
$loginBody = @{
    email = "admin@sahool.io"
    password = "admin123"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $loginBody

$token = $loginResponse.access_token
Write-Host "Token: $token"

# Register new user
$registerBody = @{
    email = "newuser@example.com"
    password = "SecurePass123!"
    firstName = "محمد"
    lastName = "أحمد"
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" `
    -Method POST `
    -ContentType "application/json" `
    -Body $registerBody

# Get current user (with token)
$headers = @{
    Authorization = "Bearer $token"
}
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" `
    -Method POST `
    -Headers $headers
```

---

## Troubleshooting | حل المشاكل

### Common Issues | المشاكل الشائعة

#### Port Already in Use | المنفذ مستخدم

```powershell
# Find process using port
netstat -ano | findstr :8000

# Kill process by PID
taskkill /PID <PID> /F

# Or use PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

#### Docker Issues | مشاكل Docker

```powershell
# Restart Docker service
Restart-Service docker

# Clean up Docker
docker system prune -a -f

# Remove all containers
docker rm -f $(docker ps -aq)

# Remove all images
docker rmi -f $(docker images -q)

# Reset Docker Desktop (if needed)
# Go to Docker Desktop > Troubleshoot > Reset to factory defaults
```

#### Permission Issues | مشاكل الصلاحيات

```powershell
# Run PowerShell as Administrator
Start-Process powershell -Verb runAs

# Set execution policy
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Node.js Issues | مشاكل Node.js

```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

---

## Quick Start Script | سكربت البدء السريع

Create `start-dev.ps1`:

```powershell
# start-dev.ps1 - SAHOOL Development Quick Start
# سكربت البدء السريع للتطوير

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SAHOOL Development Environment" -ForegroundColor Cyan
Write-Host "  بيئة تطوير سهول" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check Docker
Write-Host "`nChecking Docker..." -ForegroundColor Yellow
if (!(Get-Process "Docker Desktop" -ErrorAction SilentlyContinue)) {
    Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Start-Sleep -Seconds 30
}

# Start infrastructure
Write-Host "`nStarting infrastructure services..." -ForegroundColor Yellow
docker-compose -f docker-compose.infra.yml up -d

# Wait for services
Write-Host "`nWaiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check health
Write-Host "`nChecking service health..." -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "http://localhost:8000/healthz" -TimeoutSec 10
    Write-Host "Kong Gateway: OK" -ForegroundColor Green
} catch {
    Write-Host "Kong Gateway: Starting..." -ForegroundColor Yellow
}

# Print URLs
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Services URLs:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Kong Gateway:    http://localhost:8000" -ForegroundColor White
Write-Host "  Admin Portal:    http://localhost:3000" -ForegroundColor White
Write-Host "  Web Dashboard:   http://localhost:3001" -ForegroundColor White
Write-Host "  WebSocket:       ws://localhost:8081" -ForegroundColor White
Write-Host "  PostgreSQL:      localhost:5432" -ForegroundColor White
Write-Host "  Redis:           localhost:6379" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nTo start Admin Portal:" -ForegroundColor Green
Write-Host "  cd apps\admin && npm run dev" -ForegroundColor White

Write-Host "`nTo start Web Dashboard:" -ForegroundColor Green
Write-Host "  cd apps\web && npm run dev" -ForegroundColor White

Write-Host "`nTo start Mobile App:" -ForegroundColor Green
Write-Host "  cd apps\mobile\sahool_field_app && flutter run" -ForegroundColor White
```

Run with:
```powershell
.\start-dev.ps1
```

---

## Environment Variables | متغيرات البيئة

### Set Environment Variables | تعيين متغيرات البيئة

```powershell
# Temporary (current session only)
$env:NEXT_PUBLIC_API_URL = "http://localhost:8000"
$env:NEXT_PUBLIC_WS_URL = "ws://localhost:8081"
$env:JWT_SECRET = "your-secret-key-min-32-characters-long"

# Permanent (user level)
[Environment]::SetEnvironmentVariable("NEXT_PUBLIC_API_URL", "http://localhost:8000", "User")

# Permanent (system level - requires admin)
[Environment]::SetEnvironmentVariable("NEXT_PUBLIC_API_URL", "http://localhost:8000", "Machine")
```

---

## Useful Aliases | اختصارات مفيدة

Add to PowerShell profile (`$PROFILE`):

```powershell
# Open profile for editing
notepad $PROFILE

# Add these aliases:
function sahool-up { docker-compose up -d }
function sahool-down { docker-compose down }
function sahool-logs { docker-compose logs -f }
function sahool-admin { cd $env:USERPROFILE\sahool-unified-v15-idp\apps\admin; npm run dev }
function sahool-web { cd $env:USERPROFILE\sahool-unified-v15-idp\apps\web; npm run dev }
function sahool-mobile { cd $env:USERPROFILE\sahool-unified-v15-idp\apps\mobile\sahool_field_app; flutter run }
```

---

_Last Updated: January 2025_
