"""Rotas de suporte, feedback e bugs"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from supabase import create_client

from app.config import get_settings
from app.schemas import TicketCreate, TicketUpdate, TicketResponse
from app.dependencies import get_current_user, require_super_admin

router = APIRouter(prefix="/tickets", tags=["Suporte"])
settings = get_settings()


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def criar_ticket(
    ticket: TicketCreate,
    current_user: dict = Depends(get_current_user)
):
    """Cria novo ticket de suporte/feedback/bug."""
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    ticket_data = ticket.model_dump()
    ticket_data["usuario_id"] = current_user["id"]
    ticket_data["empresa_id"] = current_user.get("empresa_id")
    ticket_data["metadata"] = {
        "user_agent": "API",
        "timestamp": str(datetime.now())
    }

    result = supabase.table("tickets_suporte").insert(ticket_data).execute()
    return result.data[0]


@router.get("/", response_model=List[TicketResponse])
async def listar_tickets(
    current_user: dict = Depends(require_super_admin),
    tipo: str = None,
    status: str = None,
    prioridade: str = None
):
    """Lista todos os tickets (Super Admin)."""
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    query = supabase.table("tickets_suporte").select("*, empresas(nome), usuarios(nome, email)").order("created_at", desc=True)

    if tipo:
        query = query.eq("tipo", tipo)
    if status:
        query = query.eq("status", status)
    if prioridade:
        query = query.eq("prioridade", prioridade)

    result = query.execute()
    return result.data


@router.get("/meus", response_model=List[TicketResponse])
async def meus_tickets(
    current_user: dict = Depends(get_current_user)
):
    """Lista tickets do usuário logado."""
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    result = supabase.table("tickets_suporte").select("*").eq("usuario_id", current_user["id"]).order("created_at", desc=True).execute()
    return result.data


@router.put("/{ticket_id}", response_model=TicketResponse)
async def atualizar_ticket(
    ticket_id: UUID,
    update: TicketUpdate,
    current_user: dict = Depends(require_super_admin)
):
    """Atualiza status e resposta do ticket (Super Admin)."""
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    update_data["resolvido_por"] = current_user["id"]

    if update_data.get("status") == "resolvido":
        from datetime import datetime
        update_data["data_resolucao"] = datetime.now().isoformat()

    result = supabase.table("tickets_suporte").update(update_data).eq("id", str(ticket_id)).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")

    return result.data[0]


@router.get("/estatisticas")
async def estatisticas_tickets(
    current_user: dict = Depends(require_super_admin)
):
    """Retorna estatísticas para o dashboard de suporte."""
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    total = supabase.table("tickets_suporte").select("*", count="exact").execute()
    abertos = supabase.table("tickets_suporte").select("*", count="exact").eq("status", "aberto").execute()
    resolvidos = supabase.table("tickets_suporte").select("*", count="exact").eq("status", "resolvido").execute()

    # Satisfação média
    sat = supabase.table("tickets_suporte").select("satisfacao").not_.is_("satisfacao", "null").execute()
    media_sat = sum(s["satisfacao"] for s in sat.data) / len(sat.data) if sat.data else 0

    return {
        "total": total.count,
        "abertos": abertos.count,
        "resolvidos": resolvidos.count,
        "media_satisfacao": round(media_sat, 1),
        "taxa_resolucao": round((resolvidos.count / total.count * 100), 1) if total.count else 0
    }
