#!/bin/bash
# SAHOOL Infrastructure Setup Script
# Sets up Kubernetes secrets and deploys infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default values
NAMESPACE="${NAMESPACE:-sahool-staging}"
ENVIRONMENT="${ENVIRONMENT:-staging}"

echo -e "${GREEN}SAHOOL Infrastructure Setup${NC}"
echo "Environment: $ENVIRONMENT"
echo "Namespace: $NAMESPACE"

# Create namespace
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Create secrets (prompts for values or uses env vars)
create_secrets() {
    echo -e "${YELLOW}Creating secrets...${NC}"

    # PostgreSQL secret
    POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-$(openssl rand -base64 32)}"
    kubectl create secret generic sahool-postgresql-secret \
        --namespace=$NAMESPACE \
        --from-literal=postgres-password="$POSTGRES_PASSWORD" \
        --from-literal=password="$POSTGRES_PASSWORD" \
        --dry-run=client -o yaml | kubectl apply -f -

    # Redis secret
    REDIS_PASSWORD="${REDIS_PASSWORD:-$(openssl rand -base64 32)}"
    kubectl create secret generic sahool-redis-secret \
        --namespace=$NAMESPACE \
        --from-literal=redis-password="$REDIS_PASSWORD" \
        --dry-run=client -o yaml | kubectl apply -f -

    # JWT secret
    JWT_SECRET="${JWT_SECRET:-$(openssl rand -base64 64)}"
    kubectl create secret generic sahool-jwt-secret \
        --namespace=$NAMESPACE \
        --from-literal=jwt-secret="$JWT_SECRET" \
        --dry-run=client -o yaml | kubectl apply -f -

    echo -e "${GREEN}Secrets created successfully${NC}"
}

# Deploy infrastructure with Helm
deploy_infra() {
    echo -e "${YELLOW}Deploying infrastructure...${NC}"

    helm upgrade --install sahool-infra ./helm/infra \
        --namespace $NAMESPACE \
        --set environment=$ENVIRONMENT \
        --wait \
        --timeout 10m

    echo -e "${GREEN}Infrastructure deployed successfully${NC}"
}

# Main
create_secrets
deploy_infra

echo -e "${GREEN}Setup complete!${NC}"
