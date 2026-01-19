# usuarios/views.py
import os
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from datetime import date
import logging
from .forms import CompletarPerfilUsuarioForm, UserRegistrationForm
from recenseamento.forms import RecenseamentoForm, CompletarPerfilCidadaoForm
from recenseamento.models import Recenseamento, PerfilCidadao
from .forms import EmailAuthenticationForm

# OCR Tesseract Windows
import pytesseract
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

logger = logging.getLogger(__name__)

# ======================================================
# CADASTRO
# ======================================================
def cadastro(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            novo_usuario = form.save()
            messages.success(request, "Conta criada com sucesso. Faça login.")
            return redirect("usuarios:login")
    else:
        form = UserRegistrationForm()
    return render(request, "usuarios/cadastro.html", {"form": form})


# ======================================================
# LOGIN
# ======================================================


# usuarios/views.py

def login_view(request):
    next_url = request.GET.get("next") or request.POST.get("next") or ""

    if request.method == "POST":
        form = EmailAuthenticationForm(data=request.POST, request=request)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(next_url if next_url.startswith("/") else "usuarios:painel")
    else:
        form = EmailAuthenticationForm(request=request)

    return render(request, "usuarios/login.html", {
        "form": form,
        "next": next_url
    })






# ======================================================
# LOGOUT
# ======================================================
def logout_view(request):
    logout(request)
    return redirect("/")


# ======================================================
# COMPLETAR PERFIL
# ======================================================
@login_required
def completar_perfil(request):
    usuario = request.user
    perfil = PerfilCidadao.objects.filter(user=usuario).first()
    recenseamento = Recenseamento.objects.filter(usuario=usuario).first()

    # Calcula idade se existir data de nascimento
    idade = None
    data_nasc = None
    if recenseamento and recenseamento.data_nascimento:
        data_nasc = recenseamento.data_nascimento
    elif perfil and perfil.data_nascimento:
        data_nasc = perfil.data_nascimento
    if data_nasc:
        idade = (date.today() - data_nasc).days // 365

    if request.method == "POST":
        form_usuario = CompletarPerfilUsuarioForm(request.POST, instance=usuario)
        form_recenseamento = RecenseamentoForm(request.POST, request.FILES, instance=recenseamento)
        form_cidadao = CompletarPerfilCidadaoForm(request.POST, request.FILES, instance=perfil)

        def render_forms():
            return render(request, "usuarios/completar_perfil.html", {
                "form_usuario": form_usuario,
                "form_recenseamento": form_recenseamento,
                "form_cidadao": form_cidadao,
                "idade": idade or 0,
            })

        # Atualiza dados básicos do usuário
        if not form_usuario.is_valid():
            return render_forms()
        form_usuario.save()

        # Define idade se ainda não definida
        if idade is None:
            data_nasc = None
            if form_recenseamento.is_valid():
                data_nasc = form_recenseamento.cleaned_data.get("data_nascimento")
            if not data_nasc and form_cidadao.is_valid():
                data_nasc = form_cidadao.cleaned_data.get("data_nascimento")
            if not data_nasc:
                messages.error(request, "Informe a data de nascimento.")
                return render_forms()
            idade = date.today().year - data_nasc.year - ((date.today().month, date.today().day) < (data_nasc.month, data_nasc.day))

        # ================= Recenseamento (≤35 anos) =================
        if idade <= 35:
            if not form_recenseamento.is_valid():
                return render_forms()
            rec = form_recenseamento.save(commit=False)
            rec.usuario = usuario
            rec.save()
            try:
                if rec.nim:
                    from notificacoes.accoes import apos_recenseamento
                    apos_recenseamento(usuario, rec.nim)
            except Exception as e:
                logger.error(f"Erro ao enviar email de recenseamento: {e}", exc_info=True)
            messages.success(request, "Recenseamento concluído com sucesso.")
            return redirect("usuarios:painel")

        # ================= Perfil Cidadão (>35 anos) =================
        if not form_cidadao.is_valid():
            return render_forms()

        foto = request.FILES.get("foto")
        bi_file = request.FILES.get("bi")
        if not foto or not bi_file:
            messages.error(request, "Para maiores de 35 anos é obrigatório enviar foto e BI.")
            return render_forms()

        perfil = form_cidadao.save(commit=False)
        perfil.user = usuario
        perfil.status_validacao = "PENDENTE"

        perfil_completo = perfil.completo() and not perfil.acao_completada

        try:
            perfil.save()
        except IntegrityError:
            messages.error(request, "Número do BI já registrado para outro usuário.")
            return render_forms()

        # Sincroniza nome
        nome_completo = perfil.nome_completo.strip().split(" ", 1)
        usuario.first_name = nome_completo[0]
        usuario.last_name = nome_completo[1] if len(nome_completo) > 1 else ""
        usuario.save()
        perfil.refresh_from_db()

        # Envio de email seguro
        if perfil_completo:
            try:
                with transaction.atomic():
                    from notificacoes.accoes import apos_completar_perfil
                    apos_completar_perfil(usuario)
                    perfil.acao_completada = True
                    perfil.save(update_fields=["acao_completada"])
            except Exception as e:
                logger.error(f"Erro ao enviar email de perfil +35: {e}", exc_info=True)

        messages.success(request, "Perfil atualizado com sucesso.")
        return redirect("usuarios:painel")

    # ---------------- GET ----------------
    else:
        form_usuario = CompletarPerfilUsuarioForm(instance=usuario)
        form_recenseamento = RecenseamentoForm(instance=recenseamento)
        form_cidadao = CompletarPerfilCidadaoForm(instance=perfil)

    return render(request, "usuarios/completar_perfil.html", {
        "form_usuario": form_usuario,
        "form_recenseamento": form_recenseamento,
        "form_cidadao": form_cidadao,
        "idade": idade or 0,
    })


# ======================================================
# PAINEL
# ======================================================
@login_required
def painel(request):
    user = request.user
    recenseamento = Recenseamento.objects.filter(usuario=user).first()
    perfil = PerfilCidadao.objects.filter(user=user).first()
    return render(request, "usuarios/painel.html", {"recenseamento": recenseamento, "perfil": perfil})


# ======================================================
# VALIDAR FOTO CIDADÃO (Face Recognition)
# ======================================================
@login_required
def validar_foto_cidadao(request, perfil_id):
    from recenseamento.services.reconhecimento_facial import verificar_foto
    perfil = get_object_or_404(PerfilCidadao, id=perfil_id)

    if not settings.FACE_RECOGNITION_ENABLED:
        perfil.status_validacao = "PENDENTE"
        perfil.save()
        messages.info(request, "Validação será feita manualmente.")
        return redirect("usuarios:painel")

    try:
        verificado = False
        if perfil.bi and perfil.foto:
            verificado = verificar_foto(perfil.bi.path, perfil.foto.path)

        perfil.foto_verificada = verificado
        perfil.status_validacao = "VALIDADO" if verificado else "REJEITADO"
        perfil.save()
    except Exception as e:
        perfil.status_validacao = "ERRO"
        perfil.save()
        logger.error(f"Erro no reconhecimento facial: {e}", exc_info=True)
        messages.error(request, "Ocorreu um erro ao validar a foto. Tente novamente.")

    return redirect("usuarios:painel")


from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.core import signing

from .utils import gerar_token_reset

User = get_user_model()


def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Usuário não encontrado.")
            return redirect("password_reset_request")

        token = gerar_token_reset(user)

        # guarda no cache por 15 minutos
        cache.set(f"pwd-reset-{token}", user.pk, timeout=900)

        return render(
            request,
            "usuarios/password_reset_token.html",
            {"token": token}
        )

    return render(request, "usuarios/password_reset_request.html")


from django.contrib.auth.hashers import make_password

def password_reset_confirm(request):
    if request.method == "POST":
        token = request.POST.get("token")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            messages.error(request, "As senhas não coincidem.")
            return redirect("password_reset_confirm")

        try:
            signer = signing.TimestampSigner()
            user_id = signer.unsign(token, max_age=900)
        except signing.BadSignature:
            messages.error(request, "Token inválido ou expirado.")
            return redirect("password_reset_confirm")

        cache_key = f"pwd-reset-{token}"
        if not cache.get(cache_key):
            messages.error(request, "Token já utilizado ou expirado.")
            return redirect("password_reset_confirm")

        user = User.objects.get(pk=user_id)
        user.password = make_password(password)
        user.save()

        cache.delete(cache_key)

        messages.success(request, "Senha redefinida com sucesso.")
        return redirect("login")

    return render(request, "usuarios/password_reset_confirm.html")
