"""
Service-to-Service Authentication Test Examples
Quick tests to verify the service auth system is working correctly
"""

import os
import sys

# Set up environment for testing
os.environ["JWT_SECRET"] = "test-secret-key-minimum-32-characters-long"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_ISSUER"] = "sahool-platform"
os.environ["JWT_AUDIENCE"] = "sahool-api"

from service_auth import (
    ALLOWED_SERVICES,
    SERVICE_COMMUNICATION_MATRIX,
    ServiceToken,
    check_service_call_rate_limit,
    create_service_token,
    get_allowed_targets,
    get_audit_log,
    get_rate_limiter,
    get_revocation_store,
    get_service_audit_logs,
    get_service_call_stats,
    is_service_authorized,
    is_service_token_revoked,
    log_service_call,
    revoke_service_token,
    verify_service_token,
)


def test_basic_token_creation():
    """Test basic service token creation and verification"""
    print("\n=== Test 1: Basic Token Creation ===")

    try:
        # Create a token
        token = create_service_token(service_name="farm-service", target_service="field-service", ttl=300)
        print("✓ Token created successfully")
        print(f"  Token (first 50 chars): {token[:50]}...")

        # Verify the token
        payload = verify_service_token(token)
        print("✓ Token verified successfully")
        print(f"  Service Name: {payload['service_name']}")
        print(f"  Target Service: {payload['target_service']}")
        print(f"  Expires: {payload['exp']}")
        print(f"  Issued: {payload['iat']}")

        assert payload["service_name"] == "farm-service"
        assert payload["target_service"] == "field-service"
        print("✓ All assertions passed")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

    return True


def test_service_class():
    """Test ServiceToken class methods"""
    print("\n=== Test 2: ServiceToken Class ===")

    try:
        # Create using class method
        token = ServiceToken.create(
            service_name="crop-service",
            target_service="weather-service",
            ttl=600,
            extra_claims={"request_id": "test-123"},
        )
        print("✓ Token created with ServiceToken.create()")

        # Verify using class method
        payload = ServiceToken.verify(token)
        print("✓ Token verified with ServiceToken.verify()")
        print(f"  Service: {payload['service_name']} → {payload['target_service']}")

        assert payload["service_name"] == "crop-service"
        assert payload["target_service"] == "weather-service"
        print("✓ All assertions passed")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

    return True


def test_unauthorized_service():
    """Test that unauthorized service calls are rejected"""
    print("\n=== Test 3: Unauthorized Service Call ===")

    try:
        # This should fail - notification-service cannot call farm-service
        create_service_token(service_name="notification-service", target_service="farm-service", ttl=300)
        print("✗ Test failed: Should have raised an exception")
        return False

    except Exception as e:
        print(f"✓ Correctly rejected unauthorized call: {e}")
        return True


def test_invalid_service():
    """Test that invalid service names are rejected"""
    print("\n=== Test 4: Invalid Service Name ===")

    try:
        # This should fail - invalid service name
        create_service_token(service_name="invalid-service", target_service="field-service", ttl=300)
        print("✗ Test failed: Should have raised an exception")
        return False

    except Exception as e:
        print(f"✓ Correctly rejected invalid service: {e}")
        return True


def test_service_authorization_check():
    """Test service authorization checking"""
    print("\n=== Test 5: Service Authorization Check ===")

    # Authorized calls
    authorized_pairs = [
        ("farm-service", "field-service"),
        ("crop-service", "weather-service"),
        ("field-service", "precision-ag-service"),
    ]

    for service, target in authorized_pairs:
        if is_service_authorized(service, target):
            print(f"✓ {service} → {target} is authorized")
        else:
            print(f"✗ {service} → {target} should be authorized")
            return False

    # Unauthorized calls
    unauthorized_pairs = [
        ("notification-service", "farm-service"),
        ("analytics-service", "crop-service"),
    ]

    for service, target in unauthorized_pairs:
        if not is_service_authorized(service, target):
            print(f"✓ {service} → {target} is correctly unauthorized")
        else:
            print(f"✗ {service} → {target} should be unauthorized")
            return False

    return True


def test_get_allowed_targets():
    """Test getting allowed target services"""
    print("\n=== Test 6: Get Allowed Targets ===")

    # Test farm-service
    targets = get_allowed_targets("farm-service")
    print(f"farm-service can call: {targets}")

    expected_targets = [
        "field-service",
        "crop-service",
        "equipment-service",
        "user-service",
        "tenant-service",
    ]
    for target in expected_targets:
        if target not in targets:
            print(f"✗ Missing expected target: {target}")
            return False

    print("✓ All expected targets found")

    # Test idp-service (should call all services)
    idp_targets = get_allowed_targets("idp-service")
    print(f"idp-service can call {len(idp_targets)} services")

    if len(idp_targets) != len(ALLOWED_SERVICES):
        print("✗ IDP should be able to call all services")
        return False

    print("✓ IDP can call all services")
    return True


