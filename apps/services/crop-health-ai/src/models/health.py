"""
Sahool Vision - Health Check Models
نماذج فحص الصحة
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    """استجابة فحص الصحة"""
    status: str
    service: str
    version: str
    model_loaded: bool
    model_type: Optional[str] = None  # 'tflite', 'keras', 'mock'
    is_real_model: bool = False
    timestamp: datetime
