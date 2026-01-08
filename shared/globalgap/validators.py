"""
GlobalGAP IFA v6 Validators
أدوات التحقق من GlobalGAP IFA v6

Validation functions for IFA v6 compliance data.
وظائف التحقق من بيانات الامتثال لـ IFA v6.
"""

import re
from datetime import date, datetime, timedelta

from .constants import (
    CERTIFICATE_VALIDITY_DAYS,
    COMPLIANCE_THRESHOLDS,
    GGN_FORMAT_PATTERN,
    GGN_LENGTH,
    GGN_PREFIX,
    ComplianceLevel,
)


def validate_ggn_number(ggn: str) -> tuple[bool, str | None]:
    """
    Validate GlobalGAP Number (GGN) format
    التحقق من صحة تنسيق رقم GlobalGAP (GGN)

    GGN must be 13 digits starting with 40.
    يجب أن يكون GGN مكوناً من 13 رقماً يبدأ بـ 40.

    Args:
        ggn: GlobalGAP Number to validate

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_ggn_number("4000000000001")
        (True, None)
        >>> validate_ggn_number("1234567890123")
        (False, "GGN must start with 40")
    """
    # Remove any spaces or dashes
    ggn_clean = ggn.replace(" ", "").replace("-", "")

    # Check length
    if len(ggn_clean) != GGN_LENGTH:
        return False, f"GGN must be exactly {GGN_LENGTH} digits"

    # Check if numeric
    if not ggn_clean.isdigit():
        return False, "GGN must contain only digits"

    # Check prefix
    if not ggn_clean.startswith(GGN_PREFIX):
        return False, f"GGN must start with {GGN_PREFIX}"

    # Validate with regex pattern
    if not re.match(GGN_FORMAT_PATTERN, ggn_clean):
        return False, "GGN format is invalid"

    return True, None


def validate_compliance_percentage(
    compliant_count: int, total_count: int, not_applicable_count: int = 0
) -> tuple[float, bool]:
    """
    Calculate and validate compliance percentage
    حساب والتحقق من نسبة الامتثال

    Args:
        compliant_count: Number of compliant items
        total_count: Total number of items
        not_applicable_count: Number of N/A items

    Returns:
        Tuple of (percentage, is_valid)

    Examples:
        >>> validate_compliance_percentage(95, 100, 0)
        (95.0, True)
        >>> validate_compliance_percentage(20, 20, 0)
        (100.0, True)
    """
    # Calculate applicable items
    applicable_count = total_count - not_applicable_count

    if applicable_count <= 0:
        return 100.0, True  # All N/A means 100% compliance

    if compliant_count < 0 or compliant_count > applicable_count:
        return 0.0, False

    percentage = (compliant_count / applicable_count) * 100.0
    return round(percentage, 2), True


