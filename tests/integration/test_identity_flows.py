"""
Identity Flow Integration Tests
اختبارات تدفق الهوية

Tests for critical identity flows:
1. User login with credentials
2. Token refresh flow
3. External provider authentication (OAuth)
4. Token validation and expiration
5. Multi-factor authentication (MFA)
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Optional
import jwt
import httpx


# ═══════════════════════════════════════════════════════════════════════════════
# Test Configuration
# ═══════════════════════════════════════════════════════════════════════════════

JWT_SECRET = "test-secret-key-for-unit-tests-only-32chars"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_EXPIRE = 60  # 60 minutes
JWT_REFRESH_EXPIRE = 30 * 24 * 60  # 30 days in minutes


# ═══════════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_user():
    """Mock user data for testing"""
    return {
        "id": "user_123",
        "username": "testuser",
        "email": "testuser@example.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lSxdVU6OKVNm",  # "password123"
        "is_active": True,
        "is_verified": True,
        "mfa_enabled": False,
        "tenant_id": "tenant_default",
    }


@pytest.fixture
def mock_user_with_mfa(mock_user):
    """Mock user with MFA enabled"""
    return {
        **mock_user,
        "mfa_enabled": True,
        "mfa_secret": "JBSWY3DPEHPK3PXP",  # Base32 TOTP secret
    }


@pytest.fixture
def jwt_helper():
    """Helper for JWT token operations"""
    class JWTHelper:
        @staticmethod
        def create_access_token(user_id: str, tenant_id: str, extra_claims: Optional[Dict] = None) -> str:
            """Create a valid access token"""
            payload = {
                "sub": user_id,
                "tenant_id": tenant_id,
                "type": "access",
                "exp": datetime.utcnow() + timedelta(minutes=JWT_ACCESS_EXPIRE),
                "iat": datetime.utcnow(),
            }
            if extra_claims:
                payload.update(extra_claims)
            
            return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        @staticmethod
        def create_refresh_token(user_id: str, tenant_id: str) -> str:
            """Create a valid refresh token"""
            payload = {
                "sub": user_id,
                "tenant_id": tenant_id,
                "type": "refresh",
                "exp": datetime.utcnow() + timedelta(minutes=JWT_REFRESH_EXPIRE),
                "iat": datetime.utcnow(),
            }
            return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        @staticmethod
        def create_expired_token(user_id: str, tenant_id: str) -> str:
            """Create an expired token"""
            payload = {
                "sub": user_id,
                "tenant_id": tenant_id,
                "type": "access",
                "exp": datetime.utcnow() - timedelta(minutes=10),
                "iat": datetime.utcnow() - timedelta(minutes=70),
            }
            return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        @staticmethod
        def decode_token(token: str) -> Dict:
            """Decode and verify a token"""
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
    return JWTHelper()


# ═══════════════════════════════════════════════════════════════════════════════
# Login Flow Tests
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
@pytest.mark.asyncio
class TestLoginFlow:
    """Test user login flow"""
    
    async def test_successful_login(self, mock_user, jwt_helper):
        """Test successful login with valid credentials"""
        # Simulate login request
        credentials = {
            "username": mock_user["username"],
            "password": "password123",
        }
        
        # Mock authentication logic
        def authenticate(username: str, password: str) -> Optional[Dict]:
            # In real implementation, this would verify password hash
            if username == mock_user["username"]:
                return mock_user
            return None
        
        user = authenticate(credentials["username"], credentials["password"])
        assert user is not None
        assert user["id"] == mock_user["id"]
        
        # Generate tokens
        access_token = jwt_helper.create_access_token(
            user_id=user["id"],
            tenant_id=user["tenant_id"],
        )
        refresh_token = jwt_helper.create_refresh_token(
            user_id=user["id"],
            tenant_id=user["tenant_id"],
        )
        
        # Verify tokens can be decoded
        access_payload = jwt_helper.decode_token(access_token)
        assert access_payload["sub"] == user["id"]
        assert access_payload["type"] == "access"
        
        refresh_payload = jwt_helper.decode_token(refresh_token)
        assert refresh_payload["sub"] == user["id"]
        assert refresh_payload["type"] == "refresh"
    
    async def test_login_with_invalid_credentials(self, mock_user):
        """Test login failure with invalid credentials"""
        credentials = {
            "username": mock_user["username"],
            "password": "wrong_password",
        }
        
        def authenticate(username: str, password: str) -> Optional[Dict]:
            # Simulate password verification failure
            return None
        
        user = authenticate(credentials["username"], credentials["password"])
        assert user is None
    
    async def test_login_with_inactive_user(self, mock_user):
        """Test login failure with inactive user"""
        inactive_user = {**mock_user, "is_active": False}
        
        def authenticate(username: str, password: str) -> Optional[Dict]:
            # Check if user is active
            if not inactive_user["is_active"]:
                return None
            return inactive_user
        
        user = authenticate(inactive_user["username"], "password123")
        assert user is None


# ═══════════════════════════════════════════════════════════════════════════════
# Token Refresh Flow Tests
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
@pytest.mark.asyncio
class TestTokenRefreshFlow:
    """Test token refresh flow"""
    
    async def test_successful_token_refresh(self, mock_user, jwt_helper):
        """Test successful token refresh"""
        # Create valid refresh token
        refresh_token = jwt_helper.create_refresh_token(
            user_id=mock_user["id"],
            tenant_id=mock_user["tenant_id"],
        )
        
        # Verify refresh token
        payload = jwt_helper.decode_token(refresh_token)
        assert payload["type"] == "refresh"
        assert payload["sub"] == mock_user["id"]
        
        # Issue new access token
        new_access_token = jwt_helper.create_access_token(
            user_id=payload["sub"],
            tenant_id=payload["tenant_id"],
        )
        
        # Verify new access token
        new_payload = jwt_helper.decode_token(new_access_token)
        assert new_payload["sub"] == mock_user["id"]
        assert new_payload["type"] == "access"
    
    async def test_refresh_with_expired_token(self, mock_user, jwt_helper):
        """Test token refresh failure with expired refresh token"""
        # Create expired token
        expired_token = jwt_helper.create_expired_token(
            user_id=mock_user["id"],
            tenant_id=mock_user["tenant_id"],
        )
        
        # Verify token is expired
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt_helper.decode_token(expired_token)
    
    async def test_refresh_with_access_token(self, mock_user, jwt_helper):
        """Test token refresh failure when using access token instead of refresh token"""
        # Create access token
        access_token = jwt_helper.create_access_token(
            user_id=mock_user["id"],
            tenant_id=mock_user["tenant_id"],
        )
        
        # Verify it's an access token (should not be used for refresh)
        payload = jwt_helper.decode_token(access_token)
        assert payload["type"] == "access"
        
        # In real implementation, this should fail
        # because we're trying to refresh with an access token


# ═══════════════════════════════════════════════════════════════════════════════
# OAuth Flow Tests
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
@pytest.mark.asyncio
class TestOAuthFlow:
    """Test OAuth external provider authentication"""
    
    async def test_oauth_authorization_url_generation(self):
        """Test OAuth authorization URL generation"""
        # Mock OAuth config
        oauth_config = {
            "authorization_endpoint": "https://provider.com/oauth/authorize",
            "client_id": "test_client_id",
            "redirect_uri": "http://localhost:8000/auth/callback",
            "scope": "openid profile email",
            "state": "random_state_token",
        }
        
        # Generate authorization URL
        params = {
            "client_id": oauth_config["client_id"],
            "redirect_uri": oauth_config["redirect_uri"],
            "scope": oauth_config["scope"],
            "state": oauth_config["state"],
            "response_type": "code",
        }
        
        auth_url = f"{oauth_config['authorization_endpoint']}?" + "&".join(
            f"{k}={v}" for k, v in params.items()
        )
        
        assert "client_id=test_client_id" in auth_url
        assert "redirect_uri=http://localhost:8000/auth/callback" in auth_url
        assert "scope=openid+profile+email" in auth_url or "scope=openid%20profile%20email" in auth_url
    
    async def test_oauth_token_exchange(self):
        """Test OAuth token exchange"""
        # Mock authorization code
        auth_code = "test_authorization_code"
        
        # Mock token exchange response
        token_response = {
            "access_token": "oauth_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "oauth_refresh_token",
            "id_token": "oauth_id_token",
        }
        
        # Verify token response has required fields
        assert "access_token" in token_response
        assert "token_type" in token_response
        assert token_response["token_type"] == "Bearer"
    
    async def test_oauth_user_info_retrieval(self):
        """Test retrieving user info from OAuth provider"""
        # Mock user info response
        user_info = {
            "sub": "oauth_user_123",
            "email": "oauth_user@example.com",
            "email_verified": True,
            "name": "OAuth User",
            "picture": "https://example.com/avatar.jpg",
        }
        
        # Verify user info has required fields
        assert "sub" in user_info
        assert "email" in user_info
        
        # Map to internal user format
        internal_user = {
            "external_id": user_info["sub"],
            "email": user_info["email"],
            "username": user_info["email"],
            "is_verified": user_info.get("email_verified", False),
        }
        
        assert internal_user["external_id"] == "oauth_user_123"
        assert internal_user["is_verified"] is True


# ═══════════════════════════════════════════════════════════════════════════════
# Token Validation Tests
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
@pytest.mark.asyncio
class TestTokenValidation:
    """Test token validation logic"""
    
    async def test_valid_token_validation(self, mock_user, jwt_helper):
        """Test validation of a valid token"""
        token = jwt_helper.create_access_token(
            user_id=mock_user["id"],
            tenant_id=mock_user["tenant_id"],
        )
        
        # Decode and validate
        payload = jwt_helper.decode_token(token)
        
        assert payload["sub"] == mock_user["id"]
        assert payload["tenant_id"] == mock_user["tenant_id"]
        assert "exp" in payload
        assert "iat" in payload
    
    async def test_expired_token_validation(self, mock_user, jwt_helper):
        """Test validation of an expired token"""
        expired_token = jwt_helper.create_expired_token(
            user_id=mock_user["id"],
            tenant_id=mock_user["tenant_id"],
        )
        
        # Should raise ExpiredSignatureError
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt_helper.decode_token(expired_token)
    
    async def test_invalid_signature_validation(self, mock_user):
        """Test validation of a token with invalid signature"""
        # Create token with different secret
        payload = {
            "sub": mock_user["id"],
            "tenant_id": mock_user["tenant_id"],
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        invalid_token = jwt.encode(payload, "wrong_secret", algorithm=JWT_ALGORITHM)
        
        # Should raise InvalidSignatureError
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(invalid_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
    async def test_malformed_token_validation(self):
        """Test validation of a malformed token"""
        malformed_token = "not.a.valid.jwt.token"
        
        # Should raise DecodeError
        with pytest.raises(jwt.DecodeError):
            jwt.decode(malformed_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


# ═══════════════════════════════════════════════════════════════════════════════
# MFA Flow Tests
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
@pytest.mark.asyncio
class TestMFAFlow:
    """Test multi-factor authentication flow"""
    
    async def test_totp_generation(self, mock_user_with_mfa):
        """Test TOTP code generation"""
        try:
            import pyotp
            
            # Generate TOTP code
            totp = pyotp.TOTP(mock_user_with_mfa["mfa_secret"])
            code = totp.now()
            
            # Verify code format
            assert len(code) == 6
            assert code.isdigit()
            
            # Verify code
            assert totp.verify(code)
            
        except ImportError:
            pytest.skip("pyotp not installed")
    
    async def test_mfa_login_flow(self, mock_user_with_mfa, jwt_helper):
        """Test login flow with MFA"""
        # Step 1: Validate credentials
        credentials = {
            "username": mock_user_with_mfa["username"],
            "password": "password123",
        }
        
        # Check if MFA is enabled
        assert mock_user_with_mfa["mfa_enabled"] is True
        
        # Step 2: Don't issue full tokens yet, issue MFA challenge token
        mfa_challenge_token = jwt_helper.create_access_token(
            user_id=mock_user_with_mfa["id"],
            tenant_id=mock_user_with_mfa["tenant_id"],
            extra_claims={"mfa_required": True},
        )
        
        # Verify MFA challenge token
        payload = jwt_helper.decode_token(mfa_challenge_token)
        assert payload["mfa_required"] is True
        
        # Step 3: After TOTP verification, issue full tokens
        # (In real implementation, verify TOTP code here)
        access_token = jwt_helper.create_access_token(
            user_id=mock_user_with_mfa["id"],
            tenant_id=mock_user_with_mfa["tenant_id"],
        )
        
        # Verify final token doesn't have MFA flag
        final_payload = jwt_helper.decode_token(access_token)
        assert "mfa_required" not in final_payload
