"""
Multi-Channel Adapter — محوّل القنوات المتعددة
Normalizes messages from WhatsApp, USSD, WeChat, Web into unified format.
Phase 2 of Component Unification Plan (PR #1344)
"""
from .models import ChannelMessage, ChannelResponse, ChannelType
from .normalizer import ChannelNormalizer
