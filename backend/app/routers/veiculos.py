"""Rotas de veículos com validação de limite do plano"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from supabase import create_client

from app.config import get_settings
from app.schemas import VeiculoCreate, VeiculoUpdate, VeiculoResponse
from app.dependencies import get_current_user, require_tenant_admin

router = APIRouter(prefix="/veiculos", tags=["Veículos"])
settings = get_settings()


@router.post("/novo", response_model=VeiculoResponse, status_code=status.HTTP_201_CREATED)
async def criar_veiculo(
    veiculo: VeiculoCreate,
    current_user: dict = Depends(require_tenant_admin)
):
    """
    Cria novo veículo com validação rigorosa de limite do plano.
    Bloqueia inserção se max_veiculos do plano foi atingido.
    """
    empresa_id = current_user["empresa_id"]
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    # 1. Busca plano da empresa
    empresa = supabase.table("empresas").select("plano_id, status_assinatura").eq("id", empresa_id).single().execute()

    if not empresa.data:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    if empresa.data["status_assinatura"] not in ["ativa", "trial"]:
        raise HTTPException(status_code=402, detail="Assinatura inativa")

    plano = supabase.table("planos").select("*").eq("id", empresa.data["plano_id"]).single().execute()

    # 2. Conta veículos atuais
    veiculos_count = supabase.table("veiculos").select("*", count="exact").eq("empresa_id", empresa_id).neq("status", "vendido").execute()
    veiculos_atuais = veiculos_count.count or 0

    # 3. Valida limite
    if veiculos_atuais >= plano.data["max_veiculos"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Limite atingido. Plano '{plano.data['nome']}': {plano.data['max_veiculos']} veículos."
        )

    # 4. Insere veículo
    veiculo_data = veiculo.model_dump()
    veiculo_data["empresa_id"] = empresa_id
    veiculo_data["placa"] = veiculo_data["placa"].upper().replace("-", "")

    result = supabase.table("veiculos").insert(veiculo_data).execute()

    # 5. Alerta de proximidade (80%)
    percentual = (veiculos_atuais + 1) / plano.data["max_veiculos"]
    if percentual >= 0.8:
        # TODO: Enviar notificação
        pass

    return result.data[0]


@router.get("/", response_model=List[VeiculoResponse])
async def listar_veiculos(
    current_user: dict = Depends(get_current_user),
    status: str = None
):
    """Lista veículos do tenant."""
    empresa_id = current_user["empresa_id"]
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    query = supabase.table("veiculos").select("*").eq("empresa_id", empresa_id)
    if status:
        query = query.eq("status", status)

    result = query.order("created_at", desc=True).execute()
    return result.data


@router.get("/{veiculo_id}", response_model=VeiculoResponse)
async def obter_veiculo(
    veiculo_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Obtém detalhes de um veículo."""
    empresa_id = current_user["empresa_id"]
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    result = supabase.table("veiculos").select("*").eq("id", str(veiculo_id)).eq("empresa_id", empresa_id).single().execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    return result.data


@router.put("/{veiculo_id}", response_model=VeiculoResponse)
async def atualizar_veiculo(
    veiculo_id: UUID,
    veiculo: VeiculoUpdate,
    current_user: dict = Depends(require_tenant_admin)
):
    """Atualiza dados do veículo."""
    empresa_id = current_user["empresa_id"]
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    update_data = {k: v for k, v in veiculo.model_dump().items() if v is not None}

    result = supabase.table("veiculos").update(update_data).eq("id", str(veiculo_id)).eq("empresa_id", empresa_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    return result.data[0]


@router.delete("/{veiculo_id}")
async def deletar_veiculo(
    veiculo_id: UUID,
    current_user: dict = Depends(require_tenant_admin)
):
    """Remove veículo (soft delete)."""
    empresa_id = current_user["empresa_id"]
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    result = supabase.table("veiculos").update({"status": "vendido"}).eq("id", str(veiculo_id)).eq("empresa_id", empresa_id).execute()

    return {"message": "Veículo removido com sucesso"}
