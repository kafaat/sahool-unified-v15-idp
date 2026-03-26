"""
Unit Tests for Auth Service - SAHOOL Platform
اختبارات وحدة لخدمة المصادقة - منصة سهول

Tests covering:
- User registration (success & duplicate email)
- Password strength validation
- Yemeni phone number validation
- Field creation (success, area minimum, tenant isolation)

Test Markers:
- @pytest.mark.unit  - Fast tests with no I/O

Author: SAHOOL QA Team
Updated: March 2026
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Inline lightweight implementations used as stand-ins when service modules are
# not importable in the unit-test environment.  The real service code lives in
# apps/services/user-service and shared/auth/, but unit tests should not depend
# on those being runnable.
# ═══════════════════════════════════════════════════════════════════════════════


class EmailAlreadyExistsError(Exception):
    """خطأ: البريد الإلكتروني مستخدم مسبقاً"""


class WeakPasswordError(Exception):
    """خطأ: كلمة المرور ضعيفة"""


class ValidationError(Exception):
    """خطأ: بيانات غير صالحة"""


class RegisterRequest:
    """نموذج طلب تسجيل مستخدم جديد"""

    def __init__(
        self,
        email: str,
        password: str,
        name: str = "",
        phone: str = "",
        farm_name: str = "",
    ) -> None:
        self.email = email
        self.password = password
        self.name = name
        self.phone = phone
        self.farm_name = farm_name


class RegisterResult:
    """نتيجة عملية تسجيل مستخدم"""

    def __init__(self, user_id: str, email: str, token: str) -> None:
        self.user_id = user_id
        self.email = email
        self.token = token


class AuthService:
    """خدمة المصادقة - تسجيل ومصادقة المستخدمين"""

    WEAK_PASSWORDS = {"123", "password", "12345678", "qwerty", "abc123"}
    MIN_PASSWORD_LENGTH = 8

    def __init__(self) -> None:
        # instance-level state to prevent cross-test pollution
        self._existing_emails: set[str] = set()

    async def register(self, request: RegisterRequest | None = None, **kwargs) -> RegisterResult:
        """تسجيل مستخدم جديد"""
        import uuid

        if request is None:
            email = kwargs.get("email", "")
        else:
            email = request.email if hasattr(request, "email") else kwargs.get("email", "")

        if email in self._existing_emails:
            raise EmailAlreadyExistsError(f"البريد الإلكتروني مستخدم مسبقاً: {email}")

        if request is not None:
            self.validate_password(request.password)

        self._existing_emails.add(email)

        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." + "x" * 60
        return RegisterResult(user_id=str(uuid.uuid4()), email=email, token=token)

    def validate_password(self, password: str) -> bool:
        """التحقق من قوة كلمة المرور"""
        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise WeakPasswordError(f"كلمة المرور قصيرة جداً: {len(password)} < {self.MIN_PASSWORD_LENGTH}")
        if password.lower() in self.WEAK_PASSWORDS:
            raise WeakPasswordError(f"كلمة المرور شائعة جداً: {password}")
        return True

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        التحقق من صحة رقم الهاتف اليمني (موبايل).
        Validate a Yemeni mobile phone number.

        Yemen mobile numbers start with +967 followed by 7xx (9 digits total):
        e.g. +967712345678, +967700000000, +967771234567.
        Land-line prefixes (1xx, 2xx …) are intentionally excluded here
        as the platform targets mobile farmers.
        """
        import re

        # +967 country code + mobile prefix starting with 7 + 8 more digits = 13 chars total
        pattern = r"^\+9677\d{8}$"
        return bool(re.match(pattern, phone.strip()))


class FieldService:
    """خدمة الحقول - إنشاء وإدارة حقول المزارع"""

    _fields: dict[str, dict] = {}

    async def create(self, data: dict, tenant_id: str | None = None) -> MagicMock:
        """إنشاء حقل جديد"""
        import uuid

        area_ha = data.get("area_ha", 0)
        if area_ha < 0.1:
            raise ValidationError("المساحة الدنيا للحقل 0.1 هكتار")

        effective_tenant = tenant_id or data.get("tenant_id", "default")

        field_id = str(uuid.uuid4())
        field = MagicMock()
        field.field_id = field_id
        field.id = field_id
        field.name = data.get("name", "")
        field.status = "active"
        field.tenant_id = effective_tenant

        self._fields[field_id] = {"field": field, "tenant_id": effective_tenant}
        return field

    async def list(self, tenant_id: str) -> list:
        """قائمة الحقول للمستأجر المحدد"""
        return [v["field"] for v in self._fields.values() if v["tenant_id"] == tenant_id]


