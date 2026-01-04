"""
Input Application Tracker
Links inventory with field operations, tracking all input applications to fields
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any


class ApplicationMethod(Enum):
    BROADCAST = "broadcast"  # Even spreading
    BAND = "band"  # In rows
    FOLIAR = "foliar"  # Spray on leaves
    DRIP = "drip"  # Through irrigation
    SOIL_INJECTION = "soil_injection"
    SEED_TREATMENT = "seed_treatment"
    AERIAL = "aerial"  # Drone/plane spray


class ApplicationPurpose(Enum):
    BASAL = "basal"  # At planting
    TOP_DRESSING = "top_dressing"  # During growth
    PEST_CONTROL = "pest_control"
    DISEASE_CONTROL = "disease_control"
    WEED_CONTROL = "weed_control"
    GROWTH_REGULATION = "growth_regulation"
    NUTRIENT_DEFICIENCY = "nutrient_deficiency"


@dataclass
class InputApplication:
    id: str
    field_id: str
    crop_season_id: str
    item_id: str  # Inventory item
    batch_lot_id: str | None

    # Application details
    application_date: datetime
    method: ApplicationMethod
    purpose: ApplicationPurpose
    quantity_applied: float
    unit: str
    area_covered_ha: float
    rate_per_ha: float  # Calculated: quantity / area

    # Conditions
    weather_conditions: dict | None = None  # {temp, humidity, wind}
    growth_stage: str | None = None

    # Operator
    applied_by: str = ""
    equipment_used: str | None = None

    # Safety & Compliance
    withholding_period_days: int | None = None  # Days before harvest
    safe_harvest_date: date | None = None
    ppe_used: list[str] = field(default_factory=list)  # Personal protective equipment

    # Cost
    unit_cost: float = 0.0
    total_cost: float = 0.0

    # Efficacy tracking
    target_pest_disease: str | None = None
    efficacy_rating: int | None = None  # 1-5
    notes: str | None = None

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "id": self.id,
            "field_id": self.field_id,
            "crop_season_id": self.crop_season_id,
            "item_id": self.item_id,
            "batch_lot_id": self.batch_lot_id,
            "application_date": self.application_date.isoformat(),
            "method": self.method.value,
            "purpose": self.purpose.value,
            "quantity_applied": self.quantity_applied,
            "unit": self.unit,
            "area_covered_ha": self.area_covered_ha,
            "rate_per_ha": self.rate_per_ha,
            "weather_conditions": self.weather_conditions,
            "growth_stage": self.growth_stage,
            "applied_by": self.applied_by,
            "equipment_used": self.equipment_used,
            "withholding_period_days": self.withholding_period_days,
            "safe_harvest_date": (
                self.safe_harvest_date.isoformat() if self.safe_harvest_date else None
            ),
            "ppe_used": self.ppe_used,
            "unit_cost": self.unit_cost,
            "total_cost": self.total_cost,
            "target_pest_disease": self.target_pest_disease,
            "efficacy_rating": self.efficacy_rating,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class ApplicationPlan:
    id: str
    field_id: str
    crop_season_id: str
    crop_type: str

    # Schedule
    planned_applications: list[dict] = field(
        default_factory=list
    )  # [{date, item_id, quantity, purpose}]
    total_fertilizer_kg: float = 0.0
    total_pesticide_l: float = 0.0
    estimated_cost: float = 0.0

    status: str = "draft"
    approved_by: str | None = None
    approved_at: datetime | None = None

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "id": self.id,
            "field_id": self.field_id,
            "crop_season_id": self.crop_season_id,
            "crop_type": self.crop_type,
            "planned_applications": self.planned_applications,
            "total_fertilizer_kg": self.total_fertilizer_kg,
            "total_pesticide_l": self.total_pesticide_l,
            "estimated_cost": self.estimated_cost,
            "status": self.status,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# Default withholding periods for common pesticides (in days)
DEFAULT_WITHHOLDING_PERIODS = {
    "PESTICIDE": 14,
    "HERBICIDE": 7,
    "FUNGICIDE": 10,
    "FERTILIZER": 0,
    "SEED": 0,
}


class ApplicationTracker:
    """Track input applications to fields and link with inventory"""

    def __init__(self, db):
        """
        Initialize the tracker with database connection
        Args:
            db: Prisma client instance
        """
        self.db = db

    async def record_application(
        self,
        field_id: str,
        crop_season_id: str,
        item_id: str,
        quantity: float,
        method: ApplicationMethod,
        purpose: ApplicationPurpose,
        applied_by: str,
        area_ha: float,
        application_date: datetime | None = None,
        **kwargs,
    ) -> InputApplication:
        """
        Record an input application and deduct from inventory.

        Steps:
        1. Validate item exists and has sufficient stock
        2. Calculate rate per hectare
        3. Deduct from inventory (FIFO from batches)
        4. Create stock movement record
        5. Calculate safe harvest date if applicable
        6. Create application record

        Args:
            field_id: Field identifier
            crop_season_id: Crop season identifier
            item_id: Inventory item ID
            quantity: Quantity applied
            method: Application method
            purpose: Application purpose
            applied_by: Person who applied
            area_ha: Area covered in hectares
            application_date: Date of application (defaults to now)
            **kwargs: Additional optional fields

        Returns:
            InputApplication object

        Raises:
            ValueError: If item not found or insufficient stock
        """
        # Step 1: Validate item exists
        item = await self.db.inventoryitem.find_unique(where={"id": item_id})
        if not item:
            raise ValueError(f"Inventory item {item_id} not found")

        # Check available quantity
        if item.availableQuantity < quantity:
            raise ValueError(
                f"Insufficient stock for {item.name_en}. "
                f"Available: {item.availableQuantity}, Requested: {quantity}"
            )

        # Step 2: Calculate rate per hectare
        rate_per_ha = quantity / area_ha if area_ha > 0 else 0

        # Step 3: Deduct from inventory using FIFO
        batch_lot_id = await self._deduct_from_batches(item_id, quantity)

        # Step 4: Create stock movement record
        await self.db.stockmovement.create(
            data={
                "itemId": item_id,
                "movementType": "FIELD_APPLICATION",
                "quantity": -quantity,  # Negative for outgoing
                "previousQty": item.currentQuantity,
                "newQty": item.currentQuantity - quantity,
                "unitCost": item.unitCost,
                "totalCost": (item.unitCost or 0) * quantity,
                "referenceType": "application",
                "fieldId": field_id,
                "cropSeasonId": crop_season_id,
                "performedBy": applied_by,
                "notes": f"Applied {quantity} {item.unit} using {method.value} for {purpose.value}",
            }
        )

        # Update item quantities
        await self.db.inventoryitem.update(
            where={"id": item_id},
            data={
                "currentQuantity": item.currentQuantity - quantity,
                "availableQuantity": item.availableQuantity - quantity,
            },
        )

        # Step 5: Calculate safe harvest date
        withholding_days = kwargs.get("withholding_period_days")
        if withholding_days is None:
            # Use default based on category
            withholding_days = DEFAULT_WITHHOLDING_PERIODS.get(item.category, 0)

        app_date = application_date or datetime.now()
        safe_harvest_date = None
        if withholding_days and withholding_days > 0:
            safe_harvest_date = (app_date + timedelta(days=withholding_days)).date()

        # Extract weather conditions
        weather_conditions = {
            "temperature": kwargs.get("temperature"),
            "humidity": kwargs.get("humidity"),
            "wind_speed": kwargs.get("wind_speed"),
        }
        # Remove None values
        weather_conditions = {
            k: v for k, v in weather_conditions.items() if v is not None
        }

        # Step 6: Create application record
        application_data = {
            "fieldId": field_id,
            "cropSeasonId": crop_season_id,
            "itemId": item_id,
            "batchLotId": batch_lot_id,
            "applicationDate": app_date,
            "method": method.value.upper(),
            "purpose": purpose.value.upper(),
            "quantityApplied": quantity,
            "unit": item.unit,
            "areaCoveredHa": area_ha,
            "ratePerHa": rate_per_ha,
            "appliedBy": applied_by,
            "withholdingDays": withholding_days,
            "safeHarvestDate": safe_harvest_date,
            "unitCost": item.unitCost,
            "totalCost": (item.unitCost or 0) * quantity,
            "temperature": kwargs.get("temperature"),
            "humidity": kwargs.get("humidity"),
            "windSpeed": kwargs.get("wind_speed"),
            "growthStage": kwargs.get("growth_stage"),
            "equipmentUsed": kwargs.get("equipment_used"),
            "ppeUsed": kwargs.get("ppe_used", []),
            "targetPest": kwargs.get("target_pest_disease"),
            "efficacyRating": kwargs.get("efficacy_rating"),
            "notes": kwargs.get("notes"),
        }

        application_record = await self.db.inputapplication.create(
            data=application_data
        )

        # Convert to dataclass
        return self._db_to_dataclass(application_record)

    async def _deduct_from_batches(self, item_id: str, quantity: float) -> str | None:
        """
        Deduct quantity from batches using FIFO (First In, First Out)

        Args:
            item_id: Item ID
            quantity: Quantity to deduct

        Returns:
            Batch lot ID if single batch used, None if multiple
        """
        # Get batches ordered by received date (FIFO)
        batches = await self.db.batchlot.find_many(
            where={"itemId": item_id, "remainingQty": {"gt": 0}},
            order_by={"receivedDate": "asc"},
        )

        if not batches:
            return None

        remaining = quantity
        used_batch_id = None
        batches_used = 0

        for batch in batches:
            if remaining <= 0:
                break

            deduct = min(remaining, batch.remainingQty)
            new_remaining = batch.remainingQty - deduct

            await self.db.batchlot.update(
                where={"id": batch.id}, data={"remainingQty": new_remaining}
            )

            remaining -= deduct
            used_batch_id = batch.id
            batches_used += 1

        # Return batch ID only if single batch was used
        return used_batch_id if batches_used == 1 else None

    async def get_field_applications(
        self,
        field_id: str,
        crop_season_id: str | None = None,
        category: str | None = None,  # fertilizer, pesticide
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[InputApplication]:
        """
        Get all applications for a field

        Args:
            field_id: Field ID
            crop_season_id: Optional crop season filter
            category: Optional item category filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of InputApplication objects
        """
        where_clause = {"fieldId": field_id}

        if crop_season_id:
            where_clause["cropSeasonId"] = crop_season_id

        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["gte"] = datetime.combine(start_date, datetime.min.time())
            if end_date:
                date_filter["lte"] = datetime.combine(end_date, datetime.max.time())
            where_clause["applicationDate"] = date_filter

        applications = await self.db.inputapplication.find_many(
            where=where_clause, order_by={"applicationDate": "desc"}
        )

        # Filter by category if specified (requires joining with inventory items)
        if category:
            filtered = []
            for app in applications:
                item = await self.db.inventoryitem.find_unique(where={"id": app.itemId})
                if item and item.category.upper() == category.upper():
                    filtered.append(app)
            applications = filtered

        return [self._db_to_dataclass(app) for app in applications]

    async def get_application_summary(self, field_id: str, crop_season_id: str) -> dict:
        """
        Get summary of all inputs applied to a crop season.

        Returns:
        - Total fertilizer by type (NPK breakdown)
        - Total pesticide by type
        - Total cost
        - Application timeline
        """
        applications = await self.get_field_applications(field_id, crop_season_id)

        # Initialize summary
        summary = {
            "field_id": field_id,
            "crop_season_id": crop_season_id,
            "total_applications": len(applications),
            "total_cost": 0.0,
            "by_category": {},
            "by_purpose": {},
            "by_method": {},
            "timeline": [],
            "fertilizer_details": {"total_kg": 0.0, "by_type": {}},
            "pesticide_details": {"total_l": 0.0, "by_type": {}},
        }

        for app in applications:
            # Get item details
            item = await self.db.inventoryitem.find_unique(where={"id": app.item_id})
            if not item:
                continue

            category = item.category

            # Total cost
            summary["total_cost"] += app.total_cost

            # By category
            if category not in summary["by_category"]:
                summary["by_category"][category] = {
                    "count": 0,
                    "total_quantity": 0.0,
                    "total_cost": 0.0,
                }
            summary["by_category"][category]["count"] += 1
            summary["by_category"][category]["total_quantity"] += app.quantity_applied
            summary["by_category"][category]["total_cost"] += app.total_cost

            # By purpose
            purpose = (
                app.purpose.value
                if isinstance(app.purpose, ApplicationPurpose)
                else app.purpose
            )
            if purpose not in summary["by_purpose"]:
                summary["by_purpose"][purpose] = {"count": 0, "total_cost": 0.0}
            summary["by_purpose"][purpose]["count"] += 1
            summary["by_purpose"][purpose]["total_cost"] += app.total_cost

            # By method
            method = (
                app.method.value
                if isinstance(app.method, ApplicationMethod)
                else app.method
            )
            if method not in summary["by_method"]:
                summary["by_method"][method] = {"count": 0}
            summary["by_method"][method]["count"] += 1

            # Timeline
            summary["timeline"].append(
                {
                    "date": app.application_date.isoformat(),
                    "item_name": item.name_en,
                    "quantity": app.quantity_applied,
                    "unit": app.unit,
                    "purpose": purpose,
                    "cost": app.total_cost,
                }
            )

            # Fertilizer details
            if category == "FERTILIZER":
                summary["fertilizer_details"]["total_kg"] += app.quantity_applied
                item_name = item.name_en
                if item_name not in summary["fertilizer_details"]["by_type"]:
                    summary["fertilizer_details"]["by_type"][item_name] = 0.0
                summary["fertilizer_details"]["by_type"][
                    item_name
                ] += app.quantity_applied

            # Pesticide details
            if category in ["PESTICIDE", "HERBICIDE", "FUNGICIDE"]:
                summary["pesticide_details"]["total_l"] += app.quantity_applied
                item_name = item.name_en
                if item_name not in summary["pesticide_details"]["by_type"]:
                    summary["pesticide_details"]["by_type"][item_name] = 0.0
                summary["pesticide_details"]["by_type"][
                    item_name
                ] += app.quantity_applied

        # Sort timeline by date
        summary["timeline"].sort(key=lambda x: x["date"])

        return summary

    async def create_application_plan(
        self,
        field_id: str,
        crop_season_id: str,
        crop_type: str,
        custom_applications: list[dict] | None = None,
    ) -> ApplicationPlan:
        """
        Generate recommended application plan based on:
        - Crop requirements from agro-advisor
        - Soil analysis (if available)
        - Growth stage schedule
        - Custom applications if provided

        Args:
            field_id: Field ID
            crop_season_id: Crop season ID
            crop_type: Type of crop
            custom_applications: Custom list of planned applications

        Returns:
            ApplicationPlan object
        """
        # For now, use a simple template-based approach
        # In production, this would integrate with agro-advisor service

        planned_apps = custom_applications or self._get_default_plan(crop_type)

        # Calculate totals
        total_fertilizer = 0.0
        total_pesticide = 0.0
        total_cost = 0.0

        for app in planned_apps:
            # Look up item to get category and cost
            item_id = app.get("item_id")
            if item_id:
                item = await self.db.inventoryitem.find_unique(where={"id": item_id})
                if item:
                    quantity = app.get("quantity", 0)
                    if item.category == "FERTILIZER":
                        total_fertilizer += quantity
                    elif item.category in ["PESTICIDE", "HERBICIDE", "FUNGICIDE"]:
                        total_pesticide += quantity

                    if item.unitCost:
                        total_cost += item.unitCost * quantity

        plan_data = {
            "fieldId": field_id,
            "cropSeasonId": crop_season_id,
            "cropType": crop_type,
            "plannedApplications": planned_apps,
            "totalFertilizerKg": total_fertilizer,
            "totalPesticideL": total_pesticide,
            "estimatedCost": total_cost,
            "status": "DRAFT",
        }

        plan_record = await self.db.applicationplan.create(data=plan_data)

        return ApplicationPlan(
            id=plan_record.id,
            field_id=plan_record.fieldId,
            crop_season_id=plan_record.cropSeasonId,
            crop_type=plan_record.cropType,
            planned_applications=plan_record.plannedApplications,
            total_fertilizer_kg=plan_record.totalFertilizerKg,
            total_pesticide_l=plan_record.totalPesticideL,
            estimated_cost=plan_record.estimatedCost,
            status=plan_record.status,
            approved_by=plan_record.approvedBy,
            approved_at=plan_record.approvedAt,
            created_at=plan_record.createdAt,
            updated_at=plan_record.updatedAt,
        )

    def _get_default_plan(self, crop_type: str) -> list[dict]:
        """Get default application plan template for a crop"""
        # Simple templates - in production, fetch from agro-advisor
        templates = {
            "wheat": [
                {
                    "stage": "basal",
                    "days_after_planting": 0,
                    "purpose": "BASAL",
                    "notes": "NPK at planting",
                },
                {
                    "stage": "tillering",
                    "days_after_planting": 30,
                    "purpose": "TOP_DRESSING",
                    "notes": "Nitrogen boost",
                },
                {
                    "stage": "heading",
                    "days_after_planting": 60,
                    "purpose": "TOP_DRESSING",
                    "notes": "Final nitrogen",
                },
            ],
            "tomato": [
                {
                    "stage": "transplant",
                    "days_after_planting": 0,
                    "purpose": "BASAL",
                    "notes": "Starter fertilizer",
                },
                {
                    "stage": "flowering",
                    "days_after_planting": 21,
                    "purpose": "TOP_DRESSING",
                    "notes": "Calcium + NPK",
                },
                {
                    "stage": "fruiting",
                    "days_after_planting": 45,
                    "purpose": "TOP_DRESSING",
                    "notes": "Potassium boost",
                },
            ],
        }

        return templates.get(crop_type.lower(), [])

    async def check_withholding_period(
        self, field_id: str, crop_season_id: str, harvest_date: date | None = None
    ) -> dict:
        """
        Check if harvest is safe based on pesticide withholding periods.

        Args:
            field_id: Field ID
            crop_season_id: Crop season ID
            harvest_date: Planned harvest date (defaults to today)

        Returns:
            Dict with:
            - is_safe: bool
            - days_remaining: int
            - blocking_applications: List
        """
        if harvest_date is None:
            harvest_date = date.today()

        applications = await self.get_field_applications(field_id, crop_season_id)

        blocking = []
        max_wait_days = 0

        for app in applications:
            if app.safe_harvest_date and app.safe_harvest_date > harvest_date:
                days_remaining = (app.safe_harvest_date - harvest_date).days
                max_wait_days = max(max_wait_days, days_remaining)

                # Get item details
                item = await self.db.inventoryitem.find_unique(
                    where={"id": app.item_id}
                )

                blocking.append(
                    {
                        "application_id": app.id,
                        "application_date": app.application_date.isoformat(),
                        "item_name": item.name_en if item else "Unknown",
                        "safe_harvest_date": app.safe_harvest_date.isoformat(),
                        "days_remaining": days_remaining,
                    }
                )

        return {
            "is_safe": len(blocking) == 0,
            "days_remaining": max_wait_days,
            "blocking_applications": blocking,
            "earliest_safe_date": (
                (harvest_date + timedelta(days=max_wait_days)).isoformat()
                if max_wait_days > 0
                else harvest_date.isoformat()
            ),
        }

    async def calculate_input_costs(self, field_id: str, crop_season_id: str) -> dict:
        """
        Calculate total input costs for a crop season

        Returns breakdown by category and item
        """
        summary = await self.get_application_summary(field_id, crop_season_id)

        return {
            "field_id": field_id,
            "crop_season_id": crop_season_id,
            "total_cost": summary["total_cost"],
            "by_category": summary["by_category"],
            "cost_per_application": (
                summary["total_cost"] / summary["total_applications"]
                if summary["total_applications"] > 0
                else 0
            ),
        }

    async def get_application_by_id(
        self, application_id: str
    ) -> InputApplication | None:
        """Get a single application by ID"""
        app = await self.db.inputapplication.find_unique(where={"id": application_id})
        if not app:
            return None
        return self._db_to_dataclass(app)

    def _db_to_dataclass(self, db_record) -> InputApplication:
        """Convert database record to InputApplication dataclass"""
        # Parse enums
        method = ApplicationMethod(db_record.method.lower())
        purpose = ApplicationPurpose(db_record.purpose.lower())

        # Build weather conditions dict
        weather = {}
        if db_record.temperature:
            weather["temperature"] = db_record.temperature
        if db_record.humidity:
            weather["humidity"] = db_record.humidity
        if db_record.windSpeed:
            weather["wind_speed"] = db_record.windSpeed

        return InputApplication(
            id=db_record.id,
            field_id=db_record.fieldId,
            crop_season_id=db_record.cropSeasonId,
            item_id=db_record.itemId,
            batch_lot_id=db_record.batchLotId,
            application_date=db_record.applicationDate,
            method=method,
            purpose=purpose,
            quantity_applied=db_record.quantityApplied,
            unit=db_record.unit,
            area_covered_ha=db_record.areaCoveredHa,
            rate_per_ha=db_record.ratePerHa,
            weather_conditions=weather if weather else None,
            growth_stage=db_record.growthStage,
            applied_by=db_record.appliedBy,
            equipment_used=db_record.equipmentUsed,
            withholding_period_days=db_record.withholdingDays,
            safe_harvest_date=db_record.safeHarvestDate,
            ppe_used=db_record.ppeUsed or [],
            unit_cost=db_record.unitCost or 0.0,
            total_cost=db_record.totalCost or 0.0,
            target_pest_disease=db_record.targetPest,
            efficacy_rating=db_record.efficacyRating,
            notes=db_record.notes,
            created_at=db_record.createdAt,
            updated_at=db_record.updatedAt,
        )
