# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Production Vault Configuration
# HashiCorp Vault - High Availability Setup
# ═══════════════════════════════════════════════════════════════════════════════
#
# This configuration provides:
# - Raft storage for HA
# - TLS encryption
# - Auto-unsealing with cloud KMS
# - Audit logging
# - Prometheus metrics
#
# Documentation: https://www.vaultproject.io/docs/configuration
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# Storage Backend - Raft (Integrated Storage)
# ─────────────────────────────────────────────────────────────────────────────
storage "raft" {
  path    = "/vault/data"
  node_id = "vault-node-1"

  # Raft performance tuning
  performance_multiplier = 1

  # Retry configuration
  retry_join {
    leader_api_addr = "https://vault-0.vault-internal:8200"
  }

  retry_join {
    leader_api_addr = "https://vault-1.vault-internal:8200"
  }

  retry_join {
    leader_api_addr = "https://vault-2.vault-internal:8200"
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# Listener - HTTPS with TLS
# ─────────────────────────────────────────────────────────────────────────────
listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_cert_file = "/vault/certs/vault.crt"
  tls_key_file  = "/vault/certs/vault.key"

  # TLS configuration
  tls_min_version = "tls12"
  tls_cipher_suites = [
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
  ]

  # Client authentication (optional - for mTLS)
  # tls_require_and_verify_client_cert = true
  # tls_client_ca_file = "/vault/certs/ca.crt"

  # Telemetry
  telemetry {
    unauthenticated_metrics_access = false
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# Cluster Configuration
# ─────────────────────────────────────────────────────────────────────────────
cluster_addr  = "https://VAULT_NODE_IP:8201"
api_addr      = "https://vault.sahool.com:8200"

# ─────────────────────────────────────────────────────────────────────────────
# Auto-Unseal — AWS KMS (Default for AWS / me-south-1 deployments)
# ─────────────────────────────────────────────────────────────────────────────
# All values are injected at deploy-time via environment variables.
# Set VAULT_AWSKMS_SEAL_KEY_ID to the KMS key alias or ARN, e.g.:
#   export VAULT_AWSKMS_SEAL_KEY_ID="alias/sahool-vault-unseal"
# AWS credentials are provided automatically by the EC2/EKS IAM role —
# do NOT hardcode access keys here.
#
# To use Azure Key Vault instead, comment out this stanza and uncomment
# the "seal azurekeyvault" block below.
seal "awskms" {
  region     = "me-south-1"        # Override via VAULT_AWSKMS_SEAL_REGION env var
  kms_key_id = "VAULT_AWSKMS_SEAL_KEY_ID"  # Replaced at runtime by Vault from env
  # endpoint can be left empty; Vault resolves it from the region
}

# ─────────────────────────────────────────────────────────────────────────────
# Auto-Unseal — Azure Key Vault (alternative for Azure deployments)
# ─────────────────────────────────────────────────────────────────────────────
# Uncomment and configure for Azure deployments.
# Inject secrets at deploy-time via environment variables; never hardcode.
#
# seal "azurekeyvault" {
#   tenant_id      = "VAULT_AZUREKEYVAULT_TENANT_ID"   # set via env VAULT_AZUREKEYVAULT_TENANT_ID
#   client_id      = "VAULT_AZUREKEYVAULT_CLIENT_ID"   # set via env VAULT_AZUREKEYVAULT_CLIENT_ID
#   client_secret  = "VAULT_AZUREKEYVAULT_CLIENT_SECRET" # set via env VAULT_AZUREKEYVAULT_CLIENT_SECRET
#   vault_name     = "sahool-vault"
#   key_name       = "vault-unseal-key"
# }

# ─────────────────────────────────────────────────────────────────────────────
# Auto-Unseal — GCP Cloud KMS (alternative for GCP deployments)
# ─────────────────────────────────────────────────────────────────────────────
# Uncomment and configure for GCP deployments.
# seal "gcpckms" {
#   project     = "sahool-project"
#   region      = "me-central1"
#   key_ring    = "vault-keyring"
#   crypto_key  = "vault-unseal-key"
# }

# ─────────────────────────────────────────────────────────────────────────────
# UI Configuration
# ─────────────────────────────────────────────────────────────────────────────
ui = true

# ─────────────────────────────────────────────────────────────────────────────
# Logging & Audit
# ─────────────────────────────────────────────────────────────────────────────
log_level = "info"
log_format = "json"

# ─────────────────────────────────────────────────────────────────────────────
# Telemetry - Prometheus Metrics
# ─────────────────────────────────────────────────────────────────────────────
telemetry {
  prometheus_retention_time = "30s"
  disable_hostname          = false

  # Statsd configuration (optional)
  # statsd_address = "statsd:8125"
}

# ─────────────────────────────────────────────────────────────────────────────
# Performance & Limits
# ─────────────────────────────────────────────────────────────────────────────
default_lease_ttl = "168h"  # 7 days
max_lease_ttl     = "720h"  # 30 days

# Disable mlock for containerized environments
# Enable in bare-metal production deployments
disable_mlock = true

# ─────────────────────────────────────────────────────────────────────────────
# Plugin Directory
# ─────────────────────────────────────────────────────────────────────────────
plugin_directory = "/vault/plugins"

# ─────────────────────────────────────────────────────────────════════════════
# API Rate Limiting
# ─────────────────────────────────────────────────────────────────────────────
# api_rate_limit {
#   rate = 10000
#   burst = 100
# }

# ─────────────────────────────────────────────────────────────────────────────
# Service Registration (Kubernetes)
# ─────────────────────────────────────────────────────────────────────────────
# Enable Kubernetes service registration so that Vault pods are discoverable
# via standard k8s service annotations (used by Vault Helm chart).
service_registration "kubernetes" {
  namespace = "vault"
  pod_name  = "vault-0"
}
