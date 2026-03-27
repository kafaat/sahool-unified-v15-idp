"""Channel Normalizer — تطبيع رسائل القنوات"""

from .models import ChannelMessage, ChannelType


class ChannelNormalizer:
    @staticmethod
    def normalize_whatsapp(raw: dict) -> ChannelMessage:
        return ChannelMessage(
            text=raw.get("text", raw.get("body", "")),
            channel=ChannelType.WHATSAPP,
            sender_id=raw.get("from", raw.get("sender", "")),
            language="ar" if any("\u0600" <= c <= "\u06ff" for c in raw.get("text", "")) else "en",
            image=raw.get("image"),
            location=raw.get("location"),
            metadata={"message_id": raw.get("id", ""), "profile_name": raw.get("profile", {}).get("name", "")},
        )

    @staticmethod
    def normalize_ussd(raw: dict) -> ChannelMessage:
        return ChannelMessage(
            text=raw.get("text", ""),
            channel=ChannelType.USSD,
            sender_id=raw.get("phone", raw.get("msisdn", "")),
            language="ar",
            metadata={"session_id": raw.get("session_id", "")},
        )

    @staticmethod
    def normalize_web(raw: dict) -> ChannelMessage:
        return ChannelMessage(
            text=raw.get("message", raw.get("query", "")),
            channel=ChannelType.WEB,
            sender_id=raw.get("user_id", ""),
            tenant_id=raw.get("tenant_id"),
            field_id=raw.get("field_id"),
            language=raw.get("language", "ar"),
            metadata=raw.get("metadata", {}),
        )

    @staticmethod
    def normalize(raw: dict, channel: ChannelType) -> ChannelMessage:
        normalizers = {
            ChannelType.WHATSAPP: ChannelNormalizer.normalize_whatsapp,
            ChannelType.USSD: ChannelNormalizer.normalize_ussd,
            ChannelType.WEB: ChannelNormalizer.normalize_web,
            ChannelType.WECHAT: ChannelNormalizer.normalize_web,  # WeChat uses similar format
            ChannelType.MOBILE: ChannelNormalizer.normalize_web,
        }
        normalizer = normalizers.get(channel, ChannelNormalizer.normalize_web)
        return normalizer(raw)
