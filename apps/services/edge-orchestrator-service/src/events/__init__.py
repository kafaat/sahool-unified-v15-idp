# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""Events module for Edge Orchestrator Service."""

from .websocket import WebSocketManager, get_websocket_manager

__all__ = ["WebSocketManager", "get_websocket_manager"]
