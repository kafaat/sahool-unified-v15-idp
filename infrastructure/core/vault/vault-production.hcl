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
# Auto-Unseal - AWS KMS (Production Recommended)
# ─────────────────────────────────────────────────────────────────────────────
# Uncomment and configure for AWS deployments
# seal "awskms" {
#   region     = "us-east-1"
#   kms_key_id = "alias/sahool-vault-unseal"
#   endpoint   = "https://kms.us-east-1.amazonaws.com"
# }

# ─────────────────────────────────────────────────────────────────────────────
# Auto-Unseal - Azure Key Vault (Production Recommended)
# ─────────────────────────────────────────────────────────────────────────────
# Uncomment and configure for Azure deployments
# seal "azurekeyvault" {
#   tenant_id      = "AZURE_TENANT_ID"
#   client_id      = "AZURE_CLIENT_ID"
#   client_secret  = "AZURE_CLIENT_SECRET"
#   vault_name     = "sahool-vault"
#   key_name       = "vault-unseal-key"
# }

# ─────────────────────────────────────────────────────────────────────────────
# Auto-Unseal - GCP Cloud KMS (Production Recommended)
# ─────────────────────────────────────────────────────────────────────────────
# Uncomment and configure for GCP deployments
# seal "gcpckms" {
#   project     = "sahool-project"
#   region      = "us-east1"
#   key_ring    = "vault-keyring"
#   crypto_key  = "vault-key"
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
# service_registration "kubernetes" {
#   namespace      = "vault"
#   pod_name       = "vault-0"
# }
