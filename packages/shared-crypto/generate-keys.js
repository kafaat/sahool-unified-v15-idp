#!/usr/bin/env node

/**
 * Encryption Key Generator
 * =========================
 *
 * Generates secure encryption keys for the SAHOOL shared-crypto package.
 *
 * Usage:
 *   node generate-keys.js
 *   node generate-keys.js --format env
 *   node generate-keys.js --format json
 *
 * Author: SAHOOL Team
 */

const crypto = require('crypto');

// Parse command line arguments
const args = process.argv.slice(2);
const formatFlag = args.find(arg => arg.startsWith('--format'));
const format = formatFlag ? formatFlag.split('=')[1] : 'env';

// Generate keys
const encryptionKey = crypto.randomBytes(32).toString('hex');
const deterministicKey = crypto.randomBytes(32).toString('hex');
const hmacSecret = crypto.randomBytes(32).toString('hex');

// Output based on format
if (format === 'json') {
  // JSON format
  const keys = {
    ENCRYPTION_KEY: encryptionKey,
    DETERMINISTIC_ENCRYPTION_KEY: deterministicKey,
    HMAC_SECRET: hmacSecret,
    generated_at: new Date().toISOString(),
    warning: 'NEVER commit these keys to version control. Store in a secure secret manager.'
  };
  console.log(JSON.stringify(keys, null, 2));
} else {
  // ENV format (default)
  console.log('# ========================================');
  console.log('# SAHOOL Encryption Keys');
  console.log('# Generated:', new Date().toISOString());
  console.log('# ========================================');
  console.log('');
  console.log('# ⚠️  WARNING: Never commit these keys to version control!');
  console.log('# Store them securely in AWS Secrets Manager, Azure Key Vault, or similar.');
  console.log('');
  console.log('# Primary Encryption Key (for standard encryption)');
  console.log(`ENCRYPTION_KEY=${encryptionKey}`);
  console.log('');
  console.log('# Deterministic Encryption Key (for searchable fields)');
  console.log(`DETERMINISTIC_ENCRYPTION_KEY=${deterministicKey}`);
  console.log('');
  console.log('# HMAC Secret (for data integrity verification)');
  console.log(`HMAC_SECRET=${hmacSecret}`);
  console.log('');
  console.log('# ========================================');
  console.log('# Next Steps:');
  console.log('# 1. Copy these keys to your .env file');
  console.log('# 2. Store backups in a secure location');
  console.log('# 3. Never share keys in plain text');
  console.log('# 4. Set up key rotation schedule');
  console.log('# ========================================');
}
