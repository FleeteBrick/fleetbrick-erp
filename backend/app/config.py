"""Configurações da aplicação"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações carregadas de variáveis de ambiente."""

    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str

    # Asaas
    ASAAS_API_KEY: str
    ASAAS_API_URL: str = "https://api.asaas.com/v3"

    # Resend
    RESEND_API_KEY: str
    RESEND_FROM_EMAIL: str = "fleetebrick@gmail.com"

    # App
    APP_SECRET_KEY: str
    APP_ENV: str = "development"
    APP_URL: str = "http://localhost:3000"

    # OpenClaw
    OPENCLAW_API_KEY: str | None = None

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
