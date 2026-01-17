# SAHOOL Platform - Environment Variables Guide

## Overview

This document describes all environment variables used by the SAHOOL Platform.
Always keep `.env.example` in sync with this documentation.

## Quick Start

```bash
# Copy example to .env
cp .env.example .env

# Edit with your values
nano .env

# Validate configuration
make env-check
```

## Variable Categories

### 1. Application Core

| Variable         | Required | Default       | Description                                         |
| ---------------- | -------- | ------------- | --------------------------------------------------- |
| `APP_ENV`        | Yes      | `development` | Environment: `development`, `staging`, `production` |
| `APP_DEBUG`      | No       | `true`        | Enable debug mode (disable in production!)          |
| `APP_SECRET_KEY` | Yes      | -             | Application secret for encryption                   |
| `APP_HOST`       | No       | `0.0.0.0`     | Server bind address                                 |
| `APP_PORT`       | No       | `8000`        | Server port                                         |

### 2. Database (PostgreSQL)

| Variable       | Required | Default     | Description                      |
| -------------- | -------- | ----------- | -------------------------------- |
| `DATABASE_URL` | Yes      | -           | Full database connection URL     |
| `DB_HOST`      | No       | `localhost` | Database host (if not using URL) |
| `DB_PORT`      | No       | `5432`      | Database port                    |
| `DB_NAME`      | No       | `sahool`    | Database name                    |
| `DB_USER`      | No       | `sahool`    | Database user                    |
| `DB_PASSWORD`  | Yes      | -           | Database password                |

### 3. Redis Cache

| Variable     | Required | Default                    | Description          |
| ------------ | -------- | -------------------------- | -------------------- |
| `REDIS_URL`  | No       | `redis://localhost:6379/0` | Redis connection URL |
| `REDIS_HOST` | No       | `localhost`                | Redis host           |
| `REDIS_PORT` | No       | `6379`                     | Redis port           |

### 4. NATS Messaging

| Variable          | Required | Default          | Description             |
| ----------------- | -------- | ---------------- | ----------------------- |
| `NATS_URL`        | Yes      | -                | NATS server URL         |
| `NATS_CLUSTER_ID` | No       | `sahool-cluster` | NATS cluster identifier |

### 5. Authentication

| Variable                 | Required | Default | Description                             |
| ------------------------ | -------- | ------- | --------------------------------------- |
| `JWT_SECRET`             | Yes      | -       | JWT signing secret (min 32 chars)       |
| `JWT_ALGORITHM`          | No       | `HS256` | JWT algorithm                           |
| `JWT_EXPIRATION_HOURS`   | No       | `24`    | Token validity period                   |
| `OTP_LENGTH`             | No       | `4`     | OTP code length                         |
| `OTP_EXPIRATION_MINUTES` | No       | `5`     | OTP validity period                     |
| `SMS_PROVIDER`           | No       | `mock`  | SMS provider: `mock`, `twilio`, `nexmo` |

### 6. External APIs

| Variable            | Required | Default | Description                   |
| ------------------- | -------- | ------- | ----------------------------- |
| `WEATHER_API_KEY`   | No       | -       | Weather service API key       |
| `SATELLITE_API_KEY` | No       | -       | Satellite imagery API key     |
| `OPENAI_API_KEY`    | No       | -       | OpenAI API key for AI Advisor |

### 7. Storage

| Variable          | Required | Default | Description            |
| ----------------- | -------- | ------- | ---------------------- |
| `STORAGE_BACKEND` | No       | `local` | Storage: `local`, `s3` |
| `S3_BUCKET`       | If S3    | -       | S3 bucket name         |
| `S3_REGION`       | If S3    | -       | AWS region             |
| `S3_ACCESS_KEY`   | If S3    | -       | AWS access key         |
| `S3_SECRET_KEY`   | If S3    | -       | AWS secret key         |

### 8. Monitoring

| Variable             | Required | Default | Description               |
| -------------------- | -------- | ------- | ------------------------- |
| `LOG_LEVEL`          | No       | `INFO`  | Logging level             |
| `SENTRY_DSN`         | No       | -       | Sentry error tracking DSN |
| `PROMETHEUS_ENABLED` | No       | `true`  | Enable metrics endpoint   |
| `PROMETHEUS_PORT`    | No       | `9090`  | Metrics port              |

### 9. Feature Flags

| Variable               | Required | Default | Description                 |
| ---------------------- | -------- | ------- | --------------------------- |
| `FEATURE_AI_ADVISOR`   | No       | `true`  | Enable AI Advisor feature   |
| `FEATURE_MARKETPLACE`  | No       | `true`  | Enable Marketplace feature  |
| `FEATURE_OFFLINE_SYNC` | No       | `true`  | Enable offline sync feature |

## Environment-Specific Settings

### Development

```bash
APP_ENV=development
APP_DEBUG=true
LOG_LEVEL=DEBUG
SMS_PROVIDER=mock
```

### Staging

```bash
APP_ENV=staging
APP_DEBUG=false
LOG_LEVEL=INFO
SMS_PROVIDER=twilio
```

### Production

```bash
APP_ENV=production
APP_DEBUG=false
LOG_LEVEL=WARNING
SMS_PROVIDER=twilio
SENTRY_DSN=https://...
```

## Security Notes

1. **Never commit `.env` files** - They are in `.gitignore`
2. **Use strong secrets** - Minimum 32 characters for keys
3. **Rotate secrets regularly** - Especially after team changes
4. **Use different secrets per environment**
5. **Validate before deploy** - Run `make env-check`

## Validation

The platform validates environment variables on startup.
Run manual validation with:

```bash
# Check all required variables
make env-check

# Scan for undocumented ENV usage
make env-scan
```

## Adding New Variables

1. Add to `.env.example` with a placeholder
2. Document in this file
3. Add to `tools/env/required_env.json` if required
4. Update `tools/env/validate_env.py` if needed
5. Run `make env-scan` to verify no drift
