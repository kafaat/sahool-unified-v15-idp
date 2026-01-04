"""
SAHOOL Agent Card Model - A2A Protocol
نموذج بطاقة وكيل سهول - بروتوكول A2A

Implements the Agent-to-Agent (A2A) protocol AgentCard specification.
ينفذ مواصفات بطاقة الوكيل لبروتوكول A2A.

Reference: https://github.com/a2a-protocol/spec
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl, validator


class SecurityScheme(str, Enum):
    """Security authentication schemes / مخططات المصادقة الأمنية"""

    API_KEY = "apiKey"
    BEARER = "bearer"
    OAUTH2 = "oauth2"
    MUTUAL_TLS = "mutualTLS"
    NONE = "none"


class InputMode(str, Enum):
    """Agent input modes / أنماط إدخال الوكيل"""

    TEXT = "text"
    STRUCTURED = "structured"
    MULTIMODAL = "multimodal"
    STREAM = "stream"


class OutputMode(str, Enum):
    """Agent output modes / أنماط إخراج الوكيل"""

    TEXT = "text"
    STRUCTURED = "structured"
    MULTIMODAL = "multimodal"
    STREAM = "stream"


class AgentCapability(BaseModel):
    """
    Agent capability definition
    تعريف قدرة الوكيل

    Describes a specific capability or function the agent can perform.
    يصف قدرة أو وظيفة محددة يمكن للوكيل أدائها.
    """

    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Capability description")
    description_ar: str | None = Field(None, description="Arabic description")
    input_schema: dict[str, Any] | None = Field(
        None, description="JSON Schema for input"
    )
    output_schema: dict[str, Any] | None = Field(
        None, description="JSON Schema for output"
    )
    examples: list[dict[str, Any]] | None = Field(
        default_factory=list, description="Usage examples"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "diagnose_disease",
                "description": "Diagnose crop diseases from symptoms",
                "description_ar": "تشخيص أمراض المحاصيل من الأعراض",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "crop_type": {"type": "string"},
                        "symptoms": {"type": "object"},
                    },
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "disease": {"type": "string"},
                        "confidence": {"type": "number"},
                    },
                },
            }
        }


class AgentSkill(BaseModel):
    """
    Agent skill/expertise area
    مهارة/مجال خبرة الوكيل

    Represents a domain or area of expertise for the agent.
    يمثل مجالًا أو منطقة خبرة للوكيل.
    """

    skill_id: str = Field(..., description="Unique skill identifier")
    name: str = Field(..., description="Skill name")
    name_ar: str | None = Field(None, description="Arabic name")
    level: Literal["beginner", "intermediate", "advanced", "expert"] = Field(
        ..., description="Proficiency level"
    )
    keywords: list[str] = Field(default_factory=list, description="Search keywords")

    class Config:
        json_schema_extra = {
            "example": {
                "skill_id": "crop_disease_diagnosis",
                "name": "Crop Disease Diagnosis",
                "name_ar": "تشخيص أمراض المحاصيل",
                "level": "expert",
                "keywords": ["disease", "diagnosis", "pathology", "pest"],
            }
        }


class AgentEndpoint(BaseModel):
    """
    Agent endpoint configuration
    تكوين نقطة نهاية الوكيل
    """

    url: HttpUrl = Field(..., description="Endpoint URL")
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = Field(
        default="POST", description="HTTP method"
    )
    headers: dict[str, str] | None = Field(
        default_factory=dict, description="Required headers"
    )
    timeout_seconds: int = Field(default=30, description="Request timeout")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://api.sahool.app/agents/disease-expert/invoke",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "timeout_seconds": 30,
            }
        }


class AgentMetadata(BaseModel):
    """
    Agent metadata and discovery information
    البيانات الوصفية للوكيل ومعلومات الاكتشاف
    """

    tags: list[str] = Field(default_factory=list, description="Searchable tags")
    category: str | None = Field(None, description="Agent category")
    organization: str | None = Field(None, description="Organization/owner")
    license: str | None = Field(None, description="License type")
    homepage: HttpUrl | None = Field(None, description="Agent homepage")
    documentation: HttpUrl | None = Field(None, description="Documentation URL")
    source_code: HttpUrl | None = Field(None, description="Source code repository")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tags": ["agriculture", "ai", "disease-detection"],
                "category": "agricultural-intelligence",
                "organization": "SAHOOL",
                "license": "MIT",
                "homepage": "https://sahool.app",
                "documentation": "https://docs.sahool.app/agents/disease-expert",
            }
        }


class AgentCard(BaseModel):
    """
    A2A Protocol Agent Card
    بطاقة الوكيل - بروتوكول A2A

    Complete agent specification following the A2A protocol.
    مواصفات كاملة للوكيل تتبع بروتوكول A2A.

    This is the core data structure for agent registry and discovery.
    هذا هو هيكل البيانات الأساسي لسجل واكتشاف الوكلاء.
    """

    # Core Identity / الهوية الأساسية
    agent_id: str = Field(..., description="Unique agent identifier", min_length=1)
    name: str = Field(..., description="Agent name", min_length=1)
    name_ar: str | None = Field(None, description="Arabic name")
    version: str = Field(
        ..., description="Agent version (semver)", pattern=r"^\d+\.\d+\.\d+$"
    )

    # Description / الوصف
    description: str = Field(..., description="Agent description", min_length=1)
    description_ar: str | None = Field(None, description="Arabic description")

    # Capabilities / القدرات
    capabilities: list[AgentCapability] = Field(
        default_factory=list, description="Agent capabilities"
    )
    skills: list[AgentSkill] = Field(
        default_factory=list, description="Agent skills/expertise"
    )

    # Communication / التواصل
    input_modes: list[InputMode] = Field(
        default_factory=lambda: [InputMode.TEXT, InputMode.STRUCTURED],
        description="Supported input modes",
    )
    output_modes: list[OutputMode] = Field(
        default_factory=lambda: [OutputMode.TEXT, OutputMode.STRUCTURED],
        description="Supported output modes",
    )

    # Endpoints / نقاط النهاية
    endpoint: AgentEndpoint = Field(..., description="Primary agent endpoint")
    health_endpoint: HttpUrl | None = Field(
        None, description="Health check endpoint"
    )

    # Security / الأمان
    security_scheme: SecurityScheme = Field(
        default=SecurityScheme.BEARER, description="Authentication scheme"
    )
    requires_authentication: bool = Field(
        default=True, description="Whether authentication is required"
    )

    # Dependencies / التبعيات
    dependencies: list[str] = Field(
        default_factory=list, description="Other agents this agent depends on"
    )

    # Metadata / البيانات الوصفية
    metadata: AgentMetadata = Field(
        default_factory=AgentMetadata, description="Additional metadata"
    )

    # Status / الحالة
    status: Literal["active", "inactive", "deprecated", "maintenance"] = Field(
        default="active", description="Agent status"
    )

    @validator("version")
    def validate_version(cls, v):
        """Validate semantic versioning format"""
        parts = v.split(".")
        if len(parts) != 3:
            raise ValueError("Version must follow semver format (e.g., 1.0.0)")
        try:
            [int(p) for p in parts]
        except ValueError:
            raise ValueError("Version parts must be integers")
        return v

    @validator("agent_id")
    def validate_agent_id(cls, v):
        """Validate agent ID format"""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "Agent ID must contain only alphanumeric characters, hyphens, and underscores"
            )
        return v

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary
        تحويل إلى قاموس
        """
        return self.model_dump(exclude_none=True)

    def to_json(self) -> str:
        """
        Convert to JSON string
        تحويل إلى نص JSON
        """
        return self.model_dump_json(exclude_none=True, indent=2)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentCard":
        """
        Create from dictionary
        إنشاء من قاموس
        """
        return cls(**data)

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "disease-expert-agent",
                "name": "Disease Expert Agent",
                "name_ar": "وكيل خبير الأمراض",
                "version": "1.0.0",
                "description": "AI agent specialized in diagnosing crop diseases",
                "description_ar": "وكيل ذكاء اصطناعي متخصص في تشخيص أمراض المحاصيل",
                "capabilities": [
                    {
                        "name": "diagnose_disease",
                        "description": "Diagnose crop diseases from symptoms",
                        "input_schema": {"type": "object"},
                        "output_schema": {"type": "object"},
                    }
                ],
                "skills": [
                    {
                        "skill_id": "crop_pathology",
                        "name": "Crop Pathology",
                        "level": "expert",
                        "keywords": ["disease", "diagnosis"],
                    }
                ],
                "input_modes": ["text", "structured", "multimodal"],
                "output_modes": ["text", "structured"],
                "endpoint": {
                    "url": "https://api.sahool.app/agents/disease-expert/invoke",
                    "method": "POST",
                },
                "health_endpoint": "https://api.sahool.app/agents/disease-expert/health",
                "security_scheme": "bearer",
                "requires_authentication": True,
                "dependencies": ["crop-health-service", "satellite-service"],
                "status": "active",
            }
        }
