from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from usuarios.forms import EmailPasswordResetForm
from . import views

app_name = "usuarios"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path("completar_perfil/", views.completar_perfil, name="completar_perfil"),
    path("painel/", views.painel, name="painel"),

    # =========================
    # RECUPERAÇÃO DE SENHA
    # =========================

    path("password-reset/", views.password_reset_request, name="password_reset"),
    path("password-reset/<str:token>/", views.password_reset_confirm, name="password_reset_confirm"),
    path("password-reset/done/", views.password_reset_done, name="password_reset_done"),


]
