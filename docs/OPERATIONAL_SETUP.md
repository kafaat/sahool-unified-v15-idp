# SAHOOL Platform - Operational Setup Guide
# دليل التشغيل لمنصة سهول

## Quick Start (البداية السريعة)

### Prerequisites (المتطلبات)
- Docker 20.10+
- Docker Compose 2.0+
- Node.js 20+
- npm 10+
- Python 3.11+ (optional, for backend services)
- Flutter 3.16+ (optional, for mobile development)

### One-Command Setup (تنصيب بأمر واحد)

```bash
# Clone and setup
git clone https://github.com/kafaat/sahool-unified-v15-idp.git
cd sahool-unified-v15-idp

# Run bootstrap (generates secrets, installs deps, starts infra)
./scripts/bootstrap.sh --dev
```

---

## Environment Modes (أوضاع البيئة)

| Mode | Command | Usage |
|------|---------|-------|
| Development | `./scripts/bootstrap.sh --dev` | Local development with debug logging |
| CI/Testing | `./scripts/bootstrap.sh --ci` | Automated testing environment |
| Production | `./scripts/bootstrap.sh --prod` | Production build and deployment |

---

## Configuration Files (ملفات التكوين)

```
config/
├── base.env      # Base configuration (all variables)
├── local.env     # Local development overrides
├── ci.env        # CI/Testing overrides
└── prod.env      # Production overrides (secrets from CI/CD)
```

### Key Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `POSTGRES_PASSWORD` | Database password | ✅ |
| `REDIS_PASSWORD` | Redis password | ✅ |
| `JWT_SECRET_KEY` | JWT signing key (32+ chars) | ✅ |
| `APP_SECRET_KEY` | Application secret | ✅ |
| `ENVIRONMENT` | dev/ci/production | ✅ |

---

## Infrastructure Services (خدمات البنية التحتية)

### Start Infrastructure Only

```bash
# Start infrastructure services
docker-compose -f docker/docker-compose.infra.yml up -d

# Wait for all services to be healthy
docker-compose -f docker/docker-compose.infra.yml up -d --wait

# View service status
docker-compose -f docker/docker-compose.infra.yml ps
```

### Service Endpoints

| Service | Port | Health Check |
|---------|------|--------------|
| PostgreSQL | 5432 | `pg_isready` |
| Redis | 6379 | `redis-cli ping` |
| NATS | 4222/8222 | `/healthz` |
| MQTT | 1883/9001 | Sub test |
| Kong API | 8000 | `/health` |

---

## Database Migrations (ترحيل قاعدة البيانات)

Migrations run automatically when starting infrastructure:

```bash
# View migration status
docker-compose -f docker/docker-compose.infra.yml logs db-migrator

# Run migrations manually
docker-compose -f docker/docker-compose.infra.yml up db-migrator
```

### Migration Files Location
```
infra/postgres/migrations/
├── 001_init_extensions.sql    # PostGIS, UUID, etc.
├── 002_base_tables.sql        # Core tables
└── ...
```

---

## Frontend Development (تطوير الواجهة)

### Web Application

```bash
cd apps/web
npm install --legacy-peer-deps
npm run dev
# Available at http://localhost:3001
```

### Admin Dashboard

```bash
cd apps/admin
npm install --legacy-peer-deps
npm run dev
# Available at http://localhost:3002
```

### Run Tests

```bash
# Web tests
cd apps/web && npm test -- --run

# Admin tests
cd apps/admin && npm test -- --run

# Build for production
npm run build
```

---

## Mobile Development (تطوير التطبيق)

### Setup

```bash
cd apps/mobile/sahool_field_app
flutter pub get
```

### Configure Environment

```bash
# Copy dev configuration
cp config/dev.json.example config/dev.json

# Edit API endpoints
nano config/dev.json
```

### Run

```bash
# Android
flutter run -d android

# iOS
flutter run -d ios

# Web
flutter run -d chrome
```

---

## Troubleshooting (استكشاف الأخطاء)

### Docker Issues

```bash
# Reset all containers and volumes
docker-compose down -v
docker system prune -f

# Restart from scratch
./scripts/bootstrap.sh --dev
```

### Database Connection

```bash
# Check PostgreSQL status
docker-compose -f docker/docker-compose.infra.yml exec postgres pg_isready

# Connect to database
docker-compose -f docker/docker-compose.infra.yml exec postgres psql -U sahool
```

### Port Conflicts

```bash
# Check what's using a port
lsof -i :5432
lsof -i :3000

# Kill process
kill -9 <PID>
```

---

## CI/CD Pipeline

The CI pipeline runs the same commands as local development:

1. **Lint** - Code quality checks
2. **Test** - Unit and integration tests
3. **Build** - Docker images and frontend bundles
4. **Security** - Vulnerability scanning
5. **Deploy** - Staging/Production (on main branch)

### Running CI Locally

```bash
# Run the same steps as CI
./scripts/bootstrap.sh --ci
```

---

## Production Deployment (النشر للإنتاج)

### Build Production Images

```bash
# Build all services
./scripts/bootstrap.sh --prod

# Or build specific service
docker build -t sahool/field-core:latest ./archive/kernel-legacy/kernel/services/field_core
```

### Kubernetes Deployment

```bash
# Apply Helm chart
helm upgrade --install sahool ./helm/sahool \
  --namespace sahool \
  --values helm/sahool/values-prod.yaml
```

---

## Support (الدعم)

- **Documentation**: `/docs`
- **Issues**: GitHub Issues
- **Email**: support@sahool.app
