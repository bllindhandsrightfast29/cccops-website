"""
Configuration module for different environments
"""

import os
from typing import Optional


class Config:
    """Base configuration"""

    # API Configuration
    API_TITLE = "Triple C Contact API"
    API_VERSION = "1.0.0"

    # Security
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "change-in-production")

    # CORS
    ALLOWED_ORIGINS = [
        "https://cccops.com",
        "https://www.cccops.com",
    ]

    # Rate Limiting
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "5"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "3600"))

    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", "contact_submissions.db")

    # SMTP Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", os.getenv("SMTP_USER", ""))
    OWNER_EMAIL: str = os.getenv("OWNER_EMAIL", "consultingbytriplec@gmail.com")

    # Application
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ALLOWED_ORIGINS = Config.ALLOWED_ORIGINS + [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    DATABASE_PATH = "test_contact_submissions.db"
    RATE_LIMIT_REQUESTS = 100  # Higher limit for testing


def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv("ENV", "development").lower()

    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }

    return config_map.get(env, DevelopmentConfig)()


# Export current config
config = get_config()
