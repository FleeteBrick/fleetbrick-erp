"""
Rotas de Propriedades (Imóveis)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from supabase import create_client

from app.config import get_settings
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/propriedades", tags=["Propriedades"])


class PropriedadeCreate(BaseModel):
    codigo_interno: Optional[str] = None
    endereco: str
    cep: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    tipo: str
    valor_aluguel: Optional[float] = None
    valor_condominio: Optional[float] = None
    area_m2: Optional[float] = None
    quartos: Optional[int] = None
    banheiros: Optional[int] = None
    vagas_garagem: Optional[int] = None
    descricao: Optional[str] = None


class PropriedadeUpdate(BaseModel):
    codigo_interno: Optional[str] = None
    endereco: Optional[str] = None
    cep: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    tipo: Optional[str] = None
    status: Optional[str] = None
    valor_aluguel: Optional[float] = None
    valor_condominio: Optional[float] = None
    area_m2: Optional[float] = None
    quartos: Optional[int] = None
    banheiros: Optional[int] = None
    vagas_garagem: Optional[int] = None
    descricao: Optional[str] = None


class PropriedadeResponse(BaseModel):
    id: str
    empresa_id: str
    codigo_interno: Optional[str]
    endereco: str
    cidade: Optional[str]
    estado: Optional[str]
    tipo: str
    status: str
    valor_aluguel: Optional[float]


@router.post("/", response_model=PropriedadeResponse, status_code=status.HTTP_201_CREATED)
async def criar_propriedade(
    propriedade: PropriedadeCreate,
    current_user: dict = Depends(get_current_user)
):
    """Cria propriedade com validação de limite do plano"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user["empresa_id"]
    
    # Busca plano da empresa
    empresa = supabase.table("empresas").select("plano_id, status_assinatura").eq("id", empresa_id).single().execute()
    
    if empresa.data["status_assinatura"] not in ["ativa", "trial"]:
        raise HTTPException(status_code=402, detail="Assinatura inativa")
    
    # Conta imóveis atuais
    imoveis_count = supabase.table("propriedades").select("*", count="exact").eq("empresa_id", empresa_id).neq("status", "vendido").execute()
    imoveis_atuais = imoveis_count.count or 0
    
    plano = supabase.table("planos").select("max_imoveis, nome").eq("id", empresa.data["plano_id"]).single().execute()
    
    if imoveis_atuais >= plano.data["max_imoveis"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Limite atingido! Plano '{plano.data['nome']}' permite máximo de {plano.data['max_imoveis']} imóveis."
        )
    
    prop_data = propriedade.model_dump()
    prop_data["empresa_id"] = empresa_id
    
    result = supabase.table("propriedades").insert(prop_data).execute()
    return result.data[0]


@router.get("/", response_model=List[PropriedadeResponse])
async def listar_propriedades(
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = None,
    tipo: Optional[str] = None
):
    """Lista propriedades"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user["empresa_id"]
    
    query = supabase.table("propriedades").select("*").eq("empresa_id", empresa_id)
    if status:
        query = query.eq("status", status)
    if tipo:
        query = query.eq("tipo", tipo)
    
    result = query.order("created_at", desc=True).execute()
    return result.data


@router.get("/{propriedade_id}", response_model=PropriedadeResponse)
async def obter_propriedade(
    propriedade_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtém detalhes de uma propriedade"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user["empresa_id"]
    
    result = supabase.table("propriedades").select("*").eq("id", propriedade_id).eq("empresa_id", empresa_id).single().execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada")
    
    return result.data


@router.put("/{propriedade_id}", response_model=PropriedadeResponse)
async def atualizar_propriedade(
    propriedades_id: str,
    propriedade: PropriedadeUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Atualiza propriedade"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user["empresa_id"]
    
    update_data = {k: v for k, v in propriedade.model_dump().items() if v is not None}
    
    result = supabase.table("propriedades").update(update_data).eq("id", propriedades_id).eq("empresa_id", empresa_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada")
    
    return result.data[0]