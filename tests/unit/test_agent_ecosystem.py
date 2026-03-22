"""Tests for AI agent ecosystem."""

import pytest

from shared.ai.agent_ecosystem import (
    AGENT_DEFINITIONS,
    AgentCategory,
    AgentEcosystem,
    AgentStatus,
)


class TestAgentEcosystem:
    def setup_method(self):
        self.ecosystem = AgentEcosystem()

    def test_has_25_agents(self):
        agents = self.ecosystem.list_agents()
        assert len(agents) == 25

    def test_all_categories_present(self):
        categories = set()
        for agent in self.ecosystem.list_agents():
            categories.add(agent.category)
        assert AgentCategory.PRODUCTION in categories
        assert AgentCategory.MONITORING in categories
        assert AgentCategory.PLANNING in categories
        assert AgentCategory.MARKET in categories
        assert AgentCategory.SUPPORT in categories
        assert AgentCategory.ADVANCED in categories

    def test_production_has_5_agents(self):
        agents = self.ecosystem.list_agents(AgentCategory.PRODUCTION)
        assert len(agents) == 5

    def test_monitoring_has_5_agents(self):
        agents = self.ecosystem.list_agents(AgentCategory.MONITORING)
        assert len(agents) == 5

    def test_activate_agent(self):
        assert self.ecosystem.activate_agent("crop_advisor")
        agent = self.ecosystem.get_agent("crop_advisor")
        assert agent.status == AgentStatus.ACTIVE

    def test_activate_all(self):
        count = self.ecosystem.activate_all()
        assert count == 25
        status = self.ecosystem.get_status()
        assert status.active_agents == 25

    def test_get_status(self):
        status = self.ecosystem.get_status()
        assert status.total_agents == 25
        assert status.inactive_agents == 25

    def test_all_agents_have_arabic(self):
        for agent in self.ecosystem.list_agents():
            assert agent.name_ar, f"Agent {agent.agent_id} missing name_ar"
            assert agent.description_ar, f"Agent {agent.agent_id} missing description_ar"

    def test_find_agents_for_irrigation(self):
        matches = self.ecosystem.find_agents_for_task(["irrigation"])
        assert len(matches) > 0
        agent_ids = [a.agent_id for a in matches]
        assert "irrigation_expert" in agent_ids

    def test_activate_category(self):
        count = self.ecosystem.activate_category(AgentCategory.PRODUCTION)
        assert count == 5

    def test_deactivate_agent(self):
        self.ecosystem.activate_agent("crop_advisor")
        self.ecosystem.deactivate_agent("crop_advisor")
        agent = self.ecosystem.get_agent("crop_advisor")
        assert agent.status == AgentStatus.INACTIVE
