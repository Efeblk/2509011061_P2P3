"""
Configuration module for EventGraph application.
Loads settings from environment variables with type validation.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class FalkorDBSettings(BaseSettings):
    """FalkorDB database configuration."""

    host: str = Field(default="localhost", alias="FALKORDB_HOST")
    port: int = Field(default=6379, alias="FALKORDB_PORT")
    password: Optional[str] = Field(default=None, alias="FALKORDB_PASSWORD")
    db: int = Field(default=0, alias="FALKORDB_DB")
    graph_name: str = Field(default="eventgraph", alias="FALKORDB_GRAPH_NAME")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def connection_string(self) -> str:
        """Generate Redis connection string."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class GeminiSettings(BaseSettings):
    """Google Gemini API configuration."""

    api_key: str = Field(..., alias="GEMINI_API_KEY")
    model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class OllamaSettings(BaseSettings):
    """Local Ollama configuration."""

    base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    model: str = Field(default="llama3.2", alias="OLLAMA_MODEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class ScrapySettings(BaseSettings):
    """Web scraping configuration."""

    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        alias="SCRAPY_USER_AGENT"
    )
    concurrent_requests: int = Field(default=16, alias="SCRAPY_CONCURRENT_REQUESTS")
    download_delay: float = Field(default=1.0, alias="SCRAPY_DOWNLOAD_DELAY")
    playwright_headless: bool = Field(default=True, alias="PLAYWRIGHT_HEADLESS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class AISettings(BaseSettings):
    """AI analysis configuration."""

    batch_size: int = Field(default=10, alias="AI_BATCH_SIZE")
    rate_limit_delay: float = Field(default=1.0, alias="AI_RATE_LIMIT_DELAY")
    max_retries: int = Field(default=3, alias="AI_MAX_RETRIES")
    cache_enabled: bool = Field(default=True, alias="AI_CACHE_ENABLED")
    enable_embeddings: bool = Field(default=False, alias="AI_ENABLE_EMBEDDINGS")
    
    # Provider selection: "gemini" or "ollama"
    provider: str = Field(default="gemini", alias="AI_PROVIDER")

    # Models
    model_fast: str = Field(default="llama3.2", alias="AI_MODEL_FAST")
    model_reasoning: str = Field(default="gemini-3.0-pro", alias="AI_MODEL_REASONING")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class AppSettings(BaseSettings):
    """General application configuration."""

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="logs/eventgraph.log", alias="LOG_FILE")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # Pipeline settings
    enable_ai_enrichment: bool = Field(default=True, alias="ENABLE_AI_ENRICHMENT")
    enable_duplicate_detection: bool = Field(default=True, alias="ENABLE_DUPLICATE_DETECTION")
    min_event_price: float = Field(default=0.0, alias="MIN_EVENT_PRICE")
    max_event_price: float = Field(default=10000.0, alias="MAX_EVENT_PRICE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()

    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment."""
        allowed = ["development", "staging", "production"]
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v.lower()

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


class Settings:
    """
    Main settings class that aggregates all configuration sections.
    Implements Singleton pattern to ensure single instance.
    """

    _instance: Optional["Settings"] = None

    def __new__(cls):
        """Ensure only one instance exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize settings only once."""
        if self._initialized:
            return

        self.falkordb = FalkorDBSettings()
        self.gemini = GeminiSettings()
        self.ollama = OllamaSettings()
        self.scrapy = ScrapySettings()
        self.ai = AISettings()
        self.app = AppSettings()

        self._initialized = True

    def reload(self):
        """Reload all settings from environment."""
        self.falkordb = FalkorDBSettings()
        self.gemini = GeminiSettings()
        self.ollama = OllamaSettings()
        self.scrapy = ScrapySettings()
        self.ai = AISettings()
        self.app = AppSettings()


# Global settings instance
settings = Settings()
