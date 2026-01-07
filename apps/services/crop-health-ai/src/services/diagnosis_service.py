"""
Sahool Vision - Diagnosis Service
خدمة التشخيص

هذه الخدمة مسؤولة عن:
- إدارة عملية التشخيص الكاملة
- حفظ الصور
- إدارة سجل التشخيصات
"""

import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from ..models.diagnosis import DiagnosisResult

# Fixed relative imports - إصلاح الاستيرادات النسبية
from ..models.disease import CropType, DiseaseSeverity
from .disease_service import disease_service
from .prediction_service import prediction_service

logger = logging.getLogger("sahool-vision")

# Configuration
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "static/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
BASE_URL = os.getenv("BASE_URL", "http://localhost:8095")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
EXPERT_REVIEW_THRESHOLD = float(os.getenv("EXPERT_REVIEW_THRESHOLD", "0.5"))
MAX_HISTORY_SIZE = 1000


class DiagnosisService:
    """
    خدمة إدارة التشخيصات
    Diagnosis Management Service
    """

    def __init__(self):
        # TODO: MIGRATE TO POSTGRESQL
        # Current: self._history stored in-memory (lost on restart, limited to MAX_HISTORY_SIZE=1000)
        # Issues:
        #   - No persistence across service restarts
        #   - Limited to 1000 records (older records dropped)
        #   - No multi-instance support (each pod has separate history)
        #   - No complex queries (filtering by date range, aggregations)
        # Required:
        #   1. Create PostgreSQL table 'crop_diagnoses' with schema:
        #      - id (UUID, PK)
        #      - image_url (TEXT)
        #      - thumbnail_url (TEXT)
        #      - disease_id (VARCHAR)
        #      - disease_name (VARCHAR)
        #      - disease_name_ar (VARCHAR)
        #      - confidence (DECIMAL)
        #      - severity (VARCHAR)
        #      - crop_type (VARCHAR)
        #      - field_id (VARCHAR, indexed)
        #      - governorate (VARCHAR, indexed)
        #      - location (GEOGRAPHY POINT) -- for spatial queries
        #      - status (VARCHAR, indexed)
        #      - farmer_id (VARCHAR, indexed)
        #      - expert_notes (TEXT)
        #      - created_at (TIMESTAMP, indexed)
        #      - updated_at (TIMESTAMP)
        #   2. Create Tortoise ORM model: CropDiagnosis
        #   3. Create repository: DiagnosisRepository with methods:
        #      - create(diagnosis_data) -> CropDiagnosis
        #      - get_by_id(id) -> CropDiagnosis
        #      - get_history(filters, limit, offset) -> List[CropDiagnosis]
        #      - update_status(id, status, expert_notes) -> bool
        #      - get_stats() -> Dict (aggregation queries)
        #      - get_by_governorate(governorate) -> List (epidemic monitoring)
        #      - get_recent_by_disease(disease_id, days) -> List (outbreak detection)
        #   4. Update all methods to use repository:
        #      - diagnose() -> call DiagnosisRepository.create()
        #      - get_history() -> call DiagnosisRepository.get_history()
        #      - get_diagnosis_by_id() -> call DiagnosisRepository.get_by_id()
        #      - update_diagnosis_status() -> call DiagnosisRepository.update_status()
        #      - get_stats() -> call DiagnosisRepository.get_stats()
        #   5. Add database indexes for common queries:
        #      - governorate (epidemic monitoring by region)
        #      - created_at (time-series analysis)
        #      - field_id (field history)
        #      - farmer_id (farmer history)
        #   6. Consider partitioning by created_at for large datasets
        # Migration Priority: CRITICAL - Diagnosis history is essential for epidemic monitoring
        # In-memory diagnosis history (PostgreSQL in production)
        self._history: list[dict[str, Any]] = []

    def diagnose(
        self,
        image_bytes: bytes,
        filename: str,
        field_id: str | None = None,
        crop_type: CropType | None = None,
        symptoms: str | None = None,
        governorate: str | None = None,
        lat: float | None = None,
        lng: float | None = None,
        farmer_id: str | None = None,
    ) -> DiagnosisResult:
        """
        تشخيص مرض النبات من الصورة
        Diagnose plant disease from image
        """
        # Generate unique ID
        diagnosis_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        # Save image
        image_url = self._save_image(image_bytes, filename, diagnosis_id)

        # Run prediction
        disease_key, confidence, all_predictions = prediction_service.predict(image_bytes)

        # Get disease info
        disease_info = disease_service.get_disease(disease_key)
        if not disease_info:
            disease_info = disease_service.get_disease("healthy")

        # Determine expert review need
        needs_expert = confidence < EXPERT_REVIEW_THRESHOLD
        expert_reason = None
        if needs_expert:
            expert_reason = f"نسبة الثقة منخفضة ({confidence:.1%}). يُنصح بمراجعة مهندس زراعي."

        # Calculate severity
        severity = disease_info["severity_default"]
        if confidence < 0.5:
            severity = DiseaseSeverity.LOW

        # Check if urgent
        urgent = severity in [DiseaseSeverity.HIGH, DiseaseSeverity.CRITICAL]

        # Get detected crop
        detected_crop = disease_info.get("crop", CropType.UNKNOWN)

        # Save to history
        self._save_to_history(
            diagnosis_id=diagnosis_id,
            image_url=image_url,
            disease_key=disease_key,
            disease_info=disease_info,
            confidence=confidence,
            severity=severity,
            detected_crop=detected_crop,
            field_id=field_id,
            governorate=governorate,
            lat=lat,
            lng=lng,
            farmer_id=farmer_id,
            timestamp=timestamp,
        )

        # Build result
        diagnosis = DiagnosisResult(
            diagnosis_id=diagnosis_id,
            timestamp=timestamp,
            disease_name=disease_info["name"],
            disease_name_ar=disease_info["name_ar"],
            disease_description=disease_info["description"],
            disease_description_ar=disease_info["description_ar"],
            confidence=confidence,
            severity=severity,
            affected_area_percent=min(confidence * 100, 100),
            detected_crop=detected_crop,
            growth_stage=None,
            treatments=disease_info.get("treatments", []),
            urgent_action_required=urgent,
            needs_expert_review=needs_expert,
            expert_review_reason=expert_reason,
            weather_consideration=(
                "تجنب الرش قبل المطر" if disease_info.get("treatments") else None
            ),
            prevention_tips=disease_info.get("prevention", []),
            prevention_tips_ar=disease_info.get("prevention_ar", []),
            image_url=image_url,
        )

        logger.info(
            f"✅ Diagnosis completed: {disease_key} ({confidence:.2%}) for field {field_id}"
        )

        return diagnosis

    def batch_diagnose(
        self,
        images: list[tuple],  # List of (bytes, filename)
        field_id: str | None = None,
    ) -> dict[str, Any]:
        """تشخيص دفعة من الصور"""
        batch_id = str(uuid.uuid4())
        results = []

        for image_bytes, filename in images:
            disease_key, confidence, _ = prediction_service.predict(image_bytes)
            disease_info = disease_service.get_disease(disease_key)

            results.append(
                {
                    "filename": filename,
                    "disease": disease_key,
                    "confidence": confidence,
                    "disease_name_ar": (
                        disease_info.get("name_ar", "غير معروف") if disease_info else "غير معروف"
                    ),
                }
            )

        return {
            "batch_id": batch_id,
            "field_id": field_id,
            "total_images": len(images),
            "processed": len(results),
            "results": results,
            "summary": {
                "healthy_count": sum(1 for r in results if r["disease"] == "healthy"),
                "infected_count": sum(1 for r in results if r["disease"] != "healthy"),
                "average_confidence": (
                    sum(r["confidence"] for r in results) / len(results) if results else 0
                ),
            },
        }

    def get_history(
        self,
        status: str | None = None,
        severity: str | None = None,
        governorate: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """الحصول على سجل التشخيصات"""
        filtered = self._history.copy()

        if status:
            filtered = [d for d in filtered if d.get("status") == status]
        if severity:
            filtered = [d for d in filtered if d.get("severity") == severity]
        if governorate:
            filtered = [d for d in filtered if d.get("governorate") == governorate]

        return filtered[offset : offset + limit]

    def get_diagnosis_by_id(self, diagnosis_id: str) -> dict[str, Any] | None:
        """الحصول على تشخيص محدد"""
        for record in self._history:
            if record.get("id") == diagnosis_id:
                disease_key = record.get("disease_id")
                disease_info = disease_service.get_disease(disease_key)
                if disease_info:
                    record["treatments"] = [
                        t.model_dump() for t in disease_info.get("treatments", [])
                    ]
                    record["prevention_tips_ar"] = disease_info.get("prevention_ar", [])
                return record
        return None

    def update_diagnosis_status(
        self,
        diagnosis_id: str,
        status: str,
        expert_notes: str | None = None,
    ) -> dict[str, Any] | None:
        """تحديث حالة التشخيص"""
        for record in self._history:
            if record.get("id") == diagnosis_id:
                record["status"] = status
                if expert_notes:
                    record["expert_notes"] = expert_notes
                record["updated_at"] = datetime.utcnow().isoformat()

                logger.info(f"📝 Diagnosis {diagnosis_id} updated: status={status}")
                return {"success": True, "diagnosis_id": diagnosis_id, "status": status}

        return None

    def get_stats(self) -> dict[str, Any]:
        """إحصائيات التشخيصات"""
        if not self._history:
            return {
                "total": 0,
                "pending": 0,
                "confirmed": 0,
                "treated": 0,
                "critical_count": 0,
                "high_count": 0,
                "by_disease": {},
                "by_governorate": {},
            }

        total = len(self._history)
        pending = sum(1 for d in self._history if d.get("status") == "pending")
        confirmed = sum(1 for d in self._history if d.get("status") == "confirmed")
        treated = sum(1 for d in self._history if d.get("status") == "treated")
        critical = sum(1 for d in self._history if d.get("severity") == "critical")
        high = sum(1 for d in self._history if d.get("severity") == "high")

        by_disease = {}
        for d in self._history:
            disease = d.get("disease_name_ar", "غير معروف")
            by_disease[disease] = by_disease.get(disease, 0) + 1

        by_governorate = {}
        for d in self._history:
            gov = d.get("governorate") or "غير محدد"
            by_governorate[gov] = by_governorate.get(gov, 0) + 1

        return {
            "total": total,
            "pending": pending,
            "confirmed": confirmed,
            "treated": treated,
            "critical_count": critical,
            "high_count": high,
            "by_disease": by_disease,
            "by_governorate": by_governorate,
            "last_updated": datetime.utcnow().isoformat(),
        }

    # Allowed image extensions for security
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "bmp"}
    MAX_FILENAME_LENGTH = 255

    def _save_image(
        self,
        image_bytes: bytes,
        filename: str,
        diagnosis_id: str,
    ) -> str | None:
        """حفظ الصورة على القرص مع التحقق من الأمان"""
        try:
            # Security: Validate and sanitize filename
            if not filename or len(filename) > self.MAX_FILENAME_LENGTH:
                logger.warning(f"Invalid filename length: {len(filename) if filename else 0}")
                filename = "image.jpg"

            # Extract and validate extension
            file_ext = filename.split(".")[-1].lower() if "." in filename else "jpg"

            # Security: Only allow safe image extensions
            if file_ext not in self.ALLOWED_EXTENSIONS:
                logger.warning(f"Blocked unsafe file extension: {file_ext}")
                file_ext = "jpg"  # Default to safe extension

            # Security: Use UUID-based filename to prevent path traversal
            # Discard original filename completely
            new_filename = f"{diagnosis_id}.{file_ext}"
            file_path = UPLOAD_DIR / new_filename

            # Security: Ensure path doesn't escape upload directory
            resolved_path = file_path.resolve()
            if not str(resolved_path).startswith(str(UPLOAD_DIR.resolve())):
                logger.error(f"Path traversal attempt detected: {filename}")
                return None

            with open(file_path, "wb") as f:
                f.write(image_bytes)

            image_url = f"{BASE_URL}/static/uploads/{new_filename}"
            logger.info(f"📷 Image saved: {file_path}")
            return image_url

        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return None

    def _save_to_history(
        self,
        diagnosis_id: str,
        image_url: str | None,
        disease_key: str,
        disease_info: dict[str, Any],
        confidence: float,
        severity: DiseaseSeverity,
        detected_crop: CropType,
        field_id: str | None,
        governorate: str | None,
        lat: float | None,
        lng: float | None,
        farmer_id: str | None,
        timestamp: datetime,
    ) -> None:
        """حفظ التشخيص في السجل"""
        record = {
            "id": diagnosis_id,
            "image_url": image_url,
            "thumbnail_url": image_url,
            "disease_id": disease_key,
            "disease_name": disease_info["name"],
            "disease_name_ar": disease_info["name_ar"],
            "confidence": confidence,
            "severity": severity.value,
            "crop_type": (
                detected_crop.value if hasattr(detected_crop, "value") else str(detected_crop)
            ),
            "field_id": field_id,
            "governorate": governorate,
            "location": {"lat": lat, "lng": lng} if lat and lng else None,
            "status": "pending",
            "timestamp": timestamp.isoformat(),
            "farmer_id": farmer_id,
        }

        self._history.insert(0, record)

        if len(self._history) > MAX_HISTORY_SIZE:
            self._history.pop()


# Singleton instance
diagnosis_service = DiagnosisService()
