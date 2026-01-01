"""
Crop Domain Events
==================

Events related to crop lifecycle and health.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Any, Dict, List, Optional
from uuid import UUID

from .base import BaseEvent


@dataclass
class CropPlantedEvent(BaseEvent):
    """Event emitted when a crop is planted"""

    EVENT_TYPE = "crop.planted"
    EVENT_VERSION = "1.0.0"
    SCHEMA_PATH = "crop.planted.v1.json"

    field_id: UUID = None
    crop_type: str = ""
    variety: str = ""
    planting_date: date = None
    expected_harvest_date: Optional[date] = None
    seed_source: Optional[str] = None
    planting_density: Optional[float] = None

    def _payload_to_dict(self) -> Dict[str, Any]:
        payload = {
            "field_id": str(self.field_id),
            "crop_type": self.crop_type,
            "variety": self.variety,
            "planting_date": (
                self.planting_date.isoformat() if self.planting_date else None
            ),
        }
        if self.expected_harvest_date:
            payload["expected_harvest_date"] = self.expected_harvest_date.isoformat()
        if self.seed_source:
            payload["seed_source"] = self.seed_source
        if self.planting_density:
            payload["planting_density"] = self.planting_density
        return payload


@dataclass
class CropDiseaseDetectedEvent(BaseEvent):
    """Event emitted when disease is detected in a crop"""

    EVENT_TYPE = "crop.disease_detected"
    EVENT_VERSION = "1.0.0"
    SCHEMA_PATH = "crop.disease_detected.v1.json"
    PRIORITY = "high"

    field_id: UUID = None
    crop_id: Optional[UUID] = None
    disease_type: str = ""
    disease_category: Optional[str] = None
    confidence_score: float = 0.0
    detected_at: datetime = None
    affected_area_percentage: float = 0.0
    severity_level: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
    detection_method: Optional[str] = None
    recommended_actions: List[Dict[str, Any]] = field(default_factory=list)

    def _payload_to_dict(self) -> Dict[str, Any]:
        payload = {
            "field_id": str(self.field_id),
            "disease_type": self.disease_type,
            "confidence_score": self.confidence_score,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "affected_area_percentage": self.affected_area_percentage,
        }
        if self.crop_id:
            payload["crop_id"] = str(self.crop_id)
        if self.disease_category:
            payload["disease_category"] = self.disease_category
        if self.severity_level:
            payload["severity_level"] = self.severity_level
        if self.image_urls:
            payload["image_urls"] = self.image_urls
        if self.detection_method:
            payload["detection_method"] = self.detection_method
        if self.recommended_actions:
            payload["recommended_actions"] = self.recommended_actions
        return payload


@dataclass
class CropHarvestedEvent(BaseEvent):
    """Event emitted when a crop is harvested"""

    EVENT_TYPE = "crop.harvested"
    EVENT_VERSION = "1.0.0"
    SCHEMA_PATH = "crop.harvested.v1.json"

    field_id: UUID = None
    crop_id: UUID = None
    harvest_date: date = None
    yield_kg: float = 0.0
    area_harvested_hectares: float = 0.0
    quality_grade: Optional[str] = None
    moisture_content: Optional[float] = None
    storage_location: Optional[str] = None

    def _payload_to_dict(self) -> Dict[str, Any]:
        payload = {
            "field_id": str(self.field_id),
            "crop_id": str(self.crop_id),
            "harvest_date": (
                self.harvest_date.isoformat() if self.harvest_date else None
            ),
            "yield_kg": self.yield_kg,
            "area_harvested_hectares": self.area_harvested_hectares,
        }
        if self.quality_grade:
            payload["quality_grade"] = self.quality_grade
        if self.moisture_content:
            payload["moisture_content"] = self.moisture_content
        if self.storage_location:
            payload["storage_location"] = self.storage_location
        return payload
