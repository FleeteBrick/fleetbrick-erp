"""
Sprint 4: Agentes Autônomos OpenClaw
Agente de Triagem e Agente de Cobrança
"""
import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from supabase import create_client
import resend
from app.config import get_settings

# Configuração do cliente Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://guzzdpvrcslpqejnansv.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmMyM2E2NWJiLTY4NmQtNDdiMC04NGJiLTJlNjJmNGM1NGViODo6JGFhY2hfNTIzZjY5OTYtODVhNy00ZTVjLTkyOWMtZGNhNjMzMzU4ODI1")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuração Resend
resend.api_key = os.getenv("RESEND_API_KEY", "re_9F9k6iq9_BThXjsbptQ2aabaiGGd9jGNH")


class AgenteTriagem:
    """
    Agente Engenheiro de Triagem
    Monitora feedbacks e classifica automaticamente
    """
    
    def __init__(self):
        self.trigger_words_bug = [
            "erro", "bug", "não funciona", "falha", "crash", 
            "exception", "problema", "danificado", "quebrado"
        ]
        self.trigger_words_sugestao = [
            "sugestão", "melhoria", "ideal", "seria bom", 
            "poderia ter", "feature", "nova função"
        ]
        self.trigger_words_duvida = [
            "como fazer", "como usar", "duvida", "dúvida", 
            "não sei", "help", "ajuda"
        ]
    
    def classify_feedback(self, descricao: str) -> dict:
        """Classifica o feedback automaticamente"""
        desc_lower = descricao.lower()
        
        tipo = "suporte"
        nivel = "media"
        
        if any(palavra in desc_lower for palavra in self.trigger_words_bug):
            tipo = "bug"
            nivel = "critica"
        elif any(palavra in desc_lower for palavra in self.trigger_words_sugestao):
            tipo = "sugestao"
            nivel = "baixa"
        elif any(palavra in desc_lower for palavra in self.trigger_words_duvida):
            tipo = "duvida"
            nivel = "baixa"
        
        return {"tipo": tipo, "nivel": nivel}
    
    def processar_novos_chamados(self):
        """Processa chamados abertos e classifica"""
        chamados = supabase.table("chamados_suporte").select("*").eq("status", "aberto").eq("categoria", None).execute()
        
        results = []
        for chamado in chamados.data:
            classificacao = self.classify_feedback(chamado["descricao"])
            
            supabase.table("chamados_suporte").update({
                "categoria": classificacao["tipo"],
                "nivel_prioridade": classificacao["nivel"]
            }).eq("id", chamado["id"]).execute()
            
            results.append({
                "chamado_id": chamado["id"],
                "classificacao": classificacao
            })
            
            # Se for bug crítico, enviar e-mail
            if classificacao["tipo"] == "bug" and classificacao["nivel"] == "critica":
                self.enviar_email_alerta_bug(chamado)
        
        return {"processados": results, "total": len(results)}
    
    def enviar_email_alerta_bug(self, chamado: dict):
        """Envia e-mail para fleetebrick@gmail.com sobre bug crítico"""
        try:
            msg = resend.Emails.send({
                "from": "Fleet&Brick <fleetebrick@gmail.com>",
                "to": ["fleetebrick@gmail.com"],
                "subject": f"[BUG CRÍTICO] #{chamado['id']} - {chamado.get('titulo', 'Sem título')}",
                "html": f"""
                <h2>🐛 Bug Crítico Detectado</h2>
                <p><strong>Empresa:</strong> {chamado.get('empresa_id', 'N/A')}</p>
                <p><strong>Descrição:</strong></p>
                <p>{chamado.get('descricao', 'N/A')}</p>
                <p><strong>Data:</strong> {chamado.get('created_at', 'N/A')}</p>
                """
            })
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")


