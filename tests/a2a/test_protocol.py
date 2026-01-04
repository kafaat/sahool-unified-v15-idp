"""
A2A Protocol Tests
اختبارات بروتوكول A2A

Comprehensive tests for A2A protocol implementation.
اختبارات شاملة لتطبيق بروتوكول A2A.
"""

import os
import sys
from typing import Any

import pytest

# Add shared path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))

from a2a.agent import (
    A2AAgent,
    AgentCapability,
    AgentCard,
)
from a2a.client import (
    A2AClient,
    AgentDiscovery,
)
from a2a.protocol import (
    ConversationContext,
    ErrorMessage,
    MessageType,
    TaskMessage,
    TaskQueue,
    TaskResultMessage,
    TaskState,
)

# Test Protocol Messages
# اختبار رسائل البروتوكول


class TestTaskMessage:
    """Test TaskMessage creation and validation"""

    def test_create_task_message(self):
        """Test creating a basic task message"""
        task = TaskMessage(
            sender_agent_id="agent-1",
            receiver_agent_id="agent-2",
            task_type="test-task",
            task_description="Test task description",
            parameters={"param1": "value1"},
        )

        assert task.sender_agent_id == "agent-1"
        assert task.receiver_agent_id == "agent-2"
        assert task.task_type == "test-task"
        assert task.message_type == MessageType.TASK
        assert task.priority == 5  # Default priority
        assert isinstance(task.task_id, str)
        assert isinstance(task.message_id, str)

    def test_task_message_with_priority(self):
        """Test task message with custom priority"""
        task = TaskMessage(
            sender_agent_id="agent-1",
            task_type="high-priority",
            task_description="Urgent task",
            parameters={},
            priority=10,
        )

        assert task.priority == 10

    def test_task_message_serialization(self):
        """Test task message JSON serialization"""
        task = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test",
            task_description="Test",
            parameters={"key": "value"},
        )

        json_str = task.json()
        assert isinstance(json_str, str)
        assert "task_id" in json_str
        assert "sender_agent_id" in json_str

    def test_task_message_dict(self):
        """Test task message dictionary conversion"""
        task = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test",
            task_description="Test",
            parameters={"key": "value"},
        )

        task_dict = task.dict()
        assert isinstance(task_dict, dict)
        assert task_dict["sender_agent_id"] == "agent-1"
        assert task_dict["task_type"] == "test"


class TestTaskResultMessage:
    """Test TaskResultMessage creation and validation"""

    def test_create_task_result(self):
        """Test creating task result message"""
        result = TaskResultMessage(
            sender_agent_id="agent-2",
            receiver_agent_id="agent-1",
            task_id="task-123",
            state=TaskState.COMPLETED,
            result={"output": "success"},
        )

        assert result.sender_agent_id == "agent-2"
        assert result.task_id == "task-123"
        assert result.state == TaskState.COMPLETED
        assert result.is_final is True
        assert result.result["output"] == "success"

    def test_task_result_in_progress(self):
        """Test in-progress task result with partial data"""
        result = TaskResultMessage(
            sender_agent_id="agent-2",
            task_id="task-123",
            state=TaskState.IN_PROGRESS,
            progress=0.5,
            partial_result={"status": "processing"},
            is_final=False,
        )

        assert result.state == TaskState.IN_PROGRESS
        assert result.progress == 0.5
        assert result.is_final is False
        assert result.partial_result["status"] == "processing"

    def test_task_result_failed(self):
        """Test failed task result"""
        result = TaskResultMessage(
            sender_agent_id="agent-2",
            task_id="task-123",
            state=TaskState.FAILED,
            result={"error": "Task failed"},
            is_final=True,
        )

        assert result.state == TaskState.FAILED
        assert result.is_final is True


class TestErrorMessage:
    """Test ErrorMessage creation"""

    def test_create_error_message(self):
        """Test creating error message"""
        error = ErrorMessage(
            sender_agent_id="agent-1",
            task_id="task-123",
            error_code="TASK_FAILED",
            error_message="Task execution failed",
            recoverable=True,
        )

        assert error.sender_agent_id == "agent-1"
        assert error.error_code == "TASK_FAILED"
        assert error.error_message == "Task execution failed"
        assert error.recoverable is True
        assert error.message_type == MessageType.ERROR


