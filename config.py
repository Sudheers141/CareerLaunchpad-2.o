# config.py
import os

class Config:
    """Base configuration with common settings."""
    # General settings
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1")
    TESTING = os.getenv("TESTING", "False").lower() in ("true", "1")
    FLASK_ENV = os.getenv("FLASK_ENV", "development").lower()
    
    # API Keys
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_API_KEY_NEW = os.getenv("NVIDIA_API_KEY_NEW", "")

    # Database
    DB_PATH = os.getenv("DB_PATH", "career_launchpad.db")

    # Logging level
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    DB_PATH = os.getenv("DEV_DB_PATH", "dev_career_launchpad.db")

class TestingConfig(Config):
    """Testing-specific configuration."""
    TESTING = True
    LOG_LEVEL = "DEBUG"
    DB_PATH = os.getenv("TEST_DB_PATH", "test_career_launchpad.db")

class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = "WARNING"
    DB_PATH = os.getenv("PROD_DB_PATH", "prod_career_launchpad.db")

def get_config():
    """Retrieve the correct config based on the FLASK_ENV environment variable."""
    env = os.getenv("FLASK_ENV", "development").lower()
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    return DevelopmentConfig()
