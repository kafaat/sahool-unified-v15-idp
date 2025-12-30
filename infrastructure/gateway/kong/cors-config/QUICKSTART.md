# CORS Configuration Quick Start Guide

## 🚀 Quick Setup (2 Minutes)

### Step 1: Set Your Environment

Edit your `.env` file in the Kong directory:

```bash
cd /home/user/sahool-unified-v15-idp/infrastructure/gateway/kong
```

Add this line to your `.env` file (or create it from `.env.example`):

```bash
CORS_ENVIRONMENT=development
```

### Step 2: Start Kong

```bash
docker-compose up -d
```

That's it! Your CORS configuration is now active.

## 🔄 Switching Environments

### Development → Staging

```bash
# Update .env
sed -i 's/CORS_ENVIRONMENT=development/CORS_ENVIRONMENT=staging/' .env

# Restart Kong
docker-compose restart kong
```

### Staging → Production

```bash
# Update .env
sed -i 's/CORS_ENVIRONMENT=staging/CORS_ENVIRONMENT=production/' .env

# Restart Kong
docker-compose restart kong
```

## ✅ Verify Configuration

### Check Current Environment

```bash
# View current setting
grep CORS_ENVIRONMENT .env

# Check Kong container
docker exec kong-gateway env | grep CORS
```

### Test CORS (Development)

```bash
# Test from localhost:3000
curl -X OPTIONS http://localhost:8000/api/v1/health \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -i | grep -i "access-control"
```

Expected output:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 3600
```

## 📝 Common Tasks

### Add New Development Origin

1. Edit `cors-config/cors-development.yml`
2. Add your origin to the list:
   ```yaml
   cors:
     origins:
       - http://localhost:3000
       - http://localhost:4200  # ← Your new origin
   ```
3. Restart Kong: `docker-compose restart kong`

### Add New Production Origin

⚠️ **IMPORTANT:** Only add trusted domains!

1. Edit `cors-config/cors-production.yml`
2. Add the HTTPS origin:
   ```yaml
   cors:
     origins:
       - https://sahool.app
       - https://newdomain.com  # ← Must be HTTPS!
   ```
3. Test in staging first
4. Deploy to production: `docker-compose restart kong`

## 🐛 Troubleshooting

### CORS Error in Browser

**Error:** "Access to fetch blocked by CORS policy"

**Quick Fix:**
```bash
# 1. Check your origin is allowed
grep -A 20 "origins:" cors-config/cors-${CORS_ENVIRONMENT}.yml

# 2. Reload Kong
docker exec kong-gateway kong reload

# 3. Check Kong logs
docker logs kong-gateway --tail 50
```

### Configuration Not Applied

```bash
# Force apply
./scripts/apply-cors-config.sh ${CORS_ENVIRONMENT}

# Restart Kong
docker-compose restart kong

# Verify
docker logs kong-gateway | grep -i cors
```

## 📚 Need More Help?

- Full documentation: [README.md](./README.md)
- Implementation details: [../CORS_IMPLEMENTATION_SUMMARY.md](../CORS_IMPLEMENTATION_SUMMARY.md)
- Kong CORS plugin: https://docs.konghq.com/hub/kong-inc/cors/

## 🎯 Environment Cheat Sheet

| Environment | Origins | Use Case |
|------------|---------|----------|
| **development** | localhost + dev domains | Local development |
| **staging** | staging domains + limited localhost | QA/Testing |
| **production** | Production domains only | Live application |

## 🔒 Security Reminders

- ✅ Always use `https://` in production
- ✅ Never use wildcard (`*`) origins
- ✅ Test in staging before production
- ❌ Never enable development CORS in production
- ❌ Never commit `.env` files to git

---

**Pro Tip:** Run `./scripts/apply-cors-config.sh` without arguments to see which environment is currently active!
