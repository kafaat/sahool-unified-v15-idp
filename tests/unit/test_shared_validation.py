"""
Unit Tests for Shared Validation Functions
Tests data validation, input sanitization, and business rule validation
"""

import re
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, ValidationError, field_validator

# ═══════════════════════════════════════════════════════════════════════════
# Helper Functions for Testing
# ═══════════════════════════════════════════════════════════════════════════


def is_valid_email(email: str) -> bool:
    """Validate email format"""
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_regex, email))


def is_valid_phone_yemen(phone: str) -> bool:
    """Validate Yemen phone number format"""
    # Yemen phone format: +967XXXXXXXXX or 967XXXXXXXXX or 7XXXXXXXX
    phone_regex = r"^(\+967|00967|967)?[1-9]\d{8}$"
    return bool(re.match(phone_regex, phone.replace(" ", "")))


def is_valid_uuid(value: str) -> bool:
    """Validate UUID format"""
    uuid_regex = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    return bool(re.match(uuid_regex, value.lower()))


def is_positive_number(value: float | int) -> bool:
    """Validate positive number"""
    return isinstance(value, (int, float)) and value > 0


def is_valid_date_range(start_date: datetime, end_date: datetime) -> bool:
    """Validate date range"""
    return start_date < end_date


def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input"""
    if not value:
        return ""
    # Remove extra whitespace
    value = " ".join(value.split())
    # Truncate to max length
    return value[:max_length]


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate geographic coordinates"""
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def validate_password_strength(password: str) -> dict:
    """Validate password strength"""
    result = {
        "is_valid": True,
        "errors": [],
        "strength": "weak",
    }

    if len(password) < 8:
        result["is_valid"] = False
        result["errors"].append("Password must be at least 8 characters")

    if not re.search(r"[A-Z]", password):
        result["is_valid"] = False
        result["errors"].append("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        result["is_valid"] = False
        result["errors"].append("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        result["is_valid"] = False
        result["errors"].append("Password must contain at least one digit")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result["errors"].append("Password should contain at least one special character")

    # Calculate strength
    if result["is_valid"]:
        strength_score = 0
        strength_score += 1 if len(password) >= 12 else 0
        strength_score += 1 if re.search(r'[!@#$%^&*(),.?":{}|<>]', password) else 0
        strength_score += 1 if len(set(password)) > len(password) * 0.7 else 0

        if strength_score >= 2:
            result["strength"] = "strong"
        elif strength_score >= 1:
            result["strength"] = "medium"

    return result


# ═══════════════════════════════════════════════════════════════════════════
# Email Validation Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestEmailValidation:
    """Test email validation"""

    def test_valid_email(self):
        """Test valid email addresses"""
        valid_emails = [
            "user@example.com",
            "test.user@example.com",
            "user+tag@example.co.uk",
            "user123@test-domain.com",
        ]

        for email in valid_emails:
            assert is_valid_email(email), f"Expected {email} to be valid"

    def test_invalid_email(self):
        """Test invalid email addresses"""
        invalid_emails = [
            "invalid",
            "invalid@",
            "@example.com",
            "user@",
            "user @example.com",
            "user@example",
            "",
            "user@.com",
        ]

        for email in invalid_emails:
            assert not is_valid_email(email), f"Expected {email} to be invalid"


# ═══════════════════════════════════════════════════════════════════════════
# Phone Number Validation Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestPhoneValidation:
    """Test phone number validation for Yemen"""

    def test_valid_yemen_phone(self):
        """Test valid Yemen phone numbers"""
        valid_phones = [
            "+967712345678",
            "967712345678",
            "00967712345678",
            "712345678",
            "+967 71 234 5678",  # With spaces
        ]

        for phone in valid_phones:
            assert is_valid_phone_yemen(phone), f"Expected {phone} to be valid"

    def test_invalid_yemen_phone(self):
        """Test invalid Yemen phone numbers"""
        invalid_phones = [
            "123456",  # Too short
            "+966712345678",  # Wrong country code
            "012345678",  # Starts with 0 after country code
            "+967 012345678",
            "",
            "abcdefghij",
        ]

        for phone in invalid_phones:
            assert not is_valid_phone_yemen(phone), f"Expected {phone} to be invalid"


# ═══════════════════════════════════════════════════════════════════════════
# UUID Validation Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestUUIDValidation:
    """Test UUID validation"""

    def test_valid_uuid(self):
        """Test valid UUIDs"""
        valid_uuids = [
            "550e8400-e29b-41d4-a716-446655440000",
            "123e4567-e89b-12d3-a456-426614174000",
            "00000000-0000-0000-0000-000000000000",
        ]

        for uuid in valid_uuids:
            assert is_valid_uuid(uuid), f"Expected {uuid} to be valid"

    def test_invalid_uuid(self):
        """Test invalid UUIDs"""
        invalid_uuids = [
            "not-a-uuid",
            "550e8400-e29b-41d4-a716",  # Too short
            "550e8400-e29b-41d4-a716-44665544000g",  # Invalid character
            "",
            "550e8400e29b41d4a716446655440000",  # Missing dashes
        ]

        for uuid in invalid_uuids:
            assert not is_valid_uuid(uuid), f"Expected {uuid} to be invalid"


# ═══════════════════════════════════════════════════════════════════════════
# Number Validation Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestNumberValidation:
    """Test number validation"""

    def test_positive_numbers(self):
        """Test positive number validation"""
        assert is_positive_number(1)
        assert is_positive_number(0.1)
        assert is_positive_number(1000.5)

    def test_non_positive_numbers(self):
        """Test non-positive numbers"""
        assert not is_positive_number(0)
        assert not is_positive_number(-1)
        assert not is_positive_number(-0.1)

    def test_invalid_types(self):
        """Test invalid types"""
        assert not is_positive_number("1")
        assert not is_positive_number(None)
        assert not is_positive_number([1])


# ═══════════════════════════════════════════════════════════════════════════
# Date Range Validation Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestDateRangeValidation:
    """Test date range validation"""

    def test_valid_date_range(self):
        """Test valid date range"""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 12, 31)
        assert is_valid_date_range(start, end)

    def test_invalid_date_range(self):
        """Test invalid date range (end before start)"""
        start = datetime(2024, 12, 31)
        end = datetime(2024, 1, 1)
        assert not is_valid_date_range(start, end)

    def test_equal_dates(self):
        """Test equal start and end dates"""
        date = datetime(2024, 1, 1)
        assert not is_valid_date_range(date, date)


# ═══════════════════════════════════════════════════════════════════════════
# String Sanitization Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestStringSanitization:
    """Test string sanitization"""

    def test_remove_extra_whitespace(self):
        """Test removing extra whitespace"""
        assert sanitize_string("  hello   world  ") == "hello world"
        assert sanitize_string("hello\n\nworld") == "hello world"
        assert sanitize_string("hello\t\tworld") == "hello world"

    def test_truncate_long_strings(self):
        """Test truncating long strings"""
        long_string = "a" * 300
        result = sanitize_string(long_string, max_length=255)
        assert len(result) == 255

    def test_empty_strings(self):
        """Test empty strings"""
        assert sanitize_string("") == ""
        assert sanitize_string("   ") == ""
        assert sanitize_string(None) == ""


# ═══════════════════════════════════════════════════════════════════════════
# Coordinate Validation Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestCoordinateValidation:
    """Test geographic coordinate validation"""

    def test_valid_coordinates(self):
        """Test valid coordinates"""
        assert validate_coordinates(15.552727, 48.516388)  # Yemen
        assert validate_coordinates(0, 0)  # Null Island
        assert validate_coordinates(-90, -180)  # South Pole
        assert validate_coordinates(90, 180)  # North Pole

    def test_invalid_latitude(self):
        """Test invalid latitude"""
        assert not validate_coordinates(91, 0)
        assert not validate_coordinates(-91, 0)
        assert not validate_coordinates(100, 0)

    def test_invalid_longitude(self):
        """Test invalid longitude"""
        assert not validate_coordinates(0, 181)
        assert not validate_coordinates(0, -181)
        assert not validate_coordinates(0, 200)


# ═══════════════════════════════════════════════════════════════════════════
# Password Validation Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestPasswordValidation:
    """Test password strength validation"""

    def test_strong_password(self):
        """Test strong password"""
        result = validate_password_strength("MyStr0ng!P@ssw0rd")
        assert result["is_valid"]
        assert result["strength"] in ["medium", "strong"]

    def test_weak_password_too_short(self):
        """Test weak password (too short)"""
        result = validate_password_strength("Pass1!")
        assert not result["is_valid"]
        assert "at least 8 characters" in result["errors"][0]

    def test_weak_password_no_uppercase(self):
        """Test weak password (no uppercase)"""
        result = validate_password_strength("password123!")
        assert not result["is_valid"]
        assert any("uppercase" in error.lower() for error in result["errors"])

    def test_weak_password_no_lowercase(self):
        """Test weak password (no lowercase)"""
        result = validate_password_strength("PASSWORD123!")
        assert not result["is_valid"]
        assert any("lowercase" in error.lower() for error in result["errors"])

    def test_weak_password_no_digit(self):
        """Test weak password (no digit)"""
        result = validate_password_strength("Password!")
        assert not result["is_valid"]
        assert any("digit" in error.lower() for error in result["errors"])

    def test_medium_password(self):
        """Test medium strength password"""
        result = validate_password_strength("Password123")
        assert result["is_valid"]
        # Note: may have warning about special character

    def test_very_strong_password(self):
        """Test very strong password"""
        result = validate_password_strength("MyV3ry!Str0ng#P@ssw0rd#2024")
        assert result["is_valid"]
        assert result["strength"] == "strong"


# ═══════════════════════════════════════════════════════════════════════════
# Pydantic Model Validation Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestPydanticValidation:
    """Test Pydantic model validation"""

    def test_user_model_validation(self):
        """Test user model validation"""

        class User(BaseModel):
            email: str
            phone: str
            age: int

            @field_validator("email")
            @classmethod
            def validate_email(cls, v):
                if not is_valid_email(v):
                    raise ValueError("Invalid email format")
                return v

            @field_validator("phone")
            @classmethod
            def validate_phone(cls, v):
                if not is_valid_phone_yemen(v):
                    raise ValueError("Invalid Yemen phone number")
                return v

            @field_validator("age")
            @classmethod
            def validate_age(cls, v):
                if v < 0 or v > 150:
                    raise ValueError("Age must be between 0 and 150")
                return v

        # Valid user
        user = User(email="test@example.com", phone="+967712345678", age=30)
        assert user.email == "test@example.com"

        # Invalid email
        with pytest.raises(ValidationError):
            User(email="invalid", phone="+967712345678", age=30)

        # Invalid phone
        with pytest.raises(ValidationError):
            User(email="test@example.com", phone="123", age=30)

        # Invalid age
        with pytest.raises(ValidationError):
            User(email="test@example.com", phone="+967712345678", age=200)

    def test_field_model_validation(self):
        """Test agricultural field model validation"""

        class Field(BaseModel):
            name: str
            area_hectares: float
            latitude: float
            longitude: float

            @field_validator("name")
            @classmethod
            def validate_name(cls, v):
                v = sanitize_string(v, max_length=100)
                if not v:
                    raise ValueError("Field name cannot be empty")
                return v

            @field_validator("area_hectares")
            @classmethod
            def validate_area(cls, v):
                if not is_positive_number(v):
                    raise ValueError("Area must be positive")
                if v > 10000:
                    raise ValueError("Area seems unreasonably large")
                return v

            @field_validator("latitude", "longitude")
            @classmethod
            def validate_coordinates(cls, v, info):
                # This is a simplified version
                if info.field_name == "latitude" and not (-90 <= v <= 90):
                    raise ValueError("Invalid latitude")
                if info.field_name == "longitude" and not (-180 <= v <= 180):
                    raise ValueError("Invalid longitude")
                return v

        # Valid field
        field = Field(name="Field 1", area_hectares=50.5, latitude=15.5, longitude=48.5)
        assert field.name == "Field 1"

        # Invalid area
        with pytest.raises(ValidationError):
            Field(name="Field 1", area_hectares=-10, latitude=15.5, longitude=48.5)

        # Invalid coordinates
        with pytest.raises(ValidationError):
            Field(name="Field 1", area_hectares=50, latitude=100, longitude=48.5)


# ═══════════════════════════════════════════════════════════════════════════
# Business Rule Validation Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestBusinessRuleValidation:
    """Test business rule validation"""

    def test_crop_planting_date_validation(self):
        """Test crop planting date must be before harvest date"""

        def validate_crop_dates(planting_date: datetime, harvest_date: datetime) -> bool:
            """Planting must be before harvest"""
            if not is_valid_date_range(planting_date, harvest_date):
                return False

            # Check minimum growing period (e.g., 30 days)
            min_days = 30
            delta = harvest_date - planting_date
            if delta.days < min_days:
                return False

            return True

        planting = datetime(2024, 1, 1)
        harvest = datetime(2024, 6, 1)
        assert validate_crop_dates(planting, harvest)

        # Harvest before planting
        assert not validate_crop_dates(harvest, planting)

        # Too short growing period
        harvest_too_soon = datetime(2024, 1, 15)
        assert not validate_crop_dates(planting, harvest_too_soon)

    def test_irrigation_schedule_validation(self):
        """Test irrigation schedule validation"""

        def validate_irrigation_schedule(water_amount_liters: float, frequency_days: int) -> dict:
            """Validate irrigation parameters"""
            errors = []

            if not is_positive_number(water_amount_liters):
                errors.append("Water amount must be positive")

            if water_amount_liters > 10000:
                errors.append("Water amount seems unreasonably high")

            if frequency_days < 1:
                errors.append("Frequency must be at least 1 day")

            if frequency_days > 30:
                errors.append("Frequency should not exceed 30 days")

            return {"is_valid": len(errors) == 0, "errors": errors}

        # Valid schedule
        result = validate_irrigation_schedule(100.0, 3)
        assert result["is_valid"]

        # Invalid water amount
        result = validate_irrigation_schedule(-50.0, 3)
        assert not result["is_valid"]

        # Invalid frequency
        result = validate_irrigation_schedule(100.0, 0)
        assert not result["is_valid"]

    def test_farm_capacity_validation(self):
        """Test farm capacity validation"""

        def validate_farm_capacity(total_area: float, field_areas: list[float]) -> bool:
            """Total field areas should not exceed farm total area"""
            if not is_positive_number(total_area):
                return False

            if not all(is_positive_number(area) for area in field_areas):
                return False

            fields_total = sum(field_areas)
            return fields_total <= total_area

        # Valid capacity
        assert validate_farm_capacity(100.0, [30.0, 25.0, 40.0])

        # Fields exceed farm area
        assert not validate_farm_capacity(100.0, [60.0, 50.0])

        # Negative values
        assert not validate_farm_capacity(-100.0, [30.0])


# ═══════════════════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestValidationIntegration:
    """Test integrated validation scenarios"""

    def test_complete_user_registration_validation(self):
        """Test complete user registration validation"""

        class UserRegistration(BaseModel):
            email: str
            phone: str
            password: str
            full_name: str

            @field_validator("email")
            @classmethod
            def validate_email(cls, v):
                if not is_valid_email(v):
                    raise ValueError("Invalid email")
                return v.lower()

            @field_validator("phone")
            @classmethod
            def validate_phone(cls, v):
                if not is_valid_phone_yemen(v):
                    raise ValueError("Invalid phone number")
                return v

            @field_validator("password")
            @classmethod
            def validate_password(cls, v):
                result = validate_password_strength(v)
                if not result["is_valid"]:
                    raise ValueError("; ".join(result["errors"]))
                return v

            @field_validator("full_name")
            @classmethod
            def validate_name(cls, v):
                v = sanitize_string(v, max_length=100)
                if not v or len(v) < 2:
                    raise ValueError("Name must be at least 2 characters")
                return v

        # Valid registration
        user = UserRegistration(
            email="user@example.com",
            phone="+967712345678",
            password="Str0ng!Pass",
            full_name="John Doe",
        )
        assert user.email == "user@example.com"

        # Invalid email
        with pytest.raises(ValidationError):
            UserRegistration(
                email="invalid",
                phone="+967712345678",
                password="Str0ng!Pass",
                full_name="John Doe",
            )

    def test_farm_field_creation_validation(self):
        """Test farm and field creation with cross-validation"""

        class FieldCreate(BaseModel):
            name: str
            area_hectares: float
            crop_type: str
            latitude: float
            longitude: float

            @field_validator("name")
            @classmethod
            def validate_name(cls, v):
                v = sanitize_string(v)
                if not v:
                    raise ValueError("Field name required")
                return v

            @field_validator("area_hectares")
            @classmethod
            def validate_area(cls, v):
                if not is_positive_number(v):
                    raise ValueError("Area must be positive")
                return v

        # Valid field
        field = FieldCreate(
            name="North Field",
            area_hectares=50.0,
            crop_type="wheat",
            latitude=15.5,
            longitude=48.5,
        )
        assert field.area_hectares == 50.0

        # Invalid field
        with pytest.raises(ValidationError):
            FieldCreate(
                name="", area_hectares=50.0, crop_type="wheat", latitude=15.5, longitude=48.5
            )
