# Redis Security Hardening - Deployment Checklist
# قائمة التحقق من نشر تعزيز أمان Redis

**Platform:** SAHOOL Unified Agricultural Platform v15-IDP
**Version:** 1.0.0
**Date:** 2026-01-06

---

## Pre-Deployment Checklist

### 1. Environment Preparation

- [ ] **Backup Current Redis Data**
  ```bash
  docker exec sahool-redis redis-cli -a $REDIS_PASSWORD SAVE
  docker cp sahool-redis:/data/sahool-dump.rdb ./backup/redis-$(date +%Y%m%d).rdb
  docker cp sahool-redis:/data/sahool-appendonly.aof ./backup/redis-aof-$(date +%Y%m%d).aof
  ```

- [ ] **Verify Environment Variables**
  ```bash
  # Check .env file has all required variables
  grep "REDIS_PASSWORD" .env
  # Optional: ACL passwords (if enabling ACL)
  grep "REDIS_APP_PASSWORD" .env
  grep "REDIS_ADMIN_PASSWORD" .env
  grep "REDIS_KONG_PASSWORD" .env
  grep "REDIS_READONLY_PASSWORD" .env
  ```

- [ ] **Review Configuration Files**
  - [ ] `infrastructure/redis/redis-secure.conf` exists
  - [ ] `scripts/generate-redis-certs.sh` is executable
  - [ ] `docker-compose.yml` updated with new volume mounts
  - [ ] `docker-compose.redis-ha.yml` updated (if using HA)

### 2. Security Review

- [ ] **Password Strength**
  - [ ] `REDIS_PASSWORD` is at least 32 characters
  - [ ] ACL passwords (if used) are unique and strong
  - [ ] Passwords stored securely (not in git)

- [ ] **Certificate Preparation (if enabling TLS)**
  - [ ] Certificates generated: `./scripts/generate-redis-certs.sh`
  - [ ] Certificates verified: `openssl verify -CAfile config/redis/certs/ca.crt config/redis/certs/server.crt`
  - [ ] Private keys excluded from git: Check `.gitignore`

- [ ] **Network Security**
  - [ ] Redis port bound to localhost only: `127.0.0.1:6379`
  - [ ] Docker network isolation configured
  - [ ] Firewall rules reviewed (if applicable)

### 3. Testing Environment Ready

- [ ] **Staging Environment Available**
  - [ ] Staging environment mirrors production
  - [ ] Can test without affecting production
  - [ ] Rollback plan prepared

- [ ] **Monitoring Setup**
  - [ ] Prometheus/Grafana configured
  - [ ] Alert rules defined
  - [ ] On-call rotation established

---

## Deployment Steps

### Phase 1: Standalone Redis (No TLS, No ACL)

**Goal:** Use enhanced configuration without breaking changes

- [ ] **Step 1.1: Update Configuration File**
  ```bash
  # Verify new config file
  cat infrastructure/redis/redis-secure.conf | head -50

  # Note: TLS and ACL sections are commented by default
  ```

- [ ] **Step 1.2: Update Docker Compose**
  - [ ] `docker-compose.yml` uses `redis-secure.conf`
  - [ ] ACL password env vars added (defaults to REDIS_PASSWORD)
  - [ ] TLS settings remain commented

- [ ] **Step 1.3: Restart Redis**
  ```bash
  docker-compose restart redis
  ```

- [ ] **Step 1.4: Verify Operation**
  ```bash
  # Basic connectivity
  docker exec sahool-redis redis-cli -a $REDIS_PASSWORD PING
  # Expected: PONG

  # Check memory limit
  docker exec sahool-redis redis-cli -a $REDIS_PASSWORD CONFIG GET maxmemory
  # Expected: 512000000 (512MB)

  # Verify persistence
  docker exec sahool-redis redis-cli -a $REDIS_PASSWORD INFO persistence | grep aof_enabled
  # Expected: aof_enabled:1
  ```

- [ ] **Step 1.5: Test Services**
  - [ ] All services connect successfully
  - [ ] Session management works
  - [ ] Cache operations work
  - [ ] Kong rate limiting works
  - [ ] No errors in service logs

**✅ Phase 1 Complete - Baseline Security Active**

---

### Phase 2: Enable TLS Encryption (Staging First)

**Goal:** Enable encrypted connections in staging, then production

#### Staging Deployment

- [ ] **Step 2.1: Generate TLS Certificates**
  ```bash
  ./scripts/generate-redis-certs.sh

  # Verify certificates
  ls -la config/redis/certs/
  openssl x509 -in config/redis/certs/server.crt -noout -dates
  ```

