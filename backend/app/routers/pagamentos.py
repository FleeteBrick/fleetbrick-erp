"""
Rotas de Pagamentos de Aluguel
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from supabase import create_client

from app.config import get_settings
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/pagamentos", tags=["Pagamentos"])


class PagamentoResponse(BaseModel):
    id: str
    empresa_id: str
    contrato_id: str
    valor: float
    data_vencimento: str
    status: str
    mes_referencia: str
    link_boleto: Optional[str]
    pix_copia_cola: Optional[str]


@router.get("/", response_model=List[PagamentoResponse])
async def listar_pagamentos(
    current_user: dict = Depends(get_current_user),
    contrato_id: Optional[str] = None,
    status: Optional[str] = None
):
    """Lista pagamentos"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user["empresa_id"]
    
    query = supabase.table("pagamentos_aluguel").select("*").eq("empresa_id", empresa_id)
    if contrato_id:
        query = query.eq("contrato_id", contrato_id)
    if status:
        query = query.eq("status", status)
    
    result = query.order("data_vencimento", desc=True).execute()
    return result.data


@router.get("/{pagamento_id}", response_model=PagamentoResponse)
async def obter_pagamento(
    pagamento_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtém pagamento"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    empresa_id = current_user["empresa_id"]
    
    result = supabase.table("pagamentos_aluguel").select("*").eq("id", pagamento_id).eq("empresa_id", empresa_id).single().execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    return result.data