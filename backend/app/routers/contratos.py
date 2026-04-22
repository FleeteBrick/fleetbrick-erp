"""
Rotas de Contratos de Locação
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from supabase import create_client
from datetime import date

from app.config import get_settings
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/contratos", tags=["Contratos"])


class ContratoCreate(BaseModel):
    propriedade_id: str
    inquilino_nome: str
    inquilino_cpf: Optional[str] = None
    inquilino_email: Optional[str] = None
    inquilino_telefone: Optional[str] = None
    data_entrada: date
    data_inicio_contrato: date
    data_fim_contrato: Optional[date] = None
    valor_aluguel: float
    dia_vencimento: int


class ContratoUpdate(BaseModel):
    status: Optional[str] = None
    data_fim_contrato: Optional[date] = None


class ContratoResponse(BaseModel):
    id: str
    empresa_id: str
    propriedade_id: str
    inquilino_nome: str
    data_entrada: str
    data_inicio_contrato: str
    valor_aluguel: float
    dia_vencimento: int
    status: str


@router.post("/", response_model=ContratoResponse, status_code=status.HTTP_201_CREATED)
async def criar_contrato(
    contrato: ContratoCreate,
    current_user: dict = Depends(get_current_user)
):
    """Cria contrato de locação"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user["empresa_id"]
    
    contrato_data = contrato.model_dump()
    contrato_data["empresa_id"] = empresa_id
    
    result = supabase.table("contratos_locacao").insert(contrato_data).execute()
    return result.data[0]


@router.get("/", response_model=List[ContratoResponse])
async def listar_contratos(
    current_user: dict = Depends(get_current_user),
    propriedade_id: Optional[str] = None,
    status: Optional[str] = None
):
    """Lista contratos"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user["empresa_id"]
    
    query = supabase.table("contratos_locacao").select("*").eq("empresa_id", empresa_id)
    if propriedade_id:
        query = query.eq("propriedade_id", propriedade_id)
    if status:
        query = query.eq("status", status)
    
    result = query.order("created_at", desc=True).execute()
    return result.data


@router.get("/{contrato_id}", response_model=ContratoResponse)
async def obter_contrato(
    contrato_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtém contrato"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user["empresa_id"]
    
    result = supabase.table("contratos_locacao").select("*").eq("id", contrato_id).eq("empresa_id", empresa_id).single().execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    
    return result.data


@router.put("/{contrato_id}", response_model=ContratoResponse)
async def atualizar_contrato(
    contrato_id: str,
    contrato: ContratoUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Atualiza contrato"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user["empresa_id"]
    
    update_data = {k: v for k, v in contrato.model_dump().items() if v is not None}
    
    result = supabase.table("contratos_locacao").update(update_data).eq("id", contrato_id).eq("empresa_id", empresa_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    
    return result.data[0]