- [ ] **Step 2.2: Enable TLS in Docker Compose**
  - [ ] Uncomment TLS command arguments in `docker-compose.yml`
  - [ ] Uncomment certificate volume mount
  - [ ] Update healthcheck (if using TLS for healthcheck)

- [ ] **Step 2.3: Update Connection Strings**
  - [ ] Change `redis://` to `rediss://` in all services
  - [ ] Update `.env` files with new URLs
  - [ ] Verify client libraries support TLS

- [ ] **Step 2.4: Deploy to Staging**
  ```bash
  docker-compose down
  docker-compose up -d
  ```

- [ ] **Step 2.5: Verify TLS**
  ```bash
  # Test TLS connection
  redis-cli --tls \
    --cert config/redis/certs/client.crt \
    --key config/redis/certs/client.key \
    --cacert config/redis/certs/ca.crt \
    -h localhost -p 6379 -a $REDIS_PASSWORD PING
  # Expected: PONG

  # Check encryption in INFO
  docker exec sahool-redis redis-cli --tls \
    --cert /etc/redis/certs/client.crt \
    --key /etc/redis/certs/client.key \
    --cacert /etc/redis/certs/ca.crt \
    -a $REDIS_PASSWORD INFO server | grep tls
  ```

- [ ] **Step 2.6: Staging Testing**
  - [ ] All services connect over TLS
  - [ ] Performance acceptable (expect 20-40% overhead)
  - [ ] No certificate errors
  - [ ] Session management works
  - [ ] Run full integration test suite

#### Production Deployment

- [ ] **Step 2.7: Generate Production Certificates**
  - [ ] Use proper CA-signed certificates (recommended)
  - [ ] OR generate self-signed with production SANs
  - [ ] Verify certificate validity period (recommend 90 days)

- [ ] **Step 2.8: Schedule Maintenance Window**
  - [ ] Notify users of planned downtime
  - [ ] Set up monitoring alerts
  - [ ] Prepare rollback procedure
  - [ ] On-call team ready

- [ ] **Step 2.9: Deploy TLS to Production**
  ```bash
  # Backup current state
  docker exec sahool-redis redis-cli -a $REDIS_PASSWORD SAVE

  # Update configuration
  # (same steps as staging)

  # Restart
  docker-compose restart redis
  ```

- [ ] **Step 2.10: Post-Deployment Verification**
  - [ ] All services reconnect successfully
  - [ ] TLS encryption confirmed
  - [ ] Monitor performance metrics
  - [ ] Check error rates
  - [ ] Verify session persistence

**✅ Phase 2 Complete - TLS Encryption Active**

---

### Phase 3: Enable ACL (Staged Rollout)

**Goal:** Implement fine-grained access control

#### Preparation

- [ ] **Step 3.1: Generate ACL Passwords**
  ```bash
  # Generate strong passwords
  REDIS_APP_PASSWORD=$(openssl rand -base64 32)
  REDIS_ADMIN_PASSWORD=$(openssl rand -base64 32)
  REDIS_KONG_PASSWORD=$(openssl rand -base64 32)
  REDIS_READONLY_PASSWORD=$(openssl rand -base64 32)

  # Add to .env file (secure storage)
  echo "REDIS_APP_PASSWORD=$REDIS_APP_PASSWORD" >> .env
  echo "REDIS_ADMIN_PASSWORD=$REDIS_ADMIN_PASSWORD" >> .env
  echo "REDIS_KONG_PASSWORD=$REDIS_KONG_PASSWORD" >> .env
  echo "REDIS_READONLY_PASSWORD=$REDIS_READONLY_PASSWORD" >> .env
  ```

- [ ] **Step 3.2: Store Passwords Securely**
  - [ ] Add to secrets management system (Vault, AWS Secrets Manager, etc.)
  - [ ] Document password rotation procedure
  - [ ] Set up password expiration reminders

- [ ] **Step 3.3: Enable ACL in Configuration**
  - [ ] Edit `infrastructure/redis/redis-secure.conf`
  - [ ] Uncomment ACL user definitions (lines 47-72)
  - [ ] Uncomment "user default off" (line 54)

#### Staging Deployment

- [ ] **Step 3.4: Deploy ACL to Staging**
  ```bash
  docker-compose restart redis
  ```

