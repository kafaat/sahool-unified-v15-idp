"""
USSD Gateway API v1
"""

from fastapi import APIRouter

router = APIRouter(tags=["ussd-gateway"])


@router.get("/status")
async def get_service_status():
    """Get USSD gateway service status"""
    return {
        "service": "ussd-gateway",
        "version": "16.0.0",
        "providers": {
            "sms": "unifonic",
            "ussd": "africa_talking",
            "whatsapp": "meta_business",
        },
        "supported_features": [
            "ussd_menus",
            "sms_keywords",
            "sms_alerts",
            "whatsapp_messages",
            "whatsapp_buttons",
        ],
    }


@router.get("/menus")
async def get_ussd_menus():
    """Get available USSD menu structure"""
    from ..main import USSD_MENUS
    return USSD_MENUS


@router.get("/keywords")
async def get_sms_keywords():
    """Get supported SMS keywords"""
    return {
        "weather": ["WEATHER", "طقس", "RAIN", "مطر"],
        "field": ["FIELD", "حقل", "NDVI"],
        "irrigation": ["WATER", "ماء", "ري"],
        "prices": ["PRICE", "سعر"],
        "help": ["HELP", "مساعدة"],
        "registration": ["REGISTER", "تسجيل"],
    }
