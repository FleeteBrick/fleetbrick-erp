"""
Rotas de Veículos com Validação de Limite de Plano
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from supabase import create_client

from app.config import get_settings
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/veiculos", tags=["Veículos"])


class VeiculoCreate(BaseModel):
    placa: str
    chassi: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    ano: Optional[int] = None
    cor: Optional[str] = None
    tipo_combustivel: Optional[str] = "flex"
    quilometragem_atual: Optional[int] = 0
    valor_fip: Optional[float] = None


class VeiculoUpdate(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    ano: Optional[int] = None
    cor: Optional[str] = None
    tipo_combustivel: Optional[str] = None
    quilometragem_atual: Optional[int] = None
    status: Optional[str] = None


class VeiculoResponse(BaseModel):
    id: str
    empresa_id: str
    placa: str
    chassi: Optional[str]
    marca: Optional[str]
    modelo: Optional[str]
    ano: Optional[int]
    cor: Optional[str]
    tipo_combustivel: Optional[str]
    quilometragem_atual: int
    status: str


@router.post("/", response_model=VeiculoResponse, status_code=status.HTTP_201_CREATED)
async def criar_veiculo(
    veiculo: VeiculoCreate,
    current_user: dict = Depends(get_current_user)
):
    """Cria veículo com validação de limite do plano"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user["empresa_id"]
    
    # Busca plano da empresa
    empresa = supabase.table("empresas").select("plano_id, status_assinatura").eq("id", empresa_id).single().execute()
    
    if not empresa.data:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    
    if empresa.data["status_assinatura"] not in ["ativa", "trial"]:
        raise HTTPException(status_code=402, detail="Assinatura inativa. Regularize o pagamento.")
    
    # Busca limites do plano
    plano = supabase.table("planos").select("*").eq("id", empresa.data["plano_id"]).single().execute()
    
    # Conta veículos atuais
    veiculos_count = supabase.table("veiculos").select("*", count="exact").eq("empresa_id", empresa_id).neq("status", "vendido").execute()
    veiculos_atuais = veiculos_count.count or 0
    
    # Valida limite
    if veiculos_atuais >= plano.data["max_veiculos"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Limite atingido! Plano '{plano.data['nome']}' permite máximo de {plano.data['max_veiculos']} veículos."
        )
    
    # Insere veículo
    veiculo_data = veiculo.model_dump()
    veiculo_data["empresa_id"] = empresa_id
    veiculo_data["placa"] = veiculo_data["placa"].upper().replace("-", "").replace(" ", "")
    
    result = supabase.table("veiculos").insert(veiculo_data).execute()
    
    return result.data[0]


@router.get("/", response_model=List[VeiculoResponse])
async def listar_veiculos(
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = None
):
    """Lista veículos da empresa"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user["empresa_id"]
    
    query = supabase.table("veiculos").select("*").eq("empresa_id", empresa_id)
    if status:
        query = query.eq("status", status)
    
    result = query.order("created_at", desc=True).execute()
    return result.data


@router.get("/{veiculo_id}", response_model=VeiculoResponse)
async def obter_veiculo(
    veiculo_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtém detalhes de um veículo"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user["empresa_id"]
    
    result = supabase.table("veiculos").select("*").eq("id", veiculo_id).eq("empresa_id", empresa_id).single().execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    return result.data


@router.put("/{veiculo_id}", response_model=VeiculoResponse)
async def atualizar_veiculo(
    veiculo_id: str,
    veiculo: VeiculoUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Atualiza veículo"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user["empresa_id"]
    
    update_data = {k: v for k, v in veiculo.model_dump().items() if v is not None}
    
    result = supabase.table("veiculos").update(update_data).eq("id", veiculo_id).eq("empresa_id", empresa_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    return result.data[0]


@router.delete("/{veiculo_id}")
async def deletar_veiculo(
    veiculo_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove veículo (soft delete)"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user["empresa_id"]
    
    result = supabase.table("veiculos").update({"status": "vendido"}).eq("id", veiculo_id).eq("empresa_id", empresa_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    return {"message": "Veículo removido com sucesso"}