# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Session Manager for WhatsApp Bot Service.
مدير الجلسات لخدمة روبوت واتساب.

Handles:
- Session creation and retrieval
- Context storage between messages
- Farmer preferences tracking
- Session expiration
"""

import json
import uuid
from datetime import UTC, datetime, timedelta, timezone
from typing import TYPE_CHECKING

import structlog

from ..api.schemas import (
    ConversationIntent,
    ConversationState,
    FarmerProfile,
    Language,
)

if TYPE_CHECKING:
    import redis.asyncio as redis

logger = structlog.get_logger(__name__)


class SessionManager:
    """
    Manager for conversation sessions.
    مدير لجلسات المحادثة.
    """

    # Redis key prefixes
    SESSION_PREFIX = "whatsapp:session:"
    PROFILE_PREFIX = "whatsapp:profile:"

    def __init__(
        self,
        redis_client: "redis.Redis | None" = None,
        session_ttl: int = 3600,
        context_limit: int = 10,
    ):
        self.redis_client = redis_client
        self.session_ttl = session_ttl  # 1 hour default
        self.context_limit = context_limit

        # In-memory fallback when Redis is not available
        self._memory_sessions: dict[str, ConversationState] = {}
        self._memory_profiles: dict[str, FarmerProfile] = {}

    @property
    def has_redis(self) -> bool:
        """Check if Redis is available."""
        return self.redis_client is not None

    async def get_session(self, phone_number: str) -> ConversationState | None:
        """
        Get existing session for phone number.
        الحصول على جلسة موجودة لرقم الهاتف.
        """
        session_key = f"{self.SESSION_PREFIX}{phone_number}"

        try:
            if self.has_redis:
                data = await self.redis_client.get(session_key)
                if data:
                    session_dict = json.loads(data)
                    session = ConversationState(**session_dict)
                    logger.debug("session_retrieved", phone=phone_number[-4:] + "...")
                    return session
            else:
                if phone_number in self._memory_sessions:
                    session = self._memory_sessions[phone_number]
                    # Check if expired
                    if session.expires_at and session.expires_at < datetime.now(UTC):
                        del self._memory_sessions[phone_number]
                        return None
                    return session

        except Exception as e:
            logger.error("get_session_error", error=str(e), phone=phone_number[-4:] + "...")

        return None

    async def create_session(
        self,
        phone_number: str,
        sender_name: str | None = None,
        language: Language = Language.ARABIC,
    ) -> ConversationState:
        """
        Create a new session for phone number.
        إنشاء جلسة جديدة لرقم الهاتف.
        """
        session_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        expires_at = now + timedelta(seconds=self.session_ttl)

        # Create farmer profile
        profile = FarmerProfile(
            phone_number=phone_number,
            name=sender_name,
            language=language,
            registered_at=now,
        )

        # Create session
        session = ConversationState(
            phone_number=phone_number,
            session_id=session_id,
            profile=profile,
            language=language,
            current_intent=ConversationIntent.UNKNOWN,
            created_at=now,
            updated_at=now,
            expires_at=expires_at,
        )

        # Save session
        await self.save_session(session)

        logger.info(
            "session_created",
            phone=phone_number[-4:] + "...",
            session_id=session_id,
            language=language.value,
        )

        return session

    async def save_session(self, session: ConversationState) -> bool:
        """
        Save session to storage.
        حفظ الجلسة في التخزين.
        """
        phone_number = session.phone_number
        session_key = f"{self.SESSION_PREFIX}{phone_number}"

        # Update timestamp and expiration
        session.updated_at = datetime.now(UTC)
        session.expires_at = session.updated_at + timedelta(seconds=self.session_ttl)

        # Trim message history if needed
        if len(session.messages) > self.context_limit:
            session.messages = session.messages[-self.context_limit :]

        try:
            session_dict = session.model_dump(mode="json")

            if self.has_redis:
                await self.redis_client.setex(
                    session_key,
                    self.session_ttl,
                    json.dumps(session_dict, default=str),
                )
            else:
                self._memory_sessions[phone_number] = session

            logger.debug(
                "session_saved",
                phone=phone_number[-4:] + "...",
                messages_count=len(session.messages),
            )
            return True

        except Exception as e:
            logger.error("save_session_error", error=str(e), phone=phone_number[-4:] + "...")
            return False

    async def delete_session(self, phone_number: str) -> bool:
        """
        Delete session for phone number.
        حذف الجلسة لرقم الهاتف.
        """
        session_key = f"{self.SESSION_PREFIX}{phone_number}"

        try:
            if self.has_redis:
                await self.redis_client.delete(session_key)
            else:
                if phone_number in self._memory_sessions:
                    del self._memory_sessions[phone_number]

            logger.info("session_deleted", phone=phone_number[-4:] + "...")
            return True

        except Exception as e:
            logger.error("delete_session_error", error=str(e), phone=phone_number[-4:] + "...")
            return False

    async def get_profile(self, phone_number: str) -> FarmerProfile | None:
        """
        Get farmer profile by phone number.
        الحصول على ملف المزارع برقم الهاتف.
        """
        profile_key = f"{self.PROFILE_PREFIX}{phone_number}"

        try:
            if self.has_redis:
                data = await self.redis_client.get(profile_key)
                if data:
                    profile_dict = json.loads(data)
                    return FarmerProfile(**profile_dict)
            else:
                if phone_number in self._memory_profiles:
                    return self._memory_profiles[phone_number]

        except Exception as e:
            logger.error("get_profile_error", error=str(e), phone=phone_number[-4:] + "...")

        return None

    async def save_profile(self, profile: FarmerProfile) -> bool:
        """
        Save farmer profile.
        حفظ ملف المزارع.
        """
        phone_number = profile.phone_number
        profile_key = f"{self.PROFILE_PREFIX}{phone_number}"

        try:
            profile_dict = profile.model_dump(mode="json")

            if self.has_redis:
                # Profiles don't expire
                await self.redis_client.set(
                    profile_key,
                    json.dumps(profile_dict, default=str),
                )
            else:
                self._memory_profiles[phone_number] = profile

            logger.info("profile_saved", phone=phone_number[-4:] + "...")
            return True

        except Exception as e:
            logger.error("save_profile_error", error=str(e), phone=phone_number[-4:] + "...")
            return False

    async def update_profile(
        self,
        phone_number: str,
        **updates,
    ) -> FarmerProfile | None:
        """
        Update farmer profile fields.
        تحديث حقول ملف المزارع.
        """
        profile = await self.get_profile(phone_number)

        if not profile:
            return None

        # Update fields
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        await self.save_profile(profile)
        return profile

    async def set_language(self, phone_number: str, language: Language) -> bool:
        """
        Set user's preferred language.
        تعيين اللغة المفضلة للمستخدم.
        """
        session = await self.get_session(phone_number)
        if session:
            session.language = language
            if session.profile:
                session.profile.language = language
            await self.save_session(session)
            return True
        return False

    async def set_location(
        self,
        phone_number: str,
        latitude: float,
        longitude: float,
    ) -> bool:
        """
        Set user's location.
        تعيين موقع المستخدم.
        """
        session = await self.get_session(phone_number)
        if session and session.profile:
            session.profile.location = {"lat": latitude, "lng": longitude}
            await self.save_session(session)
            return True
        return False

    async def set_crops(self, phone_number: str, crops: list[str]) -> bool:
        """
        Set user's crops.
        تعيين محاصيل المستخدم.
        """
        session = await self.get_session(phone_number)
        if session and session.profile:
            session.profile.crops = crops
            await self.save_session(session)
            return True
        return False

    async def get_context(
        self,
        phone_number: str,
        limit: int | None = None,
    ) -> list[dict[str, str]]:
        """
        Get conversation context for LLM.
        الحصول على سياق المحادثة لنموذج اللغة.
        """
        session = await self.get_session(phone_number)
        if not session:
            return []

        limit = limit or self.context_limit
        return session.get_context_for_llm(limit)

    async def clear_context(self, phone_number: str) -> bool:
        """
        Clear conversation context (messages).
        مسح سياق المحادثة (الرسائل).
        """
        session = await self.get_session(phone_number)
        if session:
            session.messages = []
            session.current_intent = ConversationIntent.UNKNOWN
            await self.save_session(session)
            return True
        return False

    async def get_active_sessions_count(self) -> int:
        """
        Get count of active sessions.
        الحصول على عدد الجلسات النشطة.
        """
        try:
            if self.has_redis:
                count = 0
                cursor = 0
                while True:
                    cursor, keys = await self.redis_client.scan(cursor, match=f"{self.SESSION_PREFIX}*", count=100)
                    count += len(keys)
                    if cursor == 0:
                        break
                return count
            else:
                # Clean expired sessions
                now = datetime.now(UTC)
                expired = [
                    phone
                    for phone, session in self._memory_sessions.items()
                    if session.expires_at and session.expires_at < now
                ]
                for phone in expired:
                    del self._memory_sessions[phone]

                return len(self._memory_sessions)

        except Exception as e:
            logger.error("get_sessions_count_error", error=str(e))
            return 0

    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions (for in-memory storage).
        تنظيف الجلسات المنتهية الصلاحية.
        """
        if self.has_redis:
            # Redis handles expiration automatically
            return 0

        now = datetime.now(UTC)
        expired = [
            phone for phone, session in self._memory_sessions.items() if session.expires_at and session.expires_at < now
        ]

        for phone in expired:
            del self._memory_sessions[phone]

        if expired:
            logger.info("expired_sessions_cleaned", count=len(expired))

        return len(expired)
