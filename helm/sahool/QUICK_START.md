# SAHOOL Helm Chart - Quick Start Guide

# دليل البدء السريع لمخطط Helm

## Prerequisites | المتطلبات

```bash
# Verify Kubernetes
kubectl version

# Verify Helm
helm version
```

## Step 1: Create Secrets | إنشاء الأسرار

```bash
# PostgreSQL
kubectl create secret generic sahool-postgresql-secret \
  --from-literal=password='ChangeMe123!' \
  -n sahool

# Redis
kubectl create secret generic sahool-redis-secret \
  --from-literal=redis-password='ChangeMe456!' \
  -n sahool

# JWT Secret (min 32 characters)
kubectl create secret generic sahool-jwt-secret \
  --from-literal=secret-key='your-very-long-jwt-secret-key-min-32-characters' \
  -n sahool

# Database URL
kubectl create secret generic sahool-database-secret \
  --from-literal=url='postgresql://sahool:ChangeMe123!@sahool-postgresql:5432/sahool' \
  -n sahool
```

## Step 2: Deploy SAHOOL | نشر سهول

### Option A: Starter Package (Recommended for Testing)

```bash
# Create namespace
kubectl create namespace sahool

# Install
helm install sahool /home/user/sahool-unified-v15-idp/helm/sahool \
  --set packageTier=starter \
  --namespace sahool

# Watch deployment
kubectl get pods -n sahool -w
```

### Option B: Professional Package (Staging)

```bash
kubectl create namespace sahool-staging

helm install sahool /home/user/sahool-unified-v15-idp/helm/sahool \
  --values /home/user/sahool-unified-v15-idp/helm/sahool/values-staging.yaml \
  --namespace sahool-staging

kubectl get pods -n sahool-staging -w
```

### Option C: Enterprise Package (Production)

```bash
kubectl create namespace sahool-prod

helm install sahool /home/user/sahool-unified-v15-idp/helm/sahool \
  --values /home/user/sahool-unified-v15-idp/helm/sahool/values-production.yaml \
  --namespace sahool-prod

kubectl get pods -n sahool-prod -w
```

## Step 3: Verify Deployment | التحقق من النشر

```bash
# Check all resources
kubectl get all -n sahool

# Check services
kubectl get svc -n sahool

# Check ingress
kubectl get ingress -n sahool

# Check logs
kubectl logs -l app.kubernetes.io/name=sahool -n sahool --tail=50
```

## Step 4: Access Services | الوصول إلى الخدمات

### Port Forward (for testing)

```bash
# Field Core
kubectl port-forward svc/sahool-field-core 3000:3000 -n sahool

# Weather Core
kubectl port-forward svc/sahool-weather-core 8108:8108 -n sahool

# Kong Admin
kubectl port-forward svc/sahool-kong-admin 8001:8001 -n sahool
```

### Via Ingress (production)

```bash
# Get ingress IP
kubectl get ingress sahool -n sahool

# Add to /etc/hosts
echo "<INGRESS-IP> api.sahool.ag" | sudo tee -a /etc/hosts

# Access
curl https://api.sahool.ag/api/v1/fields/health
```

## Step 5: Monitor | المراقبة

```bash
# Pod status
kubectl get pods -n sahool

# Resource usage
kubectl top pods -n sahool
kubectl top nodes

# Events
kubectl get events -n sahool --sort-by='.lastTimestamp'

# Logs
kubectl logs -f deployment/sahool-field-core -n sahool
```

## Troubleshooting | استكشاف الأخطاء

### Pods not starting

```bash
# Describe pod
kubectl describe pod <pod-name> -n sahool

# Check events
kubectl get events -n sahool | grep Error

# Check logs
kubectl logs <pod-name> -n sahool
```

### Database connection issues

```bash
# Test PostgreSQL connection
kubectl exec -it deployment/sahool-field-core -n sahool -- sh
# Inside pod:
psql $DATABASE_URL -c "SELECT version();"
```

### Secret issues

```bash
# List secrets
kubectl get secrets -n sahool

# Verify secret
kubectl get secret sahool-postgresql-secret -n sahool -o yaml
```

## Upgrade | الترقية

```bash
# Upgrade to Professional
helm upgrade sahool /home/user/sahool-unified-v15-idp/helm/sahool \
  --set packageTier=professional \
  --namespace sahool

# Upgrade to Enterprise
helm upgrade sahool /home/user/sahool-unified-v15-idp/helm/sahool \
  --values /home/user/sahool-unified-v15-idp/helm/sahool/values-production.yaml \
  --namespace sahool
```

## Uninstall | إلغاء التثبيت

```bash
# Uninstall
helm uninstall sahool -n sahool

# Delete PVCs (optional - deletes data!)
kubectl delete pvc -l app.kubernetes.io/instance=sahool -n sahool

# Delete namespace
kubectl delete namespace sahool
```

## Common Commands | الأوامر الشائعة

```bash
# List releases
helm list -n sahool

# Get values
helm get values sahool -n sahool

# Get manifest
helm get manifest sahool -n sahool

# Helm history
helm history sahool -n sahool

# Rollback
helm rollback sahool 1 -n sahool
```

## Service Endpoints | نقاط النهاية

| Service       | Port | Path                  |
| ------------- | ---- | --------------------- |
| Field Core    | 3000 | /api/v1/fields        |
| Weather Core  | 8108 | /api/v1/weather       |
| Agro Advisor  | 8105 | /api/v1/advisory      |
| Notifications | 8110 | /api/v1/notifications |
| Kong Admin    | 8001 | /admin                |
| Kong Proxy    | 8000 | /                     |

## Support | الدعم

- Documentation: `/home/user/sahool-unified-v15-idp/helm/sahool/README.md`
- Summary: `/home/user/sahool-unified-v15-idp/helm/HELM_CHART_SUMMARY.md`
- Issues: https://github.com/sahool/platform/issues

---

Made with ❤️ for SAHOOL Platform
