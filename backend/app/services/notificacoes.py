"""Serviço central de notificações"""
from app.services.email_service import EmailService

class NotificacaoService:
    """Orquestra notificações por múltiplos canais."""

    def __init__(self):
        self.email = EmailService()

    async def enviar_alerta_proximidade_limite(self, **kwargs):
        """Delega para email service."""
        await self.email.enviar_alerta_proximidade_limite(**kwargs)
