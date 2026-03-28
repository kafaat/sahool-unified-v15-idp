"""
Tests for Task Automation Hook - advisory-service
"""

import asyncio
import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.hooks.task_automation import (
    ACTION_TASK_MAPPING,
    FieldOpsClient,
    TaskAutomationHook,
)


class TestActionTaskMapping:
    """Tests for ACTION_TASK_MAPPING constant"""

    def test_all_mappings_have_required_fields(self):
        for action_id, mapping in ACTION_TASK_MAPPING.items():
            assert "task_type" in mapping, f"{action_id} missing task_type"
            assert "title_ar" in mapping, f"{action_id} missing title_ar"
            assert "title_en" in mapping, f"{action_id} missing title_en"
            assert "priority" in mapping, f"{action_id} missing priority"

    def test_spray_actions_are_spray_type(self):
        spray_actions = [k for k in ACTION_TASK_MAPPING if k.startswith("spray_")]
        for action_id in spray_actions:
            assert ACTION_TASK_MAPPING[action_id]["task_type"] == "spray"

    def test_known_actions_present(self):
        expected = [
            "spray_copper",
            "spray_mancozeb",
            "spray_sulfur",
            "spray_neem_oil",
            "remove_infected_parts",
            "improve_air_circulation",
            "avoid_overhead_irrigation",
            "use_yellow_sticky_traps",
        ]
        for action in expected:
            assert action in ACTION_TASK_MAPPING


class TestFieldOpsClient:
    """Tests for FieldOpsClient"""

    def test_create_task(self):
        client = FieldOpsClient(base_url="http://test:8080")
        mock_http = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "task_1", "status": "created"}
        mock_response.raise_for_status = MagicMock()
        mock_http.post.return_value = mock_response
        client._client = mock_http

        result = asyncio.run(
            client.create_task(
                tenant_id="t1",
                field_id="f1",
                title="Test Task",
                description="Description",
                task_type="spray",
                priority="high",
                due_date=datetime.now(UTC),
            )
        )
        assert result["id"] == "task_1"
        mock_http.post.assert_called_once()

    def test_close(self):
        client = FieldOpsClient()
        mock_http = AsyncMock()
        client._client = mock_http
        asyncio.run(client.close())
        mock_http.aclose.assert_called_once()
        assert client._client is None


