# Kong API Gateway Quick Start Guide

# دليل البدء السريع لبوابة Kong API

## Quick Setup (5 minutes) | الإعداد السريع (5 دقائق)

### 1. Setup Environment | إعداد البيئة

```bash
# Navigate to Kong directory
cd /home/user/sahool-unified-v15-idp/infrastructure/kong

# Run the automated setup script
./setup.sh
```

The setup script will:

- Check prerequisites
- Generate secure JWT secrets
- Create .env file
- Start all Kong services
- Apply configurations
- Verify setup

سيقوم سكريبت الإعداد بـ:

- فحص المتطلبات الأساسية
- توليد أسرار JWT آمنة
- إنشاء ملف .env
- بدء جميع خدمات Kong
- تطبيق التكوينات
- التحقق من الإعداد

### 2. Access Services | الوصول إلى الخدمات

Once setup is complete, you can access:

| Service    | URL                   | Purpose       |
| ---------- | --------------------- | ------------- |
| Kong Proxy | http://localhost:8000 | API Gateway   |
| Kong Admin | http://localhost:8001 | Admin API     |
| Konga UI   | http://localhost:1337 | Web Interface |
| Prometheus | http://localhost:9090 | Metrics       |
| Grafana    | http://localhost:3002 | Dashboards    |

### 3. Test the Setup | اختبار الإعداد

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"message": "SAHOOL Platform is healthy"}

# Check Kong status
curl http://localhost:8001/status

# List all services
curl http://localhost:8001/services
```

## Manual Setup | الإعداد اليدوي

### Step 1: Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and update these critical values:

```bash
STARTER_JWT_SECRET=your-random-secret-here
PROFESSIONAL_JWT_SECRET=your-random-secret-here
ENTERPRISE_JWT_SECRET=your-random-secret-here
KONG_PG_PASSWORD=your-database-password
```

Generate secrets:

```bash
openssl rand -base64 32
```

### Step 2: Start Services

```bash
docker-compose up -d
```

### Step 3: Wait for Kong

```bash
# Wait until Kong is ready (may take 30-60 seconds)
until curl -f http://localhost:8001/status > /dev/null 2>&1; do
    echo "Waiting for Kong..."
    sleep 5
done
echo "Kong is ready!"
```

### Step 4: Apply Configuration

Using deck (recommended):

```bash
# Install deck
brew install deck

# Sync configuration
deck sync -s kong.yml
deck sync -s kong-packages.yml
deck sync -s consumers.yml
```

Or using Kong Admin API:

```bash
curl -i -X POST http://localhost:8001/config \
  --form config=@kong.yml
