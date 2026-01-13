# NATS NKey Quick Start Guide

## 🚀 Setup in 3 Steps

### Step 1: Generate NKeys

```bash
cd /home/user/sahool-unified-v15-idp

# Generate all NKeys, accounts, and users
./scripts/nats/generate-nkeys.sh

# Setup environment variables
./scripts/nats/setup-nkey-env.sh
```

### Step 2: Start NATS Server

Update your `docker-compose.yml`:

```yaml
services:
  nats:
    image: nats:2.10-alpine
    container_name: sahool-nats
    command:
      - "-c"
      - "/etc/nats/nats-nkey.conf"
    volumes:
      - ./config/nats/nats-nkey.conf:/etc/nats/nats-nkey.conf:ro
      - ./config/nats/resolver:/etc/nats/resolver:ro
      - ./config/nats/certs:/etc/nats/certs:ro
      - nats-data:/data
    env_file:
      - ./config/nats/.env.nkey
    ports:
      - "4222:4222"
      - "8222:8222"
    restart: unless-stopped
```

Start NATS:

```bash
docker-compose up -d nats
```

### Step 3: Connect Your Application

Use the generated credential files in `config/nats/creds/`:

**Node.js/TypeScript:**

```typescript
import { connect } from "nats";

const nc = await connect({
  servers: "nats://localhost:4222",
  userCreds: "./config/nats/creds/APP_field-service.creds",
});
```

**Go:**

```go
nc, err := nats.Connect(
    "nats://localhost:4222",
    nats.UserCredentials("./config/nats/creds/APP_field-service.creds"),
)
```

**Python:**

```python
await nc.connect(
    servers=["nats://localhost:4222"],
    user_credentials="./config/nats/creds/APP_field-service.creds"
)
```

---

## 📋 Available Credentials

After setup, you'll have these credential files:

| Credential File                  | Use Case               | Permissions                 |
| -------------------------------- | ---------------------- | --------------------------- |
| `SYS_system-monitor.creds`       | System monitoring      | Read-only system metrics    |
| `APP_admin.creds`                | Administration         | Full access to all subjects |
| `APP_monitor.creds`              | Application monitoring | Read-only app subjects      |
| `APP_field-service.creds`        | Field operations       | Field-related subjects      |
| `APP_weather-service.creds`      | Weather data           | Weather subjects            |
| `APP_iot-service.creds`          | IoT sensors            | IoT data subjects           |
| `APP_notification-service.creds` | Notifications          | Notification subjects       |
| `APP_marketplace-service.creds`  | Marketplace            | Marketplace subjects        |
| `APP_billing-service.creds`      | Billing                | Billing subjects            |
| `APP_chat-service.creds`         | Chat                   | Chat message subjects       |

---

## 🧪 Test Your Setup

### Using nats CLI

```bash
# Install nats CLI
curl -L https://github.com/nats-io/natscli/releases/latest/download/nats-linux-amd64.tar.gz | tar -xz
sudo mv nats /usr/local/bin/

# Create a context
nats context save sahool \
    --server nats://localhost:4222 \
    --creds ./config/nats/creds/APP_admin.creds

# Publish a message
nats pub test.subject "Hello NATS" --context sahool

# Subscribe to messages
nats sub "test.>" --context sahool

# Check account info
nats account info --context sahool
```

### Using Docker

```bash
# Test pub/sub with docker
docker run --rm -v $(pwd)/config/nats/creds:/creds natsio/nats-box:latest \
    nats pub -s nats://host.docker.internal:4222 \
    --creds /creds/APP_admin.creds \
    test "Hello from Docker"
```

---

## 🔐 Security Checklist

