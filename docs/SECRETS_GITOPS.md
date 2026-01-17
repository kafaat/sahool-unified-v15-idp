# Secrets GitOps for SAHOOL

This setup uses **External Secrets Operator + Vault (or K8s SecretStore)**.
Secrets are never committed in plaintext.

## Components

- external-secrets (ESO)
- SecretStore / ClusterSecretStore
- ExternalSecret CRDs
- Optional: HashiCorp Vault / SOPS

## Flow

Developer -> values.yaml references -> ExternalSecret -> SecretStore -> Pod env
