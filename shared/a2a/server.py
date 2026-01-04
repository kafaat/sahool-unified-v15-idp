"""
A2A Server Implementation
تطبيق خادم A2A

FastAPI router for A2A protocol endpoints with WebSocket support.
موجه FastAPI لنقاط نهاية بروتوكول A2A مع دعم WebSocket.
"""

from datetime import datetime
from typing import Any

import structlog
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse

from .agent import A2AAgent, AgentCard
from .protocol import (
    ErrorMessage,
    MessageType,
    TaskMessage,
    TaskResultMessage,
    TaskState,
)

logger = structlog.get_logger()


class A2AServer:
    """
    A2A Server for handling incoming tasks
    خادم A2A لمعالجة المهام الواردة

    Provides HTTP and WebSocket endpoints for A2A protocol.
    يوفر نقاط نهاية HTTP و WebSocket لبروتوكول A2A.
    """

    def __init__(self, agent: A2AAgent):
        """
        Initialize A2A server
        تهيئة خادم A2A

        Args:
            agent: A2A agent instance to handle tasks
        """
        self.agent = agent
        self.active_connections: dict[str, WebSocket] = {}

        logger.info(
            "a2a_server_initialized",
            agent_id=self.agent.agent_id,
            agent_name=self.agent.name,
        )

    async def handle_websocket_connection(self, websocket: WebSocket, client_id: str):
        """
        Handle WebSocket connection for streaming tasks
        معالجة اتصال WebSocket للمهام المتدفقة

        Args:
            websocket: WebSocket connection
            client_id: Client identifier
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket

        logger.info(
            "websocket_connected", client_id=client_id, agent_id=self.agent.agent_id
        )

        try:
            while True:
                # Receive task message
                # استقبال رسالة المهمة
                message_data = await websocket.receive_text()

                try:
                    import json

                    message_dict = json.loads(message_data)

                    if message_dict.get("message_type") == MessageType.TASK.value:
                        task = TaskMessage(**message_dict)

                        # Process task with streaming
                        # معالجة المهمة مع البث
                        await self._handle_streaming_task(task, websocket)

                    else:
                        # Unsupported message type
                        # نوع رسالة غير مدعوم
                        error = ErrorMessage(
                            sender_agent_id=self.agent.agent_id,
                            error_code="UNSUPPORTED_MESSAGE_TYPE",
                            error_message=f"Unsupported message type: {message_dict.get('message_type')}",
                        )
                        await websocket.send_text(error.json())

                except Exception as e:
                    # Send error message
                    # إرسال رسالة خطأ
                    error = ErrorMessage(
                        sender_agent_id=self.agent.agent_id,
                        error_code="MESSAGE_PARSE_ERROR",
                        error_message=str(e),
                    )
                    await websocket.send_text(error.json())
                    logger.error(
                        "websocket_message_error", client_id=client_id, error=str(e)
                    )

        except WebSocketDisconnect:
            logger.info("websocket_disconnected", client_id=client_id)

        except Exception as e:
            logger.error(
                "websocket_connection_error", client_id=client_id, error=str(e)
            )

        finally:
            # Clean up connection
            # تنظيف الاتصال
            if client_id in self.active_connections:
                del self.active_connections[client_id]

    async def _handle_streaming_task(self, task: TaskMessage, websocket: WebSocket):
        """
        Handle task with streaming progress updates
        معالجة المهمة مع تحديثات التقدم المتدفقة

        Args:
            task: Task message
            websocket: WebSocket connection for sending updates
        """

        # Send progress updates via callback
        # إرسال تحديثات التقدم عبر callback
        async def progress_callback(
            progress: float, partial_result: dict[str, Any] | None
        ):
            """Send progress update to client"""
            update = TaskResultMessage(
                sender_agent_id=self.agent.agent_id,
                receiver_agent_id=task.sender_agent_id,
                conversation_id=task.conversation_id,
                task_id=task.task_id,
                state=TaskState.IN_PROGRESS,
                progress=progress,
                partial_result=partial_result,
                is_final=False,
            )
            await websocket.send_text(update.json())

        try:
            # Handle task with progress callback
            # معالجة المهمة مع callback التقدم
            result = await self.agent.stream_task_progress(task, progress_callback)

            # Send final result
            # إرسال النتيجة النهائية
            await websocket.send_text(result.json())

        except Exception as e:
            # Send error
            # إرسال خطأ
            error = ErrorMessage(
                sender_agent_id=self.agent.agent_id,
                receiver_agent_id=task.sender_agent_id,
                task_id=task.task_id,
                error_code="TASK_EXECUTION_ERROR",
                error_message=str(e),
            )
            await websocket.send_text(error.json())


def create_a2a_router(agent: A2AAgent, prefix: str = "/a2a") -> APIRouter:
    """
    Create FastAPI router for A2A endpoints
    إنشاء موجه FastAPI لنقاط نهاية A2A

    Args:
        agent: A2A agent instance
        prefix: URL prefix for router

    Returns:
        Configured APIRouter
    """
    router = APIRouter(prefix=prefix, tags=["A2A Protocol"])
    server = A2AServer(agent)

    @router.get(
        "/.well-known/agent-card.json",
        response_model=AgentCard,
        summary="Get Agent Card",
        description="Returns the agent discovery card (A2A protocol)",
    )
    async def get_agent_card() -> AgentCard:
        """
        Agent discovery endpoint
        نقطة نهاية اكتشاف الوكيل

        Returns agent card following A2A specification.
        يعيد بطاقة الوكيل وفقاً لمواصفات A2A.
        """
        try:
            agent_card = agent.get_agent_card()
            logger.info("agent_card_requested", agent_id=agent.agent_id)
            return agent_card

        except Exception as e:
            logger.error("agent_card_error", agent_id=agent.agent_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate agent card: {str(e)}",
            )

    @router.post(
        "/tasks",
        response_model=TaskResultMessage,
        summary="Submit Task",
        description="Submit a task to the agent for execution",
    )
    async def submit_task(task: TaskMessage) -> TaskResultMessage:
        """
        Task submission endpoint
        نقطة نهاية إرسال المهام

        Accepts task messages and returns results.
        يقبل رسائل المهام ويعيد النتائج.
        """
        try:
            logger.info(
                "task_received",
                task_id=task.task_id,
                task_type=task.task_type,
                sender_agent_id=task.sender_agent_id,
            )

            # Check if streaming is required but not supported
            # التحقق من طلب البث لكنه غير مدعوم
            if task.require_streaming and not agent.websocket_endpoint:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Streaming not supported by this agent. Use WebSocket endpoint.",
                )

            # Handle task
            # معالجة المهمة
            result = await agent.handle_task(task)

            return result

        except HTTPException:
            raise

        except Exception as e:
            logger.error(
                "task_submission_error",
                task_id=task.task_id if hasattr(task, "task_id") else "unknown",
                error=str(e),
            )

            # Return error as task result
            # إرجاع الخطأ كنتيجة مهمة
            return TaskResultMessage(
                sender_agent_id=agent.agent_id,
                receiver_agent_id=(
                    task.sender_agent_id
                    if hasattr(task, "sender_agent_id")
                    else "unknown"
                ),
                conversation_id=(
                    task.conversation_id if hasattr(task, "conversation_id") else None
                ),
                task_id=task.task_id if hasattr(task, "task_id") else "unknown",
                state=TaskState.FAILED,
                result={"error": str(e)},
                is_final=True,
            )

    @router.get(
        "/tasks/{task_id}/status",
        response_model=TaskResultMessage,
        summary="Get Task Status",
        description="Query the status of a submitted task",
    )
    async def get_task_status(task_id: str) -> TaskResultMessage:
        """
        Task status query endpoint
        نقطة نهاية الاستعلام عن حالة المهمة

        Returns current status of a task.
        يعيد الحالة الحالية للمهمة.
        """
        try:
            # Get task from queue
            # الحصول على المهمة من القائمة
            task = agent.task_queue.get_task(task_id)

            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Task {task_id} not found",
                )

            task_state = agent.task_queue.states.get(task_id, TaskState.PENDING)

            # Return status
            # إرجاع الحالة
            return TaskResultMessage(
                sender_agent_id=agent.agent_id,
                receiver_agent_id=task.sender_agent_id,
                conversation_id=task.conversation_id,
                task_id=task_id,
                state=task_state,
                result=None if task_state != TaskState.COMPLETED else {},
                is_final=task_state in [TaskState.COMPLETED, TaskState.FAILED],
            )

        except HTTPException:
            raise

        except Exception as e:
            logger.error("task_status_error", task_id=task_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    @router.get(
        "/stats",
        summary="Get Agent Statistics",
        description="Returns agent performance statistics",
    )
    async def get_stats() -> dict[str, Any]:
        """
        Agent statistics endpoint
        نقطة نهاية إحصائيات الوكيل

        Returns performance metrics and statistics.
        يعيد مقاييس الأداء والإحصائيات.
        """
        try:
            stats = agent.get_stats()
            return {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "stats": stats,
            }

        except Exception as e:
            logger.error("stats_error", agent_id=agent.agent_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    @router.get(
        "/conversations/{conversation_id}",
        summary="Get Conversation",
        description="Returns conversation history and summary",
    )
    async def get_conversation(conversation_id: str) -> dict[str, Any]:
        """
        Conversation query endpoint
        نقطة نهاية الاستعلام عن المحادثة

        Returns conversation context and history.
        يعيد سياق المحادثة وتاريخها.
        """
        try:
            conversation = agent.get_conversation(conversation_id)

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Conversation {conversation_id} not found",
                )

            return {
                "status": "success",
                "conversation_id": conversation_id,
                "summary": conversation.get_summary(),
                "message_count": len(conversation.messages),
            }

        except HTTPException:
            raise

        except Exception as e:
            logger.error(
                "conversation_query_error",
                conversation_id=conversation_id,
                error=str(e),
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    @router.delete(
        "/tasks/{task_id}",
        summary="Cancel Task",
        description="Cancel a pending or in-progress task",
    )
    async def cancel_task(task_id: str) -> JSONResponse:
        """
        Task cancellation endpoint
        نقطة نهاية إلغاء المهمة

        Attempts to cancel a task.
        يحاول إلغاء مهمة.
        """
        try:
            # Get task
            # الحصول على المهمة
            task = agent.task_queue.get_task(task_id)

            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Task {task_id} not found",
                )

            task_state = agent.task_queue.states.get(task_id)

            # Check if task can be cancelled
            # التحقق من إمكانية إلغاء المهمة
            if task_state in [TaskState.COMPLETED, TaskState.FAILED]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Task {task_id} already in final state: {task_state}",
                )

            # Update state to cancelled
            # تحديث الحالة إلى ملغاة
            agent.task_queue.update_state(task_id, TaskState.CANCELLED)

            logger.info("task_cancelled", task_id=task_id, agent_id=agent.agent_id)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "success",
                    "message": f"Task {task_id} cancelled",
                    "task_id": task_id,
                },
            )

        except HTTPException:
            raise

        except Exception as e:
            logger.error("task_cancellation_error", task_id=task_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    @router.websocket("/ws/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, client_id: str):
        """
        WebSocket endpoint for streaming tasks
        نقطة نهاية WebSocket للمهام المتدفقة

        Provides real-time streaming of task results.
        يوفر بثاً في الوقت الفعلي لنتائج المهام.
        """
        await server.handle_websocket_connection(websocket, client_id)

    @router.get(
        "/health", summary="Health Check", description="Agent health check endpoint"
    )
    async def health_check() -> dict[str, Any]:
        """
        Health check endpoint
        نقطة نهاية فحص الصحة
        """
        return {
            "status": "healthy",
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
            "version": agent.version,
            "timestamp": datetime.utcnow().isoformat(),
            "active_websocket_connections": len(server.active_connections),
        }

    return router


# Convenience function for standalone usage
# دالة ملائمة للاستخدام المستقل
def create_standalone_a2a_app(agent: A2AAgent) -> "FastAPI":
    """
    Create standalone FastAPI app with A2A endpoints
    إنشاء تطبيق FastAPI مستقل مع نقاط نهاية A2A

    Args:
        agent: A2A agent instance

    Returns:
        FastAPI application
    """
    from fastapi import FastAPI

    app = FastAPI(
        title=f"{agent.name} - A2A Agent",
        description=agent.description,
        version=agent.version,
    )

    # Add A2A router
    # إضافة موجه A2A
    router = create_a2a_router(agent, prefix="")
    app.include_router(router)

    return app