- [ ] **Step 3.5: Verify ACL Users**
  ```bash
  # List ACL users
  docker exec sahool-redis redis-cli -a $REDIS_PASSWORD ACL LIST

  # Check app user permissions
  docker exec sahool-redis redis-cli -a $REDIS_PASSWORD ACL GETUSER sahool_app

  # Test app user login
  redis-cli --user sahool_app --pass $REDIS_APP_PASSWORD PING
  # Expected: PONG
  ```

- [ ] **Step 3.6: Update Service Configurations**
  - [ ] Field Management: Use `sahool_app` user
  - [ ] Marketplace: Use `sahool_app` user
  - [ ] Kong Gateway: Use `kong_gateway` user
  - [ ] Monitoring: Use `sahool_readonly` user
  - [ ] Operations scripts: Use `sahool_admin` user

- [ ] **Step 3.7: Test ACL Permissions**
  ```bash
  # Test app user can read/write sessions
  redis-cli --user sahool_app --pass $REDIS_APP_PASSWORD \
    SET session:test value
  # Expected: OK

  # Test app user CANNOT run admin commands
  redis-cli --user sahool_app --pass $REDIS_APP_PASSWORD \
    CONFIG GET maxmemory
  # Expected: NOPERM error

  # Test admin user CAN run admin commands
  redis-cli --user sahool_admin --pass $REDIS_ADMIN_PASSWORD \
    CONFIG GET maxmemory
  # Expected: maxmemory value
  ```

- [ ] **Step 3.8: Staging Testing**
  - [ ] All services authenticate correctly
  - [ ] Permissions enforced as expected
  - [ ] No permission denied errors in logs
  - [ ] Session management works
  - [ ] Cache operations work
  - [ ] Admin operations work with admin user

#### Production Deployment

- [ ] **Step 3.9: Deploy ACL to Production**
  - [ ] Follow same steps as staging
  - [ ] Schedule during maintenance window
  - [ ] Monitor closely for permission errors

- [ ] **Step 3.10: Post-Deployment Verification**
  - [ ] All services connect with correct users
  - [ ] No authentication failures
  - [ ] Audit logs show correct user activity
  - [ ] Performance metrics normal

**✅ Phase 3 Complete - ACL Active**

---

### Phase 4: High Availability (Optional)

**Goal:** Deploy Redis Sentinel for automatic failover

- [ ] **Step 4.1: Review HA Architecture**
  - [ ] Read `docker-compose.redis-ha.yml`
  - [ ] Understand Sentinel quorum (2 of 3)
  - [ ] Plan for 5-30 second failover time

- [ ] **Step 4.2: Prepare HA Environment**
  - [ ] Ensure sufficient resources (3x Redis + 3x Sentinel)
  - [ ] Update service configs to use Sentinel
  - [ ] Test Sentinel-aware client libraries

- [ ] **Step 4.3: Deploy Sentinel**
  ```bash
  docker-compose -f docker-compose.redis-ha.yml up -d
  ```

- [ ] **Step 4.4: Verify HA Setup**
  ```bash
  # Check master
  docker exec sahool-redis-sentinel-1 redis-cli -p 26379 \
    SENTINEL MASTER sahool-master

  # Check replicas
  docker exec sahool-redis-sentinel-1 redis-cli -p 26379 \
    SENTINEL REPLICAS sahool-master
  # Expected: 2 replicas

  # Check Sentinels
  docker exec sahool-redis-sentinel-1 redis-cli -p 26379 \
    SENTINEL SENTINELS sahool-master
  # Expected: 2 other sentinels
  ```

- [ ] **Step 4.5: Test Failover**
  ```bash
  # Simulate master failure
  docker stop sahool-redis-master

  # Wait for failover (5-30 seconds)
  sleep 30

  # Verify new master
  docker exec sahool-redis-sentinel-1 redis-cli -p 26379 \
    SENTINEL GET-MASTER-ADDR-BY-NAME sahool-master
  # Expected: New master address

  # Restart old master (becomes replica)
  docker start sahool-redis-master
  ```

**✅ Phase 4 Complete - High Availability Active**

---

### Phase 5: Kubernetes Deployment

**Goal:** Deploy with maxmemory settings

- [ ] **Step 5.1: Update Helm Values**
  ```yaml
  redis:
    master:
      maxmemory: "768mb"
      evictionPolicy: "allkeys-lru"
  ```

- [ ] **Step 5.2: Deploy Helm Chart**
  ```bash
  helm upgrade --install sahool-infra helm/infra -f helm/infra/values.yaml
  ```

