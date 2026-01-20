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

    # 1. Tela para digitar o e-mail
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='usuarios/password_reset.html',
        email_template_name='usuarios/password_reset_email.html',
        subject_template_name='usuarios/password_reset_subject.txt',
        success_url='/usuarios/password_reset/done/'
    ), name='password_reset'),

    # 2. Tela de confirmação de envio
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='usuarios/password_reset_done.html'
    ), name='password_reset_done'),

    # 3. Link enviado por e-mail (token)
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='usuarios/password_reset_confirm.html',
        success_url='/usuarios/reset/done/'
    ), name='password_reset_confirm'),

    # 4. Tela de sucesso final
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='usuarios/password_reset_complete.html'
    ), name='password_reset_complete'),
]
