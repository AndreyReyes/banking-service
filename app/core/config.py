from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    app_env: str = "dev"
    database_url: str = "sqlite:///./banking.db"
    log_level: str = "INFO"
    auto_migrate: bool = False
    jwt_secret: str = "dev_insecure_secret_change_me"
    jwt_issuer: str = "banking-service"
    jwt_audience: str = "banking-service"
    access_token_ttl_minutes: int = 30
    refresh_token_ttl_days: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
    )

    @model_validator(mode="after")
    def validate_jwt_secret(self) -> "AppSettings":
        env = self.app_env.lower()
        if env in {"prod", "production"}:
            if self.jwt_secret == "dev_insecure_secret_change_me":
                raise ValueError("jwt_secret must be set in production")
            if self.auto_migrate:
                raise ValueError("auto_migrate must be disabled in production")
        if env in {"dev", "development"} and "auto_migrate" not in self.model_fields_set:
            object.__setattr__(self, "auto_migrate", True)
        return self


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
