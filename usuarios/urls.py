from django.urls import path
from . import views   # ✅ IMPORTA O MÓDULO views


app_name = "usuarios"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path("completar_perfil/", views.completar_perfil, name="completar_perfil"),
    path("painel/", views.painel, name="painel"),
]
