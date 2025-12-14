"""
FieldOps Client - SAHOOL Agro Rules
HTTP client for creating tasks in FieldOps service
"""

import os
from typing import Optional
from datetime import datetime, timezone, timedelta

import httpx


FIELDOPS_URL = os.getenv("FIELDOPS_URL", "http://fieldops:8080")


class FieldOpsClient:
    """
    Client for interacting with FieldOps task service
    """

    def __init__(self, base_url: str = None):
        self.base_url = base_url or FIELDOPS_URL
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                headers={"Content-Type": "application/json"},
            )
        return self._client

    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def create_task(
        self,
        tenant_id: str,
        field_id: str,
        title: str,
        description: str,
        priority: str,
        correlation_id: str = None,
        task_type: str = "general",
        due_hours: int = 24,
        source: str = "agro_rules",
        metadata: dict = None,
    ) -> dict:
        """
        Create a new task in FieldOps

        Args:
            tenant_id: Tenant identifier
            field_id: Field identifier
            title: Task title
            description: Task description
            priority: Task priority (low, medium, high, urgent)
            correlation_id: Correlation ID for tracing
            task_type: Type of task
            due_hours: Hours until task is due
            source: Source system creating the task
            metadata: Additional metadata

        Returns:
            Created task data
        """
        client = await self._get_client()

        due_date = datetime.now(timezone.utc) + timedelta(hours=due_hours)

        payload = {
            "tenant_id": tenant_id,
            "field_id": field_id,
            "title": title,
            "description": description,
            "priority": priority,
            "task_type": task_type,
            "due_date": due_date.isoformat(),
            "source": source,
            "status": "open",
        }

        if correlation_id:
            payload["correlation_id"] = correlation_id

        if metadata:
            payload["metadata"] = metadata

        try:
            response = await client.post("/tasks", json=payload)

            if response.status_code in (200, 201):
                print(f"✅ Created task: {title} (field: {field_id})")
                return response.json()
            else:
                print(
                    f"⚠️ Task creation returned {response.status_code}: {response.text}"
                )
                return {"status": "error", "code": response.status_code}

        except httpx.ConnectError as e:
            print(f"❌ Cannot connect to FieldOps: {e}")
            return {"status": "connection_error", "error": str(e)}

        except Exception as e:
            print(f"❌ Task creation failed: {e}")
            return {"status": "error", "error": str(e)}

    async def update_task_status(
        self,
        task_id: str,
        status: str,
    ) -> dict:
        """Update task status"""
        client = await self._get_client()

        try:
            response = await client.patch(
                f"/tasks/{task_id}",
                json={"status": status},
            )
            return response.json()
        except Exception as e:
            print(f"❌ Task update failed: {e}")
            return {"status": "error", "error": str(e)}

    async def get_task(self, task_id: str) -> Optional[dict]:
        """Get task by ID"""
        client = await self._get_client()

        try:
            response = await client.get(f"/tasks/{task_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Get task failed: {e}")
            return None

    async def list_tasks(
        self,
        tenant_id: str = None,
        field_id: str = None,
        status: str = None,
        limit: int = 50,
    ) -> list[dict]:
        """List tasks with filters"""
        client = await self._get_client()

        params = {"limit": limit}
        if tenant_id:
            params["tenant_id"] = tenant_id
        if field_id:
            params["field_id"] = field_id
        if status:
            params["status"] = status

        try:
            response = await client.get("/tasks", params=params)
            if response.status_code == 200:
                return response.json().get("tasks", [])
            return []
        except Exception as e:
            print(f"❌ List tasks failed: {e}")
            return []

    async def health_check(self) -> bool:
        """Check if FieldOps service is healthy"""
        client = await self._get_client()

        try:
            response = await client.get("/healthz")
            return response.status_code == 200
        except Exception:
            return False


# Singleton instance
_client: Optional[FieldOpsClient] = None


def get_fieldops_client() -> FieldOpsClient:
    """Get or create FieldOps client singleton"""
    global _client
    if _client is None:
        _client = FieldOpsClient()
    return _client
