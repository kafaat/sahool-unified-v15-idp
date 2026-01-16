# NATS NKey Authentication Setup Guide

## Table of Contents

1. [Introduction](#introduction)
2. [What are NKeys?](#what-are-nkeys)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [NKey Generation](#nkey-generation)
6. [Server Configuration](#server-configuration)
7. [Client Integration](#client-integration)
8. [Deployment](#deployment)
9. [Security Best Practices](#security-best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Migration Guide](#migration-guide)

---

## Introduction

This guide walks through setting up NKey-based authentication for NATS in the SAHOOL platform. NKeys provide cryptographic authentication without transmitting passwords, offering superior security compared to traditional username/password authentication.

### Benefits of NKey Authentication

- **No Password Transmission**: Private keys never leave the client
- **Cryptographic Security**: Ed25519 signatures for authentication
- **Decentralized Authorization**: No central password database
- **Account Isolation**: Multi-tenancy with complete separation
- **JWT-based Permissions**: Fine-grained access control
- **Easy Rotation**: Change credentials without server restarts
- **Revocation Support**: Centrally revoke access via JWT updates

---

## What are NKeys?

NKeys are Ed25519 key pairs used for authentication in NATS. The authentication flow works as follows:

1. **Operator** creates and signs **Account** JWTs
2. **Accounts** create and sign **User** JWTs
3. **Users** connect with their credentials (seed + JWT)
4. NATS server verifies the JWT signature chain
5. Server grants access based on JWT claims

### Key Components

```
Operator (Root of Trust)
    └── Account (Tenant/Organization)
            ├── User 1 (Service/Application)
            ├── User 2 (Service/Application)
            └── User N (Service/Application)
```

---

## Prerequisites

### Required Tools

1. **NSC (NATS Security CLI)** - For generating NKeys and JWTs
2. **NATS CLI** - For testing connections
3. **NATS Server** - Version 2.2.0 or higher

### Install NSC

```bash
# Using curl
curl -L https://raw.githubusercontent.com/nats-io/nsc/master/install.sh | sh

# Using go
go install github.com/nats-io/nsc/v2@latest

# Add to PATH
export PATH=$PATH:$HOME/.local/bin

# Verify installation
nsc --version
```

### Install NATS CLI

```bash
# Using curl
curl -L https://github.com/nats-io/natscli/releases/latest/download/nats-linux-amd64.tar.gz | tar -xz
sudo mv nats /usr/local/bin/

# Verify installation
nats --version
```

---

## NKey Generation

### Automated Setup

Use the provided script to generate all NKeys automatically:

```bash
# Navigate to scripts directory
cd /home/user/sahool-unified-v15-idp/scripts/nats

# Run generation script
./generate-nkeys.sh

# Output will be in:
# - /home/user/sahool-unified-v15-idp/config/nats/nkeys/
# - /home/user/sahool-unified-v15-idp/config/nats/creds/
# - /home/user/sahool-unified-v15-idp/config/nats/generated/
```

### Manual Setup

If you prefer manual setup, follow these steps:

#### 1. Initialize NSC Environment

```bash
# Set NSC store directory
export NSC_HOME=/home/user/sahool-unified-v15-idp/config/nats/nkeys
export NKEYS_PATH=/home/user/sahool-unified-v15-idp/config/nats/nkeys

# Initialize NSC
nsc env -s "${NSC_HOME}"
```

#### 2. Create Operator

```bash
# Create operator with system account support
nsc add operator SAHOOL --sys --generate-signing-key

# Export operator JWT
nsc describe operator SAHOOL -J > operator.jwt
```

#### 3. Create Accounts

```bash
# Create system account (for monitoring)
nsc add account SYS

# Create application account with JetStream
nsc add account APP \
    --js-mem-storage 1G \
    --js-disk-storage 10G \
    --js-streams 100 \
    --js-consumer 1000
```

#### 4. Create Users

```bash
# Admin user (full access)
nsc add user -a APP admin \
    --allow-pub ">" \
    --allow-sub ">" \
    --max-connections 10 \
    --max-subscriptions 100 \
    --max-payload 8M

# Service user (limited access)
nsc add user -a APP field-service \
    --allow-pub "field.>,sahool.field.>,_INBOX.>" \
    --allow-sub "field.>,sahool.field.>,_INBOX.>" \
    --deny-pub "\$SYS.>,\$JS.API.>" \
    --max-connections 50 \
    --max-subscriptions 200 \
    --max-payload 8M

# Monitor user (read-only)
nsc add user -a APP monitor \
    --deny-pub ">" \
    --allow-sub "sahool.>,field.>,weather.>" \
    --deny-sub "\$SYS.>,\$JS.API.>" \
    --max-connections 5 \
    --max-subscriptions 50 \
    --max-payload 1M
```

#### 5. Generate Credential Files

```bash
# Create credentials directory
mkdir -p /home/user/sahool-unified-v15-idp/config/nats/creds

# Generate credentials for each user
nsc generate creds -a APP -n admin > /home/user/sahool-unified-v15-idp/config/nats/creds/APP_admin.creds
nsc generate creds -a APP -n field-service > /home/user/sahool-unified-v15-idp/config/nats/creds/APP_field-service.creds
nsc generate creds -a APP -n monitor > /home/user/sahool-unified-v15-idp/config/nats/creds/APP_monitor.creds

# Set proper permissions
chmod 600 /home/user/sahool-unified-v15-idp/config/nats/creds/*.creds
```

---

## Server Configuration

### 1. Prepare Resolver Directory

```bash
# Create resolver directory
mkdir -p /home/user/sahool-unified-v15-idp/config/nats/resolver

# Export account JWTs to resolver
nsc describe account SYS -J > /home/user/sahool-unified-v15-idp/config/nats/resolver/SYS.jwt
nsc describe account APP -J > /home/user/sahool-unified-v15-idp/config/nats/resolver/APP.jwt
```

### 2. Extract Required Keys

```bash
# Get operator JWT
OPERATOR_JWT=$(nsc describe operator SAHOOL -J)

# Get operator public key
OPERATOR_PUBLIC_KEY=$(nsc describe operator SAHOOL -J | jq -r '.nats.signing_keys[0]')

# Get system account public key
SYSTEM_ACCOUNT_PUBLIC_KEY=$(nsc describe account SYS -J | jq -r '.sub')

# Save to environment file
cat > /home/user/sahool-unified-v15-idp/config/nats/.env.nkey << EOF
NATS_OPERATOR_JWT="${OPERATOR_JWT}"
NATS_OPERATOR_PUBLIC_KEY="${OPERATOR_PUBLIC_KEY}"
NATS_SYSTEM_ACCOUNT_PUBLIC_KEY="${SYSTEM_ACCOUNT_PUBLIC_KEY}"
NATS_JETSTREAM_KEY="$(openssl rand -base64 32)"
NATS_CLUSTER_USER="cluster_user"
NATS_CLUSTER_PASSWORD="$(openssl rand -base64 32)"
EOF
```

### 3. Update NATS Configuration

The NKey configuration is already created at:

```
/home/user/sahool-unified-v15-idp/config/nats/nats-nkey.conf
```

### 4. Docker Compose Integration

Update your `docker-compose.yml` to use the NKey configuration:

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
      - "4222:4222" # Client connections
      - "8222:8222" # HTTP monitoring
      - "6222:6222" # Cluster connections
    networks:
      - sahool-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "nats-server", "-sl=https://localhost:8222"]
      interval: 10s
      timeout: 5s
      retries: 3

volumes:
  nats-data:
    driver: local

networks:
  sahool-network:
    driver: bridge
```

### 5. Kubernetes Deployment

Create ConfigMaps and Secrets:

```yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: nats-config
  namespace: sahool
data:
  nats-nkey.conf: |
    # Include content from /home/user/sahool-unified-v15-idp/config/nats/nats-nkey.conf
---
apiVersion: v1
kind: Secret
metadata:
  name: nats-resolver
  namespace: sahool
type: Opaque
data:
  SYS.jwt: <base64-encoded-jwt>
  APP.jwt: <base64-encoded-jwt>
---
apiVersion: v1
kind: Secret
metadata:
  name: nats-env
  namespace: sahool
type: Opaque
stringData:
  NATS_OPERATOR_JWT: "<operator-jwt>"
  NATS_OPERATOR_PUBLIC_KEY: "<operator-public-key>"
  NATS_SYSTEM_ACCOUNT_PUBLIC_KEY: "<system-account-public-key>"
  NATS_JETSTREAM_KEY: "<jetstream-encryption-key>"
  NATS_CLUSTER_USER: "cluster_user"
  NATS_CLUSTER_PASSWORD: "<cluster-password>"
---
apiVersion: v1
kind: Service
metadata:
  name: nats
  namespace: sahool
spec:
  selector:
    app: nats
  ports:
    - name: client
      port: 4222
      targetPort: 4222
    - name: monitoring
      port: 8222
      targetPort: 8222
    - name: cluster
      port: 6222
      targetPort: 6222
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: nats
  namespace: sahool
spec:
  serviceName: nats
  replicas: 1
  selector:
    matchLabels:
      app: nats
  template:
    metadata:
      labels:
        app: nats
    spec:
      containers:
        - name: nats
          image: nats:2.10-alpine
          command:
            - "nats-server"
            - "-c"
            - "/etc/nats/nats-nkey.conf"
          ports:
            - containerPort: 4222
              name: client
            - containerPort: 8222
              name: monitoring
            - containerPort: 6222
              name: cluster
          volumeMounts:
            - name: config
              mountPath: /etc/nats
            - name: resolver
              mountPath: /etc/nats/resolver
            - name: data
              mountPath: /data
          envFrom:
            - secretRef:
                name: nats-env
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 1000m
              memory: 1Gi
      volumes:
        - name: config
          configMap:
            name: nats-config
        - name: resolver
          secret:
            secretName: nats-resolver
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 10Gi
```

---

## Client Integration

### Node.js / TypeScript

#### Install Dependencies

```bash
npm install nats
```

#### Connection Example

```typescript
import { connect, NatsConnection } from "nats";

async function connectToNATS(): Promise<NatsConnection> {
  const nc = await connect({
    servers: "nats://localhost:4222",
    userCreds:
      "/home/user/sahool-unified-v15-idp/config/nats/creds/APP_field-service.creds",

    // Optional: TLS configuration
    tls: {
      caFile: "/etc/nats/certs/ca.crt",
      certFile: "/etc/nats/certs/client.crt",
      keyFile: "/etc/nats/certs/client.key",
    },

    // Connection options
    maxReconnectAttempts: -1,
    reconnectTimeWait: 2000,
    timeout: 10000,
  });

  console.log(`Connected to ${nc.getServer()}`);

  // Handle connection events
  nc.closed().then((err) => {
    if (err) {
      console.error("Connection closed with error:", err);
    }
  });

  return nc;
}

// Usage
const nc = await connectToNATS();

// Publish
await nc.publish(
  "field.operation.created",
  JSON.stringify({
    id: "123",
    type: "harvest",
  }),
);

// Subscribe
const sub = nc.subscribe("field.>");
for await (const msg of sub) {
  console.log(`Received: ${msg.subject}`, msg.data);
}
```

### Go

#### Install Dependencies

```bash
go get github.com/nats-io/nats.go
```

#### Connection Example

```go
package main

import (
    "log"
    "github.com/nats-io/nats.go"
)

func main() {
    // Connect with credentials
    nc, err := nats.Connect(
        "nats://localhost:4222",
        nats.UserCredentials("/home/user/sahool-unified-v15-idp/config/nats/creds/APP_field-service.creds"),
        nats.MaxReconnects(-1),
        nats.ReconnectWait(2*time.Second),
    )
    if err != nil {
        log.Fatal(err)
    }
    defer nc.Close()

    log.Printf("Connected to %s", nc.ConnectedUrl())

    // Publish
    err = nc.Publish("field.operation.created", []byte(`{"id":"123","type":"harvest"}`))
    if err != nil {
        log.Fatal(err)
    }

    // Subscribe
    sub, err := nc.Subscribe("field.>", func(msg *nats.Msg) {
        log.Printf("Received on [%s]: %s", msg.Subject, string(msg.Data))
    })
    if err != nil {
        log.Fatal(err)
    }
    defer sub.Unsubscribe()

    // Keep alive
    select {}
}
```

### Python

#### Install Dependencies

```bash
pip install nats-py
```

#### Connection Example

```python
import asyncio
from nats.aio.client import Client as NATS

async def main():
    nc = NATS()

    # Connect with credentials
    await nc.connect(
        servers=["nats://localhost:4222"],
        user_credentials="/home/user/sahool-unified-v15-idp/config/nats/creds/APP_field-service.creds",
        max_reconnect_attempts=-1,
        reconnect_time_wait=2,
    )

    print(f"Connected to {nc.connected_url}")

    # Publish
    await nc.publish("field.operation.created", b'{"id":"123","type":"harvest"}')

    # Subscribe
    async def message_handler(msg):
        subject = msg.subject
        data = msg.data.decode()
        print(f"Received on [{subject}]: {data}")

    await nc.subscribe("field.>", cb=message_handler)

    # Keep alive
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        await nc.close()

if __name__ == '__main__':
    asyncio.run(main())
```

### Java

#### Maven Dependency

```xml
<dependency>
    <groupId>io.nats</groupId>
    <artifactId>jnats</artifactId>
    <version>2.17.0</version>
</dependency>
```

#### Connection Example

```java
import io.nats.client.*;

public class NATSExample {
    public static void main(String[] args) {
        try {
            // Connect with credentials
            Options options = new Options.Builder()
                .server("nats://localhost:4222")
                .userInfo(null, "/home/user/sahool-unified-v15-idp/config/nats/creds/APP_field-service.creds".toCharArray())
                .maxReconnects(-1)
                .reconnectWait(Duration.ofSeconds(2))
                .build();

            Connection nc = Nats.connect(options);
            System.out.println("Connected to " + nc.getConnectedUrl());

            // Publish
            nc.publish("field.operation.created", "{\"id\":\"123\",\"type\":\"harvest\"}".getBytes());

            // Subscribe
            Dispatcher d = nc.createDispatcher((msg) -> {
                System.out.printf("Received on [%s]: %s%n",
                    msg.getSubject(),
                    new String(msg.getData())
                );
            });
            d.subscribe("field.>");

            // Keep alive
            Thread.sleep(Long.MAX_VALUE);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

---

## Deployment

### Distribution of Credentials

Credentials must be securely distributed to each service:

#### Docker Secrets

```yaml
services:
  field-service:
    image: sahool/field-service:latest
    secrets:
      - nats_field_service_creds
    environment:
      NATS_CREDENTIALS_FILE: /run/secrets/nats_field_service_creds

secrets:
  nats_field_service_creds:
    file: ./config/nats/creds/APP_field-service.creds
```

#### Kubernetes Secrets

```bash
# Create secret from credential file
kubectl create secret generic field-service-nats-creds \
    --from-file=nats.creds=./config/nats/creds/APP_field-service.creds \
    -n sahool

# Mount in pod
apiVersion: v1
kind: Pod
metadata:
  name: field-service
spec:
  containers:
  - name: app
    image: sahool/field-service:latest
    env:
    - name: NATS_CREDENTIALS_FILE
      value: /etc/nats/creds/nats.creds
    volumeMounts:
    - name: nats-creds
      mountPath: /etc/nats/creds
      readOnly: true
  volumes:
  - name: nats-creds
    secret:
      secretName: field-service-nats-creds
      defaultMode: 0400
```

#### HashiCorp Vault

```bash
# Store credential in Vault
vault kv put secret/sahool/nats/field-service \
    creds=@./config/nats/creds/APP_field-service.creds

# Retrieve in application
vault kv get -field=creds secret/sahool/nats/field-service > /tmp/nats.creds
```

---

## Security Best Practices

### 1. Credential File Protection

```bash
# Set proper permissions
chmod 600 /home/user/sahool-unified-v15-idp/config/nats/creds/*.creds

# Set ownership
chown app:app /home/user/sahool-unified-v15-idp/config/nats/creds/*.creds

# Never commit credentials to git
echo "config/nats/creds/" >> .gitignore
echo "config/nats/.env.nkey" >> .gitignore
```

### 2. Credential Rotation

```bash
# Generate new user credentials
nsc add user -a APP field-service-new \
    --allow-pub "field.>,sahool.field.>,_INBOX.>" \
    --allow-sub "field.>,sahool.field.>,_INBOX.>" \
    --max-connections 50

# Generate new credential file
nsc generate creds -a APP -n field-service-new > APP_field-service-new.creds

# Deploy new credentials to services
# ... deployment steps ...

# After verification, revoke old user
nsc revoke user -a APP -n field-service

# Update resolver
nsc describe account APP -J > resolver/APP.jwt
```

### 3. JWT Expiration

```bash
# Add expiration to user JWT (1 year)
nsc edit user -a APP -n field-service --expiry 8760h

# Regenerate credentials
nsc generate creds -a APP -n field-service > APP_field-service.creds
```

### 4. Monitor Access

```bash
# Subscribe to system events (requires system account access)
nats sub -s nats://localhost:4222 --creds=SYS_system-monitor.creds "\$SYS.ACCOUNT.*.CONNECT"
nats sub -s nats://localhost:4222 --creds=SYS_system-monitor.creds "\$SYS.ACCOUNT.*.DISCONNECT"
```

### 5. Audit Logging

Enable comprehensive logging in NATS config:

```conf
# In nats-nkey.conf
connect_error_reports: 1
reconnect_error_reports: 1

system_account_events: {
    connect: true
    disconnect: true
    account_connections: true
}
```

---

## Troubleshooting

### Connection Failed: "authorization violation"

**Problem**: Client cannot authenticate

**Solutions**:

```bash
# 1. Verify credential file exists and is readable
ls -la /home/user/sahool-unified-v15-idp/config/nats/creds/APP_field-service.creds

# 2. Verify credential file format
cat /home/user/sahool-unified-v15-idp/config/nats/creds/APP_field-service.creds
# Should contain both JWT and seed

# 3. Check account JWT is in resolver
ls -la /home/user/sahool-unified-v15-idp/config/nats/resolver/APP.jwt

# 4. Verify NATS server logs
docker logs sahool-nats

# 5. Test with nats CLI
nats pub -s nats://localhost:4222 \
    --creds=/home/user/sahool-unified-v15-idp/config/nats/creds/APP_field-service.creds \
    test "Hello"
```

### Permission Denied on Subject

**Problem**: User doesn't have permission to publish/subscribe

**Solutions**:

```bash
# 1. Check user permissions
nsc describe user -a APP -n field-service

# 2. Update permissions
nsc edit user -a APP -n field-service \
    --allow-pub "field.>,new-subject.>"

# 3. Regenerate credentials
nsc generate creds -a APP -n field-service > APP_field-service.creds

# 4. Update resolver
nsc describe account APP -J > resolver/APP.jwt

# 5. Restart NATS or wait for resolver refresh (2 minutes)
```

### Server Not Loading Resolver

**Problem**: NATS server can't find account JWTs

**Solutions**:

```bash
# 1. Verify resolver directory path in config
grep "dir:" /home/user/sahool-unified-v15-idp/config/nats/nats-nkey.conf

# 2. Check resolver directory permissions
ls -la /home/user/sahool-unified-v15-idp/config/nats/resolver/

# 3. Verify JWT files exist
ls -la /home/user/sahool-unified-v15-idp/config/nats/resolver/*.jwt

# 4. Validate JWT format
cat /home/user/sahool-unified-v15-idp/config/nats/resolver/APP.jwt | jq '.'

# 5. Check NATS server logs for resolver errors
docker logs sahool-nats | grep resolver
```

### Testing Connection

```bash
# Install nats CLI if not already installed
curl -L https://github.com/nats-io/natscli/releases/latest/download/nats-linux-amd64.tar.gz | tar -xz
sudo mv nats /usr/local/bin/

# Create context
nats context save sahool \
    --server=nats://localhost:4222 \
    --creds=/home/user/sahool-unified-v15-idp/config/nats/creds/APP_admin.creds

# Test pub/sub
nats pub --context=sahool test.subject "Hello NATS"
nats sub --context=sahool "test.>"

# Check account info
nats account info --context=sahool

# List streams (JetStream)
nats stream ls --context=sahool
```

---

## Migration Guide

### Migrating from Password Auth to NKey Auth

#### Phase 1: Dual Authentication

1. Keep existing password authentication
2. Add NKey resolver alongside
3. Test NKey connections with new services

```conf
# nats-migration.conf - Supports both auth methods

# Legacy password auth
accounts {
    APP: {
        users: [
            { user: $NATS_USER, password: $NATS_PASSWORD }
        ]
    }
}

# New NKey auth
operator: $NATS_OPERATOR_JWT
resolver {
    type: full
    dir: "/etc/nats/resolver"
}
```

#### Phase 2: Service Migration

Gradually migrate services one by one:

1. Deploy NKey credentials to service
2. Update service configuration
3. Restart service
4. Verify connection and functionality
5. Move to next service

#### Phase 3: Complete Cutover

Once all services are migrated:

1. Remove password authentication from config
2. Use pure NKey configuration (`nats-nkey.conf`)
3. Restart NATS server
4. Monitor for any issues

---

## Advanced Topics

### Account Exports and Imports

Allow services in different accounts to communicate:

```bash
# In account A, export a service
nsc add export -a AccountA \
    --service \
    --subject "service.request"

# In account B, import the service
nsc add import -a AccountB \
    --service \
    --src-account $(nsc describe account AccountA -J | jq -r .sub) \
    --remote-subject "service.request"

# Update resolver
nsc describe account AccountA -J > resolver/AccountA.jwt
nsc describe account AccountB -J > resolver/AccountB.jwt
```

### Signing Keys for Delegation

Use signing keys for key rotation without changing operator:

```bash
# Generate signing key for operator
nsc edit operator SAHOOL --sk generate

# Use signing key to create account
nsc add account NewAccount --sk <signing-key-from-above>

# Rotate signing keys
nsc edit operator SAHOOL --sk generate
nsc edit operator SAHOOL --sk revoke <old-key>
```

### Account Server (Production)

For production with many accounts, use NATS Account Server:

```bash
# Install account server
go install github.com/nats-io/nats-account-server@latest

# Run account server
nats-account-server -nsc $NSC_HOME

# Update NATS config to use URL resolver
# resolver: URL(http://nats-account-server:9090/jwt/v1/accounts/)
```

---

## References

- [NATS Documentation](https://docs.nats.io/)
- [NKey Authentication Guide](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/auth_intro/nkey_auth)
- [NSC Tool Documentation](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/auth_intro/nsc)
- [NATS Account Server](https://github.com/nats-io/nats-account-server)
- [NATS Security Best Practices](https://docs.nats.io/running-a-nats-service/configuration/securing_nats)

---

## Support

For issues or questions:

1. Check NATS server logs: `docker logs sahool-nats`
2. Review NSC configuration: `nsc env`
3. Test credentials: `nats pub --creds=<creds-file> test "hello"`
4. Join NATS Slack: https://slack.nats.io/

---

**Last Updated**: 2026-01-07
**Version**: 1.0
**Author**: SAHOOL Platform Team
