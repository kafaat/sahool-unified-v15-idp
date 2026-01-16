# SAHOOL Infrastructure Documentation

## Overview

The SAHOOL Unified Platform infrastructure is designed for cloud-native deployment using Kubernetes, with support for multiple environments (staging, production). The infrastructure consists of:

- **PostgreSQL Database** - Primary data storage for all services
- **Redis Cache** - Session management, caching, and pub/sub
- **Microservices** - Domain-driven services (IDP, Inventory, CMS, etc.)
- **Gateway** - API Gateway for routing and authentication
- **Frontend** - Next.js web application

## Architecture

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Ingress Layer"
            INGRESS[Ingress Controller]
        end

        subgraph "Application Layer"
            GATEWAY[API Gateway]
            FRONTEND[Frontend Service]
            IDP[IDP Service]
            INVENTORY[Inventory Service]
            CMS[CMS Service]
            COMMUNICATION[Communication Service]
        end

        subgraph "Data Layer"
            POSTGRES[(PostgreSQL)]
            REDIS[(Redis)]
        end

        subgraph "External Services"
            OPENWEATHER[OpenWeather API]
            SENTINEL[Sentinel Hub]
            STRIPE[Stripe]
            SLACK[Slack]
        end
    end

    INGRESS --> GATEWAY
    INGRESS --> FRONTEND
    GATEWAY --> IDP
    GATEWAY --> INVENTORY
    GATEWAY --> CMS
    GATEWAY --> COMMUNICATION

    IDP --> POSTGRES
    INVENTORY --> POSTGRES
    CMS --> POSTGRES
    COMMUNICATION --> POSTGRES

    GATEWAY --> REDIS
    IDP --> REDIS

    INVENTORY --> OPENWEATHER
    INVENTORY --> SENTINEL
    IDP --> STRIPE
    COMMUNICATION --> SLACK
```

## Prerequisites

### Required Tools

- **kubectl** (v1.24+) - Kubernetes command-line tool
- **helm** (v3.10+) - Kubernetes package manager
- **docker** (v20.10+) - Container runtime
- **openssl** - For generating secrets
- **git** - Version control

### Installation

```bash
# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### Cluster Access

You need access to a Kubernetes cluster. Supported providers:

- Google Kubernetes Engine (GKE)
- Amazon Elastic Kubernetes Service (EKS)
- Azure Kubernetes Service (AKS)
- DigitalOcean Kubernetes
- Self-hosted Kubernetes

Verify cluster access:

```bash
kubectl cluster-info
kubectl get nodes
```

## Required Secrets

### Kubernetes Secrets

The following secrets must be configured in your Kubernetes cluster:

#### 1. PostgreSQL Secret (`sahool-postgresql-secret`)

- **postgres-password** - PostgreSQL admin password
- **password** - Application user password

```bash
kubectl create secret generic sahool-postgresql-secret \
  --namespace=sahool-staging \
  --from-literal=postgres-password=<STRONG_PASSWORD> \
  --from-literal=password=<STRONG_PASSWORD>
```

#### 2. Redis Secret (`sahool-redis-secret`)

- **redis-password** - Redis authentication password

```bash
kubectl create secret generic sahool-redis-secret \
  --namespace=sahool-staging \
  --from-literal=redis-password=<STRONG_PASSWORD>
```

#### 3. JWT Secret (`sahool-jwt-secret`)

- **jwt-secret** - Secret key for JWT token signing

```bash
JWT_SECRET=$(openssl rand -base64 64)
kubectl create secret generic sahool-jwt-secret \
  --namespace=sahool-staging \
  --from-literal=jwt-secret="$JWT_SECRET"
```

#### 4. External API Secrets

**OpenWeather API:**

```bash
kubectl create secret generic sahool-openweather-secret \
  --namespace=sahool-staging \
  --from-literal=api-key=<YOUR_OPENWEATHER_API_KEY>
```

**Sentinel Hub:**

```bash
kubectl create secret generic sahool-sentinel-secret \
  --namespace=sahool-staging \
  --from-literal=client-id=<YOUR_CLIENT_ID> \
  --from-literal=client-secret=<YOUR_CLIENT_SECRET>
```

