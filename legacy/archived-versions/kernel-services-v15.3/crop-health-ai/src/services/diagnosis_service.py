"""
Sahool Vision - Diagnosis Service
خدمة التشخيص

هذه الخدمة مسؤولة عن:
- إدارة عملية التشخيص الكاملة
- حفظ الصور
- إدارة سجل التشخيصات
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from models.disease import DiseaseSeverity, CropType
from models.diagnosis import DiagnosisResult, DiagnosisHistoryRecord
from services.disease_service import disease_service
from services.prediction_service import prediction_service

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
        # In-memory diagnosis history (PostgreSQL in production)
        self._history: List[Dict[str, Any]] = []

    def diagnose(
        self,
        image_bytes: bytes,
        filename: str,
        field_id: Optional[str] = None,
        crop_type: Optional[CropType] = None,
        symptoms: Optional[str] = None,
        governorate: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        farmer_id: Optional[str] = None,
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
            weather_consideration="تجنب الرش قبل المطر" if disease_info.get("treatments") else None,
            prevention_tips=disease_info.get("prevention", []),
            prevention_tips_ar=disease_info.get("prevention_ar", []),
            image_url=image_url,
        )

        logger.info(f"✅ Diagnosis completed: {disease_key} ({confidence:.2%}) for field {field_id}")

        return diagnosis

    def batch_diagnose(
        self,
        images: List[tuple],  # List of (bytes, filename)
        field_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """تشخيص دفعة من الصور"""
        batch_id = str(uuid.uuid4())
        results = []

        for image_bytes, filename in images:
            disease_key, confidence, _ = prediction_service.predict(image_bytes)
            disease_info = disease_service.get_disease(disease_key)

            results.append({
                "filename": filename,
                "disease": disease_key,
                "confidence": confidence,
                "disease_name_ar": disease_info.get("name_ar", "غير معروف") if disease_info else "غير معروف"
            })

        return {
            "batch_id": batch_id,
            "field_id": field_id,
            "total_images": len(images),
            "processed": len(results),
            "results": results,
            "summary": {
                "healthy_count": sum(1 for r in results if r["disease"] == "healthy"),
                "infected_count": sum(1 for r in results if r["disease"] != "healthy"),
                "average_confidence": sum(r["confidence"] for r in results) / len(results) if results else 0
            }
        }

    def get_history(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        governorate: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """الحصول على سجل التشخيصات"""
        filtered = self._history.copy()

        if status:
            filtered = [d for d in filtered if d.get("status") == status]
        if severity:
            filtered = [d for d in filtered if d.get("severity") == severity]
        if governorate:
            filtered = [d for d in filtered if d.get("governorate") == governorate]

        return filtered[offset:offset + limit]

    def get_diagnosis_by_id(self, diagnosis_id: str) -> Optional[Dict[str, Any]]:
        """الحصول على تشخيص محدد"""
        for record in self._history:
            if record.get("id") == diagnosis_id:
                disease_key = record.get("disease_id")
                disease_info = disease_service.get_disease(disease_key)
                if disease_info:
                    record["treatments"] = [t.model_dump() for t in disease_info.get("treatments", [])]
                    record["prevention_tips_ar"] = disease_info.get("prevention_ar", [])
                return record
        return None

    def update_diagnosis_status(
        self,
        diagnosis_id: str,
        status: str,
        expert_notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
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

    def get_stats(self) -> Dict[str, Any]:
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
            "last_updated": datetime.utcnow().isoformat()
        }

    def _save_image(
        self,
        image_bytes: bytes,
        filename: str,
        diagnosis_id: str,
    ) -> Optional[str]:
        """حفظ الصورة على القرص"""
        try:
            file_ext = filename.split(".")[-1] if "." in filename else "jpg"
            new_filename = f"{diagnosis_id}.{file_ext}"
            file_path = UPLOAD_DIR / new_filename

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
        image_url: Optional[str],
        disease_key: str,
        disease_info: Dict[str, Any],
        confidence: float,
        severity: DiseaseSeverity,
        detected_crop: CropType,
        field_id: Optional[str],
        governorate: Optional[str],
        lat: Optional[float],
        lng: Optional[float],
        farmer_id: Optional[str],
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
            "crop_type": detected_crop.value if hasattr(detected_crop, 'value') else str(detected_crop),
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
