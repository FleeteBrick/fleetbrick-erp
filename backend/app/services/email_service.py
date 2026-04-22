"""Serviço de e-mail transacional via Resend"""
import os
from typing import Dict, Any
import resend
from jinja2 import Template

class EmailService:
    """Envio de e-mails transacionais com templates HTML."""

    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY")
        self.from_email = os.getenv("RESEND_FROM_EMAIL", "fleetebrick@gmail.com")
        resend.api_key = self.api_key

    async def enviar_email(
        self,
        to: str,
        subject: str,
        template: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Envia e-mail usando template."""

        html_content = self._render_template(template, context or {})

        try:
            response = resend.Emails.send({
                "from": f"Fleet&Brick <{self.from_email}>",
                "to": to,
                "subject": subject,
                "html": html_content
            })
            return {"success": True, "id": response["id"]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Renderiza template HTML."""

        templates = {
            "manutencao_preventiva": """
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #10b981;">🚗 Manutenção Preventiva Agendada</h2>
                <p>Olá {{ motorista_nome }},</p>
                <p>Seu veículo <strong>{{ veiculo_placa }}</strong> ({{ veiculo_modelo }}) 
                   possui manutenção preventiva agendada.</p>
                <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0;">{{ mensagem }}</p>
                </div>
                <p>Por favor, entre em contato com a gestão da frota para agendar.</p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="color: #6b7280; font-size: 12px;">Fleet&Brick ERP - Gestão Inteligente</p>
            </div>
            """,

            "pagamento_confirmado": """
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #10b981;">✅ Pagamento Confirmado</h2>
                <p>Olá {{ nome }},</p>
                <p>Seu pagamento de <strong>R$ {{ valor }}</strong> referente a <strong>{{ mes_referencia }}</strong> 
                   foi confirmado com sucesso!</p>
                <p>Obrigado por sua pontualidade.</p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                <p style="color: #6b7280; font-size: 12px;">Fleet&Brick ERP</p>
            </div>
            """,

            "alerta_limite": """
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #f59e0b;">⚠️ Atenção: Limite do Plano Próximo</h2>
                <p>Você está utilizando <strong>{{ usados }} de {{ limite }} {{ tipo_recurso }}</strong> 
                   ({{ percentual }}%).</p>
                <p>Considere fazer um upgrade do seu plano para evitar bloqueios.</p>
                <a href="https://app.fleetbrick.com/planos" 
                   style="display: inline-block; background: #10b981; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 6px; margin-top: 15px;">
                    Ver Planos
                </a>
            </div>
            """,

            "bem_vindo": """
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #10b981;">🎉 Bem-vindo ao Fleet&Brick!</h2>
                <p>Olá {{ nome }},</p>
                <p>Sua conta foi criada com sucesso. Você tem <strong>14 dias de trial gratuito</strong> 
                   para explorar todas as funcionalidades.</p>
                <p>Plano escolhido: <strong>{{ plano }}</strong></p>
                <a href="https://app.fleetbrick.com/dashboard" 
                   style="display: inline-block; background: #10b981; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 6px; margin-top: 15px;">
                    Acessar Dashboard
                </a>
            </div>
            """
        }

        template_str = templates.get(template_name, "<p>{{ mensagem }}</p>")
        return Template(template_str).render(**context)

    async def enviar_alerta_proximidade_limite(
        self,
        empresa_id: str,
        tipo_recurso: str,
        usados: int,
        limite: int,
        percentual: float
    ):
        """Envia alerta quando empresa atinge 80% do limite."""
        from supabase import create_client
        import os

        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

        # Busca admins da empresa
        admins = supabase.table("usuarios").select("email, nome").eq("empresa_id", empresa_id).in_("nivel_acesso", ["tenant_admin", "manager"]).execute()

        for admin in admins.data:
            await self.enviar_email(
                to=admin["email"],
                subject="⚠️ Alerta: Limite do Plano Próximo",
                template="alerta_limite",
                context={
                    "usados": usados,
                    "limite": limite,
                    "tipo_recurso": tipo_recurso,
                    "percentual": f"{percentual * 100:.0f}%"
                }
            )