class TestConversationContext:
    """Test ConversationContext functionality"""

    def test_create_conversation(self):
        """Test creating conversation context"""
        conv = ConversationContext()

        assert isinstance(conv.conversation_id, str)
        assert len(conv.messages) == 0
        assert len(conv.tasks) == 0

    def test_add_task_message(self):
        """Test adding task message to conversation"""
        conv = ConversationContext()
        task = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test",
            task_description="Test",
            parameters={},
        )

        conv.add_message(task)

        assert len(conv.messages) == 1
        assert task.task_id in conv.tasks
        assert conv.tasks[task.task_id] == TaskState.PENDING

    def test_add_result_message(self):
        """Test adding result message updates task state"""
        conv = ConversationContext()
        task = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test",
            task_description="Test",
            parameters={},
        )
        conv.add_message(task)

        result = TaskResultMessage(
            sender_agent_id="agent-2",
            task_id=task.task_id,
            state=TaskState.COMPLETED,
            result={"output": "done"},
        )
        conv.add_message(result)

        assert len(conv.messages) == 2
        assert conv.tasks[task.task_id] == TaskState.COMPLETED

    def test_get_task_state(self):
        """Test retrieving task state"""
        conv = ConversationContext()
        task = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test",
            task_description="Test",
            parameters={},
        )
        conv.add_message(task)

        state = conv.get_task_state(task.task_id)
        assert state == TaskState.PENDING

    def test_get_messages_by_type(self):
        """Test filtering messages by type"""
        conv = ConversationContext()

        task1 = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test1",
            task_description="Test 1",
            parameters={},
        )
        task2 = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test2",
            task_description="Test 2",
            parameters={},
        )
        result = TaskResultMessage(
            sender_agent_id="agent-2",
            task_id=task1.task_id,
            state=TaskState.COMPLETED,
            result={},
        )

        conv.add_message(task1)
        conv.add_message(task2)
        conv.add_message(result)

        task_messages = conv.get_messages_by_type(MessageType.TASK)
        assert len(task_messages) == 2

        result_messages = conv.get_messages_by_type(MessageType.TASK_RESULT)
        assert len(result_messages) == 1

    def test_get_conversation_summary(self):
        """Test getting conversation summary"""
        conv = ConversationContext()

        task = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test",
            task_description="Test",
            parameters={},
        )
        conv.add_message(task)

        summary = conv.get_summary()

        assert summary["conversation_id"] == conv.conversation_id
        assert summary["total_messages"] == 1
        assert summary["tasks"]["total"] == 1
        assert summary["tasks"]["pending"] == 1

    def test_clear_completed_tasks(self):
        """Test clearing completed tasks"""
        conv = ConversationContext()

        task1 = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test1",
            task_description="Test 1",
            parameters={},
        )
        task2 = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test2",
            task_description="Test 2",
            parameters={},
        )

        conv.add_message(task1)
        conv.add_message(task2)

        # Complete task1
        result1 = TaskResultMessage(
            sender_agent_id="agent-2",
            task_id=task1.task_id,
            state=TaskState.COMPLETED,
            result={},
        )
        conv.add_message(result1)

        cleared = conv.clear_completed_tasks()

        assert cleared == 1
        assert task1.task_id not in conv.tasks
        assert task2.task_id in conv.tasks


