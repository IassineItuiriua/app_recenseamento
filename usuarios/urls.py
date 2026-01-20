from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

app_name = "usuarios"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path("completar_perfil/", views.completar_perfil, name="completar_perfil"),
    path("painel/", views.painel, name="painel"),

    # 1. Solicitação - Adicionamos o success_url e o caminho da pasta registration
    path('reset_password/', 
         auth_views.PasswordResetView.as_view(
             template_name="registration/password_reset_form.html",
             success_url=reverse_lazy('usuarios:password_reset_done') # Importante!
         ), 
         name='password_reset'),

    # 2. E-mail enviado
    path('reset_password_sent/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name="registration/password_reset_done.html"
         ), 
         name='password_reset_done'),

    # 3. Confirmar nova senha - Adicionamos o success_url
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name="registration/password_reset_confirm.html",
             success_url=reverse_lazy('usuarios:password_reset_complete') # Importante!
         ), 
         name='password_reset_confirm'),

    # 4. Sucesso final
    path('reset_password_complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name="registration/password_reset_complete.html"
         ), 
         name='password_reset_complete'),
]
