from pathlib import Path
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
import dj_database_url  # importante para render
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega .env apenas localmente (dev)
if (BASE_DIR / ".env.local").exists():
    load_dotenv(BASE_DIR / ".env.local")


# ----------------------------
# Configurações principais
# ----------------------------
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY não definida")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"


# Render fornece o domínio do app, adiciona aqui
ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")

# ----------------------------
# Aplicações
# ----------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'usuarios',
    'recenseamento',
    'documento',
    'cloudinary',
    'cloudinary_storage',
]

# ----------------------------
# Middleware
# ----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve arquivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meu_projecto.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'meu_projecto' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'meu_projecto.wsgi.application'

# ----------------------------
# Banco de Dados (Render)
# ----------------------------
# ----------------------------
# Banco de Dados
# ----------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # PRODUÇÃO (Render)
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    # DESENVOLVIMENTO (Local / Docker)
    DATABASES = {
        "default": {
            "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.postgresql"),
            "NAME": os.getenv("DB_NAME", "postgres"),
            "USER": os.getenv("DB_USER", "iassine"),
            "PASSWORD": os.getenv("DB_PASSWORD", "iassine123"),
            "HOST": os.getenv("DB_HOST", "db"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }


# ----------------------------
# Validação de senhas
# ----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ----------------------------
# Internacionalização
# ----------------------------
LANGUAGE_CODE = "pt-pt"
TIME_ZONE = "Africa/Maputo"
USE_I18N = True
USE_TZ = True

# ----------------------------
# Arquivos estáticos
# ----------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Diretórios extras de estáticos
if (BASE_DIR / "static").exists():
    STATICFILES_DIRS = [BASE_DIR / "static"]
else:
    STATICFILES_DIRS = []


# ----------------------------
# Arquivos de mídia
# ----------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"  # ou usar S3 se quiser deploy cloud storage

# ----------------------------
# Autenticação
# ----------------------------
AUTH_USER_MODEL = "usuarios.CustomUser"
LOGIN_URL = "usuarios:login"
LOGIN_REDIRECT_URL = "usuarios:painel"
LOGOUT_REDIRECT_URL = "/"

# ----------------------------
# Email
# ----------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER
)

EMAIL_TIMEOUT = 30


# ----------------------------
# Outras configs
# ----------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

FACE_RECOGNITION_ENABLED = os.getenv("FACE_RECOGNITION_ENABLED", "False").lower() == "true"


# Limite de upload
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760

# ----------------------------
# Logging
# ----------------------------
LOGGING = {
    "version": 1,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "ERROR"},
}


CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

ENABLE_OCR = os.getenv("ENABLE_OCR", "false") == "true"


AUTHENTICATION_BACKENDS = [
    "usuarios.backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

CSRF_TRUSTED_ORIGINS = [
    "https://app-recenseamento.onrender.com",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
