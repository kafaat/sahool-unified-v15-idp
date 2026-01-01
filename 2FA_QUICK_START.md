# 2FA Quick Start Guide

## Installation (5 minutes)

### 1. Install Python Dependencies
```bash
cd /home/user/sahool-unified-v15-idp
pip install pyotp qrcode[pil]
```

### 2. Database Migration
Add 2FA fields to your users table:

```sql
ALTER TABLE users
ADD COLUMN twofa_secret TEXT,
ADD COLUMN twofa_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN twofa_backup_codes TEXT[];
```

### 3. Configure Your Application

#### For FastAPI Backend:
```python
from fastapi import FastAPI
from shared.auth.auth_api import router as auth_router, set_user_service
from shared.auth.twofa_api import router as twofa_router
from shared.auth.twofa_config import configure_twofa, TwoFAEnforcementLevel
from shared.domain.users.service import UserService

app = FastAPI()

# Initialize user service
user_service = UserService()
set_user_service(user_service)

# Configure 2FA (require for admins, 7-day grace period)
configure_twofa(
    enforcement_level=TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN,
    grace_period_days=7
)

# Register routes
app.include_router(auth_router)
app.include_router(twofa_router)
```

## Usage

### For End Users (Admins)

#### Enable 2FA:
1. Login to admin dashboard
2. Navigate to **Settings → Security**
3. Click **"Enable 2FA"**
4. Scan QR code with authenticator app (Google Authenticator, Authy, etc.)
5. Enter verification code
6. **Save backup codes securely!**

#### Login with 2FA:
1. Enter email and password
2. Enter 6-digit code from authenticator app
3. Click **"Verify"**

#### Disable 2FA:
1. Navigate to **Settings → Security**
2. Click **"Disable 2FA"**
3. Enter verification code or backup code
4. Confirm

### For Developers

#### API Endpoints:
```bash
# Setup 2FA
POST /admin/2fa/setup
Authorization: Bearer {token}

# Verify and Enable
POST /admin/2fa/verify
Authorization: Bearer {token}
Content-Type: application/json
{"token": "123456"}

# Login with 2FA
POST /api/v1/auth/login
Content-Type: application/json
{
  "email": "admin@sahool.io",
  "password": "password",
  "totp_code": "123456"
}

# Check Status
GET /admin/2fa/status
Authorization: Bearer {token}

# Disable 2FA
POST /admin/2fa/disable
Authorization: Bearer {token}
Content-Type: application/json
{"token": "123456"}

# Regenerate Backup Codes
POST /admin/2fa/backup-codes
Authorization: Bearer {token}
Content-Type: application/json
{"token": "123456"}
```

## Configuration Options

### Enforcement Levels:

```python
from shared.auth.twofa_config import TwoFAEnforcementLevel

# Optional (users can choose)
enforcement_level=TwoFAEnforcementLevel.OPTIONAL

# Required for admins only (recommended)
enforcement_level=TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN

# Required for everyone (maximum security)
enforcement_level=TwoFAEnforcementLevel.REQUIRED_FOR_ALL
```

### Presets:

```python
from shared.auth.twofa_config import get_production_config, set_twofa_config

# Production preset (recommended)
set_twofa_config(get_production_config())

# Development preset
set_twofa_config(get_development_config())

# Strict preset (maximum security)
set_twofa_config(get_strict_config())
```

## Testing

### Quick Test:
```bash
# 1. Start backend
python shared/auth/example_integration.py

# 2. Start frontend (in another terminal)
cd apps/admin
npm run dev

# 3. Open browser
# http://localhost:3001/login
# Login: admin@sahool.io / admin123

# 4. Navigate to Security Settings
# http://localhost:3001/settings/security

# 5. Enable 2FA and test
```

### Manual Testing Checklist:
- [ ] Setup 2FA with QR code
- [ ] Verify TOTP code
- [ ] Save backup codes
- [ ] Logout and login with 2FA
- [ ] Test backup code
- [ ] Disable 2FA
- [ ] Re-enable 2FA
- [ ] Regenerate backup codes

## Files Overview

### Created:
- `/shared/auth/twofa_service.py` - Core 2FA service
- `/shared/auth/twofa_api.py` - API endpoints
- `/shared/auth/auth_api.py` - Authentication with 2FA
- `/shared/auth/twofa_config.py` - Configuration
- `/shared/auth/requirements-2fa.txt` - Dependencies
- `/shared/auth/2FA_IMPLEMENTATION_GUIDE.md` - Full documentation
- `/shared/auth/example_integration.py` - Integration example
- `/apps/admin/src/app/settings/security/page.tsx` - Settings UI

### Modified:
- `/shared/domain/users/models.py` - Added 2FA fields
- `/shared/domain/users/service.py` - Added 2FA methods
- `/apps/admin/src/app/login/page.tsx` - Added 2FA input
- `/apps/admin/src/lib/api-client.ts` - Updated login method
- `/apps/admin/src/stores/auth.store.tsx` - Handle 2FA flow

## Troubleshooting

**QR Code not showing?**
→ Run: `pip install qrcode[pil]`

**"Invalid verification code"?**
→ Check system time is synced (NTP)
→ Try the next code from authenticator

**Locked out of account?**
→ Use backup codes
→ Contact administrator

**Backend errors?**
→ Check: `pip list | grep -E "pyotp|qrcode"`
→ Verify database migrations ran

## Security Tips

✅ **DO:**
- Save backup codes securely
- Use unique passwords
- Enable 2FA on all admin accounts
- Keep authenticator app updated

❌ **DON'T:**
- Share backup codes
- Screenshot QR codes publicly
- Disable 2FA unless necessary
- Store codes in plain text

## Support

- Documentation: `/shared/auth/2FA_IMPLEMENTATION_GUIDE.md`
- Example: `/shared/auth/example_integration.py`
- Issues: Check application logs

## Next Steps

1. ✅ Install dependencies
2. ✅ Run database migrations
3. ✅ Configure enforcement level
4. ✅ Test 2FA flow
5. ✅ Train admin users
6. ✅ Monitor adoption
7. ✅ Enforce for all admins

---

**Ready to go!** 🚀

All components are implemented and ready for use. Start with the Quick Test above to see 2FA in action.