class TestTaskAutomationHook:
    """Tests for TaskAutomationHook"""

    def test_handle_recommendation(self):
        hook = TaskAutomationHook()
        hook.fieldops = AsyncMock(spec=FieldOpsClient)
        hook.fieldops.create_task = AsyncMock(return_value={"id": "task_1"})

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "tenant_id": "t1",
                "correlation_id": "c1",
                "payload": {
                    "field_id": "f1",
                    "actions": ["spray_copper", "remove_infected_parts"],
                    "severity": "high",
                    "title_ar": "اشتباه مرض",
                    "confidence": 0.85,
                    "category": "disease",
                    "details": {"urgency_hours": 24},
                },
            }
        ).encode()

        asyncio.run(hook._handle_recommendation(msg))
        assert hook.fieldops.create_task.call_count == 2

    def test_handle_recommendation_unknown_action(self):
        hook = TaskAutomationHook()
        hook.fieldops = AsyncMock(spec=FieldOpsClient)
        hook.fieldops.create_task = AsyncMock()

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "tenant_id": "t1",
                "payload": {
                    "field_id": "f1",
                    "actions": ["unknown_action"],
                    "severity": "medium",
                },
            }
        ).encode()

        asyncio.run(hook._handle_recommendation(msg))
        hook.fieldops.create_task.assert_not_called()

    def test_handle_recommendation_max_3_tasks(self):
        hook = TaskAutomationHook()
        hook.fieldops = AsyncMock(spec=FieldOpsClient)
        hook.fieldops.create_task = AsyncMock(return_value={"id": "task_1"})

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "tenant_id": "t1",
                "payload": {
                    "field_id": "f1",
                    "actions": [
                        "spray_copper",
                        "spray_mancozeb",
                        "remove_infected_parts",
                        "avoid_overhead_irrigation",
                        "improve_air_circulation",
                    ],
                    "severity": "medium",
                },
            }
        ).encode()

        asyncio.run(hook._handle_recommendation(msg))
        # Max 3 tasks from actions[:3]
        assert hook.fieldops.create_task.call_count <= 3

    def test_handle_fertilizer_plan(self):
        hook = TaskAutomationHook()
        hook.fieldops = AsyncMock(spec=FieldOpsClient)
        hook.fieldops.create_task = AsyncMock(return_value={"id": "task_1"})

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "tenant_id": "t1",
                "payload": {
                    "field_id": "f1",
                    "crop": "tomato",
                    "stage": "vegetative",
                    "plan": [
                        {
                            "product": "Urea",
                            "product_ar": "يوريا",
                            "dose_kg_per_ha": 50,
                            "total_kg": 50,
                            "method": "broadcast",
                            "timing_days": 0,
                        },
                        {
                            "product": "DAP",
                            "product_ar": "داب",
                            "dose_kg_per_ha": 30,
                            "total_kg": 30,
                            "method": "banding",
                            "timing_days": 3,
                        },
                    ],
                },
            }
        ).encode()

        asyncio.run(hook._handle_fertilizer_plan(msg))
        assert hook.fieldops.create_task.call_count == 2

    def test_handle_nutrient_assessment_high_confidence(self):
        hook = TaskAutomationHook()
        hook.fieldops = AsyncMock(spec=FieldOpsClient)
        hook.fieldops.create_task = AsyncMock(return_value={"id": "task_1"})

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "tenant_id": "t1",
                "payload": {
                    "field_id": "f1",
                    "nutrient": "N",
                    "severity": "high",
                    "title_ar": "نقص النيتروجين",
                    "deficiency_id": "nitrogen_deficiency",
                    "confidence": 0.8,
                    "corrections": [
                        {"type": "fertilizer", "product": "urea", "dose_kg_ha": 50},
                        {"type": "fertilizer", "product": "ammonium_sulfate", "dose_kg_ha": 75},
                        {"type": "practice", "action": "foliar_spray"},
                    ],
                },
            }
        ).encode()

        asyncio.run(hook._handle_nutrient_assessment(msg))
        # 1 inspection + up to 2 correction tasks (only fertilizer type)
        assert hook.fieldops.create_task.call_count == 3  # inspection + 2 fertilizer corrections

    def test_handle_nutrient_assessment_low_confidence(self):
        hook = TaskAutomationHook()
        hook.fieldops = AsyncMock(spec=FieldOpsClient)
        hook.fieldops.create_task = AsyncMock(return_value={"id": "task_1"})

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "tenant_id": "t1",
                "payload": {
                    "field_id": "f1",
                    "nutrient": "N",
                    "severity": "medium",
                    "title_ar": "نقص النيتروجين",
                    "confidence": 0.5,
                    "corrections": [
                        {"type": "fertilizer", "product": "urea", "dose_kg_ha": 50},
                    ],
                },
            }
        ).encode()

        asyncio.run(hook._handle_nutrient_assessment(msg))
        # Only inspection task, no corrections (confidence < 0.7)
        assert hook.fieldops.create_task.call_count == 1

    def test_handle_recommendation_error(self):
        hook = TaskAutomationHook()
        hook.fieldops = AsyncMock(spec=FieldOpsClient)
        hook.fieldops.create_task = AsyncMock(side_effect=Exception("Connection refused"))

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "tenant_id": "t1",
                "payload": {
                    "field_id": "f1",
                    "actions": ["spray_copper"],
                    "severity": "medium",
                },
            }
        ).encode()

        # Should not raise - errors are caught internally
        asyncio.run(hook._handle_recommendation(msg))
