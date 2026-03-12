#!/bin/bash
set -e

echo "Aplicando migrações..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput


echo "Configurando superuser..."

python manage.py shell << END
from django.contrib.auth import get_user_model
import os

User = get_user_model()

email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

print("EMAIL CONFIGURADO:", email)

if email:

    users = User.objects.filter(email=email)

    if users.exists():
        for user in users:
            user.is_staff = True
            user.is_superuser = True
            if password:
                user.set_password(password)
            user.save()
            print("Permissões corrigidas para:", user.email)

    else:
        user = User.objects.create_superuser(
            email=email,
            password=password
        )
        print("Superuser criado:", email)

else:
    print("DJANGO_SUPERUSER_EMAIL não definido")

END


echo "Iniciando servidor..."
exec "$@"
# #!/bin/bash
# set -e

# echo "Aplicando migrações..."
# python manage.py migrate --noinput

# echo "Coletando arquivos estáticos..."
# python manage.py collectstatic --noinput

# echo "Criando superuser (se não existir)..."

# python manage.py shell << END
# from django.contrib.auth import get_user_model
# import os

# User = get_user_model()

# email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
# password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

# if email and password:
#     if not User.objects.filter(email=email).exists():
#         print("Criando superuser...")
#         User.objects.create_superuser(
#             email=email,
#             password=password
#         )
#     else:
#         print("Superuser já existe.")
# else:
#     print("Variáveis de ambiente não definidas.")
# END

# echo "Iniciando servidor..."

# exec "$@"
# #!/bin/sh
# set -e

# echo ">>> Aplicando migrações"
# python manage.py migrate --noinput || true

# echo ">>> Coletando estáticos"
# python manage.py collectstatic --noinput || true

# exec "$@"



# #!/bin/sh
# set -e

# echo "▶️ Entrypoint iniciado"
# echo "▶️ SECRET_KEY está definida? ${SECRET_KEY:+SIM}"

# python manage.py migrate --noinput
# python manage.py collectstatic --noinput

# exec "$@"






# #!/usr/bin/env bash
# set -e

# echo "==> Iniciando Django no Render..."

# # 1. Rodar migrations SEM criar unique ainda
# echo "==> Aplicando migrations (sem constraints)..."
# python manage.py migrate auth
# python manage.py migrate contenttypes
# python manage.py migrate admin
# python manage.py migrate sessions
# python manage.py migrate usuarios --fake-initial || true
# # python manage.py migrate recenseamento
# # python manage.py migrate documento
# echo "==> Sincronizando migrations críticas..."

# python manage.py showmigrations recenseamento | grep 0002_initial | grep "\[ \]" && \
# python manage.py migrate recenseamento 0002 --fake || true

# python manage.py showmigrations documento | grep 0001_initial | grep "\[ \]" && \
# python manage.py migrate documento 0001 --fake || true

# # 2. Remover duplicados ANTES de criar o índice unique
# echo "==> Limpando emails duplicados..."
# python manage.py shell -c "
# from django.contrib.auth import get_user_model
# User = get_user_model()

# seen = set()
# for u in User.objects.all().order_by('id'):
#     if u.email in seen:
#         print('Removendo duplicado:', u.email)
#         u.delete()
#     else:
#         seen.add(u.email)
# "

# echo "==> Forçando sincronização da migration documento.0002..."

# python manage.py migrate documento 0002 --fake || true

# # 3. Agora aplicar migrations reais (cria UNIQUE)
# echo "==> Aplicando migrations finais..."
# python manage.py migrate

# # 4. Criar superuser via env
# python manage.py shell -c "
# import os
# from django.contrib.auth import get_user_model
# User = get_user_model()

# email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
# password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

# if email and password:
#     if not User.objects.filter(email=email).exists():
#         User.objects.create_superuser(email=email, password=password)
#         print('Superuser criado')
#     else:
#         print('Superuser já existe')
# "

# # 5. Coletar estáticos
# python manage.py collectstatic --noinput

# # 6. Iniciar servidor
# exec gunicorn meu_projecto.wsgi:application --bind 0.0.0.0:$PORT



#!/bin/bash
# set -e

# echo "Aplicando migrações..."
# python manage.py migrate --noinput

# echo "Coletando arquivos estáticos..."
# python manage.py collectstatic --noinput

# echo "Inicializando sistema..."
# python manage.py bootstrap_system || true

# echo "Iniciando servidor..."
# exec "$@"