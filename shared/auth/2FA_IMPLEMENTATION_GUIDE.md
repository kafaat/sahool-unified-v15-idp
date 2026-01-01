# Two-Factor Authentication (2FA) Implementation Guide

## Overview

This guide documents the complete Two-Factor Authentication (2FA) implementation for the SAHOOL Platform admin accounts using TOTP (Time-based One-Time Password).

## Features

- TOTP-based 2FA using authenticator apps (Google Authenticator, Authy, etc.)
- QR code generation for easy setup
- Backup codes for account recovery
- Configurable enforcement levels
- Grace period for 2FA setup
- Admin-only 2FA or platform-wide enforcement

## Architecture

### Backend Components

1. **User Model** (`shared/domain/users/models.py`)
   - Added 2FA fields: `twofa_secret`, `twofa_enabled`, `twofa_backup_codes`

2. **2FA Service** (`shared/auth/twofa_service.py`)
   - TOTP secret generation
   - QR code generation
   - TOTP verification
   - Backup code generation and verification

3. **2FA API** (`shared/auth/twofa_api.py`)
   - `POST /admin/2fa/setup` - Initiate 2FA setup
   - `POST /admin/2fa/verify` - Verify and enable 2FA
   - `POST /admin/2fa/disable` - Disable 2FA
   - `GET /admin/2fa/status` - Get 2FA status
   - `POST /admin/2fa/backup-codes` - Regenerate backup codes

4. **Auth API** (`shared/auth/auth_api.py`)
   - Updated login flow with 2FA support
   - Handles TOTP verification during login
   - Supports backup codes

5. **2FA Configuration** (`shared/auth/twofa_config.py`)
   - Enforcement levels: optional, recommended, required_for_admin, required_for_all
   - Grace periods
   - Security settings

### Frontend Components

1. **Login Page** (`apps/admin/src/app/login/page.tsx`)
   - 2FA code input field
   - Two-step login flow
   - Support for backup codes

2. **Security Settings Page** (`apps/admin/src/app/settings/security/page.tsx`)
   - 2FA setup wizard with QR code
   - Backup codes display and download
   - 2FA disable functionality
   - Backup codes regeneration

## Installation

### Backend Requirements

```bash
# Install Python dependencies
pip install pyotp qrcode[pil]
```

### Frontend Requirements

The frontend uses existing dependencies (no additional packages needed).

## Configuration

### Basic Setup

```python
from shared.auth.twofa_config import configure_twofa, TwoFAEnforcementLevel

# Configure 2FA for admin users only (recommended for production)
configure_twofa(
    enforcement_level=TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN,
    grace_period_days=7,
    max_2fa_attempts=3,
    lockout_duration_minutes=30
)
```

### Enforcement Levels

1. **OPTIONAL** - 2FA is completely optional
   ```python
   enforcement_level=TwoFAEnforcementLevel.OPTIONAL
   ```

2. **RECOMMENDED** - 2FA is suggested but not enforced
   ```python
   enforcement_level=TwoFAEnforcementLevel.RECOMMENDED
   ```

3. **REQUIRED_FOR_ADMIN** - Required for admin and supervisor roles
   ```python
   enforcement_level=TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN
   ```

4. **REQUIRED_FOR_ALL** - Required for all users
   ```python
   enforcement_level=TwoFAEnforcementLevel.REQUIRED_FOR_ALL
   ```

### Preset Configurations

```python
from shared.auth.twofa_config import (
    get_production_config,
    get_development_config,
    get_strict_config,
    set_twofa_config
)

# Use production preset
set_twofa_config(get_production_config())

# Or use development preset
set_twofa_config(get_development_config())

# Or use strict preset (maximum security)
set_twofa_config(get_strict_config())
```

## Integration Guide

### Step 1: Register API Routes

```python
from fastapi import FastAPI
from shared.auth.twofa_api import router as twofa_router
from shared.auth.auth_api import router as auth_router, set_user_service
from shared.domain.users.service import UserService

app = FastAPI()

# Initialize user service
user_service = UserService()

# Set user service for auth APIs
set_user_service(user_service)

# Register routes
app.include_router(auth_router)
app.include_router(twofa_router)
```

### Step 2: Update User Repository

Implement the 2FA methods in your user repository:

```python
from shared.domain.users.service import UserService

class DatabaseUserService(UserService):
    async def update_twofa_secret(self, user_id: str, secret: str):
        # Update user's 2FA secret in database
        await db.execute(
            "UPDATE users SET twofa_secret = $1 WHERE id = $2",
            secret, user_id
        )

    async def enable_twofa(self, user_id: str, backup_codes: list[str]):
        # Enable 2FA and save backup codes
        await db.execute(
            "UPDATE users SET twofa_enabled = true, twofa_backup_codes = $1 WHERE id = $2",
            backup_codes, user_id
        )

    # Implement other 2FA methods...
```

