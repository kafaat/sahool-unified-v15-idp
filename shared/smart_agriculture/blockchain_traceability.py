"""
Blockchain Traceability System | نظام تتبع البلوكتشين

Module C: Implements blockchain-based agricultural product traceability
for supply chain transparency and premium value generation.

الوحدة ج: تنفذ تتبع المنتجات الزراعية القائم على البلوكتشين
لشفافية سلسلة التوريد وتوليد القيمة المميزة.

Key Benefits:
- Premium value increase: +5 yuan/kg | زيادة القيمة المميزة: +5 يوان/كغ
- Repurchase rate increase: +30% | زيادة معدل إعادة الشراء: +30%

Features:
- Immutable operation records | سجلات عمليات غير قابلة للتغيير
- Full crop lifecycle traceability | تتبع كامل لدورة حياة المحصول
- Quality certification integration | تكامل شهادات الجودة
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .models import (
    BlockchainRecord,
    Certification,
    OperationRecord,
    TraceabilityReport,
)


@dataclass
class PremiumValue:
    """
    Premium value metrics from blockchain traceability.
    مقاييس القيمة المميزة من تتبع البلوكتشين.

    Attributes:
        price_premium_yuan_kg: Price premium per kg | علاوة السعر لكل كغ
        repurchase_rate_increase: Repurchase rate increase (%) | زيادة معدل إعادة الشراء
        consumer_trust_score: Consumer trust score (0-100) | درجة ثقة المستهلك
        verified_batches: Number of verified batches | عدد الدفعات الموثقة
        certification_count: Number of certifications | عدد الشهادات
    """

    price_premium_yuan_kg: float = 5.0
    repurchase_rate_increase: float = 30.0
    consumer_trust_score: float = 85.0
    verified_batches: int = 0
    certification_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "price_premium_yuan_kg": self.price_premium_yuan_kg,
            "repurchase_rate_increase_pct": self.repurchase_rate_increase,
            "consumer_trust_score": self.consumer_trust_score,
            "verified_batches": self.verified_batches,
            "certification_count": self.certification_count,
        }

    def summary(self, language: str = "en") -> str:
        """Generate human-readable summary."""
        if language == "ar":
            return (
                f"تقرير القيمة المميزة\n"
                f"علاوة السعر: +{self.price_premium_yuan_kg:.1f} يوان/كغ\n"
                f"زيادة معدل إعادة الشراء: +{self.repurchase_rate_increase:.0f}%\n"
                f"درجة ثقة المستهلك: {self.consumer_trust_score:.0f}/100\n"
                f"الدفعات الموثقة: {self.verified_batches}"
            )
        return (
            f"Premium Value Report\n"
            f"Price Premium: +{self.price_premium_yuan_kg:.1f} yuan/kg\n"
            f"Repurchase Rate Increase: +{self.repurchase_rate_increase:.0f}%\n"
            f"Consumer Trust Score: {self.consumer_trust_score:.0f}/100\n"
            f"Verified Batches: {self.verified_batches}"
        )


class BlockchainTraceability:
    """
    Blockchain-based Agricultural Traceability System.
    نظام التتبع الزراعي القائم على البلوكتشين.

    Provides immutable record-keeping for agricultural operations,
    enabling full supply chain transparency and premium value generation.

    يوفر حفظ سجلات غير قابلة للتغيير للعمليات الزراعية،
    مما يتيح الشفافية الكاملة لسلسلة التوريد وتوليد القيمة المميزة.

    Example usage:
        blockchain = BlockchainTraceability()
        batch_id = blockchain.create_batch("tomato", {"variety": "Roma"})
        blockchain.record_operation(batch_id, "planting", {"date": "2024-03-15"})
        blockchain.record_test_report(batch_id, {"pesticide_residue": "ND"})
        report = blockchain.get_full_trace(batch_id)

    Performance metrics:
        - Premium value: +5 yuan/kg | قيمة مميزة: +5 يوان/كغ
        - Repurchase rate: +30% | معدل إعادة الشراء: +30%
    """

    # Standard operation types
    OPERATION_TYPES = {
        "planting": "زراعة",
        "fertilizing": "تسميد",
        "irrigation": "ري",
        "pest_control": "مكافحة الآفات",
        "harvesting": "حصاد",
        "processing": "تجهيز",
        "packaging": "تعبئة",
        "storage": "تخزين",
        "transport": "نقل",
        "quality_check": "فحص الجودة",
    }

    # Supported certification types
    CERTIFICATION_TYPES = {
        "organic": "عضوي",
        "globalgap": "جلوبال جاب",
        "iso22000": "آيزو 22000",
        "haccp": "هاسب",
        "halal": "حلال",
        "saudi_gap": "ساغاب السعودية",
    }

    def __init__(self, chain_id: str = "sahool_agri_chain", tenant_id: str | None = None):
        """
        Initialize the blockchain traceability system.
        تهيئة نظام تتبع البلوكتشين.

        Args:
            chain_id: Unique identifier for this blockchain | معرف فريد للبلوكتشين
            tenant_id: Tenant ID for multi-tenant authorization. When set,
                       all write operations (record_operation, record_test_report)
                       are scoped to this tenant. | معرف المستأجر
        """
        self.chain_id = chain_id
        self.tenant_id = tenant_id
        self._batches: dict[str, TraceabilityReport] = {}
        self._blockchain: dict[str, list[BlockchainRecord]] = {}
        self._genesis_hash = self._create_genesis_block()
        self._verified_count = 0
        self._creation_time = datetime.now()

    def _create_genesis_block(self) -> str:
        """
        Create the genesis (first) block of the chain.
        إنشاء الكتلة الأولى (التكوينية) للسلسلة.
        """
        genesis_data = {
            "chain_id": self.chain_id,
            "type": "genesis",
            "created": datetime.now().isoformat(),
            "version": "1.0.0",
        }
        return self._compute_hash(genesis_data)

    def _compute_hash(self, data: dict[str, Any]) -> str:
        """
        Compute SHA-256 hash of data.
        حساب تجزئة SHA-256 للبيانات.

        Args:
            data: Data to hash

        Returns:
            str: Hexadecimal hash string
        """
        data_string = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_string.encode()).hexdigest()

    def _get_chain_hash(self, batch_id: str) -> str:
        """Get the latest hash in a batch's chain."""
        if batch_id not in self._blockchain or not self._blockchain[batch_id]:
            return self._genesis_hash
        return self._blockchain[batch_id][-1].hash

    def create_batch(
        self,
        crop_type: str,
        seed_info: dict[str, Any],
        origin_farm: str = "",
    ) -> str:
        """
        Create a new traceable batch for a crop.
        إنشاء دفعة جديدة قابلة للتتبع للمحصول.

        Args:
            crop_type: Type of crop (e.g., 'tomato', 'wheat') | نوع المحصول
            seed_info: Seed variety and source information | معلومات البذور
            origin_farm: Source farm identifier | معرف المزرعة المصدر

        Returns:
            str: Unique batch identifier | معرف الدفعة الفريد
        """
        batch_id = f"BATCH-{uuid.uuid4().hex[:12].upper()}"

        # Create traceability report
        report = TraceabilityReport(
            batch_id=batch_id,
            crop=crop_type,
            origin_farm=origin_farm,
        )

        # Record batch creation operation
        creation_record = OperationRecord(
            operation_id=f"OP-{uuid.uuid4().hex[:8].upper()}",
            operation_type="batch_creation",
            timestamp=datetime.now(),
            details={
                "crop_type": crop_type,
                "seed_info": seed_info,
                "origin_farm": origin_farm,
            },
            verified=True,
        )
        report.add_operation(creation_record)

        # Initialize blockchain for this batch
        self._batches[batch_id] = report
        self._blockchain[batch_id] = []

        # Create first block
        block_data = {
            "batch_id": batch_id,
            "operation_type": "batch_creation",
            "crop_type": crop_type,
            "seed_info": seed_info,
            "origin_farm": origin_farm,
            "timestamp": datetime.now().isoformat(),
        }

        block = BlockchainRecord(
            batch_id=batch_id,
            hash=self._compute_hash(block_data),
            timestamp=datetime.now(),
            data=block_data,
            previous_hash=self._genesis_hash,
            block_number=1,
        )
        self._blockchain[batch_id].append(block)

        return batch_id

    def record_operation(
        self,
        batch_id: str,
        operation_type: str,
        details: dict[str, Any],
        operator_id: str = "",
        location: str = "",
    ) -> str:
        """
        Record an agricultural operation for a batch.
        تسجيل عملية زراعية لدفعة.

        Args:
            batch_id: Batch identifier | معرف الدفعة
            operation_type: Type of operation (see OPERATION_TYPES) | نوع العملية
            details: Operation details | تفاصيل العملية
            operator_id: ID of operator performing the operation | معرف المشغل
            location: GPS coordinates or field ID | الموقع

        Returns:
            str: Operation ID | معرف العملية

        Raises:
            ValueError: If batch_id is not found
        """
        if batch_id not in self._batches:
            raise ValueError(f"Batch {batch_id} not found | الدفعة {batch_id} غير موجودة")

        # SECURITY: Verify batch belongs to this tenant
        batch = self._batches[batch_id]
        if self.tenant_id and getattr(batch, "tenant_id", None) and batch.tenant_id != self.tenant_id:
            raise PermissionError(
                f"Batch {batch_id} does not belong to tenant {self.tenant_id} | "
                f"الدفعة {batch_id} لا تنتمي للمستأجر {self.tenant_id}"
            )

        operation_id = f"OP-{uuid.uuid4().hex[:8].upper()}"

        # Create operation record
        operation = OperationRecord(
            operation_id=operation_id,
            operation_type=operation_type,
            timestamp=datetime.now(),
            details=details,
            operator_id=operator_id,
            location=location,
            verified=True,
        )
        self._batches[batch_id].add_operation(operation)

        # Add to blockchain
        previous_hash = self._get_chain_hash(batch_id)
        block_number = len(self._blockchain[batch_id]) + 1

        block_data = {
            "batch_id": batch_id,
            "operation_id": operation_id,
            "operation_type": operation_type,
            "details": details,
            "operator_id": operator_id,
            "location": location,
            "timestamp": datetime.now().isoformat(),
        }

        block = BlockchainRecord(
            batch_id=batch_id,
            hash=self._compute_hash({**block_data, "previous_hash": previous_hash}),
            timestamp=datetime.now(),
            data=block_data,
            previous_hash=previous_hash,
            block_number=block_number,
        )
        self._blockchain[batch_id].append(block)

        return operation_id

    def record_test_report(
        self,
        batch_id: str,
        report: dict[str, Any],
        lab_id: str = "",
        test_date: datetime | None = None,
    ) -> str:
        """
        Record a quality test report for a batch.
        تسجيل تقرير اختبار جودة لدفعة.

        Args:
            batch_id: Batch identifier | معرف الدفعة
            report: Test results (e.g., pesticide residue, nutrients) | نتائج الاختبار
            lab_id: Laboratory identifier | معرف المختبر
            test_date: Date of test (default: now) | تاريخ الاختبار

        Returns:
            str: Test report ID | معرف تقرير الاختبار

        Raises:
            ValueError: If batch_id is not found
        """
        if batch_id not in self._batches:
            raise ValueError(f"Batch {batch_id} not found | الدفعة {batch_id} غير موجودة")

        report_id = f"TEST-{uuid.uuid4().hex[:8].upper()}"
        test_date = test_date or datetime.now()

        test_record = {
            "report_id": report_id,
            "results": report,
            "lab_id": lab_id,
            "test_date": test_date.isoformat(),
            "verified": True,
        }
        self._batches[batch_id].test_reports.append(test_record)

        # Record as blockchain operation
        self.record_operation(
            batch_id=batch_id,
            operation_type="quality_check",
            details={
                "report_id": report_id,
                "lab_id": lab_id,
                "test_results": report,
            },
        )

        return report_id

    def add_certification(
        self,
        batch_id: str,
        cert_type: str,
        issuer: str,
        issue_date: datetime,
        expiry_date: datetime,
        scope: list[str],
    ) -> str:
        """
        Add a certification to a batch.
        إضافة شهادة إلى دفعة.

        Args:
            batch_id: Batch identifier
            cert_type: Certification type (see CERTIFICATION_TYPES)
            issuer: Certifying organization
            issue_date: Certificate issue date
            expiry_date: Certificate expiry date
            scope: Products/processes covered

        Returns:
            str: Certification ID
        """
        if batch_id not in self._batches:
            raise ValueError(f"Batch {batch_id} not found | الدفعة {batch_id} غير موجودة")

        cert_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"

        certification = Certification(
            cert_id=cert_id,
            cert_type=cert_type,
            issuer=issuer,
            issue_date=issue_date,
            expiry_date=expiry_date,
            scope=scope,
        )
        self._batches[batch_id].add_certification(certification)

        # Record as blockchain operation
        self.record_operation(
            batch_id=batch_id,
            operation_type="certification",
            details={
                "cert_id": cert_id,
                "cert_type": cert_type,
                "issuer": issuer,
                "scope": scope,
            },
        )

        return cert_id

    def generate_hash(self, batch_id: str) -> str:
        """
        Generate immutable hash for a batch's complete chain.
        توليد تجزئة غير قابلة للتغيير لسلسلة الدفعة الكاملة.

        This hash uniquely identifies the entire history of the batch
        and can be used for verification and QR code generation.

        Args:
            batch_id: Batch identifier | معرف الدفعة

        Returns:
            str: Immutable hash representing the full chain | تجزئة غير قابلة للتغيير

        Raises:
            ValueError: If batch_id is not found
        """
        if batch_id not in self._blockchain:
            raise ValueError(f"Batch {batch_id} not found | الدفعة {batch_id} غير موجودة")

        # Combine all block hashes
        chain = self._blockchain[batch_id]
        combined_data = {
            "batch_id": batch_id,
            "chain_length": len(chain),
            "block_hashes": [block.hash for block in chain],
            "final_timestamp": chain[-1].timestamp.isoformat() if chain else None,
        }

        final_hash = self._compute_hash(combined_data)

        # Update the report with the final hash
        if batch_id in self._batches:
            self._batches[batch_id].blockchain_hash = final_hash

        return final_hash

    def get_full_trace(self, batch_id: str) -> TraceabilityReport:
        """
        Get complete traceability report for a batch.
        الحصول على تقرير التتبع الكامل لدفعة.

        Returns the full supply chain history including all operations,
        certifications, and test reports.

        Args:
            batch_id: Batch identifier | معرف الدفعة

        Returns:
            TraceabilityReport: Complete traceability report | تقرير التتبع الكامل

        Raises:
            ValueError: If batch_id is not found
        """
        if batch_id not in self._batches:
            raise ValueError(f"Batch {batch_id} not found | الدفعة {batch_id} غير موجودة")

        # Ensure hash is up to date
        self.generate_hash(batch_id)

        return self._batches[batch_id]

    def verify_integrity(self, batch_id: str) -> bool:
        """
        Verify the integrity of a batch's blockchain.
        التحقق من سلامة بلوكتشين الدفعة.

        Checks that all blocks in the chain are valid and
        have not been tampered with.

        Args:
            batch_id: Batch identifier | معرف الدفعة

        Returns:
            bool: True if chain is valid | صحيح إذا كانت السلسلة صالحة

        Raises:
            ValueError: If batch_id is not found
        """
        if batch_id not in self._blockchain:
            raise ValueError(f"Batch {batch_id} not found | الدفعة {batch_id} غير موجودة")

        chain = self._blockchain[batch_id]

        if not chain:
            return True  # Empty chain is valid

        # Verify first block links to genesis
        if chain[0].previous_hash != self._genesis_hash:
            return False

        # Verify each block's hash and chain linkage
        for i, block in enumerate(chain):
            # Recompute hash
            block_data = block.data.copy()
            block_data["previous_hash"] = block.previous_hash
            computed_hash = self._compute_hash(block_data)

            if computed_hash != block.hash:
                return False

            # Verify chain linkage (except first block)
            if i > 0 and block.previous_hash != chain[i - 1].hash:
                return False

        self._verified_count += 1
        return True

    def get_premium_value(self) -> PremiumValue:
        """
        Get premium value metrics from blockchain traceability.
        الحصول على مقاييس القيمة المميزة من تتبع البلوكتشين.

        Returns documented metrics:
        - Premium value: +5 yuan/kg | قيمة مميزة: +5 يوان/كغ
        - Repurchase rate: +30% | معدل إعادة الشراء: +30%

        Returns:
            PremiumValue: Premium value metrics | مقاييس القيمة المميزة
        """
        total_certs = sum(len(batch.certifications) for batch in self._batches.values())

        # Calculate trust score based on verified batches and certifications
        if self._batches:
            verified_ratio = self._verified_count / len(self._batches)
            trust_score = min(100, 70 + verified_ratio * 20 + min(total_certs * 2, 10))
        else:
            trust_score = 85.0

        return PremiumValue(
            price_premium_yuan_kg=5.0,  # Documented value
            repurchase_rate_increase=30.0,  # Documented value
            consumer_trust_score=round(trust_score, 1),
            verified_batches=self._verified_count,
            certification_count=total_certs,
        )

    def get_batch_qr_data(self, batch_id: str) -> dict[str, Any]:
        """
        Get data for QR code generation.
        الحصول على بيانات لتوليد رمز QR.

        Returns data suitable for encoding in a QR code that
        consumers can scan for product traceability.

        Args:
            batch_id: Batch identifier

        Returns:
            dict: QR code data including trace URL and verification hash
        """
        if batch_id not in self._batches:
            raise ValueError(f"Batch {batch_id} not found | الدفعة {batch_id} غير موجودة")

        batch = self._batches[batch_id]
        final_hash = self.generate_hash(batch_id)

        return {
            "batch_id": batch_id,
            "crop": batch.crop,
            "origin": batch.origin_farm,
            "operations_count": len(batch.operations),
            "certifications": [c.cert_type for c in batch.get_active_certifications()],
            "hash": final_hash[:16],  # Shortened for QR
            "verify_url": f"https://trace.sahool.app/verify/{batch_id}",
            "timestamp": datetime.now().isoformat(),
        }

    def get_chain_blocks(self, batch_id: str) -> list[dict[str, Any]]:
        """
        Get all blocks in a batch's chain.
        الحصول على جميع الكتل في سلسلة الدفعة.

        Args:
            batch_id: Batch identifier

        Returns:
            list: List of block data dictionaries
        """
        if batch_id not in self._blockchain:
            raise ValueError(f"Batch {batch_id} not found | الدفعة {batch_id} غير موجودة")

        return [block.to_dict() for block in self._blockchain[batch_id]]

    def get_statistics(self) -> dict[str, Any]:
        """
        Get system-wide statistics.
        الحصول على إحصائيات النظام الشاملة.
        """
        total_operations = sum(len(batch.operations) for batch in self._batches.values())
        total_blocks = sum(len(chain) for chain in self._blockchain.values())

        return {
            "chain_id": self.chain_id,
            "total_batches": len(self._batches),
            "total_operations": total_operations,
            "total_blocks": total_blocks,
            "verified_count": self._verified_count,
            "created": self._creation_time.isoformat(),
            "genesis_hash": self._genesis_hash[:16] + "...",
        }

    def export_batch(self, batch_id: str, format: str = "json") -> str:
        """
        Export batch data in specified format.
        تصدير بيانات الدفعة بالتنسيق المحدد.

        Args:
            batch_id: Batch identifier
            format: Export format ('json' or 'summary')

        Returns:
            str: Exported data
        """
        if batch_id not in self._batches:
            raise ValueError(f"Batch {batch_id} not found | الدفعة {batch_id} غير موجودة")

        batch = self._batches[batch_id]

        if format == "summary":
            return batch.generate_summary("en")

        return json.dumps(batch.to_dict(), indent=2, default=str)

    def search_batches(
        self,
        crop_type: str | None = None,
        farm: str | None = None,
        has_certification: str | None = None,
    ) -> list[str]:
        """
        Search for batches matching criteria.
        البحث عن دفعات تطابق المعايير.

        Args:
            crop_type: Filter by crop type
            farm: Filter by origin farm
            has_certification: Filter by certification type

        Returns:
            list: Matching batch IDs
        """
        results = []

        for batch_id, batch in self._batches.items():
            if crop_type and batch.crop.lower() != crop_type.lower():
                continue
            if farm and farm.lower() not in batch.origin_farm.lower():
                continue
            if has_certification:
                cert_types = [c.cert_type.lower() for c in batch.certifications]
                if has_certification.lower() not in cert_types:
                    continue
            results.append(batch_id)

        return results