**Stripe:**

```bash
kubectl create secret generic sahool-stripe-secret \
  --namespace=sahool-staging \
  --from-literal=secret-key=<YOUR_STRIPE_SECRET_KEY>
```

**Slack Webhook:**

```bash
kubectl create secret generic sahool-slack-secret \
  --namespace=sahool-staging \
  --from-literal=webhook-url=<YOUR_SLACK_WEBHOOK_URL>
```

### GitHub Secrets (for CI/CD)

The following secrets must be added to your GitHub repository:

| Secret Name              | Description                                      | Required For           |
| ------------------------ | ------------------------------------------------ | ---------------------- |
| `KUBE_CONFIG_STAGING`    | Base64 encoded kubeconfig for staging cluster    | Staging deployments    |
| `KUBE_CONFIG_PRODUCTION` | Base64 encoded kubeconfig for production cluster | Production deployments |
| `POSTGRES_PASSWORD`      | PostgreSQL password                              | Database setup         |
| `REDIS_PASSWORD`         | Redis password                                   | Cache setup            |
| `JWT_SECRET`             | JWT signing secret                               | Authentication         |
| `OPENWEATHER_API_KEY`    | OpenWeather API key                              | Weather data           |
| `SENTINEL_HUB_ID`        | Sentinel Hub client ID                           | Satellite imagery      |
| `SENTINEL_HUB_SECRET`    | Sentinel Hub client secret                       | Satellite imagery      |
| `STRIPE_SECRET_KEY`      | Stripe secret key                                | Payment processing     |
| `SLACK_WEBHOOK_URL`      | Slack webhook URL                                | Notifications          |

See [SECRETS_SETUP.md](./SECRETS_SETUP.md) for detailed instructions on setting up GitHub secrets.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd sahool-unified-v15-idp
```

### 2. Configure Environment

Set environment variables for your target environment:

**For Staging:**

```bash
export NAMESPACE=sahool-staging
export ENVIRONMENT=staging
```

**For Production:**

```bash
export NAMESPACE=sahool-production
export ENVIRONMENT=production
```

### 3. Generate Secrets

You can either:

**A. Auto-generate secure secrets:**

```bash
export POSTGRES_PASSWORD=$(openssl rand -base64 32)
export REDIS_PASSWORD=$(openssl rand -base64 32)
export JWT_SECRET=$(openssl rand -base64 64)
```

**B. Use existing secrets:**

```bash
export POSTGRES_PASSWORD="your-existing-password"
export REDIS_PASSWORD="your-existing-password"
export JWT_SECRET="your-existing-jwt-secret"
```

### 4. Run Infrastructure Setup

```bash
# Make script executable
chmod +x scripts/setup-infrastructure.sh

# Run setup
./scripts/setup-infrastructure.sh
```

This script will:

1. Create the Kubernetes namespace
2. Create all required secrets
3. Deploy infrastructure using Helm

### 5. Verify Deployment

```bash
# Check all resources
kubectl get all -n $NAMESPACE

# Check secrets
kubectl get secrets -n $NAMESPACE

# Check PostgreSQL
kubectl get pods -n $NAMESPACE -l app=postgresql

# Check Redis
kubectl get pods -n $NAMESPACE -l app=redis

# View logs
kubectl logs -n $NAMESPACE -l app=postgresql --tail=50
kubectl logs -n $NAMESPACE -l app=redis --tail=50
```

### 6. Deploy Services

After infrastructure is ready, deploy the services:

```bash
# Deploy using Helm
helm upgrade --install sahool-services ./helm/services \
  --namespace $NAMESPACE \
  --set environment=$ENVIRONMENT \
  --wait \
  --timeout 10m
```

Or use GitHub Actions for automated deployment (push to main or staging branch).

## Configuration

### Helm Values

The infrastructure can be customized using Helm values:

**values-staging.yaml:**

```yaml
environment: staging
namespace: sahool-staging

postgresql:
  enabled: true
  auth:
    existingSecret: sahool-postgresql-secret
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