def check_major_must_compliance(
    findings: list[dict], checklist_items: list[dict]
) -> tuple[bool, dict]:
    """
    Check if Major Must requirements are met
    التحقق من استيفاء المتطلبات الإلزامية الرئيسية

    All Major Must items must be 100% compliant.
    يجب أن تكون جميع العناصر الإلزامية الرئيسية متوافقة بنسبة 100%.

    Args:
        findings: List of audit findings
        checklist_items: List of checklist items

    Returns:
        Tuple of (is_compliant, details_dict)
    """
    # Filter Major Must items
    major_must_items = [
        item
        for item in checklist_items
        if item.get("compliance_level") == ComplianceLevel.MAJOR_MUST
    ]

    if not major_must_items:
        return True, {
            "total_major_must": 0,
            "compliant": 0,
            "non_compliant": 0,
            "percentage": 100.0,
            "meets_threshold": True,
        }

    # Create findings lookup
    findings_dict = {f["checklist_item_id"]: f for f in findings}

    total = 0
    compliant = 0
    non_compliant = 0
    not_applicable = 0
    failed_items = []

    for item in major_must_items:
        item_id = item.get("id")
        finding = findings_dict.get(item_id)

        if not finding:
            # No finding means not assessed - counts as non-compliant
            non_compliant += 1
            total += 1
            failed_items.append(
                {
                    "id": item_id,
                    "title_en": item.get("title_en"),
                    "reason": "Not assessed",
                }
            )
            continue

        if finding.get("is_not_applicable", False):
            not_applicable += 1
            continue

        total += 1
        if finding.get("is_compliant", False):
            compliant += 1
        else:
            non_compliant += 1
            failed_items.append(
                {
                    "id": item_id,
                    "title_en": item.get("title_en"),
                    "reason": finding.get("notes_en", "Non-compliant"),
                }
            )

    # Calculate percentage
    percentage, _ = validate_compliance_percentage(compliant, total, 0)

    # Major Must requires 100%
    meets_threshold = percentage >= COMPLIANCE_THRESHOLDS["major_must"]

    return meets_threshold, {
        "total_major_must": total,
        "compliant": compliant,
        "non_compliant": non_compliant,
        "not_applicable": not_applicable,
        "percentage": percentage,
        "meets_threshold": meets_threshold,
        "threshold_required": COMPLIANCE_THRESHOLDS["major_must"],
        "failed_items": failed_items,
    }


def check_minor_must_compliance(
    findings: list[dict], checklist_items: list[dict]
) -> tuple[bool, dict]:
    """
    Check if Minor Must requirements are met
    التحقق من استيفاء المتطلبات الإلزامية الثانوية

    Minor Must items must be at least 95% compliant.
    يجب أن تكون العناصر الإلزامية الثانوية متوافقة بنسبة 95% على الأقل.

    Args:
        findings: List of audit findings
        checklist_items: List of checklist items

    Returns:
        Tuple of (is_compliant, details_dict)
    """
    # Filter Minor Must items
    minor_must_items = [
        item
        for item in checklist_items
        if item.get("compliance_level") == ComplianceLevel.MINOR_MUST
    ]

    if not minor_must_items:
        return True, {
            "total_minor_must": 0,
            "compliant": 0,
            "non_compliant": 0,
            "percentage": 100.0,
            "meets_threshold": True,
        }

    # Create findings lookup
    findings_dict = {f["checklist_item_id"]: f for f in findings}

    total = 0
    compliant = 0
    non_compliant = 0
    not_applicable = 0
    failed_items = []

    for item in minor_must_items:
        item_id = item.get("id")
        finding = findings_dict.get(item_id)

        if not finding:
            non_compliant += 1
            total += 1
            failed_items.append(
                {
                    "id": item_id,
                    "title_en": item.get("title_en"),
                    "reason": "Not assessed",
                }
            )
            continue

        if finding.get("is_not_applicable", False):
            not_applicable += 1
            continue

        total += 1
        if finding.get("is_compliant", False):
            compliant += 1
        else:
            non_compliant += 1
            failed_items.append(
                {
                    "id": item_id,
                    "title_en": item.get("title_en"),
                    "reason": finding.get("notes_en", "Non-compliant"),
                }
            )

    # Calculate percentage
    percentage, _ = validate_compliance_percentage(compliant, total, 0)

    # Minor Must requires 95%
    meets_threshold = percentage >= COMPLIANCE_THRESHOLDS["minor_must"]

    return meets_threshold, {
        "total_minor_must": total,
        "compliant": compliant,
        "non_compliant": non_compliant,
        "not_applicable": not_applicable,
        "percentage": percentage,
        "meets_threshold": meets_threshold,
        "threshold_required": COMPLIANCE_THRESHOLDS["minor_must"],
        "failed_items": failed_items,
    }