class TestTaskQueue:
    """Test TaskQueue functionality"""

    def test_create_task_queue(self):
        """Test creating task queue"""
        queue = TaskQueue()

        assert len(queue.tasks) == 0
        assert len(queue.states) == 0

    def test_add_task(self):
        """Test adding task to queue"""
        queue = TaskQueue()
        task = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test",
            task_description="Test",
            parameters={},
        )

        queue.add_task(task)

        assert task.task_id in queue.tasks
        assert queue.states[task.task_id] == TaskState.PENDING

    def test_get_task(self):
        """Test retrieving task from queue"""
        queue = TaskQueue()
        task = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test",
            task_description="Test",
            parameters={},
        )
        queue.add_task(task)

        retrieved = queue.get_task(task.task_id)

        assert retrieved is not None
        assert retrieved.task_id == task.task_id

    def test_update_state(self):
        """Test updating task state"""
        queue = TaskQueue()
        task = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test",
            task_description="Test",
            parameters={},
        )
        queue.add_task(task)

        queue.update_state(task.task_id, TaskState.IN_PROGRESS)

        assert queue.states[task.task_id] == TaskState.IN_PROGRESS

    def test_get_pending_tasks(self):
        """Test getting pending tasks sorted by priority"""
        queue = TaskQueue()

        task1 = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test1",
            task_description="Low priority",
            parameters={},
            priority=3,
        )
        task2 = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test2",
            task_description="High priority",
            parameters={},
            priority=9,
        )

        queue.add_task(task1)
        queue.add_task(task2)

        pending = queue.get_pending_tasks()

        assert len(pending) == 2
        assert pending[0].priority == 9  # Highest priority first
        assert pending[1].priority == 3

    def test_remove_task(self):
        """Test removing task from queue"""
        queue = TaskQueue()
        task = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test",
            task_description="Test",
            parameters={},
        )
        queue.add_task(task)

        removed = queue.remove_task(task.task_id)

        assert removed is True
        assert task.task_id not in queue.tasks
        assert task.task_id not in queue.states

    def test_get_stats(self):
        """Test queue statistics"""
        queue = TaskQueue()

        task1 = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test1",
            task_description="Test 1",
            parameters={},
        )
        task2 = TaskMessage(
            sender_agent_id="agent-1",
            task_type="test2",
            task_description="Test 2",
            parameters={},
        )

        queue.add_task(task1)
        queue.add_task(task2)
        queue.update_state(task1.task_id, TaskState.COMPLETED)

        stats = queue.get_stats()

        assert stats["total"] == 2
        assert stats["pending"] == 1
        assert stats["completed"] == 1


# Test Agent Implementation
# اختبار تطبيق الوكيل


class TestA2AAgent:
    """Test A2AAgent base class"""

    class MockA2AAgent(A2AAgent):
        """Mock agent for testing"""

        def get_capabilities(self):
            return [
                AgentCapability(
                    capability_id="test-capability",
                    name="Test Capability",
                    description="Test capability",
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                )
            ]

    def test_create_agent(self):
        """Test creating A2A agent"""
        agent = self.MockA2AAgent(
            agent_id="test-agent",
            name="Test Agent",
            version="1.0.0",
            description="Test agent",
            provider="Test Provider",
            task_endpoint="http://localhost:8000/tasks",
        )

        assert agent.agent_id == "test-agent"
        assert agent.name == "Test Agent"
        assert agent.version == "1.0.0"

    def test_get_agent_card(self):
        """Test agent card generation"""
        agent = self.MockA2AAgent(
            agent_id="test-agent",
            name="Test Agent",
            version="1.0.0",
            description="Test agent",
            provider="Test Provider",
            task_endpoint="http://localhost:8000/tasks",
        )

        card = agent.get_agent_card()

        assert isinstance(card, AgentCard)
        assert card.agent_id == "test-agent"
        assert card.name == "Test Agent"
        assert len(card.capabilities) == 1
        assert card.protocol_version == "1.0"

    def test_register_task_handler(self):
        """Test registering task handler"""
        agent = self.MockA2AAgent(
            agent_id="test-agent",
            name="Test Agent",
            version="1.0.0",
            description="Test agent",
            provider="Test Provider",
            task_endpoint="http://localhost:8000/tasks",
        )

        async def test_handler(task: TaskMessage) -> dict[str, Any]:
            return {"result": "success"}

        agent.register_task_handler("test-task", test_handler)

        assert "test-task" in agent.task_handlers

    @pytest.mark.asyncio
    async def test_handle_task(self):
        """Test handling task"""
        agent = self.MockA2AAgent(
            agent_id="test-agent",
            name="Test Agent",
            version="1.0.0",
            description="Test agent",
            provider="Test Provider",
            task_endpoint="http://localhost:8000/tasks",
        )

        async def test_handler(task: TaskMessage) -> dict[str, Any]:
            return {"result": "success", "input": task.parameters}

        agent.register_task_handler("test-task", test_handler)

        task = TaskMessage(
            sender_agent_id="sender",
            task_type="test-task",
            task_description="Test",
            parameters={"param": "value"},
        )

        result = await agent.handle_task(task)

        assert isinstance(result, TaskResultMessage)
        assert result.state == TaskState.COMPLETED
        assert result.result["result"] == "success"
        assert result.result["input"]["param"] == "value"

    @pytest.mark.asyncio
    async def test_handle_task_error(self):
        """Test handling task with error"""
        agent = self.MockA2AAgent(
            agent_id="test-agent",
            name="Test Agent",
            version="1.0.0",
            description="Test agent",
            provider="Test Provider",
            task_endpoint="http://localhost:8000/tasks",
        )

        async def failing_handler(task: TaskMessage) -> dict[str, Any]:
            raise ValueError("Test error")

        agent.register_task_handler("failing-task", failing_handler)

        task = TaskMessage(
            sender_agent_id="sender",
            task_type="failing-task",
            task_description="Test",
            parameters={},
        )

        result = await agent.handle_task(task)

        assert result.state == TaskState.FAILED
        assert "error" in result.result

    def test_get_stats(self):
        """Test getting agent statistics"""
        agent = self.MockA2AAgent(
            agent_id="test-agent",
            name="Test Agent",
            version="1.0.0",
            description="Test agent",
            provider="Test Provider",
            task_endpoint="http://localhost:8000/tasks",
        )

        stats = agent.get_stats()

        assert stats["agent_id"] == "test-agent"
        assert stats["name"] == "Test Agent"
        assert stats["tasks_received"] == 0
        assert stats["tasks_completed"] == 0


