#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Secure Environment Generator
# منصة سهول - مولد البيئة الآمنة
# ═══════════════════════════════════════════════════════════════════════════════
#
# This script generates a secure .env file with random passwords
# Usage: ./scripts/security/generate-env.sh
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SAHOOL Platform - Secure Environment Generator${NC}"
echo -e "${BLUE}مولد البيئة الآمنة لمنصة سهول${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file already exists!${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Aborted. Existing .env file preserved.${NC}"
        exit 1
    fi
    # Backup existing .env
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✅ Backed up existing .env file${NC}"
fi

# Function to generate secure random password
generate_password() {
    local length=$1
    openssl rand -base64 $length | tr -d "=+/" | cut -c1-$length
}

# Generate secure passwords
echo -e "${BLUE}🔐 Generating secure passwords...${NC}"
POSTGRES_PASSWORD=$(generate_password 32)
REDIS_PASSWORD=$(generate_password 32)
JWT_SECRET=$(generate_password 64)
MQTT_PASSWORD=$(generate_password 32)

# Get environment type
echo ""
echo -e "${YELLOW}Select environment type:${NC}"
echo "1) development (localhost origins allowed)"
echo "2) staging"
echo "3) production (strict security)"
read -p "Enter choice (1-3): " env_choice

case $env_choice in
    1)
        ENVIRONMENT="development"
        ALLOWED_ORIGINS="http://localhost:3000,http://localhost:3001,http://localhost:8080"
        ;;
    2)
        ENVIRONMENT="staging"
        ALLOWED_ORIGINS="https://staging-admin.sahool.io,https://staging-app.sahool.io"
        ;;
    3)
        ENVIRONMENT="production"
        ALLOWED_ORIGINS="https://admin.sahool.io,https://app.sahool.io,https://dashboard.sahool.io"
        ;;
    *)
        echo -e "${RED}❌ Invalid choice. Defaulting to development.${NC}"
        ENVIRONMENT="development"
        ALLOWED_ORIGINS="http://localhost:3000,http://localhost:3001"
        ;;
esac

# Create .env file
echo -e "${BLUE}📝 Creating .env file...${NC}"

cat > .env << EOF
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform - Environment Variables
# Generated on $(date)
# ═══════════════════════════════════════════════════════════════════════════════

# Environment Configuration
ENVIRONMENT=${ENVIRONMENT}

# PostgreSQL Database Configuration
POSTGRES_USER=sahool
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=sahool
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis Cache Configuration
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# JWT Authentication Configuration
JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=60
JWT_REFRESH_EXPIRY_DAYS=30

# CORS Configuration
ALLOWED_ORIGINS=${ALLOWED_ORIGINS}

# API Gateway Configuration
API_BASE_URL=http://localhost:8000
API_VERSION=v1

# NATS Message Broker Configuration
NATS_URL=nats://nats:4222
NATS_CLUSTER_ID=sahool-cluster
NATS_CLIENT_ID=sahool-client

# MQTT IoT Configuration
MQTT_HOST=mqtt
MQTT_PORT=1883
MQTT_USERNAME=sahool
MQTT_PASSWORD=${MQTT_PASSWORD}

# External API Keys (Fill these manually)
OPENWEATHER_API_KEY=your_api_key_here
SENTINEL_HUB_CLIENT_ID=your_client_id_here
SENTINEL_HUB_CLIENT_SECRET=your_client_secret_here

# AWS Configuration (Optional)
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
AWS_S3_BUCKET=sahool-uploads

# Logging Configuration
LOG_LEVEL=INFO

# Monitoring Configuration
PROMETHEUS_ENABLED=true
METRICS_PORT=9090

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
SMTP_FROM_EMAIL=noreply@sahool.io
SMTP_FROM_NAME=Sahool Platform

# Feature Flags
FEATURE_AI_DIAGNOSIS=true
FEATURE_MARKETPLACE=true
FEATURE_OFFLINE_SYNC=true
EOF

# Set proper permissions
chmod 600 .env

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ .env file created successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📋 Generated credentials (first 8 characters shown):${NC}"
echo -e "  PostgreSQL Password: ${POSTGRES_PASSWORD:0:8}...****"
echo -e "  Redis Password:      ${REDIS_PASSWORD:0:8}...****"
echo -e "  JWT Secret:          ${JWT_SECRET:0:8}...****"
echo -e "  MQTT Password:       ${MQTT_PASSWORD:0:8}...****"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT SECURITY REMINDERS:${NC}"
echo -e "  1. ${RED}NEVER${NC} commit the .env file to version control"
echo -e "  2. Keep this file secure with proper permissions (chmod 600)"
echo -e "  3. Update external API keys manually in the .env file"
echo -e "  4. For production, consider using a secret management service"
echo -e "  5. Rotate passwords regularly (every 90 days recommended)"
echo ""
echo -e "${GREEN}🚀 You can now start the platform with: docker-compose up -d${NC}"
echo ""
