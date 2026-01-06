# notificacoes/accoes.py
from django.conf import settings
from notificacoes.email_service import enviar_email
import logging

logger = logging.getLogger(__name__)


# ======================================================
# Função auxiliar segura para envio de email
# ======================================================
def enviar_email_usuario(user, assunto, texto, html=None):
    """
    Envia email apenas se o usuário tiver email válido.
    Captura erros sem quebrar o fluxo principal.
    """
    if not user or not user.email:
        return
    try:
        enviar_email(destinatario=user.email, assunto=assunto, texto=texto, html=html)
    except Exception as e:
        logger.error("Erro ao enviar email", exc_info=True)


# ======================================================
# 1 — Após cadastro do utilizador
# ======================================================
def apos_registro(user):
    assunto = "Cadastro realizado com sucesso"
    texto = (
        f"Olá {user.first_name},\n\n"
        "O seu cadastro foi realizado com sucesso.\n"
        "Agora já pode aceder ao sistema."
    )
    html = (
        f"<h2>Olá {user.first_name}!</h2>"
        "<p>O seu cadastro foi realizado com sucesso 👌</p>"
        "<p>Agora já pode aceder ao sistema.</p>"
    )
    enviar_email_usuario(user, assunto, texto, html)


# ======================================================
# 2 — Após recenseamento
# ======================================================
def apos_recenseamento(user, nim):
    assunto = "Recenseamento concluído com sucesso"
    texto = (
        f"Olá {user.first_name},\n\n"
        "O seu recenseamento foi concluído com sucesso.\n"
        f"NIM: {nim}"
    )
    html = (
        f"<h2>Olá {user.first_name}!</h2>"
        "<p>O seu recenseamento foi concluído com sucesso.</p>"
        f"<p><b>NIM:</b> {nim}</p>"
    )
    enviar_email_usuario(user, assunto, texto, html)


# ======================================================
# 3 — Após emissão de documento (geral)
# ======================================================
def apos_documento_emitido(user, documento):
    tipo_doc = documento.get_tipo_display()
    assunto = "Documento emitido com sucesso"
    texto = (
        f"Olá {user.first_name},\n\n"
        f"O seu documento '{tipo_doc}' foi emitido com sucesso.\n"
        "Já se encontra disponível no sistema."
    )
    html = (
        "<h2>Documento emitido!</h2>"
        f"<p>O documento <b>{tipo_doc}</b> foi emitido com sucesso.</p>"
        "<p>Já se encontra disponível no sistema.</p>"
    )
    enviar_email_usuario(user, assunto, texto, html)


# ======================================================
# 4 — Após completar Perfil de Cidadão (+35 anos)
# ======================================================
def apos_completar_perfil(user):
    assunto = "Perfil atualizado com sucesso"
    texto = (
        f"Olá {user.first_name},\n\n"
        "O seu Perfil de Cidadão (+35 anos) foi atualizado com sucesso.\n"
        "Agora já pode solicitar documentos militares através do sistema."
    )
    html = (
        "<h2>Perfil atualizado!</h2>"
        "<p>O seu <b>Perfil de Cidadão (+35 anos)</b> foi atualizado com sucesso.</p>"
        "<p>Agora já pode solicitar documentos militares.</p>"
    )
    enviar_email_usuario(user, assunto, texto, html)


# ======================================================
# 5 — Emissão de documento para Cidadão +35 anos
# ======================================================
def apos_documento_emitido_cidadao35(user, documento):
    tipo_doc = documento.get_tipo_display()
    assunto = "Documento emitido com sucesso"
    texto = (
        f"Olá {user.first_name},\n\n"
        f"O seu documento '{tipo_doc}' foi emitido com sucesso.\n"
        "Pode fazer o download diretamente na sua área de utilizador."
    )
    html = (
        "<h2>Documento emitido!</h2>"
        f"<p>O documento <b>{tipo_doc}</b> foi emitido com sucesso.</p>"
        "<p>Já está disponível para download na sua área de utilizador.</p>"
    )
    enviar_email_usuario(user, assunto, texto, html)
