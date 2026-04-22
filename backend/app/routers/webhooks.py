"""
Router de Webhooks - Asaas
"""
import hashlib
import hmac
import json
from fastapi import APIRouter, Request, HTTPException, Depends
from supabase import create_client

from app.config import get_settings

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/asaas")
async def asaas_webhook(request: Request):
    """Webhooks do Asaas para atualização de pagamentos"""
    settings = get_settings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    
    body = await request.json()
    event = body.get("event")
    payment = body.get("payment", {})
    
    if event == "PAYMENT_RECEIVED" or event == "PAYMENT_CONFIRMED":
        payment_id = payment.get("id")
        value = payment.get("value")
        payment_date = payment.get("paymentDate")
        
        # Atualiza pagamento no banco
        supabase.table("pagamentos_aluguel").update({
            "status": "pago",
            "valor_pago": value,
            "data_pagamento": payment_date
        }).eq("asaas_payment_id", payment_id).execute()
        
        # Verifica se é pagamento de assinatura SaaS
        subscription = payment.get("subscription")
        if subscription:
            empresa = supabase.table("empresas").select("id").eq("asaas_subscription_id", subscription.get("id")).single().execute()
            if empresa.data:
                supabase.table("empresas").update({
                    "status_assinatura": "ativa"
                }).eq("id", empresa.data["id"]).execute()
    
    elif event == "PAYMENTOverdue" or event == "PAYMENT_FAILED":
        payment_id = payment.get("id")
        
        supabase.table("pagamentos_aluguel").update({
            "status": "vencido"
        }).eq("asaas_payment_id", payment_id).execute()
    
    return {"received": True}


@router.get("/asaas")
async def asaas_webhook_test():
    """Endpoint de teste para webhook"""
    return {"status": "ok", "message": "Webhook Asaas configurado"}