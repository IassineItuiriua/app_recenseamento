#!/usr/bin/env bash
set -e

echo "==> Iniciando Django no Render..."

# 1. Esperar o banco estar pronto
echo "==> Aguardando banco..."
python manage.py migrate --check || true

# 2. Aplicar migrations
echo "==> Aplicando migrations..."
python manage.py migrate

# 3. Garantir que o banco tem constraints
echo "==> Sincronizando schema..."
python manage.py migrate --run-syncdb

# 4. Limpar usuários duplicados (segurança)
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()

emails = User.objects.values_list('email', flat=True)
for e in set(emails):
    qs = User.objects.filter(email=e)
    if qs.count() > 1:
        keep = qs.first()
        qs.exclude(id=keep.id).delete()
        print(f'Duplicados removidos para {e}')
"

# 5. Criar superuser apenas se não existir
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

# 6. Coletar estáticos
echo "==> Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# 7. Iniciar servidor
echo "==> Iniciando Gunicorn..."
exec gunicorn meu_projecto.wsgi:application --bind 0.0.0.0:$PORT
