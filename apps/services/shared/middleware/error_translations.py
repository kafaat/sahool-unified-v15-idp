"""
SAHOOL Error Translations
ترجمات الأخطاء لنظام سهول

Centralized error message translations for English and Arabic.
ترجمات مركزية لرسائل الخطأ بالإنجليزية والعربية.
"""

from typing import Dict, Optional

# Error code to translation mapping
# تعيين رموز الأخطاء إلى الترجمات
ERROR_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # ════════════════════════════════════════════════════════════════════════
    # VALIDATION ERRORS - أخطاء التحقق من الصحة
    # ════════════════════════════════════════════════════════════════════════
    "VALIDATION_ERROR": {
        "en": "Validation failed. Please check your input.",
        "ar": "فشل التحقق من الصحة. يرجى التحقق من المدخلات."
    },
    "REQUIRED_FIELD": {
        "en": "Required field is missing.",
        "ar": "حقل مطلوب غير موجود."
    },
    "INVALID_FORMAT": {
        "en": "Invalid format.",
        "ar": "تنسيق غير صالح."
    },
    "INVALID_EMAIL": {
        "en": "Invalid email address.",
        "ar": "عنوان البريد الإلكتروني غير صالح."
    },
    "INVALID_PHONE": {
        "en": "Invalid phone number.",
        "ar": "رقم الهاتف غير صالح."
    },
    "INVALID_UUID": {
        "en": "Invalid UUID format.",
        "ar": "تنسيق UUID غير صالح."
    },
    "INVALID_DATE": {
        "en": "Invalid date format.",
        "ar": "تنسيق التاريخ غير صالح."
    },
    "VALUE_TOO_SMALL": {
        "en": "Value is too small.",
        "ar": "القيمة صغيرة جداً."
    },
    "VALUE_TOO_LARGE": {
        "en": "Value is too large.",
        "ar": "القيمة كبيرة جداً."
    },
    "STRING_TOO_SHORT": {
        "en": "String is too short.",
        "ar": "النص قصير جداً."
    },
    "STRING_TOO_LONG": {
        "en": "String is too long.",
        "ar": "النص طويل جداً."
    },
    "INVALID_ENUM_VALUE": {
        "en": "Invalid value. Must be one of the allowed values.",
        "ar": "قيمة غير صالحة. يجب أن تكون واحدة من القيم المسموح بها."
    },

    # ════════════════════════════════════════════════════════════════════════
    # AUTHENTICATION ERRORS - أخطاء المصادقة
    # ════════════════════════════════════════════════════════════════════════
    "AUTHENTICATION_ERROR": {
        "en": "Authentication required. Please log in.",
        "ar": "المصادقة مطلوبة. يرجى تسجيل الدخول."
    },
    "UNAUTHORIZED": {
        "en": "Authentication required. Please log in.",
        "ar": "المصادقة مطلوبة. يرجى تسجيل الدخول."
    },
    "INVALID_CREDENTIALS": {
        "en": "Invalid username or password.",
        "ar": "اسم المستخدم أو كلمة المرور غير صحيحة."
    },
    "TOKEN_EXPIRED": {
        "en": "Your session has expired. Please log in again.",
        "ar": "انتهت صلاحية الجلسة. يرجى تسجيل الدخول مرة أخرى."
    },
    "TOKEN_INVALID": {
        "en": "Invalid authentication token.",
        "ar": "رمز المصادقة غير صالح."
    },
    "TOKEN_MISSING": {
        "en": "Authentication token is missing.",
        "ar": "رمز المصادقة غير موجود."
    },

    # ════════════════════════════════════════════════════════════════════════
    # AUTHORIZATION ERRORS - أخطاء التفويض
    # ════════════════════════════════════════════════════════════════════════
    "AUTHORIZATION_ERROR": {
        "en": "You don't have permission to perform this action.",
        "ar": "ليس لديك إذن لتنفيذ هذا الإجراء."
    },
    "FORBIDDEN": {
        "en": "Access denied. You don't have permission to access this resource.",
        "ar": "تم رفض الوصول. ليس لديك إذن للوصول إلى هذا المورد."
    },
    "INSUFFICIENT_PERMISSIONS": {
        "en": "Insufficient permissions to perform this action.",
        "ar": "أذونات غير كافية لتنفيذ هذا الإجراء."
    },
    "TENANT_ACCESS_DENIED": {
        "en": "You don't have access to this organization.",
        "ar": "ليس لديك صلاحية الوصول إلى هذه المؤسسة."
    },

    # ════════════════════════════════════════════════════════════════════════
    # RESOURCE ERRORS - أخطاء الموارد
    # ════════════════════════════════════════════════════════════════════════
    "NOT_FOUND": {
        "en": "Resource not found.",
        "ar": "المورد غير موجود."
    },
    "FIELD_NOT_FOUND": {
        "en": "Field not found.",
        "ar": "الحقل غير موجود."
    },
    "USER_NOT_FOUND": {
        "en": "User not found.",
        "ar": "المستخدم غير موجود."
    },
    "TENANT_NOT_FOUND": {
        "en": "Organization not found.",
        "ar": "المؤسسة غير موجودة."
    },
    "CROP_NOT_FOUND": {
        "en": "Crop not found.",
        "ar": "المحصول غير موجود."
    },
    "DEVICE_NOT_FOUND": {
        "en": "Device not found.",
        "ar": "الجهاز غير موجود."
    },

    # ════════════════════════════════════════════════════════════════════════
    # CONFLICT ERRORS - أخطاء التعارض
    # ════════════════════════════════════════════════════════════════════════
    "CONFLICT": {
        "en": "A conflict occurred. The resource may have been modified.",
        "ar": "حدث تعارض. قد يكون المورد قد تم تعديله."
    },
    "DUPLICATE_ENTRY": {
        "en": "This entry already exists.",
        "ar": "هذا الإدخال موجود بالفعل."
    },
    "EMAIL_ALREADY_EXISTS": {
        "en": "An account with this email already exists.",
        "ar": "حساب بهذا البريد الإلكتروني موجود بالفعل."
    },
    "PHONE_ALREADY_EXISTS": {
        "en": "An account with this phone number already exists.",
        "ar": "حساب بهذا رقم الهاتف موجود بالفعل."
    },
    "VERSION_CONFLICT": {
        "en": "The resource has been modified by another user. Please refresh and try again.",
        "ar": "تم تعديل المورد من قبل مستخدم آخر. يرجى التحديث والمحاولة مرة أخرى."
    },
    "OPTIMISTIC_LOCK_ERROR": {
        "en": "The resource was updated by another user. Please refresh and try again.",
        "ar": "تم تحديث المورد من قبل مستخدم آخر. يرجى التحديث والمحاولة مرة أخرى."
    },

    # ════════════════════════════════════════════════════════════════════════
    # RATE LIMIT ERRORS - أخطاء الحد الأقصى للطلبات
    # ════════════════════════════════════════════════════════════════════════
    "RATE_LIMIT_EXCEEDED": {
        "en": "Too many requests. Please try again later.",
        "ar": "طلبات كثيرة جداً. يرجى المحاولة لاحقاً."
    },
    "QUOTA_EXCEEDED": {
        "en": "You have exceeded your quota. Please upgrade your plan.",
        "ar": "لقد تجاوزت حصتك. يرجى ترقية خطتك."
    },

    # ════════════════════════════════════════════════════════════════════════
    # SERVER ERRORS - أخطاء الخادم
    # ════════════════════════════════════════════════════════════════════════
    "INTERNAL_ERROR": {
        "en": "An internal error occurred. Please try again later.",
        "ar": "حدث خطأ داخلي. يرجى المحاولة لاحقاً."
    },
    "DATABASE_ERROR": {
        "en": "A database error occurred. Please try again later.",
        "ar": "حدث خطأ في قاعدة البيانات. يرجى المحاولة لاحقاً."
    },
    "SERVICE_UNAVAILABLE": {
        "en": "Service is temporarily unavailable. Please try again later.",
        "ar": "الخدمة غير متاحة مؤقتاً. يرجى المحاولة لاحقاً."
    },
    "TIMEOUT": {
        "en": "Request timed out. Please try again.",
        "ar": "انتهت مهلة الطلب. يرجى المحاولة مرة أخرى."
    },
    "EXTERNAL_SERVICE_ERROR": {
        "en": "External service error. Please try again later.",
        "ar": "خطأ في الخدمة الخارجية. يرجى المحاولة لاحقاً."
    },

    # ════════════════════════════════════════════════════════════════════════
    # HTTP STATUS ERRORS - أخطاء حالة HTTP
    # ════════════════════════════════════════════════════════════════════════
    "BAD_REQUEST": {
        "en": "Bad request. Please check your input.",
        "ar": "طلب غير صالح. يرجى التحقق من المدخلات."
    },
    "METHOD_NOT_ALLOWED": {
        "en": "Method not allowed.",
        "ar": "الطريقة غير مسموح بها."
    },
    "UNPROCESSABLE_ENTITY": {
        "en": "Unable to process the request.",
        "ar": "تعذر معالجة الطلب."
    },
    "BAD_GATEWAY": {
        "en": "Bad gateway. Please try again later.",
        "ar": "بوابة سيئة. يرجى المحاولة لاحقاً."
    },
    "GATEWAY_TIMEOUT": {
        "en": "Gateway timeout. Please try again later.",
        "ar": "انتهت مهلة البوابة. يرجى المحاولة لاحقاً."
    },

    # ════════════════════════════════════════════════════════════════════════
    # BUSINESS LOGIC ERRORS - أخطاء منطق الأعمال
    # ════════════════════════════════════════════════════════════════════════
    "INVALID_OPERATION": {
        "en": "Invalid operation.",
        "ar": "عملية غير صالحة."
    },
    "OPERATION_NOT_PERMITTED": {
        "en": "This operation is not permitted.",
        "ar": "هذه العملية غير مسموح بها."
    },
    "FIELD_ALREADY_ASSIGNED": {
        "en": "This field is already assigned to another user.",
        "ar": "هذا الحقل مخصص بالفعل لمستخدم آخر."
    },
    "CROP_SEASON_CONFLICT": {
        "en": "Crop season conflicts with existing planting schedule.",
        "ar": "موسم المحصول يتعارض مع جدول الزراعة الحالي."
    },
    "INSUFFICIENT_INVENTORY": {
        "en": "Insufficient inventory to complete this operation.",
        "ar": "مخزون غير كافٍ لإتمام هذه العملية."
    },
    "PAYMENT_REQUIRED": {
        "en": "Payment is required to access this feature.",
        "ar": "الدفع مطلوب للوصول إلى هذه الميزة."
    },
    "SUBSCRIPTION_EXPIRED": {
        "en": "Your subscription has expired. Please renew to continue.",
        "ar": "انتهت صلاحية اشتراكك. يرجى التجديد للمتابعة."
    },

    # ════════════════════════════════════════════════════════════════════════
    # FILE/UPLOAD ERRORS - أخطاء الملفات/التحميل
    # ════════════════════════════════════════════════════════════════════════
    "FILE_TOO_LARGE": {
        "en": "File size exceeds the maximum limit.",
        "ar": "حجم الملف يتجاوز الحد الأقصى."
    },
    "INVALID_FILE_TYPE": {
        "en": "Invalid file type. Please upload a supported file format.",
        "ar": "نوع ملف غير صالح. يرجى تحميل تنسيق ملف مدعوم."
    },
    "FILE_UPLOAD_FAILED": {
        "en": "File upload failed. Please try again.",
        "ar": "فشل تحميل الملف. يرجى المحاولة مرة أخرى."
    },

    # ════════════════════════════════════════════════════════════════════════
    # GEOSPATIAL ERRORS - أخطاء الموقع الجغرافي
    # ════════════════════════════════════════════════════════════════════════
    "INVALID_COORDINATES": {
        "en": "Invalid coordinates provided.",
        "ar": "إحداثيات غير صالحة."
    },
    "INVALID_POLYGON": {
        "en": "Invalid polygon geometry.",
        "ar": "شكل مضلع غير صالح."
    },
    "AREA_TOO_LARGE": {
        "en": "Field area exceeds the maximum allowed size.",
        "ar": "مساحة الحقل تتجاوز الحجم الأقصى المسموح به."
    },
    "AREA_TOO_SMALL": {
        "en": "Field area is below the minimum required size.",
        "ar": "مساحة الحقل أقل من الحد الأدنى المطلوب."
    },
    "BOUNDARY_REQUIRED": {
        "en": "Field boundary is required.",
        "ar": "حدود الحقل مطلوبة."
    },
}