```

## Testing Different Package Tiers | اختبار مستويات الباقات المختلفة

### Generate JWT Tokens | توليد رموز JWT

```bash
# For starter package
export STARTER_TOKEN=$(python3 -c "
import jwt
import time
token = jwt.encode(
    {'iss': 'starter-jwt-key', 'exp': int(time.time()) + 3600},
    '${STARTER_JWT_SECRET}',
    algorithm='HS256'
)
print(token)
")

# For professional package
export PROFESSIONAL_TOKEN=$(python3 -c "
import jwt
import time
token = jwt.encode(
    {'iss': 'professional-jwt-key', 'exp': int(time.time()) + 3600},
    '${PROFESSIONAL_JWT_SECRET}',
    algorithm='HS256'
)
print(token)
")

# For enterprise package
export ENTERPRISE_TOKEN=$(python3 -c "
import jwt
import time
token = jwt.encode(
    {'iss': 'enterprise-jwt-key', 'exp': int(time.time()) + 3600},
    '${ENTERPRISE_JWT_SECRET}',
    algorithm='HS256'
)
print(token)
")
```

### Test Starter Package Routes

```bash
# Test field core (should work)
curl -H "Authorization: Bearer $STARTER_TOKEN" \
  http://localhost:8000/api/v1/starter/fields

# Test weather service (should work)
curl -H "Authorization: Bearer $STARTER_TOKEN" \
  http://localhost:8000/api/v1/starter/weather

# Test satellite service (should fail - not in starter package)
curl -H "Authorization: Bearer $STARTER_TOKEN" \
  http://localhost:8000/api/v1/starter/satellite
# Expected: 403 Forbidden
```

### Test Professional Package Routes

```bash
# Test satellite service (should work)
curl -H "Authorization: Bearer $PROFESSIONAL_TOKEN" \
  http://localhost:8000/api/v1/professional/satellite

# Test NDVI engine (should work)
curl -H "Authorization: Bearer $PROFESSIONAL_TOKEN" \
  http://localhost:8000/api/v1/professional/ndvi

# Test AI advisor (should fail - not in professional package)
curl -H "Authorization: Bearer $PROFESSIONAL_TOKEN" \
  http://localhost:8000/api/v1/professional/ai-advisor
# Expected: 403 Forbidden
```

### Test Enterprise Package Routes

```bash
# Test AI advisor (should work)
curl -H "Authorization: Bearer $ENTERPRISE_TOKEN" \
  http://localhost:8000/api/v1/enterprise/ai-advisor

# Test IoT gateway (should work)
curl -H "Authorization: Bearer $ENTERPRISE_TOKEN" \
  http://localhost:8000/api/v1/enterprise/iot

# Test marketplace (should work)
curl -H "Authorization: Bearer $ENTERPRISE_TOKEN" \
  http://localhost:8000/api/v1/enterprise/marketplace
```

## Common Commands | الأوامر الشائعة

### Service Management

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart Kong
docker-compose restart kong

# View logs
docker-compose logs -f kong

# View all logs
docker-compose logs -f
```

### Configuration Management

```bash
# Validate configuration
deck validate -s kong.yml

# Diff configuration
deck diff -s kong.yml

# Apply configuration
deck sync -s kong.yml

# Backup configuration
deck dump -o kong-backup.yml
```

### Debugging

```bash
# Check Kong health
curl http://localhost:8001/status

# List all services
curl http://localhost:8001/services | jq

# List all routes
curl http://localhost:8001/routes | jq

# List all consumers
curl http://localhost:8001/consumers | jq

# List all plugins
curl http://localhost:8001/plugins | jq

# Check specific service
curl http://localhost:8001/services/field-core | jq

# Check service health
curl http://localhost:8001/services/field-core/health | jq
```

### Monitoring

```bash
# View Prometheus metrics
curl http://localhost:8001/metrics

# Query specific metric
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=kong_http_status'

# Check rate limiting
curl -I http://localhost:8000/api/v1/starter/fields
# Look for X-RateLimit-* headers
```

## Troubleshooting | استكشاف الأخطاء

### Kong won't start

```bash
# Check logs
docker-compose logs kong

# Check database connection
docker-compose exec kong kong config db_import /dev/null

# Restart database and Kong
docker-compose restart kong-database kong
```

### Configuration not applying

```bash
# Validate configuration
deck validate -s kong.yml

# Check for syntax errors
cat kong.yml | yq eval

# Force sync
deck sync -s kong.yml --skip-consumers
```

### Rate limiting not working

```bash
# Check plugin configuration
curl http://localhost:8001/plugins | jq '.data[] | select(.name == "rate-limiting")'

# Test with multiple requests
for i in {1..150}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -H "Authorization: Bearer $STARTER_TOKEN" \
    http://localhost:8000/api/v1/starter/fields
done
# Should see 429 after 100 requests
```

### JWT authentication failing

```bash
# Verify JWT secret is correct
echo $STARTER_JWT_SECRET

# Check consumer exists
curl http://localhost:8001/consumers/starter-user-demo

# Check JWT credentials
curl http://localhost:8001/consumers/starter-user-demo/jwt

# Decode JWT token to verify
echo $STARTER_TOKEN | cut -d. -f2 | base64 -d | jq
```

## Performance Tuning | ضبط الأداء

### Optimize for High Traffic

Edit `docker-compose.yml`:

```yaml
kong:
  environment:
    KONG_NGINX_WORKER_PROCESSES: 8
    KONG_NGINX_WORKER_CONNECTIONS: 10000
  deploy:
    resources:
      limits:
        cpus: "4.0"
        memory: 4G
```

### Enable Caching

```bash
curl -X POST http://localhost:8001/plugins \
  --data "name=proxy-cache" \
  --data "config.strategy=memory" \
  --data "config.cache_ttl=300"
```

### Database Connection Pooling

Edit `docker-compose.yml`:

```yaml
kong:
  environment:
    KONG_PG_MAX_CONCURRENT_QUERIES: 100
    KONG_PG_SEMAPHORE_TIMEOUT: 60000
```

## Security Hardening | تعزيز الأمان

### Production Recommendations

1. **Enable HTTPS Only**

```yaml
routes:
  - protocols:
      - https
```

2. **Restrict Admin API Access**

```yaml
plugins:
  - name: ip-restriction
    route: admin
    config:
      allow:
        - 10.0.0.0/8
```

3. **Enable Rate Limiting Globally**

```yaml
plugins:
  - name: rate-limiting
    config:
      minute: 1000
      policy: cluster
```

4. **Rotate JWT Secrets Regularly**

```bash
# Generate new secret
NEW_SECRET=$(openssl rand -base64 32)

# Update .env
sed -i "s/STARTER_JWT_SECRET=.*/STARTER_JWT_SECRET=$NEW_SECRET/" .env

# Restart Kong
docker-compose restart kong
```

## Next Steps | الخطوات التالية

1. Configure Grafana dashboards for monitoring
2. Set up alerts in Prometheus
3. Integrate with your microservices
4. Configure SSL/TLS certificates
5. Set up log aggregation
6. Configure backup strategy

For detailed documentation, see [README.md](README.md)

---

**Quick Reference:**

- Main Config: `kong.yml`
- Package Routes: `kong-packages.yml`
- Consumers: `consumers.yml`
- Environment: `.env`
- Setup Script: `./setup.sh`

**Support:**

- Documentation: https://docs.sahool.platform
- Email: support@sahool.platform
