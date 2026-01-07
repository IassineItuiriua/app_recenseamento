FROM python:3.10-bullseye

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /meu_projecto

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-por \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python -m pip install --upgrade "pip<24" setuptools wheel

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar app
COPY . .
RUN python manage.py collectstatic --noinput
# Variáveis de produção
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Expor porta do Render
EXPOSE 8000

# Comando padrão para Gunicorn
CMD ["gunicorn", "meu_projecto.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