def test_all_services_in_matrix():
    """Test that all services are properly defined in the matrix"""
    print("\n=== Test 7: Service Matrix Validation ===")

    for service in ALLOWED_SERVICES:
        if service not in SERVICE_COMMUNICATION_MATRIX:
            print(f"✗ Service {service} not in communication matrix")
            return False

    print(f"✓ All {len(ALLOWED_SERVICES)} services defined in matrix")

    # Count total communication paths
    total_paths = sum(len(targets) for targets in SERVICE_COMMUNICATION_MATRIX.values())
    print(f"✓ Total communication paths: {total_paths}")

    return True


def test_token_expiration():
    """Test token with very short TTL"""
    print("\n=== Test 8: Token Expiration ===")
    import time

    try:
        # Create token with 1 second TTL
        token = create_service_token(service_name="farm-service", target_service="field-service", ttl=1)
        print("✓ Token created with 1 second TTL")

        # Verify immediately (should work)
        verify_service_token(token)
        print("✓ Token verified immediately")

        # Wait 2 seconds
        print("  Waiting 2 seconds...")
        time.sleep(2)

        # Try to verify (should fail)
        try:
            verify_service_token(token)
            print("✗ Expired token should have been rejected")
            return False
        except Exception as e:
            print(f"✓ Expired token correctly rejected: {e}")
            return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_service_token_revocation():
    """Test service token revocation functionality"""
    print("\n=== Test 9: Service Token Revocation ===")

    try:
        # Create a token
        token = create_service_token(service_name="crop-service", target_service="advisory-service", ttl=300)
        print("✓ Token created")

        # Verify it works
        payload = verify_service_token(token)
        print("✓ Token verified successfully")
        jti = payload["jti"]

        # Revoke the token
        revoke_service_token(jti)
        print(f"✓ Token revoked: {jti}")

        # Check revocation status
        if is_service_token_revoked(jti):
            print("✓ Token correctly marked as revoked")
        else:
            print("✗ Token should be marked as revoked")
            return False

        # Try to verify revoked token (should fail)
        try:
            verify_service_token(token)
            print("✗ Revoked token should have been rejected")
            return False
        except Exception as e:
            print(f"✓ Revoked token correctly rejected: {e}")
            return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_audit_logging():
    """Test service call audit logging"""
    print("\n=== Test 10: Audit Logging ===")

    try:
        # Create and verify a token to get JTI
        token = create_service_token(
            service_name="field-service",
            target_service="weather-service",
            ttl=300,
        )
        payload = verify_service_token(token)
        jti = payload["jti"]

        # Log some service calls
        log_service_call(
            source_service="field-service",
            target_service="weather-service",
            jti=jti,
            success=True,
        )
        print("✓ Logged successful service call")

        log_service_call(
            source_service="field-service",
            target_service="weather-service",
            jti=jti,
            success=False,
            error_message="Connection timeout",
        )
        print("✓ Logged failed service call")

        # Get audit logs
        logs = get_service_audit_logs("field-service", limit=10)
        print(f"✓ Retrieved {len(logs)} audit log entries")

        if len(logs) >= 2:
            print("✓ Audit log contains expected entries")
            return True
        else:
            print("✗ Not enough audit log entries")
            return False

    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_rate_limiting():
    """Test service call rate limiting"""
    print("\n=== Test 11: Rate Limiting ===")

    try:
        limiter = get_rate_limiter()
        print(f"✓ Rate limiter configured: {limiter.calls_per_minute} calls/min")

        # Check rate limit multiple times
        for i in range(3):
            allowed, remaining = check_service_call_rate_limit("advisory-service", "notification-service")
            print(f"  Call {i + 1}: Allowed={allowed}, Remaining={remaining}")

        # Test stats
        stats = get_service_call_stats("advisory-service", "notification-service")
        print("✓ Service call stats retrieved")
        print(f"  Recent calls: {stats['recent_call_count']}")
        print(f"  Success rate: {stats['success_rate']:.0%}")

        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_revocation_store_access():
    """Test access to revocation store"""
    print("\n=== Test 12: Revocation Store Access ===")

    try:
        # Get the revocation store
        store = get_revocation_store()
        print("✓ Revocation store accessed")

        # Create and revoke a token
        token = create_service_token(
            service_name="equipment-service",
            target_service="inventory-service",
            ttl=300,
        )
        payload = verify_service_token(token)
        jti = payload["jti"]

        # Revoke using store
        store.revoke(jti)
        print(f"✓ Token revoked via store: {jti}")

        # Verify it's revoked
        if store.is_revoked(jti):
            print("✓ Revocation check passed")
            return True
        else:
            print("✗ Token should be revoked")
            return False

    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 60)
    print("Service-to-Service Authentication Test Suite")
    print("=" * 60)

    tests = [
        ("Basic Token Creation", test_basic_token_creation),
        ("ServiceToken Class", test_service_class),
        ("Unauthorized Service Call", test_unauthorized_service),
        ("Invalid Service Name", test_invalid_service),
        ("Service Authorization Check", test_service_authorization_check),
        ("Get Allowed Targets", test_get_allowed_targets),
        ("Service Matrix Validation", test_all_services_in_matrix),
        ("Token Expiration", test_token_expiration),
        ("Service Token Revocation", test_service_token_revocation),
        ("Audit Logging", test_audit_logging),
        ("Rate Limiting", test_rate_limiting),
        ("Revocation Store Access", test_revocation_store_access),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results.append((name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
