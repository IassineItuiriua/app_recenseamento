#!/usr/bin/env bash
set -e

echo "==> Iniciando Django no Render..."

# 1. Rodar migrations SEM criar unique ainda
echo "==> Aplicando migrations (sem constraints)..."
python manage.py migrate auth
python manage.py migrate contenttypes
python manage.py migrate admin
python manage.py migrate sessions
python manage.py migrate usuarios --fake-initial || true
# python manage.py migrate recenseamento
# python manage.py migrate documento
echo "==> Sincronizando migrations críticas..."

python manage.py showmigrations recenseamento | grep 0002_initial | grep "\[ \]" && \
python manage.py migrate recenseamento 0002 --fake || true

python manage.py showmigrations documento | grep 0001_initial | grep "\[ \]" && \
python manage.py migrate documento 0001 --fake || true

# 2. Remover duplicados ANTES de criar o índice unique
echo "==> Limpando emails duplicados..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()

seen = set()
for u in User.objects.all().order_by('id'):
    if u.email in seen:
        print('Removendo duplicado:', u.email)
        u.delete()
    else:
        seen.add(u.email)
"

echo "==> Forçando sincronização da migration documento.0002..."

python manage.py migrate documento 0002 --fake || true

# 3. Agora aplicar migrations reais (cria UNIQUE)
echo "==> Aplicando migrations finais..."
python manage.py migrate

# 4. Criar superuser via env
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()

email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if email and password:
    if not User.objects.filter(email=email).exists():
        User.objects.create_superuser(email=email, password=password)
        print('Superuser criado')
    else:
        print('Superuser já existe')
"

# 5. Coletar estáticos
python manage.py collectstatic --noinput

# 6. Iniciar servidor
exec gunicorn meu_projecto.wsgi:application --bind 0.0.0.0:$PORT



# #!/usr/bin/env bash
# set -e

# echo "==> Iniciando Django no Render..."

# # 1. Esperar o banco estar pronto
# echo "==> Aguardando banco..."
# python manage.py migrate --check || true

# # 2. Aplicar migrations
# echo "==> Aplicando migrations..."
# python manage.py migrate

# # 3. Garantir que o banco tem constraints
# echo "==> Sincronizando schema..."
# python manage.py migrate --run-syncdb

# # 4. Limpar usuários duplicados (segurança)
# python manage.py shell -c "
# from django.contrib.auth import get_user_model
# User = get_user_model()

# emails = User.objects.values_list('email', flat=True)
# for e in set(emails):
#     qs = User.objects.filter(email=e)
#     if qs.count() > 1:
#         keep = qs.first()
#         qs.exclude(id=keep.id).delete()
#         print(f'Duplicados removidos para {e}')
# "

# # 5. Criar superuser apenas se não existir
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

# # 6. Coletar estáticos
# echo "==> Coletando arquivos estáticos..."
# python manage.py collectstatic --noinput

# # 7. Iniciar servidor
# echo "==> Iniciando Gunicorn..."
# exec gunicorn meu_projecto.wsgi:application --bind 0.0.0.0:$PORT