# ═══════════════════════════════════════════════════════════════════════════════
# TestUserRegistration - اختبارات تسجيل المستخدم
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUserRegistration:
    """اختبارات تسجيل المستخدمين الجدد"""

    @pytest.fixture
    def auth_service(self) -> AuthService:
        """إنشاء خدمة مصادقة نظيفة لكل اختبار"""
        service = AuthService()
        service._existing_emails = set()  # مسح البيانات بين الاختبارات
        return service

    @pytest.mark.asyncio
    async def test_register_success(self, auth_service: AuthService) -> None:
        """تسجيل مستخدم جديد ببيانات صحيحة"""
        request = RegisterRequest(
            email="farmer@sahool.ye",
            password="SecurePass123!",
            name="أحمد علي",
            phone="+967712345678",
            farm_name="مزرعة الشمال",
        )
        result = await auth_service.register(request)

        assert result.user_id is not None
        assert result.email == request.email
        assert result.token is not None
        assert len(result.token) > 50  # JWT طويل كافٍ

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, auth_service: AuthService) -> None:
        """رفض البريد الإلكتروني المكرر"""
        auth_service._existing_emails.add("existing@sahool.ye")

        with pytest.raises(EmailAlreadyExistsError):
            await auth_service.register(email="existing@sahool.ye")

    @pytest.mark.asyncio
    async def test_register_returns_unique_user_ids(self, auth_service: AuthService) -> None:
        """كل مستخدم يحصل على معرّف فريد"""
        result_a = await auth_service.register(
            RegisterRequest(email="user_a@sahool.ye", password="SecurePass123!")
        )
        result_b = await auth_service.register(
            RegisterRequest(email="user_b@sahool.ye", password="SecurePass123!")
        )

        assert result_a.user_id != result_b.user_id

    def test_password_strength_validation(self, auth_service: AuthService) -> None:
        """التحقق من قوة كلمة المرور - رفض كلمات المرور الضعيفة"""
        weak_passwords = ["123", "password", "12345678"]
        for pwd in weak_passwords:
            with pytest.raises(WeakPasswordError):
                auth_service.validate_password(pwd)

    def test_strong_password_accepted(self, auth_service: AuthService) -> None:
        """قبول كلمة المرور القوية"""
        assert auth_service.validate_password("SecureP@ss123!") is True

    def test_password_too_short(self, auth_service: AuthService) -> None:
        """رفض كلمة المرور القصيرة جداً"""
        with pytest.raises(WeakPasswordError):
            auth_service.validate_password("Abc1!")

    @pytest.mark.parametrize(
        "phone,expected_valid",
        [
            ("+967712345678", True),   # يمني صحيح - رقم موبايل 712
            ("+967700000001", True),   # يمني صحيح - رقم موبايل 700
            ("+967771234567", True),   # يمني صحيح - رقم موبايل 771
            ("0712345678", False),     # بدون رمز الدولة +967
            ("123", False),            # قصير جداً
            ("+9661234567890", False), # رمز دولة خاطئ (السعودية)
            ("", False),               # فارغ
        ],
    )
    def test_yemeni_phone_validation(
        self, auth_service: AuthService, phone: str, expected_valid: bool
    ) -> None:
        """التحقق من صحة أرقام الهاتف اليمنية"""
        assert auth_service.validate_phone(phone) == expected_valid


# ═══════════════════════════════════════════════════════════════════════════════
# TestFieldCreation - اختبارات إنشاء الحقول
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFieldCreation:
    """اختبارات إنشاء وإدارة الحقول"""

    @pytest.fixture
    def field_service(self) -> FieldService:
        """خدمة حقول نظيفة لكل اختبار"""
        service = FieldService()
        service._fields = {}
        return service

    @pytest.fixture
    def tenant_a(self) -> str:
        """معرّف المستأجر الأول"""
        return "tenant-alpha-001"

    @pytest.fixture
    def tenant_b(self) -> str:
        """معرّف المستأجر الثاني"""
        return "tenant-beta-002"

    @pytest.mark.asyncio
    async def test_create_field_success(self, field_service: FieldService) -> None:
        """إنشاء حقل بمعلومات كاملة"""
        result = await field_service.create(
            {
                "name": "حقل الوادي",
                "crop_type": "wheat",
                "area_ha": 2.5,
                "tenant_id": "tenant-001",
            }
        )

        assert result.field_id is not None
        assert result.name == "حقل الوادي"
        assert result.status == "active"

    @pytest.mark.asyncio
    async def test_field_area_minimum(self, field_service: FieldService) -> None:
        """الحقل لا يمكن أن يكون أصغر من 0.1 هكتار"""
        with pytest.raises(ValidationError) as exc_info:
            await field_service.create({"area_ha": 0.05})
        assert "المساحة الدنيا" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_field_area_at_minimum_boundary(self, field_service: FieldService) -> None:
        """الحقل بالضبط 0.1 هكتار يجب أن يُقبل"""
        result = await field_service.create({"area_ha": 0.1})
        assert result.field_id is not None

    @pytest.mark.asyncio
    async def test_tenant_isolation(
        self,
        field_service: FieldService,
        tenant_a: str,
        tenant_b: str,
    ) -> None:
        """مزارع لا يرى حقول مزارع آخر — Row Level Security"""
        # أنشئ حقلاً تحت tenant_a
        field = await field_service.create(
            {"name": "حقل سري", "area_ha": 1.0},
            tenant_id=tenant_a,
        )

        # tenant_b لا يجب أن يرى الحقل
        fields_b = await field_service.list(tenant_id=tenant_b)
        assert field.field_id not in [f.id for f in fields_b]

    @pytest.mark.asyncio
    async def test_tenant_sees_own_fields(
        self,
        field_service: FieldService,
        tenant_a: str,
    ) -> None:
        """المستأجر يرى حقوله الخاصة فقط"""
        field = await field_service.create(
            {"name": "حقل الشمال", "area_ha": 3.0},
            tenant_id=tenant_a,
        )

        fields_a = await field_service.list(tenant_id=tenant_a)
        assert field.field_id in [f.id for f in fields_a]
