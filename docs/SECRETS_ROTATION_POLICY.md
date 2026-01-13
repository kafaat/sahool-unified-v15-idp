# SAHOOL Platform - Secrets Rotation Policy

**Version:** 1.0
**Effective Date:** 2026-01-06
**Review Frequency:** Quarterly
**Owner:** DevOps & Security Teams

---

## 1. Purpose

This document defines the secrets rotation policy for the SAHOOL platform, ensuring:

- Regular rotation of cryptographic keys and credentials
- Minimized exposure window in case of compromise
- Compliance with security best practices and regulations
- Zero-downtime rotation procedures

---

## 2. Scope

This policy applies to all secrets used in the SAHOOL platform, including:

- Database credentials (PostgreSQL, Redis, etc.)
- API keys (internal and external)
- Encryption keys
- JWT signing keys
- TLS/SSL certificates
- Service account credentials
- OAuth client secrets

---

## 3. Rotation Schedule

### 3.1 Database Credentials

| Credential Type             | Rotation Frequency | Method                          | Downtime     |
| --------------------------- | ------------------ | ------------------------------- | ------------ |
| PostgreSQL application user | Every 90 days      | Vault dynamic secrets or manual | None         |
| PostgreSQL admin user       | Every 180 days     | Manual with coordination        | None         |
| PostgreSQL replication user | Every 180 days     | Manual with coordination        | None         |
| Redis password              | Every 90 days      | Manual (requires restart)       | < 30 seconds |
| Redis ACL users             | Every 90 days      | Manual                          | None         |

**Rotation Process:**

1. **Vault Dynamic Secrets (Recommended):**
   - Credentials automatically rotate every 24 hours
   - No manual intervention required
   - Old credentials revoked after grace period

2. **Manual Rotation:**

   ```bash
   # Step 1: Generate new password
   NEW_PASSWORD=$(openssl rand -base64 32)

   # Step 2: Update in Vault
   vault kv patch secret/sahool/database/postgres password="$NEW_PASSWORD"

   # Step 3: Update database
   PGPASSWORD="$OLD_PASSWORD" psql -h postgres -U postgres -c \
     "ALTER USER sahool WITH PASSWORD '$NEW_PASSWORD';"

   # Step 4: Trigger secret refresh in Kubernetes
   kubectl annotate externalsecret postgresql-credentials \
     force-sync="$(date +%s)" -n sahool --overwrite

   # Step 5: Verify applications can connect
   kubectl logs -n sahool deployment/field-ops --tail=50
   ```

### 3.2 JWT Signing Keys

| Key Type          | Rotation Frequency   | Method    | Grace Period |
| ----------------- | -------------------- | --------- | ------------ |
| HS256 secret key  | Every 180 days       | Manual    | 7 days       |
| RS256 private key | Every 365 days       | Manual    | 30 days      |
| RS256 public key  | When private rotates | Automatic | N/A          |

**Rotation Process:**

```bash
# Step 1: Generate new keys
openssl genrsa -out private-new.pem 4096
openssl rsa -in private-new.pem -pubout -out public-new.pem

# Step 2: Add new key to Vault (don't remove old yet)
vault kv patch secret/sahool/auth/jwt \
  private_key_new="$(cat private-new.pem)" \
  public_key_new="$(cat public-new.pem)"

# Step 3: Configure application to accept both old and new keys
# for verification (grace period)

# Step 4: Start signing with new key

# Step 5: After grace period, remove old key
vault kv patch secret/sahool/auth/jwt \
  private_key="$(cat private-new.pem)" \
  public_key="$(cat public-new.pem)"

# Step 6: Clean up
rm private-new.pem public-new.pem
```

**Impact:**

- Users must re-authenticate after grace period
- Active sessions remain valid during grace period
- Notify users 24 hours before rotation

### 3.3 Encryption Keys

| Key Type                      | Rotation Frequency | Method | Re-encryption Required |
| ----------------------------- | ------------------ | ------ | ---------------------- |
| Data encryption key (AES-256) | Every 365 days     | Manual | Yes                    |
| Backup encryption key         | Every 365 days     | Manual | Yes                    |
| Database column encryption    | Every 365 days     | Manual | Yes                    |