- [ ] **Step 5.3: Verify Deployment**
  ```bash
  kubectl get pods -l app.kubernetes.io/component=redis
  kubectl logs -l app.kubernetes.io/component=redis

  # Verify maxmemory setting
  kubectl exec deployment/sahool-redis -- \
    redis-cli -a $REDIS_PASSWORD CONFIG GET maxmemory
  # Expected: 805306368 (768MB)
  ```

**✅ Phase 5 Complete - Kubernetes Deployed**

---

## Post-Deployment Checklist

### Monitoring and Alerting

- [ ] **Configure Metrics Dashboard**
  - [ ] Import Redis Grafana dashboard
  - [ ] Configure custom panels
  - [ ] Set up real-time monitoring

- [ ] **Configure Alerts**
  - [ ] Memory usage > 90%
  - [ ] Connection count > 80% of max
  - [ ] Replication lag > 10 seconds (HA)
  - [ ] Sentinel master changes (HA)
  - [ ] Authentication failures
  - [ ] TLS certificate expiration (30 days)

- [ ] **Test Alerts**
  - [ ] Trigger test alert
  - [ ] Verify notification delivery
  - [ ] Confirm escalation procedures

### Documentation

- [ ] **Update Documentation**
  - [ ] Architecture diagrams
  - [ ] Connection string examples
  - [ ] Troubleshooting guide
  - [ ] Runbooks

- [ ] **Training**
  - [ ] Operations team training
  - [ ] Development team guidelines
  - [ ] Security team briefing

### Security Audit

- [ ] **Security Review**
  - [ ] Penetration testing (if required)
  - [ ] Compliance validation
  - [ ] Security audit report

- [ ] **Certificate Management**
  - [ ] Certificate renewal procedure documented
  - [ ] Renewal reminders configured
  - [ ] Auto-renewal scripts (if applicable)

### Backup and Recovery

- [ ] **Test Backup**
  - [ ] Manual backup: `docker exec sahool-redis redis-cli -a $REDIS_PASSWORD SAVE`
  - [ ] Verify backup file exists
  - [ ] Test restore procedure

- [ ] **Automate Backups**
  - [ ] Cron job for daily backups
  - [ ] Retention policy configured (7 daily, 4 weekly, 12 monthly)
  - [ ] Backup verification automated

---

## Rollback Plan

### If Issues Occur

- [ ] **Immediate Rollback (< 5 minutes)**
  ```bash
  # Revert to previous docker-compose configuration
  git checkout HEAD~1 docker-compose.yml
  docker-compose restart redis

  # Verify services reconnect
  docker exec sahool-redis redis-cli -a $REDIS_PASSWORD PING
  ```

- [ ] **Restore from Backup**
  ```bash
  # Stop Redis
  docker-compose stop redis

  # Restore RDB file
  docker cp ./backup/redis-20260106.rdb sahool-redis:/data/sahool-dump.rdb

  # Start Redis
  docker-compose start redis
  ```

- [ ] **Escalation**
  - [ ] Contact on-call engineer
  - [ ] Notify security team (if security issue)
  - [ ] Update incident report

---

## Success Criteria

### Technical Metrics

- [ ] **Performance**
  - [ ] Latency < 5ms (P99)
  - [ ] Throughput > 10,000 ops/sec
  - [ ] CPU usage < 50%
  - [ ] Memory usage < 80% of limit

- [ ] **Reliability**
  - [ ] Uptime > 99.9%
  - [ ] Data durability (no data loss)
  - [ ] Automatic failover < 30 seconds (HA)

- [ ] **Security**
  - [ ] All connections encrypted (if TLS enabled)
  - [ ] All commands authenticated
  - [ ] ACL permissions enforced (if ACL enabled)
  - [ ] No security vulnerabilities detected

### Business Metrics

- [ ] **User Experience**
  - [ ] No user-facing errors
  - [ ] Response times acceptable
  - [ ] Session persistence working

- [ ] **Operational**
  - [ ] Monitoring dashboards active
  - [ ] Alerts configured
  - [ ] Team trained
  - [ ] Documentation complete

---

## Sign-Off

**Deployment Team:**
- [ ] DevOps Lead: _______________ Date: _______
- [ ] Security Lead: _______________ Date: _______
- [ ] Platform Architect: _______________ Date: _______

**Approval:**
- [ ] CTO/Engineering Manager: _______________ Date: _______

---

**Deployment Date:** __________
**Deployment Time:** __________
**Deployed By:** __________

---

*End of Deployment Checklist*
