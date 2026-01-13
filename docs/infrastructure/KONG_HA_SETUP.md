# Kong HA Setup Guide

## دليل إعداد Kong عالي التوفر

**Version:** 15.5.0
**Last Updated:** 2024-12-22

---

## Overview | نظرة عامة

This document describes the High Availability (HA) setup for Kong Gateway in the SAHOOL platform. The setup provides:

- **3-node Kong cluster** for redundancy
- **Nginx load balancer** for traffic distribution
- **Automatic failover** when nodes fail
- **Health checks** for all services

---

## Architecture | البنية

```
                    ┌─────────────────┐
                    │   Nginx LB      │
                    │   Port: 8000    │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
    │ Kong Primary│   │Kong Secondary│  │Kong Tertiary│
    │   :8000     │   │    :8000     │  │    :8000    │
    └─────────────┘   └──────────────┘  └─────────────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Backend        │
                    │  Services       │
                    └─────────────────┘
```

---

## Quick Start | البدء السريع

### Prerequisites | المتطلبات

- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum

### Deployment | النشر

```bash
# Navigate to Kong HA directory
cd infra/kong-ha

# Start the cluster
docker-compose -f docker-compose.kong-ha.yml up -d

# Verify health
curl http://localhost:8000/health
# Expected: OK

# Check cluster status
docker-compose -f docker-compose.kong-ha.yml ps
```

---

## Configuration Files | ملفات الإعداد

### 1. docker-compose.kong-ha.yml

Main orchestration file defining:

- 3 Kong nodes (primary, secondary, tertiary)
- Nginx load balancer
- Network configuration
- Resource limits

### 2. nginx-kong-ha.conf

Load balancer configuration:

- Upstream cluster definition
- Health check endpoints
- Timeout settings
- Retry logic

### 3. kong/declarative/kong.yml

Service definitions:

- All SAHOOL API services
- Rate limiting plugins
- CORS configuration
- Request transformation

---

## Services Configured | الخدمات المُعدة

| Service              | Upstream                  | Rate Limit | Path                  |
| -------------------- | ------------------------- | ---------- | --------------------- |
| field-ops            | field-service:8080        | 1000/min   | /api/v1/fields        |
| satellite-service    | satellite-service:8090    | 500/min    | /api/v1/satellite     |
| virtual-sensors      | virtual-sensors:8085      | 2000/min   | /api/v1/sensors       |
| yield-prediction     | yield-prediction:8091     | 300/min    | /api/v1/yield         |
| lai-estimation       | lai-estimation:8093       | 500/min    | /api/v1/lai           |
| irrigation-smart     | irrigation-smart:8086     | 1000/min   | /api/v1/irrigation    |
| notification-service | notification-service:8083 | 5000/min   | /api/v1/notifications |
| crop-growth-timing   | crop-growth-timing:8098   | 500/min    | /api/v1/crop-timing   |
| weather-service      | weather-advanced:8092     | 1000/min   | /api/v1/weather       |

---

## Failover Testing | اختبار الـFailover

```bash
# Test normal operation
curl http://localhost:8000/api/v1/fields
# Should return 200 OK

# Stop primary node
docker stop sahool-kong-primary

# Test again - should still work via secondary/tertiary
curl http://localhost:8000/api/v1/fields
# Should still return 200 OK

# Restart primary
docker start sahool-kong-primary

# Verify cluster is healthy
docker-compose -f docker-compose.kong-ha.yml ps
```

---

## Monitoring | المراقبة

### Health Endpoints

```bash
# Load balancer health
curl http://localhost:8000/health

# Kong status (admin API)
curl http://localhost:8001/status

# Individual node health
docker exec sahool-kong-primary kong health
docker exec sahool-kong-secondary kong health
docker exec sahool-kong-tertiary kong health
```

### Logs

```bash
# All logs
docker-compose -f docker-compose.kong-ha.yml logs -f

# Specific node
docker logs -f sahool-kong-primary

# Nginx load balancer
docker logs -f sahool-kong-lb
```

---

## Troubleshooting | استكشاف الأخطاء

### Common Issues

| Issue                   | Cause                | Solution                     |
| ----------------------- | -------------------- | ---------------------------- |
| 502 Bad Gateway         | All Kong nodes down  | Check Kong container health  |
| 503 Service Unavailable | Backend service down | Check backend service status |
| Connection refused      | Nginx not running    | Restart nginx container      |
| Slow responses          | Network issues       | Check docker network         |

### Recovery Steps

```bash
# Full restart
docker-compose -f docker-compose.kong-ha.yml down
docker-compose -f docker-compose.kong-ha.yml up -d

# Reload Kong configuration
docker exec sahool-kong-primary kong reload
docker exec sahool-kong-secondary kong reload
docker exec sahool-kong-tertiary kong reload
```

---

## Security Considerations | اعتبارات الأمان

1. **Admin API**: Only accessible from internal networks (10.x, 172.x, 192.168.x)
2. **Rate Limiting**: Applied per-service to prevent abuse
3. **CORS**: Configured for API services
4. **TLS**: Add TLS termination at Nginx for production

### Adding TLS

```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    # ... rest of config
}
```

---

## Scaling | التوسع

To add more Kong nodes:

1. Add new service in docker-compose.yml
2. Add to nginx upstream
3. Restart cluster

```yaml
# In docker-compose.yml
kong-fourth:
  image: kong:3.4.0-ubuntu
  # ... same config as other nodes
```

```nginx
# In nginx-kong-ha.conf
upstream kong_cluster {
    server kong-primary:8000;
    server kong-secondary:8000;
    server kong-tertiary:8000;
    server kong-fourth:8000;  # New node
}
```

---

**Related Documents:**

- [Engineering Recovery Plan](../engineering/ENGINEERING_RECOVERY_PLAN.md)
- [Service Activation Map](../architecture/SERVICE_ACTIVATION_MAP.md)