# Test Client Implementation
# اختبار تطبيق العميل


class TestA2AClient:
    """Test A2AClient"""

    def test_create_client(self):
        """Test creating A2A client"""
        client = A2AClient(
            sender_agent_id="client-agent",
            timeout=60,
        )

        assert client.sender_agent_id == "client-agent"
        assert client.timeout == 60


class TestAgentDiscovery:
    """Test AgentDiscovery"""

    def test_create_discovery(self):
        """Test creating agent discovery"""
        discovery = AgentDiscovery(timeout=30)

        assert discovery.timeout == 30
        assert len(discovery.discovered_agents) == 0


# Integration Tests
# اختبارات التكامل


@pytest.mark.asyncio
class TestA2AIntegration:
    """Integration tests for A2A protocol"""

    async def test_full_task_lifecycle(self):
        """Test complete task lifecycle from submission to completion"""

        # Create agent
        class TestAgent(A2AAgent):
            def get_capabilities(self):
                return [
                    AgentCapability(
                        capability_id="echo",
                        name="Echo",
                        description="Echo input",
                        input_schema={"type": "object"},
                        output_schema={"type": "object"},
                    )
                ]

        agent = TestAgent(
            agent_id="echo-agent",
            name="Echo Agent",
            version="1.0.0",
            description="Echo agent",
            provider="Test",
            task_endpoint="http://localhost:8000/tasks",
        )

        # Register handler
        async def echo_handler(task: TaskMessage) -> dict[str, Any]:
            return {"echo": task.parameters}

        agent.register_task_handler("echo", echo_handler)

        # Create and handle task
        task = TaskMessage(
            sender_agent_id="client",
            task_type="echo",
            task_description="Echo test",
            parameters={"message": "Hello, A2A!"},
        )

        result = await agent.handle_task(task)

        # Verify result
        assert result.state == TaskState.COMPLETED
        assert result.result["echo"]["message"] == "Hello, A2A!"
        assert result.execution_time_ms is not None
        assert result.execution_time_ms > 0

        # Verify stats
        stats = agent.get_stats()
        assert stats["tasks_received"] == 1
        assert stats["tasks_completed"] == 1
        assert stats["success_rate"] == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