### Step 3: Frontend Integration

The frontend components are already integrated. Ensure your routing includes:

- `/login` - Login page with 2FA support
- `/settings/security` - 2FA management page

## User Flow

### Setup Flow

1. Admin navigates to `/settings/security`
2. Clicks "Enable 2FA"
3. Backend generates TOTP secret and QR code
4. User scans QR code with authenticator app
5. User enters verification code
6. Backend verifies code and enables 2FA
7. Backup codes are displayed (user must save them)

### Login Flow

1. User enters email and password
2. Backend verifies credentials
3. If 2FA is enabled:
   - User is prompted for TOTP code
   - User enters 6-digit code from authenticator app
   - Backend verifies TOTP code
4. If verification succeeds, user is logged in

### Backup Code Flow

1. If user loses access to authenticator app
2. During login, user can enter backup code instead of TOTP
3. Backup code is verified and removed from available codes
4. User is logged in

## API Examples

### Setup 2FA

```bash
# Initiate 2FA setup
curl -X POST https://api.sahool.io/admin/2fa/setup \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Response
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KG...",
  "manual_entry_key": "JBSWY3DPEHPK3PXP",
  "issuer": "SAHOOL Agricultural Platform",
  "account_name": "admin@sahool.io"
}
```

### Verify and Enable

```bash
curl -X POST https://api.sahool.io/admin/2fa/verify \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"token": "123456"}'

# Response
{
  "success": true,
  "backup_codes": [
    "ABCD-EFGH",
    "IJKL-MNOP",
    ...
  ],
  "message": "Two-factor authentication enabled successfully"
}
```

### Login with 2FA

```bash
# Initial login (returns temp_token if 2FA required)
curl -X POST https://api.sahool.io/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@sahool.io",
    "password": "password123"
  }'

# Response when 2FA is enabled
{
  "access_token": "",
  "requires_2fa": true,
  "temp_token": "temporary_token_here",
  "user": {...}
}

# Complete login with 2FA code
curl -X POST https://api.sahool.io/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@sahool.io",
    "password": "password123",
    "totp_code": "123456"
  }'

# Response on successful verification
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user": {...},
  "requires_2fa": false
}
```

## Security Best Practices

1. **Enforce 2FA for Admin Accounts**
   - Always require 2FA for admin and supervisor roles
   - Use `TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN`

2. **Secure Secret Storage**
   - TOTP secrets are encrypted in database
   - Backup codes are hashed (SHA-256)

3. **Rate Limiting**
   - Limit 2FA verification attempts
   - Implement account lockout after failed attempts

4. **Backup Codes**
   - Generate 10 backup codes by default
   - Each code is single-use
   - Encourage users to store codes securely

5. **Grace Period**
   - Provide 7-30 day grace period for setup
   - Send reminders before enforcement

## Testing

### Manual Testing

1. Create a test admin user
2. Navigate to `/settings/security`
3. Enable 2FA and scan QR code
4. Logout and test login with 2FA
5. Test backup codes
6. Test disabling 2FA

### Automated Testing

```python
from shared.auth.twofa_service import get_twofa_service

def test_totp_generation():
    service = get_twofa_service()
    secret = service.generate_secret()
    assert len(secret) > 0

def test_totp_verification():
    service = get_twofa_service()
    secret = service.generate_secret()
    token = service.get_current_totp(secret)
    assert service.verify_totp(secret, token) == True

def test_backup_codes():
    service = get_twofa_service()
    codes = service.generate_backup_codes(count=10)
    assert len(codes) == 10
    assert all('-' in code for code in codes)
```

## Troubleshooting

### Common Issues

1. **QR Code Not Displaying**
   - Ensure `qrcode[pil]` is installed
   - Check image generation in backend logs

2. **TOTP Verification Fails**
   - Check system time synchronization
   - Verify time drift (±30 seconds tolerance)
   - Ensure user entered correct 6-digit code

3. **Backup Codes Not Working**
   - Verify code format (XXXX-XXXX)
   - Check if code was already used
   - Ensure codes are properly hashed in database

## Migration Guide

### For Existing Users

If you're adding 2FA to an existing system:

1. Add database migrations for new fields:
   ```sql
   ALTER TABLE users ADD COLUMN twofa_secret TEXT;
   ALTER TABLE users ADD COLUMN twofa_enabled BOOLEAN DEFAULT FALSE;
   ALTER TABLE users ADD COLUMN twofa_backup_codes TEXT[];
   ```

2. Set enforcement level to OPTIONAL initially
3. Gradually increase enforcement over time
4. Send notifications to users about 2FA availability

## Support

For issues or questions:
- Check logs in `/var/log/sahool/`
- Review error messages in frontend console
- Contact platform administrator

## License

Copyright © 2025 SAHOOL Agricultural Platform
