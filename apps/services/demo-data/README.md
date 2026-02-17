# Demo Data Service - خدمة البيانات التجريبية

## Overview

The Demo Data Service generates realistic demonstration data by sending HTTP requests to SAHOOL platform APIs, creating a lifelike demo environment for testing and presentations.

## Features

- Simulates real-world agricultural data (fields, weather, sensors, crops)
- Sends data to platform APIs via Kong gateway
- Supports multiple modes: continuous, once, batch
- Configurable interval and tenant context

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `KONG_URL` | `http://kong:8000` | Kong API gateway URL |
| `API_KEY` | `demo-api-key` | API authentication key |
| `TENANT_ID` | (uuid) | Target tenant ID |
| `USER_ID` | (uuid) | Demo user ID |
| `INTERVAL_SECONDS` | `30` | Data generation interval |
| `DEMO_MODE` | `continuous` | Mode: continuous, once, batch |
| `PORT` | `8261` | Service port |

## Usage

```bash
# Start with Docker
docker compose up demo-data

# Or run directly
python main.py
```

## Port

**8261**

## Version

16.0.0
