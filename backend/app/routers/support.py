"""
Rotas de Suporte
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import BaseModel
from supabase import create_client

from app.config import get_settings
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/chamados", tags=["Suporte"])


class ChamadoCreate(BaseModel):
    tipo: str
    titulo: str
    descricao: str
    nivel_prioridade: str = "media"


class ChamadoUpdate(BaseModel):
    status: str = None
    resposta: str = None


class ChamadoResponse(BaseModel):
    id: str
    empresa_id: str
    tipo: str
    titulo: str
    descricao: str
    nivel_prioridade: str
    status: str
    categoria: str


@router.post("/", response_model=ChamadoResponse, status_code=status.HTTP_201_CREATED)
async def criar_chamado(
    chamado: ChamadoCreate,
    current_user: dict = Depends(get_current_user)
):
    """Cria novo chamado de suporte"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user.get("empresa_id")
    
    chamado_data = chamado.model_dump()
    if empresa_id:
        chamado_data["empresa_id"] = empresa_id
    if current_user.get("id"):
        chamado_data["usuario_id"] = current_user["id"]
    
    result = supabase.table("chamados_suporte").insert(chamado_data).execute()
    return result.data[0]


@router.get("/", response_model=List[ChamadoResponse])
async def listar_chamados(
    current_user: dict = Depends(get_current_user),
    status: str = None,
    tipo: str = None
):
    """Lista chamados"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user.get("empresa_id")
    
    query = supabase.table("chamados_suporte").select("*")
    
    # Super admin vê todos, outros veem apenas os da empresa
    if current_user.get("nivel_acesso") != "super_admin":
        query = query.eq("empresa_id", empresa_id)
    
    if status:
        query = query.eq("status", status)
    if tipo:
        query = query.eq("tipo", tipo)
    
    result = query.order("created_at", desc=True).execute()
    return result.data


@router.get("/{chamado_id}", response_model=ChamadoResponse)
async def obter_chamado(
    chamado_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtém chamado específico"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user.get("empresa_id")
    
    result = supabase.table("chamados_suporte").select("*").eq("id", chamado_id).single().execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    
    return result.data


@router.put("/{chamado_id}", response_model=ChamadoResponse)
async def atualizar_chamado(
    chamado_id: str,
    chamado: ChamadoUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Atualiza chamado (responder)"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    
    update_data = {k: v for k, v in chamado.model_dump().items() if v is not None}
    if current_user.get("nivel_acesso") in ["super_admin", "tenant_admin"]:
        update_data["resolvido_por"] = current_user.get("id")
    
    result = supabase.table("chamados_suporte").update(update_data).eq("id", chamado_id).execute()
    
    return result.data[0]