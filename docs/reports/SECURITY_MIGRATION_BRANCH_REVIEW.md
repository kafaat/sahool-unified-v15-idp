# Security Migration Branch Review Report

**Date**: 2026-03-21
**Branch**: `claude/review-user-migration-7CihF`
**Scope**: Crypto, audit trail, GlobalGAP integrity, PII handling, prompt injection
**Files Changed**: 15 files, +1,148 / -113 lines
**Reviewer**: Automated Security Audit (3 parallel agents)

---

## Executive Summary

This branch implements important security hardening: HMAC-signed audit logs, searchable encryption migration, prompt injection protection, and PII masking. However, **the implementation contains 27 security issues**, including **AES-GCM with deterministic IV** (breaks GCM security guarantees), **5 fields missing from GlobalGAP integrity hash** (tamper-undetectable), and **10 cross-platform PII inconsistencies**.

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| Cryptography | 1 | 2 | 1 | 0 | **4** |
| Audit & Integrity | 2 | 3 | 2 | 0 | **7** |
| SQL & Input Validation | 0 | 0 | 2 | 0 | **2** |
| PII Handling | 1 | 2 | 4 | 3 | **10** |
| Tests | 0 | 0 | 1 | 0 | **1** |
| **Total** | **4** | **7** | **10** | **3** | **24** |

---

## 1. Cryptography Issues

### CRITICAL: AES-GCM with Deterministic IV
- **File**: `packages/shared-crypto/src/field-encryption.ts:219-232`
- `encryptDeterministic()` uses AES-256-GCM with HMAC-derived IV from plaintext
- **GCM requires unique IVs per encryption with same key** — deterministic IVs break GCM's authentication guarantees
- `encryptSearchable()` correctly uses AES-256-CTR for deterministic mode
- **Fix**: Use CTR mode (not GCM) for deterministic encryption

### HIGH: Timing Side-Channel in Hint Comparison
- **File**: `field-encryption.ts:390-392`
- `if (decrypted !== hint)` — string comparison vulnerable to timing attack
- **Fix**: Use `crypto.timingSafeEqual(Buffer.from(decrypted), Buffer.from(hint))`

### HIGH: Fixed Salt in Legacy Encryption
- **File**: `field-encryption.ts:419`
- `Buffer.from("sahool-deterministic-salt")` — same salt across all deployments
- Rainbow table precomputation possible with known salt

### MEDIUM: PBKDF2 Iteration Count 1,000 (Legacy)
- **File**: `field-encryption.ts:420`
- NIST recommends ≥600,000 iterations for PBKDF2-SHA256

---

## 2. Audit Trail & GlobalGAP Integrity Issues

### CRITICAL: 5 Fields Missing from FarmRegistration Hash
- **File**: `shared/globalgap/models.py:518-544`
- Missing: `location_coordinates`, `registration_date`, `last_audit_date`, `next_audit_date`, `updated_at`
- **Attack**: Farm location, audit dates, registration can be tampered without detection

### CRITICAL: Unsealed Nested Findings in AuditSession
- **File**: `shared/globalgap/models.py:614-627`
- `model_dump()` includes nested AuditFindings that may have `data_hash=None`
- Parent hash doesn't verify child integrity if children are unsealed

### HIGH: HMAC Secret Can Be Empty (Silent Fallback to SHA-256)
- **Files**: `globalgap/models.py:38-40`, `audit_trail/models.py:398-402`
- `if secret:` — empty string defaults to plaintext SHA-256 without warning
- No environment check, no minimum length, no production enforcement

### HIGH: No Hash Chains for GlobalGAP Records
- AuditFinding, NonConformance, CorrectiveAction, FarmRegistration — none have `prev_hash`
- Records can be reordered/deleted without detection (unlike audit_trail which has chains)

### HIGH: Silent Downgrade to SHA-256 in Production
- No check if `ENVIRONMENT=production` — falls back silently if env var missing