def get_translation(error_code: str, language: str = "en", default: Optional[str] = None) -> str:
    """
    Get translated error message for the given error code and language.
    احصل على رسالة الخطأ المترجمة لرمز الخطأ واللغة المحددة.

    Args:
        error_code: The error code (e.g., "NOT_FOUND", "VALIDATION_ERROR")
        language: Language code ("en" or "ar")
        default: Default message if translation not found

    Returns:
        Translated error message
    """
    # Normalize language code
    lang = language.lower()[:2]
    if lang not in ("en", "ar"):
        lang = "en"

    # Get translation
    if error_code in ERROR_TRANSLATIONS:
        return ERROR_TRANSLATIONS[error_code].get(lang, ERROR_TRANSLATIONS[error_code].get("en", default or error_code))

    # Fallback to default or error code
    return default or error_code


def get_bilingual_translation(error_code: str, default_en: Optional[str] = None, default_ar: Optional[str] = None) -> Dict[str, str]:
    """
    Get both English and Arabic translations for an error code.
    احصل على الترجمة باللغتين الإنجليزية والعربية لرمز خطأ.

    Args:
        error_code: The error code
        default_en: Default English message if not found
        default_ar: Default Arabic message if not found

    Returns:
        Dict with "en" and "ar" keys containing translations
    """
    if error_code in ERROR_TRANSLATIONS:
        return ERROR_TRANSLATIONS[error_code].copy()

    return {
        "en": default_en or error_code,
        "ar": default_ar or error_code
    }


