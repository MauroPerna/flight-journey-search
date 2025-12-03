from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[3] / ".env"  # noqa: E402
load_dotenv(dotenv_path=ENV_PATH)  # noqa: E402

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Literal
from enum import Enum
import logging


logger = logging.getLogger(__name__)


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    # ============= APPLICATION =============
    app_name: str = Field(default="Journey Search")
    app_version: str = Field(default="1.0.0")
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)

    # ============= API =============
    api_prefix: str = Field(default="/api")
    api_v1_prefix: str = Field(default="/api/v1")

    # ============= LOGGING =============
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # ============= CORS =============
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000"
    )
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: List[str] = Field(default=["*"])
    cors_allow_headers: List[str] = Field(default=["*"])

    # ============= COMPUTED PROPERTIES =============
    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        return self.environment == Environment.TESTING

    # ============= VALIDATORS =============
    def get_logging_config(self) -> dict:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.log_format
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": self.log_level,
                }
            },
            "root": {
                "level": self.log_level,
                "handlers": ["console"]
            },
            "loggers": {
                "uvicorn": {
                    "level": self.log_level,
                    "handlers": ["console"],
                    "propagate": False
                }
            }
        }


settings = Settings()
