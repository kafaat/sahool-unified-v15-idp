#!/bin/bash

# SAHOOL Notification Service - Development Startup Script
# سكريبت بدء التطوير لخدمة الإشعارات

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   SAHOOL Notification Service - Development Setup         ║"
echo "║   خدمة الإشعارات - إعداد التطوير                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Start PostgreSQL and Redis
echo -e "${YELLOW}📦 Starting PostgreSQL and Redis...${NC}"
docker-compose -f docker-compose.dev.yml up -d postgres redis

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}⏳ Waiting for PostgreSQL to be ready...${NC}"
sleep 5

until docker exec sahool-notification-db pg_isready -U sahool -d sahool_notifications > /dev/null 2>&1; do
    echo -e "${YELLOW}   Waiting for PostgreSQL...${NC}"
    sleep 2
done

echo -e "${GREEN}✅ PostgreSQL is ready!${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
pip install -r requirements.txt

# Load environment variables
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Loading environment from .env${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}⚠️  No .env file found. Using defaults.${NC}"
    echo -e "${YELLOW}   Creating .env from .env.example...${NC}"
    cp .env.example .env
    export $(cat .env | grep -v '^#' | xargs)
fi

# Initialize database
echo -e "${YELLOW}🗄️  Checking database initialization...${NC}"

# Check if migrations directory exists
if [ ! -d "migrations" ]; then
    echo -e "${YELLOW}🔧 Initializing Aerich...${NC}"
    aerich init -t src.database.TORTOISE_ORM_LOCAL || true

    echo -e "${YELLOW}🔧 Creating initial migration...${NC}"
    aerich init-db
else
    echo -e "${GREEN}✅ Migrations directory exists. Running migrations...${NC}"
    aerich upgrade
fi

# Run database health check
echo -e "${YELLOW}🏥 Checking database health...${NC}"
python init_db.py --check

# Display connection info
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Development Environment Ready!                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}📊 Database:${NC}"
echo "   PostgreSQL: postgresql://sahool:sahool123@localhost:5432/sahool_notifications"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: sahool_notifications"
echo "   User: sahool"
echo ""

echo -e "${GREEN}🔴 Redis:${NC}"
echo "   URL: redis://localhost:6379/0"
echo ""

echo -e "${GREEN}🌐 pgAdmin (Optional):${NC}"
echo "   To start: docker-compose -f docker-compose.dev.yml --profile tools up -d pgadmin"
echo "   URL: http://localhost:5050"
echo "   Email: admin@sahool.com"
echo "   Password: admin123"
echo ""

echo -e "${GREEN}🚀 Starting Notification Service...${NC}"
echo -e "${YELLOW}   Service will start on http://localhost:8110${NC}"
echo -e "${YELLOW}   API Docs: http://localhost:8110/docs${NC}"
echo -e "${YELLOW}   Health Check: http://localhost:8110/healthz${NC}"
echo ""

# Start the service
echo -e "${GREEN}▶️  Starting service... (Press Ctrl+C to stop)${NC}"
python -m uvicorn src.main:app --host 0.0.0.0 --port 8110 --reload

# Cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down...${NC}"
    deactivate 2>/dev/null || true
    echo -e "${GREEN}✅ Done!${NC}"
}

trap cleanup EXIT
