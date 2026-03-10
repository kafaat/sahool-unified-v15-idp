"""
Custom Test Assertions
======================
تأكيدات اختبار مخصصة

Custom assertion functions for SAHOOL platform testing.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import json
from typing import Any


def assert_api_response(
    response: Any,
    expected_status: int = 200,
    expected_keys: list[str] | None = None,
    error_message: str | None = None,
) -> dict:
    """
    Assert API response is valid.
    التحقق من صحة استجابة API

    Args:
        response: HTTP response object (httpx, requests, or TestClient)
        expected_status: Expected HTTP status code
        expected_keys: Keys that should exist in response body
        error_message: Custom error message

    Returns:
        Response JSON body

    Raises:
        AssertionError: If assertions fail
    """
    # Check status code
    assert response.status_code == expected_status, (
        f"Expected status {expected_status}, got {response.status_code}. "
        f"{error_message or ''}\n"
        f"Response: {response.text[:500] if hasattr(response, 'text') else 'N/A'}"
    )

    # Parse JSON
    try:
        data = response.json()
    except (json.JSONDecodeError, ValueError):
        if expected_status < 300:  # Success responses should have JSON
            raise AssertionError(f"Response is not valid JSON: {response.text[:200]}")
        return {}

    # Check expected keys
    if expected_keys:
        for key in expected_keys:
            assert key in data, f"Expected key '{key}' not in response. Available keys: {list(data.keys())}"

    return data


def assert_response_ok(response: Any, expected_keys: list[str] | None = None) -> dict:
    """
    Assert response is successful (2xx status).
    التحقق من نجاح الاستجابة

    Args:
        response: HTTP response object
        expected_keys: Keys that should exist in response

    Returns:
        Response JSON body
    """
    assert 200 <= response.status_code < 300, (
        f"Expected success status (2xx), got {response.status_code}. "
        f"Response: {response.text[:500] if hasattr(response, 'text') else 'N/A'}"
    )

    try:
        data = response.json()
    except (json.JSONDecodeError, ValueError):
        return {}

    if expected_keys:
        for key in expected_keys:
            assert key in data, f"Expected key '{key}' not in response"

    return data


def assert_response_error(
    response: Any,
    expected_status: int = 400,
    error_code: str | None = None,
) -> dict:
    """
    Assert response is an error.
    التحقق من أن الاستجابة خطأ

    Args:
        response: HTTP response object
        expected_status: Expected error status code
        error_code: Expected error code in response body

    Returns:
        Response JSON body
    """
    assert response.status_code == expected_status, f"Expected status {expected_status}, got {response.status_code}"

    try:
        data = response.json()
    except (json.JSONDecodeError, ValueError):
        return {}

    if error_code:
        actual_code = data.get("error_code") or data.get("code") or data.get("error")
        assert actual_code == error_code, f"Expected error code '{error_code}', got '{actual_code}'"

    return data


def assert_json_schema(data: dict, schema: dict) -> None:
    """
    Assert JSON data matches schema.
    التحقق من تطابق البيانات مع المخطط

    Args:
        data: JSON data to validate
        schema: Expected schema (simplified format)

    Schema format:
        {
            "required_field": str,
            "optional_field?": int,
            "nested": {"field": str},
            "list_field": [str],
        }
    """
    for key, expected_type in schema.items():
        is_optional = key.endswith("?")
        actual_key = key.rstrip("?")

        if actual_key not in data:
            if not is_optional:
                raise AssertionError(f"Required field '{actual_key}' missing from data")
            continue

        value = data[actual_key]

        # Handle nested dict
        if isinstance(expected_type, dict):
            assert isinstance(value, dict), f"Field '{actual_key}' should be dict, got {type(value).__name__}"
            assert_json_schema(value, expected_type)

        # Handle list type
        elif isinstance(expected_type, list) and len(expected_type) == 1:
            assert isinstance(value, list), f"Field '{actual_key}' should be list, got {type(value).__name__}"
            for item in value:
                assert isinstance(item, expected_type[0]), (
                    f"List item in '{actual_key}' should be {expected_type[0].__name__}"
                )

        # Handle simple type
        elif expected_type is not None:
            assert isinstance(value, expected_type), (
                f"Field '{actual_key}' should be {expected_type.__name__}, got {type(value).__name__}"
            )


def assert_event_published(
    mock_publisher,
    subject: str,
    event_type: type | None = None,
    count: int = 1,
) -> list:
    """
    Assert event was published.
    التحقق من نشر الحدث

    Args:
        mock_publisher: Mock event publisher
        subject: Expected NATS subject
        event_type: Expected event type class
        count: Expected number of publishes

    Returns:
        List of published events matching criteria
    """
    calls = mock_publisher.publish_event.call_args_list

    matching = []
    for call in calls:
        call_subject = call[0][0] if call[0] else call[1].get("subject")
        call_event = call[0][1] if len(call[0]) > 1 else call[1].get("event")

        if call_subject == subject:
            if event_type is None or isinstance(call_event, event_type):
                matching.append(call_event)

    assert len(matching) >= count, (
        f"Expected at least {count} publish(es) to '{subject}', found {len(matching)}. Total calls: {len(calls)}"
    )

    return matching


def assert_field_valid(field_data: dict) -> None:
    """
    Assert field data is valid.
    التحقق من صحة بيانات الحقل

    Args:
        field_data: Field data dictionary
    """
    required_fields = ["id", "name", "area_hectares"]

    for field in required_fields:
        assert field in field_data, f"Required field '{field}' missing"

    # Validate area
    area = field_data.get("area_hectares")
    assert isinstance(area, (int, float)), "area_hectares must be numeric"
    assert area > 0, "area_hectares must be positive"

    # Validate geometry if present
    geometry = field_data.get("geometry")
    if geometry:
        assert "type" in geometry, "geometry must have 'type'"
        assert geometry["type"] in ["Polygon", "MultiPolygon"], f"Invalid geometry type: {geometry['type']}"
        assert "coordinates" in geometry, "geometry must have 'coordinates'"


def assert_datetime_format(value: str, allow_none: bool = False) -> None:
    """
    Assert value is valid ISO datetime format.
    التحقق من صيغة التاريخ والوقت

    Args:
        value: String to validate
        allow_none: Whether None is acceptable
    """
    if value is None:
        if allow_none:
            return
        raise AssertionError("Expected datetime string, got None")

    from datetime import datetime

    try:
        # Try parsing ISO format
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise AssertionError(f"Invalid datetime format: {value}")


def assert_uuid_format(value: str, allow_none: bool = False) -> None:
    """
    Assert value is valid UUID format.
    التحقق من صيغة UUID

    Args:
        value: String to validate
        allow_none: Whether None is acceptable
    """
    if value is None:
        if allow_none:
            return
        raise AssertionError("Expected UUID string, got None")

    import re

    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )

    assert uuid_pattern.match(value), f"Invalid UUID format: {value}"


def assert_pagination(response_data: dict, page: int = 1, per_page: int = 10) -> None:
    """
    Assert pagination response is valid.
    التحقق من صحة التصفح

    Args:
        response_data: Response data dictionary
        page: Expected page number
        per_page: Expected items per page
    """
    assert "items" in response_data, "Pagination response must have 'items'"
    assert isinstance(response_data["items"], list), "'items' must be a list"

    # Check pagination metadata
    pagination_keys = ["total", "page", "per_page", "pages"]
    for key in pagination_keys:
        assert key in response_data or f"pagination.{key}" in str(response_data), (
            f"Pagination response should include '{key}'"
        )


def assert_arabic_text(value: str) -> None:
    """
    Assert value contains Arabic text.
    التحقق من وجود نص عربي

    Args:
        value: String to validate
    """
    import re

    arabic_pattern = re.compile(r"[\u0600-\u06FF]")
    assert arabic_pattern.search(value), f"Expected Arabic text, got: {value[:50]}"


def assert_coordinates_valid(lat: float, lng: float) -> None:
    """
    Assert GPS coordinates are valid.
    التحقق من صحة الإحداثيات

    Args:
        lat: Latitude
        lng: Longitude
    """
    assert -90 <= lat <= 90, f"Invalid latitude: {lat}"
    assert -180 <= lng <= 180, f"Invalid longitude: {lng}"


def assert_in_saudi_arabia(lat: float, lng: float) -> None:
    """
    Assert coordinates are within Saudi Arabia.
    التحقق من أن الإحداثيات داخل المملكة العربية السعودية

    Args:
        lat: Latitude
        lng: Longitude
    """
    # Saudi Arabia bounding box (approximate)
    assert 16.0 <= lat <= 33.0, f"Latitude {lat} is outside Saudi Arabia"
    assert 34.0 <= lng <= 56.0, f"Longitude {lng} is outside Saudi Arabia"
