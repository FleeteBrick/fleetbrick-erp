"""Dependências de autenticação e autorização"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from supabase import create_client
from app.config import get_settings

settings = get_settings()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Valida JWT e retorna usuário atual com contexto de empresa."""
    token = credentials.credentials

    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

        # Verifica sessão no Supabase
        user = supabase.auth.get_user(token)
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )

        # Busca dados do usuário no banco
        usuario = supabase.table("usuarios").select("*").eq("id", user.user.id).single().execute()

        if not usuario.data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário não encontrado no sistema"
            )

        return {
            "id": user.user.id,
            "email": user.user.email,
            "empresa_id": usuario.data["empresa_id"],
            "nivel_acesso": usuario.data["nivel_acesso"],
            "nome": usuario.data["nome"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Erro de autenticação: {str(e)}"
        )


def require_nivel_acesso(*niveis_permitidos: str):
    """Decorator para restringir acesso por nível."""
    async def checker(current_user: dict = Depends(get_current_user)):
        if current_user["nivel_acesso"] not in niveis_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso restrito. Necessário: {', '.join(niveis_permitidos)}"
            )
        return current_user
    return checker


require_super_admin = require_nivel_acesso("super_admin")
require_tenant_admin = require_nivel_acesso("super_admin", "tenant_admin", "manager")
