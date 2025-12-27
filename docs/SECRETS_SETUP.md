# GitHub Secrets Setup Guide

This guide provides step-by-step instructions for setting up all required secrets in your GitHub repository for the SAHOOL Unified Platform.

## Table of Contents

- [Overview](#overview)
- [GitHub Repository Secrets](#github-repository-secrets)
- [Kubernetes Configuration Secrets](#kubernetes-configuration-secrets)
- [Database Secrets](#database-secrets)
- [External API Secrets](#external-api-secrets)
- [Environment-Specific Secrets](#environment-specific-secrets)
- [Verification](#verification)

## Overview

GitHub Secrets are encrypted environment variables that you create in a repository. These secrets are used by GitHub Actions workflows to deploy and configure your application securely.

**Security Best Practices:**
- Never commit secrets to your repository
- Use strong, randomly generated passwords
- Rotate secrets regularly
- Use different secrets for staging and production
- Limit access to secrets to necessary team members

## GitHub Repository Secrets

### How to Add Secrets to GitHub

1. Navigate to your repository on GitHub
2. Click on **Settings** (top navigation)
3. In the left sidebar, click **Secrets and variables** > **Actions**
4. Click **New repository secret**
5. Enter the secret **Name** and **Value**
6. Click **Add secret**

### Required Secrets List

Below is a complete list of all required secrets for the SAHOOL platform:

| Secret Name | Description | Environment | Required |
|-------------|-------------|-------------|----------|
| `KUBE_CONFIG_STAGING` | Base64 encoded kubeconfig for staging cluster | Staging | Yes |
| `KUBE_CONFIG_PRODUCTION` | Base64 encoded kubeconfig for production cluster | Production | Yes |
| `POSTGRES_PASSWORD` | PostgreSQL database password | Both | Yes |
| `REDIS_PASSWORD` | Redis cache password | Both | Yes |
| `JWT_SECRET` | JWT token signing secret | Both | Yes |
| `OPENWEATHER_API_KEY` | OpenWeather API key for weather data | Both | Yes |
| `SENTINEL_HUB_ID` | Sentinel Hub client ID for satellite imagery | Both | Yes |
| `SENTINEL_HUB_SECRET` | Sentinel Hub client secret | Both | Yes |
| `STRIPE_SECRET_KEY` | Stripe payment processing secret key | Production | Yes |
| `STRIPE_TEST_SECRET_KEY` | Stripe test mode secret key | Staging | Optional |
| `SLACK_WEBHOOK_URL` | Slack webhook URL for notifications | Both | Optional |

## Kubernetes Configuration Secrets

### Generating Kubeconfig for CI/CD

The `KUBE_CONFIG_STAGING` and `KUBE_CONFIG_PRODUCTION` secrets contain base64-encoded Kubernetes configuration files that allow GitHub Actions to deploy to your clusters.

#### Method 1: Using the Provided Script

```bash
# Make the script executable
chmod +x scripts/generate-kubeconfig.sh

# Generate for staging
./scripts/generate-kubeconfig.sh --cluster staging --namespace sahool-staging

# Generate for production
./scripts/generate-kubeconfig.sh --cluster production --namespace sahool-production
```

The script will output:
- The base64 encoded kubeconfig
- Instructions for adding to GitHub
- Suggested secret name

#### Method 2: Manual Generation

**Step 1: Switch to the correct cluster context**
```bash
# For staging
kubectl config use-context staging-cluster

# For production
kubectl config use-context production-cluster
```

**Step 2: Generate kubeconfig file**
```bash
# Get current context config
kubectl config view --minify --flatten > kubeconfig-staging.yaml
```

**Step 3: Encode to base64**
```bash
# Linux/Mac
cat kubeconfig-staging.yaml | base64 -w 0 > kubeconfig-staging-base64.txt

# The content of kubeconfig-staging-base64.txt is your secret value
```

**Step 4: Add to GitHub**
- Secret Name: `KUBE_CONFIG_STAGING`
- Secret Value: Content of `kubeconfig-staging-base64.txt`

**Step 5: Clean up**
```bash
# Remove temporary files
rm kubeconfig-staging.yaml kubeconfig-staging-base64.txt
```

**Repeat for production:**
- Secret Name: `KUBE_CONFIG_PRODUCTION`

#### Verifying Kubeconfig

To verify your kubeconfig works:

```bash
# Decode and test
echo "<base64-string>" | base64 -d > test-kubeconfig.yaml
kubectl --kubeconfig=test-kubeconfig.yaml get nodes

# Clean up
rm test-kubeconfig.yaml
```

## Database Secrets

### PostgreSQL Password

Generate a strong PostgreSQL password:

```bash
# Generate a secure password
openssl rand -base64 32
```

**Add to GitHub:**
- Secret Name: `POSTGRES_PASSWORD`
- Secret Value: The generated password

**Important Notes:**
- Use the same password for both staging and production, OR
- Create separate secrets: `POSTGRES_PASSWORD_STAGING` and `POSTGRES_PASSWORD_PRODUCTION`
- Keep this password secure - it protects all your data
- Store it in a password manager as backup

### Redis Password

Generate a strong Redis password:

```bash
# Generate a secure password
openssl rand -base64 32
```

**Add to GitHub:**
- Secret Name: `REDIS_PASSWORD`
- Secret Value: The generated password

**Important Notes:**
- Redis password is used for cache authentication
- Can use separate passwords for staging/production if needed

### JWT Secret

Generate a JWT signing secret:

```bash
# Generate a secure JWT secret (longer for better security)
openssl rand -base64 64
```

**Add to GitHub:**
- Secret Name: `JWT_SECRET`
- Secret Value: The generated secret

**Important Notes:**
- This secret signs all authentication tokens
- **NEVER** share or expose this secret
- Changing this will invalidate all existing user sessions
- Use different secrets for staging and production

## External API Secrets

### OpenWeather API Key

**Obtaining the API Key:**

1. Visit [OpenWeather](https://openweathermap.org/)
2. Sign up for a free account
3. Navigate to API Keys section
4. Generate a new API key or use the default one
5. Wait for activation (can take up to 2 hours)

**Add to GitHub:**
- Secret Name: `OPENWEATHER_API_KEY`
- Secret Value: Your API key (e.g., `abc123def456...`)

**Usage Notes:**
- Free tier: 60 calls/minute, 1,000,000 calls/month
- Used for weather data in agricultural planning
- Same key can be used for staging and production

### Sentinel Hub Credentials

**Obtaining the Credentials:**

1. Visit [Sentinel Hub](https://www.sentinel-hub.com/)
2. Create an account
3. Navigate to Dashboard
4. Create a new OAuth client
5. Copy the Client ID and Client Secret

**Add to GitHub:**
- Secret Name: `SENTINEL_HUB_ID`
- Secret Value: Your client ID

- Secret Name: `SENTINEL_HUB_SECRET`
- Secret Value: Your client secret

**Usage Notes:**
- Used for satellite imagery and land analysis
- Free tier available with limited processing units
- Consider separate credentials for staging and production

### Stripe Secret Key

**Obtaining the Secret Key:**

1. Visit [Stripe Dashboard](https://dashboard.stripe.com/)
2. Sign up or log in
3. Navigate to Developers > API keys
4. Copy the **Secret key** (starts with `sk_`)

**For Production:**
- Use the **Live mode** secret key
- Secret Name: `STRIPE_SECRET_KEY`
- Secret Value: Your live secret key (e.g., `sk_live_...`)

**For Staging:**
- Use the **Test mode** secret key
- Secret Name: `STRIPE_TEST_SECRET_KEY`
- Secret Value: Your test secret key (e.g., `sk_test_...`)

**Important Notes:**
- **NEVER** expose the secret key in client-side code
- Use test mode for staging/development
- Monitor Stripe dashboard for suspicious activity
- Rotate keys if compromised

### Slack Webhook URL

**Creating a Webhook:**

1. Visit [Slack API](https://api.slack.com/apps)
2. Create a new app or select existing
3. Navigate to **Incoming Webhooks**
4. Activate incoming webhooks
5. Click **Add New Webhook to Workspace**
6. Select the channel for notifications
7. Copy the webhook URL

**Add to GitHub:**
- Secret Name: `SLACK_WEBHOOK_URL`
- Secret Value: Your webhook URL (e.g., `https://hooks.slack.com/services/...`)

**Usage Notes:**
- Used for deployment notifications and alerts
- Can use the same webhook for staging and production, OR
- Create separate webhooks: `SLACK_WEBHOOK_STAGING` and `SLACK_WEBHOOK_PRODUCTION`
- Test the webhook before deploying

**Testing the Webhook:**
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message from SAHOOL"}' \
  YOUR_WEBHOOK_URL
```

## Environment-Specific Secrets

### Staging Environment

For staging, you may want to use test/development versions of external services:

```
KUBE_CONFIG_STAGING=<base64-encoded-kubeconfig>
POSTGRES_PASSWORD=<staging-password>
REDIS_PASSWORD=<staging-password>
JWT_SECRET=<staging-jwt-secret>
OPENWEATHER_API_KEY=<api-key>
SENTINEL_HUB_ID=<staging-client-id>
SENTINEL_HUB_SECRET=<staging-client-secret>
STRIPE_TEST_SECRET_KEY=<stripe-test-key>
SLACK_WEBHOOK_URL=<staging-webhook>
```

### Production Environment

For production, use live/production credentials:

```
KUBE_CONFIG_PRODUCTION=<base64-encoded-kubeconfig>
POSTGRES_PASSWORD=<production-password>
REDIS_PASSWORD=<production-password>
JWT_SECRET=<production-jwt-secret>
OPENWEATHER_API_KEY=<api-key>
SENTINEL_HUB_ID=<production-client-id>
SENTINEL_HUB_SECRET=<production-client-secret>
STRIPE_SECRET_KEY=<stripe-live-key>
SLACK_WEBHOOK_URL=<production-webhook>
```

### Using Environment-Specific Secrets in Workflows

In your GitHub Actions workflow, reference secrets like this:

```yaml
- name: Deploy to Staging
  env:
    KUBE_CONFIG: ${{ secrets.KUBE_CONFIG_STAGING }}
    POSTGRES_PASSWORD: ${{ secrets.POSTGRES_PASSWORD }}
    JWT_SECRET: ${{ secrets.JWT_SECRET }}
  run: |
    # Deployment commands
```

## Verification

### Verify Secrets Are Set

1. Go to your repository on GitHub
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. You should see all required secrets listed
4. Note: You cannot view secret values after creation (for security)

### Test Secrets in Workflow

Create a test workflow to verify secrets are accessible:

```yaml
name: Test Secrets

on:
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Check Secrets
        run: |
          echo "Checking secrets availability..."

          # Check if secrets are set (will show true/false, not the actual values)
          [ -n "${{ secrets.KUBE_CONFIG_STAGING }}" ] && echo "✓ KUBE_CONFIG_STAGING is set" || echo "✗ KUBE_CONFIG_STAGING is missing"
          [ -n "${{ secrets.POSTGRES_PASSWORD }}" ] && echo "✓ POSTGRES_PASSWORD is set" || echo "✗ POSTGRES_PASSWORD is missing"
          [ -n "${{ secrets.REDIS_PASSWORD }}" ] && echo "✓ REDIS_PASSWORD is set" || echo "✗ REDIS_PASSWORD is missing"
          [ -n "${{ secrets.JWT_SECRET }}" ] && echo "✓ JWT_SECRET is set" || echo "✗ JWT_SECRET is missing"
          [ -n "${{ secrets.OPENWEATHER_API_KEY }}" ] && echo "✓ OPENWEATHER_API_KEY is set" || echo "✗ OPENWEATHER_API_KEY is missing"
          [ -n "${{ secrets.SENTINEL_HUB_ID }}" ] && echo "✓ SENTINEL_HUB_ID is set" || echo "✗ SENTINEL_HUB_ID is missing"
          [ -n "${{ secrets.SENTINEL_HUB_SECRET }}" ] && echo "✓ SENTINEL_HUB_SECRET is set" || echo "✗ SENTINEL_HUB_SECRET is missing"

          echo "✓ All required secrets are configured!"
```

### Common Issues

**Secret not found:**
- Verify the secret name matches exactly (case-sensitive)
- Check that the secret is created in the correct repository
- Ensure you have permissions to access secrets

**Kubeconfig not working:**
- Verify base64 encoding is correct
- Check that cluster URL is accessible from GitHub Actions
- Ensure cluster credentials are still valid

**External API errors:**
- Verify API keys are active
- Check API rate limits
- Ensure correct API endpoints are configured

## Secret Rotation

### When to Rotate Secrets

- **Immediately**: If a secret is compromised or exposed
- **Regularly**: Every 90 days for critical secrets (JWT, passwords)
- **After team changes**: When team members leave
- **After security incidents**: As part of incident response

### How to Rotate Secrets

1. Generate new secret value
2. Update in Kubernetes cluster first
3. Update in GitHub secrets
4. Trigger redeployment
5. Verify services are working
6. Revoke old secret

### Example: Rotating JWT Secret

```bash
# 1. Generate new JWT secret
NEW_JWT_SECRET=$(openssl rand -base64 64)

# 2. Update in Kubernetes
kubectl create secret generic sahool-jwt-secret \
  --namespace=sahool-staging \
  --from-literal=jwt-secret="$NEW_JWT_SECRET" \
  --dry-run=client -o yaml | kubectl apply -f -

# 3. Update in GitHub (manual step)
# Go to Settings > Secrets > JWT_SECRET > Update

# 4. Redeploy services
kubectl rollout restart deployment -n sahool-staging

# 5. Verify
kubectl rollout status deployment -n sahool-staging
```

## Security Checklist

- [ ] All required secrets are created
- [ ] Strong passwords are used (minimum 32 characters)
- [ ] Secrets are not committed to version control
- [ ] Different secrets for staging and production
- [ ] Secrets are stored in a password manager
- [ ] Team members have appropriate access levels
- [ ] Secret rotation schedule is established
- [ ] Monitoring is set up for failed authentications
- [ ] Backup of critical secrets exists in secure location

## Additional Resources

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [OpenWeather API](https://openweathermap.org/api)
- [Sentinel Hub Documentation](https://docs.sentinel-hub.com/)
- [Stripe API Keys](https://stripe.com/docs/keys)
- [Slack Webhooks](https://api.slack.com/messaging/webhooks)

## Support

If you encounter issues setting up secrets:
1. Check the troubleshooting section in [INFRASTRUCTURE.md](./INFRASTRUCTURE.md)
2. Verify you have the correct permissions
3. Contact the DevOps team
4. Open an issue on GitHub with details (never include actual secret values)
