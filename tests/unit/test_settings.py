"""
Unit tests for configuration settings.
"""

import pytest
import os
from config.settings import (
    FalkorDBSettings,
    GeminiSettings,
    ScrapySettings,
    AISettings,
    AppSettings,
    Settings
)


@pytest.mark.unit
class TestFalkorDBSettings:
    """Test FalkorDB configuration."""

    def test_default_values(self):
        """Test default configuration values."""
        settings = FalkorDBSettings()
        assert settings.host == "localhost"
        assert settings.port == 6379
        assert settings.db == 0
        assert settings.graph_name == "eventgraph"

    def test_connection_string_without_password(self):
        """Test connection string generation without password."""
        settings = FalkorDBSettings(password=None)
        expected = "redis://localhost:6379/0"
        assert settings.connection_string == expected

    def test_connection_string_with_password(self):
        """Test connection string generation with password."""
        settings = FalkorDBSettings(password="secret123")
        expected = "redis://:secret123@localhost:6379/0"
        assert settings.connection_string == expected


@pytest.mark.unit
class TestAppSettings:
    """Test application configuration."""

    def test_log_level_validation(self):
        """Test log level validation."""
        valid_settings = AppSettings(log_level="DEBUG")
        assert valid_settings.log_level == "DEBUG"

    def test_environment_validation(self):
        """Test environment validation."""
        valid_settings = AppSettings(environment="production")
        assert valid_settings.environment == "production"

    def test_is_development_property(self):
        """Test is_development property."""
        dev_settings = AppSettings(environment="development")
        assert dev_settings.is_development is True

        prod_settings = AppSettings(environment="production")
        assert prod_settings.is_development is False

    def test_is_production_property(self):
        """Test is_production property."""
        prod_settings = AppSettings(environment="production")
        assert prod_settings.is_production is True

        dev_settings = AppSettings(environment="development")
        assert dev_settings.is_production is False


@pytest.mark.unit
class TestSettings:
    """Test main Settings class."""

    def test_singleton_pattern(self):
        """Test that Settings implements Singleton pattern."""
        settings1 = Settings()
        settings2 = Settings()

        assert settings1 is settings2, "Settings should return same instance"

    def test_settings_aggregation(self):
        """Test that Settings aggregates all configuration sections."""
        settings = Settings()

        assert hasattr(settings, "falkordb")
        assert hasattr(settings, "gemini")
        assert hasattr(settings, "scrapy")
        assert hasattr(settings, "ai")
        assert hasattr(settings, "app")

        assert isinstance(settings.falkordb, FalkorDBSettings)
        assert isinstance(settings.gemini, GeminiSettings)
        assert isinstance(settings.scrapy, ScrapySettings)
        assert isinstance(settings.ai, AISettings)
        assert isinstance(settings.app, AppSettings)