- [x] NKeys generated
- [ ] `.env.nkey` file created and permissions set to 600
- [ ] Credential files in `config/nats/creds/` with permissions 600
- [ ] `.gitignore` updated (credentials won't be committed)
- [ ] TLS certificates in place (`config/nats/certs/`)
- [ ] JetStream encryption key set
- [ ] Resolver directory populated (`config/nats/resolver/`)

Verify:

```bash
# Check file permissions
ls -la config/nats/creds/
ls -la config/nats/.env.nkey

# Ensure credentials are in .gitignore
git check-ignore config/nats/creds/*.creds
```

---

## 🔄 Common Operations

### Add a New User

```bash
# Add user with NSC
nsc add user -a APP -n new-service \
    --allow-pub "new.>" \
    --allow-sub "new.>" \
    --max-connections 50

# Generate credentials
nsc generate creds -a APP -n new-service > config/nats/creds/APP_new-service.creds
chmod 600 config/nats/creds/APP_new-service.creds

# Update resolver
nsc describe account APP -J > config/nats/resolver/APP.jwt

# Restart NATS or wait 2 minutes for auto-refresh
docker-compose restart nats
```

### Rotate Credentials

```bash
# Generate new user
nsc add user -a APP -n field-service-v2 \
    --allow-pub "field.>" \
    --allow-sub "field.>" \
    --max-connections 50

# Generate new credentials
nsc generate creds -a APP -n field-service-v2 > config/nats/creds/APP_field-service-v2.creds

# Deploy new credentials to services
# ... deployment steps ...

# After verification, revoke old user
nsc revoke user -a APP -n field-service

# Update resolver
nsc describe account APP -J > config/nats/resolver/APP.jwt
```

### Check User Permissions

```bash
# View user permissions
nsc describe user -a APP -n field-service

# View account info
nsc describe account APP

# View operator info
nsc describe operator SAHOOL
```

---

## 📊 Monitoring

### Health Check

```bash
# Check NATS server health
curl http://localhost:8222/healthz

# View connections
curl http://localhost:8222/connz

# View account info
curl http://localhost:8222/accountz

# View JetStream info
curl http://localhost:8222/jsz
```

### Subscribe to System Events

```bash
# System account events (requires SYS credentials)
nats sub -s nats://localhost:4222 \
    --creds ./config/nats/creds/SYS_system-monitor.creds \
    '$SYS.ACCOUNT.*.CONNECT'

nats sub -s nats://localhost:4222 \
    --creds ./config/nats/creds/SYS_system-monitor.creds \
    '$SYS.ACCOUNT.*.DISCONNECT'
```

---

## 🐛 Troubleshooting

### "authorization violation"

**Cause**: Invalid or missing credentials

**Solution**:

```bash
# Verify credential file exists
ls -la config/nats/creds/APP_field-service.creds

# Check credential format
cat config/nats/creds/APP_field-service.creds
# Should have both JWT (-----BEGIN NATS USER JWT-----)
# and seed (-----BEGIN USER NKEY SEED-----)

# Regenerate credentials
nsc generate creds -a APP -n field-service > config/nats/creds/APP_field-service.creds
```

### "permission denied for publish to..."

**Cause**: User doesn't have permission for that subject

**Solution**:

```bash
# Check current permissions
nsc describe user -a APP -n field-service

# Add permission
nsc edit user -a APP -n field-service --allow-pub "new-subject.>"

# Regenerate credentials and update resolver
nsc generate creds -a APP -n field-service > config/nats/creds/APP_field-service.creds
nsc describe account APP -J > config/nats/resolver/APP.jwt

# Restart NATS
docker-compose restart nats
```

### "no route to account"

**Cause**: Account JWT not in resolver

**Solution**:

```bash
# Verify resolver directory
ls -la config/nats/resolver/

# Regenerate account JWTs
nsc describe account SYS -J > config/nats/resolver/SYS.jwt
nsc describe account APP -J > config/nats/resolver/APP.jwt

# Restart NATS
docker-compose restart nats
```

### Connection timeout

**Cause**: NATS server not running or network issue

**Solution**:

```bash
# Check NATS is running
docker ps | grep nats

# Check logs
docker logs sahool-nats

# Verify port is open
netstat -tuln | grep 4222

# Test connectivity
telnet localhost 4222
```

---

## 📚 Documentation

- **Full Setup Guide**: [docs/NATS_NKEY_SETUP.md](../../docs/NATS_NKEY_SETUP.md)
- **Scripts README**: [scripts/nats/README.md](../../scripts/nats/README.md)
- **Setup Summary**: [config/nats/generated/SETUP_SUMMARY.md](./generated/SETUP_SUMMARY.md)
- **NATS Official Docs**: https://docs.nats.io/

---

## 🆘 Need Help?

1. Check NATS server logs: `docker logs sahool-nats`
2. Verify NSC environment: `nsc env`
3. Test with nats CLI: `nats pub --creds <file> test "hello"`
4. Review documentation: `docs/NATS_NKEY_SETUP.md`

---

**Generated**: 2026-01-07
**Security**: NKey Authentication (No passwords transmitted)
**Status**: Production Ready ✅
