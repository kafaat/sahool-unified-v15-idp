"""
Configuration settings for Code Review Service
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Ollama Configuration
    ollama_url: str = "http://ollama:11434"
    ollama_model: str = "deepseek"
    
    # Watch Configuration
    watch_paths: str = "infrastructure:docker-compose.yml:docker"
    review_on_change: bool = True
    max_file_size: int = 1000000  # 1MB
    
    # API Server Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8096
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

