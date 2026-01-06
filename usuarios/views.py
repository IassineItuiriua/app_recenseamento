from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.conf import settings
from datetime import date
import logging

from notificacoes.accoes import apos_completar_perfil, apos_recenseamento, apos_registro
from .forms import CompletarPerfilUsuarioForm, UserRegistrationForm
from recenseamento.forms import RecenseamentoForm, CompletarPerfilCidadaoForm
from recenseamento.models import Recenseamento, PerfilCidadao

logger = logging.getLogger(__name__)


# ======================================================
# CADASTRO
# ======================================================
def cadastro(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            novo_usuario = form.save()
            try:
                apos_registro(novo_usuario)
            except Exception as e:
                logger.error(f"Erro ao enviar email de registro: {e}", exc_info=True)
            messages.success(request, "Conta criada com sucesso. Faça login.")
            return redirect("usuarios:login")
    else:
        form = UserRegistrationForm()
    return render(request, "usuarios/cadastro.html", {"form": form})


# ======================================================
# LOGIN
# ======================================================
def login_view(request):
    next_url = request.GET.get("next", "")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        next_url = request.POST.get("next", "")
        if form.is_valid():
            login(request, form.get_user())
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect("usuarios:painel")
    else:
        form = AuthenticationForm()
    return render(
        request,
        "usuarios/login.html",
        {"form": form, "next": next_url},
    )


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
            return render(
                request,
                "usuarios/completar_perfil.html",
                {
                    "form_usuario": form_usuario,
                    "form_recenseamento": form_recenseamento,
                    "form_cidadao": form_cidadao,
                    "idade": idade or 0,
                },
            )

        if not form_usuario.is_valid():
            return render_forms()
        form_usuario.save()

        if idade is None:
            if form_recenseamento.is_valid():
                data_nasc = form_recenseamento.cleaned_data.get("data_nascimento")
            if not data_nasc and form_cidadao.is_valid():
                data_nasc = form_cidadao.cleaned_data.get("data_nascimento")
            if not data_nasc:
                messages.error(request, "Informe a data de nascimento.")
                return render_forms()
            idade = date.today().year - data_nasc.year - (
                (date.today().month, date.today().day) < (data_nasc.month, data_nasc.day)
            )

        # =================================================
        # Usuários até 35 anos → Recenseamento
        # =================================================
        if idade <= 35:
            if not form_recenseamento.is_valid():
                return render_forms()
            rec = form_recenseamento.save(commit=False)
            rec.usuario = usuario
            rec.save()

            try:
                if rec.nim:
                    apos_recenseamento(usuario, rec.nim)
            except Exception as e:
                logger.error(f"Erro ao enviar email de recenseamento: {e}", exc_info=True)

            messages.success(request, "Recenseamento concluído com sucesso.")
            return redirect("usuarios:painel")

        # =================================================
        # Usuários +35 anos → Perfil Cidadão
        # =================================================
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

        perfil_ficou_completo = perfil.completo() and not perfil.acao_completada

        try:
            perfil.save()
        except IntegrityError:
            messages.error(request, "Número do BI já está registrado para outro usuário.")
            return render_forms()

        # Sincronizar nome
        nome_completo = perfil.nome_completo.strip().split(" ", 1)
        usuario.first_name = nome_completo[0]
        usuario.last_name = nome_completo[1] if len(nome_completo) > 1 else ""
        usuario.save()
        perfil.refresh_from_db()

        # Envio de email seguro
        if perfil_ficou_completo:
            try:
                with transaction.atomic():
                    apos_completar_perfil(usuario)
                    perfil.acao_completada = True
                    perfil.save(update_fields=["acao_completada"])
            except Exception as e:
                logger.error(f"Erro ao enviar email de perfil +35: {e}", exc_info=True)

        messages.success(request, "Perfil atualizado com sucesso.")
        return redirect("usuarios:painel")

    # ---------------------------- GET ----------------------------
    else:
        form_usuario = CompletarPerfilUsuarioForm(instance=usuario)
        form_recenseamento = RecenseamentoForm(instance=recenseamento)
        form_cidadao = CompletarPerfilCidadaoForm(instance=perfil)

    return render(
        request,
        "usuarios/completar_perfil.html",
        {
            "form_usuario": form_usuario,
            "form_recenseamento": form_recenseamento,
            "form_cidadao": form_cidadao,
            "idade": idade or 0,
        },
    )


# ======================================================
# PAINEL
# ======================================================
@login_required
def painel(request):
    user = request.user
    recenseamento = Recenseamento.objects.filter(usuario=user).first()
    perfil = PerfilCidadao.objects.filter(user=user).first()
    return render(
        request,
        "usuarios/painel.html",
        {"recenseamento": recenseamento, "perfil": perfil},
    )


# ======================================================
# VALIDAR FOTO CIDADÃO (PRODUÇÃO SEGURO)
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
        # ⚠️ Tratamento seguro para arquivos grandes
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


# usuarios/views.py
# from datetime import date
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.db import IntegrityError, transaction
# from .forms import CompletarPerfilUsuarioForm, CompletarPerfilCidadaoForm, RecenseamentoForm
# from recenseamento.models import PerfilCidadao, Recenseamento
# from notificacoes.accoes import apos_recenseamento, apos_completar_perfil
# import logging

# logger = logging.getLogger(__name__)


# @login_required
# def completar_perfil(request):
#     usuario = request.user

#     perfil = PerfilCidadao.objects.filter(user=usuario).first()
#     recenseamento = Recenseamento.objects.filter(usuario=usuario).first()

#     # ----------------------------
#     # CALCULAR IDADE
#     # ----------------------------
#     idade = None
#     data_nasc = None

#     if recenseamento and recenseamento.data_nascimento:
#         data_nasc = recenseamento.data_nascimento
#     elif perfil and perfil.data_nascimento:
#         data_nasc = perfil.data_nascimento

#     if data_nasc:
#         idade = (date.today() - data_nasc).days // 365

#     # ----------------------------
#     # POST
#     # ----------------------------
#     if request.method == "POST":
#         form_usuario = CompletarPerfilUsuarioForm(request.POST, instance=usuario)
#         form_recenseamento = RecenseamentoForm(
#             request.POST, request.FILES, instance=recenseamento
#         )
#         form_cidadao = CompletarPerfilCidadaoForm(
#             request.POST, request.FILES, instance=perfil
#         )

#         def render_forms():
#             return render(
#                 request,
#                 "usuarios/completar_perfil.html",
#                 {
#                     "form_usuario": form_usuario,
#                     "form_recenseamento": form_recenseamento,
#                     "form_cidadao": form_cidadao,
#                     "idade": idade or 0,
#                 },
#             )

#         # ----------------------------
#         # VALIDAR USUÁRIO
#         # ----------------------------
#         if not form_usuario.is_valid():
#             return render_forms()

#         form_usuario.save()

#         # ----------------------------
#         # GARANTIR DATA NASCIMENTO
#         # ----------------------------
#         if idade is None:
#             if form_recenseamento.is_valid():
#                 data_nasc = form_recenseamento.cleaned_data.get("data_nascimento")
#             if not data_nasc and form_cidadao.is_valid():
#                 data_nasc = form_cidadao.cleaned_data.get("data_nascimento")
#             if not data_nasc:
#                 messages.error(request, "Informe a data de nascimento.")
#                 return render_forms()
#             idade = date.today().year - data_nasc.year - (
#                 (date.today().month, date.today().day) < (data_nasc.month, data_nasc.day)
#             )

#         # =================================================
#         # ATÉ 35 ANOS → RECENSEAMENTO
#         # =================================================
#         if idade <= 35:
#             if not form_recenseamento.is_valid():
#                 return render_forms()

#             rec = form_recenseamento.save(commit=False)
#             rec.usuario = usuario
#             rec.save()

#             # 📧 EMAIL
#             try:
#                 if rec.nim:
#                     apos_recenseamento(usuario, rec.nim)
#                     logger.info(f"Email de recenseamento enviado para {usuario.email}")
#                 else:
#                     logger.warning(f"Recenseamento de {usuario.username} sem NIM — email não enviado")
#             except Exception as e:
#                 logger.error(f"Falha ao enviar email de recenseamento: {e}", exc_info=True)

#             messages.success(request, "Recenseamento concluído com sucesso.")
#             return redirect("usuarios:painel")

#         # =================================================
#         # MAIOR DE 35 → PERFIL CIDADÃO
#         # =================================================
#         if not form_cidadao.is_valid():
#             return render_forms()

#         foto = request.FILES.get("foto")
#         bi_file = request.FILES.get("bi")

#         if not foto or not bi_file:
#             messages.error(
#                 request,
#                 "Para maiores de 35 anos é obrigatório enviar foto e BI."
#             )
#             return render_forms()

#         # ----------------------------
#         # SALVAR PERFIL
#         # ----------------------------
#         perfil = form_cidadao.save(commit=False)
#         perfil.user = usuario
#         perfil.status_validacao = "PENDENTE"

#         try:
#             perfil.save()
#         except IntegrityError:
#             messages.error(request, "Número do BI já está registrado para outro usuário.")
#             return render_forms()

#         # 🔄 Sincronizar nome com o utilizador
#         nome_completo = perfil.nome_completo.strip().split(" ", 1)
#         usuario.first_name = nome_completo[0]
#         usuario.last_name = nome_completo[1] if len(nome_completo) > 1 else ""
#         usuario.save()

#         # 🔄 ATUALIZAR OBJETO A PARTIR DO BANCO
#         perfil.refresh_from_db()

#         # ✅ AGORA SIM: calcular estado correto
#         perfil_ficou_completo = perfil.completo() and not perfil.acao_completada

#         if perfil_ficou_completo:
#             with transaction.atomic():
#                 try:
#                     apos_completar_perfil(usuario)
#                     perfil.acao_completada = True
#                     perfil.save(update_fields=["acao_completada"])
#                     logger.info(f"Email de Perfil +35 enviado para {usuario.email}")
#                 except Exception as e:
#                     logger.error(f"Falha ao enviar email de Perfil +35: {e}", exc_info=True)

#         messages.success(request, "Perfil atualizado com sucesso.")
#         return redirect("usuarios:painel")

#     # ----------------------------
#     # GET
#     # ----------------------------
#     else:
#         form_usuario = CompletarPerfilUsuarioForm(instance=usuario)
#         form_recenseamento = RecenseamentoForm(instance=recenseamento)
#         form_cidadao = CompletarPerfilCidadaoForm(instance=perfil)

#     return render(
#         request,
#         "usuarios/completar_perfil.html",
#         {
#             "form_usuario": form_usuario,
#             "form_recenseamento": form_recenseamento,
#             "form_cidadao": form_cidadao,
#             "idade": idade or 0,
#         },
#     )
