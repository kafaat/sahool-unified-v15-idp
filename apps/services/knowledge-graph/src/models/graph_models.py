"""
Core Graph Models for Knowledge Graph Service
النماذج الأساسية لخدمة الرسم البياني للمعرفة
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RelationshipType(str, Enum):
    """Types of relationships in the knowledge graph"""
    AFFECTS = "affects"  # Disease affects Crop
    TREATED_BY = "treated_by"  # Disease treated by Treatment
    USED_FOR = "used_for"  # Treatment used for Disease
    CAUSES = "causes"  # Environmental factor causes Disease
    PREVENTS = "prevents"  # Treatment prevents Disease
    ALLEVIATES = "alleviates"  # Treatment alleviates symptoms
    REQUIRES = "requires"  # Crop requires condition
    COMPATIBLE = "compatible"  # Treatments compatible with Crop
    FOLLOWS = "follows"  # One treatment follows another
    RESISTANT_TO = "resistant_to"  # Crop resistant to Disease


class Crop(BaseModel):
    """Crop entity in the knowledge graph"""
    id: str = Field(..., description="Unique crop identifier (e.g., 'wheat', 'tomato')")
    name_en: str = Field(..., description="English crop name")
    name_ar: str = Field(..., description="Arabic crop name")
    description_en: str | None = Field(None, description="English description")
    description_ar: str | None = Field(None, description="Arabic description")
    growing_season: str | None = Field(None, description="Growing season (spring/summer/fall/winter)")
    family: str | None = Field(None, description="Botanical family")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Additional attributes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "wheat",
                "name_en": "Wheat",
                "name_ar": "القمح",
                "growing_season": "winter",
                "family": "Poaceae"
            }
        }


class Disease(BaseModel):
    """Disease entity in the knowledge graph"""
    id: str = Field(..., description="Unique disease identifier")
    name_en: str = Field(..., description="English disease name")
    name_ar: str = Field(..., description="Arabic disease name")
    description_en: str | None = Field(None, description="English description")
    description_ar: str | None = Field(None, description="Arabic description")
    pathogen_type: str | None = Field(None, description="Type of pathogen (fungal, bacterial, viral, etc.)")
    symptoms_en: list[str] | None = Field(None, description="List of English symptoms")
    symptoms_ar: list[str] | None = Field(None, description="List of Arabic symptoms")
    severity_level: int | None = Field(None, ge=1, le=10, description="Severity level (1-10)")
    incubation_days: int | None = Field(None, description="Incubation period in days")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Additional attributes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "powdery-mildew-wheat",
                "name_en": "Powdery Mildew",
                "name_ar": "البياض الدقيقي",
                "pathogen_type": "fungal",
                "severity_level": 7,
                "symptoms_en": ["White powder coating", "Leaf distortion"]
            }
        }


class Treatment(BaseModel):
    """Treatment/Pesticide entity in the knowledge graph"""
    id: str = Field(..., description="Unique treatment identifier")
    name_en: str = Field(..., description="English treatment name")
    name_ar: str = Field(..., description="Arabic treatment name")
    description_en: str | None = Field(None, description="English description")
    description_ar: str | None = Field(None, description="Arabic description")
    treatment_type: str | None = Field(None, description="Type (fungicide, bactericide, insecticide, etc.)")
    active_ingredient: str | None = Field(None, description="Active ingredient")
    concentration: str | None = Field(None, description="Concentration/dosage (e.g., '0.2%')")
    application_method: str | None = Field(None, description="Application method (spray, drench, dust, etc.)")
    safety_level: int | None = Field(None, ge=1, le=5, description="Safety level (1=very safe, 5=dangerous)")
    environmental_impact: str | None = Field(None, description="Environmental impact")
    cost_per_liter: float | None = Field(None, description="Cost per liter/unit")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Additional attributes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "sulfur-dust",
                "name_en": "Sulfur Dust",
                "name_ar": "مسحوق الكبريت",
                "treatment_type": "fungicide",
                "active_ingredient": "Sulfur",
                "application_method": "dust",
                "safety_level": 1
            }
        }


class Relationship(BaseModel):
    """Relationship between entities in the knowledge graph"""
    id: str = Field(..., description="Unique relationship identifier")
    source_type: str = Field(..., description="Type of source entity (crop, disease, treatment)")
    source_id: str = Field(..., description="Source entity ID")
    target_type: str = Field(..., description="Type of target entity (crop, disease, treatment)")
    target_id: str = Field(..., description="Target entity ID")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score (0-1)")
    evidence: list[str] | None = Field(None, description="List of evidence references")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Additional attributes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "rel-powdery-mildew-wheat-affects",
                "source_type": "disease",
                "source_id": "powdery-mildew-wheat",
                "target_type": "crop",
                "target_id": "wheat",
                "relationship_type": "affects",
                "confidence": 0.95
            }
        }


class GraphNode(BaseModel):
    """Graph node representation"""
    id: str = Field(..., description="Node unique identifier")
    node_type: str = Field(..., description="Type of node (crop, disease, treatment)")
    label: str = Field(..., description="Display label")
    label_ar: str | None = Field(None, description="Arabic label")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Node metadata")


class GraphEdge(BaseModel):
    """Graph edge representation"""
    id: str = Field(..., description="Edge unique identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    confidence: float = Field(default=1.0, description="Confidence score")


class PathResponse(BaseModel):
    """Response for shortest path queries"""
    start_node: GraphNode = Field(..., description="Starting node")
    end_node: GraphNode = Field(..., description="Ending node")
    path: list[str] = Field(..., description="List of node IDs in path")
    length: int = Field(..., description="Length of path")
    edges: list[GraphEdge] = Field(..., description="Edges in the path")
    explanation: str | None = Field(None, description="Human-readable explanation")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    database: bool = Field(..., description="Database connection status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "knowledge-graph",
                "version": "1.0.0",
                "database": True,
                "timestamp": "2026-01-13T10:00:00"
            }
        }
