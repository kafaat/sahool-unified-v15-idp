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
from .context_compression import context_compression_service
from .disease_service import disease_service
from .evaluation_scorer import evaluation_scorer
from .field_memory import field_memory
from .prediction_service import prediction_service

# Database imports for PostgreSQL migration
try:
    from ..repository import DiagnosisRepository
    _diagnosis_repository = DiagnosisRepository()
    DB_AVAILABLE = True
except ImportError:
    _diagnosis_repository = None
    DB_AVAILABLE = False

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
        # PostgreSQL migration completed - using DiagnosisRepository
        # Fallback to in-memory storage when database is not available
        # In-memory diagnosis history (used as fallback when PostgreSQL unavailable)
        self._history: list[dict[str, Any]] = []
        self._use_db = DB_AVAILABLE and _diagnosis_repository is not None
        if self._use_db:
            logger.info("✅ Using PostgreSQL for diagnosis storage")
        else:
            logger.warning("⚠️ PostgreSQL unavailable, using in-memory storage")

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

        # Record in field memory for pattern analysis
        if field_id:
            field_memory.record_diagnosis(
                field_id=field_id,
                diagnosis_id=diagnosis_id,
                disease_id=disease_key,
                disease_name_ar=disease_info["name_ar"],
                confidence=confidence,
                severity=severity.value,
                affected_area_percent=min(confidence * 100, 100),
            )

        # Score prediction for evaluation
        evaluation_scorer.score_prediction(
            diagnosis_id=diagnosis_id,
            predicted_disease=disease_key,
            predicted_confidence=confidence,
            field_id=field_id,
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
        """الحصول على سجل التشخيصات - PostgreSQL with in-memory fallback"""
        # Try PostgreSQL first
        if self._use_db and _diagnosis_repository:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Cannot await in sync context, use fallback
                    pass
                else:
                    return asyncio.run(_diagnosis_repository.get_history(
                        limit=limit,
                        offset=offset,
                        status=status,
                        governorate=governorate,
                    ))
            except Exception as e:
                logger.warning("PostgreSQL query failed, using fallback: %s", str(e))

        # Fallback to in-memory
        filtered = self._history.copy()

        if status:
            filtered = [d for d in filtered if d.get("status") == status]
        if severity:
            filtered = [d for d in filtered if d.get("severity") == severity]
        if governorate:
            filtered = [d for d in filtered if d.get("governorate") == governorate]

        return filtered[offset : offset + limit]

    def get_diagnosis_by_id(self, diagnosis_id: str) -> dict[str, Any] | None:
        """الحصول على تشخيص محدد - PostgreSQL with in-memory fallback"""
        record = None

        # Try PostgreSQL first
        if self._use_db and _diagnosis_repository:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_running():
                    record = asyncio.run(_diagnosis_repository.get_by_id(diagnosis_id))
            except Exception as e:
                logger.warning("PostgreSQL query failed, using fallback: %s", str(e))

        # Fallback to in-memory
        if record is None:
            for r in self._history:
                if r.get("id") == diagnosis_id:
                    record = r
                    break

        if record:
            disease_key = record.get("disease_id")
            disease_info = disease_service.get_disease(disease_key)
            if disease_info:
                record["treatments"] = [
                    t.model_dump() for t in disease_info.get("treatments", [])
                ]
                record["prevention_tips_ar"] = disease_info.get("prevention_ar", [])

        return record

    def update_diagnosis_status(
        self,
        diagnosis_id: str,
        status: str,
        expert_notes: str | None = None,
    ) -> dict[str, Any] | None:
        """تحديث حالة التشخيص - PostgreSQL with in-memory fallback"""
        updated = False

        # Try PostgreSQL first
        if self._use_db and _diagnosis_repository:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_running():
                    updated = asyncio.run(
                        _diagnosis_repository.update_status(diagnosis_id, status, expert_notes)
                    )
            except Exception as e:
                logger.warning("PostgreSQL update failed, using fallback: %s", str(e))

        # Also update in-memory (for consistency during migration)
        for record in self._history:
            if record.get("id") == diagnosis_id:
                record["status"] = status
                if expert_notes:
                    record["expert_notes"] = expert_notes
                record["updated_at"] = datetime.utcnow().isoformat()
                updated = True
                break

        if updated:
            logger.info("📝 Diagnosis %s updated: status=%s", diagnosis_id[:8], status)
            return {"success": True, "diagnosis_id": diagnosis_id, "status": status}

        return None

    def get_stats(self) -> dict[str, Any]:
        """إحصائيات التشخيصات - PostgreSQL with in-memory fallback"""
        # Try PostgreSQL first
        if self._use_db and _diagnosis_repository:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_running():
                    stats = asyncio.run(_diagnosis_repository.get_stats())
                    if stats and stats.get("total", 0) > 0:
                        # Add computed fields for compatibility
                        by_status = stats.get("by_status", {})
                        stats["pending"] = by_status.get("pending", 0)
                        stats["confirmed"] = by_status.get("confirmed", 0)
                        stats["treated"] = by_status.get("treated", 0)
                        stats["last_updated"] = datetime.utcnow().isoformat()
                        return stats
            except Exception as e:
                logger.warning("PostgreSQL stats failed, using fallback: %s", str(e))

        # Fallback to in-memory
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
        """حفظ التشخيص في السجل - PostgreSQL with in-memory fallback"""
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

        # Try to save to PostgreSQL first
        if self._use_db and _diagnosis_repository:
            import asyncio
            try:
                # Run async operation in sync context
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(_diagnosis_repository.create(record))
                else:
                    asyncio.run(_diagnosis_repository.create(record))
                logger.info("✅ Diagnosis saved to PostgreSQL: %s", diagnosis_id[:8])
            except Exception as e:
                logger.error("Failed to save to PostgreSQL, using fallback: %s", str(e))
                # Fallback to in-memory
                self._history.insert(0, record)
                if len(self._history) > MAX_HISTORY_SIZE:
                    self._history.pop()
        else:
            # Fallback to in-memory storage
            self._history.insert(0, record)
            if len(self._history) > MAX_HISTORY_SIZE:
                self._history.pop()


# Singleton instance
diagnosis_service = DiagnosisService()
