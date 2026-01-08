import os
import django
from usuarios.models import CustomUser

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meu_projecto.settings")
django.setup()

# Substitua pelos seus dados
email = "isslamiassine@gmail.com"
username = "admin"
password = "MilitarForte123"

if not CustomUser.objects.filter(email=email).exists():
    user = CustomUser.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"Superuser {email} criado com sucesso!")
else:
    print("Superuser já existe.")
