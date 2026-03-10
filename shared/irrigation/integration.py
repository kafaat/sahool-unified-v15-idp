"""
Human-Machine Collaborative (HMC) Irrigation Decision Framework - Integration
=============================================================================
تكامل إطار قرار الري التعاوني بين الإنسان والآلة

This module provides integration between the HMC Irrigation Framework and
existing SAHOOL platform agents and services:

1. Farm Advisor Agent Integration
2. Irrigation Sub-Agent Integration
3. Weather Service Sync
4. Fertilization System Sync
5. Event Publishing

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import UUID

import structlog

from .collaborative_engine import HMCIrrigationEngine
from .models import (
    DecisionSession,
    ExperienceRule,
    ExperienceSource,
    IrrigationProgram,
    SessionOutcome,
)

logger = structlog.get_logger(__name__)


# =============================================================================
# Protocol Definitions - تعريفات البروتوكول
# =============================================================================


class FarmAdvisorAgent(Protocol):
    """
    Protocol for Farm Advisor Agent integration.
    بروتوكول تكامل وكيل المستشار الزراعي

    This defines the expected interface for the FarmAdvisorAgent
    that the HMC framework can integrate with.
    """

    async def get_recommendations(
        self,
        farm_id: str,
        field_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Get recommendations from the advisor."""
        ...

    async def submit_feedback(
        self,
        recommendation_id: str,
        feedback: dict[str, Any],
    ) -> bool:
        """Submit feedback on a recommendation."""
        ...

    async def get_field_conditions(
        self,
        field_id: str,
    ) -> dict[str, Any]:
        """Get current field conditions."""
        ...


