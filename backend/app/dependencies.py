"""
Dependências do FastAPI
"""
from fastapi import Header, HTTPException
from typing import Optional
from supabase import create_client
from app.config import get_settings


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Valida token JWT e retorna usuário"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    
    try:
        token = authorization.replace("Bearer ", "")
        user = supabase.auth.get_user(token)
        
        if not user.user:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        # Busca dados do usuário no banco
        usuario = supabase.table("usuarios").select("*").eq("id", user.user.id).single().execute()
        
        if not usuario.data:
            return {"id": user.user.id, "email": user.user.email, "nivel_acesso": "end_user"}
        
        return usuario.data
    
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Erro na autenticação: {str(e)}")


async def require_tenant_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Requer nível de acesso tenant_admin"""
    if current_user.get("nivel_acesso") not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return current_user


async def require_super_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Requer nível de acesso super_admin"""
    if current_user.get("nivel_acesso") != "super_admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a super administradores")
    return current_user