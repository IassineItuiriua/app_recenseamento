from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
import os


class Command(BaseCommand):
    help = "Inicializa o sistema (superuser, grupos e permissões)"

    def handle(self, *args, **kwargs):

        User = get_user_model()

        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        # -----------------------------
        # Criar ou corrigir superuser
        # -----------------------------
        user = User.objects.filter(email=email).first()

        if user:

            if not user.is_staff or not user.is_superuser:

                self.stdout.write("Corrigindo permissões do superuser...")

                user.is_staff = True
                user.is_superuser = True
                user.save()

        else:

            self.stdout.write("Criando superuser...")

            user = User.objects.create_superuser(
                email=email,
                password=password
            )

        # -----------------------------
        # Criar grupos do sistema
        # -----------------------------
        grupos = ["Administrador", "Tecnico", "Operador"]

        for g in grupos:
            Group.objects.get_or_create(name=g)

        self.stdout.write("Grupos criados/verificados.")

        # -----------------------------
        # Permissões importantes
        # -----------------------------
        try:

            grupo_admin = Group.objects.get(name="Administrador")

            permissoes = Permission.objects.all()

            grupo_admin.permissions.set(permissoes)

            self.stdout.write("Permissões atribuídas ao Administrador.")

        except Exception as e:

            self.stdout.write(f"Erro ao configurar permissões: {e}")

        # -----------------------------
        # Adicionar superuser ao grupo
        # -----------------------------
        grupo_admin = Group.objects.get(name="Administrador")

        user.groups.add(grupo_admin)

        self.stdout.write(self.style.SUCCESS("Sistema inicializado com sucesso"))