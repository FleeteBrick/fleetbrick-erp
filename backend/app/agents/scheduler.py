"""Agendador de tarefas para agentes autônomos"""
from celery import Celery
from celery.schedules import crontab
import os

celery_app = Celery(
    'fleetbrick',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
    beat_schedule={
        'manutencao-diaria': {
            'task': 'app.agents.scheduler.executar_agente_manutencao',
            'schedule': crontab(hour=8, minute=0),  # 8h da manhã
        },
        'sincronizar-cobrancas': {
            'task': 'app.agents.scheduler.sincronizar_status_cobrancas',
            'schedule': crontab(hour='*/6', minute=0),  # A cada 6h
        },
        'verificar-assinaturas': {
            'task': 'app.agents.scheduler.verificar_assinaturas_vencidas',
            'schedule': crontab(hour=0, minute=0),  # Meia-noite
        }
    }
)

@celery_app.task
def executar_agente_manutencao():
    """Executa agente de suporte de frotas diariamente."""
    import asyncio
    from app.agents.fleet_support_agent import FleetSupportAgent

    agent = FleetSupportAgent()
    asyncio.run(agent.executar_ciclo_diario())
    return {"status": "ok", "agent": "fleet_support"}

@celery_app.task
def sincronizar_status_cobrancas():
    """Sincroniza status de cobranças com Asaas."""
    import asyncio
    from app.services.asaas_whitelabel import AsaasWhiteLabelService
    from app.services.supabase_service import get_supabase_client

    service = AsaasWhiteLabelService(get_supabase_client())
    result = asyncio.run(service.sincronizar_status_cobrancas())
    return result

@celery_app.task
def verificar_assinaturas_vencidas():
    """Verifica e suspende empresas com assinatura vencida."""
    from app.services.supabase_service import get_supabase_client
    from datetime import datetime

    supabase = get_supabase_client()

    # Busca empresas com trial vencido
    vencidas = supabase.table("empresas").select("*").lt("data_vencimento_trial", datetime.now().isoformat()).eq("status_assinatura", "trial").execute()

    for emp in vencidas.data:
        supabase.table("empresas").update({"status_assinatura": "atrasada"}).eq("id", emp["id"]).execute()

    return {"suspensas": len(vencidas.data)}
