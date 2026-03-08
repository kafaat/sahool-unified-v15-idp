"""
Farm Document Compliance Module
وحدة امتثال وثائق المزرعة

Provides compliance document tracking, requirement management,
and certification verification functionality.

توفر تتبع وثائق الامتثال، وإدارة المتطلبات،
ووظائف التحقق من الشهادات.
"""

from __future__ import annotations

from datetime import UTC, date, datetime

import structlog

from .models import (
    Certification,
    CertificationBody,
    CertificationStatus,
    CertificationSummary,
    CertificationType,
    ComplianceDocument,
    ComplianceRequirement,
    ComplianceStatus,
    ComplianceSummary,
    DocumentType,
)

logger = structlog.get_logger()


# ─────────────────────────────────────────────────────────────────────────────
# Compliance Service - خدمة الامتثال
# ─────────────────────────────────────────────────────────────────────────────


class ComplianceError(Exception):
    """
    Compliance operation error
    خطأ عملية الامتثال
    """

    def __init__(self, message: str, error_code: str = "COMPLIANCE_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ComplianceService:
    """
    Compliance document tracking service
    خدمة تتبع وثائق الامتثال

    Manages compliance requirements, certifications, and document verification.
    تدير متطلبات الامتثال، والشهادات، والتحقق من الوثائق.
    """

    def __init__(self):
        # In-memory storage for demo/testing
        self._certifications: dict[str, Certification] = {}
        self._certification_bodies: dict[str, CertificationBody] = {}
        self._requirements: dict[str, ComplianceRequirement] = {}
        self._compliance_docs: dict[str, ComplianceDocument] = {}

        # Initialize default requirements
        self._init_default_requirements()
        self._init_default_certification_bodies()

    def _init_default_requirements(self) -> None:
        """Initialize default compliance requirements"""
        default_requirements = [
            # GlobalGAP Requirements
            ComplianceRequirement(
                id="req_ggap_soil",
                code="GGAP-SOIL-001",
                category="SOIL_MANAGEMENT",
                title_en="Soil Analysis Report",
                title_ar="تقرير تحليل التربة",
                description_en="Annual soil analysis report from accredited laboratory",
                description_ar="تقرير تحليل التربة السنوي من مختبر معتمد",
                certification_type=CertificationType.GLOBALGAP,
                required_documents=[DocumentType.SOIL_TEST],
                document_renewal_days=365,
                is_mandatory=True,
                compliance_level="MAJOR_MUST",
                guidance_en="Submit soil analysis within 14 months of certification audit",
                guidance_ar="تقديم تحليل التربة خلال 14 شهراً من تدقيق الشهادة",
            ),
            ComplianceRequirement(
                id="req_ggap_water",
                code="GGAP-WATER-001",
                category="WATER_MANAGEMENT",
                title_en="Water Analysis Report",
                title_ar="تقرير تحليل المياه",
                description_en="Annual water quality analysis for irrigation",
                description_ar="تحليل جودة مياه الري السنوي",
                certification_type=CertificationType.GLOBALGAP,
                required_documents=[DocumentType.WATER_TEST],
                document_renewal_days=365,
                is_mandatory=True,
                compliance_level="MAJOR_MUST",
                guidance_en="Water analysis must include microbial and chemical parameters",
                guidance_ar="يجب أن يشمل تحليل المياه المعايير الميكروبية والكيميائية",
            ),
            ComplianceRequirement(
                id="req_ggap_pest",
                code="GGAP-IPM-001",
                category="PEST_MANAGEMENT",
                title_en="Pesticide Application Records",
                title_ar="سجلات تطبيق المبيدات",
                description_en="Complete records of all pesticide applications",
                description_ar="سجلات كاملة لجميع تطبيقات المبيدات",
                certification_type=CertificationType.GLOBALGAP,
                required_documents=[DocumentType.PESTICIDE_RECORD],
                is_mandatory=True,
                compliance_level="MAJOR_MUST",
                guidance_en="Include product name, rate, date, applicator, PHI",
                guidance_ar="تضمين اسم المنتج، المعدل، التاريخ، المطبق، فترة ما قبل الحصاد",
            ),
            ComplianceRequirement(
                id="req_ggap_fert",
                code="GGAP-FERT-001",
                category="FERTILIZER_MANAGEMENT",
                title_en="Fertilizer Application Records",
                title_ar="سجلات تطبيق الأسمدة",
                description_en="Complete records of all fertilizer applications",
                description_ar="سجلات كاملة لجميع تطبيقات الأسمدة",
                certification_type=CertificationType.GLOBALGAP,
                required_documents=[DocumentType.FERTILIZER_RECORD],
                is_mandatory=True,
                compliance_level="MAJOR_MUST",
                guidance_en="Include product type, rate, date, application method",
                guidance_ar="تضمين نوع المنتج، المعدل، التاريخ، طريقة التطبيق",
            ),
            ComplianceRequirement(
                id="req_ggap_train",
                code="GGAP-TRAIN-001",
                category="TRAINING",
                title_en="Worker Training Certificates",
                title_ar="شهادات تدريب العمال",
                description_en="Training certificates for all farm workers",
                description_ar="شهادات التدريب لجميع عمال المزرعة",
                certification_type=CertificationType.GLOBALGAP,
                required_documents=[
                    DocumentType.TRAINING_CERTIFICATE,
                    DocumentType.SAFETY_CERTIFICATE,
                ],
                document_renewal_days=365,
                is_mandatory=True,
                compliance_level="MINOR_MUST",
                guidance_en="Include hygiene, safety, and first aid training",
                guidance_ar="تضمين التدريب على النظافة والسلامة والإسعافات الأولية",
            ),
            # Organic Requirements
            ComplianceRequirement(
                id="req_org_land",
                code="ORG-LAND-001",
                category="ORGANIC_COMPLIANCE",
                title_en="Land History Documentation",
                title_ar="توثيق تاريخ الأرض",
                description_en="Documentation of land use for past 3 years",
                description_ar="توثيق استخدام الأرض للسنوات الثلاث الماضية",
                certification_type=CertificationType.ORGANIC_LOCAL,
                required_documents=[DocumentType.REPORT],
                is_mandatory=True,
                compliance_level="MAJOR_MUST",
                guidance_en="Prove 3-year transition period for organic status",
                guidance_ar="إثبات فترة التحول 3 سنوات للحالة العضوية",
            ),
            ComplianceRequirement(
                id="req_org_inputs",
                code="ORG-INPUT-001",
                category="ORGANIC_COMPLIANCE",
                title_en="Organic Input Records",
                title_ar="سجلات المدخلات العضوية",
                description_en="Records of all organic-approved inputs used",
                description_ar="سجلات جميع المدخلات العضوية المعتمدة المستخدمة",
                certification_type=CertificationType.ORGANIC_LOCAL,
                required_documents=[
                    DocumentType.FERTILIZER_RECORD,
                    DocumentType.PESTICIDE_RECORD,
                ],
                is_mandatory=True,
                compliance_level="MAJOR_MUST",
                guidance_en="Only approved organic inputs must be documented",
                guidance_ar="يجب توثيق المدخلات العضوية المعتمدة فقط",
            ),
            # SFDA Requirements
            ComplianceRequirement(
                id="req_sfda_license",
                code="SFDA-LIC-001",
                category="REGULATORY",
                title_en="SFDA Facility License",
                title_ar="ترخيص منشأة الغذاء والدواء",
                description_en="Valid SFDA facility license",
                description_ar="ترخيص منشأة صالح من الغذاء والدواء",
                certification_type=CertificationType.SFDA,
                required_documents=[DocumentType.LICENSE],
                document_renewal_days=365,
                is_mandatory=True,
                compliance_level="MAJOR_MUST",
                regulatory_reference="Saudi Food & Drug Authority Regulations",
            ),
        ]

        for req in default_requirements:
            self._requirements[req.id] = req

    def _init_default_certification_bodies(self) -> None:
        """Initialize default certification bodies"""
        default_cbs = [
            CertificationBody(
                id="cb_sgs",
                name_en="SGS Saudi Arabia",
                name_ar="إس جي إس السعودية",
                code="SGS-SA",
                accreditation_number="SGS-001-SA",
                website="https://www.sgs.com.sa",
                email="agriculture.sa@sgs.com",
                country_code="SA",
                certification_types=[
                    CertificationType.GLOBALGAP,
                    CertificationType.GLOBALGAP_IFA,
                    CertificationType.ISO_22000,
                    CertificationType.HACCP,
                ],
            ),
            CertificationBody(
                id="cb_tuv",
                name_en="TUV Middle East",
                name_ar="تي يو في الشرق الأوسط",
                code="TUV-ME",
                accreditation_number="TUV-ME-001",
                website="https://www.tuv-me.com",
                email="info@tuv-me.com",
                country_code="AE",
                certification_types=[
                    CertificationType.GLOBALGAP,
                    CertificationType.ISO_22000,
                    CertificationType.ORGANIC_EU,
                ],
            ),
            CertificationBody(
                id="cb_intertek",
                name_en="Intertek Saudi Arabia",
                name_ar="إنترتك السعودية",
                code="ITK-SA",
                accreditation_number="ITK-001-SA",
                website="https://www.intertek.com",
                country_code="SA",
                certification_types=[
                    CertificationType.GLOBALGAP,
                    CertificationType.HALAL,
                    CertificationType.SASO,
                ],
            ),
            CertificationBody(
                id="cb_sfda",
                name_en="Saudi Food & Drug Authority",
                name_ar="الهيئة العامة للغذاء والدواء",
                code="SFDA",
                website="https://www.sfda.gov.sa",
                country_code="SA",
                certification_types=[CertificationType.SFDA],
            ),
            CertificationBody(
                id="cb_saso",
                name_en="Saudi Standards Organization",
                name_ar="الهيئة السعودية للمواصفات والمقاييس والجودة",
                code="SASO",
                website="https://www.saso.gov.sa",
                country_code="SA",
                certification_types=[CertificationType.SASO],
            ),
        ]

        for cb in default_cbs:
            self._certification_bodies[cb.id] = cb

    # ─────────────────────────────────────────────────────────────────────────
    # Certification Operations - عمليات الشهادات
    # ─────────────────────────────────────────────────────────────────────────

    async def create_certification(
        self,
        tenant_id: str,
        farm_id: str,
        certification_type: CertificationType,
        certificate_number: str,
        name_en: str,
        name_ar: str,
        issue_date: date,
        expiry_date: date,
        created_by: str,
        certification_body_id: str | None = None,
        scope_en: str | None = None,
        scope_ar: str | None = None,
        products_covered: list[str] | None = None,
        certified_area_hectares: float | None = None,
        ggn: str | None = None,
        certificate_document_id: str | None = None,
    ) -> Certification:
        """
        Create a new certification record
        إنشاء سجل شهادة جديد
        """
        cert_body = self._certification_bodies.get(certification_body_id) if certification_body_id else None

        certification = Certification(
            tenant_id=tenant_id,
            farm_id=farm_id,
            certification_type=certification_type,
            certificate_number=certificate_number,
            name_en=name_en,
            name_ar=name_ar,
            certification_body_id=certification_body_id,
            certification_body_name_en=cert_body.name_en if cert_body else None,
            certification_body_name_ar=cert_body.name_ar if cert_body else None,
            scope_en=scope_en,
            scope_ar=scope_ar,
            products_covered=products_covered or [],
            certified_area_hectares=certified_area_hectares,
            issue_date=issue_date,
            expiry_date=expiry_date,
            status=CertificationStatus.ACTIVE,
            ggn=ggn,
            certificate_document_id=certificate_document_id,
            created_by=created_by,
        )

        self._certifications[certification.id] = certification

        logger.info(
            "certification_created",
            certification_id=certification.id,
            farm_id=farm_id,
            certification_type=certification_type.value,
        )

        return certification

    async def get_certification(self, certification_id: str) -> Certification | None:
        """Get certification by ID"""
        return self._certifications.get(certification_id)

    async def list_certifications(
        self,
        tenant_id: str,
        farm_id: str | None = None,
        certification_type: CertificationType | None = None,
        status: CertificationStatus | None = None,
        include_expired: bool = False,
    ) -> list[Certification]:
        """
        List certifications with filters
        قائمة الشهادات مع الفلاتر
        """
        results = []

        for cert in self._certifications.values():
            if cert.tenant_id != tenant_id:
                continue
            if farm_id and cert.farm_id != farm_id:
                continue
            if certification_type and cert.certification_type != certification_type:
                continue
            if status and cert.status != status:
                continue
            if not include_expired and not cert.is_valid:
                continue

            results.append(cert)

        # Sort by expiry date
        results.sort(key=lambda c: c.expiry_date)
        return results

    async def update_certification_status(
        self,
        certification_id: str,
        status: CertificationStatus,
        updated_by: str,
        notes_en: str | None = None,
        notes_ar: str | None = None,
    ) -> Certification | None:
        """
        Update certification status
        تحديث حالة الشهادة
        """
        certification = self._certifications.get(certification_id)
        if not certification:
            return None

        certification.status = status
        certification.updated_by = updated_by
        certification.updated_at = datetime.now(UTC)

        if notes_en:
            certification.notes_en = notes_en
        if notes_ar:
            certification.notes_ar = notes_ar

        logger.info(
            "certification_status_updated",
            certification_id=certification_id,
            new_status=status.value,
            updated_by=updated_by,
        )

        return certification

    async def renew_certification(
        self,
        certification_id: str,
        new_issue_date: date,
        new_expiry_date: date,
        new_certificate_number: str | None = None,
        renewed_by: str | None = None,
        audit_report_document_id: str | None = None,
    ) -> Certification | None:
        """
        Renew an existing certification
        تجديد شهادة موجودة
        """
        certification = self._certifications.get(certification_id)
        if not certification:
            return None

        certification.issue_date = new_issue_date
        certification.expiry_date = new_expiry_date
        certification.status = CertificationStatus.ACTIVE
        certification.updated_at = datetime.now(UTC)
        certification.updated_by = renewed_by

        if new_certificate_number:
            certification.certificate_number = new_certificate_number

        if audit_report_document_id:
            certification.audit_report_document_ids.append(audit_report_document_id)

        logger.info(
            "certification_renewed",
            certification_id=certification_id,
            new_expiry_date=new_expiry_date.isoformat(),
        )

        return certification

    async def get_certification_summary(
        self,
        tenant_id: str,
        farm_id: str,
    ) -> CertificationSummary:
        """
        Get certification summary for farm
        الحصول على ملخص الشهادات للمزرعة
        """
        certs = await self.list_certifications(
            tenant_id=tenant_id,
            farm_id=farm_id,
            include_expired=True,
        )

        summary = CertificationSummary(
            total_certifications=len(certs),
            active_certifications=sum(1 for c in certs if c.status == CertificationStatus.ACTIVE and c.is_valid),
            expired_certifications=sum(1 for c in certs if c.status == CertificationStatus.EXPIRED or not c.is_valid),
            pending_certifications=sum(1 for c in certs if c.status == CertificationStatus.PENDING),
        )

        # Count by type
        for cert in certs:
            cert_type = cert.certification_type.value
            summary.by_type[cert_type] = summary.by_type.get(cert_type, 0) + 1

        # Expiring soon (within 90 days)
        today = date.today()
        for cert in certs:
            if cert.is_valid and cert.days_until_expiry <= 90:
                summary.expiring_soon.append(
                    {
                        "certification_id": cert.id,
                        "certification_type": cert.certification_type.value,
                        "name_en": cert.name_en,
                        "name_ar": cert.name_ar,
                        "expiry_date": cert.expiry_date.isoformat(),
                        "days_until_expiry": cert.days_until_expiry,
                    }
                )

        # Next audit date
        next_audits = [c.next_audit_date for c in certs if c.next_audit_date and c.next_audit_date >= today]
        if next_audits:
            summary.next_audit_date = min(next_audits)

        return summary

    # ─────────────────────────────────────────────────────────────────────────
    # Compliance Requirement Operations - عمليات متطلبات الامتثال
    # ─────────────────────────────────────────────────────────────────────────

    async def get_requirements(
        self,
        certification_type: CertificationType | None = None,
        category: str | None = None,
        is_mandatory: bool | None = None,
    ) -> list[ComplianceRequirement]:
        """
        Get compliance requirements
        الحصول على متطلبات الامتثال
        """
        results = []

        for req in self._requirements.values():
            if not req.is_active:
                continue
            if certification_type and req.certification_type != certification_type:
                continue
            if category and req.category != category:
                continue
            if is_mandatory is not None and req.is_mandatory != is_mandatory:
                continue

            results.append(req)

        return results

    async def get_requirement(self, requirement_id: str) -> ComplianceRequirement | None:
        """Get requirement by ID"""
        return self._requirements.get(requirement_id)

    async def create_requirement(
        self,
        requirement: ComplianceRequirement,
    ) -> ComplianceRequirement:
        """Create a new compliance requirement"""
        self._requirements[requirement.id] = requirement
        return requirement

    # ─────────────────────────────────────────────────────────────────────────
    # Compliance Document Operations - عمليات وثائق الامتثال
    # ─────────────────────────────────────────────────────────────────────────

    async def link_document_to_requirement(
        self,
        tenant_id: str,
        farm_id: str,
        requirement_id: str,
        document_id: str,
        certification_id: str | None = None,
        valid_from: date | None = None,
        valid_until: date | None = None,
    ) -> ComplianceDocument:
        """
        Link a document to a compliance requirement
        ربط وثيقة بمتطلب امتثال
        """
        compliance_doc = ComplianceDocument(
            tenant_id=tenant_id,
            farm_id=farm_id,
            requirement_id=requirement_id,
            document_id=document_id,
            certification_id=certification_id,
            status=ComplianceStatus.PENDING_REVIEW,
            valid_from=valid_from,
            valid_until=valid_until,
        )

        self._compliance_docs[compliance_doc.id] = compliance_doc

        logger.info(
            "document_linked_to_requirement",
            compliance_doc_id=compliance_doc.id,
            requirement_id=requirement_id,
            document_id=document_id,
        )

        return compliance_doc

    async def review_compliance_document(
        self,
        compliance_doc_id: str,
        status: ComplianceStatus,
        reviewed_by: str,
        review_notes_en: str | None = None,
        review_notes_ar: str | None = None,
    ) -> ComplianceDocument | None:
        """
        Review and update compliance document status
        مراجعة وتحديث حالة وثيقة الامتثال
        """
        compliance_doc = self._compliance_docs.get(compliance_doc_id)
        if not compliance_doc:
            return None

        compliance_doc.status = status
        compliance_doc.reviewed_by = reviewed_by
        compliance_doc.reviewed_at = datetime.now(UTC)
        compliance_doc.review_notes_en = review_notes_en
        compliance_doc.review_notes_ar = review_notes_ar
        compliance_doc.updated_at = datetime.now(UTC)

        logger.info(
            "compliance_document_reviewed",
            compliance_doc_id=compliance_doc_id,
            status=status.value,
            reviewed_by=reviewed_by,
        )

        return compliance_doc

    async def get_compliance_status(
        self,
        tenant_id: str,
        farm_id: str,
        certification_type: CertificationType | None = None,
    ) -> list[dict]:
        """
        Get compliance status for all requirements
        الحصول على حالة الامتثال لجميع المتطلبات
        """
        requirements = await self.get_requirements(certification_type=certification_type)
        status_list = []

        for req in requirements:
            # Find linked compliance documents
            linked_docs = [
                doc
                for doc in self._compliance_docs.values()
                if doc.tenant_id == tenant_id and doc.farm_id == farm_id and doc.requirement_id == req.id
            ]

            # Determine status
            if not linked_docs:
                status = "MISSING"
                document_status = None
            else:
                latest_doc = max(linked_docs, key=lambda d: d.created_at)
                if latest_doc.is_valid:
                    status = "COMPLIANT"
                elif latest_doc.status == ComplianceStatus.PENDING_REVIEW:
                    status = "PENDING_REVIEW"
                else:
                    status = "NON_COMPLIANT"
                document_status = latest_doc.status.value

            status_list.append(
                {
                    "requirement_id": req.id,
                    "requirement_code": req.code,
                    "title_en": req.title_en,
                    "title_ar": req.title_ar,
                    "is_mandatory": req.is_mandatory,
                    "compliance_level": req.compliance_level,
                    "status": status,
                    "document_status": document_status,
                    "linked_documents": len(linked_docs),
                }
            )

        return status_list

    async def get_compliance_summary(
        self,
        tenant_id: str,
        farm_id: str,
        certification_type: CertificationType | None = None,
    ) -> ComplianceSummary:
        """
        Get compliance summary for farm
        الحصول على ملخص الامتثال للمزرعة
        """
        status_list = await self.get_compliance_status(
            tenant_id=tenant_id,
            farm_id=farm_id,
            certification_type=certification_type,
        )

        summary = ComplianceSummary(
            total_requirements=len(status_list),
            compliant=sum(1 for s in status_list if s["status"] == "COMPLIANT"),
            non_compliant=sum(1 for s in status_list if s["status"] == "NON_COMPLIANT"),
            partially_compliant=0,
            pending_review=sum(1 for s in status_list if s["status"] == "PENDING_REVIEW"),
        )

        # Calculate compliance percentage
        if summary.total_requirements > 0:
            summary.compliance_percentage = (summary.compliant / summary.total_requirements) * 100

        # Missing documents
        for status in status_list:
            if status["status"] == "MISSING" and status["is_mandatory"]:
                summary.missing_documents.append(
                    {
                        "requirement_id": status["requirement_id"],
                        "requirement_code": status["requirement_code"],
                        "title_en": status["title_en"],
                        "title_ar": status["title_ar"],
                    }
                )

        return summary

    async def check_certification_compliance(
        self,
        tenant_id: str,
        farm_id: str,
        certification_type: CertificationType,
    ) -> dict:
        """
        Check if farm meets requirements for a certification
        التحقق مما إذا كانت المزرعة تستوفي متطلبات الشهادة
        """
        requirements = await self.get_requirements(certification_type=certification_type)
        status_list = await self.get_compliance_status(
            tenant_id=tenant_id,
            farm_id=farm_id,
            certification_type=certification_type,
        )

        mandatory_compliant = 0
        mandatory_total = 0
        major_must_compliant = 0
        major_must_total = 0
        minor_must_compliant = 0
        minor_must_total = 0

        issues = []

        for status in status_list:
            req = next((r for r in requirements if r.id == status["requirement_id"]), None)
            if not req:
                continue

            is_compliant = status["status"] == "COMPLIANT"

            if req.is_mandatory:
                mandatory_total += 1
                if is_compliant:
                    mandatory_compliant += 1
                else:
                    issues.append(
                        {
                            "requirement_code": req.code,
                            "title_en": req.title_en,
                            "title_ar": req.title_ar,
                            "compliance_level": req.compliance_level,
                            "status": status["status"],
                        }
                    )

            if req.compliance_level == "MAJOR_MUST":
                major_must_total += 1
                if is_compliant:
                    major_must_compliant += 1
            elif req.compliance_level == "MINOR_MUST":
                minor_must_total += 1
                if is_compliant:
                    minor_must_compliant += 1

        # GlobalGAP requires 100% Major Must and 95% Minor Must
        major_must_percentage = (major_must_compliant / major_must_total * 100) if major_must_total > 0 else 100
        minor_must_percentage = (minor_must_compliant / minor_must_total * 100) if minor_must_total > 0 else 100

        is_eligible = major_must_percentage >= 100 and minor_must_percentage >= 95

        return {
            "certification_type": certification_type.value,
            "is_eligible": is_eligible,
            "major_must": {
                "compliant": major_must_compliant,
                "total": major_must_total,
                "percentage": round(major_must_percentage, 1),
                "required_percentage": 100,
            },
            "minor_must": {
                "compliant": minor_must_compliant,
                "total": minor_must_total,
                "percentage": round(minor_must_percentage, 1),
                "required_percentage": 95,
            },
            "mandatory_compliant": mandatory_compliant,
            "mandatory_total": mandatory_total,
            "issues": issues,
            "message_en": (
                "Farm is eligible for certification" if is_eligible else "Farm does not meet certification requirements"
            ),
            "message_ar": ("المزرعة مؤهلة للحصول على الشهادة" if is_eligible else "المزرعة لا تستوفي متطلبات الشهادة"),
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Certification Body Operations - عمليات جهات الشهادات
    # ─────────────────────────────────────────────────────────────────────────

    async def get_certification_bodies(
        self,
        certification_type: CertificationType | None = None,
        country_code: str | None = None,
    ) -> list[CertificationBody]:
        """
        Get list of certification bodies
        الحصول على قائمة جهات الشهادات
        """
        results = []

        for cb in self._certification_bodies.values():
            if not cb.is_active:
                continue
            if certification_type and certification_type not in cb.certification_types:
                continue
            if country_code and cb.country_code != country_code:
                continue

            results.append(cb)

        return results

    async def get_certification_body(self, cb_id: str) -> CertificationBody | None:
        """Get certification body by ID"""
        return self._certification_bodies.get(cb_id)

    # ─────────────────────────────────────────────────────────────────────────
    # Verification Operations - عمليات التحقق
    # ─────────────────────────────────────────────────────────────────────────

    async def verify_globalgap_number(self, ggn: str) -> dict:
        """
        Verify GlobalGAP Number format and lookup
        التحقق من تنسيق رقم GlobalGAP والبحث
        """
        import re

        # Validate format
        if not re.match(r"^40\d{11}$", ggn):
            return {
                "valid_format": False,
                "error_en": "GGN must be 13 digits starting with 40",
                "error_ar": "رقم GGN يجب أن يكون 13 رقماً يبدأ بـ 40",
            }

        # Check if GGN exists in our system
        for cert in self._certifications.values():
            if cert.ggn == ggn:
                return {
                    "valid_format": True,
                    "found": True,
                    "certification_id": cert.id,
                    "farm_id": cert.farm_id,
                    "certification_type": cert.certification_type.value,
                    "status": cert.status.value,
                    "is_valid": cert.is_valid,
                    "expiry_date": cert.expiry_date.isoformat(),
                }

        # Note: In production, this would call the GlobalGAP API
        return {
            "valid_format": True,
            "found": False,
            "message_en": "GGN not found in local database. Use GlobalGAP portal for verification.",
            "message_ar": "لم يتم العثور على GGN في قاعدة البيانات المحلية. استخدم بوابة GlobalGAP للتحقق.",
            "verification_url": f"https://database.globalgap.org/database/search.html?searchField={ggn}",
        }