redis:
  enabled: true
  auth:
    existingSecret: sahool-redis-secret
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

**values-production.yaml:**

```yaml
environment: production
namespace: sahool-production

postgresql:
  enabled: true
  auth:
    existingSecret: sahool-postgresql-secret
  resources:
    requests:
      memory: "1Gi"
      cpu: "1000m"
    limits:
      memory: "4Gi"
      cpu: "2000m"
  replication:
    enabled: true
    readReplicas: 2

redis:
  enabled: true
  auth:
    existingSecret: sahool-redis-secret
  master:
    resources:
      requests:
        memory: "512Mi"
        cpu: "500m"
      limits:
        memory: "2Gi"
        cpu: "1000m"
  replica:
    replicaCount: 2
    resources:
      requests:
        memory: "512Mi"
        cpu: "500m"
      limits:
        memory: "2Gi"
        cpu: "1000m"
```

### Environment Variables

Each service can be configured with environment variables in Helm values:

```yaml
services:
  idp:
    env:
      NODE_ENV: production
      PORT: "3000"
      LOG_LEVEL: info
      DATABASE_URL: postgresql://user:pass@postgres:5432/sahool_idp
      REDIS_URL: redis://:pass@redis:6379
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check pod health
kubectl get pods -n $NAMESPACE

# Check pod details
kubectl describe pod <pod-name> -n $NAMESPACE

# Check service endpoints
kubectl get endpoints -n $NAMESPACE
```

### Logs

```bash
# View logs for a service
kubectl logs -n $NAMESPACE -l app=idp-service --tail=100 -f

# View logs for specific pod
kubectl logs -n $NAMESPACE <pod-name> -f

# View logs from all containers in a pod
kubectl logs -n $NAMESPACE <pod-name> --all-containers -f
```

### Database Maintenance

```bash
# Connect to PostgreSQL
kubectl exec -it -n $NAMESPACE <postgres-pod-name> -- psql -U postgres

# Backup database
kubectl exec -n $NAMESPACE <postgres-pod-name> -- pg_dump -U postgres sahool_idp > backup.sql

# Restore database
kubectl exec -i -n $NAMESPACE <postgres-pod-name> -- psql -U postgres sahool_idp < backup.sql
```

### Redis Maintenance

```bash
# Connect to Redis
kubectl exec -it -n $NAMESPACE <redis-pod-name> -- redis-cli -a <password>

# Check Redis stats
kubectl exec -it -n $NAMESPACE <redis-pod-name> -- redis-cli -a <password> INFO

# Flush cache (use with caution)
kubectl exec -it -n $NAMESPACE <redis-pod-name> -- redis-cli -a <password> FLUSHALL
```

## Troubleshooting

### Pods Not Starting

**Symptom:** Pods in `Pending` or `CrashLoopBackOff` state

**Solutions:**

```bash
# Check pod events
kubectl describe pod <pod-name> -n $NAMESPACE

# Check logs
kubectl logs <pod-name> -n $NAMESPACE --previous

# Check resource availability
kubectl top nodes
kubectl describe nodes
```

### Database Connection Issues

**Symptom:** Services can't connect to PostgreSQL

**Solutions:**

```bash
# Verify PostgreSQL is running
kubectl get pods -n $NAMESPACE -l app=postgresql

# Check PostgreSQL logs
kubectl logs -n $NAMESPACE -l app=postgresql

# Test connection from a pod
kubectl run -it --rm debug --image=postgres:14 --restart=Never -n $NAMESPACE -- \
  psql -h sahool-postgresql -U postgres

# Verify secret exists
kubectl get secret sahool-postgresql-secret -n $NAMESPACE
```

### Redis Connection Issues

**Symptom:** Services can't connect to Redis

**Solutions:**

```bash
# Verify Redis is running
kubectl get pods -n $NAMESPACE -l app=redis

# Check Redis logs
kubectl logs -n $NAMESPACE -l app=redis

# Test connection
kubectl run -it --rm debug --image=redis:7 --restart=Never -n $NAMESPACE -- \
  redis-cli -h sahool-redis -a <password> PING

# Verify secret exists
kubectl get secret sahool-redis-secret -n $NAMESPACE
```