class AgenteCobranca:
    """
    Agente de Cobrança Autônoma
    Verifica inadimplência e envia mensagens via WhatsApp
    """
    
    def calcular_vencimento(self, data_entrada: str, dia_vencimento: int, mes_ref: str) -> str:
        """Calcula data de vencimiento basada na data de entrada"""
        from datetime import date
        
        ano, mes = map(int, mes_ref.split("-"))
        data_venc = date(ano, mes, dia_vencimento)
        
        return data_venc.isoformat()
    
    def verificar_inadimplencia(self, empresa_id: str) -> list:
        """Verifica pagamentos inadimplentes"""
        from datetime import date, timedelta
        
        hoje = date.today()
        
        contratos = supabase.table("contratos_locacao").select(
            "*, propriedades(endereco)"
        ).eq("empresa_id", empresa_id).eq("status", "ativo").execute()
        
        inadimplentes = []
        
        for contrato in contratos.data:
            dia_venc = contrato.get("dia_vencimento", 5)
            valor = contrato.get("valor_aluguel", 0)
            contrato_id = contrato["id"]
            data_entrada = contrato.get("data_entrada")
            
            if not data_entrada:
                continue
            
            for i in range(1, 4):
                mes = hoje.month - i
                ano = hoje.year
                if mes <= 0:
                    mes += 12
                    ano -= 1
                mes_ref = f"{ano}-{mes:02d}"
                
                data_venc = self.calcular_vencimento(data_entrada, dia_venc, mes_ref)
                
                pagamento = supabase.table("pagamentos_aluguel").select("*").eq(
                    "contrato_id", contrato_id
                ).eq("mes_referencia", mes_ref).execute()
                
                if not pagamento.data:
                    inadimplentes.append({
                        "contrato_id": contrato_id,
                        "inquilino": contrato.get("inquilino_nome"),
                        "telefone": contrato.get("inquilino_telefone"),
                        "valor": valor,
                        "mes": mes_ref,
                        "data_vencimento": data_venc,
                        "status": "nao_gerado"
                    })
                elif pagamento.data[0].get("status") == "pendente":
                    data_venc_date = date.fromisoformat(data_venc)
                    dias_atraso = (hoje - data_venc_date).days
                    
                    if dias_atraso > 0:
                        inadimplentes.append({
                            "contrato_id": contrato_id,
                            "inquilino": contrato.get("inquilino_nome"),
                            "telefone": contrato.get("inquilino_telefone"),
                            "valor": valor,
                            "mes": mes_ref,
                            "data_vencimento": data_venc,
                            "dias_atraso": dias_atraso,
                            "status": "pendente"
                        })
        
        return inadimplentes
    
    def executar_cobranca(self, empresa_id: str):
        """Executa cobrança diária"""
        inadimplentes = self.verificar_inadimplencia(empresa_id)
        
        results = []
        
        for item in inadimplentes:
            if item["dias_atraso"] > 3:
                mensagem = self.gerar_mensagem_cobranca(item)
                results.append({
                    "inquilino": item["inquilino"],
                    "telefone": item["telefone"],
                    "mensagem": mensagem,
                    "dias_atraso": item["dias_atraso"]
                })
                
                # Aqui integraria com WhatsApp via OpenClaw
                # self.enviar_whatsapp(item["telefone"], mensagem)
        
        return {"cobrancoes_enviadas": results, "total": len(results)}
    
    def gerar_mensagem_cobranca(self, item: dict) -> str:
        """Gera mensagem de cobrança"""
        return f"""
Olá {item['inquilino']}, tudo bem?

提醒imos que o aluguel do mês {item['mes']} no valor de R$ {item['valor']:.2f} está atrasado há {item['dias_atraso']} dias.

Para evitar adicionais, favor realizar o pagamento o quanto antes.

Em caso de dúvidas, entre em contato conosco.
        """.strip()


class AgenteManutencao:
    """
    Agente de Manutenção
    Verifica quilometragem e alertas de manutenção
    """
    
    def verificar_pendencias(self, empresa_id: str) -> list:
        """Verifica veículos com manutenção pendente"""
        from datetime import date
        
        hoje = date.today()
        
        # Veículos com manutenção vencida
        manutencoes = supabase.table("manutencoes").select(
            "*, veiculos(placa, modelo)"
        ).eq("empresa_id", empresa_id).eq("status", "agendada").execute()
        
        pendentes = []
        for m in manutencoes.data:
            data_agendada = date.fromisoformat(m["data_agendada"])
            if data_agendada < hoje:
                pendentes.append({
                    "veiculo": m.get("veiculos"),
                    "tipo": m["tipo"],
                    "data_agendada": m["data_agendada"],
                    "dias_atraso": (hoje - data_agendada).days
                })
        
        # Veículos com km excedido
        veiculos = supabase.table("veiculos").select("*").eq(
            "empresa_id", empresa_id
        ).eq("status", "ativo").execute()
        
        for v in veiculos.data:
            km = v.get("quilometragem_atual", 0)
            if km > 10000:
                pendentes.append({
                    "veiculo": {"placa": v["placa"], "modelo": v.get("modelo")},
                    "tipo": "km_excedido",
                    "km_atual": km,
                    "dados": v
                })
        
        return pendentes
    
    def enviar_alerta_manutencao(self, empresa_id: str):
        """Envia alerta de manutenção por e-mail"""
        pendentes = self.verificar_pendencias(empresa_id)
        
        if not pendentes:
            return {"alertas": 0}
        
        corpo = "<h2>🚧 Alertas de Manutenção</h2><ul>"
        for p in pendentes:
            veiculo = p.get("veiculo", {})
            corpo += f"<li>{veiculo.get('placa', 'N/A')} - {p.get('tipo')}</li>"
        corpo += "</ul>"
        
        try:
            msg = resend.Emails.send({
                "from": "Fleet&Brick <fleetebrick@gmail.com>",
                "to": ["fleetebrick@gmail.com"],
                "subject": f"[MANUTENÇÃO] {len(pendentes)} alertas pendentes",
                "html": corpo
            })
        except:
            pass
        
        return {"alertas": len(pendentes)}


def job_diario_manutencao():
    """Job diário de manutenção - executado às 02:00"""
    empresas = supabase.table("empresas").select("id").eq("status_assinatura", "ativa").execute()
    
    for empresa in empresas.data:
        agente_manut = AgenteManutencao()
        agente_manut.enviar_alerta_manutencao(empresa["id"])


def job_cobranca_autonoma():
    """Job de cobrança autônoma - executado diariamente"""
    empresas = supabase.table("empresas").select("id").eq("status_assinatura", "ativa").execute()
    
    for empresa in empresas.data:
        agente_cob = AgenteCobranca()
        agente_cob.executar_cobranca(empresa["id"])


if __name__ == "__main__":
    print("🚀 Agentes Fleet&Brick iniciado!")
    
    # Exemplo de uso
    # agente_triagem = AgenteTriagem()
    # resultado = agente_triagem.processar_novos_chamados()
    # print(resultado)