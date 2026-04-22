"""Serviço centralizado de acesso ao Supabase"""
from supabase import create_client
from app.config import get_settings
from functools import lru_cache

settings = get_settings()

@lru_cache()
def get_supabase_client():
    """Retorna cliente Supabase com service role."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

@lru_cache()
def get_supabase_anon():
    """Retorna cliente Supabase com anon key."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
