"""
Settings configuration class for the ACKO AI Native Insurance Platform.
Uses Pydantic Settings (Pydantic v2) to parse and validate environment variables.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve the absolute path of the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Application Settings class. Reads from environment variables or .env file.
    Validates port ranges, environments, and logs warnings for missing critical keys.
    """
    model_config = SettingsConfigDict(
        env_file=os.path.join(PROJECT_ROOT, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Application Environment Settings ──────────────────────────────────────
    APP_ENV: str = Field(default="development", description="Application runtime environment: development, testing, or production")
    LOG_LEVEL: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    SECRET_KEY: str = Field(default="SECRET_KEY_PLACEHOLDER_MIN_32_CHARACTERS_ACKO_AI", description="Secret key for session encryption and signing")

    # ── PostgreSQL Database Settings ──────────────────────────────────────────
    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL host URL/IP")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL Port")
    POSTGRES_DB: str = Field(default="acko_insurance_db", description="Database name")
    POSTGRES_USER: str = Field(default="acko_user", description="Database username")
    POSTGRES_PASSWORD: str = Field(default="acko_password", description="Database password")

    # ── AI Model & Vector DB Settings ─────────────────────────────────────────
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini LLM API Key")
    CHROMA_DB_PATH: str = Field(default="./chroma_db", description="Local filepath for ChromaDB index")

    # ── AWS S3 Assets Settings ────────────────────────────────────────────────
    AWS_ACCESS_KEY_ID: str = Field(default="", description="AWS Access Key ID for S3")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", description="AWS Secret Access Key for S3")
    AWS_REGION: str = Field(default="ap-south-1", description="AWS operational region")
    AWS_BUCKET_NAME: str = Field(default="acko-insurance-assets", description="AWS S3 Bucket name")

    @field_validator("POSTGRES_PORT")
    @classmethod
    def validate_postgres_port(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError(f"POSTGRES_PORT must be in range 1-65535, received: {v}")
        return v

    @field_validator("APP_ENV")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        valid_envs = ["development", "testing", "production"]
        val_lower = v.lower()
        if val_lower not in valid_envs:
            raise ValueError(f"APP_ENV must be one of {valid_envs}, received: {v}")
        return val_lower

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        val_upper = v.upper()
        if val_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}, received: {v}")
        return val_upper

    def get_missing_keys(self) -> List[str]:
        """
        Scans settings configuration for default placeholder values or empty values.
        Returns a list of keys that must be properly set in production.
        """
        missing = []
        # Check for empty Gemini Key
        if not self.GEMINI_API_KEY or "your_gemini_api_key_here" in self.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        # Check AWS credentials
        if not self.AWS_ACCESS_KEY_ID or "your_aws_access_key_id_here" in self.AWS_ACCESS_KEY_ID:
            missing.append("AWS_ACCESS_KEY_ID")
        if not self.AWS_SECRET_ACCESS_KEY or "your_aws_secret_access_key_here" in self.AWS_SECRET_ACCESS_KEY:
            missing.append("AWS_SECRET_ACCESS_KEY")
        # Check for default secrets
        if "PLACEHOLDER" in self.SECRET_KEY or self.SECRET_KEY == "your_secret_key_minimum_32_characters_here":
            missing.append("SECRET_KEY (weak or placeholder key)")
        
        return missing


# Expose configuration instance
try:
    settings = Settings()
    # Log warning if missing key is detected
    missing_config = settings.get_missing_keys()
    if missing_config:
        print(
            f"WARNING (Settings): The following critical environment details are not configured "
            f"or contain default values: {', '.join(missing_config)}. "
            f"Please populate these in your local '.env' file prior to deploying in production.",
            file=sys.stderr
        )
except Exception as e:
    print(f"CRITICAL: Failed to load application configuration. Details: {e}", file=sys.stderr)
    raise e
