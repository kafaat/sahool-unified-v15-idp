"""
Leveling optimization API endpoints.

نقاط نهاية API لتحسين التسوية

Tenant isolation is enforced via JWT claim ``tid`` (surfaced on the authenticated
``User`` as ``tenant_id``). The service does NOT honour the ``X-Tenant-Id`` header
for authorization — if you need the tenant identifier, read it from
``current_user.tenant_id``.
"""

import re
import uuid
from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request

from shared.events.subjects import SAHOOL_TERRAIN_SIMULATION_COMPLETED, get_tenant_subject

from ...core.config import settings
from ...utils.leveling_algorithms import (
    LevelingOptimizer,
    PlaneParameters,
    Point3D,
)
from ..schemas import (
    CostEstimate,
    CutFillVolume,
    DesignPlane,
    ElevationPoint,
    EquipmentRecommendation,
    EquipmentType,
    ErrorResponse,
    LevelingAnalysisRequest,
    LevelingAnalysisResponse,
    LevelingMethod,
    LevelingPlan,
    LevelingPriority,
    SimulationRequest,
    SimulationResult,
)

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Authentication dependency & user type
# ---------------------------------------------------------------------------
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:  # pragma: no cover - offline/unit-test fallback
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

    _bearer_scheme = HTTPBearer(auto_error=False)

    class User:  # type: ignore[no-redef]
        """Fallback User shape when shared.auth is unavailable."""

        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user(  # type: ignore[no-redef]
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ) -> User:
        """Lightweight auth - validates Authorization header presence."""
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        u = User()
        u.id = "fallback"
        u.tenant_id = None
        return u


# ---------------------------------------------------------------------------
# Safe logging helpers (CodeQL log-injection guard)
# ---------------------------------------------------------------------------
_LOG_INJ_RE = re.compile(r"[\r\n\t\x00-\x1f\x7f]")


def _safe_log(value: object) -> str:
    """Strip control chars so attacker-controlled values can't forge log lines."""
    if value is None:
        return ""
    return _LOG_INJ_RE.sub("?", str(value))[:200]


# ---------------------------------------------------------------------------
# Field ID validation (defensive, avoids path-traversal-like inputs in logs)
# ---------------------------------------------------------------------------
_FIELD_ID_RE = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")


def _validate_field_id(field_id: str) -> str:
    if not field_id or not _FIELD_ID_RE.match(field_id):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid field_id",
                "error_ar": "معرف حقل غير صالح",
            },
        )
    return field_id


router = APIRouter(prefix="/api/v1/leveling", tags=["Leveling | التسوية"])

# Equipment name translations
EQUIPMENT_NAMES = {
    EquipmentType.BULLDOZER: ("Bulldozer", "جرافة"),
    EquipmentType.SCRAPER: ("Scraper", "كاشطة"),
    EquipmentType.GRADER: ("Motor Grader", "ممهدة"),
    EquipmentType.LASER_LEVELER: ("Laser Leveler", "مسوي ليزر"),
    EquipmentType.EXCAVATOR: ("Excavator", "حفارة"),
    EquipmentType.DUMP_TRUCK: ("Dump Truck", "شاحنة قلابة"),
}

# Equipment productivity and costs
EQUIPMENT_CONFIG = {
    EquipmentType.BULLDOZER: {
        "productivity": settings.BULLDOZER_PRODUCTIVITY,
        "cost_per_hour": settings.BULLDOZER_COST_PER_HOUR,
        "recommended_for": "General earthmoving, short hauls | نقل التربة العام، المسافات القصيرة",
    },
    EquipmentType.SCRAPER: {
        "productivity": settings.SCRAPER_PRODUCTIVITY,
        "cost_per_hour": settings.SCRAPER_COST_PER_HOUR,
        "recommended_for": "Large volumes, medium hauls | الأحجام الكبيرة، المسافات المتوسطة",
    },
    EquipmentType.GRADER: {
        "productivity": settings.GRADER_PRODUCTIVITY,
        "cost_per_hour": settings.GRADER_COST_PER_HOUR,
        "recommended_for": "Fine grading, finishing | التسوية الدقيقة، التشطيب",
    },
    EquipmentType.LASER_LEVELER: {
        "productivity": settings.LASER_LEVELER_PRODUCTIVITY,
        "cost_per_hour": settings.LASER_LEVELER_COST_PER_HOUR,
        "recommended_for": "Precision leveling, irrigation fields | التسوية الدقيقة، حقول الري",
    },
    EquipmentType.EXCAVATOR: {
        "productivity": settings.EXCAVATOR_PRODUCTIVITY,
        "cost_per_hour": settings.EXCAVATOR_COST_PER_HOUR,
        "recommended_for": "Deep cuts, loading trucks | القطع العميق، تحميل الشاحنات",
    },
    EquipmentType.DUMP_TRUCK: {
        "productivity": 0,  # Supporting equipment
        "cost_per_hour": settings.DUMP_TRUCK_COST_PER_HOUR,
        "recommended_for": "Hauling material for long distances | نقل المواد للمسافات الطويلة",
    },
}


