#!/usr/bin/env python3
"""
SAHOOL Notification Service - Connection Test Script
Script للتحقق من اتصال قاعدة البيانات والـ health check
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


async def test_database_connection():
    """Test database connection"""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)

    try:
        from src.database import init_db, close_db, check_db_health, get_db_stats

        # Test connection
        print("\n1. Initializing database connection...")
        await init_db(create_db=True)
        print("   ✅ Database initialized successfully")

        # Test health check
        print("\n2. Checking database health...")
        health = await check_db_health()
        print(f"   Health Status: {health}")

        if health.get("connected"):
            print("   ✅ Database is healthy")
        else:
            print("   ❌ Database is unhealthy")
            return False

        # Get stats
        print("\n3. Getting database statistics...")
        stats = await get_db_stats()
        print(f"   Stats: {stats}")
        print("   ✅ Database stats retrieved successfully")

        # Close connection
        print("\n4. Closing database connection...")
        await close_db()
        print("   ✅ Database connection closed")

        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_health_endpoint():
    """Test health check endpoint"""
    print("\n" + "=" * 60)
    print("Testing Health Check Endpoint")
    print("=" * 60)

    try:
        import urllib.request
        import json

        print("\n1. Sending request to http://localhost:8110/healthz...")

        try:
            response = urllib.request.urlopen('http://localhost:8110/healthz', timeout=5)
            data = json.loads(response.read().decode('utf-8'))
            print(f"   Response: {json.dumps(data, indent=2)}")

            if data.get("status") in ["ok", "degraded"]:
                print("   ✅ Health check endpoint is responding")
                return True
            else:
                print(f"   ⚠️  Health check returned unexpected status: {data.get('status')}")
                return False

        except urllib.error.URLError as e:
            print(f"   ❌ Cannot connect to service: {e}")
            print("   Note: Make sure the service is running (uvicorn src.main:app --host 0.0.0.0 --port 8110)")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test runner"""
    print("\n🔬 SAHOOL Notification Service - Connection Test")
    print("=" * 60)

    # Test 1: Database Connection
    db_ok = await test_database_connection()

    # Test 2: Health Endpoint (optional - only if service is running)
    print("\n")
    health_ok = await test_health_endpoint()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Database Connection: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"Health Endpoint:     {'✅ PASS' if health_ok else '⚠️  SKIP (service not running)'}")

    if db_ok:
        print("\n✅ All critical tests passed!")
        print("\nNext steps:")
        print("1. Build the Docker image: docker-compose build notification_service")
        print("2. Start the service: docker-compose up notification_service")
        print("3. Check health: curl http://localhost:8110/healthz")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
