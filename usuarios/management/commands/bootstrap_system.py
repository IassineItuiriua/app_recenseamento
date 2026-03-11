from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
import os


class Command(BaseCommand):
    help = "Inicializa o sistema criando superuser e grupos"

    def handle(self, *args, **kwargs):

        User = get_user_model()

        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if email and password:
            if not User.objects.filter(email=email).exists():

                self.stdout.write("Criando superuser...")

                User.objects.create_superuser(
                    email=email,
                    password=password
                )

            else:
                self.stdout.write("Superuser já existe.")

        # Criar grupos básicos
        grupos = ["Administrador", "Operador", "Tecnico"]

        for g in grupos:
            Group.objects.get_or_create(name=g)

        self.stdout.write(self.style.SUCCESS("Sistema inicializado com sucesso"))