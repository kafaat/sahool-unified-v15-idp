# JWT Key Rotation Procedure
# إجراءات تدوير مفاتيح JWT

> **Version:** 1.0
> **Last Updated:** 2025-12-30
> **Applies to:** SAHOOL Platform Kong Gateway

---

## Table of Contents / جدول المحتويات

1. [Overview / نظرة عامة](#overview)
2. [Why Key Rotation? / لماذا تدوير المفاتيح؟](#why-key-rotation)
3. [Supported Algorithms / الخوارزميات المدعومة](#supported-algorithms)
4. [Prerequisites / المتطلبات الأساسية](#prerequisites)
5. [Generating RSA Keys / توليد مفاتيح RSA](#generating-rsa-keys)
6. [Key Rotation Procedure / إجراءات تدوير المفاتيح](#key-rotation-procedure)
7. [Migration from HS256 to RS256 / الانتقال من HS256 إلى RS256](#migration-from-hs256-to-rs256)
8. [Rollback Procedure / إجراءات التراجع](#rollback-procedure)
9. [Best Practices / أفضل الممارسات](#best-practices)
10. [Troubleshooting / استكشاف الأخطاء](#troubleshooting)

---

## Overview / نظرة عامة

The SAHOOL Platform Kong Gateway supports both **HS256** (HMAC with SHA-256) and **RS256** (RSA Signature with SHA-256) JWT algorithms. This document provides comprehensive procedures for rotating JWT keys to maintain security and compliance.

تدعم بوابة Kong لمنصة سهول كلاً من خوارزميات JWT **HS256** (HMAC مع SHA-256) و **RS256** (توقيع RSA مع SHA-256). يوفر هذا المستند إجراءات شاملة لتدوير مفاتيح JWT للحفاظ على الأمان والامتثال.

---

## Why Key Rotation? / لماذا تدوير المفاتيح؟

Regular key rotation is critical for:

- **Security**: Limits exposure if a key is compromised
- **Compliance**: Meets industry standards (PCI-DSS, GDPR, SOC 2)
- **Best Practices**: Follows NIST and OWASP recommendations
- **Risk Management**: Reduces impact of potential breaches

تدوير المفاتيح المنتظم ضروري لـ:

- **الأمان**: يحد من التعرض في حالة اختراق المفتاح
- **الامتثال**: يلبي معايير الصناعة (PCI-DSS، GDPR، SOC 2)
- **أفضل الممارسات**: يتبع توصيات NIST و OWASP
- **إدارة المخاطر**: يقلل من تأثير الاختراقات المحتملة

**Recommended Rotation Schedule / جدول التدوير الموصى به:**
- **Production / الإنتاج**: Every 90 days
- **Staging / التجهيز**: Every 180 days
- **Development / التطوير**: As needed

---

## Supported Algorithms / الخوارزميات المدعومة

| Algorithm | Type | Security | Use Case |
|-----------|------|----------|----------|
| **HS256** | Symmetric | Good | Legacy support, simple deployments |
| **RS256** | Asymmetric | Better | Recommended for production, microservices |

| الخوارزمية | النوع | الأمان | حالة الاستخدام |
|-----------|------|--------|----------------|
| **HS256** | متماثل | جيد | دعم قديم، عمليات نشر بسيطة |
| **RS256** | غير متماثل | أفضل | موصى به للإنتاج، الخدمات المصغرة |

**Current Configuration / التكوين الحالي:**
Kong is configured to support both algorithms for backward compatibility:
```yaml
algorithms:
  - RS256  # Primary
  - HS256  # Fallback
```

---

## Prerequisites / المتطلبات الأساسية

Before starting key rotation, ensure you have:

قبل البدء في تدوير المفاتيح، تأكد من أن لديك:

- [ ] Access to production environment
- [ ] OpenSSL installed (`openssl version`)
- [ ] Backup of current configuration
- [ ] Access to `.env` file
- [ ] Notification sent to API consumers
- [ ] Maintenance window scheduled (if required)

---

## Generating RSA Keys / توليد مفاتيح RSA

### Step 1: Generate Private Key / توليد المفتاح الخاص

```bash
# Generate 2048-bit RSA private key
openssl genrsa -out private.pem 2048

# For enhanced security, use 4096-bit (recommended for production)
openssl genrsa -out private.pem 4096
```

### Step 2: Extract Public Key / استخراج المفتاح العام

```bash
# Extract public key from private key
openssl rsa -in private.pem -outform PEM -pubout -out public.pem
```

### Step 3: Format for Kong / تنسيق لـ Kong

```bash
# Remove the BEGIN/END lines and newlines for .env file
cat public.pem | grep -v "BEGIN PUBLIC KEY" | grep -v "END PUBLIC KEY" | tr -d '\n'
```

**Example Output / مثال على الإخراج:**
```
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1234567890...
```

### Step 4: Secure Storage / التخزين الآمن

**CRITICAL: Store private keys securely!**

- ✅ Use a secrets management system (HashiCorp Vault, AWS Secrets Manager)
- ✅ Encrypt at rest
- ✅ Implement access controls
- ❌ Never commit to version control
- ❌ Never share via email or chat

**هام: قم بتخزين المفاتيح الخاصة بشكل آمن!**

---

## Key Rotation Procedure / إجراءات تدوير المفاتيح

### Phase 1: Preparation / التحضير

1. **Schedule Maintenance Window** (if needed)
   ```bash
   # Notify users at least 48 hours in advance
   # Post maintenance notice on status page
   ```

2. **Backup Current Configuration**
   ```bash
   cd /home/user/sahool-unified-v15-idp/infrastructure/gateway/kong

   # Backup current .env
   cp .env .env.backup.$(date +%Y%m%d)

   # Backup Kong configuration
   cp kong.yml kong.yml.backup.$(date +%Y%m%d)
   cp consumers.yml consumers.yml.backup.$(date +%Y%m%d)
   ```

3. **Generate New RSA Keys**
   ```bash
   # Create a keys directory
   mkdir -p /secure/keys/$(date +%Y%m%d)
   cd /secure/keys/$(date +%Y%m%d)

   # Generate keys for each package
   for package in starter professional enterprise research admin sahool-api; do
     openssl genrsa -out ${package}_private.pem 2048
     openssl rsa -in ${package}_private.pem -outform PEM -pubout -out ${package}_public.pem
   done
   ```

### Phase 2: Update Configuration / تحديث التكوين

1. **Update .env File**
   ```bash
   # Edit .env file
   nano /home/user/sahool-unified-v15-idp/infrastructure/gateway/kong/.env
   ```

2. **Add New Public Keys**
   For each package, add the public key:
   ```env
   # Example for Starter Package
   STARTER_RSA_PUBLIC_KEY="MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..."
   ```

   **Script to Extract and Format:**
   ```bash
   for package in starter professional enterprise research admin sahool-api; do
     public_key=$(cat ${package}_public.pem | grep -v "BEGIN PUBLIC KEY" | grep -v "END PUBLIC KEY" | tr -d '\n')
     echo "${package^^}_RSA_PUBLIC_KEY=\"${public_key}\""
   done
   ```

3. **Validate Configuration**
   ```bash
   # Test Kong configuration
   docker exec kong kong config parse /etc/kong/kong.yml

   # Check for errors
   echo $?  # Should return 0
   ```

### Phase 3: Rolling Update / التحديث المتدرج

1. **Update Kong Configuration**
   ```bash
   cd /home/user/sahool-unified-v15-idp/infrastructure/gateway/kong

   # Reload Kong with new configuration
   docker exec kong kong reload
   ```

2. **Monitor Logs**
   ```bash
   # Watch Kong logs for errors
   docker logs -f kong

   # Watch for JWT validation errors
   grep "JWT" /tmp/kong-access.log | tail -f
   ```

3. **Health Check**
   ```bash
   # Test health endpoint
   curl -i http://localhost:8000/health

   # Should return: 200 OK
   ```

### Phase 4: API Consumer Migration / ترحيل مستهلكي API

**Option A: Gradual Migration (Recommended)**

1. Notify API consumers of new public keys
2. Provide 30-day migration period
3. Both HS256 and RS256 work simultaneously
4. Monitor usage of each algorithm
5. After migration period, deprecate HS256

**Option B: Immediate Migration**

1. Update all API consumers at once
2. Requires coordination with all teams
3. Higher risk of service disruption

### Phase 5: Verification / التحقق

1. **Test with Sample JWT**
   ```bash
   # Generate a test JWT (you'll need a JWT library or tool)
   # Example using a test script
   ./test-jwt-rs256.sh
   ```

2. **Test API Endpoints**
   ```bash
   # Test with RS256 token
   curl -H "Authorization: Bearer <RS256_TOKEN>" \
        http://localhost:8000/api/v1/fields

   # Test with HS256 token (should still work as fallback)
   curl -H "Authorization: Bearer <HS256_TOKEN>" \
        http://localhost:8000/api/v1/fields
   ```

3. **Monitor Metrics**
   ```bash
   # Check Prometheus metrics
   curl http://localhost:9090/metrics | grep kong_http_status

   # Check Grafana dashboard for anomalies
   ```

### Phase 6: Documentation / التوثيق

1. **Update Internal Documentation**
   - Record rotation date
   - Document new key IDs
   - Update API consumer guides

2. **Update Change Log**
   ```bash
   echo "$(date): JWT keys rotated - RS256" >> /var/log/kong/key_rotation.log
   ```

---

## Migration from HS256 to RS256 / الانتقال من HS256 إلى RS256

### Why Migrate? / لماذا الانتقال؟

RS256 offers superior security because:
- Private keys never leave the issuer
- Public keys can be distributed safely
- Better for microservices architecture
- Industry best practice

### Migration Timeline / الجدول الزمني للانتقال

```
Week 1-2:  Announce migration, share public keys
Week 3-4:  API consumers test RS256 in staging
Week 5-6:  Gradual production rollout
Week 7-8:  Monitor and support
Week 9-12: Full migration, deprecate HS256
```

### Step-by-Step Migration / خطوات الانتقال

1. **Preparation Phase**
   ```bash
   # Generate RS256 keys for all packages
   cd /secure/keys/rs256-migration
   ./generate-all-keys.sh
   ```

2. **Parallel Running Phase**
   - Configure Kong to accept both algorithms (already done)
   - RS256 consumers can start using new tokens
   - HS256 consumers continue using existing tokens

3. **Monitoring Phase**
   ```bash
   # Track algorithm usage
   docker exec kong kong config db_export /tmp/kong-config.json
   grep "algorithm" /tmp/kong-config.json
   ```

4. **Deprecation Phase**
   - After 90 days, remove HS256 support
   - Update kong.yml:
   ```yaml
   algorithms:
     - RS256  # Only RS256
   ```

---

## Rollback Procedure / إجراءات التراجع

If issues arise during key rotation:

### Immediate Rollback / التراجع الفوري

```bash
# Stop Kong
docker stop kong

# Restore backup configuration
cd /home/user/sahool-unified-v15-idp/infrastructure/gateway/kong
cp .env.backup.YYYYMMDD .env
cp kong.yml.backup.YYYYMMDD kong.yml
cp consumers.yml.backup.YYYYMMDD consumers.yml

# Start Kong
docker start kong

# Verify
curl http://localhost:8000/health
```

### Partial Rollback / التراجع الجزئي

If only specific consumers are affected:

```bash
# Keep RS256 configuration
# Restore specific HS256 consumer from backup
# Reload Kong
docker exec kong kong reload
```

---

## Best Practices / أفضل الممارسات

### Security / الأمان

1. **Key Storage**
   - Use hardware security modules (HSM) for production
   - Implement multi-party authorization for key access
   - Enable audit logging for all key operations

2. **Key Generation**
   - Use at least 2048-bit RSA keys (4096-bit recommended)
   - Generate keys on secure, offline systems
   - Use cryptographically secure random number generators

3. **Access Control**
   - Limit who can rotate keys
   - Implement approval workflows
   - Use separate keys per environment (dev/staging/prod)

### Operational / التشغيلية

1. **Testing**
   - Test in staging before production
   - Have rollback plan ready
   - Conduct dry runs

2. **Communication**
   - Notify stakeholders in advance
   - Provide clear migration documentation
   - Offer support during transition

3. **Monitoring**
   - Set up alerts for JWT validation failures
   - Monitor API error rates
   - Track algorithm usage statistics

### Compliance / الامتثال

1. **Audit Trail**
   ```bash
   # Maintain rotation log
   echo "$(date): Key rotation initiated by ${USER}" >> /var/log/key-rotation-audit.log
   echo "$(date): Old key ID: ${OLD_KEY_ID}" >> /var/log/key-rotation-audit.log
   echo "$(date): New key ID: ${NEW_KEY_ID}" >> /var/log/key-rotation-audit.log
   ```

2. **Retention Policy**
   - Keep old keys for 90 days after rotation
   - Store securely in cold storage
   - Document destruction procedures

---

## Troubleshooting / استكشاف الأخطاء

### Common Issues / المشاكل الشائعة

#### Issue 1: JWT Validation Failures

**Symptoms:**
```
401 Unauthorized
{"message": "Invalid JWT"}
```

**Solution:**
```bash
# Check Kong logs
docker logs kong | grep JWT

# Verify public key format
cat consumers.yml | grep -A 5 "rsa_public_key"

# Test key format
echo "YOUR_PUBLIC_KEY" | openssl rsa -pubin -text -noout
```

#### Issue 2: Algorithm Mismatch

**Symptoms:**
```
{"message": "Algorithm not allowed"}
```

**Solution:**
```bash
# Verify algorithms in kong.yml
grep -A 3 "algorithms:" kong.yml

# Should show:
# algorithms:
#   - RS256
#   - HS256
```

#### Issue 3: Public Key Format Error

**Symptoms:**
```
{"message": "Invalid public key"}
```

**Solution:**
```bash
# Ensure public key is properly formatted
# Remove all newlines except within PEM markers
sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/ /g' public.pem

# Or use the extraction script
cat public.pem | grep -v "BEGIN" | grep -v "END" | tr -d '\n'
```

#### Issue 4: Consumer Not Found

**Symptoms:**
```
{"message": "No consumer found"}
```

**Solution:**
```bash
# Verify consumer exists
docker exec kong kong config db_export /tmp/export.json
cat /tmp/export.json | jq '.consumers[] | select(.username=="sahool-api")'

# Check ACL groups
cat consumers.yml | grep -A 10 "username: sahool-api"
```

### Debug Commands / أوامر التصحيح

```bash
# Check Kong configuration
docker exec kong kong config parse /etc/kong/kong.yml

# List all consumers
docker exec kong kong config db_export /tmp/kong.json
cat /tmp/kong.json | jq '.consumers[].username'

# Test JWT token locally
echo "YOUR_JWT_TOKEN" | cut -d. -f2 | base64 -d | jq .

# Verify Kong is using updated config
docker exec kong cat /etc/kong/kong.yml | grep -A 10 "jwt"
```

### Getting Help / الحصول على المساعدة

If issues persist:

1. **Check Documentation**
   - Kong JWT Plugin: https://docs.konghq.com/hub/kong-inc/jwt/
   - Kong Troubleshooting: https://docs.konghq.com/gateway/latest/troubleshoot/

2. **Enable Debug Logging**
   ```bash
   # Temporarily enable debug mode
   docker exec kong kong config set log_level debug
   docker exec kong kong reload
   ```

3. **Contact Support**
   - Internal: platform-team@sahool.platform
   - Kong Enterprise Support: support@konghq.com

---

## Quick Reference / مرجع سريع

### Generate Keys Command / أمر توليد المفاتيح

```bash
# One-liner to generate and format RSA keys
openssl genrsa 2048 | tee private.pem | openssl rsa -pubout | grep -v "BEGIN\|END" | tr -d '\n'
```

### Rotation Checklist / قائمة التحقق من التدوير

- [ ] Backup current configuration
- [ ] Generate new RSA keys
- [ ] Update .env with public keys
- [ ] Test configuration syntax
- [ ] Reload Kong
- [ ] Monitor logs for errors
- [ ] Test API endpoints
- [ ] Verify metrics
- [ ] Document rotation
- [ ] Notify stakeholders

### Environment Variables / متغيرات البيئة

```env
JWT_ALGORITHM=RS256
STARTER_RSA_PUBLIC_KEY="..."
PROFESSIONAL_RSA_PUBLIC_KEY="..."
ENTERPRISE_RSA_PUBLIC_KEY="..."
RESEARCH_RSA_PUBLIC_KEY="..."
ADMIN_RSA_PUBLIC_KEY="..."
SAHOOL_API_RSA_PUBLIC_KEY="..."
JWT_KEY_ROTATION_ENABLED=true
JWT_KEY_ROTATION_DAYS=90
```

---

## Appendix / الملحق

### A. Example Key Generation Script

```bash
#!/bin/bash
# generate-jwt-keys.sh

set -e

KEYS_DIR="/secure/keys/$(date +%Y%m%d)"
PACKAGES=("starter" "professional" "enterprise" "research" "admin" "sahool-api")

mkdir -p "$KEYS_DIR"
cd "$KEYS_DIR"

for package in "${PACKAGES[@]}"; do
    echo "Generating keys for $package..."

    # Generate private key
    openssl genrsa -out "${package}_private.pem" 2048

    # Extract public key
    openssl rsa -in "${package}_private.pem" -pubout -out "${package}_public.pem"

    # Format for .env
    public_key=$(cat "${package}_public.pem" | grep -v "BEGIN\|END" | tr -d '\n')
    echo "${package^^}_RSA_PUBLIC_KEY=\"${public_key}\"" >> keys.env

    echo "✓ Keys generated for $package"
done

echo ""
echo "Keys generated successfully!"
echo "Location: $KEYS_DIR"
echo "Environment variables saved to: $KEYS_DIR/keys.env"
echo ""
echo "Next steps:"
echo "1. Review keys.env"
echo "2. Add variables to .env file"
echo "3. Reload Kong configuration"
```

### B. Testing Script

```bash
#!/bin/bash
# test-jwt-endpoints.sh

BASE_URL="http://localhost:8000"
ENDPOINTS=(
    "/api/v1/fields"
    "/api/v1/weather"
    "/api/v1/notifications"
)

echo "Testing JWT authentication..."

for endpoint in "${ENDPOINTS[@]}"; do
    echo "Testing $endpoint..."

    # Test with RS256 token
    response=$(curl -s -w "%{http_code}" -H "Authorization: Bearer $RS256_TOKEN" \
                    "$BASE_URL$endpoint")

    if [ "${response: -3}" == "200" ]; then
        echo "✓ $endpoint - RS256 OK"
    else
        echo "✗ $endpoint - RS256 FAILED (HTTP ${response: -3})"
    fi
done
```

---

**Document Version:** 1.0
**Last Updated:** 2025-12-30
**Maintained by:** SAHOOL Platform Team
**Contact:** platform-team@sahool.platform

