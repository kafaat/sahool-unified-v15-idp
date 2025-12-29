"""
SAHOOL Field Service - Database Models
نماذج قاعدة البيانات باستخدام Tortoise ORM
"""

from tortoise import fields
from tortoise.models import Model


class Field(Model):
    """
    حقل زراعي
    Agricultural Field
    """

    id = fields.UUIDField(pk=True)
    tenant_id = fields.CharField(max_length=64, index=True)
    user_id = fields.CharField(max_length=64, index=True)

    # Basic Info
    name = fields.CharField(max_length=200)
    name_en = fields.CharField(max_length=200, null=True)
    status = fields.CharField(
        max_length=20, default="active"
    )  # active, inactive, archived, pending

    # Location - stored as JSON
    location = fields.JSONField()  # FieldLocation object

    # Boundary - GeoJSON Polygon
    boundary = fields.JSONField(null=True)  # GeoPolygon object

    # Area
    area_hectares = fields.FloatField()

    # Soil & Irrigation
    soil_type = fields.CharField(max_length=30, default="unknown")
    irrigation_source = fields.CharField(max_length=30, default="none")

    # Current Crop
    current_crop = fields.CharField(max_length=100, null=True)

    # Metadata
    metadata = fields.JSONField(null=True)

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "fields"
        unique_together = (("tenant_id", "name"),)
        indexes = [
            ("tenant_id", "user_id"),
            ("tenant_id", "status"),
            ("user_id", "status"),
        ]

    def __str__(self):
        return f"Field({self.name})"


class CropSeason(Model):
    """
    موسم محصول
    Crop Growing Season
    """

    id = fields.UUIDField(pk=True)
    field = fields.ForeignKeyField(
        "models.Field",
        related_name="crop_seasons",
        on_delete=fields.CASCADE,
        db_column="field_id"
    )
    tenant_id = fields.CharField(max_length=64, index=True)

    # Crop Info
    crop_type = fields.CharField(max_length=100)
    variety = fields.CharField(max_length=100, null=True)

    # Dates
    planting_date = fields.DateField()
    expected_harvest = fields.DateField(null=True)
    harvest_date = fields.DateField(null=True)

    # Status
    status = fields.CharField(
        max_length=20, default="planning"
    )  # planning, active, harvested, failed

    # Yield
    expected_yield_kg = fields.FloatField(null=True)
    actual_yield_kg = fields.FloatField(null=True)
    quality_grade = fields.CharField(max_length=50, null=True)

    # Additional Info
    seed_source = fields.CharField(max_length=200, null=True)
    notes = fields.TextField(null=True)

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "crop_seasons"
        indexes = [
            ("field_id", "status"),
            ("tenant_id", "crop_type"),
            ("planting_date",),
        ]

    def __str__(self):
        return f"CropSeason({self.crop_type} - {self.planting_date})"


class Zone(Model):
    """
    منطقة داخل الحقل
    Sub-zone within a field
    """

    id = fields.UUIDField(pk=True)
    field = fields.ForeignKeyField(
        "models.Field",
        related_name="zones",
        on_delete=fields.CASCADE,
        db_column="field_id"
    )
    tenant_id = fields.CharField(max_length=64, index=True)

    # Zone Info
    name = fields.CharField(max_length=100)
    name_ar = fields.CharField(max_length=100, null=True)

    # Boundary
    boundary = fields.JSONField()  # GeoPolygon object
    area_hectares = fields.FloatField()

    # Purpose
    purpose = fields.CharField(
        max_length=50
    )  # soil_difference, water_access, slope, shade, experimental, other
    notes = fields.TextField(null=True)

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "zones"
        indexes = [
            ("field_id",),
            ("tenant_id",),
        ]

    def __str__(self):
        return f"Zone({self.name})"


class NDVIRecord(Model):
    """
    سجل قياس NDVI
    NDVI Measurement Record
    """

    id = fields.UUIDField(pk=True)
    field = fields.ForeignKeyField(
        "models.Field",
        related_name="ndvi_records",
        on_delete=fields.CASCADE,
        db_column="field_id"
    )
    tenant_id = fields.CharField(max_length=64, index=True)

    # Date of observation
    date = fields.DateField(index=True)

    # NDVI values
    mean = fields.FloatField()
    min = fields.FloatField()
    max = fields.FloatField()
    std = fields.FloatField(null=True)

    # Quality
    cloud_cover_pct = fields.FloatField(null=True)
    source = fields.CharField(max_length=50, null=True)

    # Metadata
    metadata = fields.JSONField(null=True)

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "ndvi_records"
        unique_together = (("field_id", "date", "source"),)
        indexes = [
            ("field_id", "date"),
            ("tenant_id", "date"),
        ]

    def __str__(self):
        return f"NDVI({self.field_id} - {self.date})"