def validate_certificate_validity(
    issue_date: date,
    expiry_date: date | None = None,
    check_date: date | None = None,
) -> tuple[bool, dict]:
    """
    Validate certificate validity period
    التحقق من صحة فترة صلاحية الشهادة

    Certificates are valid for exactly 12 months.
    الشهادات صالحة لمدة 12 شهراً بالضبط.

    Args:
        issue_date: Certificate issue date
        expiry_date: Certificate expiry date (optional, will be calculated)
        check_date: Date to check validity (defaults to today)

    Returns:
        Tuple of (is_valid, details_dict)
    """
    if check_date is None:
        check_date = date.today()

    # Calculate expected expiry date
    expected_expiry = issue_date + timedelta(days=CERTIFICATE_VALIDITY_DAYS)

    # If expiry_date provided, validate it matches expected
    if expiry_date:
        if expiry_date != expected_expiry:
            return False, {
                "is_valid": False,
                "issue_date": issue_date.isoformat(),
                "expiry_date": expiry_date.isoformat(),
                "expected_expiry": expected_expiry.isoformat(),
                "error": "Expiry date doesn't match expected 12-month validity",
            }
    else:
        expiry_date = expected_expiry

    # Check if currently valid
    is_currently_valid = issue_date <= check_date < expiry_date

    # Calculate days remaining
    days_remaining = (expiry_date - check_date).days

    # Check if renewal warning needed
    needs_renewal_warning = 0 < days_remaining <= 90

    return True, {
        "is_valid": True,
        "is_currently_valid": is_currently_valid,
        "issue_date": issue_date.isoformat(),
        "expiry_date": expiry_date.isoformat(),
        "check_date": check_date.isoformat(),
        "days_remaining": days_remaining,
        "needs_renewal_warning": needs_renewal_warning,
        "status": (
            "valid"
            if is_currently_valid
            else ("expired" if days_remaining < 0 else "not_yet_valid")
        ),
    }