def _convert_points(elevation_points: list[ElevationPoint]) -> list[Point3D]:
    """Convert API elevation points to internal Point3D format."""
    return [Point3D(x=p.x, y=p.y, z=p.elevation, point_id=p.point_id) for p in elevation_points]


def _calculate_cost_estimate(
    cut_fill: CutFillVolume,
    field_area_hectares: float,
    haul_distance: float,
    equipment_recommendations: list[EquipmentRecommendation],
) -> CostEstimate:
    """
    Calculate detailed cost estimate in SAR.

    حساب تقدير التكلفة المفصل بالريال السعودي
    """
    total_volume = cut_fill.cut_volume_m3 + cut_fill.fill_volume_m3

    # Equipment costs from recommendations
    equipment_cost = sum(eq.total_cost_sar for eq in equipment_recommendations)

    # Estimate hours based on total volume and average productivity
    avg_productivity = 80.0  # m³/hour average
    estimated_hours = total_volume / avg_productivity if avg_productivity > 0 else 0

    # Labor cost (operators)
    num_operators = max(1, len([eq for eq in equipment_recommendations if eq.quantity > 0]))
    labor_cost = estimated_hours * settings.OPERATOR_COST_PER_HOUR * num_operators

    # Fuel cost (estimated 20 liters/hour per machine)
    fuel_liters = estimated_hours * 20 * num_operators
    fuel_cost = fuel_liters * settings.FUEL_COST_PER_LITER

    # Surveying cost
    surveying_cost = field_area_hectares * settings.SURVEYING_COST_PER_HECTARE

    # Earthwork cost (simple calculation based on volume)
    earthwork_cost = equipment_cost + labor_cost + fuel_cost

    # Subtotal
    subtotal = earthwork_cost + surveying_cost

    # Contingency (10%)
    contingency = subtotal * 0.10

    # Total cost
    total_cost = subtotal + contingency

    # Per unit costs
    cost_per_m3 = total_cost / total_volume if total_volume > 0 else 0
    cost_per_hectare = total_cost / field_area_hectares if field_area_hectares > 0 else 0

    # Duration
    estimated_days = estimated_hours / 8  # 8-hour workday

    # Generate bilingual summaries
    summary_en = (
        f"Total estimated cost: {total_cost:,.0f} SAR for {total_volume:,.0f} m³ of earthwork "
        f"over {field_area_hectares:.2f} hectares. Estimated duration: {estimated_days:.1f} days."
    )
    summary_ar = (
        f"إجمالي التكلفة المقدرة: {total_cost:,.0f} ريال لـ {total_volume:,.0f} م³ من الحفريات "
        f"على مساحة {field_area_hectares:.2f} هكتار. المدة المقدرة: {estimated_days:.1f} يوم."
    )

    return CostEstimate(
        total_cost_sar=round(total_cost, 2),
        earthwork_cost_sar=round(earthwork_cost, 2),
        equipment_cost_sar=round(equipment_cost, 2),
        labor_cost_sar=round(labor_cost, 2),
        fuel_cost_sar=round(fuel_cost, 2),
        surveying_cost_sar=round(surveying_cost, 2),
        contingency_sar=round(contingency, 2),
        cost_per_m3_sar=round(cost_per_m3, 2),
        cost_per_hectare_sar=round(cost_per_hectare, 2),
        estimated_duration_hours=round(estimated_hours, 1),
        estimated_duration_days=round(estimated_days, 1),
        summary_en=summary_en,
        summary_ar=summary_ar,
    )


