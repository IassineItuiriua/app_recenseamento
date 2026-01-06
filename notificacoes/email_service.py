# notificacoes/email_service.py
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def enviar_email(destinatario, assunto, texto, html=None):
    """
    Envia email usando o Django SMTP configurado no settings.py.

    Parâmetros:
        destinatario (str): email do usuário
        assunto (str): assunto do email
        texto (str): mensagem em texto puro
        html (str, opcional): mensagem em HTML (se fornecido, envia HTML)
    """
    if not destinatario:
        logger.warning("Tentativa de enviar email sem destinatário.")
        return

    try:
        send_mail(
            subject=assunto,
            message=texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            fail_silently=False,
            html_message=html
        )
        logger.info(f"Email enviado para {destinatario} com sucesso: {assunto}")
    except Exception as e:
        logger.error(f"Falha ao enviar email para {destinatario}: {e}", exc_info=True)