**Rotation Process:**

```bash
# Step 1: Generate new key
NEW_KEY=$(openssl rand -base64 32)

# Step 2: Update in Vault (keep old key for decryption)
vault kv patch secret/sahool/encryption \
  data_key="$NEW_KEY" \
  previous_key="$OLD_KEY"

# Step 3: Run re-encryption job
kubectl apply -f jobs/re-encrypt-data.yaml

# Step 4: Monitor re-encryption progress
kubectl logs -f jobs/re-encrypt-data -n sahool

# Step 5: After completion, remove old key
vault kv patch secret/sahool/encryption \
  data_key="$NEW_KEY"
```

**Important:** Never delete the old encryption key before re-encrypting all data!

### 3.4 API Keys

| API Key Type                    | Rotation Frequency | Method | Provider Action               |
| ------------------------------- | ------------------ | ------ | ----------------------------- |
| Internal service keys           | Every 90 days      | Manual | None                          |
| External API keys (OpenWeather) | Every 180 days     | Manual | Regenerate in provider portal |
| Payment gateway keys (Stripe)   | Every 180 days     | Manual | Rotate via Stripe dashboard   |
| Cloud provider keys (AWS/Azure) | Every 90 days      | Manual | Rotate via IAM                |

**Rotation Process:**

```bash
# Internal service keys
NEW_KEY=$(openssl rand -base64 64)
vault kv patch secret/sahool/internal/service_key key="$NEW_KEY"

# External API keys (example: OpenWeather)
# 1. Login to provider portal
# 2. Generate new API key
# 3. Update in Vault
vault kv patch secret/sahool/external/openweather api_key="NEW_API_KEY"

# 4. Test new key
curl "https://api.openweathermap.org/data/2.5/weather?q=London&appid=NEW_API_KEY"

# 5. Deactivate old key in provider portal (after verification)
```

### 3.5 TLS/SSL Certificates

