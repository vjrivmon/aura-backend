"""
Configuración Django para el asistente de voz de movilidad urbana - Valencia
Simplificada según guía técnica: sin PostGIS, usando APIs externas
"""

from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default="django-insecure-g-bgv&ma%*4qs_k-#0c4g7n5m)iqi$tr%wp_5f3=p((!g!=7l6")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,testserver,*', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition - Simplificada para asistente de voz
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Eliminado: "django.contrib.gis",  # No necesitamos PostGIS
    "corsheaders",
    "rest_framework",  # Django REST Framework
    "rest_framework_simplejwt",  # JWT Authentication
    # Local apps
    "core.apps.CoreConfig",
    "mobility.apps.MobilityConfig",  # Nueva app para funcionalidades de movilidad
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Para servir archivos estáticos
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # CORS Middleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database - Simplificada a SQLite según guía técnica
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization - Configurado para español (Valencia)
LANGUAGE_CODE = "es-es"
TIME_ZONE = "Europe/Madrid"  # Zona horaria de Valencia
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files (para archivos de audio temporales)
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============================================================================
# CONFIGURACIÓN ESPECÍFICA PARA ASISTENTE DE VOZ
# ============================================================================

# API de Datos Abiertos del Ayuntamiento de Valencia
VALENCIA_OPENDATA_BASE_URL = "https://valencia.opendatasoft.com/api/records/1.0/"
VALENCIA_OPENDATA_SEARCH_URL = f"{VALENCIA_OPENDATA_BASE_URL}search/"

# Configuración de reconocimiento de voz (Vosk)
VOSK_MODEL_PATH = BASE_DIR / "models" / "vosk-model-es"  # Modelo español
VOSK_SAMPLE_RATE = 16000

# Configuración de síntesis de voz (gTTS)
TTS_LANGUAGE = "es"  # Español
TTS_TLD = "es"  # Dominio español para acento español
AUDIO_OUTPUT_DIR = BASE_DIR / "media" / "audio"

# Timeouts para APIs externas
API_REQUEST_TIMEOUT = 10  # segundos

# Configuración de rutas (OSRM público)
OSRM_BASE_URL = "http://router.project-osrm.org"

# Django REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# CORS settings - Configurado para desarrollo
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React/Next.js frontend
    "http://localhost:8081",  # Expo Go
    "http://localhost:19006", # Expo web
]

# Para desarrollo, permitir todas las origins (comentar en producción)
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

# Configuración de archivos estáticos para WhiteNoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Configuración de logging para debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'aura-voice.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'mobility': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
