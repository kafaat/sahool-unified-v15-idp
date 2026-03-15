#!/bin/sh
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Etcd Authentication Initialization Script
# This script enables authentication in etcd and creates the root user
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

set -e

# Cleanup function for error handling
cleanup() {
  exit_code=$?
  if [ $exit_code -ne 0 ]; then
    echo "ERROR: Etcd authentication initialization failed with exit code $exit_code"
  fi
}

# Set trap for cleanup on error
trap cleanup EXIT

# Retry function for transient failures
# Usage: retry <max_attempts> <delay_seconds> <command> [args...]
retry() {
  max_attempts=$1
  delay=$2
  shift 2
  attempt=1

  while [ $attempt -le $max_attempts ]; do
    if "$@"; then
      return 0
    fi

    if [ $attempt -lt $max_attempts ]; then
      echo "Command failed (attempt $attempt/$max_attempts). Retrying in ${delay}s..."
      sleep "$delay"
    fi
    attempt=$((attempt + 1))
  done

  echo "ERROR: Command failed after $max_attempts attempts: $*"
  return 1
}

echo "Starting etcd authentication initialization..."

# Wait for etcd to be ready
echo "Waiting for etcd to be ready..."
sleep 5

# SECURITY FIX: If ETCDCTL_INSECURE_SKIP_TLS_VERIFY is not already set,
# enable it for auto-TLS self-signed certs
if [ -z "${ETCDCTL_INSECURE_SKIP_TLS_VERIFY}" ]; then
  export ETCDCTL_INSECURE_SKIP_TLS_VERIFY=true
  echo "NOTE: Enabled ETCDCTL_INSECURE_SKIP_TLS_VERIFY for auto-TLS self-signed certs"
fi

# Check if etcd is responsive with retry logic
# Try without credentials first (auth disabled), then with credentials (auth enabled)
# SECURITY: Use ETCDCTL_USER env var (not --user flag) to avoid exposing credentials in ps output
echo "Checking etcd health..."
check_health() {
  etcdctl endpoint health 2>/dev/null || \
  ETCDCTL_USER="${ETCD_ROOT_USERNAME}:${ETCD_ROOT_PASSWORD}" etcdctl endpoint health 2>/dev/null
}
retry 3 2 check_health || {
  echo "ERROR: Etcd failed to become healthy after multiple attempts"
  exit 1
}

echo "Etcd is healthy, proceeding with authentication setup..."

# Check if authentication is already enabled
# FIX: Try both with and without auth credentials to handle all states:
# 1. Auth disabled: 'etcdctl user list' works without credentials
# 2. Auth enabled: 'etcdctl user list' requires credentials (use ETCD_ROOT env vars)
if etcdctl user list 2>/dev/null | grep -q "root"; then
  echo "Authentication already configured (auth not yet enabled). Root user exists."
  exit 0
fi

# Try with credentials (auth already enabled from a previous run)
# SECURITY: Use env var prefix to pass credentials without exposing in process args
if ETCDCTL_USER="${ETCD_ROOT_USERNAME}:${ETCD_ROOT_PASSWORD}" etcdctl user list 2>/dev/null | grep -q "root"; then
  echo "Authentication already configured and enabled. Root user exists."
  exit 0
fi

echo "Creating root user..."
# Create root user with password (with retry logic)
# SECURITY NOTE: Password is passed via stdin to avoid command-line exposure.
# While this prevents ps-based exposure, the password may still appear in logs.
# In production, consider using Kubernetes secrets or external secret management.
attempt=1
max_attempts=3
while [ $attempt -le $max_attempts ]; do
  if echo "$ETCD_ROOT_PASSWORD" | etcdctl user add root --interactive=false 2>/dev/null; then
    echo "Root user created successfully"
    break
  fi

  if [ $attempt -lt $max_attempts ]; then
    echo "Failed to create root user (attempt $attempt/$max_attempts). Retrying in 2s..."
    sleep 2
  else
    echo "ERROR: Failed to create root user after $max_attempts attempts"
    exit 1
  fi
  attempt=$((attempt + 1))
done

echo "Granting root role to root user..."
# Grant root role with retry
retry 3 2 etcdctl user grant-role root root || {
  echo "ERROR: Failed to grant root role after multiple attempts"
  exit 1
}

echo "Enabling authentication..."
# Enable authentication with retry
retry 3 2 etcdctl auth enable || {
  echo "ERROR: Failed to enable authentication after multiple attempts"
  exit 1
}

echo "Etcd authentication setup completed successfully!"
echo "  - Root user: configured"
echo "  - Authentication: ENABLED"
