"""
WeChat MCP Client
=================
عميل WeChat MCP

Async client for WeChat integration via Model Context Protocol (MCP).
Inspired by WeChat-MCP architecture for agricultural messaging.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any, AsyncIterator

import httpx
import structlog

from .config import WeChatConfig, get_wechat_config
from .models import (
    Attachment,
    FetchMessagesRequest,
    Location,
    MessageType,
    MomentVisibility,
    PublishMomentRequest,
    SearchMessagesRequest,
    SendMessageRequest,
    WeChatContact,
    WeChatGroup,
    WeChatMessage,
    WeChatMoment,
)

logger = structlog.get_logger()


class WeChatMCPError(Exception):
    """
    WeChat MCP client error.
    خطأ عميل WeChat MCP
    """

    def __init__(
        self,
        message: str,
        message_ar: str | None = None,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.message_ar = message_ar or message
        self.error_code = error_code
        self.details = details or {}


class ConnectionError(WeChatMCPError):
    """Connection to MCP server failed."""

    pass


class AuthenticationError(WeChatMCPError):
    """Authentication with WeChat failed."""

    pass


class RateLimitError(WeChatMCPError):
    """Rate limit exceeded."""

    pass


class MessageError(WeChatMCPError):
    """Message operation failed."""

    pass


class WeChatMCPClient:
    """
    WeChat MCP Client for SAHOOL Platform.
    عميل WeChat MCP لمنصة سهول

    Provides async methods for interacting with WeChat through MCP protocol.
    Supports message fetching, sending, contact management, and moments.

    Features:
    - Async/await support
    - Connection pooling
    - Automatic retry with exponential backoff
    - Rate limiting
    - Bilingual error messages (Arabic/English)
    - Agricultural context integration

    Example:
        config = WeChatConfig.from_env()
        async with WeChatMCPClient(config) as client:
            messages = await client.fetch_messages("chat_id", limit=50)
            await client.send_message("chat_id", "Hello! | مرحباً!")
    """

    def __init__(self, config: WeChatConfig | None = None):
        """
        Initialize WeChat MCP Client.

        Args:
            config: Configuration object. If None, loads from environment.
        """
        self.config = config or get_wechat_config()
        self._client: httpx.AsyncClient | None = None
        self._request_id = 0
        self._connected = False

        # Rate limiting state
        self._request_count = 0
        self._request_window_start = time.time()
        self._last_request_time = 0.0

        # Cache
        self._contact_cache: dict[str, WeChatContact] = {}
        self._message_cache: dict[str, list[WeChatMessage]] = {}

        # Statistics
        self.stats = {
            "requests_made": 0,
            "requests_failed": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "total_latency_ms": 0,
        }

        logger.info(
            "wechat_mcp_client_initialized",
            mcp_url=self.config.mcp_url,
            transport=self.config.transport.value,
        )

    async def __aenter__(self) -> WeChatMCPClient:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    # =========================================================================
    # Connection Management
    # =========================================================================

    async def connect(self) -> None:
        """
        Establish connection to WeChat MCP server.
        إنشاء اتصال بخادم WeChat MCP
        """
        if self._connected:
            return

        try:
            timeout = httpx.Timeout(
                connect=self.config.connect_timeout,
                read=self.config.read_timeout,
                write=self.config.write_timeout,
            )

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": f"SAHOOL-WeChat-Client/{self.config.version}",
            }

            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"

            self._client = httpx.AsyncClient(
                base_url=self.config.mcp_url,
                timeout=timeout,
                headers=headers,
            )

            # Initialize MCP connection
            result = await self._send_mcp_request(
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": True,
                        "resources": True,
                    },
                    "clientInfo": {
                        "name": "sahool-wechat-client",
                        "version": self.config.version,
                        "tenant_id": self.config.tenant_id,
                    },
                },
            )

            self._connected = True

            logger.info(
                "wechat_mcp_connected",
                server_info=result.get("serverInfo", {}),
            )

        except httpx.HTTPError as e:
            raise ConnectionError(
                f"Failed to connect to WeChat MCP: {e}",
                message_ar=f"فشل الاتصال بـ WeChat MCP: {e}",
                error_code="CONNECTION_FAILED",
            )

    async def close(self) -> None:
        """
        Close connection to WeChat MCP server.
        إغلاق الاتصال بخادم WeChat MCP
        """
        if self._client:
            await self._client.aclose()
            self._client = None
            self._connected = False

            logger.info("wechat_mcp_disconnected")

    async def health_check(self) -> dict[str, Any]:
        """
        Check health of WeChat MCP connection.
        التحقق من صحة اتصال WeChat MCP

        Returns:
            Health status dictionary
        """
        try:
            start = time.time()
            await self._send_mcp_request("ping", {})
            latency = (time.time() - start) * 1000

            return {
                "status": "healthy",
                "status_ar": "سليم",
                "connected": self._connected,
                "latency_ms": latency,
                "stats": self.stats,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "status_ar": "غير سليم",
                "connected": False,
                "error": str(e),
            }

    # =========================================================================
    # Message Operations
    # =========================================================================

    async def fetch_messages(
        self,
        chat_id: str,
        limit: int = 50,
        since: datetime | None = None,
        until: datetime | None = None,
        message_types: list[MessageType] | None = None,
    ) -> list[WeChatMessage]:
        """
        Fetch messages from a chat.
        جلب الرسائل من محادثة

        Args:
            chat_id: Chat/conversation ID
            limit: Maximum messages to fetch (1-500)
            since: Fetch messages after this time
            until: Fetch messages before this time
            message_types: Filter by message types

        Returns:
            List of messages

        Example:
            messages = await client.fetch_messages(
                chat_id="farmer_001",
                limit=100,
                since=datetime.now() - timedelta(days=7)
            )
        """
        await self._ensure_connected()

        request = FetchMessagesRequest(
            chat_id=chat_id,
            limit=min(limit, 500),
            since=since,
            until=until,
            message_types=message_types,
        )

        result = await self._call_tool(
            "fetch_messages",
            {
                "chat_id": request.chat_id,
                "limit": request.limit,
                "since": request.since.isoformat() if request.since else None,
                "until": request.until.isoformat() if request.until else None,
                "message_types": [mt.value for mt in request.message_types] if request.message_types else None,
            },
        )

        messages = []
        for msg_data in result.get("messages", []):
            try:
                message = WeChatMessage(**msg_data)
                messages.append(message)
            except Exception as e:
                logger.warning("message_parse_error", error=str(e), data=msg_data)

        self.stats["messages_received"] += len(messages)

        # Update cache
        if self.config.cache.enabled:
            self._message_cache[chat_id] = messages

        logger.info(
            "messages_fetched",
            chat_id=chat_id,
            count=len(messages),
        )

        return messages

    async def send_message(
        self,
        chat_id: str,
        content: str,
        content_ar: str | None = None,
        message_type: MessageType = MessageType.TEXT,
        reply_to_id: str | None = None,
        attachments: list[Attachment] | None = None,
        location: Location | None = None,
    ) -> WeChatMessage:
        """
        Send a message to a chat.
        إرسال رسالة إلى محادثة

        Args:
            chat_id: Chat/conversation ID
            content: Message content
            content_ar: Arabic content (optional)
            message_type: Type of message
            reply_to_id: ID of message to reply to
            attachments: File attachments
            location: Location data

        Returns:
            Sent message object

        Example:
            message = await client.send_message(
                chat_id="farmer_001",
                content="The irrigation should start at 6 AM tomorrow.",
                content_ar="يجب أن يبدأ الري في الساعة 6 صباحاً غداً."
            )
        """
        await self._ensure_connected()

        request = SendMessageRequest(
            chat_id=chat_id,
            content=content,
            content_ar=content_ar,
            type=message_type,
            reply_to_id=reply_to_id,
            attachments=attachments or [],
            location=location,
        )

        result = await self._call_tool(
            "send_message",
            {
                "chat_id": request.chat_id,
                "content": request.content,
                "content_ar": request.content_ar,
                "type": request.type.value,
                "reply_to_id": request.reply_to_id,
                "attachments": [a.model_dump() for a in request.attachments] if request.attachments else None,
                "location": request.location.model_dump() if request.location else None,
            },
        )

        message = WeChatMessage(
            id=result.get("message_id", str(uuid.uuid4())),
            type=message_type,
            chat_id=chat_id,
            sender_id="self",
            receiver_id=chat_id,
            content=content,
            content_ar=content_ar,
            timestamp=datetime.now(UTC),
        )

        self.stats["messages_sent"] += 1

        logger.info(
            "message_sent",
            chat_id=chat_id,
            message_id=message.id,
            type=message_type.value,
        )

        return message

    async def search_messages(
        self,
        query: str,
        chat_ids: list[str] | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 50,
    ) -> list[WeChatMessage]:
        """
        Search messages across chats.
        البحث في الرسائل عبر المحادثات

        Args:
            query: Search query
            chat_ids: Limit search to specific chats
            since: Search after this time
            until: Search before this time
            limit: Maximum results

        Returns:
            List of matching messages
        """
        await self._ensure_connected()

        request = SearchMessagesRequest(
            query=query,
            chat_ids=chat_ids,
            since=since,
            until=until,
            limit=limit,
        )

        result = await self._call_tool(
            "search_messages",
            {
                "query": request.query,
                "chat_ids": request.chat_ids,
                "since": request.since.isoformat() if request.since else None,
                "until": request.until.isoformat() if request.until else None,
                "limit": request.limit,
            },
        )

        messages = []
        for msg_data in result.get("results", []):
            try:
                message = WeChatMessage(**msg_data)
                messages.append(message)
            except Exception as e:
                logger.warning("search_result_parse_error", error=str(e))

        logger.info(
            "messages_searched",
            query=query[:50],
            results=len(messages),
        )

        return messages

    # =========================================================================
    # Contact Operations
    # =========================================================================

    async def get_contacts(
        self,
        limit: int = 100,
        offset: int = 0,
        search: str | None = None,
    ) -> list[WeChatContact]:
        """
        Get list of contacts.
        الحصول على قائمة جهات الاتصال

        Args:
            limit: Maximum contacts to fetch
            offset: Pagination offset
            search: Search filter

        Returns:
            List of contacts
        """
        await self._ensure_connected()

        result = await self._call_tool(
            "get_contacts",
            {
                "limit": limit,
                "offset": offset,
                "search": search,
            },
        )

        contacts = []
        for contact_data in result.get("contacts", []):
            try:
                contact = WeChatContact(**contact_data)
                contacts.append(contact)

                # Update cache
                if self.config.cache.enabled:
                    self._contact_cache[contact.id] = contact
            except Exception as e:
                logger.warning("contact_parse_error", error=str(e))

        logger.info("contacts_fetched", count=len(contacts))

        return contacts

    async def get_contact(self, contact_id: str) -> WeChatContact | None:
        """
        Get a single contact by ID.
        الحصول على جهة اتصال واحدة بالمعرف

        Args:
            contact_id: Contact ID

        Returns:
            Contact object or None
        """
        # Check cache first
        if self.config.cache.enabled and contact_id in self._contact_cache:
            return self._contact_cache[contact_id]

        await self._ensure_connected()

        result = await self._call_tool(
            "get_contact",
            {"contact_id": contact_id},
        )

        if not result.get("contact"):
            return None

        contact = WeChatContact(**result["contact"])

        # Update cache
        if self.config.cache.enabled:
            self._contact_cache[contact.id] = contact

        return contact

    async def add_contact(
        self,
        wechat_id: str,
        name: str | None = None,
        name_ar: str | None = None,
        message: str | None = None,
        farmer_id: str | None = None,
    ) -> WeChatContact:
        """
        Add a new contact.
        إضافة جهة اتصال جديدة

        Args:
            wechat_id: WeChat ID to add
            name: Display name
            name_ar: Arabic name
            message: Friend request message
            farmer_id: Associated SAHOOL farmer ID

        Returns:
            New contact object
        """
        await self._ensure_connected()

        result = await self._call_tool(
            "add_contact",
            {
                "wechat_id": wechat_id,
                "name": name,
                "name_ar": name_ar,
                "message": message,
                "farmer_id": farmer_id,
            },
        )

        contact = WeChatContact(
            id=result.get("contact_id", str(uuid.uuid4())),
            wechat_id=wechat_id,
            name=name or wechat_id,
            name_ar=name_ar,
            farmer_id=farmer_id,
        )

        # Update cache
        if self.config.cache.enabled:
            self._contact_cache[contact.id] = contact

        logger.info(
            "contact_added",
            contact_id=contact.id,
            wechat_id=wechat_id,
        )

        return contact

    async def update_contact(
        self,
        contact_id: str,
        updates: dict[str, Any],
    ) -> WeChatContact:
        """
        Update contact information.
        تحديث معلومات جهة الاتصال

        Args:
            contact_id: Contact ID to update
            updates: Fields to update

        Returns:
            Updated contact object
        """
        await self._ensure_connected()

        result = await self._call_tool(
            "update_contact",
            {
                "contact_id": contact_id,
                **updates,
            },
        )

        contact = WeChatContact(**result.get("contact", {"id": contact_id}))

        # Update cache
        if self.config.cache.enabled:
            self._contact_cache[contact.id] = contact

        logger.info("contact_updated", contact_id=contact_id)

        return contact

    # =========================================================================
    # Group Operations
    # =========================================================================

    async def get_groups(self, limit: int = 50) -> list[WeChatGroup]:
        """
        Get list of groups.
        الحصول على قائمة المجموعات

        Args:
            limit: Maximum groups to fetch

        Returns:
            List of groups
        """
        await self._ensure_connected()

        result = await self._call_tool(
            "get_groups",
            {"limit": limit},
        )

        groups = []
        for group_data in result.get("groups", []):
            try:
                group = WeChatGroup(**group_data)
                groups.append(group)
            except Exception as e:
                logger.warning("group_parse_error", error=str(e))

        logger.info("groups_fetched", count=len(groups))

        return groups

    # =========================================================================
    # Moments Operations
    # =========================================================================

    async def get_moments(
        self,
        contact_id: str | None = None,
        limit: int = 20,
        since: datetime | None = None,
    ) -> list[WeChatMoment]:
        """
        Get moments/timeline posts.
        الحصول على منشورات اللحظات

        Args:
            contact_id: Filter by contact (None for all friends)
            limit: Maximum moments to fetch
            since: Fetch moments after this time

        Returns:
            List of moments
        """
        await self._ensure_connected()

        result = await self._call_tool(
            "get_moments",
            {
                "contact_id": contact_id,
                "limit": limit,
                "since": since.isoformat() if since else None,
            },
        )

        moments = []
        for moment_data in result.get("moments", []):
            try:
                moment = WeChatMoment(**moment_data)
                moments.append(moment)
            except Exception as e:
                logger.warning("moment_parse_error", error=str(e))

        logger.info("moments_fetched", count=len(moments))

        return moments

    async def publish_moment(
        self,
        content: str,
        content_ar: str | None = None,
        images: list[str] | None = None,
        video_url: str | None = None,
        location: Location | None = None,
        visibility: MomentVisibility = MomentVisibility.FRIENDS_ONLY,
    ) -> WeChatMoment:
        """
        Publish a moment/timeline post.
        نشر لحظة/منشور في الجدول الزمني

        Args:
            content: Post content
            content_ar: Arabic content
            images: List of image URLs
            video_url: Video URL
            location: Location data
            visibility: Post visibility setting

        Returns:
            Published moment object

        Example:
            moment = await client.publish_moment(
                content="Great harvest today!",
                content_ar="حصاد رائع اليوم!",
                images=["https://example.com/harvest.jpg"],
                location=Location(latitude=15.55, longitude=48.51)
            )
        """
        await self._ensure_connected()

        request = PublishMomentRequest(
            content=content,
            content_ar=content_ar,
            images=images or [],
            video_url=video_url,
            location=location,
            visibility=visibility,
        )

        result = await self._call_tool(
            "publish_moment",
            {
                "content": request.content,
                "content_ar": request.content_ar,
                "images": request.images,
                "video_url": request.video_url,
                "location": request.location.model_dump() if request.location else None,
                "visibility": request.visibility.value,
            },
        )

        moment = WeChatMoment(
            id=result.get("moment_id", str(uuid.uuid4())),
            author_id="self",
            content=content,
            content_ar=content_ar,
            images=images or [],
            video_url=video_url,
            location=location,
            visibility=visibility,
        )

        logger.info(
            "moment_published",
            moment_id=moment.id,
            visibility=visibility.value,
        )

        return moment

    # =========================================================================
    # Streaming Support
    # =========================================================================

    async def stream_messages(
        self,
        chat_id: str,
        poll_interval: float = 5.0,
    ) -> AsyncIterator[WeChatMessage]:
        """
        Stream new messages from a chat.
        تدفق الرسائل الجديدة من محادثة

        Args:
            chat_id: Chat ID to stream from
            poll_interval: Seconds between polls

        Yields:
            New messages as they arrive

        Example:
            async for message in client.stream_messages("farmer_001"):
                print(f"New message: {message.content}")
        """
        await self._ensure_connected()

        last_message_time = datetime.now(UTC)

        while True:
            try:
                messages = await self.fetch_messages(
                    chat_id=chat_id,
                    since=last_message_time,
                    limit=50,
                )

                for message in messages:
                    if message.timestamp > last_message_time:
                        last_message_time = message.timestamp
                        yield message

                await asyncio.sleep(poll_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("stream_error", chat_id=chat_id, error=str(e))
                await asyncio.sleep(poll_interval * 2)

    # =========================================================================
    # Internal Methods
    # =========================================================================

    async def _ensure_connected(self) -> None:
        """Ensure client is connected."""
        if not self._connected:
            await self.connect()

    def _next_request_id(self) -> int:
        """Generate next request ID."""
        self._request_id += 1
        return self._request_id

    async def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting."""
        now = time.time()

        # Reset window if expired
        if now - self._request_window_start > 60:
            self._request_count = 0
            self._request_window_start = now

        # Check limit
        if self._request_count >= self.config.rate_limit.requests_per_minute:
            wait_time = 60 - (now - self._request_window_start)
            if wait_time > 0:
                logger.warning(
                    "rate_limit_reached",
                    wait_seconds=wait_time,
                )
                raise RateLimitError(
                    f"Rate limit exceeded. Wait {wait_time:.1f} seconds.",
                    message_ar=f"تم تجاوز حد المعدل. انتظر {wait_time:.1f} ثانية.",
                    error_code="RATE_LIMIT_EXCEEDED",
                )

        self._request_count += 1

    async def _send_mcp_request(
        self,
        method: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Send MCP JSON-RPC request."""
        await self._check_rate_limit()

        if not self._client:
            raise ConnectionError(
                "Client not connected",
                message_ar="العميل غير متصل",
            )

        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": method,
            "params": params,
        }

        start_time = time.time()

        try:
            response = await self._client.post(
                "/mcp",
                json=request,
            )
            response.raise_for_status()

            latency = (time.time() - start_time) * 1000
            self.stats["requests_made"] += 1
            self.stats["total_latency_ms"] += latency

            result = response.json()

            if "error" in result:
                error = result["error"]
                raise WeChatMCPError(
                    message=error.get("message", "Unknown error"),
                    error_code=str(error.get("code", "UNKNOWN")),
                    details=error.get("data"),
                )

            return result.get("result", {})

        except httpx.HTTPError as e:
            self.stats["requests_failed"] += 1
            raise ConnectionError(
                f"HTTP request failed: {e}",
                message_ar=f"فشل طلب HTTP: {e}",
            )

    async def _call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """Call an MCP tool with retry logic."""
        last_error = None

        for attempt in range(self.config.retry.max_retries + 1):
            try:
                result = await self._send_mcp_request(
                    "tools/call",
                    {
                        "name": tool_name,
                        "arguments": {k: v for k, v in arguments.items() if v is not None},
                    },
                )

                # Parse content if it's a text response
                content = result.get("content", [])
                if content and isinstance(content, list):
                    first_content = content[0]
                    if first_content.get("type") == "text":
                        try:
                            return json.loads(first_content.get("text", "{}"))
                        except json.JSONDecodeError:
                            return {"text": first_content.get("text")}

                return result

            except RateLimitError:
                raise  # Don't retry rate limits
            except WeChatMCPError as e:
                last_error = e
                if attempt < self.config.retry.max_retries:
                    delay = min(
                        self.config.retry.base_delay_seconds * (self.config.retry.exponential_base**attempt),
                        self.config.retry.max_delay_seconds,
                    )
                    logger.warning(
                        "tool_call_retry",
                        tool=tool_name,
                        attempt=attempt + 1,
                        delay=delay,
                        error=str(e),
                    )
                    await asyncio.sleep(delay)

        raise last_error or WeChatMCPError(f"Tool {tool_name} failed after retries")


# =============================================================================
# Context Manager
# =============================================================================


@asynccontextmanager
async def wechat_client(
    config: WeChatConfig | None = None,
) -> AsyncIterator[WeChatMCPClient]:
    """
    Context manager for WeChat MCP client.
    مدير السياق لعميل WeChat MCP

    Example:
        async with wechat_client() as client:
            messages = await client.fetch_messages("chat_id")
    """
    client = WeChatMCPClient(config)
    try:
        await client.connect()
        yield client
    finally:
        await client.close()


# =============================================================================
# Convenience Functions
# =============================================================================


async def fetch_recent_messages(
    chat_id: str,
    hours: int = 24,
    config: WeChatConfig | None = None,
) -> list[WeChatMessage]:
    """
    Fetch recent messages from a chat.
    جلب الرسائل الأخيرة من محادثة

    Args:
        chat_id: Chat ID
        hours: Number of hours to look back
        config: Optional configuration

    Returns:
        List of recent messages
    """
    from datetime import timedelta

    async with wechat_client(config) as client:
        return await client.fetch_messages(
            chat_id=chat_id,
            since=datetime.now(UTC) - timedelta(hours=hours),
        )


async def send_quick_message(
    chat_id: str,
    content: str,
    content_ar: str | None = None,
    config: WeChatConfig | None = None,
) -> WeChatMessage:
    """
    Send a quick message.
    إرسال رسالة سريعة

    Args:
        chat_id: Chat ID
        content: Message content
        content_ar: Arabic content
        config: Optional configuration

    Returns:
        Sent message
    """
    async with wechat_client(config) as client:
        return await client.send_message(
            chat_id=chat_id,
            content=content,
            content_ar=content_ar,
        )