| Certificate Type                 | Rotation Frequency | Method                   | Automation |
| -------------------------------- | ------------------ | ------------------------ | ---------- |
| Internal services (Vault-issued) | Every 90 days      | Automatic (Vault PKI)    | Yes        |
| Public-facing (Let's Encrypt)    | Every 90 days      | Automatic (cert-manager) | Yes        |
| Client certificates              | Every 180 days     | Manual                   | No         |
| CA certificates                  | Every 5 years      | Manual with planning     | No         |

**Rotation Process (Automated):**

```bash
# Vault PKI automatically rotates certificates
# cert-manager handles Let's Encrypt renewal
# No manual intervention required

# Verify auto-renewal
kubectl get certificates -n sahool
```

---

## 4. Rotation Responsibilities

### 4.1 Roles and Responsibilities

| Role                 | Responsibilities                                                                                                         |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **Security Team**    | - Define rotation policies<br>- Review audit logs<br>- Approve exceptions<br>- Incident response                         |
| **DevOps Team**      | - Execute rotations<br>- Maintain automation<br>- Monitor rotation jobs<br>- Update documentation                        |
| **Development Team** | - Test applications after rotation<br>- Implement grace periods<br>- Report rotation issues<br>- Update secret consumers |
| **CTO/CISO**         | - Policy approval<br>- Budget allocation<br>- Compliance oversight<br>- Exception approval                               |

### 4.2 Rotation Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Rotation Scheduled (Automated Scheduler)                 │
│    - Check rotation intervals                               │
│    - Generate rotation tasks                                │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Notification Sent (T-7 days)                             │
│    - Slack/email to DevOps team                            │
│    - Create Jira ticket                                     │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Preparation (T-3 days)                                   │
│    - Review rotation procedure                              │
│    - Check dependencies                                     │
│    - Schedule maintenance window (if needed)                │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Rotation Execution (T-0)                                 │
│    - Run rotation script                                    │
│    - Monitor for errors                                     │
│    - Verify new credentials work                            │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Verification (T+1 hour)                                  │
│    - Test application connectivity                          │
│    - Check error logs                                       │
│    - Verify metrics (no spike in errors)                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Cleanup (T+grace period)                                 │
│    - Remove old credentials                                 │
│    - Update documentation                                   │
│    - Close Jira ticket                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Emergency Rotation

### 5.1 Triggers

Emergency rotation must be performed immediately upon:

1. **Suspected Compromise:**
   - Credentials found in logs
   - Credentials committed to public repository
   - Unauthorized access detected
   - Employee departure (with system access)

2. **Security Vulnerabilities:**
   - Critical CVE in cryptographic library
   - Algorithm weakness discovered
   - Compliance violation identified

3. **Operational Incidents:**
   - Accidental credential exposure
   - Backup restoration (credentials may be old)
   - Disaster recovery scenario

### 5.2 Emergency Rotation Process

```bash
# 1. IMMEDIATELY revoke compromised credentials
vault kv patch secret/sahool/<path> \
  <key>="REVOKED_$(date +%s)"

# 2. Generate new credentials
NEW_SECRET=$(openssl rand -base64 32)

# 3. Update in Vault
vault kv patch secret/sahool/<path> \
  <key>="$NEW_SECRET"

# 4. Force immediate refresh in Kubernetes
kubectl annotate externalsecret <name> \
  force-sync="$(date +%s)" \
  -n sahool --overwrite

# 5. Restart affected services (if needed)
kubectl rollout restart deployment/<service> -n sahool

# 6. Monitor for errors
kubectl logs -f deployment/<service> -n sahool

# 7. Create incident report
# Document: what, when, who, why, how
```

### 5.3 Incident Notification

**Immediate notification to:**

- Security team (via PagerDuty)
- DevOps team (via Slack)
- CTO/CISO (via email/phone)

**Incident report must include:**

- What credentials were compromised
- When the compromise was detected
- How the compromise occurred
- What actions were taken
- Impact assessment
- Lessons learned

---

## 6. Compliance and Auditing

### 6.1 Compliance Requirements

| Standard       | Requirement                   | SAHOOL Implementation                   |
| -------------- | ----------------------------- | --------------------------------------- |
| **OWASP ASVS** | Regular credential rotation   | ✅ Automated rotation every 90-365 days |
| **PCI DSS**    | Cryptographic key management  | ✅ Vault with audit logging             |
| **SOC 2**      | Access control and monitoring | ✅ RBAC + audit trails                  |
| **GDPR**       | Data encryption               | ✅ AES-256-GCM encryption               |
| **ISO 27001**  | Information security controls | ✅ Comprehensive secrets management     |

### 6.2 Audit Requirements

All secret rotations must be:

1. **Logged:**
   - Timestamp
   - Who performed the rotation
   - What secret was rotated
   - Success/failure status
   - Any issues encountered

2. **Documented:**
   - Rotation procedure followed
   - Any deviations from standard process
   - Post-rotation verification results
   - Incident reports (if applicable)

3. **Reviewed:**
   - Monthly review of rotation logs
   - Quarterly policy review
   - Annual security audit

### 6.3 Audit Log Location

- **Vault audit logs:** `/vault/logs/audit.log`
- **Rotation logs:** `/var/log/sahool-rotation.log`
- **Secret access logs:** `/var/log/sahool/secret-audit.log`

**Retention:** 365 days (1 year)

---

## 7. Exceptions and Deviations

### 7.1 Requesting an Exception

Exceptions to this policy require:

1. **Written justification:**
   - Technical reason for exception
   - Business impact of compliance
   - Alternative controls in place
   - Duration of exception

2. **Approval:**
   - Manager approval (< 30 days)
   - CTO approval (< 90 days)
   - CISO approval (> 90 days)

3. **Documentation:**
   - Exception ticket in Jira
   - Expiration date
   - Review schedule

### 7.2 Common Exceptions

| Scenario                                  | Typical Duration              | Approval Level |
| ----------------------------------------- | ----------------------------- | -------------- |
| Testing new rotation procedure            | 30 days                       | Manager        |
| Third-party API key (no rotation support) | Until vendor implements       | CTO            |
| Legacy system integration                 | 90 days (with migration plan) | CISO           |
| Vendor SLA constraints                    | Per contract terms            | Legal + CTO    |

---

## 8. Automation

### 8.1 Automated Rotation (Preferred)

**Vault Dynamic Secrets:**

- Database credentials rotate every 24 hours
- No manual intervention
- Automatic revocation

**Cert-manager:**

- TLS certificates auto-renew 30 days before expiry
- Let's Encrypt integration
- Automatic deployment

### 8.2 Semi-Automated Rotation

**Rotation Scheduler:**

```bash
# /etc/cron.d/sahool-rotation
# Check and rotate secrets daily at 2 AM
0 2 * * * sahool /opt/sahool/scripts/security/automated-rotation-scheduler.sh --rotate-all
```

**Features:**

- Checks rotation schedules
- Sends notifications before rotation
- Executes rotation if due
- Logs all actions
- Alerts on failures

### 8.3 Manual Rotation

For secrets that cannot be automated:

1. Create calendar reminder (T-7 days before due)
2. Follow documented procedure
3. Update rotation tracking
4. Verify success
5. Document completion

---

## 9. Monitoring and Alerting

### 9.1 Metrics to Monitor

```bash
# Secrets approaching expiration
sahool_secret_expires_soon{secret_type, days_until_expiry}

# Failed rotation attempts
sahool_secret_rotation_failures_total{secret_type, reason}

# Secrets past rotation interval
sahool_secret_overdue{secret_type, days_overdue}

# Rotation execution time
sahool_secret_rotation_duration_seconds{secret_type}
```

### 9.2 Alerts

| Alert                        | Threshold | Severity | Action              |
| ---------------------------- | --------- | -------- | ------------------- |
| Secret expires in < 7 days   | Warning   | Medium   | Schedule rotation   |
| Secret expires in < 24 hours | Critical  | High     | Immediate rotation  |
| Rotation failed              | Immediate | Critical | Manual intervention |
| Secret overdue > 30 days     | Immediate | High     | Emergency rotation  |
| Suspicious access pattern    | Immediate | Medium   | Investigate         |

---

## 10. Training and Documentation

### 10.1 Required Training

All personnel with secrets access must complete:

1. **Security Awareness Training:**
   - Secrets handling best practices
   - Incident reporting
   - Social engineering awareness

2. **Technical Training (DevOps):**
   - Vault administration
   - Rotation procedures
   - Troubleshooting

3. **Annual Refresher:**
   - Policy updates
   - Lessons learned from incidents
   - New tools and procedures

### 10.2 Documentation

**Must maintain:**

- This rotation policy (quarterly review)
- Rotation runbooks (per secret type)
- Incident response playbook
- Contact lists (on-call rotation)

**Location:** `/docs/` in repository

---

## 11. Version History

| Version | Date       | Author      | Changes                 |
| ------- | ---------- | ----------- | ----------------------- |
| 1.0     | 2026-01-06 | DevOps Team | Initial policy creation |

---

## 12. Approval

| Role              | Name | Signature | Date |
| ----------------- | ---- | --------- | ---- |
| **CISO**          |      |           |      |
| **CTO**           |      |           |      |
| **Security Lead** |      |           |      |
| **DevOps Lead**   |      |           |      |

---

## Appendix A: Rotation Checklist

### Database Password Rotation

- [ ] Verify backup is recent (< 24 hours)
- [ ] Generate new password (32+ characters)
- [ ] Update in Vault
- [ ] Update database user password
- [ ] Trigger Kubernetes secret refresh
- [ ] Verify applications can connect
- [ ] Monitor error logs for 1 hour
- [ ] Document completion in tracking system

### JWT Key Rotation

- [ ] Generate new RSA key pair (4096 bits)
- [ ] Add new key to Vault (grace period start)
- [ ] Configure app to accept both keys
- [ ] Start signing with new key
- [ ] Send user notification (re-auth required)
- [ ] Wait grace period (7 days)
- [ ] Remove old key from Vault
- [ ] Verify no authentication errors
- [ ] Document completion

### API Key Rotation

- [ ] Identify all consumers of the key
- [ ] Generate new key (provider portal)
- [ ] Update in Vault
- [ ] Trigger secret refresh
- [ ] Test API connectivity
- [ ] Monitor for errors (1 hour)
- [ ] Deactivate old key in provider portal
- [ ] Verify no service degradation
- [ ] Document completion

---

**Next Review Date:** 2026-04-06 (Quarterly)
