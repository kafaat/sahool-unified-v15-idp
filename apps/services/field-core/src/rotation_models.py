"""
SAHOOL Crop Rotation Database Models
نماذج قاعدة البيانات لتدوير المحاصيل

SQLAlchemy models for storing rotation plans and field history
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Date,
    JSON,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class RotationPlanModel(Base):
    """
    Rotation plan for a field
    خطة تدوير للحقل
    """
    __tablename__ = "rotation_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(100), unique=True, index=True, nullable=False)

    # Field information
    tenant_id = Column(String(100), index=True, nullable=False)
    field_id = Column(String(100), index=True, nullable=False)
    field_name = Column(String(255), nullable=False)

    # Plan period
    start_year = Column(Integer, nullable=False)
    end_year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Analysis scores
    diversity_score = Column(Float, default=0.0)
    soil_health_score = Column(Float, default=0.0)
    disease_risk_score = Column(Float, default=0.0)
    nitrogen_balance = Column(String(20), default="neutral")

    # Recommendations and warnings (stored as JSON)
    recommendations_ar = Column(JSON, default=list)
    recommendations_en = Column(JSON, default=list)
    warnings_ar = Column(JSON, default=list)
    warnings_en = Column(JSON, default=list)

    # Metadata
    created_by = Column(String(100), nullable=True)
    status = Column(String(20), default="draft")  # draft, active, completed

    # Relationships
    seasons = relationship("SeasonPlanModel", back_populates="rotation_plan", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_rotation_tenant_field", "tenant_id", "field_id"),
        Index("idx_rotation_years", "start_year", "end_year"),
    )


class SeasonPlanModel(Base):
    """
    Season plan within a rotation
    خطة موسم ضمن التدوير
    """
    __tablename__ = "season_plans"

    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(String(100), unique=True, index=True, nullable=False)

    # Foreign key to rotation plan
    rotation_plan_id = Column(Integer, ForeignKey("rotation_plans.id"), nullable=False)

    # Season information
    year = Column(Integer, nullable=False)
    season = Column(String(20), nullable=False)  # winter, summer, spring, autumn

    # Crop information
    crop_code = Column(String(50), nullable=False)
    crop_name_ar = Column(String(255), nullable=False)
    crop_name_en = Column(String(255), nullable=False)
    crop_family = Column(String(50), nullable=False)

    # Dates
    planting_date = Column(Date, nullable=True)
    harvest_date = Column(Date, nullable=True)

    # Yield
    expected_yield = Column(Float, nullable=True)
    actual_yield = Column(Float, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Status
    status = Column(String(20), default="planned")  # planned, planted, growing, harvested

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rotation_plan = relationship("RotationPlanModel", back_populates="seasons")

    __table_args__ = (
        Index("idx_season_year", "year"),
        Index("idx_season_crop", "crop_code", "crop_family"),
    )


class FieldHistoryModel(Base):
    """
    Historical crop data for a field
    البيانات التاريخية للمحاصيل في الحقل
    """
    __tablename__ = "field_history"

    id = Column(Integer, primary_key=True, index=True)
    history_id = Column(String(100), unique=True, index=True, nullable=False)

    # Field information
    tenant_id = Column(String(100), index=True, nullable=False)
    field_id = Column(String(100), index=True, nullable=False)

    # Season information
    year = Column(Integer, nullable=False)
    season = Column(String(20), nullable=False)

    # Crop information
    crop_code = Column(String(50), nullable=False)
    crop_name_ar = Column(String(255), nullable=False)
    crop_name_en = Column(String(255), nullable=False)
    crop_family = Column(String(50), nullable=False)

    # Dates
    planting_date = Column(Date, nullable=True)
    harvest_date = Column(Date, nullable=True)

    # Yield
    actual_yield = Column(Float, nullable=True)

    # Health indicators
    disease_incidents = Column(JSON, default=list)  # List of disease IDs
    pest_incidents = Column(JSON, default=list)     # List of pest IDs
    soil_quality_score = Column(Float, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_field_history_tenant_field", "tenant_id", "field_id"),
        Index("idx_field_history_year", "year", "season"),
        Index("idx_field_history_crop", "crop_code", "crop_family"),
    )


class RotationRuleOverrideModel(Base):
    """
    Custom rotation rules for specific tenants/fields
    قواعد تدوير مخصصة للمستأجرين/الحقول
    """
    __tablename__ = "rotation_rule_overrides"

    id = Column(Integer, primary_key=True, index=True)

    # Scope
    tenant_id = Column(String(100), index=True, nullable=True)  # None = global
    field_id = Column(String(100), index=True, nullable=True)   # None = all fields

    # Rule
    crop_family = Column(String(50), nullable=False)
    rule_type = Column(String(50), nullable=False)  # min_years, good_predecessor, bad_predecessor
    rule_value = Column(JSON, nullable=False)

    # Metadata
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)

    __table_args__ = (
        Index("idx_rule_override_scope", "tenant_id", "field_id"),
        Index("idx_rule_override_family", "crop_family"),
    )


class RotationRecommendationModel(Base):
    """
    AI/system generated rotation recommendations
    توصيات التدوير المولدة من النظام
    """
    __tablename__ = "rotation_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(String(100), unique=True, index=True, nullable=False)

    # Target
    tenant_id = Column(String(100), index=True, nullable=False)
    field_id = Column(String(100), index=True, nullable=False)

    # Recommendation
    recommended_crop_family = Column(String(50), nullable=False)
    recommended_crop_code = Column(String(50), nullable=False)
    season = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)

    # Scoring
    suitability_score = Column(Float, nullable=False)

    # Reasons
    reasons_ar = Column(JSON, default=list)
    reasons_en = Column(JSON, default=list)
    warnings_ar = Column(JSON, default=list)
    warnings_en = Column(JSON, default=list)

    # Status
    status = Column(String(20), default="pending")  # pending, accepted, rejected, applied
    user_feedback = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_recommendation_tenant_field", "tenant_id", "field_id"),
        Index("idx_recommendation_year_season", "year", "season"),
    )


# ============== Database Initialization ==============


def create_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)


def drop_tables(engine):
    """Drop all tables from the database"""
    Base.metadata.drop_all(bind=engine)


# ============== Example Usage ==============

"""
Example usage:

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create database engine
engine = create_engine("postgresql://user:password@localhost/sahool_rotation")

# Create tables
create_tables(engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Create rotation plan
plan = RotationPlanModel(
    plan_id="PLAN_001",
    tenant_id="TENANT_001",
    field_id="FIELD_001",
    field_name="Field 1",
    start_year=2025,
    end_year=2029,
    diversity_score=75.0,
    soil_health_score=80.0,
    disease_risk_score=20.0,
    nitrogen_balance="positive"
)

# Add season
season = SeasonPlanModel(
    season_id="SEASON_001",
    year=2025,
    season="winter",
    crop_code="WHEAT",
    crop_name_ar="قمح",
    crop_name_en="Wheat",
    crop_family="cereals",
    planting_date=date(2025, 10, 1),
    harvest_date=date(2026, 3, 1)
)

plan.seasons.append(season)
db.add(plan)
db.commit()
"""
