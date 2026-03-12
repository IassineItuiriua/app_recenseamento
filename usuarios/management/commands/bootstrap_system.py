from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        User = get_user_model()

        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        user = User.objects.filter(email=email).first()

        if user:

            if not user.is_staff or not user.is_superuser:

                self.stdout.write("Corrigindo permissões do superuser...")

                user.is_staff = True
                user.is_superuser = True
                user.save()

        else:

            self.stdout.write("Criando superuser...")

            User.objects.create_superuser(
                email=email,
                password=password
            )

        self.stdout.write("Bootstrap finalizado")