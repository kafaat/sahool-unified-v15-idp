# NATS NKey Generation Scripts

This directory contains scripts for generating and managing NATS NKeys for the SAHOOL platform.

## Files

- `generate-nkeys.sh` - Automated NKey generation script

## Quick Start

### Prerequisites

Install NSC (NATS Security CLI):

```bash
curl -L https://raw.githubusercontent.com/nats-io/nsc/master/install.sh | sh
export PATH=$PATH:$HOME/.local/bin
```

### Generate NKeys

```bash
# Run the generation script
./generate-nkeys.sh
```

This will create:

- **NKeys directory**: `/home/user/sahool-unified-v15-idp/config/nats/nkeys/`
  - Operator keys
  - Account keys
  - User keys

- **Credentials directory**: `/home/user/sahool-unified-v15-idp/config/nats/creds/`
  - `SYS_system-monitor.creds`
  - `APP_admin.creds`
  - `APP_service1.creds`
  - `APP_service2.creds`
  - `APP_monitor.creds`
  - `APP_field-service.creds`
  - `APP_weather-service.creds`
  - `APP_iot-service.creds`
  - `APP_notification-service.creds`
  - `APP_marketplace-service.creds`
  - `APP_billing-service.creds`
  - `APP_chat-service.creds`

- **Generated files**: `/home/user/sahool-unified-v15-idp/config/nats/generated/`
  - `operator.jwt` - Operator JWT
  - `SYS_account.jwt` - System account JWT
  - `APP_account.jwt` - Application account JWT
  - `resolver.conf` - Account resolver configuration
  - `SETUP_SUMMARY.md` - Setup summary and usage guide

## Output Structure

```
config/nats/
├── nkeys/                    # NSC key store
│   ├── .nsc/
│   ├── operator/
│   ├── accounts/
│   └── users/
├── creds/                    # User credential files
│   ├── SYS_system-monitor.creds
│   ├── APP_admin.creds
│   ├── APP_field-service.creds
│   └── ...
├── generated/                # Generated JWTs and configs
│   ├── operator.jwt
│   ├── SYS_account.jwt
│   ├── APP_account.jwt
│   ├── resolver.conf
│   ├── SETUP_SUMMARY.md
│   └── resolver/
│       ├── SYS.jwt
│       └── APP.jwt
└── resolver/                 # Resolver directory (copy from generated)
    ├── SYS.jwt
    └── APP.jwt
```

## Environment Variables

The script supports customization via environment variables:

```bash
# Operator name (default: SAHOOL)
export OPERATOR_NAME="SAHOOL"

# Base directory (default: /home/user/sahool-unified-v15-idp/config/nats)
export NATS_DIR="/path/to/nats/config"

# NKeys directory (default: ${NATS_DIR}/nkeys)
export NKEYS_DIR="/path/to/nkeys"

# Credentials directory (default: ${NATS_DIR}/creds)
export CREDS_DIR="/path/to/creds"

# Output directory (default: ${NATS_DIR}/generated)
export OUTPUT_DIR="/path/to/output"
```

## User Permissions

The script creates users with predefined permissions:

| User | Account | Permissions | Max Connections |
|------|---------|-------------|-----------------|
| `system-monitor` | SYS | Read-only monitoring | 5 |
| `admin` | APP | Full access | 10 |
| `monitor` | APP | Read-only | 5 |
| `service1` | APP | Standard service | 50 |
| `service2` | APP | Standard service | 50 |
| `field-service` | APP | Field operations | 50 |
| `weather-service` | APP | Weather data | 20 |
| `iot-service` | APP | IoT sensors | 100 |
| `notification-service` | APP | Notifications | 50 |
| `marketplace-service` | APP | Marketplace | 50 |
| `billing-service` | APP | Billing | 30 |
| `chat-service` | APP | Chat messages | 100 |

## Next Steps

After running the generation script:

1. **Setup Resolver**:
   ```bash
   # Copy resolver JWTs to resolver directory
   cp config/nats/generated/resolver/*.jwt config/nats/resolver/
   ```

2. **Extract Environment Variables**:
   ```bash
   # Get operator JWT
   OPERATOR_JWT=$(cat config/nats/generated/operator.jwt)

   # Get system account public key
   SYSTEM_ACCOUNT_KEY=$(nsc describe account SYS -J | jq -r '.sub')

   # Create .env file
   cat > config/nats/.env.nkey << EOF
   NATS_OPERATOR_JWT="${OPERATOR_JWT}"
   NATS_SYSTEM_ACCOUNT_PUBLIC_KEY="${SYSTEM_ACCOUNT_KEY}"
   NATS_JETSTREAM_KEY="$(openssl rand -base64 32)"
   EOF
   ```

3. **Update NATS Configuration**:
   - Use `config/nats/nats-nkey.conf`
   - Load environment variables from `.env.nkey`

4. **Distribute Credentials**:
   - Copy credential files to your services
   - Use Docker secrets or Kubernetes secrets
   - Never commit `.creds` files to version control

5. **Test Connection**:
   ```bash
   nats pub -s nats://localhost:4222 \
       --creds config/nats/creds/APP_admin.creds \
       test "Hello NATS"
   ```

## Security Notes

- Credential files contain private keys - **keep them secure**
- Set proper permissions: `chmod 600 *.creds`
- Never commit credentials to version control
- Add to `.gitignore`:
  ```
  config/nats/creds/
  config/nats/nkeys/
  config/nats/.env.nkey
  ```
- Rotate credentials regularly
- Use secrets management (Vault, Kubernetes secrets)

## Troubleshooting

### NSC Command Not Found

```bash
# Install NSC
curl -L https://raw.githubusercontent.com/nats-io/nsc/master/install.sh | sh

# Add to PATH
export PATH=$PATH:$HOME/.local/bin

# Verify
nsc --version
```

### Permission Denied

```bash
# Make script executable
chmod +x generate-nkeys.sh

# Run script
./generate-nkeys.sh
```

### Directory Already Exists

The script will skip existing operators, accounts, and users. To regenerate:

```bash
# Remove existing NKeys
rm -rf /home/user/sahool-unified-v15-idp/config/nats/nkeys

# Run script again
./generate-nkeys.sh
```

## Documentation

For comprehensive documentation, see:
- [NATS NKey Setup Guide](../../docs/NATS_NKEY_SETUP.md)
- [NATS Official Documentation](https://docs.nats.io/)

## Support

For issues or questions, check:
1. Generated setup summary: `config/nats/generated/SETUP_SUMMARY.md`
2. NATS documentation: https://docs.nats.io/
3. NSC documentation: https://docs.nats.io/running-a-nats-service/configuration/securing_nats/auth_intro/nsc
