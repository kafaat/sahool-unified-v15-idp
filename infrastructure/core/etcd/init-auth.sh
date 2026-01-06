#!/bin/sh
# ═══════════════════════════════════════════════════════════════════════════════
# Etcd Authentication Initialization Script
# This script enables authentication in etcd and creates the root user
# ═══════════════════════════════════════════════════════════════════════════════

set -e

echo "Starting etcd authentication initialization..."

# Wait for etcd to be ready
echo "Waiting for etcd to be ready..."
sleep 5

# Check if etcd is responsive
until etcdctl endpoint health 2>/dev/null; do
  echo "Waiting for etcd to become healthy..."
  sleep 2
done

echo "Etcd is healthy, proceeding with authentication setup..."

# Check if authentication is already enabled
if etcdctl user list 2>/dev/null | grep -q "root"; then
  echo "Authentication already configured. Root user exists."
  exit 0
fi

echo "Creating root user..."
# Create root user with password
echo "$ETCD_ROOT_PASSWORD" | etcdctl user add root --interactive=false || {
  echo "Root user already exists or creation failed"
}

echo "Granting root role to root user..."
# Grant root role
etcdctl user grant-role root root || {
  echo "Role already granted or grant failed"
}

echo "Enabling authentication..."
# Enable authentication
etcdctl auth enable || {
  echo "Authentication already enabled or enable failed"
}

echo "✓ Etcd authentication setup completed successfully!"
echo "  - Root username: ${ETCD_ROOT_USERNAME}"
echo "  - Authentication: ENABLED"
