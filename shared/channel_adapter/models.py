"""Channel message models — نماذج رسائل القنوات"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class ChannelType(StrEnum):
    WHATSAPP = "whatsapp"
    USSD = "ussd"
    WECHAT = "wechat"
    WEB = "web"
    MOBILE = "mobile"


@dataclass
class ChannelMessage:
    text: str
    channel: ChannelType
    sender_id: str
    tenant_id: str | None = None
    field_id: str | None = None
    language: str = "ar"
    image: bytes | None = None
    location: dict | None = None  # {lat, lng}
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)


@dataclass
class ChannelResponse:
    text: str
    text_ar: str
    intent: str
    confidence: float
    services_used: list[str] = field(default_factory=list)
    sources: list[dict] = field(default_factory=list)
    images: list[str] = field(default_factory=list)
    actions: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def format_for_channel(self, channel: ChannelType) -> str:
        """Format response for specific channel constraints."""
        if channel == ChannelType.USSD:
            return self.text_ar[:140]
        if channel == ChannelType.WHATSAPP:
            sections = [self.text_ar]
            if self.sources:
                sections.append(f"\n📋 المصادر: {', '.join(s.get('name', '') for s in self.sources[:3])}")
            return "\n".join(sections)
        return self.text_ar