def _get_equipment_recommendations(
    cut_fill: CutFillVolume,
    haul_distance: float,
    method: LevelingMethod,
) -> list[EquipmentRecommendation]:
    """
    Generate equipment recommendations based on job requirements.

    إنشاء توصيات المعدات بناءً على متطلبات العمل
    """
    recommendations = []
    total_volume = cut_fill.cut_volume_m3 + cut_fill.fill_volume_m3
    priority = 1

    # Determine primary equipment based on volume and haul distance
    if total_volume < 500:
        # Small job - laser leveler for precision
        primary_equipment = [EquipmentType.LASER_LEVELER, EquipmentType.GRADER]
    elif haul_distance < 100:
        # Short haul - bulldozer
        primary_equipment = [EquipmentType.BULLDOZER, EquipmentType.GRADER]
    elif haul_distance < 300:
        # Medium haul - scraper
        primary_equipment = [EquipmentType.SCRAPER, EquipmentType.BULLDOZER, EquipmentType.GRADER]
    else:
        # Long haul - excavator + trucks
        primary_equipment = [
            EquipmentType.EXCAVATOR,
            EquipmentType.DUMP_TRUCK,
            EquipmentType.GRADER,
        ]

    # Add laser leveler for precision methods
    if method == LevelingMethod.SINGLE_PLANE and EquipmentType.LASER_LEVELER not in primary_equipment:
        primary_equipment.append(EquipmentType.LASER_LEVELER)

    for eq_type in primary_equipment:
        config = EQUIPMENT_CONFIG[eq_type]
        names = EQUIPMENT_NAMES[eq_type]

        productivity = config["productivity"]
        if productivity > 0:
            hours_required = total_volume / productivity
        else:
            # Supporting equipment (trucks) - estimate based on haul cycles
            hours_required = total_volume / 50  # Rough estimate

        quantity = 1
        if total_volume > 5000:
            quantity = 2
        if total_volume > 15000:
            quantity = 3

        total_cost = hours_required * config["cost_per_hour"] * quantity

        recommendations.append(
            EquipmentRecommendation(
                equipment_type=eq_type,
                equipment_name_en=names[0],
                equipment_name_ar=names[1],
                quantity=quantity,
                hours_required=round(hours_required, 1),
                cost_per_hour_sar=config["cost_per_hour"],
                total_cost_sar=round(total_cost, 2),
                productivity_m3_per_hour=productivity,
                recommended_for=config["recommended_for"],
                priority=priority,
            )
        )
        priority += 1

    return recommendations


