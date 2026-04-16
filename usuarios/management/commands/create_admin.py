from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        User = get_user_model()

        email = os.getenv("DJANGO_ADMIN_EMAIL")
        password = os.getenv("DJANGO_ADMIN_PASSWORD")

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password=password
            )
            self.stdout.write("Superuser criado com sucesso!")