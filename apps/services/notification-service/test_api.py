#!/usr/bin/env python3
"""
SAHOOL Notification Service - API Test Script
سكريبت اختبار واجهة برمجة التطبيقات

Tests the notification service API endpoints with PostgreSQL backend.
"""

import asyncio
from datetime import date

import httpx

BASE_URL = "http://localhost:8110"


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    END = "\033[0m"


def print_test(name: str):
    print(f"\n{Colors.BLUE}▶ Testing: {name}{Colors.END}")


def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_info(message: str):
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")


async def test_health_check():
    """Test health check endpoint"""
    print_test("Health Check")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/healthz")

        if response.status_code == 200:
            data = response.json()
            print_success("Health check passed")
            print_info(f"Service: {data.get('service')} v{data.get('version')}")
            print_info(f"Database status: {data.get('database', {}).get('status', 'unknown')}")
            print_info(f"NATS connected: {data.get('nats_connected')}")

            if data.get("stats"):
                stats = data["stats"]
                print_info(f"Total notifications: {stats.get('total_notifications', 0)}")
                print_info(f"Pending: {stats.get('pending_notifications', 0)}")

            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False


async def test_create_notification():
    """Test creating a custom notification"""
    print_test("Create Custom Notification")

    payload = {
        "type": "weather_alert",
        "priority": "high",
        "title": "Weather Alert Test",
        "title_ar": "اختبار تنبيه طقس",
        "body": "This is a test weather alert",
        "body_ar": "هذا اختبار لتنبيه الطقس",
        "data": {"temperature": 35, "humidity": 80},
        "target_farmers": ["farmer-1"],
        "channels": ["in_app", "push"],
        "expires_in_hours": 24,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/v1/notifications", json=payload)

        if response.status_code == 200:
            data = response.json()
            print_success("Notification created")
            print_info(f"ID: {data.get('id')}")
            print_info(f"Type: {data.get('type')} ({data.get('type_ar')})")
            print_info(f"Priority: {data.get('priority')} ({data.get('priority_ar')})")
            return data.get("id")
        else:
            print_error(f"Failed to create notification: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None


async def test_weather_alert():
    """Test creating weather alert"""
    print_test("Create Weather Alert")

    payload = {
        "governorates": ["sanaa", "ibb"],
        "alert_type": "frost",
        "severity": "critical",
        "expected_date": date.today().isoformat(),
        "details": {"min_temperature": -2, "duration_hours": 8},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/v1/alerts/weather", json=payload)

        if response.status_code == 200:
            data = response.json()
            print_success("Weather alert created")
            print_info(f"ID: {data.get('id')}")
            print_info(f"Title (AR): {data.get('title_ar')}")
            return data.get("id")
        else:
            print_error(f"Failed to create weather alert: {response.status_code}")
            return None


async def test_pest_alert():
    """Test creating pest alert"""
    print_test("Create Pest Alert")

    payload = {
        "governorate": "sanaa",
        "pest_name": "Aphids",
        "pest_name_ar": "المن",
        "affected_crops": ["tomato", "wheat"],
        "severity": "high",
        "recommendations": ["Use organic pesticides", "Increase monitoring"],
        "recommendations_ar": ["استخدم المبيدات العضوية", "زد من المراقبة"],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/v1/alerts/pest", json=payload)

        if response.status_code == 200:
            data = response.json()
            print_success("Pest alert created")
            print_info(f"ID: {data.get('id')}")
            print_info(f"Title (AR): {data.get('title_ar')}")
            return data.get("id")
        else:
            print_error(f"Failed to create pest alert: {response.status_code}")
            return None


async def test_irrigation_reminder():
    """Test creating irrigation reminder"""
    print_test("Create Irrigation Reminder")

    payload = {
        "farmer_id": "farmer-1",
        "field_id": "field-1",
        "field_name": "North Field",
        "crop": "tomato",
        "water_needed_mm": 25.5,
        "urgency": "medium",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/v1/reminders/irrigation", json=payload)

        if response.status_code == 200:
            data = response.json()
            print_success("Irrigation reminder created")
            print_info(f"ID: {data.get('id')}")
            print_info(f"Title (AR): {data.get('title_ar')}")
            return data.get("id")
        else:
            print_error(f"Failed to create irrigation reminder: {response.status_code}")
            return None


async def test_get_farmer_notifications():
    """Test getting farmer notifications"""
    print_test("Get Farmer Notifications")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/v1/notifications/farmer/farmer-1")

        if response.status_code == 200:
            data = response.json()
            print_success("Retrieved farmer notifications")
            print_info(f"Total: {data.get('total')}")
            print_info(f"Unread: {data.get('unread_count')}")

            notifications = data.get("notifications", [])
            if notifications:
                print_info(f"Latest notification: {notifications[0].get('title_ar')}")

            return len(notifications) > 0
        else:
            print_error(f"Failed to get farmer notifications: {response.status_code}")
            return False


async def test_mark_as_read(notification_id: str):
    """Test marking notification as read"""
    print_test("Mark Notification as Read")

    if not notification_id:
        print_info("Skipping: No notification ID")
        return False

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{BASE_URL}/v1/notifications/{notification_id}/read",
            params={"farmer_id": "farmer-1"},
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Notification marked as read")
            print_info(f"Is read: {data.get('is_read')}")
            return True
        else:
            print_error(f"Failed to mark as read: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False


async def test_broadcast_notifications():
    """Test getting broadcast notifications"""
    print_test("Get Broadcast Notifications")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/v1/notifications/broadcast?limit=10")

        if response.status_code == 200:
            data = response.json()
            print_success("Retrieved broadcast notifications")
            print_info(f"Total: {data.get('total')}")

            notifications = data.get("notifications", [])
            if notifications:
                print_info(f"Latest: {notifications[0].get('title_ar')}")

            return True
        else:
            print_error(f"Failed to get broadcast notifications: {response.status_code}")
            return False


async def test_update_preferences():
    """Test updating notification preferences"""
    print_test("Update Notification Preferences")

    payload = {
        "farmer_id": "farmer-1",
        "weather_alerts": True,
        "pest_alerts": True,
        "irrigation_reminders": True,
        "crop_health_alerts": True,
        "market_prices": False,
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "06:00",
        "min_priority": "medium",
    }

    async with httpx.AsyncClient() as client:
        response = await client.put(f"{BASE_URL}/v1/farmers/farmer-1/preferences", json=payload)

        if response.status_code == 200:
            data = response.json()
            print_success("Preferences updated")
            print_info(f"Message: {data.get('message')}")
            return True
        else:
            print_error(f"Failed to update preferences: {response.status_code}")
            return False


async def test_stats():
    """Test getting statistics"""
    print_test("Get Statistics")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/v1/stats")

        if response.status_code == 200:
            data = response.json()
            print_success("Statistics retrieved")
            print_info(f"Total notifications: {data.get('total_notifications')}")
            print_info(f"Pending: {data.get('pending_notifications')}")
            print_info(f"Active weather alerts: {data.get('active_weather_alerts')}")
            print_info(f"Active pest alerts: {data.get('active_pest_alerts')}")

            by_type = data.get("by_type", {})
            if by_type:
                print_info(f"By type: {by_type}")

            return True
        else:
            print_error(f"Failed to get statistics: {response.status_code}")
            return False


async def main():
    """Run all tests"""
    print(f"\n{Colors.GREEN}{'=' * 60}")
    print("  SAHOOL Notification Service - API Tests")
    print("  اختبار واجهة برمجة التطبيقات لخدمة الإشعارات")
    print(f"{'=' * 60}{Colors.END}\n")

    print_info(f"Testing API at: {BASE_URL}")
    print_info("Make sure the service is running!")

    # Run tests
    tests_passed = 0
    tests_total = 0

    # Health check
    tests_total += 1
    if await test_health_check():
        tests_passed += 1

    # Create notifications
    tests_total += 1
    notification_id = await test_create_notification()
    if notification_id:
        tests_passed += 1

    tests_total += 1
    if await test_weather_alert():
        tests_passed += 1

    tests_total += 1
    if await test_pest_alert():
        tests_passed += 1

    tests_total += 1
    if await test_irrigation_reminder():
        tests_passed += 1

    # Read notifications
    tests_total += 1
    if await test_get_farmer_notifications():
        tests_passed += 1

    tests_total += 1
    if await test_mark_as_read(notification_id):
        tests_passed += 1

    tests_total += 1
    if await test_broadcast_notifications():
        tests_passed += 1

    # Preferences
    tests_total += 1
    if await test_update_preferences():
        tests_passed += 1

    # Statistics
    tests_total += 1
    if await test_stats():
        tests_passed += 1

    # Summary
    print(f"\n{Colors.GREEN}{'=' * 60}")
    print("  Test Results | نتائج الاختبار")
    print(f"{'=' * 60}{Colors.END}\n")

    if tests_passed == tests_total:
        print_success(f"All tests passed! ({tests_passed}/{tests_total})")
        print_success("PostgreSQL integration is working correctly! ✓")
    else:
        print_error(f"Some tests failed: {tests_passed}/{tests_total} passed")

    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
    except Exception as e:
        print_error(f"Test failed with error: {e}")
        import traceback

        traceback.print_exc()