class IrrigationSubAgent(Protocol):
    """
    Protocol for Irrigation Sub-Agent integration.
    بروتوكول تكامل الوكيل الفرعي للري

    This defines the expected interface for the Irrigation Sub-Agent
    that handles irrigation-specific operations.
    """

    async def calculate_water_requirement(
        self,
        field_id: str,
        crop_type: str,
        growth_stage: str,
        weather_forecast: dict[str, Any],
    ) -> dict[str, Any]:
        """Calculate water requirements."""
        ...

    async def generate_schedule(
        self,
        field_id: str,
        water_requirement: dict[str, Any],
        constraints: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate irrigation schedule."""
        ...

    async def execute_schedule(
        self,
        schedule_id: str,
    ) -> bool:
        """Execute an approved schedule."""
        ...


class WeatherService(Protocol):
    """
    Protocol for Weather Service integration.
    بروتوكول تكامل خدمة الطقس
    """

    async def get_forecast(
        self,
        location: dict[str, float],
        days: int = 7,
    ) -> dict[str, Any]:
        """Get weather forecast."""
        ...

    async def get_current_conditions(
        self,
        location: dict[str, float],
    ) -> dict[str, Any]:
        """Get current weather conditions."""
        ...

    async def subscribe_alerts(
        self,
        location: dict[str, float],
        callback_url: str,
    ) -> str:
        """Subscribe to weather alerts."""
        ...


class FertilizationService(Protocol):
    """
    Protocol for Fertilization Service integration.
    بروتوكول تكامل خدمة التسميد
    """

    async def get_fertigation_schedule(
        self,
        field_id: str,
        crop_type: str,
        growth_stage: str,
    ) -> dict[str, Any]:
        """Get fertigation schedule."""
        ...

    async def sync_irrigation_schedule(
        self,
        irrigation_schedule: dict[str, Any],
        field_id: str,
    ) -> bool:
        """Sync irrigation schedule with fertigation."""
        ...


# =============================================================================
# Integration Manager - مدير التكامل
# =============================================================================


class HMCIntegrationManager:
    """
    Manager for HMC framework integrations with SAHOOL agents and services.
    مدير تكاملات إطار HMC مع وكلاء وخدمات SAHOOL

    This class coordinates the integration between the HMC Irrigation
    Framework and various SAHOOL platform components:

    - Farm Advisor Agent: Provides field recommendations
    - Irrigation Sub-Agent: Handles irrigation calculations
    - Weather Service: Weather forecasts and alerts
    - Fertilization Service: Fertigation coordination

    Example:
        manager = HMCIntegrationManager()

        # Register agents
        manager.register_farm_advisor(farm_advisor_agent)
        manager.register_irrigation_agent(irrigation_agent)

        # Sync with services
        await manager.sync_with_weather_service()
        await manager.sync_with_fertilization_system()

        # Create integrated engine
        engine = manager.create_integrated_engine(
            farm_id="FARM-001",
            farmer_id="farmer-123"
        )
    """

    def __init__(self):
        """
        Initialize the integration manager.
        تهيئة مدير التكامل
        """
        self._farm_advisor: FarmAdvisorAgent | None = None
        self._irrigation_agent: IrrigationSubAgent | None = None
        self._weather_service: WeatherService | None = None
        self._fertilization_service: FertilizationService | None = None

        # Event callbacks
        self._event_publishers: list[callable] = []

        # Integration status
        self._integrations_status: dict[str, dict[str, Any]] = {
            "farm_advisor": {"registered": False, "last_sync": None},
            "irrigation_agent": {"registered": False, "last_sync": None},
            "weather_service": {"registered": False, "last_sync": None},
            "fertilization_service": {"registered": False, "last_sync": None},
        }

        logger.info("hmc_integration_manager_initialized")

    # =========================================================================
    # Agent Registration - تسجيل الوكلاء
    # =========================================================================

    def register_farm_advisor(self, advisor: FarmAdvisorAgent) -> None:
        """
        Register a Farm Advisor Agent.
        تسجيل وكيل المستشار الزراعي

        Args:
            advisor: Farm Advisor Agent instance | مثيل وكيل المستشار الزراعي

        Example:
            manager.register_farm_advisor(farm_advisor_agent)
        """
        self._farm_advisor = advisor
        self._integrations_status["farm_advisor"]["registered"] = True
        self._integrations_status["farm_advisor"]["registered_at"] = datetime.now(UTC).isoformat()

        logger.info("farm_advisor_registered")

    def register_irrigation_agent(self, agent: IrrigationSubAgent) -> None:
        """
        Register an Irrigation Sub-Agent.
        تسجيل الوكيل الفرعي للري

        Args:
            agent: Irrigation Sub-Agent instance | مثيل الوكيل الفرعي للري

        Example:
            manager.register_irrigation_agent(irrigation_agent)
        """
        self._irrigation_agent = agent
        self._integrations_status["irrigation_agent"]["registered"] = True
        self._integrations_status["irrigation_agent"]["registered_at"] = datetime.now(UTC).isoformat()

        logger.info("irrigation_agent_registered")

    def register_weather_service(self, service: WeatherService) -> None:
        """
        Register a Weather Service.
        تسجيل خدمة الطقس

        Args:
            service: Weather Service instance | مثيل خدمة الطقس

        Example:
            manager.register_weather_service(weather_service)
        """
        self._weather_service = service
        self._integrations_status["weather_service"]["registered"] = True
        self._integrations_status["weather_service"]["registered_at"] = datetime.now(UTC).isoformat()

        logger.info("weather_service_registered")

    def register_fertilization_service(self, service: FertilizationService) -> None:
        """
        Register a Fertilization Service.
        تسجيل خدمة التسميد

        Args:
            service: Fertilization Service instance | مثيل خدمة التسميد

        Example:
            manager.register_fertilization_service(fertilization_service)
        """
        self._fertilization_service = service
        self._integrations_status["fertilization_service"]["registered"] = True
        self._integrations_status["fertilization_service"]["registered_at"] = datetime.now(UTC).isoformat()

        logger.info("fertilization_service_registered")

    # =========================================================================
    # Service Sync - مزامنة الخدمات
    # =========================================================================

    async def sync_with_weather_service(
        self,
        location: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        """
        Sync with weather service for current conditions and forecasts.
        المزامنة مع خدمة الطقس للظروف الحالية والتوقعات

        Args:
            location: Location coordinates (lat, lon) | إحداثيات الموقع

        Returns:
            Weather data dictionary | قاموس بيانات الطقس

        Example:
            weather = await manager.sync_with_weather_service(
                location={"lat": 24.7136, "lon": 46.6753}
            )
        """
        if not self._weather_service:
            logger.warning("weather_service_not_registered")
            return {"error": "Weather service not registered"}

        result = {
            "synced_at": datetime.now(UTC).isoformat(),
            "current_conditions": None,
            "forecast": None,
        }

        try:
            if location:
                result["current_conditions"] = await self._weather_service.get_current_conditions(location)
                result["forecast"] = await self._weather_service.get_forecast(location, days=7)

            self._integrations_status["weather_service"]["last_sync"] = datetime.now(UTC).isoformat()

            logger.info("weather_service_synced", location=location)

        except Exception as e:
            logger.error("weather_sync_failed", error=str(e))
            result["error"] = str(e)

        return result

    async def sync_with_fertilization_system(
        self,
        field_id: str | None = None,
        crop_type: str | None = None,
        growth_stage: str | None = None,
    ) -> dict[str, Any]:
        """
        Sync with fertilization system for fertigation coordination.
        المزامنة مع نظام التسميد لتنسيق التسميد بالري

        Args:
            field_id: Field identifier | معرف الحقل
            crop_type: Crop type | نوع المحصول
            growth_stage: Growth stage | مرحلة النمو

        Returns:
            Fertigation data dictionary | قاموس بيانات التسميد بالري

        Example:
            fertigation = await manager.sync_with_fertilization_system(
                field_id="FIELD-001",
                crop_type="wheat",
                growth_stage="tillering"
            )
        """
        if not self._fertilization_service:
            logger.warning("fertilization_service_not_registered")
            return {"error": "Fertilization service not registered"}

        result = {
            "synced_at": datetime.now(UTC).isoformat(),
            "fertigation_schedule": None,
        }

        try:
            if field_id and crop_type and growth_stage:
                result["fertigation_schedule"] = await self._fertilization_service.get_fertigation_schedule(
                    field_id, crop_type, growth_stage
                )

            self._integrations_status["fertilization_service"]["last_sync"] = datetime.now(UTC).isoformat()

            logger.info(
                "fertilization_service_synced",
                field_id=field_id,
                crop_type=crop_type,
            )

        except Exception as e:
            logger.error("fertilization_sync_failed", error=str(e))
            result["error"] = str(e)

        return result

    # =========================================================================
    # Agent Integration Methods - طرق تكامل الوكلاء
    # =========================================================================

    async def integrate_with_farm_advisor(
        self,
        engine: HMCIrrigationEngine,
        field_id: str,
    ) -> list[dict[str, Any]]:
        """
        Integrate HMC engine with Farm Advisor Agent.
        تكامل محرك HMC مع وكيل المستشار الزراعي

        Fetches recommendations from the Farm Advisor and converts
        relevant ones into experience rules for the HMC engine.

        Args:
            engine: HMC Irrigation Engine | محرك الري HMC
            field_id: Field identifier | معرف الحقل

        Returns:
            List of recommendations processed | قائمة التوصيات المعالجة

        Example:
            recommendations = await manager.integrate_with_farm_advisor(
                engine, field_id="FIELD-001"
            )
        """
        if not self._farm_advisor:
            logger.warning("farm_advisor_not_registered")
            return []

        try:
            # Get recommendations from advisor
            recommendations = await self._farm_advisor.get_recommendations(
                farm_id=str(engine.farm_id),
                field_id=field_id,
            )

            # Convert irrigation-related recommendations to experience rules
            experience_rules: list[ExperienceRule] = []

            for rec in recommendations:
                if rec.get("type") == "irrigation":
                    rule = ExperienceRule(
                        condition=rec.get("condition", "advisor_recommendation"),
                        action=rec.get("action", rec.get("description", "")),
                        source=ExperienceSource.AI_LEARNED,
                        rationale=rec.get("rationale", ""),
                        confidence=rec.get("confidence", 0.7),
                        metadata={
                            "advisor_recommendation_id": rec.get("id"),
                            "integrated_at": datetime.now(UTC).isoformat(),
                        },
                    )
                    experience_rules.append(rule)

            # Inject rules into engine
            if experience_rules and engine.current_session:
                engine.human_injects_experience(experience_rules, validate=False)

            logger.info(
                "farm_advisor_integrated",
                field_id=field_id,
                recommendations_count=len(recommendations),
                rules_injected=len(experience_rules),
            )

            return recommendations

        except Exception as e:
            logger.error("farm_advisor_integration_failed", error=str(e))
            return []

    async def integrate_with_irrigation_agent(
        self,
        engine: HMCIrrigationEngine,
        field_id: str,
        context: dict[str, Any],
    ) -> IrrigationProgram | None:
        """
        Integrate HMC engine with Irrigation Sub-Agent.
        تكامل محرك HMC مع الوكيل الفرعي للري

        Uses the Irrigation Sub-Agent to calculate water requirements
        and generate initial schedules for the HMC engine.

        Args:
            engine: HMC Irrigation Engine | محرك الري HMC
            field_id: Field identifier | معرف الحقل
            context: Context with crop and weather info | السياق

        Returns:
            Generated IrrigationProgram or None | برنامج الري المُنشأ أو لا شيء

        Example:
            program = await manager.integrate_with_irrigation_agent(
                engine,
                field_id="FIELD-001",
                context={"crop_type": "wheat", "growth_stage": "tillering"}
            )
        """
        if not self._irrigation_agent:
            logger.warning("irrigation_agent_not_registered")
            return None

        try:
            # Get weather forecast
            weather_forecast = {}
            if self._weather_service and context.get("location"):
                weather_forecast = await self._weather_service.get_forecast(context["location"], days=7)

            # Calculate water requirement
            water_req = await self._irrigation_agent.calculate_water_requirement(
                field_id=field_id,
                crop_type=context.get("crop_type", ""),
                growth_stage=context.get("growth_stage", ""),
                weather_forecast=weather_forecast,
            )

            # Generate schedule
            constraints = {}
            if engine.current_session:
                constraints = {
                    "ecological_constraints": [c.model_dump() for c in engine.current_session.constraints],
                    "goals": [g.model_dump() for g in engine.current_session.goals],
                }

            schedule_data = await self._irrigation_agent.generate_schedule(
                field_id=field_id,
                water_requirement=water_req,
                constraints=constraints,
            )

            # Generate program through HMC engine
            program = await engine.ai_generates_program(
                context={
                    **context,
                    "water_requirement": water_req,
                    "agent_schedule": schedule_data,
                }
            )

            logger.info(
                "irrigation_agent_integrated",
                field_id=field_id,
                water_requirement=water_req,
            )

            return program

        except Exception as e:
            logger.error("irrigation_agent_integration_failed", error=str(e))
            return None

    # =========================================================================
    # Event Publishing - نشر الأحداث
    # =========================================================================

    def register_event_publisher(
        self,
        publisher: callable,
    ) -> None:
        """
        Register an event publisher for HMC events.
        تسجيل ناشر أحداث لأحداث HMC

        Args:
            publisher: Callable that publishes events | كائن قابل للاستدعاء ينشر الأحداث

        Example:
            from shared.events.subjects import SAHOOL_IRRIGATION_HMC

            async def publish_to_nats(event: dict):
                await nats_client.publish(SAHOOL_IRRIGATION_HMC, json.dumps(event))

            manager.register_event_publisher(publish_to_nats)
        """
        self._event_publishers.append(publisher)
        logger.info("event_publisher_registered")

    async def publish_event(
        self,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        """
        Publish an HMC event to all registered publishers.
        نشر حدث HMC لجميع الناشرين المسجلين

        Args:
            event_type: Type of event | نوع الحدث
            data: Event data | بيانات الحدث
        """
        event = {
            "event_type": event_type,
            "timestamp": datetime.now(UTC).isoformat(),
            "data": data,
        }

        for publisher in self._event_publishers:
            try:
                await publisher(event)
            except Exception as e:
                logger.error(
                    "event_publish_failed",
                    event_type=event_type,
                    error=str(e),
                )

    async def publish_session_event(
        self,
        session: DecisionSession,
        event_type: str,
    ) -> None:
        """
        Publish a session-related event.
        نشر حدث متعلق بالجلسة

        Args:
            session: Decision session | جلسة القرار
            event_type: Event type (started, approved, completed) | نوع الحدث
        """
        await self.publish_event(
            f"hmc.session.{event_type}",
            {
                "session_id": str(session.id),
                "farm_id": str(session.farm_id),
                "field_id": str(session.field_id) if session.field_id else None,
                "farmer_id": session.farmer_id,
                "status": session.status.value,
            },
        )

    async def publish_program_event(
        self,
        program: IrrigationProgram,
        event_type: str,
    ) -> None:
        """
        Publish a program-related event.
        نشر حدث متعلق بالبرنامج

        Args:
            program: Irrigation program | برنامج الري
            event_type: Event type (generated, approved, executed) | نوع الحدث
        """
        await self.publish_event(
            f"hmc.program.{event_type}",
            {
                "program_id": str(program.id),
                "name": program.name,
                "schedule_count": len(program.schedules),
                "expected_water_m3": program.expected_water_usage_m3,
                "is_approved": program.is_approved,
                "confidence": program.confidence_score,
            },
        )

    # =========================================================================
    # Factory Method - طريقة المصنع
    # =========================================================================

    def create_integrated_engine(
        self,
        farm_id: str | UUID,
        farmer_id: str,
        field_id: str | UUID | None = None,
        **kwargs,
    ) -> HMCIrrigationEngine:
        """
        Create an HMC engine with integrations pre-configured.
        إنشاء محرك HMC مع تكوينات التكامل المسبقة

        Creates an HMCIrrigationEngine with callbacks registered to
        publish events and sync with integrated services.

        Args:
            farm_id: Farm identifier | معرف المزرعة
            farmer_id: Farmer identifier | معرف المزارع
            field_id: Field identifier | معرف الحقل
            **kwargs: Additional engine configuration

        Returns:
            Configured HMCIrrigationEngine | محرك HMC مُهيأ

        Example:
            engine = manager.create_integrated_engine(
                farm_id="FARM-001",
                farmer_id="farmer-123",
                field_id="FIELD-001"
            )
        """
        engine = HMCIrrigationEngine(
            farm_id=farm_id,
            farmer_id=farmer_id,
            field_id=field_id,
            **kwargs,
        )

        # Register callbacks for event publishing
        engine.on_session_start(lambda session: self._sync_publish_session_event(session, "started"))
        engine.on_program_generated(lambda program: self._sync_publish_program_event(program, "generated"))
        engine.on_approval(lambda session: self._sync_publish_session_event(session, "approved"))
        engine.on_completion(lambda outcome: self._sync_publish_outcome_event(outcome))

        logger.info(
            "integrated_engine_created",
            farm_id=str(farm_id),
            farmer_id=farmer_id,
        )

        return engine

    def _sync_publish_session_event(self, session: DecisionSession, event_type: str) -> None:
        """Synchronous wrapper for async session event publishing."""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.publish_session_event(session, event_type))
            else:
                loop.run_until_complete(self.publish_session_event(session, event_type))
        except RuntimeError:
            # No event loop, create new one
            asyncio.run(self.publish_session_event(session, event_type))

    def _sync_publish_program_event(self, program: IrrigationProgram, event_type: str) -> None:
        """Synchronous wrapper for async program event publishing."""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.publish_program_event(program, event_type))
            else:
                loop.run_until_complete(self.publish_program_event(program, event_type))
        except RuntimeError:
            asyncio.run(self.publish_program_event(program, event_type))

    def _sync_publish_outcome_event(self, outcome: SessionOutcome) -> None:
        """Synchronous wrapper for async outcome event publishing."""
        import asyncio

        async def publish():
            await self.publish_event(
                "hmc.session.completed",
                {
                    "session_id": str(outcome.session_id),
                    "program_id": str(outcome.program_id),
                    "success": outcome.overall_success,
                    "water_saving": outcome.water_saving_achieved,
                    "satisfaction": outcome.farmer_satisfaction,
                },
            )

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(publish())
            else:
                loop.run_until_complete(publish())
        except RuntimeError:
            asyncio.run(publish())

    # =========================================================================
    # Status - الحالة
    # =========================================================================

    def get_integration_status(self) -> dict[str, Any]:
        """
        Get status of all integrations.
        الحصول على حالة جميع التكاملات

        Returns:
            Dictionary with integration status | قاموس بحالة التكامل
        """
        return {
            "integrations": self._integrations_status,
            "event_publishers_count": len(self._event_publishers),
        }


# =============================================================================
# Integration Helper Functions - دوال مساعدة للتكامل
# =============================================================================


async def integrate_with_farm_advisor(
    advisor: FarmAdvisorAgent,
    engine: HMCIrrigationEngine,
    field_id: str,
) -> list[dict[str, Any]]:
    """
    Quick integration with Farm Advisor Agent.
    تكامل سريع مع وكيل المستشار الزراعي

    Args:
        advisor: Farm Advisor Agent | وكيل المستشار الزراعي
        engine: HMC Irrigation Engine | محرك الري HMC
        field_id: Field identifier | معرف الحقل

    Returns:
        List of recommendations | قائمة التوصيات
    """
    manager = HMCIntegrationManager()
    manager.register_farm_advisor(advisor)
    return await manager.integrate_with_farm_advisor(engine, field_id)


async def integrate_with_irrigation_agent(
    agent: IrrigationSubAgent,
    engine: HMCIrrigationEngine,
    field_id: str,
    context: dict[str, Any],
) -> IrrigationProgram | None:
    """
    Quick integration with Irrigation Sub-Agent.
    تكامل سريع مع الوكيل الفرعي للري

    Args:
        agent: Irrigation Sub-Agent | الوكيل الفرعي للري
        engine: HMC Irrigation Engine | محرك الري HMC
        field_id: Field identifier | معرف الحقل
        context: Context dictionary | قاموس السياق

    Returns:
        Generated program or None | البرنامج المُنشأ أو لا شيء
    """
    manager = HMCIntegrationManager()
    manager.register_irrigation_agent(agent)
    return await manager.integrate_with_irrigation_agent(engine, field_id, context)


async def sync_with_weather_service(
    service: WeatherService,
    location: dict[str, float],
) -> dict[str, Any]:
    """
    Quick sync with Weather Service.
    مزامنة سريعة مع خدمة الطقس

    Args:
        service: Weather Service | خدمة الطقس
        location: Location coordinates | إحداثيات الموقع

    Returns:
        Weather data | بيانات الطقس
    """
    manager = HMCIntegrationManager()
    manager.register_weather_service(service)
    return await manager.sync_with_weather_service(location)


async def sync_with_fertilization_system(
    service: FertilizationService,
    field_id: str,
    crop_type: str,
    growth_stage: str,
) -> dict[str, Any]:
    """
    Quick sync with Fertilization System.
    مزامنة سريعة مع نظام التسميد

    Args:
        service: Fertilization Service | خدمة التسميد
        field_id: Field identifier | معرف الحقل
        crop_type: Crop type | نوع المحصول
        growth_stage: Growth stage | مرحلة النمو

    Returns:
        Fertigation data | بيانات التسميد بالري
    """
    manager = HMCIntegrationManager()
    manager.register_fertilization_service(service)
    return await manager.sync_with_fertilization_system(field_id, crop_type, growth_stage)


# =============================================================================
# Singleton Instance - مثيل واحد
# =============================================================================

# Global integration manager instance
_integration_manager: HMCIntegrationManager | None = None


def get_integration_manager() -> HMCIntegrationManager:
    """
    Get the global HMC Integration Manager instance.
    الحصول على مثيل مدير تكامل HMC العام

    Returns:
        HMCIntegrationManager instance | مثيل HMCIntegrationManager
    """
    global _integration_manager
    if _integration_manager is None:
        _integration_manager = HMCIntegrationManager()
    return _integration_manager


def reset_integration_manager() -> None:
    """
    Reset the global integration manager.
    إعادة تعيين مدير التكامل العام
    """
    global _integration_manager
    _integration_manager = None