### Ingress Issues

**Symptom:** Can't access services externally

**Solutions:**

```bash
# Check ingress
kubectl get ingress -n $NAMESPACE
kubectl describe ingress <ingress-name> -n $NAMESPACE

# Verify ingress controller
kubectl get pods -n ingress-nginx

# Check service endpoints
kubectl get endpoints -n $NAMESPACE
```

### Image Pull Errors

**Symptom:** `ImagePullBackOff` or `ErrImagePull`

**Solutions:**

```bash
# Check image name and tag
kubectl describe pod <pod-name> -n $NAMESPACE

# Verify image exists in registry
docker pull <image-name>

# Check image pull secrets
kubectl get secrets -n $NAMESPACE
```

### Resource Exhaustion

**Symptom:** Pods evicted or nodes under pressure

**Solutions:**

```bash
# Check node resources
kubectl top nodes
kubectl describe nodes

# Check pod resources
kubectl top pods -n $NAMESPACE

# Adjust resource limits in Helm values
helm upgrade sahool-infra ./helm/infra \
  --namespace $NAMESPACE \
  --set postgresql.resources.limits.memory=2Gi
```

### Secret Issues

**Symptom:** Services can't access secrets

**Solutions:**

```bash
# List secrets
kubectl get secrets -n $NAMESPACE

# Verify secret content (base64 encoded)
kubectl get secret sahool-jwt-secret -n $NAMESPACE -o yaml

# Recreate secret
kubectl delete secret sahool-jwt-secret -n $NAMESPACE
kubectl create secret generic sahool-jwt-secret \
  --namespace=$NAMESPACE \
  --from-literal=jwt-secret="$(openssl rand -base64 64)"
```

## Scaling

### Horizontal Pod Autoscaling (HPA)

```bash
# Create HPA for a service
kubectl autoscale deployment idp-service \
  --namespace=$NAMESPACE \
  --cpu-percent=70 \
  --min=2 \
  --max=10

# Check HPA status
kubectl get hpa -n $NAMESPACE
```

### Manual Scaling

```bash
# Scale a deployment
kubectl scale deployment idp-service --replicas=5 -n $NAMESPACE

# Verify scaling
kubectl get pods -n $NAMESPACE -l app=idp-service
```

## Backup and Recovery

### Database Backup

```bash
# Manual backup
kubectl exec -n $NAMESPACE <postgres-pod-name> -- \
  pg_dumpall -U postgres > backup-$(date +%Y%m%d).sql

# Automated backup (using CronJob)
kubectl apply -f k8s/cronjobs/postgres-backup.yaml
```

### Disaster Recovery

```bash
# Restore from backup
kubectl exec -i -n $NAMESPACE <postgres-pod-name> -- \
  psql -U postgres < backup-20231215.sql

# Verify restoration
kubectl exec -it -n $NAMESPACE <postgres-pod-name> -- \
  psql -U postgres -c "SELECT count(*) FROM users;"
```

## Security Best Practices

1. **Secrets Management**
   - Never commit secrets to version control
   - Use strong, randomly generated passwords
   - Rotate secrets regularly
   - Use Kubernetes secrets or external secret managers

2. **Network Policies**
   - Implement network policies to restrict pod-to-pod communication
   - Use ingress rules to control external access

3. **RBAC**
   - Use Role-Based Access Control
   - Follow principle of least privilege
   - Regularly audit permissions

4. **Image Security**
   - Use official or verified base images
   - Scan images for vulnerabilities
   - Use specific image tags, not `latest`

5. **Resource Limits**
   - Always set resource requests and limits
   - Prevent resource exhaustion attacks
   - Monitor resource usage

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [SAHOOL API Documentation](./API.md)
- [SAHOOL Secrets Setup Guide](./SECRETS_SETUP.md)

## Support

For issues or questions:

- Open an issue on GitHub
- Contact the DevOps team
- Check the troubleshooting section above
