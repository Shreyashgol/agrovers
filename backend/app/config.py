"""
Configuration management for Argovers Soil Assistant.

This module loads settings from environment variables and provides
a centralized configuration object.

To modify:
- LLM provider: Change `llm_provider` and add corresponding API key
- n8n webhook: Set `N8N_WEBHOOK_URL` in .env
- Parameter list: Modify `PARAMETER_ORDER` in orchestrator.py
- Knowledge base paths: Update `kb_raw_dir`, `kb_processed_dir`, `embeddings_dir`
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Literal
import json
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_ignore_empty=True,
        extra="ignore",  # Ignore extra fields from env file
    )
    
    app_name: str = "Argovers Soil Assistant"
    
    # LLM Configuration
    gemini_api_key: str | None = None
    gemini_model_name: str = "gemini-1.5-flash"  # Using flash for faster responses
    llm_provider: Literal["gemini", "ollama", "local"] = "gemini"  # Support for Ollama and local models
    ollama_model_name: str = "phi3"  # Ollama model to use (phi3, mistral, llama2, etc.)
    
    # ASR/TTS Configuration
    groq_api_key: str | None = None
    asr_provider: Literal["groq", "local_whisper", "openai"] = "groq"
    tts_provider: Literal["gtts", "coqui", "openai"] = "gtts"
    
    # Embeddings Configuration
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    hf_token: str | None = None  # Hugging Face token for private models
    
    # n8n Integration
    n8n_webhook_url: str | None = None
    
    # Knowledge Base Paths (relative to backend/ directory)
    kb_raw_dir: str = "app/data/kb_raw"
    kb_processed_dir: str = "app/data/kb_processed"
    embeddings_dir: str = "app/data/embeddings"
    
    # API Configuration - use private field name to avoid env parsing
    _allowed_origins: list[str] | None = None
    
    # Session Configuration
    session_timeout_seconds: int = 3600  # 1 hour
    
    def __init__(self, **kwargs):
        # Get ALLOWED_ORIGINS from environment before calling super
        allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
        
        # Remove from kwargs to prevent pydantic from trying to parse it
        kwargs.pop("allowed_origins", None)
        kwargs.pop("ALLOWED_ORIGINS", None)
        
        super().__init__(**kwargs)
        
        # Parse allowed_origins after super().__init__
        if allowed_origins_env and isinstance(allowed_origins_env, str):
            # Try to parse as JSON first
            try:
                parsed = json.loads(allowed_origins_env)
                if isinstance(parsed, list):
                    object.__setattr__(self, "_allowed_origins", parsed)
                    return
            except (json.JSONDecodeError, TypeError):
                pass
            
            # If not JSON, try comma-separated string
            if allowed_origins_env.strip():
                origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
                if origins:
                    object.__setattr__(self, "_allowed_origins", origins)
                    return
        
        # Use default if not set
        if self._allowed_origins is None:
            object.__setattr__(
                self,
                "_allowed_origins",
                [
                    "http://localhost:5173",  # Vite default
                    "http://localhost:3000",  # Alternative frontend port
                ]
            )
    
    @property
    def allowed_origins(self) -> list[str]:
        """Get allowed origins list."""
        if self._allowed_origins is None:
            return [
                "http://localhost:5173",
                "http://localhost:3000",
            ]
        return self._allowed_origins


# Global settings instance
settings = Settings()

