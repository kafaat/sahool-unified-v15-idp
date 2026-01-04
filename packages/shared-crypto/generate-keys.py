#!/usr/bin/env python3

"""
Encryption Key Generator (Python)
==================================

Generates secure encryption keys for the SAHOOL shared-crypto package.

Usage:
    python3 generate-keys.py
    python3 generate-keys.py --format env
    python3 generate-keys.py --format json

Author: SAHOOL Team
"""

import json
import os
import sys
from datetime import datetime


def generate_keys():
    """Generate encryption keys."""
    return {
        "ENCRYPTION_KEY": os.urandom(32).hex(),
        "DETERMINISTIC_ENCRYPTION_KEY": os.urandom(32).hex(),
        "HMAC_SECRET": os.urandom(32).hex(),
    }


def output_env_format(keys):
    """Output keys in .env format."""
    print("# ========================================")
    print("# SAHOOL Encryption Keys")
    print(f"# Generated: {datetime.now().isoformat()}")
    print("# ========================================")
    print("")
    print("# ⚠️  WARNING: Never commit these keys to version control!")
    print("# Store them securely in AWS Secrets Manager, Azure Key Vault, or similar.")
    print("")
    print("# Primary Encryption Key (for standard encryption)")
    print(f"ENCRYPTION_KEY={keys['ENCRYPTION_KEY']}")
    print("")
    print("# Deterministic Encryption Key (for searchable fields)")
    print(f"DETERMINISTIC_ENCRYPTION_KEY={keys['DETERMINISTIC_ENCRYPTION_KEY']}")
    print("")
    print("# HMAC Secret (for data integrity verification)")
    print(f"HMAC_SECRET={keys['HMAC_SECRET']}")
    print("")
    print("# ========================================")
    print("# Next Steps:")
    print("# 1. Copy these keys to your .env file")
    print("# 2. Store backups in a secure location")
    print("# 3. Never share keys in plain text")
    print("# 4. Set up key rotation schedule")
    print("# ========================================")


def output_json_format(keys):
    """Output keys in JSON format."""
    output = {
        **keys,
        "generated_at": datetime.now().isoformat(),
        "warning": "NEVER commit these keys to version control. Store in a secure secret manager.",
    }
    print(json.dumps(output, indent=2))


def main():
    """Main function."""
    # Parse command line arguments
    format_type = "env"
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith("--format="):
                format_type = arg.split("=")[1]

    # Generate keys
    keys = generate_keys()

    # Output based on format
    if format_type == "json":
        output_json_format(keys)
    else:
        output_env_format(keys)


if __name__ == "__main__":
    main()
