"""
Configuration settings for Cyclone Tracker.

This module loads configuration from environment variables (.env file)
and provides a centralized Settings class with validation.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass


class Settings:
    """
    Centralized configuration settings.
    
    All settings are loaded from environment variables with sensible defaults.
    Validates critical settings on initialization.
    """
    
    def __init__(self):
        # API URLs
        self.WEATHER_API_URL = os.getenv(
            "WEATHER_API_URL",
            "https://api.open-meteo.com/v1/forecast"
        )
        self.MARINE_API_URL = os.getenv(
            "MARINE_API_URL",
            "https://marine-api.open-meteo.com/v1/marine"
        )
        
        # Network Settings
        self.TIMEOUT = int(os.getenv("TIMEOUT", "10"))
        self.RETRY_COUNT = int(os.getenv("RETRY_COUNT", "3"))
        self.RETRY_DELAY = int(os.getenv("RETRY_DELAY", "2"))
        self.MAX_RETRY_DELAY = int(os.getenv("MAX_RETRY_DELAY", "60"))
        
        # Cache Configuration
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
        self.CACHE_TTL = int(os.getenv("CACHE_TTL", "21600"))  # 6 hours
        self.CACHE_ENABLED = os.getenv("CACHE_ENABLED", "false").lower() == "true"
        
        # Cyclone Detection Thresholds
        self.CYCLONE_SST_THRESHOLD = float(os.getenv("CYCLONE_SST_THRESHOLD", "26.5"))
        self.CYCLONE_PRESSURE_THRESHOLD = float(os.getenv("CYCLONE_PRESSURE_THRESHOLD", "980"))
        self.CYCLONE_WIND_THRESHOLD = float(os.getenv("CYCLONE_WIND_THRESHOLD", "117"))
        
        self.STORM_PRESSURE_THRESHOLD = float(os.getenv("STORM_PRESSURE_THRESHOLD", "995"))
        self.STORM_WIND_THRESHOLD = float(os.getenv("STORM_WIND_THRESHOLD", "88"))
        
        self.DEPRESSION_PRESSURE_THRESHOLD = float(os.getenv("DEPRESSION_PRESSURE_THRESHOLD", "1000"))
        self.DEPRESSION_WIND_THRESHOLD = float(os.getenv("DEPRESSION_WIND_THRESHOLD", "62"))
        
        # Logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = os.getenv(
            "LOG_FORMAT",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.LOG_FILE = os.getenv("LOG_FILE", "logs/cyclone_tracker.log")
        self.LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
        self.LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
        
        # Validate configuration
        self.validate()
    
    def validate(self):
        """
        Validate critical configuration settings.
        
        Raises:
            ConfigurationError: If any setting is invalid
        """
        # Validate URLs
        if not self.WEATHER_API_URL.startswith("https://"):
            raise ConfigurationError(f"WEATHER_API_URL must start with https://, got: {self.WEATHER_API_URL}")
        
        if not self.MARINE_API_URL.startswith("https://"):
            raise ConfigurationError(f"MARINE_API_URL must start with https://, got: {self.MARINE_API_URL}")
        
        # Validate network settings
        if self.TIMEOUT <= 0:
            raise ConfigurationError(f"TIMEOUT must be > 0, got: {self.TIMEOUT}")
        
        if self.RETRY_COUNT < 0:
            raise ConfigurationError(f"RETRY_COUNT must be >= 0, got: {self.RETRY_COUNT}")
        
        # Validate thresholds
        if self.CYCLONE_SST_THRESHOLD <= 0 or self.CYCLONE_SST_THRESHOLD > 40:
            raise ConfigurationError(f"CYCLONE_SST_THRESHOLD must be between 0 and 40, got: {self.CYCLONE_SST_THRESHOLD}")
        
        if self.CYCLONE_PRESSURE_THRESHOLD <= 0 or self.CYCLONE_PRESSURE_THRESHOLD > 1100:
            raise ConfigurationError(f"CYCLONE_PRESSURE_THRESHOLD must be between 0 and 1100, got: {self.CYCLONE_PRESSURE_THRESHOLD}")
    
    def display(self):
        """
        Display configuration settings (masks sensitive values).
        """
        config_groups = {
            "API Configuration": [
                ("WEATHER_API_URL", self.WEATHER_API_URL),
                ("MARINE_API_URL", self.MARINE_API_URL),
            ],
            "Network Settings": [
                ("TIMEOUT", self.TIMEOUT),
                ("RETRY_COUNT", self.RETRY_COUNT),
                ("RETRY_DELAY", self.RETRY_DELAY),
                ("MAX_RETRY_DELAY", self.MAX_RETRY_DELAY),
            ],
            "Cache Configuration": [
                ("REDIS_HOST", self.REDIS_HOST),
                ("REDIS_PORT", self.REDIS_PORT),
                ("REDIS_PASSWORD", "****" if self.REDIS_PASSWORD else ""),
                ("CACHE_TTL", self.CACHE_TTL),
                ("CACHE_ENABLED", self.CACHE_ENABLED),
            ],
            "Cyclone Thresholds": [
                ("SST", f"{self.CYCLONE_SST_THRESHOLD}°C"),
                ("CYCLONE_PRESSURE", f"{self.CYCLONE_PRESSURE_THRESHOLD} hPa"),
                ("CYCLONE_WIND", f"{self.CYCLONE_WIND_THRESHOLD} km/h"),
                ("STORM_PRESSURE", f"{self.STORM_PRESSURE_THRESHOLD} hPa"),
                ("STORM_WIND", f"{self.STORM_WIND_THRESHOLD} km/h"),
            ],
            "Logging": [
                ("LOG_LEVEL", self.LOG_LEVEL),
                ("LOG_FILE", self.LOG_FILE),
            ],
        }
        
        print("\n" + "=" * 60)
        print("CYCLONE TRACKER CONFIGURATION")
        print("=" * 60)
        
        for group_name, settings in config_groups.items():
            print(f"\n{group_name}:")
            print("-" * 40)
            for key, value in settings:
                print(f"  {key:25} = {value}")
        
        print("\n" + "=" * 60 + "\n")


# Create global settings instance
settings = Settings()
