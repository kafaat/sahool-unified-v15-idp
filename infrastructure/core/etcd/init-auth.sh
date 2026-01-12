#!/bin/sh
# ═══════════════════════════════════════════════════════════════════════════════
# Etcd Authentication Initialization Script
# This script enables authentication in etcd and creates the root user
# ═══════════════════════════════════════════════════════════════════════════════

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

# Check if etcd is responsive with retry logic
echo "Checking etcd health..."
retry 3 2 etcdctl endpoint health || {
  echo "ERROR: Etcd failed to become healthy after multiple attempts"
  exit 1
}

echo "Etcd is healthy, proceeding with authentication setup..."

# Check if authentication is already enabled
if etcdctl user list 2>/dev/null | grep -q "root"; then
  echo "Authentication already configured. Root user exists."
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

echo "✓ Etcd authentication setup completed successfully!"
echo "  - Root user configured"
echo "  - Authentication: ENABLED"
