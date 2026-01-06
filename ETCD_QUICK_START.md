# Etcd Authentication - Quick Start Guide

## 🚀 Quick Deployment

### 1. Set Credentials
```bash
# Edit .env file
nano .env

# Add these lines (or update if they exist):
ETCD_ROOT_USERNAME=root
ETCD_ROOT_PASSWORD=$(openssl rand -base64 24)
```

### 2. Start Services
```bash
# Start etcd
docker-compose up -d etcd

# Wait for etcd to be healthy (5-10 seconds)
docker-compose ps etcd

# Initialize authentication
docker-compose up -d etcd-init

# Check init logs
docker logs sahool-etcd-init

# Start Milvus
docker-compose up -d milvus
```

### 3. Verify
```bash
# Test authenticated access
docker exec -e ETCDCTL_USER=root -e ETCDCTL_PASSWORD=your-password \
  sahool-etcd etcdctl endpoint health

# Should output: 127.0.0.1:2379 is healthy
```

---

## 🔍 Quick Checks

### Check if authentication is enabled:
```bash
docker exec sahool-etcd etcdctl user list
# If auth enabled: Error: etcdserver: user name is empty
# If auth disabled: Lists users without authentication
```

### Check Milvus connection:
```bash
docker logs sahool-milvus 2>&1 | grep -i "etcd" | tail -5
# Should show successful etcd connection
```

### View etcd-init logs:
```bash
docker logs sahool-etcd-init
# Should show: ✓ Etcd authentication setup completed successfully!
```

---

## 🛠️ Common Commands

### Access etcd with authentication:
```bash
# Set credentials as environment variables
export ETCDCTL_USER=root
export ETCDCTL_PASSWORD=your-password

# Run etcdctl commands
docker exec -e ETCDCTL_USER -e ETCDCTL_PASSWORD sahool-etcd etcdctl endpoint health
docker exec -e ETCDCTL_USER -e ETCDCTL_PASSWORD sahool-etcd etcdctl user list
docker exec -e ETCDCTL_USER -e ETCDCTL_PASSWORD sahool-etcd etcdctl get --prefix /
```

### Backup etcd data:
```bash
docker exec -e ETCDCTL_USER=root -e ETCDCTL_PASSWORD=your-password \
  sahool-etcd etcdctl snapshot save /etcd/backup.db

docker cp sahool-etcd:/etcd/backup.db ./etcd-backup-$(date +%Y%m%d).db
```

---

## ⚠️ Troubleshooting

### Problem: "etcdserver: authentication is not enabled"
**Solution**: Authentication not yet enabled. Run etcd-init:
```bash
docker-compose up -d etcd-init
docker logs sahool-etcd-init
```

### Problem: Milvus fails to start
**Solution**: Check etcd credentials match in .env:
```bash
grep ETCD_ .env
docker logs sahool-milvus | grep -i error
```

### Problem: Need to reset authentication
**Solution**: Stop services and clear etcd data:
```bash
docker-compose down
docker volume rm sahool-etcd-data
docker-compose up -d etcd etcd-init milvus
```

---

## 📝 Environment Variables

Required in `.env` file:
```bash
ETCD_ROOT_USERNAME=root
ETCD_ROOT_PASSWORD=<secure-password-here>
```

Used by:
- `etcd` - For authentication configuration
- `etcd-init` - For enabling authentication
- `milvus` - For connecting to etcd

---

## 🔐 Security Checklist

- [ ] Strong password set (minimum 16 characters)
- [ ] Password not committed to git
- [ ] .env file in .gitignore
- [ ] Only Milvus has etcd access credentials
- [ ] Etcd port (2379) bound to localhost only
- [ ] Regular backups scheduled
- [ ] Authentication logs monitored

---

## 📚 Related Documentation

- Full implementation details: `ETCD_AUTHENTICATION_IMPLEMENTATION.md`
- Etcd official docs: https://etcd.io/docs/latest/op-guide/authentication/
- Milvus etcd configuration: https://milvus.io/docs/configure_etcd.md

---

**Last Updated**: 2026-01-06