@router.post(
    "/analyze",
    response_model=LevelingAnalysisResponse,
    response_model_by_alias=True,
    summary="Analyze field for leveling | تحليل الحقل للتسوية",
    description=(
        "Full leveling analysis. The response bundles **cut/fill volumes**, "
        "equipment recommendations and cost estimation in a single envelope; "
        "there is no separate `/cut-fill` endpoint.\n\n"
        "يحتوي هذا المسار على أحجام القطع/الردم ضمن استجابته."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Analysis failed"},
    },
)
async def analyze_field_leveling(
    request: LevelingAnalysisRequest,
    http_request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Analyze a field for leveling requirements and generate an optimal plan.

    تحليل الحقل لمتطلبات التسوية وإنشاء خطة مثالية

    This endpoint:
    - Computes the optimal design plane
    - Calculates cut/fill volumes (in the same response — no split endpoint)
    - Provides equipment recommendations
    - Estimates costs in SAR

    Tenant isolation is enforced via ``current_user.tenant_id`` (from the JWT
    ``tid`` claim). ``X-Tenant-Id`` header is ignored for authorization.
    """
    _validate_field_id(request.field_id)

    tenant_id = getattr(current_user, "tenant_id", None)
    logger.info(
        "leveling_analysis_requested",
        field_id=_safe_log(request.field_id),
        tenant_id=_safe_log(tenant_id),
        point_count=len(request.elevation_points),
        method=request.method.value,
    )

    try:
        # Convert elevation points
        points = _convert_points(request.elevation_points)

        # Initialize optimizer
        optimizer = LevelingOptimizer(
            soil_expansion_factor=settings.SOIL_EXPANSION_FACTOR,
            soil_compaction_factor=settings.SOIL_COMPACTION_FACTOR,
        )

        # Compute optimal plane based on priority
        if request.priority == LevelingPriority.IRRIGATION_EFFICIENCY:
            plane = optimizer.optimize_for_irrigation(
                points,
                min_grade=settings.MIN_DRAINAGE_GRADE,
                max_grade=settings.MAX_IRRIGATION_GRADE,
            )
        else:
            plane = optimizer.compute_optimal_plane(
                points,
                target_grade_x=request.target_grade_x,
                target_grade_y=request.target_grade_y,
                balance_cut_fill=(request.priority == LevelingPriority.MINIMIZE_EARTHWORK),
            )

        # Calculate volumes
        cut_fill_result = optimizer.calculate_cut_fill_volumes(points, plane)

        # Calculate field statistics
        stats = optimizer.calculate_statistics(points)
        field_area_m2 = optimizer.calculate_field_area(points)
        field_area_hectares = field_area_m2 / 10000

        # Calculate haul distance
        haul_distance = optimizer.calculate_haul_distance(
            cut_fill_result.cut_points,
            cut_fill_result.fill_points,
        )

        # Create design plane model
        design_plane = DesignPlane(
            centroid_elevation=plane.c + plane.a * (stats.get("min_elevation", 0) + stats.get("max_elevation", 0)) / 2,
            grade_x_percent=round(plane.a * 100, 3),
            grade_y_percent=round(plane.b * 100, 3),
            plane_equation=f"z = {plane.a:.6f}*x + {plane.b:.6f}*y + {plane.c:.3f}",
            coefficient_a=plane.a,
            coefficient_b=plane.b,
            coefficient_c=plane.c,
        )

        # Create cut/fill volume model
        net_volume = cut_fill_result.cut_volume - cut_fill_result.fill_volume
        balance_ratio = (
            cut_fill_result.cut_volume / cut_fill_result.fill_volume
            if cut_fill_result.fill_volume > 0
            else float("inf")
        )

        cut_fill = CutFillVolume(
            cut_volume_m3=round(cut_fill_result.cut_volume, 2),
            fill_volume_m3=round(cut_fill_result.fill_volume, 2),
            net_volume_m3=round(net_volume, 2),
            cut_area_m2=round(cut_fill_result.cut_area, 2),
            fill_area_m2=round(cut_fill_result.fill_area, 2),
            balance_ratio=round(balance_ratio, 3) if balance_ratio != float("inf") else 999.0,
            max_cut_depth_m=round(cut_fill_result.max_cut_depth, 3),
            max_fill_depth_m=round(cut_fill_result.max_fill_depth, 3),
            avg_cut_depth_m=round(cut_fill_result.avg_cut_depth, 3),
            avg_fill_depth_m=round(cut_fill_result.avg_fill_depth, 3),
        )

        # Get equipment recommendations
        equipment_recommendations = _get_equipment_recommendations(cut_fill, haul_distance, request.method)

        # Calculate cost estimate if requested
        cost_estimate = None
        if request.include_cost_estimate:
            cost_estimate = _calculate_cost_estimate(
                cut_fill, field_area_hectares, haul_distance, equipment_recommendations
            )

        # Generate bilingual summaries
        elevation_range = stats.get("elevation_range", 0)

        summary_en = (
            f"Field analysis complete for {field_area_hectares:.2f} hectares. "
            f"Elevation range: {elevation_range:.2f}m. "
            f"Cut volume: {cut_fill.cut_volume_m3:,.0f} m³, Fill volume: {cut_fill.fill_volume_m3:,.0f} m³. "
            f"Recommended grade: {design_plane.grade_x_percent:.2f}% (X), {design_plane.grade_y_percent:.2f}% (Y)."
        )

        summary_ar = (
            f"اكتمل تحليل الحقل لمساحة {field_area_hectares:.2f} هكتار. "
            f"نطاق الارتفاع: {elevation_range:.2f} م. "
            f"حجم القطع: {cut_fill.cut_volume_m3:,.0f} م³، حجم الردم: {cut_fill.fill_volume_m3:,.0f} م³. "
            f"الميل الموصى به: {design_plane.grade_x_percent:.2f}% (س)، {design_plane.grade_y_percent:.2f}% (ص)."
        )

        # Generate recommendations
        recommendations_en = []
        recommendations_ar = []

        if balance_ratio < 0.8 or balance_ratio > 1.2:
            recommendations_en.append("Consider adjusting design elevation to better balance cut and fill volumes.")
            recommendations_ar.append("فكر في تعديل ارتفاع التصميم لتحقيق توازن أفضل بين أحجام القطع والردم.")

        if design_plane.grade_x_percent < settings.MIN_DRAINAGE_GRADE:
            recommendations_en.append(
                f"Grade in X direction ({design_plane.grade_x_percent:.2f}%) is below minimum for drainage ({settings.MIN_DRAINAGE_GRADE}%)."
            )
            recommendations_ar.append(
                f"الميل بالاتجاه السيني ({design_plane.grade_x_percent:.2f}%) أقل من الحد الأدنى للتصريف ({settings.MIN_DRAINAGE_GRADE}%)."
            )

        if cut_fill.max_cut_depth_m > 0.5:
            recommendations_en.append(
                f"Maximum cut depth ({cut_fill.max_cut_depth_m:.2f}m) may require heavy equipment."
            )
            recommendations_ar.append(f"أقصى عمق قطع ({cut_fill.max_cut_depth_m:.2f} م) قد يتطلب معدات ثقيلة.")

        # Create leveling plan
        plan = LevelingPlan(
            plan_id=str(uuid.uuid4()),
            field_id=request.field_id,
            created_at=datetime.utcnow(),
            design_plane=design_plane,
            method=request.method,
            cut_fill=cut_fill,
            field_area_m2=round(field_area_m2, 2),
            field_area_hectares=round(field_area_hectares, 4),
            original_elevation_range=round(elevation_range, 3),
            leveled_elevation_range=round(
                max(design_plane.grade_x_percent, design_plane.grade_y_percent) / 100 * max(p.x for p in points)
                if points
                else 0,
                3,
            ),
            avg_haul_distance_m=round(haul_distance, 1),
            equipment_recommendations=equipment_recommendations,
            cost_estimate=cost_estimate,
            summary_en=summary_en,
            summary_ar=summary_ar,
            recommendations_en=recommendations_en,
            recommendations_ar=recommendations_ar,
        )

        logger.info(
            "leveling_analysis_completed",
            field_id=request.field_id,
            cut_volume=cut_fill.cut_volume_m3,
            fill_volume=cut_fill.fill_volume_m3,
        )

        # Publish NATS event for leveling analysis completed
        nc = getattr(http_request.app.state, "nc", None)
        nats_connected = getattr(http_request.app.state, "nats_connected", False)
        if nc and nats_connected:
            try:
                import json

                event_payload = json.dumps(
                    {
                        "event_type": "leveling_analyzed",
                        "field_id": request.field_id,
                        "method": request.method.value,
                        "cut_volume_m3": cut_fill.cut_volume_m3,
                        "fill_volume_m3": cut_fill.fill_volume_m3,
                        "field_area_hectares": round(field_area_hectares, 4),
                        "total_cost_sar": cost_estimate.total_cost_sar if cost_estimate else None,
                        "plan_id": plan.plan_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    default=str,
                ).encode()
                # get_tenant_subject enforces UUID shape; fall back to the
                # inline pattern when tenant_id is missing/non-UUID so the
                # publish still lands on a tenant-scoped subject.
                try:
                    subject = get_tenant_subject(tenant_id or "unknown", "terrain", "leveling_recommended")
                except ValueError:
                    subject = f"sahool.tenant.{tenant_id or 'unknown'}.terrain.leveling_recommended"
                await nc.publish(subject, event_payload)
                logger.info("nats_event_published", subject=subject, field_id=request.field_id)
            except Exception as pub_err:
                logger.warning("nats_publish_failed", error=str(pub_err))

        return LevelingAnalysisResponse(
            success=True,
            field_id=request.field_id,
            analysis_timestamp=datetime.utcnow(),
            plan=plan,
            message_en="Leveling analysis completed successfully.",
            message_ar="تم إكمال تحليل التسوية بنجاح.",
        )

    except Exception as e:
        logger.error("leveling_analysis_failed", field_id=request.field_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Analysis failed: {str(e)}",
                "error_ar": f"فشل التحليل: {str(e)}",
            },
        )


@router.get(
    "/plan/{field_id}",
    response_model=LevelingPlan,
    response_model_by_alias=True,
    summary="Get optimal leveling plan | الحصول على خطة التسوية المثلى",
)
async def get_leveling_plan(
    field_id: str = Path(..., description="Field identifier | معرف الحقل"),
    current_user: User = Depends(get_current_user),
):
    """
    Get the optimal leveling plan for a field.

    الحصول على خطة التسوية المثلى للحقل

    Note: In production, this would retrieve a stored plan from the database
    filtered by ``current_user.tenant_id``. For demonstration, it returns a
    sample plan.
    """
    _validate_field_id(field_id)
    tenant_id = getattr(current_user, "tenant_id", None)
    logger.info(
        "leveling_plan_requested",
        field_id=_safe_log(field_id),
        tenant_id=_safe_log(tenant_id),
    )

    # In production, fetch from database
    # For now, return a sample response

    design_plane = DesignPlane(
        centroid_elevation=100.5,
        grade_x_percent=0.2,
        grade_y_percent=0.1,
        plane_equation="z = 0.002*x + 0.001*y + 100.5",
        coefficient_a=0.002,
        coefficient_b=0.001,
        coefficient_c=100.5,
    )

    cut_fill = CutFillVolume(
        cut_volume_m3=2500.0,
        fill_volume_m3=2300.0,
        net_volume_m3=200.0,
        cut_area_m2=15000.0,
        fill_area_m2=12000.0,
        balance_ratio=1.09,
        max_cut_depth_m=0.35,
        max_fill_depth_m=0.28,
        avg_cut_depth_m=0.17,
        avg_fill_depth_m=0.19,
    )

    return LevelingPlan(
        plan_id=str(uuid.uuid4()),
        field_id=field_id,
        created_at=datetime.utcnow(),
        design_plane=design_plane,
        method=LevelingMethod.SINGLE_PLANE,
        cut_fill=cut_fill,
        field_area_m2=25000.0,
        field_area_hectares=2.5,
        original_elevation_range=0.85,
        leveled_elevation_range=0.05,
        avg_haul_distance_m=75.0,
        equipment_recommendations=[],
        cost_estimate=None,
        summary_en=f"Leveling plan for field {field_id}",
        summary_ar=f"خطة تسوية الحقل {field_id}",
        recommendations_en=["Proceed with single-plane leveling"],
        recommendations_ar=["المتابعة بتسوية المستوى الواحد"],
    )


@router.get(
    "/cost/{field_id}",
    response_model=CostEstimate,
    response_model_by_alias=True,
    summary="Get cost estimation | الحصول على تقدير التكلفة",
    description=(
        "Cost estimation for a leveling operation. Only ``cut_volume_m3`` is "
        "required; ``fill_volume_m3`` defaults to the cut volume (balanced "
        "earthwork) and ``field_area_hectares`` defaults to 1.0 hectare when "
        "omitted — matching the unified API contract.\n\n"
        "تقدير تكلفة عملية التسوية. المعلمة الوحيدة المطلوبة هي "
        "``cut_volume_m3``؛ القيم الأخرى تأخذ قيمًا افتراضية عند عدم "
        "تمريرها لتتوافق مع عقد الواجهة الموحدة."
    ),
)
async def get_cost_estimation(
    field_id: str = Path(..., description="Field identifier | معرف الحقل"),
    cut_volume_m3: float = Query(
        ...,
        ge=0,
        description="Cut volume (m³) | حجم القطع (م³)",
    ),
    fill_volume_m3: float | None = Query(
        default=None,
        ge=0,
        description=(
            "Fill volume (m³) — defaults to cut_volume_m3 for balanced earthwork "
            "| حجم الردم (م³) - افتراضيًا يساوي حجم القطع"
        ),
    ),
    field_area_hectares: float | None = Query(
        default=None,
        gt=0,
        description=(
            "Field area (hectares) — defaults to 1.0 ha when omitted | مساحة الحقل (هكتار) - افتراضيًا 1.0 هكتار"
        ),
    ),
    haul_distance_m: float = Query(
        default=100.0,
        ge=0,
        description="Average haul distance (m) | متوسط مسافة النقل (م)",
    ),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed cost estimation for leveling operation.

    الحصول على تقدير التكلفة المفصل لعملية التسوية
    """
    _validate_field_id(field_id)

    # Apply contract defaults so only cut_volume_m3 is strictly required.
    if fill_volume_m3 is None:
        fill_volume_m3 = cut_volume_m3
    if field_area_hectares is None:
        field_area_hectares = 1.0

    tenant_id = getattr(current_user, "tenant_id", None)
    logger.info(
        "cost_estimation_requested",
        field_id=_safe_log(field_id),
        tenant_id=_safe_log(tenant_id),
        cut_volume=cut_volume_m3,
        fill_volume=fill_volume_m3,
        field_area_ha=field_area_hectares,
    )

    # Create cut/fill model
    cut_fill = CutFillVolume(
        cut_volume_m3=cut_volume_m3,
        fill_volume_m3=fill_volume_m3,
        net_volume_m3=cut_volume_m3 - fill_volume_m3,
        cut_area_m2=0,
        fill_area_m2=0,
        balance_ratio=cut_volume_m3 / fill_volume_m3 if fill_volume_m3 > 0 else 999.0,
        max_cut_depth_m=0,
        max_fill_depth_m=0,
        avg_cut_depth_m=0,
        avg_fill_depth_m=0,
    )

    # Get equipment recommendations
    equipment_recommendations = _get_equipment_recommendations(cut_fill, haul_distance_m, LevelingMethod.SINGLE_PLANE)

    # Calculate cost estimate
    cost_estimate = _calculate_cost_estimate(cut_fill, field_area_hectares, haul_distance_m, equipment_recommendations)

    return cost_estimate


@router.get(
    "/equipment/{field_id}",
    response_model=list[EquipmentRecommendation],
    response_model_by_alias=True,
    summary="Get equipment recommendations | الحصول على توصيات المعدات",
)
async def get_equipment_recommendations(
    field_id: str = Path(..., description="Field identifier | معرف الحقل"),
    total_volume_m3: float = Query(..., ge=0, description="Total earthwork volume (m³) | إجمالي حجم الحفريات (م³)"),
    haul_distance_m: float = Query(
        default=100.0, ge=0, description="Average haul distance (m) | متوسط مسافة النقل (م)"
    ),
    method: LevelingMethod = Query(default=LevelingMethod.SINGLE_PLANE, description="Leveling method | طريقة التسوية"),
    current_user: User = Depends(get_current_user),
):
    """
    Get equipment recommendations for leveling operation.

    الحصول على توصيات المعدات لعملية التسوية
    """
    _validate_field_id(field_id)
    tenant_id = getattr(current_user, "tenant_id", None)
    logger.info(
        "equipment_recommendations_requested",
        field_id=_safe_log(field_id),
        tenant_id=_safe_log(tenant_id),
        total_volume=total_volume_m3,
        haul_distance=haul_distance_m,
    )

    # Create simplified cut/fill model (assume 50/50 split)
    cut_fill = CutFillVolume(
        cut_volume_m3=total_volume_m3 / 2,
        fill_volume_m3=total_volume_m3 / 2,
        net_volume_m3=0,
        cut_area_m2=0,
        fill_area_m2=0,
        balance_ratio=1.0,
        max_cut_depth_m=0,
        max_fill_depth_m=0,
        avg_cut_depth_m=0,
        avg_fill_depth_m=0,
    )

    return _get_equipment_recommendations(cut_fill, haul_distance_m, method)


@router.post(
    "/simulate",
    response_model=SimulationResult,
    response_model_by_alias=True,
    summary="Simulate leveling scenario | محاكاة سيناريو التسوية",
)
async def simulate_leveling(
    request: SimulationRequest,
    http_request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Simulate a leveling scenario and return predicted results.

    محاكاة سيناريو التسوية وإرجاع النتائج المتوقعة

    This endpoint allows testing different leveling parameters
    before committing to an actual leveling plan.

    Tenant is derived from ``current_user.tenant_id`` (JWT ``tid`` claim).
    """
    _validate_field_id(request.field_id)
    tenant_id = getattr(current_user, "tenant_id", None)
    logger.info(
        "leveling_simulation_requested",
        field_id=_safe_log(request.field_id),
        tenant_id=_safe_log(tenant_id),
        target_grade_x=request.target_grade_x,
        target_grade_y=request.target_grade_y,
    )

    try:
        # Convert points
        points = _convert_points(request.elevation_points)

        # Initialize optimizer
        optimizer = LevelingOptimizer(
            soil_expansion_factor=settings.SOIL_EXPANSION_FACTOR,
            soil_compaction_factor=settings.SOIL_COMPACTION_FACTOR,
        )

        # Calculate original statistics
        original_stats = optimizer.calculate_statistics(points)
        original_std_dev = original_stats.get("std_dev", 0)

        # Compute design plane with specified parameters
        plane = optimizer.compute_optimal_plane(
            points,
            target_grade_x=request.target_grade_x,
            target_grade_y=request.target_grade_y,
            balance_cut_fill=True,
        )

        # If target elevation specified, adjust plane
        if request.target_elevation is not None:
            # Recalculate c to achieve target elevation at centroid
            x_centroid = sum(p.x for p in points) / len(points)
            y_centroid = sum(p.y for p in points) / len(points)
            plane = PlaneParameters(
                a=plane.a,
                b=plane.b,
                c=request.target_elevation - plane.a * x_centroid - plane.b * y_centroid,
            )

        # Calculate volumes
        cut_fill_result = optimizer.calculate_cut_fill_volumes(points, plane)

        # Generate simulated points (post-leveling elevations)
        simulated_points = []
        for p in points:
            design_z = plane.a * p.x + plane.b * p.y + plane.c
            simulated_points.append(ElevationPoint(x=p.x, y=p.y, elevation=design_z, point_id=p.point_id))

        # Convert cut/fill points
        cut_points = [
            ElevationPoint(x=p.x, y=p.y, elevation=p.z, point_id=p.point_id) for p in cut_fill_result.cut_points
        ]
        fill_points = [
            ElevationPoint(x=p.x, y=p.y, elevation=p.z, point_id=p.point_id) for p in cut_fill_result.fill_points
        ]

        # Calculate simulated statistics
        simulated_elevations = [sp.elevation for sp in simulated_points]
        simulated_mean = sum(simulated_elevations) / len(simulated_elevations)
        simulated_std_dev = (
            sum((e - simulated_mean) ** 2 for e in simulated_elevations) / len(simulated_elevations)
        ) ** 0.5

        # Calculate uniformity improvement
        uniformity_improvement = (
            (original_std_dev - simulated_std_dev) / original_std_dev * 100 if original_std_dev > 0 else 0
        )

        # Create design plane model
        design_plane = DesignPlane(
            centroid_elevation=round(plane.c, 3),
            grade_x_percent=round(plane.a * 100, 3),
            grade_y_percent=round(plane.b * 100, 3),
            plane_equation=f"z = {plane.a:.6f}*x + {plane.b:.6f}*y + {plane.c:.3f}",
            coefficient_a=plane.a,
            coefficient_b=plane.b,
            coefficient_c=plane.c,
        )

        # Create cut/fill volume model
        net_volume = cut_fill_result.cut_volume - cut_fill_result.fill_volume
        balance_ratio = (
            cut_fill_result.cut_volume / cut_fill_result.fill_volume if cut_fill_result.fill_volume > 0 else 999.0
        )

        cut_fill = CutFillVolume(
            cut_volume_m3=round(cut_fill_result.cut_volume, 2),
            fill_volume_m3=round(cut_fill_result.fill_volume, 2),
            net_volume_m3=round(net_volume, 2),
            cut_area_m2=round(cut_fill_result.cut_area, 2),
            fill_area_m2=round(cut_fill_result.fill_area, 2),
            balance_ratio=round(balance_ratio, 3) if balance_ratio != float("inf") else 999.0,
            max_cut_depth_m=round(cut_fill_result.max_cut_depth, 3),
            max_fill_depth_m=round(cut_fill_result.max_fill_depth, 3),
            avg_cut_depth_m=round(cut_fill_result.avg_cut_depth, 3),
            avg_fill_depth_m=round(cut_fill_result.avg_fill_depth, 3),
        )

        # Generate bilingual summaries
        summary_en = (
            f"Simulation complete. With grades of {design_plane.grade_x_percent:.2f}% (X) and "
            f"{design_plane.grade_y_percent:.2f}% (Y), the field would require "
            f"{cut_fill.cut_volume_m3:,.0f} m³ cut and {cut_fill.fill_volume_m3:,.0f} m³ fill. "
            f"Uniformity improvement: {uniformity_improvement:.1f}%."
        )
        summary_ar = (
            f"اكتملت المحاكاة. بميول {design_plane.grade_x_percent:.2f}% (س) و"
            f"{design_plane.grade_y_percent:.2f}% (ص)، سيحتاج الحقل إلى "
            f"{cut_fill.cut_volume_m3:,.0f} م³ قطع و{cut_fill.fill_volume_m3:,.0f} م³ ردم. "
            f"تحسن التجانس: {uniformity_improvement:.1f}%."
        )

        logger.info(
            "leveling_simulation_completed",
            field_id=request.field_id,
            cut_volume=cut_fill.cut_volume_m3,
            fill_volume=cut_fill.fill_volume_m3,
            uniformity_improvement=uniformity_improvement,
        )

        # Publish NATS event for simulation completed
        nc = getattr(http_request.app.state, "nc", None)
        nats_connected = getattr(http_request.app.state, "nats_connected", False)
        if nc and nats_connected:
            try:
                import json

                event_payload = json.dumps(
                    {
                        "event_type": "leveling_simulated",
                        "field_id": request.field_id,
                        "cut_volume_m3": cut_fill.cut_volume_m3,
                        "fill_volume_m3": cut_fill.fill_volume_m3,
                        "uniformity_improvement": round(uniformity_improvement, 2),
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    default=str,
                ).encode()
                await nc.publish(SAHOOL_TERRAIN_SIMULATION_COMPLETED, event_payload)
                logger.info(
                    "nats_event_published", subject=SAHOOL_TERRAIN_SIMULATION_COMPLETED, field_id=request.field_id
                )
            except Exception as pub_err:
                logger.warning("nats_publish_failed", error=str(pub_err))

        return SimulationResult(
            field_id=request.field_id,
            simulation_timestamp=datetime.utcnow(),
            original_points=request.elevation_points,
            simulated_points=simulated_points,
            cut_points=cut_points,
            fill_points=fill_points,
            design_plane=design_plane,
            cut_fill=cut_fill,
            original_std_dev=round(original_std_dev, 4),
            simulated_std_dev=round(simulated_std_dev, 4),
            uniformity_improvement=round(uniformity_improvement, 2),
            summary_en=summary_en,
            summary_ar=summary_ar,
        )

    except Exception as e:
        logger.error("leveling_simulation_failed", field_id=request.field_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Simulation failed: {str(e)}",
                "error_ar": f"فشلت المحاكاة: {str(e)}",
            },
        )
