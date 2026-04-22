"""
Asaas Service - Integração com Gateway de Pagamentos
"""
import os
from typing import Optional
import httpx
from app.config import get_settings


class AsaasService:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.ASAAS_API_KEY
        self.base_url = settings.ASAAS_API_URL or "https://sandbox.asaas.com/api/v3"
        self.headers = {
            "access_token": self.api_key,
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        with httpx.Client() as client:
            response = client.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json() if response.text else {}
    
    def criar_cliente(self, nome: str, email: str, cpf_cnpj: str, telefone: str = None) -> dict:
        """Cria cliente no Asaas"""
        data = {
            "name": nome,
            "email": email,
            "cpfCnpj": cpf_cnpj,
        }
        if telefone:
            data["phone"] = telefone
        return self._request("POST", "/customers", json=data)
    
    def criar_assinatura(self, customer_id: str, valor: float, descricao: str, ciclo: str = "MONTHLY") -> dict:
        """Cria assinatura SaaS"""
        data = {
            "customer": customer_id,
            "billingType": "CREDIT_CARD",
            "value": valor,
            "cycle": ciclo,
            "description": descricao,
        }
        return self._request("POST", "/subscriptions", json=data)
    
    def criar_cobranca(self, customer_id: str, valor: float, descricao: str, Data_vencimento: str = None) -> dict:
        """Cria cobrança única"""
        data = {
            "customer": customer_id,
            "billingType": "UNDEFINED",
            "value": valor,
            "dueDate": Data_vencimento,
            "description": descricao,
        }
        return self._request("POST", "/payments", json=data)
    
    def criar_subconta(self, nome_empresa: str, cnpj: str, email: str) -> dict:
        """Cria sub-conta (white-label) para empresa cobrar inquilinos"""
        data = {
            "name": nome_empresa,
            "cpfCnpj": cnpj,
            "email": email,
            "entity": {
                "type": "COMPANY"
            }
        }
        return self._request("POST", "/customers", json=data)
    
    def obter_status_pagamento(self, payment_id: str) -> dict:
        """Verifica status de pagamento"""
        return self._request("GET", f"/payments/{payment_id}")
    
    def listar_cobrancas_cliente(self, customer_id: str) -> dict:
        """Lista cobranças de um cliente"""
        return self._request("GET", f"/payments?customer={customer_id}")


# Instância global
asaas_service = AsaasService()