### MEDIUM: Weak HMAC Key — No Minimum Entropy
- Raw environment variable used as key without key strengthening
- Test uses `"test-globalgap-secret"` (short, predictable)

### MEDIUM: Incomplete Field Coverage in Hashing
- Future fields added to models won't be auto-included in hash

---

## 3. SQL & Input Validation

### MEDIUM: SQL Injection in ON CONFLICT Regex
- **File**: `shared/service_enhancements/database.py:533-538`
- Pattern `DO UPDATE SET .+` is overly permissive — allows arbitrary SQL in SET clause
- **Example bypass**: `(id) DO UPDATE SET password = '1' WHERE id=1 --`

### MEDIUM: Prompt Injection Unicode Bypasses
- **File**: `shared/ai/validation.py:113-137`
- No Arabic prompt injection patterns
- Zero-width characters, null bytes, ROT13, base32 not detected
- No UTF-8 normalization before pattern matching

---

## 4. PII Handling — 10 Cross-Platform Inconsistencies

### CRITICAL: Email Masking Off-By-One (Main App)
- **File**: `apps/mobile/lib/core/utils/pii_filter.dart:238`
- Main app: `if (username.length < 2)` — 2-char usernames fully exposed
- Field app: `if (username.length <= 2)` — correct masking

### HIGH: Sanitization Order Mismatch Between Apps
- Main app: phones processed LAST (after IDs, GPS, cards) — correct
- Field app: phones processed EARLY — may false-match other numeric data

### HIGH: Phone Regex Missing Third Alternative (Field App)
- Main app: 3 phone patterns
- Field app: 2 phone patterns — misses parenthetical format `(123) 456-7890`

### MEDIUM: Email Regex Loose in Main App
- Allows consecutive dots `test..name@example.com`
- Field app has strict TLD validation (2-63 chars)

### MEDIUM: API Key Detection Inconsistent
- Main app: 32 char + mixed digits+letters + underscores
- Field app: 32 char alphanumeric only (no underscore, no mixed requirement)

### MEDIUM: Arabic Name Detection — TypeScript Requires 2 Words
- Dart: matches single-word Arabic names (Gulf naming convention)
- TypeScript: requires exactly 2 words — misses single-word names

### MEDIUM: Arabic Phone Numbers NOT in Dart or TypeScript
- Only Python detects Arabic-Indic numerals (`٠٥٥١٢٣٤٥٦٧`)
- Mobile apps won't mask Arabic-format phone numbers

### LOW: TypeScript Name Confidence Artificially Low for Arabic
- Non-English names get 0.6 confidence (vs 0.7 for English)
- May be skipped by confidence threshold filtering

### LOW: No Length Coordination Across Platforms
### LOW: Python API Key Pattern Too Broad

---

## 5. Test Coverage Gaps

### MEDIUM: Missing Critical Edge Case Tests
- No test for IV uniqueness across 1000+ encryptions
- No timing attack tests for hint comparison
- No auth tag corruption test for GCM mode
- No test for FarmRegistration location/date tampering
- No test for empty HMAC secret in production mode
- No cross-platform PII test consistency suite

---

## Priority Action Plan

### Immediate (Before Merge)
1. **Change `encryptDeterministic()` to AES-256-CTR** (not GCM)
2. **Use `crypto.timingSafeEqual()`** for hint comparison
3. **Add 5 missing fields** to FarmRegistration hash
4. **Fix email masking** off-by-one in main app Dart
5. **Enforce HMAC secret** minimum length + production check

### Before Production
6. Fix ON CONFLICT SQL regex (restrict SET clause)
7. Add hash chains to GlobalGAP records
8. Unify PII phone patterns across both Dart apps
9. Fix sanitization order in field app (phones last)
10. Add Arabic prompt injection patterns
11. Add Arabic phone detection to Dart/TypeScript

### Short-Term
12. Migrate legacy searchable encryption (fixed salt + 1000 iterations)
13. Add comprehensive cross-platform PII test suite
14. Require sealed nested findings in AuditSession
15. Add startup warning when HMAC secret is missing