def parse_accept_language(accept_language_header: Optional[str]) -> str:
    """
    Parse Accept-Language header and return preferred language.
    تحليل رأس Accept-Language وإرجاع اللغة المفضلة.

    Supports formats like:
    - "en-US,en;q=0.9,ar;q=0.8"
    - "ar"
    - "en"

    Args:
        accept_language_header: The Accept-Language header value

    Returns:
        Language code ("en" or "ar")
    """
    if not accept_language_header:
        return "en"

    # Parse header and extract languages with their quality values
    languages = []
    for lang_item in accept_language_header.split(","):
        parts = lang_item.strip().split(";")
        lang = parts[0].strip().lower()

        # Extract quality value (default to 1.0 if not specified)
        quality = 1.0
        if len(parts) > 1:
            for part in parts[1:]:
                if part.strip().startswith("q="):
                    try:
                        quality = float(part.strip()[2:])
                    except ValueError:
                        quality = 1.0
                    break

        # Extract base language code (e.g., "en" from "en-US")
        base_lang = lang.split("-")[0]
        languages.append((base_lang, quality))

    # Sort by quality (descending)
    languages.sort(key=lambda x: x[1], reverse=True)

    # Return first supported language
    for lang, _ in languages:
        if lang in ("ar", "en"):
            return lang

    # Default to English
    return "en"


# Export all
__all__ = [
    "ERROR_TRANSLATIONS",
    "get_translation",
    "get_bilingual_translation",
    "parse_accept_language",
]