def validate_farm_registration(farm_data: dict) -> tuple[bool, list[str]]:
    """
    Validate farm registration data completeness
    التحقق من اكتمال بيانات تسجيل المزرعة

    Args:
        farm_data: Farm registration dictionary

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Required fields
    required_fields = [
        ("ggn", "GlobalGAP Number"),
        ("producer_id", "Producer ID"),
        ("farm_name_en", "Farm name (English)"),
        ("farm_name_ar", "Farm name (Arabic)"),
        ("farm_size_hectares", "Farm size"),
        ("certified_area_hectares", "Certified area"),
        ("country_code", "Country code"),
        ("region", "Region"),
    ]

    for field_name, field_label in required_fields:
        if not farm_data.get(field_name):
            errors.append(f"{field_label} is required")

    # Validate GGN format
    ggn = farm_data.get("ggn", "")
    if ggn:
        is_valid_ggn, ggn_error = validate_ggn_number(ggn)
        if not is_valid_ggn:
            errors.append(f"Invalid GGN: {ggn_error}")

    # Validate farm size
    farm_size = farm_data.get("farm_size_hectares", 0)
    certified_area = farm_data.get("certified_area_hectares", 0)

    if farm_size <= 0:
        errors.append("Farm size must be greater than 0")

    if certified_area <= 0:
        errors.append("Certified area must be greater than 0")

    if certified_area > farm_size:
        errors.append("Certified area cannot exceed total farm size")

    # Validate certification scope
    cert_scope = farm_data.get("certification_scope", [])
    if not cert_scope:
        errors.append("At least one certification scope is required")

    # Validate product types
    products_en = farm_data.get("product_types_en", [])
    if not products_en:
        errors.append("At least one product type is required")

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_audit_completion(
    audit_data: dict, findings: list[dict], checklist_items: list[dict]
) -> tuple[bool, dict]:
    """
    Validate if audit is complete and ready for certification decision
    التحقق من اكتمال التدقيق والجاهزية لقرار الشهادة

    Args:
        audit_data: Audit session data
        findings: List of audit findings
        checklist_items: Complete checklist items

    Returns:
        Tuple of (is_ready, validation_results)
    """
    errors = []
    warnings = []

    # Check if all items are assessed
    findings_dict = {f["checklist_item_id"]: f for f in findings}
    missing_items = []

    for item in checklist_items:
        if item["id"] not in findings_dict:
            missing_items.append(
                {
                    "id": item["id"],
                    "title_en": item["title_en"],
                    "compliance_level": item["compliance_level"],
                }
            )

    if missing_items:
        errors.append(f"{len(missing_items)} items not assessed")

    # Check Major Must compliance
    major_compliant, major_details = check_major_must_compliance(findings, checklist_items)
    if not major_compliant:
        errors.append(
            f"Major Must compliance not met: {major_details['percentage']}% "
            f"(requires {major_details['threshold_required']}%)"
        )

    # Check Minor Must compliance
    minor_compliant, minor_details = check_minor_must_compliance(findings, checklist_items)
    if not minor_compliant:
        warnings.append(
            f"Minor Must compliance not met: {minor_details['percentage']}% "
            f"(requires {minor_details['threshold_required']}%)"
        )

    # Check for critical non-conformances
    critical_ncs = [
        nc for nc in audit_data.get("non_conformances", []) if nc.get("severity") == "CRITICAL"
    ]
    if critical_ncs:
        errors.append(f"{len(critical_ncs)} critical non-conformances found")

    # Check for open non-conformances
    open_ncs = [nc for nc in audit_data.get("non_conformances", []) if nc.get("status") == "OPEN"]
    if open_ncs:
        warnings.append(f"{len(open_ncs)} open non-conformances require corrective actions")

    # Determine certification recommendation
    can_certify = len(errors) == 0
    certification_recommendation = "APPROVE" if can_certify else "REJECT"

    if can_certify and len(warnings) > 0:
        certification_recommendation = "CONDITIONAL"

    is_ready = len(errors) == 0

    return is_ready, {
        "is_ready": is_ready,
        "can_certify": can_certify,
        "certification_recommendation": certification_recommendation,
        "errors": errors,
        "warnings": warnings,
        "missing_items": missing_items,
        "major_must_compliance": major_details,
        "minor_must_compliance": minor_details,
        "critical_non_conformances": len(critical_ncs),
        "open_non_conformances": len(open_ncs),
    }


def validate_corrective_action(
    corrective_action: dict, non_conformance: dict
) -> tuple[bool, list[str]]:
    """
    Validate corrective action plan
    التحقق من صحة خطة الإجراء التصحيحي

    Args:
        corrective_action: Corrective action data
        non_conformance: Associated non-conformance

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Required fields
    if not corrective_action.get("action_description_en"):
        errors.append("Action description (English) is required")

    if not corrective_action.get("action_description_ar"):
        errors.append("Action description (Arabic) is required")

    if not corrective_action.get("responsible_person"):
        errors.append("Responsible person is required")

    if not corrective_action.get("planned_date"):
        errors.append("Planned completion date is required")

    # Validate planned date against NC due date
    planned_date = corrective_action.get("planned_date")
    nc_due_date = non_conformance.get("due_date")

    if planned_date and nc_due_date:
        if isinstance(planned_date, str):
            planned_date = datetime.fromisoformat(planned_date).date()
        if isinstance(nc_due_date, str):
            nc_due_date = datetime.fromisoformat(nc_due_date).date()

        if planned_date > nc_due_date:
            errors.append(f"Planned date ({planned_date}) exceeds NC due date ({nc_due_date})")

    # If completed, check for evidence
    status = corrective_action.get("status")
    if status in ["COMPLETED", "VERIFIED"]:
        evidence_docs = corrective_action.get("evidence_documents", [])
        evidence_photos = corrective_action.get("evidence_photos", [])

        if not evidence_docs and not evidence_photos:
            errors.append("Evidence required for completed actions")

        if not corrective_action.get("actual_date"):
            errors.append("Actual completion date required for completed actions")

    # If verified, check for verification details
    if status == "VERIFIED":
        if not corrective_action.get("effectiveness_verified"):
            errors.append("Effectiveness verification flag not set")

        if not corrective_action.get("verification_date"):
            errors.append("Verification date required")

    is_valid = len(errors) == 0
    return is_valid, errors
